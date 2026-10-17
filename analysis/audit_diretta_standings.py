"""Audit read-only delle classifiche GioOver25 contro Diretta/Flashscore.

Il comando legge ``data/storico/classifiche_calcolate`` e non modifica mai
storici o classifiche. Gli unici file scritti sono i report nella directory
selezionata (per default ``analysis/data_quality_report``).

Esempi::

    python -m analysis.audit_diretta_standings
    python -m analysis.audit_diretta_standings --league-id Italy_SerieA

Diretta e Flashscore usano lo stesso backend Livesport. La ricerca pubblica
fornisce torneo e stage correnti; il feed ``to_`` contiene la classifica.
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gioover25.registry import LeagueInfo, load_league_registry
from gioover25.team_names import get_team_id, normalize_team_name
from tools.diretta_mobile import FEED_SIGN


LOGGER = logging.getLogger("diretta_standings_audit")

SEARCH_URL = "https://s.livesport.services/api/v2/search/"
STANDINGS_FEED_URL = (
    "https://global.flashscore.ninja/323/x/feed/to_{tournament_id}_{stage_id}_1"
)
DEFAULT_STANDINGS_DIR = ROOT / "data" / "storico" / "classifiche_calcolate"
DEFAULT_REGISTRY = ROOT / "data" / "league_registry.csv"
DEFAULT_LEAGUE_ALIASES = ROOT / "data" / "league_aliases.csv"
DEFAULT_OUTPUT_DIR = ROOT / "analysis" / "data_quality_report"

INTEGER_METRICS = (
    "position",
    "played",
    "wins",
    "draws",
    "losses",
    "gf",
    "ga",
    "gd",
    "points",
)
ALL_METRICS = INTEGER_METRICS + ("ppg",)


@dataclass(frozen=True)
class StandingRow:
    team: str
    position: int
    played: int
    wins: int
    draws: int
    losses: int
    gf: int
    ga: int
    gd: int
    points: int
    ppg: float


@dataclass(frozen=True)
class LeagueAlias:
    country: str
    league: str


@dataclass(frozen=True)
class LeagueTarget:
    info: LeagueInfo
    standings_path: Path
    aliases: tuple[LeagueAlias, ...] = ()


@dataclass(frozen=True)
class TournamentCandidate:
    tournament_id: str
    stage_ids: tuple[str, ...]
    name: str
    country: str
    template_id: str
    score: float


@dataclass(frozen=True)
class RemoteStandingSource:
    rows: tuple[StandingRow, ...]
    tournament_id: str
    stage_id: str
    tournament_name: str
    country: str
    source_url: str
    exact_overlap: int
    fuzzy_overlap: int


@dataclass
class ComparisonRow:
    league_id: str
    status: str
    match_method: str = ""
    local_team: str = ""
    remote_team: str = ""
    normalized_team: str = ""
    name_issue: str = ""
    differences: str = ""
    local: StandingRow | None = None
    remote: StandingRow | None = None


@dataclass
class LeagueAudit:
    league_id: str
    status: str
    local_count: int = 0
    remote_count: int = 0
    comparison_rows: list[ComparisonRow] = field(default_factory=list)
    tournament_id: str = ""
    stage_id: str = ""
    remote_country: str = ""
    remote_league: str = ""
    source_url: str = ""
    message: str = ""

    @property
    def matches(self) -> int:
        return sum(row.status == "MATCH" for row in self.comparison_rows)

    @property
    def aliases(self) -> int:
        return sum(bool(row.name_issue) for row in self.comparison_rows)

    @property
    def differences(self) -> int:
        return sum(
            row.status
            in {
                "DIFFERENCE",
                "ALIAS_WITH_DIFFERENCES",
                "ALIAS_SUSPECTED_WITH_DIFFERENCES",
                "MISSING_ON_DIRETTA",
                "MISSING_LOCALLY",
            }
            for row in self.comparison_rows
        )


def parse_records(payload: str) -> list[dict[str, str]]:
    """Decodifica il formato compatto Livesport (``~``, ``¬``, ``÷``)."""
    records: list[dict[str, str]] = []
    for raw_record in (payload or "").split("~"):
        fields: dict[str, str] = {}
        for item in raw_record.split("¬"):
            if "÷" not in item:
                continue
            key, value = item.split("÷", 1)
            fields[key] = value
        if fields:
            records.append(fields)
    return records


def _to_int(value: object, field_name: str) -> int:
    text = str(value if value is not None else "").strip().rstrip(".")
    if not re.fullmatch(r"-?\d+", text):
        raise ValueError(f"{field_name} non intero: {value!r}")
    return int(text)


def _to_float(value: object, fallback: float) -> float:
    text = str(value if value is not None else "").strip().replace(",", ".")
    try:
        return float(text)
    except ValueError:
        return fallback


def parse_standings_feed(payload: str) -> list[StandingRow]:
    """Estrae la tabella generale dal feed ``to_`` di Diretta/Flashscore."""
    rows: list[StandingRow] = []
    for fields in parse_records(payload):
        if not fields.get("TR") or not fields.get("TN") or not fields.get("TM"):
            continue
        try:
            played = _to_int(fields.get("TM"), "TM/Played")
            points = _to_int(fields.get("TP"), "TP/Points")
            goals = re.fullmatch(
                r"\s*(-?\d+)\s*[:\-]\s*(-?\d+)\s*", fields.get("TG", "")
            )
            if goals is None:
                raise ValueError(f"TG/Gol non valido: {fields.get('TG')!r}")
            gf, ga = int(goals.group(1)), int(goals.group(2))
            calculated_ppg = points / played if played else 0.0
            rows.append(
                StandingRow(
                    team=" ".join(fields["TN"].split()),
                    position=_to_int(fields.get("TR"), "TR/Position"),
                    played=played,
                    wins=_to_int(fields.get("TW"), "TW/Wins"),
                    draws=_to_int(fields.get("TDR"), "TDR/Draws"),
                    losses=_to_int(fields.get("TL"), "TL/Losses"),
                    gf=gf,
                    ga=ga,
                    gd=gf - ga,
                    points=points,
                    ppg=_to_float(fields.get("TPK"), calculated_ppg),
                )
            )
        except ValueError as exc:
            LOGGER.warning("Riga classifica Diretta ignorata (%s): %s", exc, fields)
    return rows


def load_local_standings(path: Path) -> list[StandingRow]:
    """Legge la classifica locale; se contiene più round usa quello massimo."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        raw_rows = list(csv.DictReader(handle, delimiter=";"))
    if not raw_rows:
        return []

    rounds: list[int] = []
    for raw in raw_rows:
        try:
            rounds.append(_to_int(raw.get("Round"), "Round"))
        except ValueError:
            pass
    if rounds:
        latest_round = max(rounds)
        raw_rows = [
            row
            for row in raw_rows
            if str(row.get("Round", "")).strip() == str(latest_round)
        ]

    rows: list[StandingRow] = []
    for raw in raw_rows:
        played = _to_int(raw.get("Played"), "Played")
        points = _to_int(raw.get("Points"), "Points")
        gf = _to_int(raw.get("GF"), "GF")
        ga = _to_int(raw.get("GA"), "GA")
        calculated_ppg = points / played if played else 0.0
        rows.append(
            StandingRow(
                team=" ".join(str(raw.get("Team", "")).split()),
                position=_to_int(raw.get("Position"), "Position"),
                played=played,
                wins=_to_int(raw.get("Wins"), "Wins"),
                draws=_to_int(raw.get("Draws"), "Draws"),
                losses=_to_int(raw.get("Losses"), "Losses"),
                gf=gf,
                ga=ga,
                gd=_to_int(raw.get("GD"), "GD"),
                points=points,
                ppg=_to_float(raw.get("PPG"), calculated_ppg),
            )
        )
    return rows


def load_diretta_aliases(path: Path) -> dict[str, tuple[LeagueAlias, ...]]:
    aliases: dict[str, list[LeagueAlias]] = {}
    if not path.exists():
        LOGGER.warning("File alias leghe non trovato: %s", path)
        return {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle, delimiter=";"):
            if str(row.get("Source", "")).strip().casefold() != "diretta":
                continue
            league_id = str(row.get("LeagueId", "")).strip()
            if not league_id:
                continue
            aliases.setdefault(league_id, []).append(
                LeagueAlias(
                    country=str(row.get("CountryAlias", "")).strip(),
                    league=str(row.get("LeagueAlias", "")).strip(),
                )
            )
    return {key: tuple(value) for key, value in aliases.items()}


def _ascii_words(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or "").casefold())
    text = text.encode("ascii", "ignore").decode("ascii")
    replacements = {
        "girone": "group",
        "gruppo": "group",
        "femminile": "women",
        "femminili": "women",
        "damer": "women",
        "frauen": "women",
        "ovest": "west",
        "est": "east",
        "nord": "north",
        "sud": "south",
        "centrale": "central",
        "repubblica ceca": "czech republic",
        "bosnia erzegovina": "bosnia herzegovina",
    }
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = " ".join(text.split())
    for source, target in replacements.items():
        text = re.sub(rf"\b{re.escape(source)}\b", target, text)
    return " ".join(text.split())


def _compact(value: object) -> str:
    return _ascii_words(value).replace(" ", "")


def _name_similarity(left: object, right: object) -> float:
    a, b = _ascii_words(left), _ascii_words(right)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    compact_a, compact_b = a.replace(" ", ""), b.replace(" ", "")
    if compact_a == compact_b:
        return 0.99
    sequence = SequenceMatcher(None, compact_a, compact_b).ratio()
    words_a, words_b = set(a.split()), set(b.split())
    token_score = len(words_a & words_b) / len(words_a | words_b)
    return max(sequence, token_score)


def _is_women(value: object) -> bool:
    normalized = _ascii_words(value)
    return any(
        marker in normalized.split()
        for marker in ("women", "woman", "femenino", "kvenna")
    )


def _request_text(url: str, timeout: int, params: dict[str, object] | None = None) -> str:
    if params:
        url = f"{url}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (GioOver25 DirettaStandingsAudit)",
            "Accept": "*/*",
            "Accept-Language": "it-IT,it;q=0.9,en;q=0.7",
            "Referer": "https://www.diretta.it/",
            "Origin": "https://www.diretta.it",
            "x-fsign": FEED_SIGN,
        },
    )
    with urlopen(request, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def search_tournaments(query: str, timeout: int) -> list[dict]:
    payload = _request_text(
        SEARCH_URL,
        timeout,
        {
            "q": query,
            "lang-id": 1,
            "type-ids": 1,
            "project-id": 2,
            "project-type-id": 1,
        },
    )
    decoded = json.loads(payload)
    return decoded if isinstance(decoded, list) else []


def select_tournament_candidates(
    search_rows: Iterable[dict], target: LeagueTarget
) -> list[TournamentCandidate]:
    """Ordina i risultati di ricerca per paese, genere e nome della lega."""
    target_names = [target.info.league]
    target_names.extend(alias.league for alias in target.aliases if alias.league)
    target_is_women = _is_women(target.info.league_id + " " + target.info.league)
    candidates: list[TournamentCandidate] = []

    for raw in search_rows:
        sport_id = ((raw.get("sport") or {}).get("id"))
        if str(sport_id) != "1":
            continue
        country = str((raw.get("defaultCountry") or {}).get("name", "")).strip()
        country_score = _name_similarity(country, target.info.country)
        if country_score < 0.78:
            continue
        gender = str((raw.get("gender") or {}).get("name", ""))
        candidate_is_women = _is_women(gender + " " + str(raw.get("name", "")))
        if candidate_is_women != target_is_women:
            continue

        league_name = str(raw.get("name", "")).strip()
        league_score = max(
            (_name_similarity(league_name, wanted) for wanted in target_names),
            default=0.0,
        )
        if league_score < 0.62:
            continue

        tournament = raw.get("defaultTournament") or {}
        tournament_id = str(tournament.get("id", "")).strip()
        stage_ids = tuple(
            str(stage).strip()
            for stage in tournament.get("stageWithStatsDataIds") or []
            if str(stage).strip()
        )
        if not tournament_id:
            continue
        candidates.append(
            TournamentCandidate(
                tournament_id=tournament_id,
                stage_ids=stage_ids,
                name=league_name or str(tournament.get("name", "")).strip(),
                country=country,
                template_id=str(raw.get("id", "")).strip(),
                score=(country_score * 0.25) + (league_score * 0.75),
            )
        )

    unique: dict[tuple[str, tuple[str, ...]], TournamentCandidate] = {}
    for candidate in candidates:
        key = (candidate.tournament_id, candidate.stage_ids)
        previous = unique.get(key)
        if previous is None or candidate.score > previous.score:
            unique[key] = candidate
    return sorted(unique.values(), key=lambda item: item.score, reverse=True)


def _identity(league_id: str, team: str) -> str:
    return normalize_team_name(league_id, team)


def _overlap_score(
    league_id: str, local_rows: Iterable[StandingRow], remote_rows: Iterable[StandingRow]
) -> tuple[int, int]:
    local = list(local_rows)
    remote = list(remote_rows)
    local_keys = {_identity(league_id, row.team) for row in local}
    remote_keys = {_identity(league_id, row.team) for row in remote}
    exact = len(local_keys & remote_keys)

    unmatched_local = [row for row in local if _identity(league_id, row.team) not in remote_keys]
    unmatched_remote = [row for row in remote if _identity(league_id, row.team) not in local_keys]
    fuzzy = len(_pair_fuzzy(unmatched_local, unmatched_remote))
    return exact, fuzzy


def fetch_best_remote_standing(
    target: LeagueTarget,
    local_rows: list[StandingRow],
    timeout: int,
    request_text: Callable[[str, int, dict[str, object] | None], str] = _request_text,
) -> tuple[RemoteStandingSource | None, str]:
    query_names = [
        f"{alias.country} {alias.league}".strip()
        for alias in target.aliases
        if alias.country or alias.league
    ]
    # Gli alias Diretta sono mapping espliciti e devono avere priorità sul
    # nome canonico del registry (spesso inglese, mentre la search è localizzata).
    query_names.append(f"{target.info.country} {target.info.league}".strip())
    query_names = list(dict.fromkeys(query_names))

    selected_candidates: list[TournamentCandidate] = []
    search_errors: list[str] = []
    for query in query_names:
        try:
            payload = request_text(
                SEARCH_URL,
                timeout,
                {
                    "q": query,
                    "lang-id": 1,
                    "type-ids": 1,
                    "project-id": 2,
                    "project-type-id": 1,
                },
            )
            decoded = json.loads(payload)
            rows = decoded if isinstance(decoded, list) else []
            selected_candidates.extend(select_tournament_candidates(rows, target))
        except Exception as exc:  # la singola query non deve fermare tutto l'audit
            search_errors.append(f"{query!r}: {type(exc).__name__}: {exc}")

    unique_candidates: dict[tuple[str, tuple[str, ...]], TournamentCandidate] = {}
    for candidate in selected_candidates:
        key = (candidate.tournament_id, candidate.stage_ids)
        previous = unique_candidates.get(key)
        if previous is None or candidate.score > previous.score:
            unique_candidates[key] = candidate
    candidates = sorted(
        unique_candidates.values(), key=lambda item: item.score, reverse=True
    )[:3]

    if not candidates:
        detail = "Nessun torneo compatibile trovato dalla ricerca Diretta/Flashscore."
        if search_errors:
            detail += " Errori ricerca: " + " | ".join(search_errors)
        return None, detail

    best: RemoteStandingSource | None = None
    attempted = 0
    feed_errors: list[str] = []
    for candidate in candidates:
        if not candidate.stage_ids:
            feed_errors.append(f"{candidate.name}: nessuno stage con classifica")
            continue
        for stage_id in candidate.stage_ids:
            if attempted >= 10:
                break
            attempted += 1
            source_url = STANDINGS_FEED_URL.format(
                tournament_id=candidate.tournament_id, stage_id=stage_id
            )
            try:
                payload = request_text(source_url, timeout, None)
                remote_rows = parse_standings_feed(payload)
            except Exception as exc:
                feed_errors.append(
                    f"{candidate.name}/{stage_id}: {type(exc).__name__}: {exc}"
                )
                continue
            if not remote_rows:
                feed_errors.append(f"{candidate.name}/{stage_id}: classifica vuota")
                continue
            exact, fuzzy = _overlap_score(
                target.info.league_id, local_rows, remote_rows
            )
            current = RemoteStandingSource(
                rows=tuple(remote_rows),
                tournament_id=candidate.tournament_id,
                stage_id=stage_id,
                tournament_name=candidate.name,
                country=candidate.country,
                source_url=source_url,
                exact_overlap=exact,
                fuzzy_overlap=fuzzy,
            )
            if best is None or (
                current.exact_overlap,
                current.fuzzy_overlap,
                -abs(len(current.rows) - len(local_rows)),
            ) > (
                best.exact_overlap,
                best.fuzzy_overlap,
                -abs(len(best.rows) - len(local_rows)),
            ):
                best = current
        if attempted >= 10:
            break

    if best is None:
        return None, "Classifica Diretta non disponibile. " + " | ".join(feed_errors[:5])
    if local_rows and best.exact_overlap + best.fuzzy_overlap == 0:
        return (
            None,
            "Torneo trovato, ma nessuna squadra coincide con la classifica locale; "
            "mapping rifiutato per sicurezza.",
        )
    return best, ""


def _pair_fuzzy(
    local_rows: Iterable[StandingRow], remote_rows: Iterable[StandingRow]
) -> list[tuple[StandingRow, StandingRow, float]]:
    local = list(local_rows)
    remote = list(remote_rows)
    if not local or not remote:
        return []
    matrix = {
        (li, ri): _name_similarity(left.team, right.team)
        for li, left in enumerate(local)
        for ri, right in enumerate(remote)
    }
    pairs: list[tuple[StandingRow, StandingRow, float]] = []
    used_local: set[int] = set()
    used_remote: set[int] = set()
    for (li, ri), score in sorted(matrix.items(), key=lambda item: item[1], reverse=True):
        if score < 0.88 or li in used_local or ri in used_remote:
            continue
        local_alternatives = sorted(
            (value for (lidx, ridx), value in matrix.items() if lidx == li and ridx != ri),
            reverse=True,
        )
        remote_alternatives = sorted(
            (value for (lidx, ridx), value in matrix.items() if ridx == ri and lidx != li),
            reverse=True,
        )
        if local_alternatives and score - local_alternatives[0] < 0.04:
            continue
        if remote_alternatives and score - remote_alternatives[0] < 0.04:
            continue
        used_local.add(li)
        used_remote.add(ri)
        pairs.append((local[li], remote[ri], score))
    return pairs


def _metric_differences(local: StandingRow, remote: StandingRow) -> list[str]:
    differences = [
        metric
        for metric in INTEGER_METRICS
        if getattr(local, metric) != getattr(remote, metric)
    ]
    if abs(local.ppg - remote.ppg) > 0.011:
        differences.append("ppg")
    return differences


def _known_alias(league_id: str, left: str, right: str) -> bool:
    left_id = get_team_id(league_id, left)
    right_id = get_team_id(league_id, right)
    return bool(left_id and right_id and left_id == right_id and left != right)


def compare_standings(
    league_id: str,
    local_rows: Iterable[StandingRow],
    remote_rows: Iterable[StandingRow],
) -> list[ComparisonRow]:
    """Confronta due classifiche e separa alias noti/sospetti da scarti reali."""
    local = list(local_rows)
    remote = list(remote_rows)
    local_by_key: dict[str, list[StandingRow]] = {}
    remote_by_key: dict[str, list[StandingRow]] = {}
    for row in local:
        local_by_key.setdefault(_identity(league_id, row.team), []).append(row)
    for row in remote:
        remote_by_key.setdefault(_identity(league_id, row.team), []).append(row)

    comparisons: list[ComparisonRow] = []
    matched_local: set[int] = set()
    matched_remote: set[int] = set()

    for key in sorted(set(local_by_key) & set(remote_by_key)):
        for left, right in zip(local_by_key[key], remote_by_key[key]):
            local_index = local.index(left)
            remote_index = remote.index(right)
            matched_local.add(local_index)
            matched_remote.add(remote_index)
            metrics = _metric_differences(left, right)
            known_alias = _known_alias(league_id, left.team, right.team)
            same_display = (
                " ".join(left.team.split()).casefold()
                == " ".join(right.team.split()).casefold()
            )
            name_issue = "KNOWN_ALIAS" if known_alias else (
                "NORMALIZED_NAME" if not same_display else ""
            )
            if metrics:
                status = "ALIAS_WITH_DIFFERENCES" if name_issue else "DIFFERENCE"
            else:
                status = "ALIAS_ONLY" if name_issue else "MATCH"
            comparisons.append(
                ComparisonRow(
                    league_id=league_id,
                    status=status,
                    match_method="team_dictionary" if known_alias else "normalized_name",
                    local_team=left.team,
                    remote_team=right.team,
                    normalized_team=key,
                    name_issue=name_issue,
                    differences="|".join(metrics),
                    local=left,
                    remote=right,
                )
            )

    remaining_local = [row for index, row in enumerate(local) if index not in matched_local]
    remaining_remote = [row for index, row in enumerate(remote) if index not in matched_remote]
    fuzzy_pairs = _pair_fuzzy(remaining_local, remaining_remote)
    fuzzy_local_ids = {id(left) for left, _, _ in fuzzy_pairs}
    fuzzy_remote_ids = {id(right) for _, right, _ in fuzzy_pairs}

    for left, right, score in fuzzy_pairs:
        metrics = _metric_differences(left, right)
        comparisons.append(
            ComparisonRow(
                league_id=league_id,
                status=(
                    "ALIAS_SUSPECTED_WITH_DIFFERENCES"
                    if metrics
                    else "ALIAS_SUSPECTED"
                ),
                match_method=f"fuzzy:{score:.3f}",
                local_team=left.team,
                remote_team=right.team,
                normalized_team=_compact(left.team),
                name_issue="SUSPECTED_ALIAS",
                differences="|".join(metrics),
                local=left,
                remote=right,
            )
        )

    for row in remaining_local:
        if id(row) in fuzzy_local_ids:
            continue
        comparisons.append(
            ComparisonRow(
                league_id=league_id,
                status="MISSING_ON_DIRETTA",
                local_team=row.team,
                normalized_team=_identity(league_id, row.team),
                differences="team_missing",
                local=row,
            )
        )
    for row in remaining_remote:
        if id(row) in fuzzy_remote_ids:
            continue
        comparisons.append(
            ComparisonRow(
                league_id=league_id,
                status="MISSING_LOCALLY",
                remote_team=row.team,
                normalized_team=_identity(league_id, row.team),
                differences="team_missing",
                remote=row,
            )
        )

    comparisons.sort(
        key=lambda row: (
            row.local.position if row.local else 10_000,
            row.remote.position if row.remote else 10_000,
            row.local_team or row.remote_team,
        )
    )
    return comparisons


def audit_league(target: LeagueTarget, timeout: int) -> LeagueAudit:
    league_id = target.info.league_id
    try:
        local_rows = load_local_standings(target.standings_path)
    except Exception as exc:
        return LeagueAudit(
            league_id=league_id,
            status="LOCAL_ERROR",
            message=f"{type(exc).__name__}: {exc}",
        )
    if not local_rows:
        return LeagueAudit(
            league_id=league_id,
            status="LOCAL_EMPTY",
            message="Classifica locale vuota.",
        )

    try:
        source, message = fetch_best_remote_standing(target, local_rows, timeout)
    except Exception as exc:
        return LeagueAudit(
            league_id=league_id,
            status="REMOTE_ERROR",
            local_count=len(local_rows),
            message=f"{type(exc).__name__}: {exc}",
        )
    if source is None:
        status = "UNMAPPED" if "Nessun torneo" in message or "mapping rifiutato" in message else "UNAVAILABLE"
        return LeagueAudit(
            league_id=league_id,
            status=status,
            local_count=len(local_rows),
            message=message,
        )

    comparisons = compare_standings(league_id, local_rows, source.rows)
    actual_differences = any(
        row.status
        in {
            "DIFFERENCE",
            "ALIAS_WITH_DIFFERENCES",
            "ALIAS_SUSPECTED_WITH_DIFFERENCES",
            "MISSING_ON_DIRETTA",
            "MISSING_LOCALLY",
        }
        for row in comparisons
    )
    suspected_alias = any("SUSPECTED" in row.status for row in comparisons)
    known_alias = any(row.status == "ALIAS_ONLY" for row in comparisons)
    status = (
        "DIFFERENCES"
        if actual_differences
        else "ALIAS_REVIEW"
        if suspected_alias
        else "OK_WITH_ALIASES"
        if known_alias
        else "OK"
    )
    return LeagueAudit(
        league_id=league_id,
        status=status,
        local_count=len(local_rows),
        remote_count=len(source.rows),
        comparison_rows=comparisons,
        tournament_id=source.tournament_id,
        stage_id=source.stage_id,
        remote_country=source.country,
        remote_league=source.tournament_name,
        source_url=source.source_url,
        message=(
            f"overlap esatto={source.exact_overlap}, fuzzy={source.fuzzy_overlap}"
        ),
    )


def discover_targets(
    registry_path: Path,
    standings_dir: Path,
    aliases_path: Path,
    requested_leagues: list[str] | None,
) -> tuple[list[LeagueTarget], list[LeagueAudit]]:
    registry = load_league_registry(registry_path)
    aliases = load_diretta_aliases(aliases_path)
    preflight: list[LeagueAudit] = []

    if requested_leagues:
        league_ids = list(dict.fromkeys(requested_leagues))
    else:
        league_ids = sorted(path.stem for path in standings_dir.glob("*.csv"))

    targets: list[LeagueTarget] = []
    for league_id in league_ids:
        info = registry.get(league_id)
        standings_path = standings_dir / f"{league_id}.csv"
        if info is None:
            preflight.append(
                LeagueAudit(
                    league_id=league_id,
                    status="UNMAPPED",
                    message="Classifica locale senza voce in league_registry.csv.",
                )
            )
            continue
        if not standings_path.exists():
            preflight.append(
                LeagueAudit(
                    league_id=league_id,
                    status="LOCAL_MISSING",
                    message=f"Classifica locale non trovata: {standings_path}",
                )
            )
            continue
        targets.append(
            LeagueTarget(
                info=info,
                standings_path=standings_path,
                aliases=aliases.get(league_id, ()),
            )
        )
    return targets, preflight


def _csv_value(row: StandingRow | None, field_name: str) -> object:
    return "" if row is None else getattr(row, field_name)


def write_detailed_csv(audits: Iterable[LeagueAudit], path: Path, run_at: str) -> None:
    fieldnames = [
        "RunAt",
        "LeagueId",
        "LeagueStatus",
        "RemoteCountry",
        "RemoteLeague",
        "TournamentId",
        "StageId",
        "SourceUrl",
        "Status",
        "MatchMethod",
        "LocalTeam",
        "RemoteTeam",
        "NormalizedTeam",
        "NameIssue",
        "Differences",
    ]
    for metric in ALL_METRICS:
        label = "PPG" if metric == "ppg" else metric.title()
        fieldnames.extend((f"Local{label}", f"Remote{label}"))
    fieldnames.append("LeagueMessage")

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for audit in audits:
            rows = audit.comparison_rows or [
                ComparisonRow(league_id=audit.league_id, status=audit.status)
            ]
            for comparison in rows:
                record = {
                    "RunAt": run_at,
                    "LeagueId": audit.league_id,
                    "LeagueStatus": audit.status,
                    "RemoteCountry": audit.remote_country,
                    "RemoteLeague": audit.remote_league,
                    "TournamentId": audit.tournament_id,
                    "StageId": audit.stage_id,
                    "SourceUrl": audit.source_url,
                    "Status": comparison.status,
                    "MatchMethod": comparison.match_method,
                    "LocalTeam": comparison.local_team,
                    "RemoteTeam": comparison.remote_team,
                    "NormalizedTeam": comparison.normalized_team,
                    "NameIssue": comparison.name_issue,
                    "Differences": comparison.differences,
                    "LeagueMessage": audit.message,
                }
                for metric in ALL_METRICS:
                    label = "PPG" if metric == "ppg" else metric.title()
                    record[f"Local{label}"] = _csv_value(comparison.local, metric)
                    record[f"Remote{label}"] = _csv_value(comparison.remote, metric)
                writer.writerow(record)


def _markdown(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_summary_report(
    audits: list[LeagueAudit], path: Path, csv_path: Path, run_at: str
) -> None:
    by_status: dict[str, int] = {}
    for audit in audits:
        by_status[audit.status] = by_status.get(audit.status, 0) + 1
    all_rows = [row for audit in audits for row in audit.comparison_rows]
    real_differences = [
        row
        for row in all_rows
        if row.status
        in {
            "DIFFERENCE",
            "ALIAS_WITH_DIFFERENCES",
            "ALIAS_SUSPECTED_WITH_DIFFERENCES",
            "MISSING_ON_DIRETTA",
            "MISSING_LOCALLY",
        }
    ]
    alias_rows = [row for row in all_rows if row.name_issue]
    unavailable = [
        audit
        for audit in audits
        if audit.status
        in {"UNMAPPED", "UNAVAILABLE", "REMOTE_ERROR", "LOCAL_ERROR", "LOCAL_EMPTY", "LOCAL_MISSING"}
    ]

    lines = [
        "# Audit classifiche GioOver25 vs Diretta/Flashscore",
        "",
        f"Generato: **{run_at}**",
        "",
        f"- Leghe richieste: **{len(audits)}**",
        f"- Leghe confrontate: **{sum(bool(a.comparison_rows) for a in audits)}**",
        f"- Leghe OK: **{by_status.get('OK', 0) + by_status.get('OK_WITH_ALIASES', 0)}**",
        f"- Leghe con differenze reali: **{by_status.get('DIFFERENCES', 0)}**",
        f"- Leghe da rivedere per alias: **{by_status.get('ALIAS_REVIEW', 0)}**",
        f"- Leghe non mappate/non disponibili/in errore: **{len(unavailable)}**",
        f"- Righe squadra con differenze reali: **{len(real_differences)}**",
        f"- Righe squadra con alias noto o sospetto: **{len(alias_rows)}**",
        f"- Dettaglio CSV: `{csv_path.name}`",
        "",
        "## Sintesi per lega",
        "",
        "| LeagueId | Stato | Locale | Diretta | Match | Alias | Differenze | Note |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for audit in audits:
        lines.append(
            "| {league} | {status} | {local} | {remote} | {matches} | {aliases} | "
            "{differences} | {message} |".format(
                league=_markdown(audit.league_id),
                status=_markdown(audit.status),
                local=audit.local_count,
                remote=audit.remote_count,
                matches=audit.matches,
                aliases=audit.aliases,
                differences=audit.differences,
                message=_markdown(audit.message),
            )
        )

    lines.extend(
        [
            "",
            "## Differenze principali",
            "",
        ]
    )
    if not real_differences:
        lines.append("Nessuna differenza reale rilevata nelle leghe confrontate.")
    else:
        lines.extend(
            [
                "| LeagueId | Stato | Squadra locale | Squadra Diretta | Campi diversi |",
                "|---|---|---|---|---|",
            ]
        )
        for row in real_differences[:200]:
            lines.append(
                f"| {_markdown(row.league_id)} | {_markdown(row.status)} | "
                f"{_markdown(row.local_team)} | {_markdown(row.remote_team)} | "
                f"{_markdown(row.differences)} |"
            )
        if len(real_differences) > 200:
            lines.append(
                f"\n_Altre {len(real_differences) - 200} righe sono disponibili nel CSV._"
            )

    lines.extend(["", "## Alias da verificare", ""])
    if not alias_rows:
        lines.append("Nessun alias rilevato.")
    else:
        lines.extend(
            [
                "| LeagueId | Tipo | Locale | Diretta | Esito |",
                "|---|---|---|---|---|",
            ]
        )
        for row in alias_rows[:100]:
            lines.append(
                f"| {_markdown(row.league_id)} | {_markdown(row.name_issue)} | "
                f"{_markdown(row.local_team)} | {_markdown(row.remote_team)} | "
                f"{_markdown(row.status)} |"
            )

    lines.extend(["", "## Leghe non confrontate", ""])
    if not unavailable:
        lines.append("Tutte le leghe richieste sono state confrontate.")
    else:
        for audit in unavailable:
            lines.append(
                f"- **{audit.league_id}** — {audit.status}: {audit.message}"
            )

    lines.extend(
        [
            "",
            "## Interpretazione",
            "",
            "- `ALIAS_ONLY` indica nomi diversi ricondotti alla stessa identità senza scarti statistici.",
            "- `ALIAS_SUSPECTED` indica un abbinamento testuale molto probabile ma non ancora censito nel dizionario squadre.",
            "- `DIFFERENCE` e gli stati `MISSING_*` sono differenze sostanziali da verificare.",
            "- L'audit non modifica né gli storici né le classifiche calcolate.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Confronta in sola lettura le classifiche locali con Diretta/Flashscore "
            "e produce un report Markdown più un CSV dettagliato."
        )
    )
    parser.add_argument(
        "--league-id",
        action="append",
        help="Limita l'audit a una LeagueId; ripetibile.",
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--league-aliases", type=Path, default=DEFAULT_LEAGUE_ALIASES)
    parser.add_argument("--standings-dir", type=Path, default=DEFAULT_STANDINGS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--timeout", type=int, default=25, help="Timeout HTTP in secondi.")
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Numero massimo di leghe scaricate in parallelo (default: 4).",
    )
    parser.add_argument(
        "--fail-on-difference",
        action="store_true",
        help="Restituisce exit code 1 se esistono differenze reali.",
    )
    parser.add_argument("--verbose", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    if args.workers < 1:
        raise SystemExit("--workers deve essere almeno 1")
    if args.timeout < 1:
        raise SystemExit("--timeout deve essere almeno 1")

    targets, audits = discover_targets(
        args.registry,
        args.standings_dir,
        args.league_aliases,
        args.league_id,
    )
    LOGGER.info("Leghe da analizzare: %d", len(targets))

    # Carica il dizionario prima dei worker: resta una cache read-only condivisa.
    normalize_team_name("__preload__", "__preload__")
    with ThreadPoolExecutor(max_workers=min(args.workers, max(len(targets), 1))) as executor:
        future_to_target = {
            executor.submit(audit_league, target, args.timeout): target
            for target in targets
        }
        for future in as_completed(future_to_target):
            target = future_to_target[future]
            try:
                audit = future.result()
            except Exception as exc:  # ultima barriera: una lega non blocca le altre
                audit = LeagueAudit(
                    league_id=target.info.league_id,
                    status="REMOTE_ERROR",
                    message=f"{type(exc).__name__}: {exc}",
                )
            audits.append(audit)
            log = LOGGER.warning if audit.status in {
                "UNMAPPED",
                "UNAVAILABLE",
                "REMOTE_ERROR",
                "LOCAL_ERROR",
                "LOCAL_EMPTY",
                "LOCAL_MISSING",
            } else LOGGER.info
            log(
                "%s: %s (locale=%d, Diretta=%d, differenze=%d, alias=%d)",
                audit.league_id,
                audit.status,
                audit.local_count,
                audit.remote_count,
                audit.differences,
                audit.aliases,
            )

    audits.sort(key=lambda audit: audit.league_id)
    run_at = datetime.now().astimezone().isoformat(timespec="seconds")
    csv_path = args.output_dir / "diretta_standings_audit_details.csv"
    report_path = args.output_dir / "diretta_standings_audit.md"
    write_detailed_csv(audits, csv_path, run_at)
    write_summary_report(audits, report_path, csv_path, run_at)

    LOGGER.info("Report sintetico: %s", report_path)
    LOGGER.info("Dettaglio CSV: %s", csv_path)
    real_difference_count = sum(audit.differences for audit in audits)
    unavailable_count = sum(
        audit.status
        in {"UNMAPPED", "UNAVAILABLE", "REMOTE_ERROR", "LOCAL_ERROR", "LOCAL_EMPTY", "LOCAL_MISSING"}
        for audit in audits
    )
    LOGGER.info(
        "Completato: %d differenze reali; %d leghe non confrontate.",
        real_difference_count,
        unavailable_count,
    )
    return 1 if args.fail_on_difference and real_difference_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
