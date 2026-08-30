from __future__ import annotations

import argparse
import csv
from collections import defaultdict, deque
from pathlib import Path

RAW_DIR = Path('data/xg/raw')
FEATURE_DIR = Path('data/xg/features')


def _f(value) -> float:
    return float(str(value).replace(',', '.'))


def _avg(values) -> float | None:
    values = list(values)
    return sum(values) / len(values) if values else None


def _fmt(value) -> str:
    return '' if value is None else f'{value:.4f}'


def read_rows(league_id: str) -> list[dict]:
    rows = []
    seen = set()
    for path in sorted(RAW_DIR.glob(f'*/{league_id}*.csv')):
        with path.open('r', encoding='utf-8-sig', newline='') as handle:
            for row in csv.DictReader(handle, delimiter=';'):
                key = (row.get('LeagueId'), row.get('MatchDate'), row.get('Home'), row.get('Away'))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
    rows.sort(key=lambda r: (r.get('MatchDate', ''), r.get('Home', ''), r.get('Away', '')))
    return rows


def build_point_in_time_features(rows: list[dict]) -> list[dict]:
    """Costruisce feature usando solo xG di partite STRETTAMENTE precedenti.

    Le gare dello stesso giorno vengono elaborate come blocco: nessuna partita
    può vedere gli xG di un'altra gara disputata nello stesso giorno. Questo
    rende il dataset adatto ai backtest senza leakage temporale.
    """
    season = defaultdict(lambda: {'xgf': [], 'xga': []})
    recent = defaultdict(lambda: {'xgf': deque(maxlen=10), 'xga': deque(maxlen=10)})
    output = []

    by_date = defaultdict(list)
    for row in rows:
        by_date[row.get('MatchDate', '')].append(row)

    for match_date in sorted(by_date):
        pending_updates = []
        for row in by_date[match_date]:
            league = row['LeagueId']
            home, away = row['Home'], row['Away']
            hk, ak = (league, home), (league, away)

            def side_features(key, prefix: str) -> dict:
                s = season[key]
                r = recent[key]
                result = {
                    f'{prefix}XGPlayed': len(s['xgf']),
                    f'{prefix}XGFAvg': _fmt(_avg(s['xgf'])),
                    f'{prefix}XGAAvg': _fmt(_avg(s['xga'])),
                }
                for n in (3, 5, 10):
                    result[f'{prefix}XGFLast{n}Avg'] = _fmt(_avg(list(r['xgf'])[-n:]))
                    result[f'{prefix}XGALast{n}Avg'] = _fmt(_avg(list(r['xga'])[-n:]))
                return result

            feat = {
                'LeagueId': league,
                'MatchDate': match_date,
                'Home': home,
                'Away': away,
                'ActualHomeXG': row['HomeXG'],
                'ActualAwayXG': row['AwayXG'],
                'Source': row.get('Source', ''),
            }
            feat.update(side_features(hk, 'Home'))
            feat.update(side_features(ak, 'Away'))

            # Stima neutra e leggibile: forza offensiva di una squadra mediata
            # con la vulnerabilità xG dell'avversaria. Non è ancora un engine.
            home_xgf = _avg(season[hk]['xgf'])
            home_xga = _avg(season[hk]['xga'])
            away_xgf = _avg(season[ak]['xgf'])
            away_xga = _avg(season[ak]['xga'])
            projected_home = None if home_xgf is None or away_xga is None else (home_xgf + away_xga) / 2
            projected_away = None if away_xgf is None or home_xga is None else (away_xgf + home_xga) / 2
            projected_total = None if projected_home is None or projected_away is None else projected_home + projected_away
            feat['ProjectedHomeXG'] = _fmt(projected_home)
            feat['ProjectedAwayXG'] = _fmt(projected_away)
            feat['ProjectedTotalXG'] = _fmt(projected_total)
            output.append(feat)

            hxg, axg = _f(row['HomeXG']), _f(row['AwayXG'])
            pending_updates.extend([(hk, hxg, axg), (ak, axg, hxg)])

        for key, xgf, xga in pending_updates:
            season[key]['xgf'].append(xgf)
            season[key]['xga'].append(xga)
            recent[key]['xgf'].append(xgf)
            recent[key]['xga'].append(xga)

    return output


def main() -> None:
    parser = argparse.ArgumentParser(description='Costruisce feature xG point-in-time per backtest/engine')
    parser.add_argument('--league-id', required=True)
    args = parser.parse_args()

    rows = read_rows(args.league_id)
    if not rows:
        raise SystemExit(f'Nessun dato xG trovato per {args.league_id}')
    features = build_point_in_time_features(rows)
    out = FEATURE_DIR / f'xg_features_{args.league_id}.csv'
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(features[0].keys()), delimiter=';')
        writer.writeheader()
        writer.writerows(features)
    print(f'[OK] {len(features)} feature match -> {out}')


if __name__ == '__main__':
    main()
