from __future__ import annotations

import argparse
import csv
from pathlib import Path

from .providers import BigBallsProvider, UnderstatProvider
from .providers.bigballs import BIGBALLS_LEAGUES
from .providers.understat import UNDERSTAT_LEAGUES

ROOT = Path('.')
REGISTRY = ROOT / 'data' / 'league_registry_xg.csv'
RAW_DIR = ROOT / 'data' / 'xg' / 'raw'


def read_registry() -> list[str]:
    with REGISTRY.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, delimiter=';')
        if reader.fieldnames != ['LeagueId']:
            raise ValueError(f'{REGISTRY} deve contenere la sola colonna LeagueId')
        return [str(row['LeagueId']).strip() for row in reader if str(row.get('LeagueId', '')).strip()]


def write_matches(path: Path, matches) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ['LeagueId','MatchDate','Home','Away','HomeXG','AwayXG','HomeGoals','AwayGoals','Source','SourceMatchId']
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for match in sorted(matches, key=lambda x: (x.match_date, x.home, x.away)):
            writer.writerow(match.to_csv_row())


def available_providers(league_id: str) -> list[str]:
    providers = []
    if league_id in UNDERSTAT_LEAGUES:
        providers.append('understat')
    if league_id in BIGBALLS_LEAGUES:
        providers.append('bigballs')
    return providers


def default_provider(league_id: str) -> str:
    if league_id in UNDERSTAT_LEAGUES:
        return 'understat'
    if league_id in BIGBALLS_LEAGUES:
        return 'bigballs'
    raise ValueError(f'Nessun provider xG configurato per {league_id}')


def download_one(league_id: str, provider_name: str, season: int | None):
    if provider_name == 'understat':
        if league_id not in UNDERSTAT_LEAGUES:
            raise ValueError(f'{league_id} non disponibile su Understat')
        if season is None:
            raise ValueError('Understat richiede --season (anno iniziale, es. 2026)')
        return UnderstatProvider().download_league_matches(league_id, season)
    if provider_name == 'bigballs':
        if league_id not in BIGBALLS_LEAGUES:
            raise ValueError(f'{league_id} non disponibile su Big Balls')
        return BigBallsProvider().download_league_matches(league_id)
    raise ValueError(f'Provider sconosciuto: {provider_name}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Scarica e normalizza dati xG')
    parser.add_argument('--league-id', help='LeagueId canonico; se omesso usa tutto il registry xG')
    parser.add_argument('--provider', choices=['understat','bigballs'], help='Forza un provider')
    parser.add_argument('--season', type=int, help='Anno iniziale stagione Understat, es. 2026')
    args = parser.parse_args()

    league_ids = read_registry()
    if args.league_id:
        if args.league_id not in league_ids:
            raise SystemExit(f'LeagueId non presente in {REGISTRY}: {args.league_id}')
        league_ids = [args.league_id]

    total = 0
    for league_id in league_ids:
        provider_name = args.provider or default_provider(league_id)
        if provider_name not in available_providers(league_id):
            print(f'[SKIP] {league_id}: {provider_name} non supportato')
            continue
        print(f'[XG] {league_id} <- {provider_name}')
        try:
            matches = download_one(league_id, provider_name, args.season)
        except Exception as exc:
            print(f'[WARN] {league_id}: {exc}')
            continue
        suffix = f'_{args.season}' if provider_name == 'understat' and args.season else ''
        out = RAW_DIR / provider_name / f'{league_id}{suffix}.csv'
        write_matches(out, matches)
        total += len(matches)
        print(f'      {len(matches)} match -> {out}')

    print(f'[OK] xG normalizzati: {total}')


if __name__ == '__main__':
    main()
