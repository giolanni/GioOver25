from __future__ import annotations
import argparse
from datetime import date, timedelta
from itertools import combinations
from pathlib import Path
from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUT = Path('analysis/experiments/output/young_history_feature_analysis')
BANDS=((5,6,'5-6'),(7,8,'7-8'),(5,8,'5-8'))

def d(v):
    try:return date.fromisoformat(str(v).strip())
    except:return None

def enrich(r):
    for s in ('Full','L5','L7'):
        r[f'MinGF{s}']=min(float(r[f'HomeGF{s}']),float(r[f'AwayGF{s}']))
        r[f'AvgGA{s}']=(float(r[f'HomeGA{s}'])+float(r[f'AwayGA{s}']))/2
        r[f'AvgOver{s}']=(float(r[f'HomeOverRate{s}'])+float(r[f'AwayOverRate{s}']))/2
        r[f'MinOver{s}']=min(float(r[f'HomeOverRate{s}']),float(r[f'AwayOverRate{s}']))
        r[f'PPGGap{s}']=abs(float(r[f'HomePPG{s}'])-float(r[f'AwayPPG{s}']))
    for s in ('L5','L7'):
        r[f'DeltaOver{s}']=r[f'AvgOver{s}']-r['AvgOverFull']
        r[f'AbsDeltaOver{s}']=abs(r[f'DeltaOver{s}'])
        r[f'DeltaGF{s}']=((float(r[f'HomeGF{s}'])+float(r[f'AwayGF{s}']))/2)-((float(r['HomeGFFull'])+float(r['AwayGFFull']))/2)
    return r

def rate(rows):
    n=len(rows); ok=sum(int(r['Over25']) for r in rows)
    return ok,n,(100*ok/n if n else 0.0)

def catalog():
    out=[]
    def ge(name,t): out.append((f'{name}>={t}',lambda r,n=name,x=t:float(r[n])>=x))
    def le(name,t): out.append((f'{name}<={t}',lambda r,n=name,x=t:float(r[n])<=x))
    for s in ('Full','L5','L7'):
        for t in (1.2,1.4,1.6,1.8): ge(f'MinGF{s}',t)
        for t in (1.3,1.5,1.7,1.9): ge(f'AvgGA{s}',t)
        for t in (.5,.6,.7,.8): ge(f'AvgOver{s}',t)
        for t in (.4,.5,.6,.7): ge(f'MinOver{s}',t)
        for t in (.5,.8,1.0,1.2): le(f'PPGGap{s}',t)
    for s in ('L5','L7'):
        for t in (.05,.10,.15,.20): le(f'AbsDeltaOver{s}',t)
        for t in (0,.05,.10,.15): ge(f'DeltaOver{s}',t)
        for t in (0,.1,.2,.3): ge(f'DeltaGF{s}',t)
    return out

def discover(train,min_n,topn):
    base=rate(train); conds=catalog(); specs=[]
    specs += [((n,), (f,)) for n,f in conds]
    specs += [((a[0],b[0]),(a[1],b[1])) for a,b in combinations(conds,2)]
    cand=[]
    for names,funcs in specs:
        s=[r for r in train if all(f(r) for f in funcs)]
        if len(s)<min_n: continue
        ok,n,hit=rate(s)
        cand.append({'Rule':' AND '.join(names),'TrainOK':ok,'TrainN':n,'TrainHitRate':round(hit,2),'TrainLift':round(hit-base[2],2),'_funcs':funcs})
    cand.sort(key=lambda x:(x['TrainHitRate'],x['TrainN']),reverse=True)
    return cand[:topn],base

def main():
    p=argparse.ArgumentParser(); p.add_argument('--test-days',type=int,default=30); p.add_argument('--min-train-n',type=int,default=40); p.add_argument('--topn',type=int,default=20); p.add_argument('--output-dir',default=str(OUT)); a=p.parse_args()
    rows=[enrich(r) for r in build_feature_rows(min_history=5,windows=(5,7,8))]
    split=max(d(r['MatchDate']) for r in rows if d(r['MatchDate']))-timedelta(days=a.test_days-1)
    train_all=[r for r in rows if d(r['MatchDate'])<split]; test_all=[r for r in rows if d(r['MatchDate'])>=split]
    result=[]
    print(f'Split temporale: train < {split}; test >= {split}')
    for lo,hi,label in BANDS:
        train=[r for r in train_all if lo<=int(r['MinPlayedBefore'])<=hi]; test=[r for r in test_all if lo<=int(r['MinPlayedBefore'])<=hi]
        cand,tbase=discover(train,a.min_train_n,a.topn); xbase=rate(test)
        print(f'\n{label}: baseline train {tbase[0]}/{tbase[1]}={tbase[2]:.2f}% | test {xbase[0]}/{xbase[1]}={xbase[2]:.2f}%')
        shown=0
        for c in cand:
            s=[r for r in test if all(f(r) for f in c['_funcs'])]; ok,n,hit=rate(s)
            row={k:v for k,v in c.items() if not k.startswith('_')}; row.update({'Maturity':label,'TestOK':ok,'TestN':n,'TestHitRate':round(hit,2),'TestLift':round(hit-xbase[2],2) if n else 0.0}); result.append(row)
            if n>=10 and hit>=xbase[2] and c['TrainLift']>0 and shown<8:
                print(f"  {c['Rule']}: train {c['TrainOK']}/{c['TrainN']}={c['TrainHitRate']}% ({c['TrainLift']:+.2f}) | test {ok}/{n}={hit:.2f}% ({hit-xbase[2]:+.2f})")
                shown+=1
        if shown==0: print('  Nessuna regola stabile con almeno 10 eventi nel test.')
    out=Path(a.output_dir); write_csv(out/'young_history_rule_validation.csv',result); write_csv(out/'young_history_dataset.csv',rows); print('\nOutput:',out/'young_history_rule_validation.csv')
if __name__=='__main__': main()
