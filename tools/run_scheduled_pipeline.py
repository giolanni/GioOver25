"""Orchestrate the daily GioOver jobs used by GitHub Actions."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
MATCHES_FILE = ROOT / "data" / "input_partite" / "partite.csv"
RESULTS_FILE = ROOT / "data" / "input_risultati" / "risultati.csv"

def run(*args: str) -> None:
    command = [sys.executable, *args]
    print(f"[PIPELINE] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def read_matches(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def has_result_rows() -> bool:
    if not RESULTS_FILE.exists():
        return False
    with RESULTS_FILE.open(encoding="utf-8-sig", newline="") as handle:
        return next(csv.DictReader(handle, delimiter=";"), None) is not None


def acquire_results(*day_args: str) -> None:
    run("getresults.py", *day_args)
    if has_result_rows():
        run("-m", "gioover25.append_results", str(RESULTS_FILE.relative_to(ROOT)))
    else:
        print("[PIPELINE] Nessun risultato importabile: append_results saltato.")


def acquire_and_rank() -> None:
    run("getmatches.py", "--today")
    if not read_matches(MATCHES_FILE):
        raise RuntimeError("getmatches non ha prodotto partite: ranking interrotto")
    run("-m", "gioover25.rank_matches_v2", str(MATCHES_FILE.relative_to(ROOT)), "--engine", "all")


def morning_recovery() -> None:
    today = datetime.now(ZoneInfo("Europe/Rome")).date().isoformat()
    existing_dates = {
        (row.get("MatchDate") or "").strip()
        for row in read_matches(MATCHES_FILE)
        if row.get("MatchDate")
    }
    if today in existing_dates:
        print(f"[MORNING-RECOVERY] dati {today} gia' presenti: nessun doppione.")
        return
    print(f"[MORNING-RECOVERY] dati {today} mancanti: avvio ciclo completo.")
    acquire_results("--yesterday")
    acquire_and_rank()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("morning", "morning_recovery", "results", "smoke"))
    args = parser.parse_args()

    if args.operation == "morning":
        acquire_results("--yesterday")
        acquire_and_rank()
    elif args.operation == "morning_recovery":
        morning_recovery()
    elif args.operation == "results":
        now_rome = datetime.now(ZoneInfo("Europe/Rome"))
        # A scheduled GitHub job can be delayed for hours. If the evening job
        # actually starts after midnight/morning, it must still process the
        # day that has just ended rather than the new, empty calendar day.
        target = now_rome.date() if now_rome.hour >= 12 else now_rome.date() - timedelta(days=1)
        acquire_results("--date", target.isoformat())
    else:
        run("getresults.py", "--yesterday", "--dry-run")
        run("getmatches.py", "--today", "--dry-run")


if __name__ == "__main__":
    main()
