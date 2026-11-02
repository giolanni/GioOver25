"""Audit mirato delle leghe TIER1-3 gia presenti emerse dall'onboarding.

Legge automaticamente l'ultimo league_onboarding_plan_*.csv, seleziona le
righe MERGE_EXISTING e delega il confronto a bonifica_storici_diretta senza
--apply. Non modifica registry o storici.
"""
from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEBUG = ROOT / "data" / "debug"


def latest_plan() -> Path:
    files = sorted(DEBUG.glob("league_onboarding_plan_*.csv"), key=lambda p: p.stat().st_mtime)
    if not files:
        raise SystemExit("[ERROR] Nessun league_onboarding_plan_*.csv trovato in data/debug")
    return files[-1]


def main() -> int:
    plan = latest_plan()
    with plan.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))

    ids = []
    for row in rows:
        if (row.get("Action") or "").strip().upper() != "MERGE_EXISTING":
            continue
        lid = (row.get("LeagueId") or row.get("CanonicalLeagueId") or "").strip()
        if lid and lid not in ids:
            ids.append(lid)

    if not ids:
        print(f"[INPUT] {plan}")
        print("[AUDIT] Nessuna lega MERGE_EXISTING trovata.")
        return 0

    print(f"[INPUT] {plan}")
    print(f"[AUDIT] MERGE_EXISTING={len(ids)}")
    cmd = [sys.executable, "-m", "tools.bonifica_storici_diretta"]
    for lid in ids:
        cmd += ["--league-id", lid]
    print("[MODE] dry-run; nessuna modifica a registry o storici.")
    return subprocess.call(cmd, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
