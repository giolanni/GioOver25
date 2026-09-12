from __future__ import annotations
import argparse, math
from pathlib import Path
from statistics import mean
from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUTPUT_DEFAULT = Path("analysis/experiments/output/goal_feature_backtest")
BASE_FEATURES = [
    "HomeGFFull","AwayGFFull","HomeGAFull","AwayGAFull","HomeOverRateFull","AwayOverRateFull","HomeBTTSRateFull","AwayBTTSRateFull",
    "HomeGFL5","AwayGFL5","HomeGAL5","AwayGAL5","HomeOverRateL5","AwayOverRateL5","HomeBTTSRateL5","AwayBTTSRateL5",
    "HomeGFL7","AwayGFL7","HomeGAL7","AwayGAL7","HomeBTTSRateL7","AwayBTTSRateL7",
    "HomeGFL8","AwayGFL8","HomeGAL8","AwayGAL8","HomeBTTSRateL8","AwayBTTSRateL8",
]

def point_biserial(rows, field):
    xs=[float(r[field]) for r in rows]; ys=[int(r["BTTS"]) for r in rows]
    if not xs or len(set(ys)) < 2: return 0.0
    mx,my=mean(xs),mean(ys)
    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    den=math.sqrt(sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))
    return num/den if den else 0.0

def btts_rate(rows):
    return sum(int(r["BTTS"]) for r in rows)/len(rows)*100 if rows else 0.0

def add_combined(rows):
    for r in rows:
        for suffix in ("Full","L5","L7","L8"):
            r[f"MinGF{suffix}"]=min(float(r[f"HomeGF{suffix}"]),float(r[f"AwayGF{suffix}"]))
            r[f"AvgGA{suffix}"]=mean([float(r[f"HomeGA{suffix}"]),float(r[f"AwayGA{suffix}"])])
            r[f"MinBTTSRate{suffix}"]=min(float(r[f"HomeBTTSRate{suffix}"]),float(r[f"AwayBTTSRate{suffix}"]))
            r[f"GoalBalance{suffix}"]=mean([
                float(r[f"HomeGF{suffix}"]),float(r[f"AwayGF{suffix}"]),
                float(r[f"HomeGA{suffix}"]),float(r[f"AwayGA{suffix}"])
            ])

def correlation_results(rows):
    features=list(BASE_FEATURES)
    for suffix in ("Full","L5","L7","L8"):
        features += [f"MinGF{suffix}",f"AvgGA{suffix}",f"MinBTTSRate{suffix}",f"GoalBalance{suffix}"]
    out=[]; baseline=btts_rate(rows)
    for field in features:
        values=sorted(float(r[field]) for r in rows)
        if not values: continue
        q50=values[len(values)//2]; q75=values[min(len(values)-1,int(len(values)*0.75))]
        for label,thr in (("median",q50),("q75",q75)):
            sel=[r for r in rows if float(r[field]) >= thr]
            if not sel: continue
            hit=btts_rate(sel)
            out.append({"Feature":field,"PointBiserial":round(point_biserial(rows,field),4),"Cut":label,
                        "Threshold":round(thr,4),"N":len(sel),"BTTS":sum(int(r["BTTS"]) for r in sel),
                        "BTTSRate":round(hit,2),"LiftVsBaseline":round(hit-baseline,2)})
    out.sort(key=lambda r:(-r["BTTSRate"],-r["N"]))
    return out

def rule_results(rows):
    baseline=btts_rate(rows); out=[]
    specs=[]
    for suffix in ("L5","L7","L8","Full"):
        for gf in (0.8,1.0,1.2,1.4,1.6):
            specs.append((f"{suffix}: both_GF>={gf}",lambda r,s=suffix,t=gf: float(r[f"HomeGF{s}"])>=t and float(r[f"AwayGF{s}"])>=t))
        for gf,ga in ((1.0,0.8),(1.2,0.8),(1.2,1.0),(1.4,1.0)):
            specs.append((f"{suffix}: both_GF>={gf} AND avg_GA>={ga}",lambda r,s=suffix,g=gf,a=ga: float(r[f"HomeGF{s}"])>=g and float(r[f"AwayGF{s}"])>=g and float(r[f"AvgGA{s}"])>=a))
        for br in (0.5,0.6,0.7):
            specs.append((f"{suffix}: min_BTTS_rate>={br}",lambda r,s=suffix,t=br: float(r[f"MinBTTSRate{s}"])>=t))
    for name,pred in specs:
        sel=[r for r in rows if pred(r)]
        if len(sel)<20: continue
        hit=btts_rate(sel); ok=sum(int(r["BTTS"]) for r in sel)
        out.append({"Rule":name,"N":len(sel),"BTTS":ok,"NO_GOAL":len(sel)-ok,"BTTSRate":round(hit,2),
                    "CoveragePct":round(len(sel)/len(rows)*100,2),"LiftVsBaseline":round(hit-baseline,2)})
    out.sort(key=lambda r:(-r["BTTSRate"],-r["N"]))
    return out

def main():
    parser=argparse.ArgumentParser(description="Esplora correlazioni e regole predittive per GOAL/BTTS.")
    parser.add_argument("--output-dir",default=str(OUTPUT_DEFAULT))
    parser.add_argument("--min-history",type=int,default=5)
    args=parser.parse_args()
    rows=build_feature_rows(min_history=args.min_history,windows=(5,7,8))
    if not rows: raise RuntimeError("Nessuna partita storica eleggibile.")
    add_combined(rows)
    corr=correlation_results(rows); rules=rule_results(rows)
    out=Path(args.output_dir)
    write_csv(out/"goal_feature_correlations.csv",corr)
    write_csv(out/"goal_rule_results.csv",rules)
    write_csv(out/"goal_dataset.csv",rows)
    base=btts_rate(rows)
    print(f"Partite eleggibili: {len(rows)} | GOAL baseline: {base:.2f}%")
    print("\nMigliori regole:")
    for r in rules[:15]: print(f"  {r['Rule']}: {r['BTTS']}/{r['N']} = {r['BTTSRate']}% | lift {r['LiftVsBaseline']:+.2f}")
    print("Output:",out)
if __name__=="__main__": main()
