"""GS1-OVER independent selector. No ranking engine dependencies."""
from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

from .history import read_results_file
from .team_names import normalize_team_name

OUTPUT_DIR = Path("data/output_gs1_over")
HISTORY_FILE = Path("data/storico/gs1_over/storico_gs1_over.csv")
NEAR_HISTORY_FILE = Path("data/storico/gs1_over/storico_gs1_over_near.csv")
FIELDS = ["MatchDate","LeagueId","Home","Away","Round","PredictionDate",
          "Band","MinOverThreshold","DeltaGAThreshold","MinOverRateFull","DeltaGA","HomeOverRateFull","AwayOverRateFull",
          "HomeGAFull","AwayGAFull","HomeGAL5","AwayGAL5",
          "Status","HG","AG","Outcome"]
MIN_OVER = 0.8
MEDIA_MIN_OVER = 0.65
MIN_DELTA_GA = 0.4
NEAR_MIN_OVER = 0.60
NEAR_MIN_DELTA_GA = 0.22


def key(row):
    league = str(row.get("LeagueId","")).strip()
    return (league,str(row.get("MatchDate","")).strip(),
            normalize_team_name(league,row.get("Home","")),
            normalize_team_name(league,row.get("Away","")))


def read_csv(path):
    if not path.exists(): return []
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f,delimiter=";"))


def write_csv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,delimiter=";",extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _goals(match):
    try: return int(match.home_goals),int(match.away_goals)
    except (ValueError,TypeError,AttributeError): return None


def _stats(team,league,histories,match_date):
    observations=[]
    target=normalize_team_name(league,team)
    for source_league,matches in histories.items():
        for match in matches:
            try: d=date.fromisoformat(str(match.date).strip())
            except ValueError: continue
            if d>=match_date: continue
            goals=_goals(match)
            if goals is None: continue
            home=normalize_team_name(league,match.home)
            away=normalize_team_name(league,match.away)
            if home==target:
                gf,ga=goals
            elif away==target:
                ga,gf=goals
            else: continue
            observations.append((d,gf,ga))
    observations.sort(key=lambda v:v[0])
    if len(observations)<5: return None
    n=len(observations)
    return {"OverRateFull":sum(int(gf+ga>=3) for _,gf,ga in observations)/n,
            "GAFull":sum(ga for _,_,ga in observations)/n,
            "GAL5":sum(ga for _,_,ga in observations[-5:])/5}


def select_both(rows,registry_rows,prediction_date):
    from .rank_matches_v2 import get_competition_group,get_group_league_ids
    result=[]
    near=[]
    cache={}
    for row in rows:
        league=row["LeagueId"].strip()
        # Keep initial lab's exclusion of Australia.
        if league.startswith("Australia_"): continue
        try: match_date=date.fromisoformat(row["MatchDate"].strip())
        except ValueError: continue
        ids=tuple(get_group_league_ids(league,get_competition_group(league,registry_rows),registry_rows))
        if ids not in cache:
            cache[ids]={name:read_results_file(Path("data/storico/risultati")/f"{name}.csv")
                        for name in ids if (Path("data/storico/risultati")/f"{name}.csv").exists()}
        histories=cache[ids]
        if not histories: continue
        home=_stats(row["Home"],league,histories,match_date)
        away=_stats(row["Away"],league,histories,match_date)
        if home is None or away is None: continue
        min_over=min(home["OverRateFull"],away["OverRateFull"])
        # Same definition as analysis.gs1_over_lab.features:
        # DeltaGA = min(GA_L5 home, GA_L5 away) - min(GA_full home, GA_full away).
        delta=min(home["GAL5"],away["GAL5"])-min(home["GAFull"],away["GAFull"])
        official = min_over+1e-10>=MEDIA_MIN_OVER and delta+1e-10>=MIN_DELTA_GA
        if not official and (min_over+1e-10<NEAR_MIN_OVER or delta+1e-10<NEAR_MIN_DELTA_GA):
            continue
        if official:
            band = "ALTA" if min_over+1e-10>=MIN_OVER else "MEDIA"
            over_threshold = MIN_OVER if band=="ALTA" else MEDIA_MIN_OVER
        elif min_over+1e-10>=MIN_OVER:
            band,over_threshold = "PROX-ALTA",MIN_OVER
        elif min_over+1e-10>=0.70:
            band,over_threshold = "PROX-MEDIA-DELTA",0.70
        else:
            band,over_threshold = "PROX-MEDIA-OVER",MEDIA_MIN_OVER
        record = {"MatchDate":row["MatchDate"],"LeagueId":league,
                       "Home":row["Home"],"Away":row["Away"],
                       "Round":row.get("Round",""),"PredictionDate":prediction_date,
                       "Band":band,
                       "MinOverThreshold":f"{over_threshold:.6f}",
                       "DeltaGAThreshold":f"{MIN_DELTA_GA:.6f}",
                       "MinOverRateFull":f"{min_over:.6f}","DeltaGA":f"{delta:.6f}",
                       "HomeOverRateFull":f"{home['OverRateFull']:.6f}",
                       "AwayOverRateFull":f"{away['OverRateFull']:.6f}",
                       "HomeGAFull":f"{home['GAFull']:.6f}","AwayGAFull":f"{away['GAFull']:.6f}",
                       "HomeGAL5":f"{home['GAL5']:.6f}","AwayGAL5":f"{away['GAL5']:.6f}",
                       "Status":"SCHEDULED","HG":"","AG":"","Outcome":""}
        (result if official else near).append(record)
    order={"ALTA":0,"MEDIA":1,"PROX-ALTA":0,"PROX-MEDIA-DELTA":1,"PROX-MEDIA-OVER":2}
    sorter=lambda x:(x["MatchDate"],order[x["Band"]],-float(x["MinOverRateFull"]),
                     -float(x["DeltaGA"]),x["LeagueId"],x["Home"],x["Away"])
    return sorted(result,key=sorter),sorted(near,key=sorter)


def select(rows,registry_rows,prediction_date):
    """Compatibility API: official GS1 selections only."""
    official,_=select_both(rows,registry_rows,prediction_date)
    return official


def _append_history(path,selections):
    previous=read_csv(path)
    by_key={key(r):r for r in previous}
    inserted=0
    for row in selections:
        k=key(row)
        if k not in by_key:
            by_key[k]=row
            inserted+=1
    write_csv(path,sorted(by_key.values(),key=lambda r:(r["MatchDate"],r["LeagueId"],r["Home"],r["Away"])))
    return inserted


def select_near(rows, registry_rows, prediction_date):
    """GS1 Near/OSSERVAZIONE: vicino alle soglie ufficiali, non selezione GS1."""
    from .rank_matches_v2 import get_competition_group, get_group_league_ids
    result = []
    cache = {}
    for row in rows:
        league = row["LeagueId"].strip()
        if league.startswith("Australia_"):
            continue
        try:
            match_date = date.fromisoformat(row["MatchDate"].strip())
        except ValueError:
            continue
        ids = tuple(get_group_league_ids(
            league, get_competition_group(league, registry_rows), registry_rows
        ))
        if ids not in cache:
            cache[ids] = {
                name: read_results_file(Path("data/storico/risultati") / f"{name}.csv")
                for name in ids
                if (Path("data/storico/risultati") / f"{name}.csv").exists()
            }
        histories = cache[ids]
        if not histories:
            continue
        home = _stats(row["Home"], league, histories, match_date)
        away = _stats(row["Away"], league, histories, match_date)
        if home is None or away is None:
            continue
        min_over = min(home["OverRateFull"], away["OverRateFull"])
        delta = min(home["GAL5"], away["GAL5"]) - min(home["GAFull"], away["GAFull"])

        # Regola OSSERVAZIONE congelata dal GS1 shadow:
        # MinOver >= .70 e DeltaGA >= .22. Escludiamo le partite che
        # soddisfano gia' ALTA o MEDIA ufficiali.
        official = (
            min_over + 1e-10 >= MEDIA_MIN_OVER
            and delta + 1e-10 >= MIN_DELTA_GA
        )
        near = min_over + 1e-10 >= 0.70 and delta + 1e-10 >= 0.22
        if not near or official:
            continue

        result.append({
            "MatchDate": row["MatchDate"], "LeagueId": league,
            "Home": row["Home"], "Away": row["Away"],
            "Round": row.get("Round", ""), "PredictionDate": prediction_date,
            "Band": "NEAR",
            "MinOverThreshold": "0.700000",
            "DeltaGAThreshold": "0.220000",
            "MinOverRateFull": f"{min_over:.6f}", "DeltaGA": f"{delta:.6f}",
            "HomeOverRateFull": f"{home['OverRateFull']:.6f}",
            "AwayOverRateFull": f"{away['OverRateFull']:.6f}",
            "HomeGAFull": f"{home['GAFull']:.6f}", "AwayGAFull": f"{away['GAFull']:.6f}",
            "HomeGAL5": f"{home['GAL5']:.6f}", "AwayGAL5": f"{away['GAL5']:.6f}",
            "Status": "SCHEDULED", "HG": "", "AG": "", "Outcome": "",
        })
    return sorted(
        result,
        key=lambda x: (-float(x["MinOverRateFull"]), -float(x["DeltaGA"]),
                       x["MatchDate"], x["LeagueId"], x["Home"], x["Away"]),
    )


def generate(rows,registry_rows,prediction_date,base_name):
    selections,near=select_both(rows,registry_rows,prediction_date)
    output=OUTPUT_DIR/f"{base_name}_gs1_over.csv"
    near_output=OUTPUT_DIR/f"{base_name}_gs1_over_near.csv"
    write_csv(output,selections)
    write_csv(near_output,near)
    inserted=_append_history(HISTORY_FILE,selections)
    near_inserted=_append_history(NEAR_HISTORY_FILE,near)
    high_count=sum(r["Band"]=="ALTA" for r in selections)
    print(f"[GS1-OVER] ALTA={high_count} MEDIA={len(selections)-high_count} "
          f"nuove_storico={inserted} output={output}")
    counts={b:sum(r["Band"]==b for r in near) for b in
            ("PROX-ALTA","PROX-MEDIA-DELTA","PROX-MEDIA-OVER")}
    print(f"[GS1-NEAR] {counts} nuove_storico={near_inserted} output={near_output}")
    return selections


def _update_history(input_file,history_file):
    rows=read_csv(history_file)
    if not rows: return
    by_key={key(r):r for r in rows}
    by_teams={}
    for r in rows:
        league,_,home,away=key(r)
        by_teams.setdefault((league,home,away),[]).append(r)
    changed=0
    with Path(input_file).open(encoding="utf-8-sig",newline="") as f:
        for result in csv.DictReader(f,delimiter=";"):
            league=result.get("LeagueId","").strip()
            match_date=result.get("MatchDate","").strip()
            home=normalize_team_name(league,result.get("Home",""))
            away=normalize_team_name(league,result.get("Away",""))
            target=by_key.get((league,match_date,home,away))
            status=str(result.get("Status","")).strip().upper()
            hg=str(result.get("HG","")).strip()
            ag=str(result.get("AG","")).strip()
            if not status and hg and ag: status="FINALE"
            if target is None and status in ("FINALE","RINVIATA","POSTICIPATA","NOT_FOUND"):
                candidates=[r for r in by_teams.get((league,home,away),[])
                            if r.get("Status","").upper() in ("SCHEDULED","NOT_FOUND","POSTICIPATA","RINVIATA")]
                # Avoid ambiguous repeated fixtures and unrelated same-team matches.
                if len(candidates)==1 and candidates[0]["Status"] in ("RINVIATA","POSTICIPATA","NOT_FOUND"):
                    target=candidates[0]
            if target is None: continue
            if status in ("RINVIATA","POSTICIPATA","NOT_FOUND"):
                if target["Status"]!=status:
                    target["Status"]=status;changed+=1
            elif status=="FINALE" and hg!="" and ag!="":
                try: outcome="OK" if int(hg)+int(ag)>=3 else "KO"
                except ValueError: continue
                if (target.get("Status"),target.get("HG"),target.get("AG"),target.get("Outcome"))!=("FINALE",hg,ag,outcome):
                    target.update(Status="FINALE",HG=hg,AG=ag,Outcome=outcome)
                    changed+=1
    if changed:
        write_csv(history_file,rows)
    print(f"[GS1] {history_file.name}: {changed} variazioni")



def update_results(input_file):
    _update_history(input_file,HISTORY_FILE)
    _update_history(input_file,NEAR_HISTORY_FILE)



def diagnose(rows,registry_rows):
    from .rank_matches_v2 import get_competition_group,get_group_league_ids
    cache={}
    totals={"input":0,"australia_excluded":0,"invalid_date":0,"no_history":0,
            "insufficient_history":0,"over_pass":0,"delta_pass":0,"both_pass":0}
    near=[]
    for row in rows:
        totals["input"]+=1
        league=row["LeagueId"].strip()
        if league.startswith("Australia_"):
            totals["australia_excluded"]+=1
            continue
        try: match_date=date.fromisoformat(row["MatchDate"].strip())
        except ValueError:
            totals["invalid_date"]+=1
            continue
        ids=tuple(get_group_league_ids(league,get_competition_group(league,registry_rows),registry_rows))
        if ids not in cache:
            cache[ids]={name:read_results_file(Path("data/storico/risultati")/f"{name}.csv")
                        for name in ids if (Path("data/storico/risultati")/f"{name}.csv").exists()}
        histories=cache[ids]
        if not histories:
            totals["no_history"]+=1
            continue
        home=_stats(row["Home"],league,histories,match_date)
        away=_stats(row["Away"],league,histories,match_date)
        if home is None or away is None:
            totals["insufficient_history"]+=1
            continue
        over=min(home["OverRateFull"],away["OverRateFull"])
        delta=min(home["GAL5"],away["GAL5"])-min(home["GAFull"],away["GAFull"])
        if over+1e-10>=MIN_OVER: totals["over_pass"]+=1
        if delta+1e-10>=MIN_DELTA_GA: totals["delta_pass"]+=1
        if over+1e-10>=MIN_OVER and delta+1e-10>=MIN_DELTA_GA: totals["both_pass"]+=1
        near.append((over,delta,league,row["Home"],row["Away"]))
    print("[GS1-DIAG] "+", ".join(f"{k}={v}" for k,v in totals.items()))
    print("[GS1-DIAG] Top 15 per MinOverRateFull (diagnostica, NON selezioni):")
    for over,delta,league,home,away in sorted(near,key=lambda x:(x[0],x[1]),reverse=True)[:15]:
        print(f"  Over={over:.3f} DeltaGA={delta:+.3f} | {league} | {home} - {away}")

def main():
    import argparse
    from datetime import date
    from .rank_matches_v2 import read_matches_to_rank, read_registry
    parser=argparse.ArgumentParser(description="Genera GS1-OVER senza rigenerare ranking")
    parser.add_argument("input_file",help="CSV delle partite da selezionare")
    parser.add_argument("--diagnose",action="store_true",help="Mostra i motivi di esclusione e le partite piu vicine alla soglia")
    args=parser.parse_args()
    input_path=Path(args.input_file)
    rows=read_matches_to_rank(input_path)
    base_name=input_path.stem.replace("partite","ranking")
    registry=read_registry()
    if args.diagnose: diagnose(rows,registry)
    generate(rows,registry,date.today().isoformat(),base_name)


if __name__=="__main__":
    main()
