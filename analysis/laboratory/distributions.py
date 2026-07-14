"""
===============================================================================
GioOver2.5 - analysis/laboratory/distributions.py
===============================================================================

SCOPO
-----
Analizzare i driver ex ante presenti in:

    analysis/laboratory/data/02_drivers.csv

e produrre statistiche aggregate per i gruppi:

    ALTA_OK
    ALTA_KO
    MEDIA_OK
    MEDIA_KO

FILE LETTI
----------
analysis/laboratory/data/02_drivers.csv

FILE SCRITTI
-------------
analysis/laboratory/data/03_driver_statistics.csv
analysis/laboratory/data/04_driver_distributions.csv

LOGICA
------
03_driver_statistics.csv:
- una riga per Driver + Gruppo;
- conteggio;
- media;
- mediana;
- minimo;
- massimo;
- deviazione standard;
- quartili 25%, 50%, 75%.

04_driver_distributions.csv:
- una riga per Driver + Gruppo + intervallo;
- distribuzione in classi calcolate automaticamente;
- numero occorrenze;
- percentuale sul gruppo.

MODALITÀ D'USO
--------------
    python -m analysis.laboratory.distributions

LIMITAZIONI
-----------
I valori non numerici vengono ignorati. Le distribuzioni descrivono ricorrenze
storiche e non rappresentano regole già validate.
===============================================================================
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Dict, Iterable, List, Tuple
import csv
import math

INPUT_FILE = Path("analysis/laboratory/data/02_drivers.csv")
OUTPUT_DIR = Path("analysis/laboratory/data")
VALID_GROUPS = {"ALTA_OK", "ALTA_KO", "MEDIA_OK", "MEDIA_KO"}
DEFAULT_BIN_COUNT = 10


def _to_float(value: object):
    if value is None:
        return None
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _percentile(sorted_values: List[float], percentile: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * percentile
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    fraction = position - lower
    return sorted_values[lower] * (1.0 - fraction) + sorted_values[upper] * fraction


def _group_name(row: Dict[str, str]) -> str:
    band = str(row.get("Band", "")).strip().upper()
    outcome = str(row.get("Outcome", "")).strip().upper()
    return f"{band}_{outcome}"


def load_driver_values(path: Path) -> Dict[Tuple[str, str], List[float]]:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    grouped = defaultdict(list)

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        required = {"Band", "Outcome", "Driver", "Value"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError("Colonne mancanti: " + ", ".join(sorted(missing)))

        for row in reader:
            group = _group_name(row)
            if group not in VALID_GROUPS:
                continue
            driver = str(row.get("Driver", "")).strip()
            value = _to_float(row.get("Value"))
            if driver and value is not None:
                grouped[(driver, group)].append(value)

    return grouped


def build_statistics(grouped):
    rows = []
    for (driver, group), values in sorted(grouped.items()):
        ordered = sorted(values)
        rows.append({
            "Driver": driver,
            "Group": group,
            "Count": len(ordered),
            "Mean": round(mean(ordered), 6),
            "Median": round(median(ordered), 6),
            "StdDev": round(pstdev(ordered), 6) if len(ordered) > 1 else 0.0,
            "Min": round(ordered[0], 6),
            "P25": round(_percentile(ordered, 0.25), 6),
            "P50": round(_percentile(ordered, 0.50), 6),
            "P75": round(_percentile(ordered, 0.75), 6),
            "Max": round(ordered[-1], 6),
        })
    return rows


def _build_edges(values: List[float], bin_count: int) -> List[float]:
    minimum = min(values)
    maximum = max(values)
    if minimum == maximum:
        return [minimum, maximum]
    width = (maximum - minimum) / bin_count
    return [minimum + width * i for i in range(bin_count + 1)]


def _find_bin(value: float, edges: List[float]) -> int:
    if len(edges) == 2 and edges[0] == edges[1]:
        return 0
    for index in range(len(edges) - 1):
        lower = edges[index]
        upper = edges[index + 1]
        if index == len(edges) - 2:
            if lower <= value <= upper:
                return index
        elif lower <= value < upper:
            return index
    return len(edges) - 2


def build_distributions(grouped, bin_count: int = DEFAULT_BIN_COUNT):
    all_values_by_driver = defaultdict(list)
    for (driver, _group), values in grouped.items():
        all_values_by_driver[driver].extend(values)

    edges_by_driver = {
        driver: _build_edges(values, bin_count)
        for driver, values in all_values_by_driver.items()
        if values
    }

    rows = []
    for (driver, group), values in sorted(grouped.items()):
        edges = edges_by_driver[driver]
        counts = [0] * max(1, len(edges) - 1)
        for value in values:
            counts[_find_bin(value, edges)] += 1

        total = len(values)
        for index, count in enumerate(counts):
            rows.append({
                "Driver": driver,
                "Group": group,
                "BinIndex": index + 1,
                "BinMin": round(edges[index], 6),
                "BinMax": round(edges[index + 1], 6),
                "Count": count,
                "GroupTotal": total,
                "Percentage": round((count / total) * 100, 6) if total else 0.0,
            })
    return rows


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    grouped = load_driver_values(INPUT_FILE)
    statistics = build_statistics(grouped)
    distributions = build_distributions(grouped)

    statistics_file = OUTPUT_DIR / "03_driver_statistics.csv"
    distributions_file = OUTPUT_DIR / "04_driver_distributions.csv"

    write_csv(statistics_file, statistics, [
        "Driver", "Group", "Count", "Mean", "Median", "StdDev",
        "Min", "P25", "P50", "P75", "Max"
    ])
    write_csv(distributions_file, distributions, [
        "Driver", "Group", "BinIndex", "BinMin", "BinMax",
        "Count", "GroupTotal", "Percentage"
    ])

    print(f"Gruppi Driver analizzati: {len(grouped)}")
    print(f"Statistiche prodotte: {len(statistics)}")
    print(f"Distribuzioni prodotte: {len(distributions)}")
    print(f"Output: {statistics_file}")
    print(f"Output: {distributions_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
