from __future__ import annotations

import argparse
import csv
from pathlib import Path

FEATURE_DIR = Path('data/xg/features')
OUTPUT_DIR = Path('analysis/experiments/xg_feature_backtest/output')

FEATURES = [
    'HomeXGFAvg', 'HomeXGAAvg', 'AwayXGFAvg', 'AwayXGAAvg',
    'HomeXGFLast3Avg', 'HomeXGALast3Avg', 'AwayXGFLast3Avg', 'AwayXGALast3Avg',
    'HomeXGFLast5Avg', 'HomeXGALast5Avg', 'AwayXGFLast5Avg', 'AwayXGALast5Avg',
    'HomeXGFLast10Avg', 'HomeXGALast10Avg', 'AwayXGFLast10Avg', 'AwayXGALast10Avg',
    'ProjectedHomeXG', 'ProjectedAwayXG', 'ProjectedTotalXG',
]


def _to_float(value: str) -> float | None:
    value = str(value or '').strip().replace(',', '.')
    if not value:
        return None
    return float(value)


def _to_int(value: str) -> int | None:
    value = str(value or '').strip()
    if value == '':
        return None
    return int(float(value))


def read_features(league_id: str) -> list[dict]:
    path = FEATURE_DIR / f'xg_features_{league_id}.csv'
    if not path.exists():
        raise SystemExit(f'Feature file non trovato: {path}')
    with path.open('r', encoding='utf-8-sig', newline='') as handle:
        return list(csv.DictReader(handle, delimiter=';'))


def eligible_rows(rows: list[dict], min_played: int) -> list[dict]:
    output = []
    for row in rows:
        over25 = _to_int(row.get('Over25', ''))
        home_played = _to_int(row.get('HomeXGPlayed', ''))
        away_played = _to_int(row.get('AwayXGPlayed', ''))
        if over25 is None or home_played is None or away_played is None:
            continue
        if home_played < min_played or away_played < min_played:
            continue
        output.append(row)
    return output


def quantile_bins(rows: list[dict], feature: str, bins: int) -> list[dict]:
    pairs = []
    for row in rows:
        value = _to_float(row.get(feature, ''))
        over25 = _to_int(row.get('Over25', ''))
        if value is None or over25 is None:
            continue
        pairs.append((value, over25, row))

    pairs.sort(key=lambda item: item[0])
    if not pairs:
        return []

    output = []
    n = len(pairs)
    for i in range(bins):
        start = i * n // bins
        end = (i + 1) * n // bins
        chunk = pairs[start:end]
        if not chunk:
            continue
        ok = sum(item[1] for item in chunk)
        total = len(chunk)
        seasons = sorted({str(item[2].get('Season') or '') for item in chunk})
        output.append({
            'Feature': feature,
            'Bin': i + 1,
            'MinValue': round(chunk[0][0], 4),
            'MaxValue': round(chunk[-1][0], 4),
            'Matches': total,
            'Over25': ok,
            'Under25': total - ok,
            'Over25Pct': round(ok * 100.0 / total, 2),
            'Seasons': ','.join(seasons),
        })
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter=';')
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Laboratorio iniziale: capacità discriminante delle feature xG sull Over 2.5'
    )
    parser.add_argument('--league-id', required=True)
    parser.add_argument('--min-played', type=int, default=5,
                        help='Minimo storico xG pre-match per entrambe le squadre (default 5)')
    parser.add_argument('--bins', type=int, default=10,
                        help='Numero di fasce quantili per feature (default 10)')
    args = parser.parse_args()

    rows = read_features(args.league_id)
    eligible = eligible_rows(rows, args.min_played)
    if not eligible:
        raise SystemExit('Nessuna partita eleggibile: genera prima le feature o riduci --min-played')

    overall_ok = sum(_to_int(row['Over25']) or 0 for row in eligible)
    print(
        f'[XG LAB] {args.league_id}: {len(eligible)} match eleggibili, '
        f'Over2.5={overall_ok}/{len(eligible)} ({overall_ok * 100.0 / len(eligible):.2f}%)'
    )

    all_bins = []
    for feature in FEATURES:
        bins = quantile_bins(eligible, feature, args.bins)
        all_bins.extend(bins)
        if not bins:
            continue
        best = max(bins, key=lambda row: (row['Over25Pct'], row['Matches']))
        worst = min(bins, key=lambda row: (row['Over25Pct'], -row['Matches']))
        print(
            f"  {feature}: best {best['MinValue']}-{best['MaxValue']} = "
            f"{best['Over25Pct']:.2f}% ({best['Matches']}), "
            f"worst {worst['MinValue']}-{worst['MaxValue']} = "
            f"{worst['Over25Pct']:.2f}% ({worst['Matches']})"
        )

    out = OUTPUT_DIR / f'xg_feature_bins_{args.league_id}.csv'
    write_csv(out, all_bins)
    print(f'[OK] Dettaglio fasce -> {out}')


if __name__ == '__main__':
    main()
