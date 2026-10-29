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
        source_leagues = [x.strip() for x in row["SourceLeagues"].split("|") if x.strip()]
        all_matches = {}
        errors = []
        for source_league in source_leagues:
            url = f"https://www.diretta.it/calcio/{slug(country)}/{slug(source_league)}/risultati/"
            try:
                _, matches, _ = fetch_embedded_results(url)
                for m in matches:
                    all_matches[(m.date, m.home.casefold(), m.away.casefold())] = m
            except Exception as exc:
                errors.append(f"{source_league}: {type(exc).__name__}: {exc}")

        matches = list(all_matches.values())
        action = row["Action"]
        status = "READY"
        if action == "CREATE" and league_id.casefold() in existing_ids:
            status = "SKIP_EXISTS"
        elif action == "CREATE" and not matches:
            status = "NO_RESULTS"
        elif action == "MERGE_EXISTING":
            status = "MERGE_PENDING"
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
        })

    out = ROOT / "data" / "debug" / f"tier123_bulk_onboarding_{datetime.now():%Y%m%d-%H%M%S}.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=["LeagueId","Action","Status","Matches","Sources","Errors"], delimiter=";")
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
