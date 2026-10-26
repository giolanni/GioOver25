"""Determina la sorgente di backfill iniziale per i candidati onboarding.

Dry-run: non modifica league_registry.csv e non scrive storici.
Assegna un provider solo tramite mapping esplicito; altrimenti BACKFILL_REQUIRED.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path

from tools.backfill_sources import unresolved_status
from tools.prepare_input import ROOT, norm


# football-data.co.uk: mapping conservativo delle competizioni note.
# Il codice provider verra' usato dal downloader nel passo successivo.
FOOTBALL_DATA = {
    ("england", "premier league"): "E0",
    ("england", "championship"): "E1",
    ("england", "league one"): "E2",
    ("england", "league two"): "E3",
    ("scotland", "premiership"): "SC0",
    ("scotland", "championship"): "SC1",
    ("scotland", "league one"): "SC2",
    ("scotland", "league two"): "SC3",
    ("germany", "bundesliga"): "D1",
    ("germany", "2 bundesliga"): "D2",
    ("italy", "serie a"): "I1",
    ("italy", "serie b"): "I2",
    ("spain", "laliga"): "SP1",
    ("spain", "la liga"): "SP1",
    ("spain", "segunda division"): "SP2",
    ("france", "ligue 1"): "F1",
    ("france", "ligue 2"): "F2",
    ("netherlands", "eredivisie"): "N1",
    ("belgium", "jupiler league"): "B1",
    ("portugal", "liga portugal"): "P1",
    ("turkey", "super lig"): "T1",
    ("greece", "super league"): "G1",
}


def key(country: str, league: str) -> tuple[str, str]:
    # norm elimina punteggiatura/spazi; manteniamo il mapping nello stesso formato.
    return norm(country), norm(league)


FOOTBALL_DATA_NORM = {key(c, l): code for (c, l), code in FOOTBALL_DATA.items()}


def latest_onboarding() -> Path:
    files = sorted((ROOT / "data" / "debug").glob("league_onboarding_*.csv"))
    if not files:
        raise SystemExit("Nessun league_onboarding_*.csv trovato in data/debug")
    return files[-1]


def detect(row: dict[str, str]) -> tuple[str, str]:
    code = FOOTBALL_DATA_NORM.get(key(row["Country"], row["League"]))
    if code:
        return "FOOTBALL_DATA", code
    # OpenFootball verra' abilitato solo dopo una mappatura esplicita
    # repository/stagione: non assumiamo copertura dal solo nome.
    return unresolved_status(), ""


def main() -> None:
    parser = argparse.ArgumentParser(description="Rileva provider di backfill per onboarding.")
    parser.add_argument("--input", help="CSV onboarding; default ultimo in data/debug")
    parser.add_argument("--output", help="CSV output")
    args = parser.parse_args()

    source = ROOT / args.input if args.input else latest_onboarding()
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = [r for r in csv.DictReader(handle, delimiter=";") if r.get("Status") == "READY"]

    output = ROOT / args.output if args.output else (
        ROOT / "data" / "debug" / f"backfill_sources_{datetime.now():%Y%m%d-%H%M%S}.csv"
    )
    output.parent.mkdir(parents=True, exist_ok=True)

    fields = list(rows[0].keys()) + ["BackfillStatus", "BackfillCode"] if rows else []
    counts: dict[str, int] = {}
    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
        if fields:
            writer.writeheader()
        for row in rows:
            status, code = detect(row)
            counts[status] = counts.get(status, 0) + 1
            row["BackfillStatus"] = status
            row["BackfillCode"] = code
            writer.writerow(row)

    print(f"[BACKFILL] input={source}")
    print("[BACKFILL] " + " | ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"[BACKFILL] output={output}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")


if __name__ == "__main__":
    main()
