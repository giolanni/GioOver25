from __future__ import annotations
import argparse
from datetime import date, timedelta
from pathlib import Path
from statistics import mean
from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUTPUT_DEFAULT = Path("analysis/experiments/output/recent_history_backtest")
WINDOWS = ("L5", "L7", "L8")
MATURITY_BANDS = ((5,6,"5-6"),(7,8,"7-8"),(9,12,"9-12"),(13,20,"13-20"),(21,10**9,"21+"))
MODELS = [("FULL", None, 0.0)]
for suffix in WINDOWS:
    MODELS.append((suffix, suffix, 1.0))
    for weight in (0.6, 0.7, 0.8, 0.9):
        MODELS.append((f"{suffix}_{int(weight*100)}REC_{int(round((1-weight)*100))}FULL", suffix, weight))

def clamp01(v): return max(0.0, min(1.0, v))
def parse_date(value):
    try: return date.fromisoformat(str(value).strip())
    except (TypeError, ValueError): return None

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

def model_score(row, recent_suffix=None, recent_weight=0.0):
    full = signal(row, "Full")
    if not recent_suffix: return full
    return recent_weight * signal(row, recent_suffix) + (1.0 - recent_weight) * full

def evaluate(rows, model, recent_suffix=None, recent_weight=0.0):
    scored = [(model_score(row, recent_suffix, recent_weight), int(row["Over25"]), row) for row in rows]
    scored.sort(key=lambda item: item[0], reverse=True)
    out = []
    for threshold in (0.60,0.65,0.70,0.75,0.80):
        selected = [item for item in scored if item[0] >= threshold]
        if not selected: continue
        hits = sum(item[1] for item in selected)
        out.append({"Model": model, "Slice": f"score>={threshold:.2f}", "N": len(selected), "OK": hits,
                    "KO": len(selected)-hits, "HitRate": round(hits/len(selected)*100,2)})
    for lo, hi, label in MATURITY_BANDS:
        selected = [item for item in scored if lo <= int(item[2]["MinPlayedBefore"]) <= hi]
        if not selected: continue
        selected.sort(key=lambda item: item[0], reverse=True)
        take = max(1, len(selected)//4)
        top = selected[:take]
        hits = sum(item[1] for item in top)
        out.append({"Model": model, "Slice": f"maturity_{label}_top25pct", "N": len(top), "OK": hits,
                    "KO": len(top)-hits, "HitRate": round(hits/len(top)*100,2)})
    return out

def top_quarter(rows, model_tuple, label):
    name, suffix, weight = model_tuple
    subset = [r for r in rows if r["MaturityBand"] == label]
    ranked = sorted(((model_score(r, suffix, weight), int(r["Over25"])) for r in subset), reverse=True)
    if not ranked: return {"Model": name, "N": 0, "OK": 0, "HitRate": 0.0}
    take = max(1, len(ranked)//4)
    selected = ranked[:take]
    ok = sum(x[1] for x in selected)
    return {"Model": name, "N": take, "OK": ok, "HitRate": round(ok/take*100, 2)}

def temporal_validation(rows, test_days):
    dates = sorted({parse_date(r["MatchDate"]) for r in rows if parse_date(r["MatchDate"])})
    if not dates: return [], None
    split = dates[-1] - timedelta(days=max(1, test_days) - 1)
    train = [r for r in rows if parse_date(r["MatchDate"]) < split]
    test = [r for r in rows if parse_date(r["MatchDate"]) >= split]
    report = []
    for _, _, label in MATURITY_BANDS:
        train_stats = [top_quarter(train, m, label) for m in MODELS]
        eligible = [x for x in train_stats if x["N"]]
        if not eligible: continue
        winner = max(eligible, key=lambda x: (x["HitRate"], x["N"]))
        chosen = next(m for m in MODELS if m[0] == winner["Model"])
        test_chosen = top_quarter(test, chosen, label)
        full_train = top_quarter(train, MODELS[0], label)
        full_test = top_quarter(test, MODELS[0], label)
        report.append({
            "Maturity": label, "SelectedOnTrain": winner["Model"],
            "Train_Selected_OK": winner["OK"], "Train_Selected_N": winner["N"], "Train_Selected_HitRate": winner["HitRate"],
            "Train_FULL_OK": full_train["OK"], "Train_FULL_N": full_train["N"], "Train_FULL_HitRate": full_train["HitRate"],
            "Train_DeltaVsFULL": round(winner["HitRate"]-full_train["HitRate"], 2),
            "Test_Selected_OK": test_chosen["OK"], "Test_Selected_N": test_chosen["N"], "Test_Selected_HitRate": test_chosen["HitRate"],
            "Test_FULL_OK": full_test["OK"], "Test_FULL_N": full_test["N"], "Test_FULL_HitRate": full_test["HitRate"],
            "Test_DeltaVsFULL": round(test_chosen["HitRate"]-full_test["HitRate"], 2),
        })
    return report, split

def main():
    parser = argparse.ArgumentParser(description="Confronta storico completo e forma recente per Over 2.5.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DEFAULT))
    parser.add_argument("--min-history", type=int, default=5)
    parser.add_argument("--test-days", type=int, default=30, help="Giorni finali usati solo come test temporale (default 30).")
    args = parser.parse_args()
    rows = build_feature_rows(min_history=args.min_history, windows=(5,7,8))
    if not rows: raise RuntimeError("Nessuna partita storica eleggibile.")
    for row in rows: row["MaturityBand"] = maturity(row["MinPlayedBefore"])
    results = []
    for name, suffix, weight in MODELS:
        results += evaluate(rows, name, suffix, weight)
    results.sort(key=lambda r: (r["Slice"], -r["HitRate"], -r["N"]))
    validation, split = temporal_validation(rows, args.test_days)
    outdir = Path(args.output_dir)
    write_csv(outdir/"recent_history_results.csv", results)
    write_csv(outdir/"recent_history_dataset.csv", rows)
    write_csv(outdir/"temporal_validation.csv", validation)
    print(f"Partite eleggibili: {len(rows)}")
    print("\nMiglior modello per fascia maturita (intero campione):")
    for _,_,label in MATURITY_BANDS:
        target = f"maturity_{label}_top25pct"
        candidates = [r for r in results if r["Slice"] == target]
        if candidates:
            best = max(candidates, key=lambda r: (r["HitRate"], r["N"]))
            full = next((r for r in candidates if r["Model"] == "FULL"), None)
            delta = best["HitRate"] - full["HitRate"] if full else 0.0
            print(f"  {label}: {best['Model']} {best['OK']}/{best['N']} = {best['HitRate']}% | FULL {full['HitRate'] if full else 0}% | delta {delta:+.2f}")
    print(f"\nVALIDAZIONE TEMPORALE - test da {split} ({args.test_days} giorni finali)")
    print("Il modello viene scelto SOLO sul train; poi applicato senza riottimizzare al test.")
    for r in validation:
        print(f"  {r['Maturity']}: {r['SelectedOnTrain']} | train {r['Train_Selected_HitRate']}% vs FULL {r['Train_FULL_HitRate']}% ({r['Train_DeltaVsFULL']:+.2f}) | test {r['Test_Selected_HitRate']}% vs FULL {r['Test_FULL_HitRate']}% ({r['Test_DeltaVsFULL']:+.2f}) | Ntest={r['Test_Selected_N']}")
    print("\nOutput:", outdir/"temporal_validation.csv")
if __name__ == "__main__": main()
