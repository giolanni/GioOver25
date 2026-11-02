"""Audit locale dei feed discovery per le CREATE Tier1-3 residue."""
from __future__ import annotations
import csv
from collections import defaultdict
from pathlib import Path
from tools.prepare_input import ROOT, norm
from tools.diretta_mobile import parse_feed
from tools.bulk_onboard_tier123 import latest_plan

def split_ids(value: str) -> set[str]:
    return {x.strip() for x in (value or "").split("|") if x.strip()}

def main() -> None:
    plan_path = latest_plan()
    with plan_path.open(encoding="utf-8-sig", newline="") as h:
        rows = [r for r in csv.DictReader(h, delimiter=";") if r.get("Action") == "CREATE"]

    cache = ROOT / "data" / "debug" / "discover_leagues_cache"
    parsed = []
    for path in sorted(cache.glob("*.feed")):
        try:
            parsed.extend(parse_feed(path.read_text(encoding="utf-8")))
        except Exception:
            pass

    print(f"[INPUT] {plan_path}")
    print(f"[CACHE] files={len(list(cache.glob('*.feed')))} | parsed_matches={len(parsed)}")
    print("LeagueId | NAME | +TID | +STAGE | FINISHED | RANGE")
    for row in rows:
        country = row["Country"]
        sources = [x.strip() for x in row["Sources"].split("|") if x.strip()]
        tids = split_ids(row.get("TournamentIds", ""))
        stages = split_ids(row.get("TournamentStageIds", ""))

        name = [m for m in parsed if norm(m.country) == norm(country) and any(norm(m.league) == norm(s) for s in sources)]
        tid = [m for m in name if not tids or not m.tournament_id or m.tournament_id in tids]
        stage = [m for m in tid if not stages or not m.tournament_stage_id or m.tournament_stage_id in stages]
        finished = [m for m in stage if m.match_date and "-" in m.score and all(x.isdigit() for x in m.score.split("-", 1))]
        dates = sorted({m.match_date for m in finished})
        span = f"{dates[0]}..{dates[-1]}" if dates else "-"
        print(f"{row['LeagueId']} | {len(name)} | {len(tid)} | {len(stage)} | {len(finished)} | {span}")

if __name__ == "__main__":
    main()
