from __future__ import annotations

"""Exploratory ALTA filter experiment based on Laboratory signals.

The script does NOT modify any engine.  It tests whether signals already visible
in analysis/laboratory/data/01_matches.csv can isolate a higher-precision subset
of the current ALTA band.

Priority is precision, but every candidate also reports coverage, temporal
train/test behaviour, no-Australia performance and worst monthly precision.
This makes small 100% samples visible without confusing them with robust rules.
"""

import argparse
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable

INPUT_DEFAULT = Path("analysis/laboratory/data/01_matches.csv")
OUTPUT_DEFAULT = Path("analysis/experiments/laboratory_alta_signal_backtest/output")


@dataclass(frozen=True)
class Signal:
    name: str
    field: str
    op: str
    threshold: float

    def matches(self, row: dict[str, str]) -> bool:
        try:
            value = float(str(row.get(self.field, "")).strip())
        except (TypeError, ValueError):
            return False
        return value >= self.threshold if self.op == ">=" else value <= self.threshold


# Thresholds intentionally coarse and interpretable. They come from signals
# repeatedly highlighted by the Laboratory, not from an optimizer fitted here.
SIGNALS = [
    Signal("away_ga_l5_ge_1_8", "AwayGALast5Avg", ">=", 1.8),
    Signal("away_ga_l5_ge_2_0", "AwayGALast5Avg", ">=", 2.0),
    Signal("worst_ppg_l5_le_1_0", "WorstPPGLast5", "<=", 1.0),
    Signal("worst_ppg_l5_le_0_8", "WorstPPGLast5", "<=", 0.8),
    Signal("away_attack_le_11_0", "AwayAttackScore", "<=", 11.0),
    Signal("away_attack_le_10_0", "AwayAttackScore", "<=", 10.0),
    Signal("away_def_weak_ge_8_0", "AwayDefenseWeaknessScore", ">=", 8.0),
    Signal("away_def_weak_ge_9_0", "AwayDefenseWeaknessScore", ">=", 9.0),
    Signal("home_restart_gf_ge_2_0", "HomeGFAvgSinceRestart", ">=", 2.0),
    Signal("home_restart_gf_ge_2_5", "HomeGFAvgSinceRestart", ">=", 2.5),
    Signal("home_restart_over_ge_0_8", "HomeOverRateSinceRestart", ">=", 0.8),
    Signal("home_restart_over_ge_1_0", "HomeOverRateSinceRestart", ">=", 1.0),
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter=";"))
    return [
        row for row in rows
        if str(row.get("Band", "")).strip().upper() == "ALTA"
        and str(row.get("Outcome", "")).strip().upper() in {"OK", "KO"}
        and _parse_date(row.get("MatchDate", "")) is not None
    ]


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(str(value).strip())
    except ValueError:
        return None


def stats(rows: list[dict[str, str]]) -> tuple[int, int, int, float]:
    ok = sum(str(row.get("Outcome", "")).strip().upper() == "OK" for row in rows)
    ko = len(rows) - ok
    hit = ok / len(rows) * 100.0 if rows else 0.0
    return ok, ko, len(rows), hit


def worst_month(rows: list[dict[str, str]], min_month_sample: int = 5) -> tuple[str, int, float]:
    months: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        month = str(row.get("MatchDate", ""))[:7]
        months.setdefault(month, []).append(row)
    eligible = []
    for month, month_rows in months.items():
        _, _, total, hit = stats(month_rows)
        if total >= min_month_sample:
            eligible.append((hit, month, total))
    if not eligible:
        return "", 0, 0.0
    hit, month, total = min(eligible)
    return month, total, hit


def evaluate(
    name: str,
    predicate: Callable[[dict[str, str]], bool],
    rows: list[dict[str, str]],
    split_date: date,
) -> dict[str, object]:
    selected = [row for row in rows if predicate(row)]
    train = [row for row in selected if _parse_date(row["MatchDate"]) < split_date]
    test = [row for row in selected if _parse_date(row["MatchDate"]) >= split_date]
    no_au = [row for row in selected if not str(row.get("LeagueId", "")).startswith("Australia_")]

    ok, ko, total, hit = stats(selected)
    train_ok, train_ko, train_total, train_hit = stats(train)
    test_ok, test_ko, test_total, test_hit = stats(test)
    noau_ok, noau_ko, noau_total, noau_hit = stats(no_au)
    month, month_total, month_hit = worst_month(selected)

    return {
        "Rule": name,
        "OK": ok,
        "KO": ko,
        "Total": total,
        "HitRate": round(hit, 2),
        "CoveragePct": round(total / len(rows) * 100.0, 2) if rows else 0.0,
        "Train_OK": train_ok,
        "Train_KO": train_ko,
        "Train_Total": train_total,
        "Train_HitRate": round(train_hit, 2),
        "Test_OK": test_ok,
        "Test_KO": test_ko,
        "Test_Total": test_total,
        "Test_HitRate": round(test_hit, 2),
        "NoAU_OK": noau_ok,
        "NoAU_KO": noau_ko,
        "NoAU_Total": noau_total,
        "NoAU_HitRate": round(noau_hit, 2),
        "WorstMonth": month,
        "WorstMonthTotal": month_total,
        "WorstMonthHitRate": round(month_hit, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Backtest segnali Laboratory sulla fascia ALTA")
    parser.add_argument("--input", default=str(INPUT_DEFAULT))
    parser.add_argument("--output-dir", default=str(OUTPUT_DEFAULT))
    parser.add_argument(
        "--test-days",
        type=int,
        default=14,
        help="Numero di giorni finali riservati al test temporale (default: 14).",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Dataset Laboratory non trovato: {input_path}")

    rows = read_rows(input_path)
    if not rows:
        raise RuntimeError("Nessuna partita ALTA conclusa trovata nel Laboratory.")

    dates = sorted(_parse_date(row["MatchDate"]) for row in rows)
    last_date = dates[-1]
    split_date = last_date.fromordinal(last_date.toordinal() - max(args.test_days, 1) + 1)

    baseline = evaluate("BASELINE_ALTA", lambda _row: True, rows, split_date)
    results = [baseline]

    for signal in SIGNALS:
        results.append(evaluate(signal.name, signal.matches, rows, split_date))

    # Pairs are deliberately AND combinations: we are looking for a purer ALTA
    # subset, not for a new score formula yet.
    for i, first in enumerate(SIGNALS):
        for second in SIGNALS[i + 1 :]:
            # Skip two thresholds of the same metric: the stricter one would
            # simply duplicate a single rule.
            if first.field == second.field:
                continue
            results.append(
                evaluate(
                    f"{first.name} AND {second.name}",
                    lambda row, a=first, b=second: a.matches(row) and b.matches(row),
                    rows,
                    split_date,
                )
            )

    baseline_hit = float(baseline["HitRate"])
    for result in results:
        result["DeltaVsBaseline"] = round(float(result["HitRate"]) - baseline_hit, 2)
        # Practical ranking: precision first, then test precision, then sample.
        result["Interesting"] = (
            "YES"
            if int(result["Total"]) >= 20
            and float(result["HitRate"]) > baseline_hit
            and int(result["Test_Total"]) >= 5
            and float(result["Test_HitRate"]) >= baseline_hit
            else "NO"
        )

    results.sort(
        key=lambda row: (
            row["Interesting"] != "YES",
            -float(row["HitRate"]),
            -float(row["Test_HitRate"]),
            -int(row["Total"]),
        )
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "alta_signal_results.csv"
    fieldnames = list(results[0].keys())
    with output_file.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(results)

    print(f"ALTA concluse: {len(rows)}")
    print(f"Periodo: {dates[0]} -> {last_date}")
    print(f"Test temporale da: {split_date}")
    print(
        f"Baseline: {baseline['OK']}/{baseline['Total']} = "
        f"{baseline['HitRate']}%"
    )
    print("\nMigliori candidati:")
    shown = 0
    for result in results:
        if result["Rule"] == "BASELINE_ALTA":
            continue
        print(
            f"  {result['Rule']}: {result['OK']}/{result['Total']} "
            f"= {result['HitRate']}% | test {result['Test_OK']}/{result['Test_Total']} "
            f"= {result['Test_HitRate']}% | noAU {result['NoAU_HitRate']}% | "
            f"delta {result['DeltaVsBaseline']:+.2f} | {result['Interesting']}"
        )
        shown += 1
        if shown >= 15:
            break

    print(f"\nCSV: {output_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
