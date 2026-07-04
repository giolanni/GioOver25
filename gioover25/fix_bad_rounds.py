import csv
from pathlib import Path


RESULTS_DIR = Path("data/storico/risultati")


def is_bad_round(value: str) -> bool:
    raw = str(value or "").strip()
    return raw.isdigit() and len(raw) == 8 and raw.startswith("20")


def fix_file(path: Path) -> int:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=";"))

    if not rows:
        return 0

    fixed = 0

    valid_rounds = []
    for row in rows:
        raw_round = str(row.get("Round", "")).strip()
        if raw_round.isdigit() and not is_bad_round(raw_round):
            valid_rounds.append(int(raw_round))

    next_round = max(valid_rounds, default=0) + 1

    for row in rows:
        raw_round = str(row.get("Round", "")).strip()

        if is_bad_round(raw_round):
            row["Round"] = str(next_round)
            next_round += 1
            fixed += 1

    if fixed > 0:
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "Country",
                    "League",
                    "Season",
                    "Round",
                    "Date",
                    "Home",
                    "Away",
                    "HG",
                    "AG",
                    "Notes",
                ],
                delimiter=";",
            )
            writer.writeheader()
            writer.writerows(rows)

    return fixed


def main() -> None:
    total_fixed = 0

    for path in sorted(RESULTS_DIR.glob("*.csv")):
        fixed = fix_file(path)

        if fixed:
            print(f"{path.name}: round corretti {fixed}")
            total_fixed += fixed

    print()
    print(f"Totale round corretti: {total_fixed}")


if __name__ == "__main__":
    main()