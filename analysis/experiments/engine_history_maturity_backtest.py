from __future__ import annotations
import argparse, csv
from pathlib import Path
from analysis.experiments.match_history_features import build_feature_rows, write_csv
from gioover25.team_names import normalize_team_name

RANKING_DIR = Path("data/storico/ranking")
OUTPUT_DEFAULT = Path("analysis/experiments/output/engine_history_maturity_backtest")
BANDS = ((5,6,"5-6"),(7,8,"7-8"),(9,12,"9-12"),(13,20,"13-20"),(21,10**9,"21+"))

def maturity(n):
    for lo,hi,label in BANDS:
        if lo <= n <= hi: return label
    return "other"

def key(league_id, match_date, home, away):
    return (league_id, match_date, normalize_team_name(league_id, home), normalize_team_name(league_id, away))

def stats(rows):
    n=len(rows); ok=sum(int(r["Over25"]) == 1 for r in rows)
    return ok,n-ok,n,round(ok/n*100,2) if n else 0.0

def main():
    parser=argparse.ArgumentParser(description="Misura gli engine per maturita dello storico disponibile.")
    parser.add_argument("--output-dir",default=str(OUTPUT_DEFAULT))
    args=parser.parse_args()
    features=build_feature_rows(min_history=5,windows=(5,7,8))
    idx={key(r["LeagueId"],r["MatchDate"],r["Home"],r["Away"]):r for r in features}
    joined=[]
    for engine_dir in sorted(RANKING_DIR.iterdir() if RANKING_DIR.exists() else []):
        if not engine_dir.is_dir(): continue
        engine=engine_dir.name
        path=engine_dir/f"storico_ranking_{engine}.csv"
        if not path.exists(): continue
        with path.open("r",encoding="utf-8-sig",newline="") as h:
            reader=csv.DictReader(h,delimiter=";")
            for row in reader:
                if str(row.get("MatchStatus","")).strip().upper() not in {"FINAL","FINALE"}: continue
                if str(row.get("Over25","")).strip() not in {"0","1"}: continue
                league_id=str(row.get("LeagueId","")).strip(); md=str(row.get("MatchDate","")).strip()
                f=idx.get(key(league_id,md,row.get("Home",""),row.get("Away","")))
                if f is None: continue
                joined.append({"Engine":engine,"Band":str(row.get("Band","")).strip().upper(),"LeagueId":league_id,"MatchDate":md,
                               "Home":row.get("Home",""),"Away":row.get("Away",""),"Over25":int(row["Over25"]),
                               "MinPlayedBefore":f["MinPlayedBefore"],"MaturityBand":maturity(int(f["MinPlayedBefore"]))})
    if not joined: raise RuntimeError("Nessuna prediction FINAL abbinata allo storico partite.")
    results=[]
    engines=sorted({r["Engine"] for r in joined})
    for engine in engines:
        erows=[r for r in joined if r["Engine"]==engine]
        populations={"ALL":erows,"ALTA":[r for r in erows if r["Band"]=="ALTA"],
                     "IMM-ALTA":[r for r in erows if r["Band"]=="IMM-ALTA"],
                     "ALTA+IMM-ALTA":[r for r in erows if r["Band"] in {"ALTA","IMM-ALTA"}]}
        for pop,prows in populations.items():
            if not prows: continue
            ok,ko,n,hit=stats(prows); results.append({"Engine":engine,"Population":pop,"Maturity":"ALL","OK":ok,"KO":ko,"N":n,"HitRate":hit})
            for _,_,label in BANDS:
                subset=[r for r in prows if r["MaturityBand"]==label]
                if not subset: continue
                ok,ko,n,hit=stats(subset); results.append({"Engine":engine,"Population":pop,"Maturity":label,"OK":ok,"KO":ko,"N":n,"HitRate":hit})
    out=Path(args.output_dir); write_csv(out/"engine_maturity_results.csv",results); write_csv(out/"engine_maturity_joined.csv",joined)
    print(f"Prediction abbinate: {len(joined)}")
    print("\nALTA - migliori engine con storico 5-8 gare:")
    short=[r for r in results if r["Population"]=="ALTA" and r["Maturity"] in {"5-6","7-8"}]
    by_engine={}
    for r in short: by_engine.setdefault(r["Engine"],[]).append(r)
    ranking=[]
    for engine,parts in by_engine.items():
        n=sum(p["N"] for p in parts); ok=sum(p["OK"] for p in parts)
        if n: ranking.append((ok/n*100,n,ok,engine))
    for hit,n,ok,engine in sorted(ranking,reverse=True)[:20]: print(f"  {engine}: {ok}/{n} = {hit:.2f}%")
    print("Output:",out/"engine_maturity_results.csv")
if __name__=="__main__": main()
