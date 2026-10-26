"""Bonifica gli storici risultati confrontandoli con Diretta/Flashscore.

Default: audit soltanto. Con --apply riscrive esclusivamente le leghe per cui
il mapping Diretta e il confronto sono considerati sicuri. Ogni problema di
una singola lega viene loggato in un file dedicato senza interrompere il batch.

Esempi:
  python -m tools.bonifica_storici_diretta
  python -m tools.bonifica_storici_diretta --league-id Italy_SerieA
  python -m tools.bonifica_storici_diretta --apply
"""
from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import shutil
import sys
import time
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from analysis.audit_diretta_standings import (
    LeagueAlias, LeagueTarget, _request_text, load_diretta_aliases,
    search_tournaments, select_tournament_candidates,
)
from gioover25.registry import load_league_registry
from gioover25.team_names import normalize_team_name

RESULTS_DIR = ROOT / "data" / "storico" / "risultati"
REGISTRY = ROOT / "data" / "league_registry.csv"
ALIASES = ROOT / "data" / "league_aliases.csv"
LOG_ROOT = ROOT / "data" / "debug" / "bonifica_storici_diretta"
RESULTS_FEED = "https://global.flashscore.ninja/323/x/feed/tr_1_{tournament}_{season}_0_2_it_1"
DIRETTA_BASE = "https://www.diretta.it"
FLASHSCORE_BASE = "https://www.flashscore.com"
LOGGER = logging.getLogger("bonifica_storici_diretta")


@dataclass(frozen=True)
class Result:
    date: str
    home: str
    away: str
    hg: int
    ag: int
    round: str = ""

@dataclass
class LeagueOutcome:
    league_id: str
    status: str
    local: int = 0
    remote: int = 0
    equal: int = 0
    missing_local: int = 0
    extra_local: int = 0
    score_diff: int = 0
    applied: bool = False
    message: str = ""


def compact(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", "", text)


def parse_records(payload: str) -> list[dict[str, str]]:
    out = []
    for raw in (payload or "").split("~"):
        row = {}
        for item in raw.split("¬"):
            if "÷" in item:
                k, v = item.split("÷", 1)
                row[k] = v
        if row:
            out.append(row)
    return out


def parse_results_feed(payload: str) -> list[Result]:
    out = []
    current_round = ""
    for row in parse_records(payload):
        # Livesport usa ER/AC per etichette di fase/giornata a seconda del feed.
        label = row.get("ER") or row.get("AC") or ""
        m = re.search(r"(?:Giornata|Round)\s*(\d+)", label, re.I)
        if m:
            current_round = m.group(1)
        if not all(row.get(k) for k in ("AA", "AD", "AE", "AF")):
            continue
        hg, ag = row.get("AG", ""), row.get("AH", "")
        if not (hg.isdigit() and ag.isdigit()):
            continue
        try:
            date = datetime.fromtimestamp(int(row["AD"])).astimezone().date().isoformat()
        except (ValueError, TypeError, OSError):
            continue
        out.append(Result(date, row["AE"].strip(), row["AF"].strip(), int(hg), int(ag), current_round))
    # deduplica per event identity visibile
    unique = {}
    for r in out:
        unique[(r.date, compact(r.home), compact(r.away))] = r
    return list(unique.values())


def load_local(path: Path) -> tuple[list[dict[str, str]], list[Result]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        raw = list(csv.DictReader(f, delimiter=";"))
    out = []
    for row in raw:
        try:
            out.append(Result(
                str(row.get("MatchDate", "")).strip(),
                str(row.get("Home", "")).strip(),
                str(row.get("Away", "")).strip(),
                int(str(row.get("HG", "")).strip()),
                int(str(row.get("AG", "")).strip()),
                str(row.get("Round", "")).strip(),
            ))
        except ValueError:
            continue
    return raw, out


def identity(league_id: str, team: str) -> str:
    return compact(normalize_team_name(league_id, team))


def key(league_id: str, r: Result) -> tuple[str, str, str]:
    return r.date, identity(league_id, r.home), identity(league_id, r.away)


def team_overlap(league_id: str, local: Iterable[Result], remote: Iterable[Result]) -> tuple[int, int]:
    lt = {identity(league_id, x) for r in local for x in (r.home, r.away)}
    rt = {identity(league_id, x) for r in remote for x in (r.home, r.away)}
    return len(lt & rt), len(lt | rt)


def log_file(log_dir: Path, league_id: str, text: str) -> None:
    log_dir.mkdir(parents=True, exist_ok=True)
    (log_dir / f"{league_id}.log").write_text(text.rstrip() + "\n", encoding="utf-8")


def _search_rows(target: LeagueTarget, timeout: int):
    queries = []
    for alias in target.aliases:
        if alias.league:
            queries += [alias.league, f"{alias.country} {alias.league}".strip()]
    queries += [target.info.league, f"{target.info.country} {target.info.league}".strip()]
    rows, errors = [], []
    for q in dict.fromkeys(x for x in queries if x):
        try:
            rows += search_tournaments(q, timeout)
        except Exception as exc:
            errors.append(f"{q!r}: {type(exc).__name__}: {exc}")
    return rows, errors


def discover(target: LeagueTarget, timeout: int):
    rows, errors = _search_rows(target, timeout)
    candidates = select_tournament_candidates(rows, target)
    unique = {}
    for candidate in candidates:
        k = candidate.tournament_id
        if k not in unique or candidate.score > unique[k].score:
            unique[k] = candidate
    return sorted(unique.values(), key=lambda x: x.score, reverse=True), rows, errors


def _walk_values(obj, key_fragment: str):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if key_fragment in str(k).casefold():
                yield v
            yield from _walk_values(v, key_fragment)
    elif isinstance(obj, list):
        for item in obj:
            yield from _walk_values(item, key_fragment)


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().casefold()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text


def _candidate_page_urls(search_rows, candidate, target=None):
    urls = []
    for raw in search_rows:
        tournament = raw.get("defaultTournament") or {}
        if str(tournament.get("id", "")).strip() != candidate.tournament_id:
            continue
        for value in list(_walk_values(raw, "url")) + list(_walk_values(raw, "path")):
            if not isinstance(value, str) or not value.strip():
                continue
            value = value.strip()
            if value.startswith("/"):
                value = DIRETTA_BASE + value
            elif not value.startswith("http"):
                continue
            if "/results" not in value.rstrip("/"):
                value = value.rstrip("/") + "/results/"
            urls.append(value)

    # La search API di Livesport normalmente restituisce gli ID ma non la URL
    # pubblica. Diretta usa URL leggibili e stabili per paese/competizione.
    if target is not None:
        country_names = [a.country for a in target.aliases if a.country]
        league_names = [a.league for a in target.aliases if a.league]
        country_names += [target.info.country]
        league_names += [target.info.league]
        for country in dict.fromkeys(x for x in country_names if x):
            for league in dict.fromkeys(x for x in league_names if x):
                urls.append(f"{DIRETTA_BASE}/calcio/{_slug(country)}/{_slug(league)}/risultati/")
                urls.append(f"{DIRETTA_BASE}/{_slug(league)}/risultati/")
                urls.append(f"{FLASHSCORE_BASE}/football/{_slug(country)}/{_slug(league)}/results/")
    return list(dict.fromkeys(urls))

def _extract_season_ids(text: str):
    ids = []
    patterns = (
        r'["\\\']seasonId["\\\']\\s*[:=]\\s*["\\\']?([A-Za-z0-9_-]{6,})',
        r'["\\\']season_id["\\\']\\s*[:=]\\s*["\\\']?([A-Za-z0-9_-]{6,})',
        r'\\bseasonId\\W+([A-Za-z0-9_-]{6,})',
    )
    for pattern in patterns:
        ids += re.findall(pattern, text, flags=re.I)
    return list(dict.fromkeys(ids))


def _html_feed_diagnostics(html: str, tournament_id: str) -> list[str]:
    """Estrae solo piccoli indizi utili dal bootstrap HTML, senza loggare 700 KB."""
    out = []
    needles = [tournament_id, "initialFeeds", "tf_1_", "tr_1_", "tournament_id", "season_id"]
    for needle in needles:
        positions = [m.start() for m in re.finditer(re.escape(needle), html, flags=re.I)]
        out.append(f"HTML needle {needle!r}: occurrences={len(positions)}")
        for pos in positions[:3]:
            snippet = re.sub(r"\\s+", " ", html[max(0, pos-180):pos+260])
            out.append(f"  ...{snippet}...")
    return out


def _extract_initial_results(html: str):
    # Diretta/Livesport può esporre il feed iniziale dei risultati
    # con nomi diversi a seconda della versione della pagina.
    #
    # Formato attuale osservato:
    #   cjs.initialFeeds["summary-results"] = {
    #       data: `SA÷1¬~ZA÷...`
    #   }
    #
    # Manteniamo anche i nomi precedenti come fallback.
    for name in ("summary-results", "results", "results_s"):
        m = re.search(
            rf'initialFeeds\s*\[\s*["\']{re.escape(name)}["\']\s*\].*?data\s*:\s*`(.*?)`',
            html,
            flags=re.S,
        )
        if m:
            return m.group(1)

    return ""


def _fetch_page(url: str, timeout: int) -> str:
    req = Request(url, headers={
        "User-Agent": "Mozilla/5.0 (GioOver25 DirettaHistoryAudit)",
        "Accept-Language": "it-IT,it;q=0.9,en;q=0.7",
    })
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")


def fetch_remote(target: LeagueTarget, local: list[Result], timeout: int):
    candidates, search_rows, search_errors = discover(target, timeout)
    attempts = []
    best = None
    for candidate in candidates[:5]:
        season_ids = []
        page_urls = _candidate_page_urls(search_rows, candidate, target)
        for page_url in page_urls:
            try:
                html = _fetch_page(page_url, timeout)
                attempts.append(f"{page_url}: pagina letta ({len(html)} bytes)")
                attempts.extend(_html_feed_diagnostics(html, candidate.tournament_id))
                embedded = _extract_initial_results(html)
                if embedded:
                    rows = parse_results_feed(embedded)
                    attempts.append(f"{page_url}: embedded results={len(rows)}")
                    if rows:
                        overlap, union = team_overlap(target.info.league_id, local, rows)
                        ratio = overlap / union if union else 0.0
                        coverage = min(len(rows), len(local)) / len(local) if local else 0.0
                        rank = (ratio, coverage, overlap, len(rows), candidate.score)
                        if best is None or rank > best[0]:
                            best = (rank, candidate, "embedded", rows, page_url)
                found_seasons = _extract_season_ids(html)
                season_ids += found_seasons
                attempts.append(f"{page_url}: season ids={found_seasons or 'NESSUNO'}")
            except Exception as exc:
                attempts.append(f"{page_url}: {type(exc).__name__}: {exc}")

        # stageWithStatsDataIds NON sono season ids. Il vecchio script li usava
        # erroneamente nel feed tr_1 e per questo otteneva solo feed vuoti.
        # I season id vengono ricavati dalla pagina pubblica della competizione.
        for season in dict.fromkeys(season_ids):
            url = RESULTS_FEED.format(tournament=candidate.tournament_id, season=season)
            try:
                payload = _request_text(url, timeout, None)
                rows = parse_results_feed(payload)
            except Exception as exc:
                attempts.append(f"{url}: {type(exc).__name__}: {exc}")
                continue
            if not rows:
                attempts.append(f"{url}: feed vuoto")
                continue
            overlap, union = team_overlap(target.info.league_id, local, rows)
            ratio = overlap / union if union else 0.0
            coverage = min(len(rows), len(local)) / len(local) if local else 0.0
            rank = (ratio, coverage, overlap, len(rows), candidate.score)
            if best is None or rank > best[0]:
                best = (rank, candidate, season, rows, url)
        if not season_ids and not page_urls:
            attempts.append(
                f"{candidate.name}/{candidate.tournament_id}: URL pagina/season id non esposti dalla search"
            )
    return best, search_errors + attempts

def compare(league_id: str, local: list[Result], remote: list[Result]):
    lm = {key(league_id, r): r for r in local}
    rm = {key(league_id, r): r for r in remote}
    common = lm.keys() & rm.keys()
    score_diff = [(lm[k], rm[k]) for k in common if (lm[k].hg, lm[k].ag) != (rm[k].hg, rm[k].ag)]
    missing = [rm[k] for k in rm.keys() - lm.keys()]
    extra = [lm[k] for k in lm.keys() - rm.keys()]
    equal = len(common) - len(score_diff)
    return equal, missing, extra, score_diff


def write_history(path: Path, remote: list[Result], local: list[Result], backup_dir: Path):
    # Mantiene solo risultati Diretta fino all'ultima data locale: evita di importare
    # accidentalmente risultati/future season non appartenenti all'orizzonte locale.
    cutoff = max((r.date for r in local), default="9999-12-31")
    rows = [r for r in remote if r.date <= cutoff]
    if not rows:
        raise ValueError("nessun risultato remoto entro il cutoff locale")
    backup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_dir / path.name)
    rows.sort(key=lambda r: (r.date, int(r.round) if r.round.isdigit() else 9999, r.home, r.away))
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["Country", "League", "Round", "MatchDate", "Home", "Away", "HG", "AG", "Notes"])
        # Country/League vengono preservati dal file locale quando possibile.
        with (backup_dir / path.name).open(encoding="utf-8-sig", newline="") as old:
            old_rows = list(csv.DictReader(old, delimiter=";"))
        country = next((x.get("Country", "") for x in old_rows if x.get("Country")), "")
        league = next((x.get("League", "") for x in old_rows if x.get("League")), "")
        for r in rows:
            w.writerow([country, league, r.round, r.date, r.home, r.away, r.hg, r.ag, ""])


def main() -> int:
    p = argparse.ArgumentParser(description="Confronta/bonifica gli storici con i risultati Diretta.")
    p.add_argument("--league-id", action="append", help="Limita a una o più LeagueId.")
    p.add_argument("--apply", action="store_true", help="Applica solo bonifiche ad alta confidenza.")
    p.add_argument("--timeout", type=int, default=20)
    p.add_argument("--sleep", type=float, default=0.20, help="Pausa tra leghe.")
    p.add_argument("--min-overlap", type=float, default=0.55, help="Overlap minimo squadre per applicare.")
    p.add_argument("--registry", type=Path, default=REGISTRY)
    p.add_argument("--aliases", type=Path, default=ALIASES)
    p.add_argument("--results-dir", type=Path, default=RESULTS_DIR)
    p.add_argument("--log-dir", type=Path, default=LOG_ROOT)
    args = p.parse_args()

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = args.log_dir / stamp
    error_dir = run_dir / "errors"
    detail_dir = run_dir / "leagues"
    backup_dir = run_dir / "backup"
    run_dir.mkdir(parents=True, exist_ok=True)

    aliases = load_diretta_aliases(args.aliases)
    registry = load_league_registry(args.registry)
    wanted = set(args.league_id or [])
    infos = [x for x in registry.values() if not wanted or x.league_id in wanted]
    outcomes = []

    for index, info in enumerate(infos, 1):
        lid = info.league_id
        path = args.results_dir / f"{lid}.csv"
        target = LeagueTarget(info=info, standings_path=path, aliases=aliases.get(lid, ()))
        prefix = f"[{index}/{len(infos)}] {lid}"
        try:
            if not path.exists():
                outcome = LeagueOutcome(lid, "FILE_MISSING", message=str(path))
                outcomes.append(outcome)
                log_file(error_dir, lid, f"{prefix}\nFILE_MISSING: {path}")
                print(f"{prefix}: FILE_MISSING")
                continue
            _, local = load_local(path)
            if not local:
                outcome = LeagueOutcome(lid, "LOCAL_EMPTY")
                outcomes.append(outcome)
                log_file(error_dir, lid, f"{prefix}\nLOCAL_EMPTY")
                print(f"{prefix}: LOCAL_EMPTY")
                continue

            best, discovery_log = fetch_remote(target, local, args.timeout)
            if best is None:
                outcome = LeagueOutcome(lid, "DIRETTA_NOT_FOUND", local=len(local))
                outcomes.append(outcome)
                log_file(error_dir, lid, f"{prefix}\nDIRETTA_NOT_FOUND\n" + "\n".join(discovery_log))
                print(f"{prefix}: DIRETTA_NOT_FOUND")
                continue

            rank, candidate, stage, remote, source_url = best
            overlap_ratio = rank[0]
            equal, missing, extra, score_diff = compare(lid, local, remote)
            safe = overlap_ratio >= args.min_overlap and equal > 0
            status = "OK" if not missing and not extra and not score_diff else "DIFFERENCES"
            outcome = LeagueOutcome(lid, status, len(local), len(remote), equal, len(missing), len(extra), len(score_diff))
            detail = [
                prefix,
                f"status={status}",
                f"tournament={candidate.name} country={candidate.country} tournament_id={candidate.tournament_id} stage={stage}",
                f"source={source_url}",
                f"team_overlap={overlap_ratio:.3f}",
                f"local={len(local)} remote={len(remote)} equal={equal} missing_local={len(missing)} extra_local={len(extra)} score_diff={len(score_diff)}",
            ]
            if missing:
                detail.append("\nMISSING_LOCAL:")
                detail += [f"{r.date};{r.home};{r.away};{r.hg};{r.ag}" for r in missing]
            if extra:
                detail.append("\nEXTRA_LOCAL:")
                detail += [f"{r.date};{r.home};{r.away};{r.hg};{r.ag}" for r in extra]
            if score_diff:
                detail.append("\nSCORE_DIFF:")
                detail += [f"{a.date};{a.home};{a.away};LOCAL={a.hg}-{a.ag};DIRETTA={b.hg}-{b.ag}" for a,b in score_diff]
            log_file(detail_dir, lid, "\n".join(detail))

            if args.apply and status == "DIFFERENCES" and safe:
                write_history(path, remote, local, backup_dir)
                outcome.applied = True
            elif args.apply and status == "DIFFERENCES" and not safe:
                outcome.status = "AMBIGUOUS"
                outcome.message = f"team_overlap={overlap_ratio:.3f}; equal={equal}"
                log_file(error_dir, lid, "\n".join(detail + ["", "NOT_APPLIED: mapping/confronto non abbastanza sicuro"]))

            outcomes.append(outcome)
            suffix = " APPLIED" if outcome.applied else ""
            print(f"{prefix}: {outcome.status}{suffix}")
        except Exception as exc:
            outcome = LeagueOutcome(lid, "ERROR", message=f"{type(exc).__name__}: {exc}")
            outcomes.append(outcome)
            log_file(error_dir, lid, f"{prefix}\n{type(exc).__name__}: {exc}")
            LOGGER.exception("%s fallita", lid)
            print(f"{prefix}: ERROR")
        finally:
            if args.sleep:
                time.sleep(args.sleep)

    summary = run_dir / "summary.csv"
    with summary.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";", lineterminator="\n")
        w.writerow(["LeagueId","Status","Local","Diretta","Equal","MissingLocal","ExtraLocal","ScoreDiff","Applied","Message"])
        for x in outcomes:
            w.writerow([x.league_id,x.status,x.local,x.remote,x.equal,x.missing_local,x.extra_local,x.score_diff,"SI" if x.applied else "NO",x.message])

    counts = {}
    for x in outcomes:
        counts[x.status] = counts.get(x.status, 0) + 1
    (run_dir / "run.json").write_text(json.dumps({
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "apply": args.apply,
        "total": len(outcomes),
        "status_counts": counts,
        "summary": str(summary),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[DONE] {len(outcomes)} leghe. Report: {summary}")
    return 1 if any(x.status == "ERROR" for x in outcomes) else 0


if __name__ == "__main__":
    raise SystemExit(main())
