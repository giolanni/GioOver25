"""GS1-OVER shadow monitor: TOP1 ALTA / OSSERVAZIONE / MEDIA and fallback.
Does not change GS1 rankings, thresholds, or existing historical records.

python -m analysis.gs1_over_shadow data/input_partite/partite.csv
python -m analysis.gs1_over_shadow --results data/input_risultati/risultati.csv
"""
from __future__ import annotations
import argparse
from datetime import date
from pathlib import Path
from gioover25 import gs1_over as gs
from gioover25.history import read_results_file
from gioover25.rank_matches_v2 import (
    read_matches_to_rank,read_registry,get_competition_group,get_group_league_ids)

OUT=Path("data/analysis/gs1/over/shadow")
HISTORY=OUT/"shadow_history.csv"
FIELDS=gs.FIELDS+["Strategy","TicketRank","RuleVersion"]
RULE="gs1-shadow-top1-v1"
BANDS=("ALTA","OSSERVAZIONE","MEDIA")

def write(path,rows):
    import csv
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,delimiter=";",extrasaction="ignore")
        w.writeheader();w.writerows(rows)

def classify(over,delta):
    if over+1e-10>=.8 and delta+1e-10>=.4: return "ALTA",.8,.4
    if over+1e-10>=.65 and delta+1e-10>=.4: return "MEDIA",.65,.4
    if over+1e-10>=.7 and delta+1e-10>=.22: return "OSSERVAZIONE",.7,.22
    return None

def candidates(rows,registry,prediction_date):
    cache={};found=[]
    for row in rows:
        league=row["LeagueId"].strip()
        if league.startswith("Australia_"):continue
        try: match_date=date.fromisoformat(row["MatchDate"].strip())
        except ValueError:continue
        ids=tuple(get_group_league_ids(league,get_competition_group(league,registry),registry))
        if ids not in cache:
            cache[ids]={name:read_results_file(Path("data/storico/risultati")/f"{name}.csv")
                        for name in ids if (Path("data/storico/risultati")/f"{name}.csv").exists()}
        if not cache[ids]:continue
        home=gs._stats(row["Home"],league,cache[ids],match_date)
        away=gs._stats(row["Away"],league,cache[ids],match_date)
        if home is None or away is None:continue
        over=min(home["OverRateFull"],away["OverRateFull"])
        delta=min(home["GAL5"],away["GAL5"])-min(home["GAFull"],away["GAFull"])
        b=classify(over,delta)
        if b is None:continue
        band,ot,dt=b
        found.append({"MatchDate":row["MatchDate"],"LeagueId":league,
                      "Home":row["Home"],"Away":row["Away"],
                      "Round":row.get("Round",""),"PredictionDate":prediction_date,
                      "Band":band,"MinOverThreshold":f"{ot:.6f}",
                      "DeltaGAThreshold":f"{dt:.6f}",
                      "MinOverRateFull":f"{over:.6f}","DeltaGA":f"{delta:.6f}",
                      "HomeOverRateFull":f"{home['OverRateFull']:.6f}",
                      "AwayOverRateFull":f"{away['OverRateFull']:.6f}",
                      "HomeGAFull":f"{home['GAFull']:.6f}",
                      "AwayGAFull":f"{away['GAFull']:.6f}",
                      "HomeGAL5":f"{home['GAL5']:.6f}",
                      "AwayGAL5":f"{away['GAL5']:.6f}",
                      "Status":"SCHEDULED","HG":"","AG":"","Outcome":"",
                      "RuleVersion":RULE})
    return found

def rank(r):
    return (-float(r["MinOverRateFull"]),-float(r["DeltaGA"]),
            r["LeagueId"],r["Home"],r["Away"])

def generate(input_file):
    rows=read_matches_to_rank(Path(input_file))
    found=candidates(rows,read_registry(),date.today().isoformat())
    groups={}
    for r in found:groups.setdefault((r["MatchDate"],r["Band"]),[]).append(r)
    best={}
    for k,items in groups.items():
        for i,r in enumerate(sorted(items,key=rank),1):
            r["TicketRank"]=i
        best[k]=min(items,key=rank)
    output=[]
    dates=sorted({d for d,_ in groups})
    for d in dates:
        alta=best.get((d,"ALTA"));media=best.get((d,"MEDIA"))
        obs=best.get((d,"OSSERVAZIONE"))
        # Every band tracked separately, regardless of fallback.
        for band in BANDS:
            pick=best.get((d,band))
            if pick:
                output.append({**pick,"Strategy":f"{band}_TOP1"})
        if not alta:
            for strategy,pick in (("OSS_FIRST",obs or media),("MEDIA_FIRST",media or obs)):
                if pick:output.append({**pick,"Strategy":strategy})
    write(OUT/"shadow_today.csv",output)
    history=gs.read_csv(HISTORY)
    # Freeze original snapshot; strategy is part of identity, unlike normal GS1.
    existing={(r["Strategy"],gs.key(r)) for r in history}
    new=0
    for r in output:
        k=(r["Strategy"],gs.key(r))
        if k not in existing:
            history.append(r);existing.add(k);new+=1
    write(HISTORY,sorted(history,key=lambda r:(r["MatchDate"],r["Strategy"],r["LeagueId"],r["Home"],r["Away"])))
    print(f"[GS1-SHADOW] candidate={len(found)} tracked={len(output)} new={new} history={HISTORY}")
    for band in BANDS:
        print(f"  {band}_TOP1={sum(r['Strategy']==band+'_TOP1' for r in output)}")
    print(f"  NO_ALTA OSS_FIRST={sum(r['Strategy']=='OSS_FIRST' for r in output)} "
          f"MEDIA_FIRST={sum(r['Strategy']=='MEDIA_FIRST' for r in output)}")

def update(input_file):
    import csv
    history=gs.read_csv(HISTORY)
    if not history:
        print("[GS1-SHADOW] Nessuna selezione storica");return
    index={}
    for r in history:index.setdefault(gs.key(r),[]).append(r)
    changes=0
    with Path(input_file).open(encoding="utf-8-sig",newline="") as f:
        for result in csv.DictReader(f,delimiter=";"):
            k=gs.key(result)
            status=str(result.get("Status","")).strip().upper()
            hg=str(result.get("HG","")).strip()
            ag=str(result.get("AG","")).strip()
            if not status and hg and ag:status="FINALE"
            for target in index.get(k,[]):
                updates={}
                if status in ("RINVIATA","POSTICIPATA","NOT_FOUND"):
                    updates={"Status":status}
                elif status=="FINALE" and hg and ag:
                    try:outcome="OK" if int(hg)+int(ag)>=3 else "KO"
                    except ValueError:continue
                    updates={"Status":"FINALE","HG":hg,"AG":ag,"Outcome":outcome}
                if any(target.get(field)!=value for field,value in updates.items()):
                    target.update(updates);changes+=1
    if changes:write(HISTORY,history)
    print(f"[GS1-SHADOW] esiti aggiornati={changes}")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input_file",nargs="?",default=None)
    p.add_argument("--results",default=None,help="CSV risultati per aggiornare gli esiti")
    args=p.parse_args()
    if args.results:update(args.results)
    elif args.input_file:generate(args.input_file)
    else:p.error("Specificare input_file oppure --results")

if __name__=="__main__":main()
