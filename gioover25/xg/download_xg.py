from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .providers import BigBallsProvider, UnderstatProvider


ROOT = Path(".")
REGISTRY = ROOT / "data" / "league_registry_xg.csv"
RAW_DIR = ROOT / "data" / "xg" / "raw"


def read_registry() -> list[dict]:
    with REGISTRY.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def write_matches(path: Path, matches) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "LeagueId", "MatchDate", "Home", "Away", "HomeXG", "AwayXG",
        "HomeGoals", "AwayGoals", "Source", "SourceMatchId",
    ]
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        for match in sorted(matches, key=lambda x: (x.match_date, x.home, x.away)):
            writer.writerow(match.to_csv_row())


def download_one(league_id: str, provider_name: str, season: int | None):
    if provider_name == "understat":
        if season is None:
            raise ValueError("Understat richiede --season (anno iniziale, es. 2026)")
        provider = UnderstatProvider()
        return provider.download_league_matches(league_id, season)
    if provider_name == "bigballs":
        return BigBallsProvider().download_league_matches(league_id)
    raise ValueError(f"Provider sconosciuto: {provider_name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Scarica e normalizza dati xG")
    parser.add_argument("--league-id", help="LeagueId canonico; se omesso usa tutto il registry xG")
    parser.add_argument("--provider", choices=["understat", "bigballs"], help="Forza un provider")
    parser.add_argument("--season", type=int, help="Anno iniziale stagione Understat, es. 2026")
    args = parser.parse_args()

    rows = read_registry()
    if args.league_id:
        rows = [row for row in rows if row["LeagueId"] == args.league_id]
        if not rows:
            raise SystemExit(f"LeagueId non presente in {REGISTRY}: {args.league_id}")

    total = 0
    for row in rows:
        league_id = row["LeagueId"]
        provider_name = args.provider or row["PrimaryProvider"]
        if provider_name == "bigballs" and row.get("BigBallsAvailable", "").strip().lower() != "yes":
            print(f"[SKIP] {league_id}: Big Balls non configurato nel registry")
            continue
        if provider_name == "understat" and row.get("UnderstatAvailable", "").strip().lower() != "yes":
            print(f"[SKIP] {league_id}: Understat non configurato nel registry")
            continue

        print(f"[XG] {league_id} <- {provider_name}")
        matches = download_one(league_id, provider_name, args.season)
        suffix = f"_{args.season}" if provider_name == "understat" and args.season else ""
        out = RAW_DIR / provider_name / f"{league_id}{suffix}.csv"
        write_matches(out, matches)
        total += len(matches)
        print(f"      {len(matches)} match -> {out}")

    print(f"[OK] xG normalizzati: {total}")


if __name__ == "__main__":
    main()
