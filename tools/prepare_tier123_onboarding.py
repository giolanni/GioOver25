"""Prepara il piano massivo di onboarding delle leghe Tier 1-3.

Legge l'ultimo league_onboarding_candidates_*.csv prodotto da
tools.select_league_tiers e lo riduce a una riga per CanonicalLeagueId.

Non modifica registry o storici. L'output e' il contratto di input del
successivo backfill massivo.
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from tools.prepare_input import ROOT, load_registry


def latest_candidates() -> Path:
    files = sorted((ROOT / "data" / "debug").glob("league_onboarding_candidates_*.csv"))
    if not files:
        raise SystemExit("Nessun league_onboarding_candidates_*.csv trovato")
    return files[-1]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", help="CSV candidati; default: ultimo")
    args = ap.parse_args()
    source = ROOT / args.input if args.input else latest_candidates()

    with source.open(encoding="utf-8-sig", newline="") as h:
        rows = list(csv.DictReader(h, delimiter=";"))

    registry = load_registry(ROOT / "data" / "league_registry.csv")
    registry_ids = {r.league_id.casefold(): r for r in registry}

    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        groups[row["CanonicalLeagueId"].casefold()].append(row)

    plan = []
    for _, group in sorted(groups.items()):
        first = group[0]
        league_id = first["CanonicalLeagueId"]
        existing = registry_ids.get(league_id.casefold())
        source_leagues = " | ".join(sorted({r["League"] for r in group}))
        tournament_ids = " | ".join(sorted({r["TournamentId"] for r in group if r.get("TournamentId")}))
        stage_ids = " | ".join(sorted({r["TournamentStageId"] for r in group if r.get("TournamentStageId")}))
        action = "MERGE_EXISTING" if existing else "CREATE"
        plan.append({
            "Action": action,
            "Tier": first["Tier"],
            "LeagueId": existing.league_id if existing else league_id,
            "Country": existing.country if existing else first.get("CanonicalCountry", first["Country"]),
            "League": existing.league if existing else first["CanonicalLeague"],
            "SourceLeagues": source_leagues,
            "TournamentIds": tournament_ids,
            "TournamentStageIds": stage_ids,
            "SourceRows": str(len(group)),
        })

    out = ROOT / "data" / "debug" / f"league_onboarding_plan_{datetime.now():%Y%m%d-%H%M%S}.csv"
    fields = ["Action","Tier","LeagueId","Country","League","SourceLeagues",
              "TournamentIds","TournamentStageIds","SourceRows"]
    with out.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, delimiter=";")
        w.writeheader()
        w.writerows(plan)

    create = sum(r["Action"] == "CREATE" for r in plan)
    merge = sum(r["Action"] == "MERGE_EXISTING" for r in plan)
    multi = sum(int(r["SourceRows"]) > 1 for r in plan)
    print(f"[INPUT] {source}")
    print(f"[PLAN] competitions={len(plan)} | CREATE={create} | MERGE_EXISTING={merge} | MULTI_SOURCE={multi}")
    print(f"[OUTPUT] {out}")
    print("[DRY-RUN] Nessuna modifica a league_registry.csv o agli storici.")


if __name__ == "__main__":
    main()
