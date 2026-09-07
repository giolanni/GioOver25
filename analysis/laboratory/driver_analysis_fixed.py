"""Robust driver analysis: missing values are handled per driver, not per match."""
from __future__ import annotations

import csv
import math
from itertools import combinations
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Callable

from .recent_form_drivers import RECENT_FORM_DRIVERS

INPUT_FILE = Path("analysis/laboratory/data/01_matches.csv")
OUTPUT_DIR = Path("analysis/laboratory/data")
DRIVERS = [
    "RankingGapScore", "HomeAttackScore", "AwayAttackScore",
    "HomeDefenseWeaknessScore", "AwayDefenseWeaknessScore",
    "HomeLast10OverScore", "AwayLast10OverScore",
    "HomeVenueOverScore", "AwayVenueOverScore", "BTTSProfileScore",
    *RECENT_FORM_DRIVERS,
]
GROUPS = ["ALTA_OK", "ALTA_KO", "MEDIA_OK", "MEDIA_KO"]
MIN_PAIR_OCCURRENCES = 15
MIN_TRIPLE_OCCURRENCES = 12
MAX_SINGLE_RULES_FOR_TRIPLES = 18


def _text(v: Any) -> str:
    return str(v or "").strip()


def _float(v: Any) -> float | None:
    s = _text(v).replace(",", ".")
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _group(row: dict) -> str:
    return f"{_text(row.get('Band')).upper()}_{_text(row.get('Outcome')).upper()}"


def _load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Dataset Laboratory non trovato: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fields = set(reader.fieldnames or [])
        missing = {"Band", "Outcome"}.difference(fields)
        if missing:
            raise ValueError("Colonne mancanti in 01_matches.csv: " + ", ".join(sorted(missing)))
        rows = []
        for raw in reader:
            group = _group(raw)
            if group not in GROUPS:
                continue
            row = dict(raw)
            row["_Group"] = group
            # IMPORTANT: a missing driver does not invalidate the match.
            # Each analysis uses only rows where its own driver is available.
            for driver in DRIVERS:
                row[driver] = _float(raw.get(driver))
            rows.append(row)
    return rows


def _valid(rows: list[dict], driver: str) -> list[dict]:
    return [r for r in rows if r.get(driver) is not None]


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    a = sorted(values)
    if len(a) == 1:
        return a[0]
    p = (len(a) - 1) * q
    lo, hi = math.floor(p), math.ceil(p)
    if lo == hi:
        return a[lo]
    return a[lo] * (hi - p) + a[hi] * (p - lo)


def _auc(pos: list[float], neg: list[float]) -> float | None:
    if not pos or not neg:
        return None
    wins = sum(1.0 if x > y else 0.5 if x == y else 0.0 for x in pos for y in neg)
    return wins / (len(pos) * len(neg))


def _cohen_d(a: list[float], b: list[float]) -> float | None:
    if len(a) < 2 or len(b) < 2:
        return None
    va, vb = pstdev(a) ** 2, pstdev(b) ** 2
    pooled = ((len(a)-1)*va + (len(b)-1)*vb) / (len(a)+len(b)-2)
    return 0.0 if pooled <= 0 else (mean(a)-mean(b)) / math.sqrt(pooled)


def _safe_round(v: float | None, n: int = 6):
    return "" if v is None else round(v, n)


def build_driver_power(rows: list[dict]) -> list[dict]:
    out = []
    for d in DRIVERS:
        rr = _valid(rows, d)
        vals = {g: [r[d] for r in rr if r["_Group"] == g] for g in GROUPS}
        aa, ma = _auc(vals["ALTA_OK"], vals["ALTA_KO"]), _auc(vals["MEDIA_OK"], vals["MEDIA_KO"])
        ae, me = _cohen_d(vals["ALTA_OK"], vals["ALTA_KO"]), _cohen_d(vals["MEDIA_OK"], vals["MEDIA_KO"])
        row = {"Driver": d}
        for g in GROUPS:
            v = vals[g]
            row[f"{g}_Count"] = len(v)
            row[f"{g}_Mean"] = _safe_round(mean(v)) if v else ""
            row[f"{g}_Median"] = _safe_round(median(v)) if v else ""
            row[f"{g}_StdDev"] = _safe_round(pstdev(v)) if len(v) > 1 else 0.0
        row["AltaDeltaMean"] = _safe_round((mean(vals["ALTA_OK"])-mean(vals["ALTA_KO"])) if vals["ALTA_OK"] and vals["ALTA_KO"] else None)
        row["MediaDeltaMean"] = _safe_round((mean(vals["MEDIA_OK"])-mean(vals["MEDIA_KO"])) if vals["MEDIA_OK"] and vals["MEDIA_KO"] else None)
        row.update({"AltaAUC": _safe_round(aa), "MediaAUC": _safe_round(ma), "AltaEffectSize": _safe_round(ae), "MediaEffectSize": _safe_round(me)})
        row["AltaDirection"] = "HIGHER_IS_BETTER" if aa is not None and aa >= .5 else "LOWER_IS_BETTER" if aa is not None else ""
        row["MediaDirection"] = "HIGHER_IS_BETTER" if ma is not None and ma >= .5 else "LOWER_IS_BETTER" if ma is not None else ""
        row["AltaPower"] = _safe_round(abs(aa-.5)*2) if aa is not None else ""
        row["MediaPower"] = _safe_round(abs(ma-.5)*2) if ma is not None else ""
        out.append(row)
    out.sort(key=lambda x: (-max(float(x["AltaPower"] or 0), float(x["MediaPower"] or 0)), x["Driver"]))
    return out


def build_driver_curves(rows: list[dict]) -> list[dict]:
    out = []
    for d in DRIVERS:
        rr = _valid(rows, d)
        values = [r[d] for r in rr]
        if not values:
            continue
        edges = sorted(set(round(_percentile(values, i/10), 6) for i in range(11)))
        if len(edges) == 1:
            edges = [edges[0], edges[0]]
        for band in ("ALTA", "MEDIA"):
            br = [r for r in rr if r["_Group"].startswith(band + "_")]
            for i in range(len(edges)-1):
                lo, hi = edges[i], edges[i+1]
                selected = [r for r in br if lo <= r[d] <= hi if i == len(edges)-2 or r[d] < hi]
                ok = sum(r["_Group"] == band + "_OK" for r in selected)
                ko = sum(r["_Group"] == band + "_KO" for r in selected)
                total = ok + ko
                out.append({"Driver":d,"Band":band,"BinIndex":i+1,"BinMin":lo,"BinMax":hi,"OK":ok,"KO":ko,"Total":total,"HitRate":round(ok/total,6) if total else ""})
    return out


def _rule_text(r: dict) -> str:
    return f"{r['Driver']}{r['Operator']}{r['Threshold']}"


def _rule_matches(row: dict, rule: dict) -> bool:
    v = row.get(rule["Driver"])
    if v is None:
        return False
    return v <= rule["Threshold"] if rule["Operator"] == "<=" else v >= rule["Threshold"]


def _evaluate(rows: list[dict], predicate: Callable[[dict], bool]) -> dict:
    c = {g: 0 for g in GROUPS}
    for r in rows:
        if predicate(r):
            c[r["_Group"]] += 1
    at, mt = c["ALTA_OK"]+c["ALTA_KO"], c["MEDIA_OK"]+c["MEDIA_KO"]
    return {**c,"AltaTotal":at,"AltaHitRate":c["ALTA_OK"]/at if at else None,"MediaTotal":mt,"MediaHitRate":c["MEDIA_OK"]/mt if mt else None}


def _single_rules(rows: list[dict]) -> list[dict]:
    rules=[]
    for d in DRIVERS:
        vals=[r[d] for r in rows if r.get(d) is not None]
        if not vals: continue
        for q in (.2,.3,.4,.5,.6,.7,.8):
            t=round(_percentile(vals,q),6)
            for op in ("<=", ">="):
                rules.append({"Driver":d,"Operator":op,"Threshold":t})
    return rules


def build_driver_pairs(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    rules=_single_rules(rows)
    scored=[]
    for rule in rules:
        result=_evaluate([r for r in rows if r.get(rule["Driver"]) is not None],lambda r,rule=rule:_rule_matches(r,rule))
        ah=result["AltaHitRate"] if result["AltaTotal"]>=MIN_PAIR_OCCURRENCES else None
        mh=result["MediaHitRate"] if result["MediaTotal"]>=MIN_PAIR_OCCURRENCES else None
        scored.append({**rule,**result,"Score":max(ah or 0,mh or 0)})
    out=[]
    for a,b in combinations(rules,2):
        if a["Driver"]==b["Driver"]: continue
        rr=[r for r in rows if r.get(a["Driver"]) is not None and r.get(b["Driver"]) is not None]
        res=_evaluate(rr,lambda r,a=a,b=b:_rule_matches(r,a) and _rule_matches(r,b))
        if res["AltaTotal"]<MIN_PAIR_OCCURRENCES and res["MediaTotal"]<MIN_PAIR_OCCURRENCES: continue
        out.append({"Rule1":_rule_text(a),"Rule2":_rule_text(b),**{g:res[g] for g in GROUPS},"AltaTotal":res["AltaTotal"],"AltaHitRate":_safe_round(res["AltaHitRate"]),"MediaTotal":res["MediaTotal"],"MediaHitRate":_safe_round(res["MediaHitRate"]),"PrimaryUse":"REDUCE_ALTA_KO" if (res["AltaHitRate"] is not None and (res["MediaHitRate"] is None or res["AltaHitRate"]>=res["MediaHitRate"])) else "PROMOTE_MEDIA_OK"})
    out.sort(key=lambda x:(-max(float(x["AltaHitRate"] or 0),float(x["MediaHitRate"] or 0)),-max(x["AltaTotal"],x["MediaTotal"])))
    scored.sort(key=lambda x:(-x["Score"],-max(x["AltaTotal"],x["MediaTotal"])))
    return out,scored


def build_driver_triples(rows: list[dict], single_scores: list[dict]) -> list[dict]:
    rules=[{"Driver":x["Driver"],"Operator":x["Operator"],"Threshold":x["Threshold"]} for x in single_scores[:MAX_SINGLE_RULES_FOR_TRIPLES]]
    out=[]
    for a,b,c in combinations(rules,3):
        if len({a["Driver"],b["Driver"],c["Driver"]})<3: continue
        rr=[r for r in rows if all(r.get(x["Driver"]) is not None for x in (a,b,c))]
        res=_evaluate(rr,lambda r,a=a,b=b,c=c:_rule_matches(r,a) and _rule_matches(r,b) and _rule_matches(r,c))
        if res["AltaTotal"]<MIN_TRIPLE_OCCURRENCES and res["MediaTotal"]<MIN_TRIPLE_OCCURRENCES: continue
        out.append({"Rule1":_rule_text(a),"Rule2":_rule_text(b),"Rule3":_rule_text(c),**{g:res[g] for g in GROUPS},"AltaTotal":res["AltaTotal"],"AltaHitRate":_safe_round(res["AltaHitRate"]),"MediaTotal":res["MediaTotal"],"MediaHitRate":_safe_round(res["MediaHitRate"]),"PrimaryUse":"REDUCE_ALTA_KO" if (res["AltaHitRate"] is not None and (res["MediaHitRate"] is None or res["AltaHitRate"]>=res["MediaHitRate"])) else "PROMOTE_MEDIA_OK"})
    out.sort(key=lambda x:(-max(float(x["AltaHitRate"] or 0),float(x["MediaHitRate"] or 0)),-max(x["AltaTotal"],x["MediaTotal"])))
    return out


def _pearson(a:list[float],b:list[float])->float|None:
    if len(a)<2 or len(a)!=len(b): return None
    ma,mb=mean(a),mean(b)
    da=sum((x-ma)**2 for x in a); db=sum((y-mb)**2 for y in b)
    den=math.sqrt(da*db)
    return sum((x-ma)*(y-mb) for x,y in zip(a,b))/den if den else 0.0


def build_correlation(rows:list[dict])->list[dict]:
    out=[]
    for a,b in combinations(DRIVERS,2):
        rr=[r for r in rows if r.get(a) is not None and r.get(b) is not None]
        c=_pearson([r[a] for r in rr],[r[b] for r in rr])
        out.append({"Driver1":a,"Driver2":b,"Count":len(rr),"Correlation":_safe_round(c),"AbsoluteCorrelation":_safe_round(abs(c) if c is not None else None),"RedundancyLevel":"HIGH" if c is not None and abs(c)>=.8 else "MEDIUM" if c is not None and abs(c)>=.6 else "LOW"})
    out.sort(key=lambda x:-float(x["AbsoluteCorrelation"] or 0))
    return out


def build_useless_report(power, correlations):
    mx={d:0.0 for d in DRIVERS}; partner={d:"" for d in DRIVERS}
    for r in correlations:
        v=float(r["AbsoluteCorrelation"] or 0)
        for d,p in ((r["Driver1"],r["Driver2"]),(r["Driver2"],r["Driver1"])):
            if v>mx[d]: mx[d]=v; partner[d]=p
    out=[]
    for r in power:
        ap=float(r["AltaPower"] or 0); mp=float(r["MediaPower"] or 0); reasons=[]
        if max(ap,mp)<.1: reasons.append("LOW_DISCRIMINATION")
        if mx[r["Driver"]]>=.8: reasons.append("HIGH_REDUNDANCY")
        if r["AltaDirection"] and r["MediaDirection"] and r["AltaDirection"]!=r["MediaDirection"]: reasons.append("UNSTABLE_DIRECTION")
        out.append({"Driver":r["Driver"],"AltaPower":ap,"MediaPower":mp,"MaxAbsoluteCorrelation":round(mx[r["Driver"]],6),"MostCorrelatedWith":partner[r["Driver"]],"Classification":"USEFUL" if not reasons else "WEAK" if "LOW_DISCRIMINATION" in reasons else "REDUNDANT_OR_UNSTABLE","Reasons":"|".join(reasons),"Recommendation":"KEEP_AND_MONITOR" if not reasons else "REVIEW_WEIGHT"})
    return out


def _write(path:Path,rows:list[dict],fields:list[str]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter=";",extrasaction="ignore"); w.writeheader(); w.writerows(rows)


def main()->int:
    rows=_load_rows(INPUT_FILE)
    power=build_driver_power(rows)
    curves=build_driver_curves(rows)
    pairs,singles=build_driver_pairs(rows)
    triples=build_driver_triples(rows,singles)
    corr=build_correlation(rows)
    useless=build_useless_report(power,corr)
    _write(OUTPUT_DIR/"07_driver_power.csv",power,["Driver",*sum(([f"{g}_Count",f"{g}_Mean",f"{g}_Median",f"{g}_StdDev"] for g in GROUPS),[]),"AltaDeltaMean","MediaDeltaMean","AltaAUC","MediaAUC","AltaEffectSize","MediaEffectSize","AltaDirection","MediaDirection","AltaPower","MediaPower"])
    _write(OUTPUT_DIR/"08_driver_curves.csv",curves,["Driver","Band","BinIndex","BinMin","BinMax","OK","KO","Total","HitRate"])
    _write(OUTPUT_DIR/"09_driver_pairs.csv",pairs,["Rule1","Rule2",*GROUPS,"AltaTotal","AltaHitRate","MediaTotal","MediaHitRate","PrimaryUse"])
    _write(OUTPUT_DIR/"10_driver_triples.csv",triples,["Rule1","Rule2","Rule3",*GROUPS,"AltaTotal","AltaHitRate","MediaTotal","MediaHitRate","PrimaryUse"])
    _write(OUTPUT_DIR/"11_driver_correlation.csv",corr,["Driver1","Driver2","Count","Correlation","AbsoluteCorrelation","RedundancyLevel"])
    _write(OUTPUT_DIR/"12_driver_useless.csv",useless,["Driver","AltaPower","MediaPower","MaxAbsoluteCorrelation","MostCorrelatedWith","Classification","Reasons","Recommendation"])
    print("=== DRIVER ANALYSIS ===")
    print(f"Partite concluse: {len(rows)}")
    for g in GROUPS: print(f"{g}: {sum(r['_Group']==g for r in rows)}")
    print(f"Driver power: {len(power)} | Curve: {len(curves)} | Coppie: {len(pairs)} | Triple: {len(triples)} | Correlazioni: {len(corr)}")
    return 0

if __name__ == "__main__": raise SystemExit(main())
