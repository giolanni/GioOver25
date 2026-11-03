"""GS1 OVER: ottimizzazione della probabilita' che TUTTE le selezioni giornaliere siano OK.

TRAIN/VALIDATION selezionano le regole; TEST e' solo audit, non guida la ricerca.
La regola base seleziona TUTTE le partite idonee, senza tetto fisso.
Esecuzione: python -m analysis.gs1_over_daily_lab
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from analysis.experiments.match_history_features import build_feature_rows, write_csv
from analysis.experiments.v30_v31_full_backtest import enrich
from analysis.gs1_over_lab import features, rule_grid, matches, label, wilson, rank


def evaluate(items, min_picks=1, max_picks=0, details=False):
    days=defaultdict(list)
    for r,f in items:
        days[r['MatchDate']].append((r,f))
    played=[]; selections=[]
    for day, group in sorted(days.items()):
        if len(group)<min_picks:
            continue
        if max_picks:
            group=sorted(group,key=rank)[:max_picks]
        ok=sum(int(r['Over25']) for r,_ in group)
        played.append({'MatchDate':day,'Picks':len(group),'OK':ok,'KO':len(group)-ok,
                       'AllOK':int(ok==len(group))})
        if details:
            for r,f in group:
                selections.append({'MatchDate':day,'LeagueId':r['LeagueId'],'Home':r['Home'],
                                   'Away':r['Away'],'HG':r['HG'],'AG':r['AG'],
                                   'Over25':r['Over25'],'MinOverRateFull':f['MinOverRateFull'],
                                   'MinGFFull':f['MinGFFull'],'MinGAFull':f['MinGAFull']})
    n=len(played); clean=sum(d['AllOK'] for d in played)
    picks=sum(d['Picks'] for d in played); ok=sum(d['OK'] for d in played)
    return {'DaysPlayed':n,'DaysAllOK':clean,'DaysKO':n-clean,
            'DailyAllOKPct':round(100*clean/n,2) if n else 0,
            'DailyWilsonLower95Pct':round(100*wilson(clean,n),2),
            'Picks':picks,'AvgPicks':round(picks/n,2) if n else 0,
            'MatchOK':ok,'MatchKO':picks-ok,
            'MatchAccuracyPct':round(100*ok/picks,2) if picks else 0},played,selections


def main():
    p=argparse.ArgumentParser(description='GS1: massimizza giornate con TUTTI gli Over 2.5 OK')
    p.add_argument('--results-dir',default='data/storico/risultati')
    p.add_argument('--out',default='data/analysis/gs1/over/daily_lab')
    p.add_argument('--train-end',default='2026-08-05')
    p.add_argument('--validation-end',default='2026-09-15')
    p.add_argument('--min-train-days',type=int,default=15)
    p.add_argument('--min-validation-days',type=int,default=10)
    p.add_argument('--top',type=int,default=20)
    args=p.parse_args()
    if args.train_end>=args.validation_end: p.error('train-end deve precedere validation-end')
    if args.min_train_days<1 or args.min_validation_days<1 or args.top<1: p.error('Soglie e top devono essere positivi')
    raw=build_feature_rows(Path(args.results_dir),min_history=5,windows=(5,7,8))
    if not raw: raise SystemExit('Nessuna partita storica valida')
    items=[(r,features(r)) for r in map(enrich,raw)]
    splits={
        'TRAIN':[x for x in items if x[0]['MatchDate']<=args.train_end],
        'VALIDATION':[x for x in items if args.train_end<x[0]['MatchDate']<=args.validation_end],
        'TEST':[x for x in items if x[0]['MatchDate']>args.validation_end],
    }
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    all_candidates=[]; audits=[]; daily=[]; selected=[]
    # min_picks e' un filtro giornaliero: 0 selezioni = giornata NON giocata.
    # max_picks=0 significa NESSUN LIMITE. Si provano anche varianti 1/2/3.
    modes=[(1,0),(2,0),(3,0),(1,1),(1,2),(1,3)]
    for scope in ('NO_AUSTRALIA','ALL'):
        scoped={name:[x for x in group if scope=='ALL' or not x[0]['LeagueId'].startswith('Australia_')]
                for name,group in splits.items()}
        pool=[]
        for rule in rule_grid():
            train_items=[x for x in scoped['TRAIN'] if matches(x[1],rule)]
            if len(train_items)<args.min_train_days: continue
            val_items=[x for x in scoped['VALIDATION'] if matches(x[1],rule)]
            if len(val_items)<args.min_validation_days: continue
            for min_picks,max_picks in modes:
                tr,_,_=evaluate(train_items,min_picks,max_picks)
                va,_,_=evaluate(val_items,min_picks,max_picks)
                if tr['DaysPlayed']<args.min_train_days or va['DaysPlayed']<args.min_validation_days:
                    continue
                row={'Scope':scope,'Rule':label(rule),'MinPicks':min_picks,
                     'MaxPicks':max_picks,'Mode':'UNLIMITED' if max_picks==0 else 'CAPPED',
                     **{'Train'+k:v for k,v in tr.items()},
                     **{'Validation'+k:v for k,v in va.items()}}
                pool.append((row,rule))
        # Conservative criterion: maximize weakest confidence lower bound between TRAIN and VALIDATION.
        pool.sort(key=lambda t:(-min(t[0]['TrainDailyWilsonLower95Pct'],
                                     t[0]['ValidationDailyWilsonLower95Pct']),
                                -t[0]['ValidationDailyAllOKPct'],
                                -t[0]['ValidationDaysPlayed'],
                                t[0]['Rule'],t[0]['MinPicks'],t[0]['MaxPicks']))
        all_candidates.extend(row for row,_ in pool)
        for row,rule in pool[:args.top]:
            test_items=[x for x in scoped['TEST'] if matches(x[1],rule)]
            result,days,picks=evaluate(test_items,row['MinPicks'],row['MaxPicks'],True)
            audit={**row,**{'Test'+k:v for k,v in result.items()}}
            audits.append(audit)
            identity={'Scope':scope,'Rule':row['Rule'],'MinPicks':row['MinPicks'],
                      'MaxPicks':row['MaxPicks']}
            daily.extend([{**identity,**d} for d in days])
            selected.extend([{**identity,**d} for d in picks])
    write_csv(out/'candidates_train_validation.csv',all_candidates)
    write_csv(out/'test_audit.csv',audits)
    write_csv(out/'test_daily.csv',daily)
    write_csv(out/'test_selected_matches.csv',selected)
    print('Feature rows:',len(items),'Candidate configurations:',len(all_candidates))
    print('Output:',out)
    for row in audits:
        if row['Scope']=='NO_AUSTRALIA':
            print(f"{row['Rule'][:56]:56} | min={row['MinPicks']} max={row['MaxPicks'] or 'ALL'} | "
                  f"TRAIN {row['TrainDaysAllOK']}/{row['TrainDaysPlayed']} | "
                  f"VAL {row['ValidationDaysAllOK']}/{row['ValidationDaysPlayed']} | "
                  f"TEST {row['TestDaysAllOK']}/{row['TestDaysPlayed']} "
                  f"({row['TestDailyAllOKPct']}%) | avg {row['TestAvgPicks']} picks")
    print('KPI PRINCIPALE: giornate con TUTTE le partite OK / giornate giocate.')
    print('TEST e\' audit esplorativo; per conferma serve validazione futura congelata.')

if __name__=='__main__':
    main()
