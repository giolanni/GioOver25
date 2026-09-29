from __future__ import annotations
import argparse
from datetime import date, timedelta
from pathlib import Path

from tools.prepare_input import ROOT, load_registry, write_csv
from tools.providers import diretta_matches, sofascore_matches, merge_matches


def parse_target(args):
    if args.date:
        return date.fromisoformat(args.date)
    if args.yesterday:
        return date.today() - timedelta(days=1)
    if args.tomorrow:
        return date.today() + timedelta(days=1)
    return date.today()


def parser(description):
    p = argparse.ArgumentParser(description=description)
    g = p.add_mutually_exclusive_group()
    g.add_argument("--date", help="YYYY-MM-DD")
    g.add_argument("--yesterday", action="store_true")
    g.add_argument("--today", action="store_true")
    g.add_argument("--tomorrow", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    return p

def main():
    args = parser("Genera risultati.csv interrogando Diretta e SofaScore.").parse_args()
    target = parse_target(args)
    registry = load_registry(ROOT / "data" / "league_registry.csv")
    d = diretta_matches(target, "results", registry)
    s = sofascore_matches(target, "results")
    matches = merge_matches(d, s)
    output = ROOT / "data" / "input_risultati" / "risultati.csv"
    print(f"[GETRESULTS] {target}: {len(matches)} risultati finali")
    if not args.dry_run:
        write_csv(output, "results", matches)
        print(f"[OK] scritto {output}")
    else:
        print("[DRY-RUN] CSV non modificato.")


if __name__ == "__main__":
    main()
