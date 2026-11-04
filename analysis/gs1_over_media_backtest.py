"""Read-only comparison of GS1 MEDIA current vs dynamic threshold.
Run: python -m analysis.gs1_over_media_backtest
Never changes predictions, ranking engines or GS1 history.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
from analysis.experiments.match_history_features import build_feature_rows, write_csv
from analysis.gs1_over_lab import features

def band(f, variant):
    over=f["MinOverRateFull"]
    delta=f["DeltaGA"]
    if over >= .8 and delta >= .4:
        return "ALTA", .8, .4
    threshold=.22 if variant=="DYNAMIC" and over>=.7 else .4
    if over>=.65 and delta>=threshold:
        return "MEDIA", .7 if variant=="DYNAMIC" and over>=.7 else .65, threshold
    return None

def summarize(rows):
    days=defaultdict(list)
    for r in rows: days[r["MatchDate"]].append(r)
    ok=sum(int(r["Over25"]) for r in rows)
    clean=sum(all(int(r["Over25"]) for r in matches) for matches in days.values())
    return {"OK":ok,"KO":len(rows)-ok,"Total":len(rows),
            "AccuracyPct":round(ok*100/len(rows),2) if rows else 0,
            "DaysPlayed":len(days),"DaysAllOK":clean,
            "DaysAllOKPct":round(clean*100/len(days),2) if days else 0,
            "AvgPicksPerDay":round(len(rows)/len(days),2) if days else 0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--results-dir",default="data/storico/risultati")
    p.add_argument("--out",default="data/analysis/gs1/over/media_comparison")
    p.add_argument("--train-end",default="2026-08-05")
    p.add_argument("--validation-end",default="2026-09-15")
    args=p.parse_args()
    if args.train_end>=args.validation_end: p.error("Split date non valide")
    raw=build_feature_rows(Path(args.results_dir),min_history=5,windows=(5,7,8))
    if not raw: raise SystemExit("Nessun risultato storico")
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    summary=[]; selected=[]
    for r in raw:
        if r["LeagueId"].startswith("Australia_"): continue
        d=r["MatchDate"]
        split="TRAIN" if d<=args.train_end else "VALIDATION" if d<=args.validation_end else "TEST"
        f=features(r)
        for variant in ("CURRENT","DYNAMIC"):
            b=band(f,variant)
            if not b: continue
            name,over_t,delta_t=b
            selected.append({"Split":split,"Variant":variant,"Band":name,
                "MatchDate":d,"LeagueId":r["LeagueId"],"Home":r["Home"],"Away":r["Away"],
                "HG":r["HG"],"AG":r["AG"],"Over25":r["Over25"],
                "MinOverRateFull":f["MinOverRateFull"],"DeltaGA":f["DeltaGA"],
                "MinOverThreshold":over_t,"DeltaGAThreshold":delta_t})
    for split in ("TRAIN","VALIDATION","TEST"):
        for variant in ("CURRENT","DYNAMIC"):
            for name in ("ALTA","MEDIA","COMBINED"):
                subset=[r for r in selected if r["Split"]==split and r["Variant"]==variant
                        and (name=="COMBINED" or r["Band"]==name)]
                row={"Split":split,"Variant":variant,"Band":name,**summarize(subset)}
                summary.append(row)
                print(f"{split:10} {variant:7} {name:8} OK={row['OK']} KO={row['KO']} "
                      f"Tot={row['Total']} Acc={row['AccuracyPct']:.2f}% "
                      f"AllOK={row['DaysAllOK']}/{row['DaysPlayed']} ({row['DaysAllOKPct']:.2f}%)")
    write_csv(out/"summary.csv",summary)
    write_csv(out/"selected_matches.csv",selected)
    print("Report:",out)
    print("ATTENZIONE: soglia dinamica proposta dopo aver visto risultati; TEST non e' conferma indipendente.")

if __name__=="__main__": main()
