"""GS1-OVER paired same-day TOP1 comparison; read-only.
Run: python -m analysis.gs1_over_same_day
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
from analysis.experiments.match_history_features import build_feature_rows, write_csv
from analysis.experiments.v30_v31_full_backtest import enrich
from analysis.gs1_over_lab import features
from analysis.gs1_over_ticket_sizes import classify, sort_key

BANDS=("ALTA","MEDIA","OSSERVAZIONE")
PAIRS=(("MEDIA","OSSERVAZIONE"),("ALTA","MEDIA"),("ALTA","OSSERVAZIONE"))

def split_of(d,train_end,val_end):
    return "TRAIN" if d<=train_end else "VALIDATION" if d<=val_end else "TEST"

def metrics(pairs,left,right):
    n=len(pairs)
    both=sum(a["Over25"]=="1" and b["Over25"]=="1" for a,b in pairs)
    left_only=sum(a["Over25"]=="1" and b["Over25"]=="0" for a,b in pairs)
    right_only=sum(a["Over25"]=="0" and b["Over25"]=="1" for a,b in pairs)
    neither=n-both-left_only-right_only
    return {"DaysBothAvailable":n,"BothOK":both,
            f"{left}OnlyOK":left_only,f"{right}OnlyOK":right_only,
            "BothKO":neither,f"{left}OK":both+left_only,
            f"{right}OK":both+right_only,
            f"{left}AccuracyPct":round(100*(both+left_only)/n,2) if n else 0,
            f"{right}AccuracyPct":round(100*(both+right_only)/n,2) if n else 0,
            "DifferencePctPoints":round(100*(right_only-left_only)/n,2) if n else 0}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--results-dir",default="data/storico/risultati")
    p.add_argument("--out",default="data/analysis/gs1/over/same_day")
    p.add_argument("--train-end",default="2026-08-05")
    p.add_argument("--validation-end",default="2026-09-15")
    args=p.parse_args()
    if args.train_end>=args.validation_end: p.error("Date split non valide")
    raw=build_feature_rows(Path(args.results_dir),min_history=5,windows=(5,7,8))
    if not raw: raise SystemExit("Nessun risultato storico valido")
    grouped=defaultdict(list)
    for r in raw:
        if r["LeagueId"].startswith("Australia_"): continue
        f=features(enrich(r))
        classification=classify(f)
        if not classification: continue
        band,over_t,delta_t=classification
        d=r["MatchDate"]
        grouped[(split_of(d,args.train_end,args.validation_end),d,band)].append({
            "Split":split_of(d,args.train_end,args.validation_end),
            "MatchDate":d,"Band":band,"LeagueId":r["LeagueId"],
            "Home":r["Home"],"Away":r["Away"],"HG":r["HG"],"AG":r["AG"],
            "Over25":str(int(r["Over25"])),
            "MinOverRateFull":f["MinOverRateFull"],"DeltaGA":f["DeltaGA"],
            "MinOverThreshold":over_t,"DeltaGAThreshold":delta_t})
    best={k:sorted(rows,key=sort_key)[0] for k,rows in grouped.items()}
    dates=sorted({(split,d) for split,d,_ in best})
    selections=[]; paired_rows=[]; summaries=[]; fallback=[]
    for (split,d,band),r in sorted(best.items()):
        selections.append(r)
    for split in ("TRAIN","VALIDATION","TEST"):
        for left,right in PAIRS:
            for scope in ("ALL_DAYS","NO_ALTA"):
                comparison=[]
                for s,d in dates:
                    if s!=split: continue
                    if scope=="NO_ALTA" and (s,d,"ALTA") in best: continue
                    a=best.get((s,d,left));b=best.get((s,d,right))
                    if a is None or b is None: continue
                    comparison.append((a,b))
                    paired_rows.append({
                        "Split":split,"Scope":scope,"MatchDate":d,
                        "LeftBand":left,"RightBand":right,
                        "LeftLeagueId":a["LeagueId"],"LeftHome":a["Home"],"LeftAway":a["Away"],
                        "LeftOver25":a["Over25"],"LeftMinOverRateFull":a["MinOverRateFull"],
                        "LeftDeltaGA":a["DeltaGA"],
                        "RightLeagueId":b["LeagueId"],"RightHome":b["Home"],"RightAway":b["Away"],
                        "RightOver25":b["Over25"],"RightMinOverRateFull":b["MinOverRateFull"],
                        "RightDeltaGA":b["DeltaGA"]})
                result=metrics(comparison,left,right)
                summaries.append({"Split":split,"Scope":scope,"LeftBand":left,
                                  "RightBand":right,**result})
                print(f"{split:10} {scope:8} {left:12} vs {right:12} "
                      f"days={result['DaysBothAvailable']} "
                      f"OK={result[left+'OK']}/{result[right+'OK']} "
                      f"onlyOK={result[left+'OnlyOK']}/{result[right+'OnlyOK']} "
                      f"bothOK={result['BothOK']} bothKO={result['BothKO']}")
        # No-ALTA days: compare alternative strategies on the SAME opportunity calendar.
        no_alta=sorted(d for s,d in dates if s==split and (s,d,"ALTA") not in best)
        for strategy in ("MEDIA_ONLY","OSS_ONLY","MEDIA_FIRST","OSS_FIRST"):
            offered=0;ok=0
            for d in no_alta:
                media=best.get((split,d,"MEDIA"))
                obs=best.get((split,d,"OSSERVAZIONE"))
                pick={"MEDIA_ONLY":media,"OSS_ONLY":obs,
                      "MEDIA_FIRST":media or obs,"OSS_FIRST":obs or media}[strategy]
                if pick is None: continue
                offered+=1;ok+=int(pick["Over25"])
                fallback.append({"Split":split,"MatchDate":d,"Strategy":strategy,
                                 "Band":pick["Band"],"LeagueId":pick["LeagueId"],
                                 "Home":pick["Home"],"Away":pick["Away"],
                                 "Over25":pick["Over25"],
                                 "MinOverRateFull":pick["MinOverRateFull"],
                                 "DeltaGA":pick["DeltaGA"],
                                 "MinOverThreshold":pick["MinOverThreshold"],
                                 "DeltaGAThreshold":pick["DeltaGAThreshold"]})
            summaries.append({"Split":split,"Scope":"NO_ALTA_FALLBACK",
                              "LeftBand":strategy,"RightBand":"",
                              "OpportunityDays":len(no_alta),
                              "DaysWithPick":offered,"DaysOK":ok,
                              "DaysKO":offered-ok,
                              "AccuracyPct":round(100*ok/offered,2) if offered else 0,
                              "CoveragePct":round(100*offered/len(no_alta),2) if no_alta else 0})
            print(f"{split:10} NO_ALTA {strategy:12} OK={ok} KO={offered-ok} "
                  f"Days={offered}/{len(no_alta)}")
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"summary.csv",summaries)
    write_csv(out/"paired_days.csv",paired_rows)
    write_csv(out/"top1_selections.csv",selections)
    write_csv(out/"no_alta_fallback.csv",fallback)
    print("Report:",out)
    print("OnlyOK counts are discordant days; compare them, not just raw accuracies.")
    print("Historical TEST is exploratory for the post-hoc OSSERVAZIONE threshold.")
if __name__=="__main__": main()
