"""Analisi non invasiva delle fasce numeriche Score degli engine GioOver."""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path("data/storico/ranking")
OUT = Path("data/analysis/score_bands")
KEY = ("LeagueId", "MatchDate", "Home", "Away")
FIELDS = ("Engine", "Market", "Scope", "Period", "Type", "ScoreRange",
          "OK", "KO", "Total", "HitRate", "SufficientSample")


def load():
    """Una sola osservazione per partita/engine; i conflitti vengono esclusi."""
    unique = {}
    conflicts = set()
    diagnostics = defaultdict(int)
    for path in sorted(ROOT.glob("*/storico_ranking_*.csv")):
        engine = path.parent.name
        market = "BTTS" if engine.lower().startswith("vg") else "Over25"
        with path.open(encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            required = set(KEY) | {"Score", market}
            if not required.issubset(reader.fieldnames or []):
                diagnostics["missing_columns"] += 1
                continue
            for r in reader:
                outcome = (r.get(market) or "").strip().upper()
                if outcome not in ("OK", "KO"):
                    diagnostics["unresolved"] += 1
                    continue
                try:
                    score = float((r.get("Score") or "").strip().replace(",", "."))
                    day = date.fromisoformat((r.get("MatchDate") or "").strip()[:10])
                    key = (engine,) + tuple((r.get(k) or "").strip() for k in KEY)
                    if not all(key[1:]):
                        raise ValueError("empty key")
                    if not 0 <= score <= 100:
                        raise ValueError("invalid score")
                except (ValueError, TypeError):
                    diagnostics["invalid"] += 1
                    continue
                if key in unique and unique[key][3] != outcome:
                    conflicts.add(key)
                elif key in unique and abs(unique[key][2] - score) > 0.00001:
                    conflicts.add(key)
                else:
                    unique[key] = (day, market, score, outcome, key[1].startswith("Australia_"))
    for key in conflicts:
        unique.pop(key, None)
    diagnostics["conflicts"] = len(conflicts)
    diagnostics["unique"] = len(unique)
    return [(k[0], *v) for k, v in unique.items()], diagnostics


def analyze(rows, width, thresholds, recent_from, min_sample):
    grouped = defaultdict(lambda: [0, 0])
    for engine, day, market, score, outcome, australia in rows:
        bucket = min(int(score // width) * width, 100)
        upper = min(bucket + width, 100)
        label = f"[{bucket},{upper})" if upper < 100 else f"[{bucket},100]"
        groups = [("ALL",), ("NO_AUSTRALIA",)] if not australia else [("ALL",)]
        periods = ["HISTORY"]
        if recent_from is not None and day >= recent_from:
            periods.append("RECENT")
        for (scope,) in groups:
            for period in periods:
                keys = [("INTERVAL", label)]
                keys.extend(("THRESHOLD", f">={t:g}") for t in thresholds if score >= t)
                for kind, band in keys:
                    grouped[(engine, market, scope, period, kind, band)][outcome == "OK"] += 1
    output = []
    for (engine, market, scope, period, kind, band), counts in grouped.items():
        ko, ok = counts
        total = ok + ko
        output.append(dict(zip(FIELDS, (engine, market, scope, period, kind, band,
                          ok, ko, total, round(100 * ok / total, 2),
                          "YES" if total >= min_sample else "NO"))))
    output.sort(key=lambda r: (r["Engine"], r["Scope"], r["Period"], r["Type"],
                              -r["HitRate"], -r["Total"], r["ScoreRange"]))
    return output


def write(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=5)
    parser.add_argument("--min-sample", type=int, default=30)
    parser.add_argument("--recent-from", default="2026-09-16")
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    if not 1 <= args.width <= 100 or args.min_sample < 1:
        parser.error("width deve essere tra 1 e 100 e min-sample >= 1")
    recent = date.fromisoformat(args.recent_from) if args.recent_from else None
    rows, diagnostics = load()
    results = analyze(rows, args.width, list(range(0, 101, 5)), recent, args.min_sample)
    write(args.output_dir / "score_band_details.csv", results, FIELDS)
    best = []
    for engine in sorted({r["Engine"] for r in results}):
        for scope in ("ALL", "NO_AUSTRALIA"):
            for kind in ("INTERVAL", "THRESHOLD"):
                subset = [r for r in results if r["Engine"] == engine and
                          r["Scope"] == scope and r["Period"] == "HISTORY" and
                          r["Type"] == kind and r["SufficientSample"] == "YES"]
                if subset:
                    best.append(subset[0])
    write(args.output_dir / "score_band_best.csv", best, FIELDS)
    write(args.output_dir / "score_band_diagnostics.csv",
          [{"Metric": k, "Value": v} for k, v in sorted(diagnostics.items())],
          ("Metric", "Value"))
    print(f"[DONE] observations={len(rows)} details={len(results)} best={len(best)}")
    print(f"[OUTPUT] {args.output_dir}")


if __name__ == "__main__":
    main()
