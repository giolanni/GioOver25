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


def read_registry() -> list[dict]:
    """Legge il registry xG, che mantiene lo stesso schema del registry canonico."""
    with REGISTRY.open('r', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle, delimiter=';')
        if not reader.fieldnames or 'LeagueId' not in reader.fieldnames:
            raise ValueError(f'{REGISTRY} deve contenere la colonna LeagueId')
        return [row for row in reader if str(row.get('LeagueId', '')).strip()]


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
            raise ValueError('Understat richiede --season/--seasons (anno iniziale, es. 2026)')
        return UnderstatProvider().download_league_matches(league_id, season)
    if provider_name == 'bigballs':
        if league_id not in BIGBALLS_LEAGUES:
            raise ValueError(f'{league_id} non disponibile su Big Balls')
        return BigBallsProvider().download_league_matches(league_id)
    raise ValueError(f'Provider sconosciuto: {provider_name}')


def main() -> None:
    parser = argparse.ArgumentParser(description='Scarica e normalizza dati xG')
    target = parser.add_mutually_exclusive_group()
    target.add_argument('--league-id', help='LeagueId canonico da scaricare')
    target.add_argument('--all', action='store_true', help='Scarica tutte le LeagueId del registry xG supportate dal provider')
    parser.add_argument('--provider', choices=['understat','bigballs'], help='Forza un provider')
    seasons = parser.add_mutually_exclusive_group()
    seasons.add_argument('--season', type=int, help='Singola stagione Understat, es. 2026')
    seasons.add_argument('--seasons', type=int, nargs='+', help='Più stagioni Understat, es. 2022 2023 2024 2025 2026')
    args = parser.parse_args()

    if args.seasons and not args.all and not args.league_id:
        parser.error('--seasons richiede --all oppure --league-id')

    rows = read_registry()
    if args.league_id:
        rows = [row for row in rows if row['LeagueId'] == args.league_id]
        if not rows:
            raise SystemExit(f'LeagueId non presente in {REGISTRY}: {args.league_id}')
    elif not args.all:
        # Compatibilità con il comportamento precedente: senza target esplicito
        # continua a scorrere l'intero registry xG.
        pass

    requested_seasons = args.seasons or ([args.season] if args.season is not None else [None])

    total = 0
    downloaded_files = 0
    for row in rows:
        league_id = str(row['LeagueId']).strip()
        provider_name = args.provider or default_provider(league_id)
        if provider_name not in available_providers(league_id):
            print(f'[SKIP] {league_id}: {provider_name} non supportato')
            continue

        league_seasons = requested_seasons if provider_name == 'understat' else [None]
        if provider_name == 'bigballs' and (args.season is not None or args.seasons):
            print(f'[SKIP] {league_id}: Big Balls non usa --season/--seasons')
            continue

        for season in league_seasons:
            season_label = f' season={season}' if season is not None else ''
            print(f'[XG] {league_id} <- {provider_name}{season_label}')
            try:
                matches = download_one(league_id, provider_name, season)
            except Exception as exc:
                print(f'[WARN] {league_id}{season_label}: {exc}')
                continue

            suffix = f'_{season}' if provider_name == 'understat' and season is not None else ''
            out = RAW_DIR / provider_name / f'{league_id}{suffix}.csv'
            write_matches(out, matches)
            total += len(matches)
            downloaded_files += 1
            print(f'      {len(matches)} match -> {out}')

    print(f'[OK] xG normalizzati: {total} match in {downloaded_files} file')


if __name__ == '__main__':
    main()
