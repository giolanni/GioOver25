from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from gioover25.team_names import normalize_team_name

RANKING_ROOT = Path('data/storico/ranking')
RESULTS_ROOT = Path('data/storico/risultati')
OUTPUT_DIR = Path('analysis/experiments/prox_all_engines')

POINT_GAPS = (1, 2, 3, 4, 5, 6)
GOAL_GAPS = (1, 2, 3, 4, 5, 6)
VALID_OUTCOMES = {'OK', 'KO'}
VALID_BANDS = {'ALTA', 'MEDIA', 'BASSA'}


@dataclass(frozen=True)
class Standing:
    played: int = 0
    points: int = 0
    goals_for: int = 0
    goals_against: int = 0


def detect_delimiter(path: Path) -> str:
    sample = path.read_text(encoding='utf-8-sig', errors='replace')[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=';,\t,').delimiter
    except csv.Error:
        return ';'


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=detect_delimiter(path),
        encoding='utf-8-sig',
        dtype=str,
        low_memory=False,
    )


def parse_date(value) -> date | None:
    raw = str(value or '').strip()
    if not raw or raw.lower() == 'nan':
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def optional_int(value) -> int | None:
    raw = str(value or '').strip()
    if not raw or raw.lower() == 'nan':
        return None
    try:
        return int(float(raw))
    except ValueError:
        return None


def outcome_from_row(row: pd.Series) -> str:
    outcome = str(row.get('Over25', '')).strip().upper()
    if outcome in VALID_OUTCOMES:
        return outcome
    hg = optional_int(row.get('HG'))
    ag = optional_int(row.get('AG'))
    if hg is None or ag is None:
        return ''
    return 'OK' if hg + ag >= 3 else 'KO'


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko
    return 0.0 if total == 0 else round(ok / total * 100.0, 4)


def engine_history_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []
    if not RANKING_ROOT.exists():
        return files
    for engine_dir in sorted(RANKING_ROOT.iterdir()):
        if not engine_dir.is_dir():
            continue
        engine = engine_dir.name
        history = engine_dir / f'storico_ranking_{engine}.csv'
        if history.exists():
            files.append((engine, history))
    return files


def load_results(league_id: str) -> pd.DataFrame | None:
    path = RESULTS_ROOT / f'{league_id}.csv'
    if not path.exists():
        return None
    results = read_csv(path)
    required = {'MatchDate', 'Home', 'Away', 'HG', 'AG'}
    if not required.issubset(results.columns):
        return None
    results = results.copy()
    results['_Date'] = results['MatchDate'].map(parse_date)
    results['_HG'] = results['HG'].map(optional_int)
    results['_AG'] = results['AG'].map(optional_int)
    results = results[
        results['_Date'].notna()
        & results['_HG'].notna()
        & results['_AG'].notna()
    ].copy()
    results['_HomeCanonical'] = results['Home'].map(
        lambda value: normalize_team_name(league_id, value)
    )
    results['_AwayCanonical'] = results['Away'].map(
        lambda value: normalize_team_name(league_id, value)
    )
    return results.sort_values('_Date')


def reconstruct_standings(results: pd.DataFrame, before_date: date) -> dict[str, Standing]:
    previous = results[results['_Date'] < before_date]
    mutable: dict[str, dict[str, int]] = {}

    def ensure(team: str) -> dict[str, int]:
        return mutable.setdefault(
            team,
            {'played': 0, 'points': 0, 'goals_for': 0, 'goals_against': 0},
        )

    for _, match in previous.iterrows():
        home = match['_HomeCanonical']
        away = match['_AwayCanonical']
        hg = int(match['_HG'])
        ag = int(match['_AG'])
        home_row = ensure(home)
        away_row = ensure(away)
        home_row['played'] += 1
        away_row['played'] += 1
        home_row['goals_for'] += hg
        home_row['goals_against'] += ag
        away_row['goals_for'] += ag
        away_row['goals_against'] += hg
        if hg > ag:
            home_row['points'] += 3
        elif hg < ag:
            away_row['points'] += 3
        else:
            home_row['points'] += 1
            away_row['points'] += 1

    return {team: Standing(**values) for team, values in mutable.items()}


def build_base_matches() -> tuple[pd.DataFrame, pd.DataFrame]:
    result_cache: dict[str, pd.DataFrame | None] = {}
    standings_cache: dict[tuple[str, date], dict[str, Standing]] = {}
    detail_rows: list[dict] = []
    unmatched_rows: list[dict] = []

    for engine, history_file in engine_history_files():
        history = read_csv(history_file)
        required = {'LeagueId', 'Home', 'Away', 'Band'}
        if not required.issubset(history.columns):
            continue

        for _, row in history.iterrows():
            outcome = outcome_from_row(row)
            band = str(row.get('Band', '')).strip().upper()
            if outcome not in VALID_OUTCOMES or band not in VALID_BANDS:
                continue

            league_id = str(row.get('LeagueId', '')).strip()
            match_date = parse_date(row.get('MatchDate')) or parse_date(row.get('PredictionDate'))
            if not league_id or match_date is None:
                unmatched_rows.append({
                    'Engine': engine,
                    'LeagueId': league_id,
                    'Home': row.get('Home', ''),
                    'Away': row.get('Away', ''),
                    'Reason': 'LeagueId o data non valida',
                })
                continue

            if league_id not in result_cache:
                result_cache[league_id] = load_results(league_id)
            results = result_cache[league_id]
            if results is None:
                unmatched_rows.append({
                    'Engine': engine,
                    'LeagueId': league_id,
                    'Home': row.get('Home', ''),
                    'Away': row.get('Away', ''),
                    'Reason': 'File risultati assente o non valido',
                })
                continue

            cache_key = (league_id, match_date)
            if cache_key not in standings_cache:
                standings_cache[cache_key] = reconstruct_standings(results, match_date)
            standings = standings_cache[cache_key]

            home = normalize_team_name(league_id, row.get('Home', ''))
            away = normalize_team_name(league_id, row.get('Away', ''))
            home_standing = standings.get(home)
            away_standing = standings.get(away)
            if home_standing is None or away_standing is None:
                unmatched_rows.append({
                    'Engine': engine,
                    'LeagueId': league_id,
                    'Home': row.get('Home', ''),
                    'Away': row.get('Away', ''),
                    'Reason': 'Squadra non trovata nella classifica ricostruita',
                })
                continue

            detail_rows.append({
                'Engine': engine,
                'LeagueId': league_id,
                'MatchDate': match_date.isoformat(),
                'Home': row.get('Home', ''),
                'Away': row.get('Away', ''),
                'OriginalBand': band,
                'Outcome': outcome,
                'HomePlayed': home_standing.played,
                'AwayPlayed': away_standing.played,
                'HomePoints': home_standing.points,
                'AwayPoints': away_standing.points,
                'PointsGap': abs(home_standing.points - away_standing.points),
                'HomeGF': home_standing.goals_for,
                'AwayGF': away_standing.goals_for,
                'GoalsForGap': abs(home_standing.goals_for - away_standing.goals_for),
            })

    return pd.DataFrame(detail_rows), pd.DataFrame(unmatched_rows)


def summarize_configuration(details: pd.DataFrame, point_gap: int, goal_gap: int) -> tuple[dict, pd.DataFrame]:
    config = details.copy()
    config['IsProx'] = (
        (config['PointsGap'] <= point_gap)
        & (config['GoalsForGap'] <= goal_gap)
    )
    config['NewBand'] = config['OriginalBand']
    config.loc[config['IsProx'], 'NewBand'] = 'PROX-' + config.loc[config['IsProx'], 'OriginalBand']

    prox = config[config['IsProx']]
    prox_ok = int((prox['Outcome'] == 'OK').sum())
    prox_ko = int((prox['Outcome'] == 'KO').sum())
    summary = {
        'PointsGapMax': point_gap,
        'GoalsForGapMax': goal_gap,
        'PROX_OK': prox_ok,
        'PROX_KO': prox_ko,
        'PROX_Total': prox_ok + prox_ko,
        'PROX_HitRate': safe_rate(prox_ok, prox_ko),
    }

    for band in ('ALTA', 'MEDIA', 'BASSA'):
        original = config[config['OriginalBand'] == band]
        remaining = config[(config['OriginalBand'] == band) & (~config['IsProx'])]
        prox_band = config[(config['OriginalBand'] == band) & (config['IsProx'])]

        original_ok = int((original['Outcome'] == 'OK').sum())
        original_ko = int((original['Outcome'] == 'KO').sum())
        remaining_ok = int((remaining['Outcome'] == 'OK').sum())
        remaining_ko = int((remaining['Outcome'] == 'KO').sum())
        prox_band_ok = int((prox_band['Outcome'] == 'OK').sum())
        prox_band_ko = int((prox_band['Outcome'] == 'KO').sum())

        original_rate = safe_rate(original_ok, original_ko)
        remaining_rate = safe_rate(remaining_ok, remaining_ko)

        summary[f'{band}_OriginalOK'] = original_ok
        summary[f'{band}_OriginalKO'] = original_ko
        summary[f'{band}_OriginalHitRate'] = original_rate
        summary[f'PROX_{band}_OK'] = prox_band_ok
        summary[f'PROX_{band}_KO'] = prox_band_ko
        summary[f'PROX_{band}_Total'] = prox_band_ok + prox_band_ko
        summary[f'PROX_{band}_HitRate'] = safe_rate(prox_band_ok, prox_band_ko)
        summary[f'Remaining{band}OK'] = remaining_ok
        summary[f'Remaining{band}KO'] = remaining_ko
        summary[f'Remaining{band}HitRate'] = remaining_rate
        summary[f'{band}Delta'] = round(remaining_rate - original_rate, 4)

    return summary, config


def engine_summaries(details: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    for engine, engine_rows in details.groupby('Engine'):
        for point_gap in POINT_GAPS:
            for goal_gap in GOAL_GAPS:
                summary, _ = summarize_configuration(engine_rows, point_gap, goal_gap)
                summary['Engine'] = engine
                rows.append(summary)
    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    details, unmatched = build_base_matches()
    if details.empty:
        raise RuntimeError('Nessuna partita analizzabile trovata.')

    all_summary_rows: list[dict] = []
    all_config_details: list[pd.DataFrame] = []
    for point_gap in POINT_GAPS:
        for goal_gap in GOAL_GAPS:
            summary, config = summarize_configuration(details, point_gap, goal_gap)
            all_summary_rows.append(summary)
            config = config.copy()
            config['PointsGapMax'] = point_gap
            config['GoalsForGapMax'] = goal_gap
            all_config_details.append(config)

    threshold_summary = pd.DataFrame(all_summary_rows)
    threshold_summary.to_csv(
        OUTPUT_DIR / '01_threshold_summary.csv',
        sep=';', index=False, encoding='utf-8-sig'
    )

    engine_summary = engine_summaries(details)
    engine_summary.to_csv(
        OUTPUT_DIR / '02_engine_summary.csv',
        sep=';', index=False, encoding='utf-8-sig'
    )

    pd.concat(all_config_details, ignore_index=True).to_csv(
        OUTPUT_DIR / '03_match_details.csv',
        sep=';', index=False, encoding='utf-8-sig'
    )

    eligible = threshold_summary[threshold_summary['PROX_ALTA_Total'] >= 20].copy()
    eligible['Utility'] = eligible['ALTADelta'] * 2 + eligible['MEDIADelta']
    best = eligible.sort_values(
        by=['Utility', 'ALTADelta', 'PROX_ALTA_Total'],
        ascending=[False, False, False],
    )
    best.to_csv(
        OUTPUT_DIR / '04_best_thresholds.csv',
        sep=';', index=False, encoding='utf-8-sig'
    )

    unmatched.to_csv(
        OUTPUT_DIR / '05_unmatched.csv',
        sep=';', index=False, encoding='utf-8-sig'
    )

    print(f'Partite analizzate: {len(details)}')
    print(f"Engine analizzati: {details['Engine'].nunique()}")
    print(f'Configurazioni soglia: {len(POINT_GAPS) * len(GOAL_GAPS)}')
    print(f'Righe non abbinate: {len(unmatched)}')
    print(f'Output: {OUTPUT_DIR}')
    print()

    columns = [
        'PointsGapMax', 'GoalsForGapMax',
        'PROX_ALTA_OK', 'PROX_ALTA_KO', 'PROX_ALTA_Total',
        'PROX_ALTA_HitRate', 'RemainingALTAHitRate', 'ALTADelta',
        'PROX_MEDIA_Total', 'PROX_MEDIA_HitRate',
        'RemainingMEDIAHitRate', 'MEDIADelta', 'Utility',
    ]
    if best.empty:
        print('Nessuna configurazione con almeno 20 PROX-ALTA.')
    else:
        print(best[columns].head(10).to_string(index=False))


if __name__ == '__main__':
    main()
