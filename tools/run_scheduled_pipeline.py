"""Orchestrate the daily GioOver jobs used by GitHub Actions."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATCHES_FILE = ROOT / "data" / "input_partite" / "partite.csv"
RESULTS_FILE = ROOT / "data" / "input_risultati" / "risultati.csv"
MATCH_FIELDS = ("LeagueId", "MatchDate", "Home", "Away")


def run(*args: str) -> None:
    command = [sys.executable, *args]
    print(f"[PIPELINE] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def read_matches(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def match_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return tuple((row.get(field) or "").strip() for field in MATCH_FIELDS)


def write_matches(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=MATCH_FIELDS, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in MATCH_FIELDS} for row in rows)


def has_result_rows() -> bool:
    if not RESULTS_FILE.exists():
        return False
    with RESULTS_FILE.open(encoding="utf-8-sig", newline="") as handle:
        return next(csv.DictReader(handle, delimiter=";"), None) is not None


def acquire_results(day: str) -> None:
    run("getresults.py", day)
    if has_result_rows():
        run("-m", "gioover25.append_results", str(RESULTS_FILE.relative_to(ROOT)))
    else:
        print("[PIPELINE] Nessun risultato importabile: append_results saltato.")


def acquire_and_rank() -> None:
    run("getmatches.py", "--today")
    if not read_matches(MATCHES_FILE):
        raise RuntimeError("getmatches non ha prodotto partite: ranking interrotto")
    run("-m", "gioover25.rank_matches_v2", str(MATCHES_FILE.relative_to(ROOT)), "--engine", "all")


def delta_rank() -> None:
    previous = read_matches(MATCHES_FILE)
    previous_keys = {match_key(row) for row in previous}
    run("getmatches.py", "--today")
    fresh = read_matches(MATCHES_FILE)
    new_rows = [row for row in fresh if match_key(row) not in previous_keys]
    if not new_rows:
        # getmatches writes a complete snapshot. Restore the prior snapshot so
        # a later, temporarily incomplete feed cannot remove known fixtures.
        write_matches(MATCHES_FILE, previous)
        print("[DELTA] 0 nuove partite: ranking non rigenerato.")
        return
    merged = list(previous)
    seen = set(previous_keys)
    for row in fresh:
        key = match_key(row)
        if key not in seen:
            merged.append(row)
            seen.add(key)
    write_matches(MATCHES_FILE, merged)
    print(f"[DELTA] {len(new_rows)} nuove partite; totale giornata {len(merged)}.")
    # Rebuild the day's outputs without archiving duplicates. Ranking history
    # already deduplicates by engine + match identity.
    run("-m", "gioover25.rank_matches_v2", str(MATCHES_FILE.relative_to(ROOT)), "--engine", "all", "--erase")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("morning", "delta", "results", "smoke"))
    args = parser.parse_args()

    if args.operation == "morning":
        acquire_results("--yesterday")
        acquire_and_rank()
    elif args.operation == "delta":
        delta_rank()
    elif args.operation == "results":
        acquire_results("--today")
    else:
        run("getresults.py", "--yesterday", "--dry-run")
        run("getmatches.py", "--today", "--dry-run")


if __name__ == "__main__":
    main()
