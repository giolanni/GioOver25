"""Onboarding massivo Tier 1-3 da piano validato.

Default dry-run. Con --apply processa ogni competizione in modo isolato:
recupera i risultati della stagione corrente, crea lo storico e aggiunge il
registry solo se il backfill contiene almeno una partita conclusa.

Teams/ExpectedRounds/HomeAway restano neutri quando non sono determinabili
dal piano: nessun formato di campionato viene inventato.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path

from tools.backfill_league_daily import slug
from tools.flashscore_history import fetch_embedded_results
from tools.prepare_input import ROOT
from tools.bonifica_storici_diretta import RESULTS_FEED, parse_results_feed
from analysis.audit_diretta_standings import search_tournaments, _request_text

DIRETTA_BASE = "https://www.diretta.it"

def _walk_values(obj, fragment: str):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if fragment in str(key).casefold():
                yield value
            yield from _walk_values(value, fragment)
    elif isinstance(obj, list):
        for value in obj:
            yield from _walk_values(value, fragment)

def _fallback_urls(source_league: str, tournament_ids: set[str], stage_ids: set[str], timeout: int = 20):
    """Trova URL pubbliche usando gli ID Flashscore del discovery, non il nome/slug."""
    urls = []
    try:
        rows = search_tournaments(source_league, timeout)
    except Exception:
        return urls
    for raw in rows:
        tournament = raw.get("defaultTournament") or {}
        tid = str(tournament.get("id", "")).strip()
        if tournament_ids and tid not in tournament_ids:
            continue
        # Lo stage e' decisivo per Apertura/Clausura e gruppi interni.
        raw_stage_ids = {
            str(v).strip()
            for v in _walk_values(raw, "stage")
            if isinstance(v, (str, int)) and str(v).strip()
        }
        if stage_ids and raw_stage_ids and not (stage_ids & raw_stage_ids):
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
    return list(dict.fromkeys(urls))

def _direct_feed_results(source_league: str, tournament_ids: set[str], stage_ids: set[str], timeout: int = 20):
    """Recupera risultati dal feed stagionale usando gli ID della discovery."""
    attempts = []
    try:
        rows = search_tournaments(source_league, timeout)
    except Exception as exc:
        return [], "", [f"{source_league}: ID search {type(exc).__name__}: {exc}"]

    for raw in rows:
        tournament = raw.get("defaultTournament") or {}
        tid = str(tournament.get("id", "")).strip()
        if tournament_ids and tid not in tournament_ids:
            continue

        raw_stage_ids = {
            str(v).strip()
            for v in _walk_values(raw, "stage")
            if isinstance(v, (str, int)) and str(v).strip()
        }
        if stage_ids and raw_stage_ids and not (stage_ids & raw_stage_ids):
            continue

        season_ids = []
        for value in _walk_values(raw, "season"):
            if isinstance(value, dict):
                for key in ("id", "seasonId", "season_id"):
                    sid = str(value.get(key, "")).strip()
                    if sid:
                        season_ids.append(sid)
            elif isinstance(value, (str, int)):
                sid = str(value).strip()
                if len(sid) >= 6:
                    season_ids.append(sid)
        # Alcune risposte espongono seasonId come chiave diretta.
        for fragment in ("seasonid", "season_id"):
            for value in _walk_values(raw, fragment):
                if isinstance(value, (str, int)) and str(value).strip():
                    season_ids.append(str(value).strip())

        for season in dict.fromkeys(season_ids):
            url = RESULTS_FEED.format(tournament=tid, season=season)
            try:
                payload = _request_text(url, timeout, None)
                matches = parse_results_feed(payload)
            except Exception as exc:
                attempts.append(f"{source_league}: direct feed {tid}/{season} {type(exc).__name__}: {exc}")
                continue
            if matches:
                return matches, f"feed:{tid}/{season}", attempts
            attempts.append(f"{source_league}: direct feed {tid}/{season} vuoto")

    if not attempts:
        attempts.append(f"{source_league}: nessun seasonId compatibile con TournamentId/StageId")
    return [], "", attempts


def _fetch_source(source_league: str, country: str, tournament_ids: set[str], stage_ids: set[str]):
    """Prima URL leggibile; poi fallback ID-driven per fasi con slug non pubblico."""
    primary = f"{DIRETTA_BASE}/calcio/{slug(country)}/{slug(source_league)}/risultati/"
    attempts = [primary]
    errors = []
    try:
        ids, matches, payload = fetch_embedded_results(primary)
        if matches:
            return matches, primary, errors
        errors.append(f"{source_league}: primary senza risultati")
    except Exception as exc:
        errors.append(f"{source_league}: primary {type(exc).__name__}: {exc}")

    # Prima del fallback URL, usa direttamente tournament/season feed.
    matches, resolved, direct_errors = _direct_feed_results(
        source_league, tournament_ids, stage_ids
    )
    errors.extend(direct_errors)
    if matches:
        return matches, resolved, errors

    for url in _fallback_urls(source_league, tournament_ids, stage_ids):
        if url in attempts:
            continue
        attempts.append(url)
        try:
            _, matches, _ = fetch_embedded_results(url)
            if matches:
                return matches, url, errors
        except Exception as exc:
            errors.append(f"{source_league}: fallback {type(exc).__name__}: {exc}")
    return [], "", errors


def latest_plan() -> Path:
    files = sorted((ROOT / "data" / "debug").glob("league_onboarding_plan_*.csv"))
    if not files:
        raise SystemExit("Nessun league_onboarding_plan_*.csv trovato")
    return files[-1]


def load_registry(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as h:
        return list(csv.DictReader(h, delimiter=";"))


def write_registry(path: Path, rows, fieldnames):
    rows.sort(key=lambda r: (r.get("LeagueId") or "").casefold())
    with path.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fieldnames, delimiter=";", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def write_history(path: Path, country: str, league: str, matches):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.writer(h, delimiter=";", lineterminator="\n")
        w.writerow(["Country","League","Round","MatchDate","Home","Away","HG","AG","Notes"])
        for m in sorted(matches, key=lambda x: (x.date, x.round, x.home, x.away)):
            w.writerow([country, league, m.round, m.date, m.home, m.away, m.hg, m.ag, ""])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="Piano; default: ultimo")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="Prime N competizioni; 0=tutte")
    args = ap.parse_args()

    source = ROOT / args.input if args.input else latest_plan()
    with source.open(encoding="utf-8-sig", newline="") as h:
        plan = list(csv.DictReader(h, delimiter=";"))
    if args.limit:
        plan = plan[:args.limit]

    registry_path = ROOT / "data" / "league_registry.csv"
    registry = load_registry(registry_path)
    fields = list(registry[0].keys())
    existing_ids = {(r.get("LeagueId") or "").casefold() for r in registry}

    summary = []
    pending_registry = []
    pending_histories = []

    for i, row in enumerate(plan, 1):
        league_id = row["LeagueId"]
        country = row["Country"]
        action = row["Action"]
        source_leagues = [x.strip() for x in row["SourceLeagues"].split("|") if x.strip()]

        # Le righe MERGE_EXISTING sono solo diagnostiche: non fare rete e non
        # fondere automaticamente fasi/playoff negli storici gia' esistenti.
        if action == "MERGE_EXISTING":
            status = "SKIP_PHASE_MERGE"
            print(f"[{i}/{len(plan)}] {league_id} | {action} | matches=0 | {status}")
            summary.append({
                "LeagueId": league_id, "Action": action, "Status": status,
                "Matches": 0, "Sources": " | ".join(source_leagues),
                "Errors": "", "ResolvedSources": "",
            })
            continue

        all_matches = {}
        errors = []
        resolved_sources = []
        tournament_ids = {x.strip() for x in row.get("TournamentIds", "").split("|") if x.strip()}
        stage_ids = {x.strip() for x in row.get("TournamentStageIds", "").split("|") if x.strip()}
        for source_league in source_leagues:
            matches, resolved_url, source_errors = _fetch_source(source_league, country, tournament_ids, stage_ids)
            errors.extend(source_errors)
            if resolved_url:
                resolved_sources.append(f"{source_league} => {resolved_url}")
            for m in matches:
                all_matches[(m.date, m.home.casefold(), m.away.casefold())] = m

        matches = list(all_matches.values())
        status = "READY"
        if action == "CREATE" and league_id.casefold() in existing_ids:
            status = "SKIP_EXISTS"
        elif action == "CREATE" and not matches:
            status = "NO_RESULTS"
        elif errors:
            status = "READY_PARTIAL"

        print(f"[{i}/{len(plan)}] {league_id} | {action} | matches={len(matches)} | {status}")

        if action == "CREATE" and status in {"READY", "READY_PARTIAL"}:
            hist = ROOT / "data" / "storico" / "risultati" / f"{league_id}.csv"
            if hist.exists():
                status = "SKIP_HISTORY_EXISTS"
            else:
                new = {k: "" for k in fields}
                new.update({
                    "LeagueId": league_id,
                    "Country": country,
                    "League": row["League"],
                    "Teams": "0",
                    "ExpectedRounds": "0",
                    "HomeAway": "",
                    "Notes": "Onboarding automatico Tier 1-3; formato competizione da completare",
                    "CompetitionGroup": "",
                })
                pending_registry.append(new)
                pending_histories.append((hist, country, row["League"], matches))
                existing_ids.add(league_id.casefold())

        summary.append({
            "LeagueId": league_id, "Action": action, "Status": status,
            "Matches": len(matches), "Sources": " | ".join(source_leagues),
            "Errors": " | ".join(errors),
            "ResolvedSources": " | ".join(resolved_sources),
        })

    out = ROOT / "data" / "debug" / f"tier123_bulk_onboarding_{datetime.now():%Y%m%d-%H%M%S}.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["LeagueId","Action","Status","Matches","Sources","Errors","ResolvedSources"], delimiter=";")
        w.writeheader()
        w.writerows(summary)

    if args.apply:
        # Scritture soltanto dopo che l'intero batch e' stato analizzato.
        created = []
        try:
            for hist, country, league, matches in pending_histories:
                write_history(hist, country, league, matches)
                created.append(hist)
            write_registry(registry_path, registry + pending_registry, fields)
        except Exception:
            for path in created:
                path.unlink(missing_ok=True)
            raise
        print(f"[APPLY] CREATE={len(pending_registry)}")
    else:
        print(f"[DRY-RUN] CREATE_READY={len(pending_registry)} | nessuna modifica")

    counts = {}
    for r in summary:
        counts[r["Status"]] = counts.get(r["Status"], 0) + 1
    print("[SUMMARY] " + " | ".join(f"{k}={v}" for k,v in sorted(counts.items())))
    print(f"[OUTPUT] {out}")


if __name__ == "__main__":
    main()
