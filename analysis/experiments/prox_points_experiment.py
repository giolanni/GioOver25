from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

import pandas as pd

from gioover25.team_names import normalize_team_name

RANKING_ROOT = Path('data/storico/ranking')
RESULTS_ROOT = Path('data/storico/risultati')
OUTPUT_DIR = Path('analysis/experiments/prox_points')
MIN_MATCHES_PLAYED = 10
POINT_GAPS = (1, 2, 3, 4, 5)
VALID_BANDS = {'ALTA', 'MEDIA', 'BASSA'}
VALID_OUTCOMES = {'OK', 'KO'}


def detect_delimiter(path: Path) -> str:
    sample = path.read_text(encoding='utf-8-sig', errors='replace')[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=';,\t,').delimiter
    except csv.Error:
        return ';'


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep=detect_delimiter(path), encoding='utf-8-sig', dtype=str, low_memory=False)


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
    return round(ok / total * 100.0, 4) if total else 0.0


def engine_history_files() -> list[tuple[str, Path]]:
    files = []
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
    results = results[results['_Date'].notna() & results['_HG'].notna() & results['_AG'].notna()].copy()
    results['_HomeCanonical'] = results['Home'].map(lambda v: normalize_team_name(league_id, v))
    results['_AwayCanonical'] = results['Away'].map(lambda v: normalize_team_name(league_id, v))
    return results.sort_values('_Date')


def reconstruct_table(results: pd.DataFrame, before_date: date) -> dict[str, dict[str, int]]:
    previous = results[results['_Date'] < before_date]
    table: dict[str, dict[str, int]] = {}

    def ensure(team: str) -> dict[str, int]:
        return table.setdefault(team, {'played': 0, 'points': 0})

    for _, match in previous.iterrows():
        home = match['_HomeCanonical']
        away = match['_AwayCanonical']
        hg = int(match['_HG'])
        ag = int(match['_AG'])
        h = ensure(home)
        a = ensure(away)
        h['played'] += 1
        a['played'] += 1
        if hg > ag:
            h['points'] += 3
        elif hg < ag:
            a['points'] += 3
        else:
            h['points'] += 1
            a['points'] += 1
    return table


def build_base_matches() -> tuple[pd.DataFrame, pd.DataFrame]:
    result_cache: dict[str, pd.DataFrame | None] = {}
    table_cache: dict[tuple[str, date], dict[str, dict[str, int]]] = {}
    matches = []
    unmatched = []

    for engine, history_file in engine_history_files():
        history = read_csv(history_file)
        if not {'LeagueId', 'Home', 'Away', 'Band'}.issubset(history.columns):
            continue
        for _, row in history.iterrows():
            outcome = outcome_from_row(row)
            band = str(row.get('Band', '')).strip().upper()
            if outcome not in VALID_OUTCOMES or band not in VALID_BANDS:
                continue
            league_id = str(row.get('LeagueId', '')).strip()
            match_date = parse_date(row.get('MatchDate')) or parse_date(row.get('PredictionDate'))
            if not league_id or match_date is None:
                unmatched.append({'Engine': engine, 'LeagueId': league_id, 'Home': row.get('Home', ''), 'Away': row.get('Away', ''), 'Reason': 'LeagueId o data non valida'})
                continue
            if league_id not in result_cache:
                result_cache[league_id] = load_results(league_id)
            results = result_cache[league_id]
            if results is None:
                unmatched.append({'Engine': engine, 'LeagueId': league_id, 'Home': row.get('Home', ''), 'Away': row.get('Away', ''), 'Reason': 'File risultati assente o non valido'})
                continue
            key = (league_id, match_date)
            if key not in table_cache:
                table_cache[key] = reconstruct_table(results, match_date)
            table = table_cache[key]
            home = normalize_team_name(league_id, row.get('Home', ''))
            away = normalize_team_name(league_id, row.get('Away', ''))
            h = table.get(home)
            a = table.get(away)
            if h is None or a is None:
                unmatched.append({'Engine': engine, 'LeagueId': league_id, 'Home': row.get('Home', ''), 'Away': row.get('Away', ''), 'Reason': 'Squadra non trovata nella classifica ricostruita'})
                continue
            matches.append({
                'Engine': engine,
                'LeagueId': league_id,
                'MatchDate': match_date.isoformat(),
                'Home': row.get('Home', ''),
                'Away': row.get('Away', ''),
                'Band': band,
                'Outcome': outcome,
                'HomePlayed': h['played'],
                'AwayPlayed': a['played'],
                'HomePoints': h['points'],
                'AwayPoints': a['points'],
                'PointsGap': abs(h['points'] - a['points']),
            })

    return pd.DataFrame(matches), pd.DataFrame(unmatched)


def summarize(rows: pd.DataFrame, engine: str, max_gap: int) -> tuple[dict, pd.DataFrame]:
    current = rows.copy()
    current['IsProx'] = (
        (current['HomePlayed'] >= MIN_MATCHES_PLAYED)
        & (current['AwayPlayed'] >= MIN_MATCHES_PLAYED)
        & (current['PointsGap'] <= max_gap)
    )
    prox = current[current['IsProx']]
    prox_ok = int((prox['Outcome'] == 'OK').sum())
    prox_ko = int((prox['Outcome'] == 'KO').sum())
    summary = {
        'Engine': engine,
        'MaxPointsGap': max_gap,
        'MinMatchesPlayed': MIN_MATCHES_PLAYED,
        'PROX_OK': prox_ok,
        'PROX_KO': prox_ko,
        'PROX_Total': prox_ok + prox_ko,
        'PROX_HitRate': safe_rate(prox_ok, prox_ko),
    }
    for band in ('ALTA', 'MEDIA', 'BASSA'):
        original = current[current['Band'] == band]
        prox_band = current[(current['Band'] == band) & current['IsProx']]
        remaining = current[(current['Band'] == band) & (~current['IsProx'])]
        original_ok = int((original['Outcome'] == 'OK').sum())
        original_ko = int((original['Outcome'] == 'KO').sum())
        prox_ok = int((prox_band['Outcome'] == 'OK').sum())
        prox_ko = int((prox_band['Outcome'] == 'KO').sum())
        rem_ok = int((remaining['Outcome'] == 'OK').sum())
        rem_ko = int((remaining['Outcome'] == 'KO').sum())
        original_rate = safe_rate(original_ok, original_ko)
        rem_rate = safe_rate(rem_ok, rem_ko)
        summary[f'{band}_OriginalOK'] = original_ok
        summary[f'{band}_OriginalKO'] = original_ko
        summary[f'{band}_OriginalHitRate'] = original_rate
        summary[f'PROX_{band}_OK'] = prox_ok
        summary[f'PROX_{band}_KO'] = prox_ko
        summary[f'PROX_{band}_Total'] = prox_ok + prox_ko
        summary[f'PROX_{band}_HitRate'] = safe_rate(prox_ok, prox_ko)
        summary[f'Remaining{band}OK'] = rem_ok
        summary[f'Remaining{band}KO'] = rem_ko
        summary[f'Remaining{band}HitRate'] = rem_rate
        summary[f'{band}Delta'] = round(rem_rate - original_rate, 4)
    return summary, current[current['IsProx']].copy()


def judgement(row: pd.Series) -> str:
    prox_alta = int(row['PROX_ALTA_Total'])
    original_alta = int(row['ALTA_OriginalOK']) + int(row['ALTA_OriginalKO'])
    removed_share = prox_alta / original_alta if original_alta else 0.0
    alta_delta = float(row['ALTADelta'])
    media_delta = float(row['MEDIADelta'])
    if prox_alta < 10 or removed_share > 0.25:
        return 'CAMPIONE_NON_VALIDO'
    if alta_delta >= 1.0 and media_delta >= 0.0:
        return 'CONSIGLIATO'
    if alta_delta > 0.0 and media_delta >= -0.5:
        return 'DEBOLE'
    return 'NON_UTILE'


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    matches, unmatched = build_base_matches()
    if matches.empty:
        raise RuntimeError('Nessuna partita analizzabile trovata.')

    summary_rows = []
    prox_rows = []

    for engine, engine_rows in matches.groupby('Engine'):
        for max_gap in POINT_GAPS:
            summary, prox = summarize(engine_rows, engine, max_gap)
            summary_rows.append(summary)
            if not prox.empty:
                prox = prox.copy()
                prox['MaxPointsGap'] = max_gap
                prox_rows.append(prox)

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(OUTPUT_DIR / '01_summary.csv', sep=';', index=False, encoding='utf-8-sig')

    (pd.concat(prox_rows, ignore_index=True) if prox_rows else pd.DataFrame()).to_csv(
        OUTPUT_DIR / '02_matches.csv', sep=';', index=False, encoding='utf-8-sig'
    )

    recommendations = []
    for engine, engine_rows in summary_df.groupby('Engine'):
        evaluated = engine_rows.copy()
        evaluated['Judgement'] = evaluated.apply(judgement, axis=1)
        evaluated['Utility'] = evaluated['ALTADelta'] * 2 + evaluated['MEDIADelta']
        valid = evaluated[evaluated['Judgement'] != 'CAMPIONE_NON_VALIDO']
        selected = valid.sort_values(by=['Utility', 'ALTADelta', 'PROX_ALTA_Total'], ascending=[False, False, False]).head(1) if not valid.empty else evaluated.head(1)
        recommendations.append(selected.iloc[0].to_dict())

    recommendations_df = pd.DataFrame(recommendations)
    recommendations_df.to_csv(OUTPUT_DIR / '03_recommendations.csv', sep=';', index=False, encoding='utf-8-sig')
    unmatched.to_csv(OUTPUT_DIR / '04_unmatched.csv', sep=';', index=False, encoding='utf-8-sig')

    print(f'Partite analizzate: {len(matches)}')
    print(f'Engine analizzati: {matches["Engine"].nunique()}')
    print(f'Soglie testate: {len(POINT_GAPS)}')
    print(f'Righe non abbinate: {len(unmatched)}')
    print(f'Output: {OUTPUT_DIR}')


if __name__ == '__main__':
    main()
