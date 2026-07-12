import argparse
import csv
import re
from datetime import date, timedelta
from pathlib import Path

from .engines.factory import get_available_engines


OUTPUT_RANKING_DIR = Path("data/output_ranking")
STORICO_RANKING_DIR = Path("data/storico/ranking")
RESULTS_DIR = Path("data/storico/risultati")


HISTORY_FIELDNAMES = [
    "PredictionDate",
    "LeagueId",
    "Round",
    "Home",
    "Away",
    "Score",
    "Band",
    "HG",
    "AG",
    "Goals",
    "Over25",
    "BTTS",
    "Reason",
    "RankingGapScore",
    "HomeAttackScore",
    "AwayAttackScore",
    "HomeDefenseWeaknessScore",
    "AwayDefenseWeaknessScore",
    "HomeLast10OverScore",
    "AwayLast10OverScore",
    "HomeVenueOverScore",
    "AwayVenueOverScore",
    "BTTSProfileScore",
    "AlgorithmVersion",
]


def history_file(engine_name: str) -> Path:
    return (
        STORICO_RANKING_DIR
        / engine_name
        / f"storico_ranking_{engine_name}.csv"
    )


def normalize(value: str) -> str:
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


def extract_prediction_date_from_filename(path: Path) -> str:
    match = re.search(
        r"ranking_(\d{4})_(\d{2})_(\d{2})",
        path.stem,
    )

    if not match:
        return ""

    year, month, day = match.groups()

    try:
        return date(
            int(year),
            int(month),
            int(day),
        ).isoformat()
    except ValueError:
        return ""


def prediction_key(row: dict) -> tuple[str, str, str, str]:
    return (
        str(row.get("PredictionDate", "")).strip(),
        str(row.get("LeagueId", "")).strip(),
        normalize(row.get("Home", "")),
        normalize(row.get("Away", "")),
    )


def normalize_history_row(
    row: dict,
    engine_name: str,
    prediction_date: str,
) -> dict:
    return {
        "PredictionDate": prediction_date,
        "LeagueId": row.get("LeagueId", ""),
        "Round": row.get("Round", ""),
        "Home": row.get("Home", ""),
        "Away": row.get("Away", ""),
        "Score": row.get("Score", ""),
        "Band": row.get("Band", ""),

        "HG": "",
        "AG": "",
        "Goals": "",
        "Over25": "",
        "BTTS": "",

        "Reason": row.get("Reason", ""),
        "RankingGapScore": row.get("RankingGapScore", ""),
        "HomeAttackScore": row.get("HomeAttackScore", ""),
        "AwayAttackScore": row.get("AwayAttackScore", ""),
        "HomeDefenseWeaknessScore": row.get(
            "HomeDefenseWeaknessScore",
            "",
        ),
        "AwayDefenseWeaknessScore": row.get(
            "AwayDefenseWeaknessScore",
            "",
        ),
        "HomeLast10OverScore": row.get(
            "HomeLast10OverScore",
            "",
        ),
        "AwayLast10OverScore": row.get(
            "AwayLast10OverScore",
            "",
        ),
        "HomeVenueOverScore": row.get(
            "HomeVenueOverScore",
            "",
        ),
        "AwayVenueOverScore": row.get(
            "AwayVenueOverScore",
            "",
        ),
        "BTTSProfileScore": row.get(
            "BTTSProfileScore",
            "",
        ),
        "AlgorithmVersion": (
            row.get("AlgorithmVersion", "")
            or engine_name
        ),
    }


def read_all_rankings(engine_name: str) -> list[dict]:
    ranking_dir = OUTPUT_RANKING_DIR / engine_name

    if not ranking_dir.exists():
        print(
            f"[{engine_name}] Cartella ranking non trovata: "
            f"{ranking_dir}"
        )
        return []

    ranking_files = sorted(ranking_dir.glob("*.csv"))

    if not ranking_files:
        print(f"[{engine_name}] Nessun file ranking trovato.")
        return []

    collected_rows = []
    seen_keys = set()

    for ranking_file in ranking_files:
        prediction_date = extract_prediction_date_from_filename(
            ranking_file
        )

        if not prediction_date:
            print(
                f"[{engine_name}] Data non ricavabile dal nome file: "
                f"{ranking_file.name}"
            )
            continue

        with ranking_file.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as f:
            reader = csv.DictReader(f, delimiter=";")
            file_rows = list(reader)

        added = 0
        duplicates = 0

        for row in file_rows:
            normalized_row = normalize_history_row(
                row=row,
                engine_name=engine_name,
                prediction_date=prediction_date,
            )

            key = prediction_key(normalized_row)

            if key in seen_keys:
                duplicates += 1
                continue

            seen_keys.add(key)
            collected_rows.append(normalized_row)
            added += 1

        print(
            f"[{engine_name}] {ranking_file.name}: "
            f"{len(file_rows)} righe, "
            f"PredictionDate={prediction_date}, "
            f"aggiunte={added}, "
            f"duplicate={duplicates}"
        )

    collected_rows.sort(
        key=lambda row: (
            str(row.get("PredictionDate", "")).strip(),
            str(row.get("LeagueId", "")).strip(),
            normalize(row.get("Home", "")),
            normalize(row.get("Away", "")),
        )
    )

    return collected_rows


def build_results_index() -> dict[str, list[dict]]:
    results_index: dict[str, list[dict]] = {}

    for results_file in sorted(RESULTS_DIR.glob("*.csv")):
        league_id = results_file.stem

        with results_file.open(
            "r",
            newline="",
            encoding="utf-8-sig",
        ) as f:
            reader = csv.DictReader(f, delimiter=";")
            rows = list(reader)

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
                    "home": normalize(row.get("Home", "")),
                    "away": normalize(row.get("Away", "")),
                    "hg": hg,
                    "ag": ag,
                }
            )

        results_index[league_id] = matches

    return results_index


def find_result_candidate(
    row: dict,
    results_index: dict[str, list[dict]],
    max_days: int,
) -> tuple[dict | None, str]:
    league_id = str(row.get("LeagueId", "")).strip()
    prediction_date = parse_date(row.get("PredictionDate", ""))
    home = normalize(row.get("Home", ""))
    away = normalize(row.get("Away", ""))

    if prediction_date is None:
        return None, "INVALID_DATE"

    if not league_id or not home or not away:
        return None, "INVALID_MATCH"

    first_valid_date = prediction_date
    last_valid_date = prediction_date + timedelta(days=max_days)

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
    row["Over25"] = "OK" if goals >= 3 else "KO"
    row["BTTS"] = "OK" if hg > 0 and ag > 0 else "KO"


def populate_results(
    rows: list[dict],
    results_index: dict[str, list[dict]],
    max_days: int,
) -> dict[str, int]:
    counters = {
        "matched": 0,
        "not_found": 0,
        "ambiguous": 0,
        "invalid": 0,
    }

    for row in rows:
        candidate, status = find_result_candidate(
            row=row,
            results_index=results_index,
            max_days=max_days,
        )

        if status == "MATCHED" and candidate is not None:
            apply_result(row, candidate)
            counters["matched"] += 1

        elif status == "NOT_FOUND":
            counters["not_found"] += 1

        elif status == "AMBIGUOUS":
            counters["ambiguous"] += 1

        else:
            counters["invalid"] += 1

    return counters


def write_history(
    engine_name: str,
    rows: list[dict],
) -> None:
    output_file = history_file(engine_name)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=HISTORY_FIELDNAMES,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)

    dates = sorted(
        {
            str(row.get("PredictionDate", "")).strip()
            for row in rows
            if str(row.get("PredictionDate", "")).strip()
        }
    )

    print()
    print(f"[{engine_name}] Storico ricostruito: {output_file}")
    print(f"[{engine_name}] Righe complessive: {len(rows)}")
    print(f"[{engine_name}] PredictionDate presenti: {dates}")


def rebuild_engine(
    engine_name: str,
    results_index: dict[str, list[dict]],
    max_days: int,
) -> None:
    print()
    print(f"========== {engine_name} ==========")

    rows = read_all_rankings(engine_name)

    if not rows:
        print(
            f"[{engine_name}] Ricostruzione non eseguita: "
            "nessuna riga valida."
        )
        return

    counters = populate_results(
        rows=rows,
        results_index=results_index,
        max_days=max_days,
    )

    write_history(
        engine_name=engine_name,
        rows=rows,
    )

    print(f"[{engine_name}] Risultati associati: {counters['matched']}")
    print(f"[{engine_name}] Risultati non trovati: {counters['not_found']}")
    print(f"[{engine_name}] Risultati ambigui: {counters['ambiguous']}")
    print(f"[{engine_name}] Righe non valide: {counters['invalid']}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Ricostruisce gli storici ranking dai ranking giornalieri "
            "e associa i risultati disponibili."
        )
    )

    parser.add_argument(
        "--engine",
        default="all",
        choices=get_available_engines() + ["all"],
        help="Motore da ricostruire",
    )

    parser.add_argument(
        "--max-days",
        type=int,
        default=3,
        help=(
            "Numero massimo di giorni tra PredictionDate "
            "e data della partita. Default: 3"
        ),
    )

    args = parser.parse_args()

    if args.max_days < 0:
        raise ValueError("--max-days non può essere negativo")

    results_index = build_results_index()

    if args.engine == "all":
        for engine_name in get_available_engines():
            rebuild_engine(
                engine_name=engine_name,
                results_index=results_index,
                max_days=args.max_days,
            )
    else:
        rebuild_engine(
            engine_name=args.engine,
            results_index=results_index,
            max_days=args.max_days,
        )


if __name__ == "__main__":
    main()