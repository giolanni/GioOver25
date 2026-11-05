"""GM1: controllo qualità del dataset prepartita (sola lettura).

Esecuzione: python -m analysis.metrics.gm1_validate_dataset
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

SOURCE = Path("data/analysis/gm1_pre_match_dataset.csv")
OUT = Path("data/analysis")
KEY = ("LeagueId", "MatchDate", "Home", "Away")
FEATURES = ("HomePlayed", "AwayPlayed", "HomePPG", "AwayPPG",
            "HomeGFLast5", "AwayGFLast5", "HomeGALast5", "AwayGALast5",
            "HomeOver25Last5", "AwayOver25Last5",
            "HomeBTTSLast5", "AwayBTTSLast5",
            "HomeVenueOver25", "AwayVenueOver25")


def write(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")


def run():
    if not SOURCE.exists():
        raise SystemExit(f"File mancante: {SOURCE}")
    by_match = defaultdict(list)
    engines = Counter()
    band_engine = defaultdict(lambda: [0, 0, 0])
    feature_coverage = defaultdict(Counter)
    warnings = []
    n = 0
    with SOURCE.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f, delimiter=";"):
            n += 1
            engine = row["Engine"]
            engines[engine] += 1
            key = tuple(row[k] for k in KEY)
            by_match[key].append(row)
            band = (row.get("Band") or "").strip()
            item = band_engine[(engine, band)]
            item[0] += 1
            item[1] += (row["Over25"] == "OK")
            item[2] += (row["Over15"] == "OK")
            for field in FEATURES:
                if str(row.get(field) or "").strip():
                    feature_coverage[engine][field] += 1
            for field in ("HomePlayed", "AwayPlayed"):
                try:
                    if float(row[field]) < 0:
                        warnings.append(dict(LeagueId=key[0], MatchDate=key[1],
                                             Home=key[2], Away=key[3],
                                             Issue="NEGATIVE_PLAYED", Detail=engine))
                except (ValueError, KeyError, TypeError):
                    warnings.append(dict(LeagueId=key[0], MatchDate=key[1],
                                         Home=key[2], Away=key[3],
                                         Issue="INVALID_PLAYED", Detail=engine))
    for key, rows in by_match.items():
        outcomes = {(r["Over25"], r["Over15"]) for r in rows}
        if len(outcomes) != 1:
            warnings.append(dict(zip(KEY, key), Issue="CONFLICTING_OUTCOME",
                                 Detail=";".join(sorted(str(x) for x in outcomes))))
        same_engine = Counter(r["Engine"] for r in rows)
        for engine, count in same_engine.items():
            if count > 1:
                warnings.append(dict(zip(KEY, key), Issue="DUPLICATE_ENGINE_MATCH",
                                     Detail=f"{engine}:{count}"))
        # All features must describe the same fixture independently of engine.
        for field in FEATURES:
            values = {r.get(field, "") for r in rows}
            if len(values) > 1:
                warnings.append(dict(zip(KEY, key), Issue="FEATURE_MISMATCH",
                                     Detail=field))
    metrics = []
    for (engine, band), (total, over25, over15) in band_engine.items():
        metrics.append({"Engine": engine, "Band": band, "Total": total,
                        "Over25_OK": over25, "Over25_KO": total - over25,
                        "Over25_Pct": round(100 * over25 / total, 2),
                        "Over15_OK": over15, "Over15_KO": total - over15,
                        "Over15_Pct": round(100 * over15 / total, 2)})
    metrics.sort(key=lambda r: (-r["Over25_Pct"], -r["Total"], r["Engine"]))
    coverage = [{"Engine": e, "Feature": feat, "NonEmpty": feature_coverage[e][feat],
                 "Total": count, "Pct": round(100 * feature_coverage[e][feat] / count, 2)}
                for e, count in sorted(engines.items()) for feat in FEATURES]
    write(OUT / "gm1_validation_engine_band.csv", metrics,
          ("Engine", "Band", "Total", "Over25_OK", "Over25_KO", "Over25_Pct",
           "Over15_OK", "Over15_KO", "Over15_Pct"))
    write(OUT / "gm1_validation_feature_coverage.csv", coverage,
          ("Engine", "Feature", "NonEmpty", "Total", "Pct"))
    write(OUT / "gm1_validation_warnings.csv", warnings,
          (*KEY, "Issue", "Detail"))
    print(f"[GM1] rows={n} unique_matches={len(by_match)} engines={len(engines)} "
          f"warnings={len(warnings)}")
    print("[GM1] ATTENZIONE: metriche descrittive in-sample, NON backtest GM1.")


if __name__ == "__main__":
    run()
