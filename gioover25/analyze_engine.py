import argparse
import csv
from pathlib import Path

from gioover25.engines.factory import get_available_engines


RANKING_DIR = Path("data/storico/ranking")
REPORT_DIR = Path("data/output_reports")


def read_history(engine_name: str) -> list[dict]:
    path = RANKING_DIR / engine_name / "storico_ranking.csv"

    if not path.exists():
        raise FileNotFoundError(f"Storico ranking non trovato: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter=";"))


def is_finished(row: dict) -> bool:
    return row.get("HG", "").strip() != "" and row.get("AG", "").strip() != ""


def goals(row: dict) -> int:
    return int(row["HG"]) + int(row["AG"])


def score(row: dict) -> float:
    return float(str(row.get("Score", "0")).replace(",", "."))


def result_label(row: dict) -> str:
    return f"{row['HG']}-{row['AG']}"


def pct(value: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round(value / total * 100, 2)


def analyze_by_band(rows: list[dict]) -> list[dict]:
    bands = ["ALTA", "MEDIA", "BASSA"]
    output = []

    for band in bands:
        band_rows = [r for r in rows if r.get("Band", "").strip().upper() == band]
        total = len(band_rows)

        over15 = sum(1 for r in band_rows if goals(r) >= 2)
        over25 = sum(1 for r in band_rows if goals(r) >= 3)
        under25 = total - over25

        output.append(
            {
                "Band": band,
                "Matches": total,
                "Over15": over15,
                "Over15Pct": pct(over15, total),
                "Over25": over25,
                "Over25Pct": pct(over25, total),
                "Under25": under25,
                "Under25Pct": pct(under25, total),
            }
        )

    return output


def top_false_positives(rows: list[dict], limit: int = 20) -> list[dict]:
    filtered = [r for r in rows if goals(r) < 3]
    filtered.sort(key=score, reverse=True)
    return filtered[:limit]


def top_false_negatives(rows: list[dict], limit: int = 20) -> list[dict]:
    filtered = [r for r in rows if goals(r) >= 3]
    filtered.sort(key=score)
    return filtered[:limit]


def export_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def simplify_match_rows(rows: list[dict]) -> list[dict]:
    output = []

    for r in rows:
        output.append(
            {
                "PredictionDate": r.get("PredictionDate", ""),
                "LeagueId": r.get("LeagueId", ""),
                "Match": r.get("Match", f"{r.get('Home', '')} - {r.get('Away', '')}"),
                "Score": r.get("Score", ""),
                "Band": r.get("Band", ""),
                "Result": result_label(r),
                "Goals": goals(r),
                "Over25": "OK" if goals(r) >= 3 else "KO",
                "BTTS": r.get("BTTS", ""),
                "Reason": r.get("Reason", ""),
            }
        )

    return output


def print_summary(engine_name: str, finished_rows: list[dict], band_rows: list[dict]) -> None:
    total = len(finished_rows)
    over15 = sum(1 for r in finished_rows if goals(r) >= 2)
    over25 = sum(1 for r in finished_rows if goals(r) >= 3)

    print()
    print(f"ENGINE {engine_name}")
    print("-" * 40)
    print(f"Partite concluse: {total}")
    print(f"Over 1.5: {over15}/{total} = {pct(over15, total)}%")
    print(f"Over 2.5: {over25}/{total} = {pct(over25, total)}%")
    print()

    for r in band_rows:
        print(
            f"{r['Band']}: "
            f"{r['Matches']} partite | "
            f"Over1.5 {r['Over15Pct']}% | "
            f"Over2.5 {r['Over25Pct']}%"
        )

def build_engine_summary(engine_name: str) -> dict:
    history = read_history(engine_name)
    finished_rows = [r for r in history if is_finished(r)]

    band_rows = analyze_by_band(finished_rows)

    summary = {
        "Engine": engine_name,
        "Matches": len(finished_rows),
        "Over15Pct": pct(sum(1 for r in finished_rows if goals(r) >= 2), len(finished_rows)),
        "Over25Pct": pct(sum(1 for r in finished_rows if goals(r) >= 3), len(finished_rows)),
        "ALTA_Matches": 0,
        "ALTA_Over15Pct": 0,
        "ALTA_Over25Pct": 0,
        "MEDIA_Matches": 0,
        "MEDIA_Over15Pct": 0,
        "MEDIA_Over25Pct": 0,
        "BASSA_Matches": 0,
        "BASSA_Over15Pct": 0,
        "BASSA_Over25Pct": 0,
    }

    for row in band_rows:
        band = row["Band"]
        summary[f"{band}_Matches"] = row["Matches"]
        summary[f"{band}_Over15Pct"] = row["Over15Pct"]
        summary[f"{band}_Over25Pct"] = row["Over25Pct"]

    return summary

def analyze_engine(engine_name: str) -> None:
    history = read_history(engine_name)
    finished_rows = [r for r in history if is_finished(r)]

    band_rows = analyze_by_band(finished_rows)
    false_positives = simplify_match_rows(top_false_positives(finished_rows))
    false_negatives = simplify_match_rows(top_false_negatives(finished_rows))

    engine_report_dir = REPORT_DIR / engine_name
    engine_report_dir.mkdir(parents=True, exist_ok=True)

    export_csv(
        engine_report_dir / "summary_by_band.csv",
        band_rows,
        [
            "Band",
            "Matches",
            "Over15",
            "Over15Pct",
            "Over25",
            "Over25Pct",
            "Under25",
            "Under25Pct",
        ],
    )

    export_csv(
        engine_report_dir / "top_false_positives.csv",
        false_positives,
        [
            "PredictionDate",
            "LeagueId",
            "Match",
            "Score",
            "Band",
            "Result",
            "Goals",
            "Over25",
            "BTTS",
            "Reason",
        ],
    )

    export_csv(
        engine_report_dir / "top_false_negatives.csv",
        false_negatives,
        [
            "PredictionDate",
            "LeagueId",
            "Match",
            "Score",
            "Band",
            "Result",
            "Goals",
            "Over25",
            "BTTS",
            "Reason",
        ],
    )

    print_summary(engine_name, finished_rows, band_rows)

    print()
    print(f"Report generati in: {engine_report_dir}")

def analyze_all_engines() -> None:
    summaries = []

    for engine_name in get_available_engines():
        print()
        print("=" * 60)
        print(f"ANALISI ENGINE {engine_name}")
        print("=" * 60)

        analyze_engine(engine_name)
        summaries.append(build_engine_summary(engine_name))

    comparison_file = REPORT_DIR / "engine_comparison.csv"

    fieldnames = [
        "Engine",
        "Matches",
        "Over15Pct",
        "Over25Pct",
        "ALTA_Matches",
        "ALTA_Over15Pct",
        "ALTA_Over25Pct",
        "MEDIA_Matches",
        "MEDIA_Over15Pct",
        "MEDIA_Over25Pct",
        "BASSA_Matches",
        "BASSA_Over15Pct",
        "BASSA_Over25Pct",
    ]

    export_csv(comparison_file, summaries, fieldnames)

    print()
    print(f"Confronto engine generato in: {comparison_file}")

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--engine", required=True)
    args = parser.parse_args()

    if args.engine == "all":
        analyze_all_engines()
    else:
        analyze_engine(args.engine)


if __name__ == "__main__":
    main()