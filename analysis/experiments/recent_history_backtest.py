from __future__ import annotations
import argparse
from pathlib import Path
from statistics import mean
from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUTPUT_DEFAULT = Path("analysis/experiments/output/recent_history_backtest")
WINDOWS = ("L5","L7","L8")
MATURITY_BANDS = ((5,6,"5-6"),(7,8,"7-8"),(9,12,"9-12"),(13,20,"13-20"),(21,10**9,"21+"))

def clamp01(v): return max(0.0, min(1.0, v))
def signal(row, suffix):
    over = mean([float(row[f"HomeOverRate{suffix}"]), float(row[f"AwayOverRate{suffix}"])])
    goals = mean([float(row[f"HomeGoals{suffix}"]), float(row[f"AwayGoals{suffix}"])])
    attack_def = (
        float(row[f"HomeGF{suffix}"]) + float(row[f"AwayGA{suffix}"]) +
        float(row[f"AwayGF{suffix}"]) + float(row[f"HomeGA{suffix}"])
    ) / 4.0
    return mean([over, clamp01(goals / 4.0), clamp01(attack_def / 2.0)])

def maturity(value):
    n = int(value)
    for lo, hi, label in MATURITY_BANDS:
        if lo <= n <= hi: return label
    return "other"

def evaluate(rows, model, recent_suffix=None, recent_weight=0.0):
    scored = []
    for row in rows:
        full = signal(row, "Full")
        score = full
        if recent_suffix:
            recent = signal(row, recent_suffix)
            score = recent_weight * recent + (1.0 - recent_weight) * full
        scored.append((score, int(row["Over25"]), row))
    scored.sort(key=lambda item: item[0], reverse=True)
    out = []
    for threshold in (0.60,0.65,0.70,0.75,0.80):
        selected = [item for item in scored if item[0] >= threshold]
        if not selected: continue
        hits = sum(item[1] for item in selected)
        out.append({"Model": model, "Slice": f"score>={threshold:.2f}", "N": len(selected),
                    "OK": hits, "KO": len(selected)-hits, "HitRate": round(hits/len(selected)*100,2)})
    for lo, hi, label in MATURITY_BANDS:
        selected = [item for item in scored if lo <= int(item[2]["MinPlayedBefore"]) <= hi]
        if not selected: continue
        selected.sort(key=lambda item: item[0], reverse=True)
        take = max(1, len(selected)//4)
        top = selected[:take]
        hits = sum(item[1] for item in top)
        out.append({"Model": model, "Slice": f"maturity_{label}_top25pct", "N": len(top),
                    "OK": hits, "KO": len(top)-hits, "HitRate": round(hits/len(top)*100,2)})
    return out

def main():
    parser = argparse.ArgumentParser(description="Confronta storico completo e forma recente per Over 2.5.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DEFAULT))
    parser.add_argument("--min-history", type=int, default=5)
    args = parser.parse_args()
    rows = build_feature_rows(min_history=args.min_history, windows=(5,7,8))
    if not rows: raise RuntimeError("Nessuna partita storica eleggibile.")
    for row in rows: row["MaturityBand"] = maturity(row["MinPlayedBefore"])
    results = []
    results += evaluate(rows, "FULL")
    for suffix in WINDOWS:
        results += evaluate(rows, suffix, suffix, 1.0)
        for weight in (0.6,0.7,0.8,0.9):
            results += evaluate(rows, f"{suffix}_{int(weight*100)}REC_{int((1-weight)*100)}FULL", suffix, weight)
    results.sort(key=lambda r: (r["Slice"], -r["HitRate"], -r["N"]))
    outdir = Path(args.output_dir)
    write_csv(outdir/"recent_history_results.csv", results)
    write_csv(outdir/"recent_history_dataset.csv", rows)
    print(f"Partite eleggibili: {len(rows)}")
    print("Output:", outdir/"recent_history_results.csv")
    print("\nMiglior modello per fascia maturita:")
    for _,_,label in MATURITY_BANDS:
        target = f"maturity_{label}_top25pct"
        candidates = [r for r in results if r["Slice"] == target]
        if candidates:
            best = max(candidates, key=lambda r: (r["HitRate"], r["N"]))
            print(f"  {label}: {best['Model']} {best['OK']}/{best['N']} = {best['HitRate']}%")
if __name__ == "__main__": main()
