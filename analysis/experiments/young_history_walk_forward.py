from __future__ import annotations
import argparse
from collections import defaultdict
from datetime import date
from pathlib import Path
from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUT=Path('analysis/experiments/output/young_history_walk_forward')
RULES=(
 ('GF14_GA19',lambda r:r['MinGFFull']>=1.4 and r['AvgGAFull']>=1.9),
 ('GF16_GA19',lambda r:r['MinGFFull']>=1.6 and r['AvgGAFull']>=1.9),
 ('L5OVER70_DGF20',lambda r:r['MinOverL5']>=.7 and r['DeltaGFL5']>=.2),
 ('L5OVER70_DGF30',lambda r:r['MinOverL5']>=.7 and r['DeltaGFL5']>=.3),
 ('L7OVER70_DGF30',lambda r:r['AvgOverL7']>=.7 and r['DeltaGFL5']>=.3),
)
BANDS=((5,6,'5-6'),(7,8,'7-8'),(5,8,'5-8'))

def dt(v): return date.fromisoformat(str(v).strip())
def enrich(r):
 for s in ('Full','L5','L7'):
  r[f'MinGF{s}']=min(float(r[f'HomeGF{s}']),float(r[f'AwayGF{s}']))
  r[f'AvgGA{s}']=(float(r[f'HomeGA{s}'])+float(r[f'AwayGA{s}']))/2
  r[f'AvgOver{s}']=(float(r[f'HomeOverRate{s}'])+float(r[f'AwayOverRate{s}']))/2
  r[f'MinOver{s}']=min(float(r[f'HomeOverRate{s}']),float(r[f'AwayOverRate{s}']))
 r['DeltaGFL5']=((float(r['HomeGFL5'])+float(r['AwayGFL5']))/2)-((float(r['HomeGFFull'])+float(r['AwayGFFull']))/2)
 return r

def stats(rows):
 n=len(rows); ok=sum(int(r['Over25']) for r in rows)
 return ok,n,100*ok/n if n else 0.0

def main():
 p=argparse.ArgumentParser();p.add_argument('--output-dir',default=str(OUT));a=p.parse_args()
 rows=[enrich(r) for r in build_feature_rows(min_history=5,windows=(5,7,8))]
 months=sorted({dt(r['MatchDate']).strftime('%Y-%m') for r in rows})
 out=[]; totals=defaultdict(lambda:[0,0])
 print('Walk-forward mensile: regole fissate, nessuna riottimizzazione per mese.')
 for lo,hi,band in BANDS:
  print(f'\n{band}')
  for name,rule in RULES:
   parts=[]
   for month in months:
    base=[r for r in rows if lo<=int(r['MinPlayedBefore'])<=hi and dt(r['MatchDate']).strftime('%Y-%m')==month]
    selected=[r for r in base if rule(r)]
    ok,n,hit=stats(selected); bok,bn,bhit=stats(base)
    if not n: continue
    lift=hit-bhit
    out.append({'Maturity':band,'Rule':name,'Month':month,'OK':ok,'N':n,'HitRate':round(hit,2),'Baseline':round(bhit,2),'Lift':round(lift,2)})
    totals[(band,name)][0]+=ok;totals[(band,name)][1]+=n
    parts.append(f'{month} {ok}/{n}={hit:.1f}%({lift:+.1f})')
   if parts: print(' ',name,':',' | '.join(parts))
 print('\nTOTALI')
 summary=[]
 for (band,name),(ok,n) in sorted(totals.items()):
  hit=100*ok/n if n else 0
  monthly=[x for x in out if x['Maturity']==band and x['Rule']==name]
  positive=sum(1 for x in monthly if x['Lift']>0); negative=sum(1 for x in monthly if x['Lift']<0)
  summary.append({'Maturity':band,'Rule':name,'OK':ok,'N':n,'HitRate':round(hit,2),'PositiveMonths':positive,'NegativeMonths':negative,'Months':len(monthly)})
  print(f'  {band} {name}: {ok}/{n}={hit:.2f}% | mesi + {positive}/{len(monthly)}, mesi - {negative}/{len(monthly)}')
 outdir=Path(a.output_dir);write_csv(outdir/'monthly_validation.csv',out);write_csv(outdir/'summary.csv',summary)
 print('\nOutput:',outdir/'summary.csv')
if __name__=='__main__':main()
