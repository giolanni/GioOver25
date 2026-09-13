from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from gioover25.engines.factory import get_available_engines, get_engine
from gioover25.history import read_results_file
from gioover25.match_statistics import build_match_statistics
from gioover25.recent_replacement import replace_overall_with_recent
from gioover25.registry import load_league_registry

RESULTS_DIR = Path("data/storico/risultati")
OUTPUT_DIR = Path("analysis/experiments/output/engine_recent_replacement")
EXCLUDED_ENGINES = {"v30", "v31"}
GROUPS = ("gf", "ga", "over", "form")
WEIGHT_GRID = (0.0, 0.40, 0.60, 0.75, 0.90, 1.00)
WINDOWS = (7, 8)
HUGE_ROUND = 10**9


@dataclass
class Sample:
    match_date: date
    league_id: str
    league_info: object
    stats: object
    target: int


def _as_date(value) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _build_samples() -> list[Sample]:
    registry = load_league_registry()
    samples: list[Sample] = []

    for path in sorted(RESULTS_DIR.glob("*.csv")):
        league_id = path.stem
        league_info = registry.get(league_id)
        if league_info is None:
            continue
        try:
            matches = read_results_file(path)
        except Exception as exc:
            print(f"[SKIP FILE] {league_id}: {exc}")
            continue

        dated = [(m, _as_date(m.date)) for m in matches]
        dated = [(m, d) for m, d in dated if d is not None]
        dated.sort(key=lambda item: (item[1], item[0].home, item[0].away))
        history = []
        i = 0
        while i < len(dated):
            current_date = dated[i][1]
            day = []
            while i < len(dated) and dated[i][1] == current_date:
                day.append(dated[i][0])
                i += 1

            for match in day:
                try:
                    stats = build_match_statistics(
                        history,
                        match.home,
                        match.away,
                        HUGE_ROUND,
                    )
                except Exception:
                    continue
                if min(stats.home.overall.played, stats.away.overall.played) < 8:
                    continue
                samples.append(
                    Sample(
                        match_date=current_date,
                        league_id=league_id,
                        league_info=league_info,
                        stats=stats,
                        target=int(match.home_goals + match.away_goals >= 3),
                    )
                )
            history.extend(day)

    return samples


def _predict(engine, sample: Sample, window: int, weights: dict[str, float]):
    stats = replace_overall_with_recent(
        sample.stats,
        window=window,
        weights=weights,
    )
    try:
        result = engine.calculate_score(stats, sample.league_info)
    except Exception:
        return None
    score = float(getattr(result, "score", 0.0))
    return score >= 75.0


def _evaluate(engine, samples, window, weights):
    n = ok = selected = 0
    for sample in samples:
        pred = _predict(engine, sample, window, weights)
        if pred is None:
            continue
        n += 1
        if pred:
            selected += 1
            ok += sample.target
    hit = (ok / selected * 100.0) if selected else 0.0
    return {"eligible": n, "n": selected, "ok": ok, "hit": hit}


def _better(candidate, best, min_n):
    if candidate["n"] < min_n:
        return False
    if best is None or best["n"] < min_n:
        return True
    if candidate["hit"] != best["hit"]:
        return candidate["hit"] > best["hit"]
    return candidate["n"] > best["n"]


def _calibrate(engine, train, window, min_train_n, passes):
    weights = {group: 0.0 for group in GROUPS}
    baseline = _evaluate(engine, train, window, weights)
    effective_min = max(min_train_n, int(baseline["n"] * 0.25))

    for _ in range(passes):
        changed = False
        for group in GROUPS:
            best_weight = weights[group]
            best_result = _evaluate(engine, train, window, weights)
            for weight in WEIGHT_GRID:
                candidate_weights = dict(weights)
                candidate_weights[group] = weight
                result = _evaluate(engine, train, window, candidate_weights)
                if _better(result, best_result, effective_min):
                    best_result = result
                    best_weight = weight
            if best_weight != weights[group]:
                weights[group] = best_weight
                changed = True
        if not changed:
            break

    final = _evaluate(engine, train, window, weights)
    return weights, baseline, final, effective_min


def _fmt_weights(weights):
    return ",".join(f"{k}={weights[k]:.2f}" for k in GROUPS)


def _write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--engines", nargs="*", default=None)
    parser.add_argument("--test-days", type=int, default=60)
    parser.add_argument("--min-train-alta", type=int, default=40)
    parser.add_argument("--passes", type=int, default=2)
    args = parser.parse_args()

    names = args.engines or [
        name for name in get_available_engines()
        if name not in EXCLUDED_ENGINES
    ]
    names = [name for name in names if name not in EXCLUDED_ENGINES]

    print("Costruzione dataset anti-lookahead...")
    samples = _build_samples()
    if not samples:
        raise SystemExit("Nessun campione disponibile")

    max_date = max(s.match_date for s in samples)
    split_date = max_date - timedelta(days=max(args.test_days - 1, 0))
    train = [s for s in samples if s.match_date < split_date]
    test = [s for s in samples if s.match_date >= split_date]

    print(f"Campioni: {len(samples)} | train={len(train)} | test={len(test)} dal {split_date}")
    summary_rows = []

    for name in names:
        engine = get_engine(name)
        best = None
        print(f"\n=== {name} ===")
        for window in WINDOWS:
            weights, base_train, tuned_train, effective_min = _calibrate(
                engine, train, window, args.min_train_alta, args.passes
            )
            base_test = _evaluate(
                engine, test, window, {group: 0.0 for group in GROUPS}
            )
            tuned_test = _evaluate(engine, test, window, weights)
            row = {
                "Engine": name,
                "Window": window,
                "Weights": _fmt_weights(weights),
                "MinTrainN": effective_min,
                "TrainBaseN": base_train["n"],
                "TrainBaseHit": round(base_train["hit"], 2),
                "TrainTunedN": tuned_train["n"],
                "TrainTunedHit": round(tuned_train["hit"], 2),
                "TrainLift": round(tuned_train["hit"] - base_train["hit"], 2),
                "TestBaseN": base_test["n"],
                "TestBaseHit": round(base_test["hit"], 2),
                "TestTunedN": tuned_test["n"],
                "TestTunedHit": round(tuned_test["hit"], 2),
                "TestLift": round(tuned_test["hit"] - base_test["hit"], 2),
            }
            summary_rows.append(row)
            print(
                f"L{window} {_fmt_weights(weights)} | "
                f"TRAIN {tuned_train['ok']}/{tuned_train['n']}={tuned_train['hit']:.2f}% "
                f"(base {base_train['hit']:.2f}%, lift {row['TrainLift']:+.2f}) | "
                f"TEST {tuned_test['ok']}/{tuned_test['n']}={tuned_test['hit']:.2f}% "
                f"(base {base_test['hit']:.2f}%, lift {row['TestLift']:+.2f})"
            )
            candidate_key = (row["TestLift"], row["TestTunedHit"], row["TestTunedN"])
            if best is None or candidate_key > best[0]:
                best = (candidate_key, row)

        if best:
            row = best[1]
            print(
                f"BEST VALIDATED {name}: L{row['Window']} {row['Weights']} | "
                f"test {row['TestTunedHit']:.2f}% N={row['TestTunedN']} "
                f"lift {row['TestLift']:+.2f}"
            )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(OUTPUT_DIR / "summary.csv", summary_rows)
    print(f"\nOutput: {OUTPUT_DIR / 'summary.csv'}")


if __name__ == "__main__":
    main()
