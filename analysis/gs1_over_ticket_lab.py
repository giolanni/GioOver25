"""GS1 OVER: separate daily all-OK leaderboards by ticket size.

Selection of winning rules uses TRAIN and VALIDATION ONLY.
TEST is audited after selection; never rank candidates using TEST.
Run: python -m analysis.gs1_over_ticket_lab
"""
from __future__ import annotations

import argparse
from pathlib import Path

from analysis.experiments.match_history_features import build_feature_rows, write_csv
from analysis.experiments.v30_v31_full_backtest import enrich
from analysis.gs1_over_lab import features, rule_grid, matches, label
from analysis.gs1_over_daily_lab import evaluate

# Exact-size modes require enough eligible matches; only the best N are chosen.
# 4PLUS and VARIABLE are uncapped: all eligible matches are selected.
MODES = (
    ('SINGLE',1,1),
    ('DOUBLE',2,2),
    ('TRIPLE',3,3),
    ('FOUR_PLUS',4,0),
    ('VARIABLE',1,0),
)


def score(row):
    # Conservative selection: best worst-period 95% lower bound.
    return (min(row['TrainDailyWilsonLower95Pct'],row['ValidationDailyWilsonLower95Pct']),
            row['ValidationDailyWilsonLower95Pct'],
            row['ValidationDaysPlayed'],
            row['TrainDaysPlayed'])


def main():
    p=argparse.ArgumentParser(description='GS1 OVER: daily all-OK by 1/2/3/4+/variable tickets')
    p.add_argument('--results-dir',default='data/storico/risultati')
    p.add_argument('--out',default='data/analysis/gs1/over/ticket_lab')
    p.add_argument('--train-end',default='2026-08-05')
    p.add_argument('--validation-end',default='2026-09-15')
    p.add_argument('--min-train-days',type=int,default=15)
    p.add_argument('--min-validation-days',type=int,default=10)
    p.add_argument('--top-per-category',type=int,default=10)
    args=p.parse_args()
    if args.train_end>=args.validation_end: p.error('Date di split non valide')
    if min(args.min_train_days,args.min_validation_days,args.top_per_category)<1: p.error('Valori minimi devono essere positivi')
    raw=build_feature_rows(Path(args.results_dir),min_history=5,windows=(5,7,8))
    if not raw: raise SystemExit('Nessuna partita valida')
    items=[(r,features(r)) for r in map(enrich,raw)]
    splits={'TRAIN':[x for x in items if x[0]['MatchDate']<=args.train_end],
            'VALIDATION':[x for x in items if args.train_end<x[0]['MatchDate']<=args.validation_end],
            'TEST':[x for x in items if x[0]['MatchDate']>args.validation_end]}
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    candidate_rows=[]; audit_rows=[]; day_rows=[]; match_rows=[]
    for scope in ('NO_AUSTRALIA','ALL'):
        scoped={k:[x for x in v if scope=='ALL' or not x[0]['LeagueId'].startswith('Australia_')]
                for k,v in splits.items()}
        buckets={mode[0]:[] for mode in MODES}
        for rule in rule_grid():
            tr=[x for x in scoped['TRAIN'] if matches(x[1],rule)]
            if len(tr)<args.min_train_days: continue
            va=[x for x in scoped['VALIDATION'] if matches(x[1],rule)]
            if len(va)<args.min_validation_days: continue
            for category,minimum,maximum in MODES:
                train,_,_=evaluate(tr,minimum,maximum)
                if train['DaysPlayed']<args.min_train_days: continue
                validation,_,_=evaluate(va,minimum,maximum)
                if validation['DaysPlayed']<args.min_validation_days: continue
                row={'Scope':scope,'Category':category,'Rule':label(rule),
                     'MinPicks':minimum,'MaxPicks':maximum,
                     **{'Train'+k:v for k,v in train.items()},
                     **{'Validation'+k:v for k,v in validation.items()}}
                buckets[category].append((row,rule))
        for category,_,_ in MODES:
            ranked=sorted(buckets[category],key=lambda x:(tuple(-v for v in score(x[0])),x[0]['Rule']))
            candidate_rows.extend(row for row,_ in ranked)
            for position,(row,rule) in enumerate(ranked[:args.top_per_category],1):
                test_matches=[x for x in scoped['TEST'] if matches(x[1],rule)]
                test,days,picks=evaluate(test_matches,row['MinPicks'],row['MaxPicks'],True)
                identity={'Scope':scope,'Category':category,'Rank':position,'Rule':row['Rule'],
                          'MinPicks':row['MinPicks'],'MaxPicks':row['MaxPicks']}
                audit_rows.append({**identity,**row,**{'Test'+k:v for k,v in test.items()}})
                day_rows.extend([{**identity,**d} for d in days])
                match_rows.extend([{**identity,**m} for m in picks])
    write_csv(out/'train_validation_leaderboards.csv',candidate_rows)
    write_csv(out/'test_audit.csv',audit_rows)
    write_csv(out/'test_daily.csv',day_rows)
    write_csv(out/'test_selected_matches.csv',match_rows)
    print('Feature rows:',len(items),'Candidate configurations:',len(candidate_rows))
    print('Output:',out)
    for category,_,_ in MODES:
        print('\n'+category+' (NO_AUSTRALIA; ranked ONLY by TRAIN/VALIDATION)')
        for r in [x for x in audit_rows if x['Scope']=='NO_AUSTRALIA' and x['Category']==category][:args.top_per_category]:
            print(f"#{r['Rank']:2} {r['Rule'][:53]:53} | TRAIN {r['TrainDaysAllOK']}/{r['TrainDaysPlayed']} "
                  f"VAL {r['ValidationDaysAllOK']}/{r['ValidationDaysPlayed']} "
                  f"TEST {r['TestDaysAllOK']}/{r['TestDaysPlayed']} ({r['TestDailyAllOKPct']}%) "
                  f"avg {r['TestAvgPicks']}")
    print('\nKPI = giornate con TUTTE le selezioni Over 2.5 / giornate giocate.')
    print('ATTENZIONE: test esplorativo; serve validazione prospettica per conferma.')


if __name__=='__main__':
    main()
