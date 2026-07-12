import argparse
import csv
import shutil
from datetime import date, timedelta
from pathlib import Path


RANKING_HISTORY_DIR = Path("data/storico/ranking")
RESULTS_DIR = Path("data/storico/risultati")
REPORT_DIR = Path("data/debug")

RESULT_FIELDS = [
    "HG",
    "AG",
    "Goals",
    "Over25",
    "BTTS",
]


def normalize_team(value: str) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .lower()
        .split()
    )


def parse_date(value: str) -> date | None:
    raw = str(value or "").strip()

    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def parse_int(value: str) -> int | None:
    raw = str(value or "").strip()

    if raw == "":
        return None

    try:
        return int(raw)
    except ValueError:
        return None


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        reader = csv.DictReader(f, delimiter=";")
        return list(reader.fieldnames or []), list(reader)


def write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict],
) -> None:
    with path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def clear_result(row: dict) -> None:
    for field in RESULT_FIELDS:
        row[field] = ""


def build_results_index() -> dict[str, list[dict]]:
    index: dict[str, list[dict]] = {}

    for results_file in sorted(RESULTS_DIR.glob("*.csv")):
        league_id = results_file.stem
        _, rows = read_csv(results_file)

        matches = []

        for row in rows:
            match_date = parse_date(row.get("Date", ""))
            hg = parse_int(row.get("HG", ""))
            ag = parse_int(row.get("AG", ""))

            if match_date is None:
                continue

            if hg is None or ag is None:
                continue

            matches.append(
                {
                    "date": match_date,
                    "home": normalize_team(
                        row.get("Home", "")
                    ),
                    "away": normalize_team(
                        row.get("Away", "")
                    ),
                    "hg": hg,
                    "ag": ag,
                }
            )

        index[league_id] = matches

    return index


def find_candidate(
    row: dict,
    results_index: dict[str, list[dict]],
    min_days_after_prediction: int,
    max_days_after_prediction: int,
) -> tuple[dict | None, str]:
    league_id = str(
        row.get("LeagueId", "")
    ).strip()

    prediction_date = parse_date(
        row.get("PredictionDate", "")
    )

    if prediction_date is None:
        return None, "INVALID_PREDICTION_DATE"

    home = normalize_team(row.get("Home", ""))
    away = normalize_team(row.get("Away", ""))

    if not league_id or not home or not away:
        return None, "INVALID_MATCH_DATA"

    first_valid_date = prediction_date + timedelta(
        days=min_days_after_prediction
    )

    last_valid_date = prediction_date + timedelta(
        days=max_days_after_prediction
    )

    candidates = []

    for match in results_index.get(league_id, []):
        if match["home"] != home:
            continue

        if match["away"] != away:
            continue

        if match["date"] < first_valid_date:
            continue

        if match["date"] > last_valid_date:
            continue

        candidates.append(match)

    if len(candidates) == 0:
        return None, "NOT_FOUND"

    if len(candidates) > 1:
        return None, "AMBIGUOUS"

    return candidates[0], "MATCHED"


def apply_result(row: dict, match: dict) -> None:
    hg = match["hg"]
    ag = match["ag"]
    goals = hg + ag

    row["HG"] = str(hg)
    row["AG"] = str(ag)
    row["Goals"] = str(goals)

    row["Over25"] = (
        "OK"
        if goals >= 3
        else "KO"
    )

    row["BTTS"] = (
        "OK"
        if hg > 0 and ag > 0
        else "KO"
    )


def process_history(
    history_file: Path,
    results_index: dict[str, list[dict]],
    min_days: int,
    max_days: int,
    apply_changes: bool,
) -> tuple[dict[str, int], list[dict]]:
    fieldnames, rows = read_csv(history_file)

    counters = {
        "rows": len(rows),
        "matched": 0,
        "not_found": 0,
        "ambiguous": 0,
        "invalid": 0,
        "previous_results": 0,
        "changed_results": 0,
    }

    not_found_rows = []

    for row in rows:
        old_result = tuple(
            str(row.get(field, "")).strip()
            for field in RESULT_FIELDS
        )

        if any(old_result):
            counters["previous_results"] += 1

        clear_result(row)

        candidate, status = find_candidate(
            row=row,
            results_index=results_index,
            min_days_after_prediction=min_days,
            max_days_after_prediction=max_days,
        )

        if status == "MATCHED" and candidate is not None:
            apply_result(row, candidate)
            counters["matched"] += 1

            new_result = tuple(
                str(row.get(field, "")).strip()
                for field in RESULT_FIELDS
            )

            if old_result != new_result:
                counters["changed_results"] += 1

        elif status == "NOT_FOUND":
            counters["not_found"] += 1

            not_found_rows.append(
                {
                    "PredictionDate": row.get("PredictionDate", ""),
                    "LeagueId": row.get("LeagueId", ""),
                    "Round": row.get("Round", ""),
                    "Home": row.get("Home", ""),
                    "Away": row.get("Away", ""),
                    "Score": row.get("Score", ""),
                    "Band": row.get("Band", ""),
                    "Status": "NOT_FOUND",
                }
            )

        elif status == "AMBIGUOUS":
            counters["ambiguous"] += 1

        else:
            counters["invalid"] += 1

    if apply_changes:
        backup_file = history_file.with_suffix(
            history_file.suffix
            + ".before_recovery.bak"
        )

        if not backup_file.exists():
            shutil.copy2(
                history_file,
                backup_file,
            )

        write_csv(
            history_file,
            fieldnames,
            rows,
        )

    return counters, not_found_rows

def write_not_found_report(
    engine_name: str,
    rows: list[dict],
) -> Path:
    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    report_file = (
        REPORT_DIR
        / f"recover_not_found_{engine_name}.csv"
    )

    fieldnames = [
        "PredictionDate",
        "LeagueId",
        "Round",
        "Home",
        "Away",
        "Score",
        "Band",
        "Status",
    ]

    with report_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    return report_file

def get_history_files(
    engine_name: str,
) -> list[Path]:
    if engine_name == "all":
        return sorted(
            RANKING_HISTORY_DIR.glob(
                "*/storico_ranking_*.csv"
            )
        )

    return [
        RANKING_HISTORY_DIR
        / engine_name
        / f"storico_ranking_{engine_name}.csv"
    ]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Recupera i risultati degli storici ranking "
            "dai file cumulativi delle leghe."
        )
    )

    parser.add_argument(
        "--engine",
        default="all",
        help="Engine da elaborare oppure all",
    )

    parser.add_argument(
        "--min-days",
        type=int,
        default=0,
        help=(
            "Giorni minimi tra PredictionDate "
            "e data partita. Default: 0"
        ),
    )

    parser.add_argument(
        "--max-days",
        type=int,
        default=2,
        help=(
            "Giorni massimi tra PredictionDate "
            "e data partita. Default: 2"
        ),
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Applica le modifiche. "
            "Senza questo flag esegue solo il controllo."
        ),
    )

    args = parser.parse_args()

    if args.min_days < 0:
        raise ValueError(
            "--min-days non può essere negativo"
        )

    if args.max_days < args.min_days:
        raise ValueError(
            "--max-days deve essere maggiore "
            "o uguale a --min-days"
        )

    results_index = build_results_index()
    history_files = get_history_files(args.engine)

    print(
        "MODALITÀ:",
        "APPLICAZIONE"
        if args.apply
        else "SOLO CONTROLLO",
    )

    print(
        "Finestra temporale:",
        f"da +{args.min_days} a +{args.max_days} giorni",
    )
    print()

    for history_file in history_files:
        if not history_file.exists():
            print(f"MANCANTE: {history_file}")
            continue

        counters, not_found_rows = process_history(
            history_file=history_file,
            results_index=results_index,
            min_days=args.min_days,
            max_days=args.max_days,
            apply_changes=args.apply,
        )

        engine_name = history_file.parent.name

        report_file = write_not_found_report(
            engine_name=engine_name,
            rows=not_found_rows,
        )

        print(history_file)
        print(
            f"  Righe totali: "
            f"{counters['rows']}"
        )
        print(
            f"  Risultati già presenti: "
            f"{counters['previous_results']}"
        )
        print(
            f"  Corrispondenze uniche: "
            f"{counters['matched']}"
        )
        print(
            f"  Non trovate: "
            f"{counters['not_found']}"
        )
        print(
            f"  Ambigue: "
            f"{counters['ambiguous']}"
        )
        print(
            f"  Non valide: "
            f"{counters['invalid']}"
        )
        print(
            f"  Risultati diversi dai precedenti: "
            f"{counters['changed_results']}"
        )
        print(
            f"  Report non trovate: "
            f"{report_file}"
        )
        print()

    if not args.apply:
        print("Nessun file è stato modificato.")
        print(
            "Dopo aver controllato i numeri, "
            "usa --apply per applicare."
        )
if __name__ == "__main__":
    main()