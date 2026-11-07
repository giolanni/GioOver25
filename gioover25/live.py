"""Acquisizione LIVE Diretta/Flashscore e riconciliazione con i ranking.

Il modulo e' deliberatamente separato dagli import dei risultati ufficiali:
scrive soltanto ``data/live/partite_live.csv`` e non richiama mai
``append_results`` o gli engine di ranking.
"""
from __future__ import annotations

import argparse
import csv
import logging
import re
import time
import unicodedata
from dataclasses import dataclass
from datetime import date, datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIVE_CSV = ROOT / "data" / "live" / "partite_live.csv"
DEFAULT_LOG = ROOT / "data" / "live" / "live.log"
DEFAULT_REGISTRY = ROOT / "data" / "league_registry.csv"
LIVE_FIELDS = (
    "MatchDate", "LeagueId", "Home", "Away", "MatchId",
    "Minute", "HG", "AG", "Status", "LastUpdate",
)

STATUS_SCHEDULED = "SCHEDULED"
STATUS_LIVE = "LIVE"
STATUS_FINAL = "FINAL"
STATUS_POSTPONED = "POSTPONED"
STATUS_UNKNOWN = "UNKNOWN"

OUTCOME_OK = "OK"
OUTCOME_KO = "KO"
OUTCOME_WAITING = "WAITING"
OUTCOME_UNAVAILABLE = "UNAVAILABLE"

_HEAD_RE = re.compile(r"^\s*([^:]+):\s*(.+?)\s*$")
_POSTPONED_TOKENS = (
    "si disputer", "posticip", "rinvi", "sospes", "annull",
    "postpon", "cancel", "suspend", "abgesag", "aplaz",
)


class LiveAcquisitionError(RuntimeError):
    """Nessun feed LIVE e' stato acquisito con successo."""


@dataclass(frozen=True)
class LiveMatch:
    match_date: str
    league_id: str
    home: str
    away: str
    match_id: str = ""
    minute: str = ""
    hg: int | None = None
    ag: int | None = None
    status: str = STATUS_UNKNOWN
    last_update: str = ""

    def as_row(self) -> dict[str, str]:
        return {
            "MatchDate": self.match_date,
            "LeagueId": self.league_id,
            "Home": self.home,
            "Away": self.away,
            "MatchId": self.match_id,
            "Minute": self.minute,
            "HG": "" if self.hg is None else str(self.hg),
            "AG": "" if self.ag is None else str(self.ag),
            "Status": self.status,
            "LastUpdate": self.last_update,
        }

    @classmethod
    def from_row(cls, row: Mapping[str, object]) -> "LiveMatch":
        return cls(
            match_date=str(row.get("MatchDate", "")).strip(),
            league_id=str(row.get("LeagueId", "")).strip(),
            home=str(row.get("Home", "")).strip(),
            away=str(row.get("Away", "")).strip(),
            match_id=str(row.get("MatchId", "")).strip(),
            minute=str(row.get("Minute", "")).strip(),
            hg=_optional_int(row.get("HG")),
            ag=_optional_int(row.get("AG")),
            status=str(row.get("Status", STATUS_UNKNOWN)).strip().upper() or STATUS_UNKNOWN,
            last_update=str(row.get("LastUpdate", "")).strip(),
        )


@dataclass(frozen=True)
class AcquisitionReport:
    matches: tuple[LiveMatch, ...]
    successful_feeds: int
    errors: tuple[str, ...]
    fetched_at: str


@dataclass(frozen=True)
class Freshness:
    state: str
    age_seconds: float | None
    last_update: str


@dataclass(frozen=True)
class EngineSummary:
    engine: str
    final_matches: int
    over_ok: int
    over_total: int
    btts_ok: int
    btts_total: int

    @property
    def over_pct(self) -> float | None:
        return _percentage(self.over_ok, self.over_total)

    @property
    def btts_pct(self) -> float | None:
        return _percentage(self.btts_ok, self.btts_total)


def _optional_int(value: object) -> int | None:
    text = str(value if value is not None else "").strip()
    return int(text) if text.isdigit() else None


def _percentage(ok: int, total: int) -> float | None:
    return round(ok * 100.0 / total, 1) if total else None


def _parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.astimezone()
    except ValueError:
        return None


def _feed_records(payload: str) -> Iterable[dict[str, str]]:
    for raw in (payload or "").split("~"):
        fields: dict[str, str] = {}
        for item in raw.split("¬"):
            if "÷" in item:
                key, value = item.split("÷", 1)
                fields[key] = value
        if fields:
            yield fields


def _event_datetime(timestamp: str, now: datetime) -> datetime | None:
    try:
        tz = now.tzinfo or datetime.now().astimezone().tzinfo
        return datetime.fromtimestamp(int(timestamp), tz=tz)
    except (TypeError, ValueError, OSError, OverflowError):
        return None


def _status_from_fields(fields: Mapping[str, str]) -> str:
    status_text = " ".join(str(value) for value in fields.values()).casefold()
    if any(token in status_text for token in _POSTPONED_TOKENS):
        return STATUS_POSTPONED
    return {
        "1": STATUS_SCHEDULED,
        "2": STATUS_LIVE,
        "3": STATUS_FINAL,
    }.get(fields.get("AB", ""), STATUS_UNKNOWN)


def _live_minute(fields: Mapping[str, str], kickoff: datetime | None, now: datetime) -> str:
    status = _status_from_fields(fields)
    if status == STATUS_FINAL:
        return "FT"
    if status != STATUS_LIVE:
        return ""
    if kickoff is None:
        return "LIVE"

    elapsed = max(0, int((now - kickoff).total_seconds() // 60) + 1)
    stage = fields.get("AC", "")
    # Nel feed calcio corrente AC=12 indica il primo tempo e AC=13 il secondo.
    # Il feed non espone sempre il cronometro: in quel caso il minuto e' una
    # stima prudente dall'orario di inizio, corretta per l'intervallo.
    if stage == "12":
        return f"{min(max(elapsed, 1), 45)}'"
    if stage == "13":
        return f"{min(max(elapsed - 15, 46), 90)}'"
    if stage in {"6", "7"}:
        return "HT"
    return "LIVE"


def parse_live_feed(
    payload: str,
    target_date: date,
    resolve_league: Callable[[str, str, str, str], str | None] | None = None,
    now: datetime | None = None,
) -> list[LiveMatch]:
    """Converte il feed Flashscore/Diretta nel formato LIVE canonico."""
    now = now or datetime.now().astimezone()
    country = league = ""
    out: list[LiveMatch] = []
    for fields in _feed_records(payload):
        if "ZA" in fields:
            heading = fields["ZA"].strip()
            match = _HEAD_RE.match(heading)
            country, league = (
                (match.group(1).strip(), match.group(2).strip())
                if match else ("", heading)
            )
            continue
        if not all(fields.get(key) for key in ("AA", "AE", "AF")):
            continue
        kickoff = _event_datetime(fields.get("AD", ""), now)
        if kickoff is None or kickoff.date() != target_date:
            continue

        home = fields["AE"].strip()
        away = fields["AF"].strip()
        league_id = resolve_league(country, league, home, away) if resolve_league else ""
        if not league_id:
            continue
        out.append(LiveMatch(
            match_date=target_date.isoformat(),
            league_id=league_id,
            home=home,
            away=away,
            match_id=fields["AA"].strip(),
            minute=_live_minute(fields, kickoff, now),
            hg=_optional_int(fields.get("AG")),
            ag=_optional_int(fields.get("AH")),
            status=_status_from_fields(fields),
            last_update=now.isoformat(timespec="seconds"),
        ))
    return deduplicate_live(out)


def _text_key(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "")).encode("ascii", "ignore").decode()
    text = text.casefold().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "", text)


def _team_key(league_id: str, value: object) -> str:
    try:
        from gioover25.team_names import normalize_team_name
        return normalize_team_name(league_id, value)
    except (ImportError, OSError, ValueError):
        return _text_key(value)


def _live_key(match: LiveMatch) -> tuple[str, ...]:
    if match.match_id:
        return ("id", match.match_id)
    return (
        "fixture", match.match_date, match.league_id,
        _team_key(match.league_id, match.home),
        _team_key(match.league_id, match.away),
    )


def _match_quality(match: LiveMatch) -> tuple[int, int, float]:
    status_rank = {
        STATUS_UNKNOWN: 0, STATUS_SCHEDULED: 1, STATUS_POSTPONED: 1,
        STATUS_LIVE: 2, STATUS_FINAL: 3,
    }.get(match.status, 0)
    score_rank = int(match.hg is not None and match.ag is not None)
    stamp = _parse_iso(match.last_update)
    return status_rank, score_rank, stamp.timestamp() if stamp else 0.0


def deduplicate_live(matches: Iterable[LiveMatch]) -> list[LiveMatch]:
    """Deduplica per MatchId, con fallback sulla chiave canonica partita."""
    merged: dict[tuple[str, ...], LiveMatch] = {}
    for match in matches:
        key = _live_key(match)
        previous = merged.get(key)
        if previous is None or _match_quality(match) >= _match_quality(previous):
            merged[key] = match
    return sorted(
        merged.values(),
        key=lambda item: (item.match_date, item.league_id, item.home.casefold(), item.away.casefold()),
    )


def _logger(log_path: Path = DEFAULT_LOG) -> logging.Logger:
    logger = logging.getLogger("gioover25.live")
    logger.setLevel(logging.INFO)
    wanted = str(log_path.resolve())
    if not any(getattr(handler, "baseFilename", "") == wanted for handler in logger.handlers):
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.addHandler(handler)
    return logger


def acquire_live_matches(
    target_date: date | None = None,
    registry_path: Path = DEFAULT_REGISTRY,
    fetcher: Callable[[int], str] | None = None,
    now: datetime | None = None,
) -> AcquisitionReport:
    """Interroga feed adiacenti e restituisce soltanto la giornata richiesta."""
    target_date = target_date or date.today()
    now = now or datetime.now().astimezone()
    if fetcher is None:
        from tools.diretta_mobile import fetch_feed
        fetcher = fetch_feed
    from tools.prepare_input import load_registry, resolve_match

    registry = load_registry(registry_path)

    def resolver(country: str, league: str, home: str, away: str) -> str | None:
        return resolve_match(registry, country, league, home, away)

    base_offset = (target_date - date.today()).days
    matches: list[LiveMatch] = []
    errors: list[str] = []
    successful = 0
    for offset in dict.fromkeys((base_offset, base_offset - 1, base_offset + 1)):
        try:
            payload = fetcher(offset)
            successful += 1
            matches.extend(parse_live_feed(payload, target_date, resolver, now))
        except Exception as exc:  # il chiamante deve mantenere disponibile il dato precedente
            errors.append(f"feed {offset}: {exc.__class__.__name__}: {exc}")
    if not successful:
        raise LiveAcquisitionError("; ".join(errors) or "Feed LIVE non disponibile")
    return AcquisitionReport(
        matches=tuple(deduplicate_live(matches)),
        successful_feeds=successful,
        errors=tuple(errors),
        fetched_at=now.isoformat(timespec="seconds"),
    )


def write_live_csv(path: Path, matches: Iterable[LiveMatch]) -> None:
    """Scrive il CSV in modo atomico, senza toccare input o storici ufficiali."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(
                stream, fieldnames=LIVE_FIELDS, delimiter=";", lineterminator="\n"
            )
            writer.writeheader()
            for match in matches:
                writer.writerow(match.as_row())
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_live_csv(path: Path = DEFAULT_LIVE_CSV) -> list[LiveMatch]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter=";")
        if not set(LIVE_FIELDS).issubset(reader.fieldnames or ()):
            raise ValueError(f"CSV LIVE non valido: {path}")
        return [LiveMatch.from_row(row) for row in reader]


def refresh_live_csv(
    path: Path = DEFAULT_LIVE_CSV,
    target_date: date | None = None,
    registry_path: Path = DEFAULT_REGISTRY,
    fetcher: Callable[[int], str] | None = None,
    now: datetime | None = None,
    log_path: Path = DEFAULT_LOG,
) -> AcquisitionReport:
    logger = _logger(log_path)
    try:
        report = acquire_live_matches(target_date, registry_path, fetcher, now)
        write_live_csv(path, report.matches)
        logger.info(
            "refresh ok matches=%s feeds=%s warnings=%s",
            len(report.matches), report.successful_feeds, len(report.errors),
        )
        for error in report.errors:
            logger.warning(error)
        return report
    except Exception:
        logger.exception("refresh LIVE fallito; CSV precedente conservato")
        raise


def freshness(
    matches: Sequence[LiveMatch],
    path: Path = DEFAULT_LIVE_CSV,
    stale_after: int = 180,
    now: datetime | None = None,
) -> Freshness:
    now = now or datetime.now().astimezone()
    timestamps = [stamp for stamp in (_parse_iso(row.last_update) for row in matches) if stamp]
    if timestamps:
        latest = max(timestamps)
    elif path.exists():
        latest = datetime.fromtimestamp(path.stat().st_mtime, tz=now.tzinfo)
    else:
        return Freshness("UNAVAILABLE", None, "")
    age = max(0.0, (now - latest.astimezone(now.tzinfo)).total_seconds())
    return Freshness("STALE" if age > stale_after else "FRESH", age, latest.isoformat(timespec="seconds"))


def load_engine_rankings(
    history_root: Path,
    match_date: str,
    engine: str | None = None,
) -> dict[str, list[dict[str, str]]]:
    paths = (
        [history_root / engine / f"storico_ranking_{engine}.csv"]
        if engine else sorted(history_root.glob("*/storico_ranking_*.csv"))
    )
    result: dict[str, list[dict[str, str]]] = {}
    for path in paths:
        if not path.is_file():
            continue
        engine_name = path.parent.name
        with path.open(encoding="utf-8-sig", newline="") as stream:
            rows = [
                dict(row) for row in csv.DictReader(stream, delimiter=";")
                if str(row.get("MatchDate", "")).strip() == match_date
            ]
        deduped: dict[tuple[str, str, str, str], dict[str, str]] = {}
        for row in rows:
            league_id = row.get("LeagueId", "").strip()
            key = (
                match_date, league_id,
                _team_key(league_id, row.get("Home", "")),
                _team_key(league_id, row.get("Away", "")),
            )
            previous = deduped.get(key)
            if previous is None or row.get("PredictionDate", "") >= previous.get("PredictionDate", ""):
                deduped[key] = row
        result[engine_name] = list(deduped.values())
    return result


def _similarity(left: object, right: object) -> float:
    return SequenceMatcher(None, _text_key(left), _text_key(right)).ratio()


def match_rankings(
    rankings: Sequence[Mapping[str, str]],
    live_matches: Sequence[LiveMatch],
    fuzzy_threshold: float = 0.88,
) -> list[tuple[Mapping[str, str], LiveMatch | None]]:
    """Matching esatto/alias e fuzzy non ambiguo, sempre entro lega e data."""
    exact: dict[tuple[str, str, str, str], list[tuple[int, LiveMatch]]] = {}
    for index, live in enumerate(live_matches):
        key = (
            live.match_date, live.league_id,
            _team_key(live.league_id, live.home),
            _team_key(live.league_id, live.away),
        )
        exact.setdefault(key, []).append((index, live))

    used: set[int] = set()
    output: list[tuple[Mapping[str, str], LiveMatch | None]] = []
    for ranking in rankings:
        league_id = str(ranking.get("LeagueId", "")).strip()
        match_date = str(ranking.get("MatchDate", "")).strip()
        key = (
            match_date, league_id,
            _team_key(league_id, ranking.get("Home", "")),
            _team_key(league_id, ranking.get("Away", "")),
        )
        candidates = [(i, row) for i, row in exact.get(key, ()) if i not in used]
        selected: tuple[int, LiveMatch] | None = candidates[0] if len(candidates) == 1 else None

        if selected is None:
            scored: list[tuple[float, int, LiveMatch]] = []
            for index, live in enumerate(live_matches):
                if index in used or live.match_date != match_date or live.league_id != league_id:
                    continue
                home_score = _similarity(ranking.get("Home", ""), live.home)
                away_score = _similarity(ranking.get("Away", ""), live.away)
                if min(home_score, away_score) < fuzzy_threshold:
                    continue
                scored.append(((home_score + away_score) / 2.0, index, live))
            scored.sort(reverse=True, key=lambda item: item[0])
            if scored and (len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.04):
                selected = (scored[0][1], scored[0][2])

        if selected is None:
            output.append((ranking, None))
        else:
            used.add(selected[0])
            output.append((ranking, selected[1]))
    return output


def evaluate_market(match: LiveMatch | None, market: str) -> str:
    if match is None or match.status in {STATUS_UNKNOWN, STATUS_POSTPONED}:
        return OUTCOME_UNAVAILABLE
    if match.hg is None or match.ag is None:
        return OUTCOME_UNAVAILABLE if match.status == STATUS_FINAL else OUTCOME_WAITING
    market_key = market.casefold().replace(" ", "")
    reached = (
        match.hg + match.ag >= 3
        if market_key in {"over2.5", "over25", "over"}
        else match.hg > 0 and match.ag > 0
        if market_key == "btts"
        else None
    )
    if reached is None:
        raise ValueError(f"Mercato LIVE non supportato: {market}")
    if reached:
        return OUTCOME_OK
    return OUTCOME_KO if match.status == STATUS_FINAL else OUTCOME_WAITING


def summarize_engine(
    engine: str,
    matched: Sequence[tuple[Mapping[str, str], LiveMatch | None]],
) -> EngineSummary:
    over_ok = over_total = btts_ok = btts_total = final_matches = 0
    for _ranking, live in matched:
        if live is None or live.status != STATUS_FINAL:
            continue
        over = evaluate_market(live, "Over2.5")
        btts = evaluate_market(live, "BTTS")
        if over not in {OUTCOME_OK, OUTCOME_KO} or btts not in {OUTCOME_OK, OUTCOME_KO}:
            continue
        final_matches += 1
        over_total += 1
        btts_total += 1
        over_ok += int(over == OUTCOME_OK)
        btts_ok += int(btts == OUTCOME_OK)
    return EngineSummary(engine, final_matches, over_ok, over_total, btts_ok, btts_total)


def _format_pct(value: float | None) -> str:
    return "n/d" if value is None else f"{value:.1f}%"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggiorna il CSV LIVE Diretta/Flashscore.")
    parser.add_argument("--date", help="Giornata YYYY-MM-DD (default: oggi)")
    parser.add_argument("--output", type=Path, default=DEFAULT_LIVE_CSV)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--watch", action="store_true", help="Ripete l'acquisizione.")
    parser.add_argument("--interval", type=int, default=60, help="Secondi tra gli aggiornamenti (default 60).")
    args = parser.parse_args(argv)
    target = date.fromisoformat(args.date) if args.date else date.today()
    if args.interval < 15:
        parser.error("--interval deve essere almeno 15 secondi")

    while True:
        try:
            report = refresh_live_csv(args.output, target, args.registry)
            warning = f"; warning feed={len(report.errors)}" if report.errors else ""
            print(f"[LIVE] {len(report.matches)} partite; feed ok={report.successful_feeds}{warning}")
        except Exception as exc:
            print(f"[LIVE ERROR] {exc}")
            if not args.watch:
                return 1
        if not args.watch:
            return 0
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
