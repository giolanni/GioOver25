"""Read-only GS1 ticket-size backtest: TOP 1/2/3 and exactly 1/2/3.
Run: python -m analysis.gs1_over_ticket_sizes
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
from analysis.experiments.match_history_features import build_feature_rows,write_csv
from analysis.experiments.v30_v31_full_backtest import enrich
from analysis.gs1_over_lab import features

def classify(f):
    over,delta=f["MinOverRateFull"],f["DeltaGA"]
    if over>=.8 and delta>=.4: return "ALTA",.8,.4
    if over>=.65 and delta>=.4: return "MEDIA",.65,.4
    if over>=.7 and delta>=.22: return "OSSERVAZIONE",.7,.22
    return None

def sort_key(r):
    return (-float(r["MinOverRateFull"]),-float(r["DeltaGA"]),
            r["LeagueId"],r["Home"],r["Away"])

def evaluate(group,cap,exact):
    daily=defaultdict(list)
    for r in group: daily[r["MatchDate"]].append(r)
    picks=[];days=[]
    for d,items in sorted(daily.items()):
        if exact and len(items)<cap: continue
        chosen=sorted(items,key=sort_key)[:cap]
        ok=sum(int(r["Over25"]) for r in chosen)
        days.append({"MatchDate":d,"Picks":len(chosen),"OK":ok,"KO":len(chosen)-ok,
                     "AllOK":int(ok==len(chosen))})
        picks.extend(chosen)
    n=len(picks);ok=sum(int(r["Over25"]) for r in picks)
    clean=sum(r["AllOK"] for r in days)
    return {"OK":ok,"KO":n-ok,"Total":n,
            "AccuracyPct":round(100*ok/n,2) if n else 0,
            "DaysPlayed":len(days),"DaysAllOK":clean,
            "DaysKO":len(days)-clean,
            "DaysAllOKPct":round(100*clean/len(days),2) if days else 0,
            "AvgPicks":round(n/len(days),2) if days else 0},days,picks

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--results-dir",default="data/storico/risultati")
    p.add_argument("--out",default="data/analysis/gs1/over/ticket_sizes")
    p.add_argument("--train-end",default="2026-08-05")
    p.add_argument("--validation-end",default="2026-09-15")
    args=p.parse_args()
    if args.train_end>=args.validation_end: p.error("Split date non valide")
    raw=build_feature_rows(Path(args.results_dir),min_history=5,windows=(5,7,8))
    if not raw: raise SystemExit("Nessuna partita storica valida")
    rows=[]
    for r in raw:
        if r["LeagueId"].startswith("Australia_"): continue
        f=features(enrich(r));b=classify(f)
        if not b: continue
        band,over_t,delta_t=b
        d=r["MatchDate"]
        split="TRAIN" if d<=args.train_end else "VALIDATION" if d<=args.validation_end else "TEST"
        rows.append({"Split":split,"Band":band,"MatchDate":d,"LeagueId":r["LeagueId"],
                     "Home":r["Home"],"Away":r["Away"],"HG":r["HG"],"AG":r["AG"],
                     "Over25":r["Over25"],"MinOverRateFull":f["MinOverRateFull"],
                     "DeltaGA":f["DeltaGA"],"MinOverThreshold":over_t,
                     "DeltaGAThreshold":delta_t})
    scopes={"ALTA":("ALTA",),"MEDIA":("MEDIA",),
            "OSSERVAZIONE":("OSSERVAZIONE",),
            "ALTA+MEDIA":("ALTA","MEDIA"),
            "TUTTE":("ALTA","MEDIA","OSSERVAZIONE")}
    summary=[];daily_out=[];picked_out=[]
    for split in ("TRAIN","VALIDATION","TEST"):
        for scope,bands in scopes.items():
            subset=[r for r in rows if r["Split"]==split and r["Band"] in bands]
            for cap in (1,2,3):
                for mode in ("TOP","EXACT"):
                    metrics,days,picks=evaluate(subset,cap,mode=="EXACT")
                    common={"Split":split,"Scope":scope,"Mode":mode,"MaxPicks":cap}
                    summary.append({**common,**metrics})
                    daily_out.extend({**common,**d} for d in days)
                    picked_out.extend({**common,**r} for r in picks)
                    print(f"{split:10} {scope:13} {mode:5} {cap} "
                          f"OK={metrics['OK']} KO={metrics['KO']} Tot={metrics['Total']} "
                          f"Acc={metrics['AccuracyPct']:.2f}% "
                          f"AllOK={metrics['DaysAllOK']}/{metrics['DaysPlayed']} "
                          f"({metrics['DaysAllOKPct']:.2f}%)")
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/"summary.csv",summary)
    write_csv(out/"daily.csv",daily_out)
    write_csv(out/"selected_matches.csv",picked_out)
    print("Report:",out)
    print("TOP = fino a N; EXACT = solo giornate con almeno N candidati, sceglie N.")
    print("Ordinamento deterministico pre-esito: MinOverRateFull DESC, DeltaGA DESC.")
    print("OSSERVAZIONE e' esplorativa: soglia definita dopo aver visto risultati storici.")
if __name__=="__main__": main()
