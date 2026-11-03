"""GS1 OVER discovery, read-only. Run: python -m analysis.gs1_over_discovery
Requires analysis.experiments.match_history_features and v30_v31_full_backtest.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from pathlib import Path
from math import sqrt
from analysis.experiments.match_history_features import build_feature_rows, write_csv
from analysis.experiments.v30_v31_full_backtest import enrich

RULES = {
    'V30': lambda r: bool(r['V30']),
    'V31_STRONG': lambda r: r['V31Level'] == 'STRONG',
    'V31_STRONG_MIN_GA_12': lambda r: r['V31Level'] == 'STRONG' and min(float(r['HomeGAL5']), float(r['AwayGAL5'])) >= 1.2,
    'V31_STRONG_MIN_OVER_80': lambda r: r['V31Level'] == 'STRONG' and float(r['MinOverL5']) >= .8,
    'V30_MIN_GA_12': lambda r: bool(r['V30']) and min(float(r['HomeGAL5']), float(r['AwayGAL5'])) >= 1.2,
}

def wilson_lower(ok, n, z=1.96):
    if not n: return 0.0
    p=ok/n; d=1+z*z/n
    return (p+z*z/(2*n)-z*sqrt((p*(1-p)+z*z/(4*n))/n))/d

def rank(r):
    # Deterministic, outcome-free priority; never use HG/AG/Over25 here.
    return (-float(r['MinOverL5']), -float(r['DeltaGFL5']), -float(r['MinGFFull']), r['LeagueId'], r['Home'], r['Away'])

def assess(rows, rule, scope, split, max_picks):
    candidates = [r for r in rows if RULES[rule](r)]
    days = defaultdict(list)
    for r in candidates: days[r['MatchDate']].append(r)
    picked=[]; day_rows=[]
    for day in sorted(days):
        selection=sorted(days[day], key=rank)[:max_picks]
        picked.extend(selection)
        day_rows.append({'Rule':rule,'Scope':scope,'Split':split,'MaxPicks':max_picks,
                         'MatchDate':day,'Picks':len(selection),
                         'AllOK':int(all(int(r['Over25']) for r in selection)),
                         'OK':sum(int(r['Over25']) for r in selection),
                         'KO':sum(1-int(r['Over25']) for r in selection)})
    n=len(picked); ok=sum(int(r['Over25']) for r in picked)
    clean=sum(d['AllOK'] for d in day_rows)
    return ({'Rule':rule,'Scope':scope,'Split':split,'MaxPicks':max_picks,
             'OK':ok,'KO':n-ok,'Total':n,'AccuracyPct':round(100*ok/n,2) if n else 0,
             'WilsonLower95Pct':round(100*wilson_lower(ok,n),2),
             'DaysWithPicks':len(day_rows),'CleanDays':clean,
             'CleanDaysPct':round(100*clean/len(day_rows),2) if day_rows else 0},
            day_rows,
            [{'Rule':rule,'Scope':scope,'Split':split,'MaxPicks':max_picks,
              'MatchDate':r['MatchDate'],'LeagueId':r['LeagueId'],'Home':r['Home'],
              'Away':r['Away'],'Over25':r['Over25'],'HG':r['HG'],'AG':r['AG'],
              'MinOverL5':r['MinOverL5'],'DeltaGFL5':r['DeltaGFL5']} for r in picked])

def main():
    p=argparse.ArgumentParser(description='GS1 OVER: benchmark cronologico senza modificare engine')
    p.add_argument('--results-dir',default='data/storico/risultati')
    p.add_argument('--out',default='data/analysis/gs1/over/discovery')
    p.add_argument('--train-end',default='2026-08-05')
    p.add_argument('--validation-end',default='2026-09-15')
    a=p.parse_args()
    if a.train_end >= a.validation_end: p.error('train-end deve precedere validation-end')
    rows=[enrich(r) for r in build_feature_rows(results_dir=Path(a.results_dir),min_history=5,windows=(5,7,8))]
    if not rows: raise SystemExit('Nessun risultato storico valido: verificare --results-dir')
    summary=[]; daily=[]; selections=[]
    for split, subset in [('TRAIN',[r for r in rows if r['MatchDate']<=a.train_end]),
                          ('VALIDATION',[r for r in rows if a.train_end<r['MatchDate']<=a.validation_end]),
                          ('TEST',[r for r in rows if r['MatchDate']>a.validation_end])]:
        for scope, scoped in [('ALL',subset),('NO_AUSTRALIA',[r for r in subset if not r['LeagueId'].startswith('Australia_')])]:
            for rule in RULES:
                for picks in (1,2,3):
                    stat,days,matches=assess(scoped,rule,scope,split,picks)
                    summary.append(stat);daily.extend(days);selections.extend(matches)
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    write_csv(out/'summary.csv',summary)
    write_csv(out/'daily.csv',daily)
    write_csv(out/'selected_matches.csv',selections)
    print('Feature rows:',len(rows),' | Output:',out)
    for r in sorted((r for r in summary if r['Split']=='TEST' and r['Scope']=='NO_AUSTRALIA' and r['MaxPicks']==3),key=lambda x:(-x['WilsonLower95Pct'],-x['AccuracyPct'])):
        print(f"{r['Rule']:<27} {r['OK']:>3} OK / {r['KO']:>3} KO | {r['AccuracyPct']:>6.2f}% | giornate 100%: {r['CleanDays']}/{r['DaysWithPicks']} | Wilson95: {r['WilsonLower95Pct']:.2f}%")
    print('NOTA: regole esplorative; non usare il TEST per scegliere nuove soglie e poi dichiararlo indipendente.')

if __name__=='__main__': main()
