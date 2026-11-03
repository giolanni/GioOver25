"""GS1 OVER broad research: train/validation discovery, untouched test audit.

Run: python -m analysis.gs1_over_lab
Read-only: never changes engines or rankings. No outcome-derived ranking features.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from math import sqrt
from pathlib import Path
from analysis.experiments.match_history_features import build_feature_rows, write_csv
from analysis.experiments.v30_v31_full_backtest import enrich

def wilson(ok,n,z=1.96):
    if not n: return 0.0
    p=ok/n
    return (p+z*z/(2*n)-z*sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)

def features(r):
    f={}
    for s in ('Full','L5','L7','L8'):
        for name in ('GF','GA','OverRate','BTTSRate','Goals','PPG'):
            h=float(r['Home'+name+s]); a=float(r['Away'+name+s])
            f['Min'+name+s]=min(h,a)
            f['Avg'+name+s]=(h+a)/2
            if name=='PPG': f['GapPPG'+s]=abs(h-a)
        f['Cross'+s]=min((float(r['HomeGF'+s])+float(r['AwayGA'+s]))/2,
                          (float(r['AwayGF'+s])+float(r['HomeGA'+s]))/2)
    f['Maturity']=float(r['MinPlayedBefore'])
    f['DeltaGF']=float(r['DeltaGFL5'])
    f['DeltaOver']=f['MinOverRateL5']-f['MinOverRateFull']
    f['DeltaGA']=f['MinGAL5']-f['MinGAFull']
    f['V30']=float(r['V30'])
    f['V31Strong']=float(r['V31Level']=='STRONG')
    return f

def rule_grid():
    # A priori candidate thresholds; TEST never used to generate/select rules.
    specs={
        'MinGFL5':('>=',(1.2,1.6,1.8,2.0,2.2,2.5)),
        'MinGFFull':('>=',(1.2,1.4,1.6,1.8,2.0)),
        'MinGAL5':('>=',(1.0,1.2,1.4,1.6,1.8,2.0)),
        'MinGAFull':('>=',(1.0,1.2,1.4,1.6)),
        'MinOverRateL5':('>=',(.6,.8,1.0)),
        'MinOverRateFull':('>=',(.6,.7,.8)),
        'MinBTTSRateL5':('>=',(.6,.8,1.0)),
        'MinBTTSRateFull':('>=',(.6,.7,.8)),
        'AvgGoalsL5':('>=',(2.8,3.2,3.6,4.0)),
        'CrossL5':('>=',(1.4,1.6,1.8,2.0)),
        'GapPPGFull':('<=',(.5,.75,1.0)),
        'Maturity':('>=',(5,7,10,15,20)),
        'DeltaGF':('>=',(0,.2,.4,.6)),
        'DeltaOver':('>=',(0,.2)),
        'DeltaGA':('>=',(0,.2,.4)),
        'V30':('>=',(1,)),
        'V31Strong':('>=',(1,)),
    }
    atoms=[(name,op,t) for name,(op,thresholds) in specs.items() for t in thresholds]
    rules=[(a,) for a in atoms]
    rules += [(a,b) for i,a in enumerate(atoms) for b in atoms[i+1:] if a[0]!=b[0]]
    return rules

def matches(f,rule):
    return all((f[name]>=v if op=='>=' else f[name]<=v) for name,op,v in rule)

def label(rule):
    return ' & '.join('%s%s%s'%atom for atom in rule)

def rank(item):
    r,f=item
    return (-f['MinOverRateL5'],-f['MinGFL5'],-f['MinGAL5'],r['LeagueId'],r['Home'],r['Away'])

def evaluate(items,limit):
    days=defaultdict(list)
    for item in items: days[item[0]['MatchDate']].append(item)
    chosen=[]; daily=[]
    for d,group in sorted(days.items()):
        picks=sorted(group,key=rank)[:limit]
        chosen.extend(picks)
        ok=sum(int(r['Over25']) for r,_ in picks)
        daily.append((d,len(picks),ok,len(picks)-ok))
    n=len(chosen); ok=sum(int(r['Over25']) for r,_ in chosen)
    clean=sum(ko==0 for _,_,_,ko in daily)
    return {'OK':ok,'KO':n-ok,'Total':n,'AccuracyPct':round(100*ok/n,2) if n else 0,
            'WilsonLower95Pct':round(100*wilson(ok,n),2),
            'DaysWithPicks':len(daily),'CleanDays':clean,
            'CleanDaysPct':round(100*clean/len(daily),2) if daily else 0},chosen,daily

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--results-dir',default='data/storico/risultati')
    ap.add_argument('--out',default='data/analysis/gs1/over/lab')
    ap.add_argument('--train-end',default='2026-08-05')
    ap.add_argument('--validation-end',default='2026-09-15')
    ap.add_argument('--min-train',type=int,default=40)
    ap.add_argument('--min-validation',type=int,default=15)
    ap.add_argument('--top',type=int,default=20)
    args=ap.parse_args()
    if args.train_end>=args.validation_end: ap.error('Date split non valide')
    raw=build_feature_rows(Path(args.results_dir),min_history=5,windows=(5,7,8))
    if not raw: raise SystemExit('Nessun risultato valido')
    items=[(r,features(r)) for r in map(enrich,raw)]
    splits={'TRAIN':[x for x in items if x[0]['MatchDate']<=args.train_end],
            'VALIDATION':[x for x in items if args.train_end<x[0]['MatchDate']<=args.validation_end],
            'TEST':[x for x in items if x[0]['MatchDate']>args.validation_end]}
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    candidates=[]
    for scope in ('ALL','NO_AUSTRALIA'):
        data={k:[x for x in v if scope=='ALL' or not x[0]['LeagueId'].startswith('Australia_')] for k,v in splits.items()}
        for rule in rule_grid():
            tr=[x for x in data['TRAIN'] if matches(x[1],rule)]
            if len(tr)<args.min_train: continue
            va=[x for x in data['VALIDATION'] if matches(x[1],rule)]
            if len(va)<args.min_validation: continue
            for limit in (1,2,3):
                train,_,_=evaluate(tr,limit); validation,_,_=evaluate(va,limit)
                candidates.append({'Scope':scope,'Rule':label(rule),'MaxPicks':limit,
                                   **{'Train'+k:v for k,v in train.items()},
                                   **{'Validation'+k:v for k,v in validation.items()},
                                   '_rule':rule})
    # Select ONLY from TRAIN and VALIDATION; TEST is an untouched final audit.
    candidates.sort(key=lambda r:(-min(r['TrainWilsonLower95Pct'],r['ValidationWilsonLower95Pct']),
                                  -r['ValidationWilsonLower95Pct'],-r['ValidationTotal'],r['Rule']))
    winners=[]; selected=[]; daily_rows=[]
    for scope in ('ALL','NO_AUSTRALIA'):
        ranked=[r for r in candidates if r['Scope']==scope][:args.top]
        for c in ranked:
            rule=c.pop('_rule')
            test_items=[x for x in splits['TEST'] if (scope=='ALL' or not x[0]['LeagueId'].startswith('Australia_')) and matches(x[1],rule)]
            test,picks,days=evaluate(test_items,c['MaxPicks'])
            winners.append({**c,**{'Test'+k:v for k,v in test.items()}})
            for r,f in picks:
                selected.append({'Scope':scope,'Rule':c['Rule'],'MaxPicks':c['MaxPicks'],
                                 'MatchDate':r['MatchDate'],'LeagueId':r['LeagueId'],
                                 'Home':r['Home'],'Away':r['Away'],'HG':r['HG'],'AG':r['AG'],
                                 'Over25':r['Over25'],'MinOverRateL5':f['MinOverRateL5'],
                                 'MinGFL5':f['MinGFL5'],'MinGAL5':f['MinGAL5']})
            for d,n,ok,ko in days:
                daily_rows.append({'Scope':scope,'Rule':c['Rule'],'MaxPicks':c['MaxPicks'],
                                   'MatchDate':d,'Picks':n,'OK':ok,'KO':ko,'AllOK':int(ko==0)})
    write_csv(out/'candidates_train_validation.csv',[{k:v for k,v in r.items() if k!='_rule'} for r in candidates])
    write_csv(out/'test_audit.csv',winners)
    write_csv(out/'test_selected_matches.csv',selected)
    write_csv(out/'test_daily.csv',daily_rows)
    print('Feature rows:',len(items),'Candidate configurations:',len(candidates))
    print('Output:',out)
    for c in winners:
        if c['Scope']=='NO_AUSTRALIA':
            print(f"{c['Rule'][:64]:64} | {c['MaxPicks']} picks | TRAIN {c['TrainOK']}/{c['TrainTotal']} | VAL {c['ValidationOK']}/{c['ValidationTotal']} | TEST {c['TestOK']}/{c['TestTotal']} ({c['TestAccuracyPct']}%) | clean {c['TestCleanDays']}/{c['TestDaysWithPicks']}")
    print('ATTENZIONE: TEST audit esplorativo; non ottimizzare nuove soglie sui risultati TEST.')

if __name__=='__main__': main()
