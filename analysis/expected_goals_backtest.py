"""Backtest walk-forward per ExpectedGoals. Eseguire dalla root del repository."""
import argparse
import csv
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

from gioover25.expected_goals import estimate_expected_goals
from gioover25.history import read_results_file
from gioover25.team_names import normalize_team_name


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="data/storico/risultati")
    parser.add_argument("--output", default="data/analysis/expected_goals_backtest.csv")
    args = parser.parse_args()
    records = []
    skipped = 0
    files = sorted(Path(args.results_dir).glob("*.csv"))
    for path in files:
        league_id = path.stem
        try:
            matches = read_results_file(path)
        except (ValueError, OSError) as exc:
            print(f"[WARN] {path}: {exc}")
            continue
        histories = {league_id: matches}
        for match in matches:
            try:
                day = date.fromisoformat(match.date)
            except ValueError:
                skipped += 1
                continue
            predicted = estimate_expected_goals(
                histories=histories, home=match.home, away=match.away,
                home_source=league_id, away_source=league_id,
                match_date=day, include_all_histories=False,
                normalize_team=normalize_team_name,
                match_date_of=lambda m: date.fromisoformat(m.date),
                match_goals=lambda m: (m.home_goals, m.away_goals),
            )
            if predicted is None:
                skipped += 1
                continue
            actual = match.home_goals + match.away_goals
            records.append({
                "LeagueId": league_id, "MatchDate": match.date,
                "Home": match.home, "Away": match.away,
                "ExpectedGoals": f"{predicted:.2f}", "ActualGoals": actual,
                "Error": f"{predicted - actual:.2f}",
                "AbsoluteError": f"{abs(predicted - actual):.2f}",
                "Over15": int(actual >= 2), "Over25": int(actual >= 3),
            })
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    columns = ["LeagueId", "MatchDate", "Home", "Away", "ExpectedGoals",
               "ActualGoals", "Error", "AbsoluteError", "Over15", "Over25"]
    with output.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=columns, delimiter=";")
        writer.writeheader()
        writer.writerows(records)

    def report(name, subset):
        if not subset:
            return
        errors = [float(r["Error"]) for r in subset]
        mae = sum(abs(x) for x in errors) / len(errors)
        bias = sum(errors) / len(errors)
        rmse = math.sqrt(sum(x*x for x in errors) / len(errors))
        print(f"{name}: N={len(errors)} MAE={mae:.3f} Bias={bias:.3f} RMSE={rmse:.3f}")

    print(f"File analizzati: {len(files)}; previsioni: {len(records)}; escluse: {skipped}")
    report("TOTALE", records)
    by_league = defaultdict(list)
    for record in records:
        by_league[record["LeagueId"]].append(record)
    for league, subset in sorted(by_league.items(), key=lambda item: -len(item[1])):
        report(league, subset)
    print(f"Dettaglio: {output}")


if __name__ == "__main__":
    main()
