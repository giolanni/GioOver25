"""Compatibility entry point for Laboratory driver analysis.

Normalizes legacy/current Band and Outcome values before delegating to the
robust implementation. This is necessary because 01_matches may contain
historical variants while downstream reports require canonical ALTA/MEDIA and
OK/KO groups.
"""
from __future__ import annotations

import csv

from . import driver_analysis_fixed as _fixed
from .driver_analysis_fixed import *


def _canonical_band(value: object) -> str:
    raw = str(value or "").strip().upper().replace(" ", "_").replace("-", "_")
    if raw in {"ALTA", "HIGH", "HA", "FASCIA_ALTA"} or raw.startswith(("ALTA_", "HIGH_")):
        return "ALTA"
    if raw in {"MEDIA", "MEDIUM", "M", "FASCIA_MEDIA"} or raw.startswith(("MEDIA_", "MEDIUM_")):
        return "MEDIA"
    return str(value or "").strip().upper()


def _canonical_outcome(row: dict) -> str:
    hg = str(row.get("HG") or "").strip().replace(",", ".")
    ag = str(row.get("AG") or "").strip().replace(",", ".")
    if hg and ag:
        try:
            return "OK" if int(float(hg)) + int(float(ag)) >= 3 else "KO"
        except ValueError:
            pass

    raw = str(row.get("Outcome") or row.get("Over25") or "").strip().upper()
    if raw in {"OK", "OVER", "OVER25", "OVER_25", "TRUE", "YES", "1"}:
        return "OK"
    if raw in {"KO", "UNDER", "UNDER25", "UNDER_25", "FALSE", "NO", "0"}:
        return "KO"
    return ""


def _load_rows_normalized(path):
    if not path.exists():
        raise FileNotFoundError(f"Dataset Laboratory non trovato: {path}")
    rows = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        fields = set(reader.fieldnames or [])
        missing = {"Band", "Outcome"}.difference(fields)
        if missing:
            raise ValueError("Colonne mancanti in 01_matches.csv: " + ", ".join(sorted(missing)))
        for raw in reader:
            row = dict(raw)
            row["Band"] = _canonical_band(row.get("Band"))
            row["Outcome"] = _canonical_outcome(row)
            group = f"{row['Band']}_{row['Outcome']}"
            if group not in _fixed.GROUPS:
                continue
            row["_Group"] = group
            for driver in _fixed.DRIVERS:
                row[driver] = _fixed._float(raw.get(driver))
            rows.append(row)
    return rows


# Patch only the loader used by the robust implementation. All statistical
# functions remain centralized in driver_analysis_fixed.
_fixed._load_rows = _load_rows_normalized
main = _fixed.main


if __name__ == "__main__":
    raise SystemExit(main())
