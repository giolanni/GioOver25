"""GM1 V20: confronto profilo/esclusi e complemento scelto solo sul TRAIN."""
from __future__ import annotations
import csv
from pathlib import Path
from .gm1_v20_profiles import DRIVERS, candidates, label, load_v20, matches, split, wilson

FIXED = ((2, "AwayDefenseWeaknessScore", ">=", 25.0),
         (4, "AwayLast10OverScore", ">=", 13.5))
OUT = Path("data/analysis")

def stats(rows):
    n = len(rows)
    ok = sum(r["ok"] for r in rows)
    return ok, n-ok, n, round(100*ok/n, 2) if n else 0

def choose(train):
    excluded = [r for r in train if not matches(r, FIXED)]
    baseline = wilson(sum(r["ok"] for r in excluded), len(excluded))
    best = None
    seen = set()
    for rule in candidates(train):
        mask = tuple(i for i,r in enumerate(excluded) if matches(r, rule))
        if len(mask) < 25 or len(mask) == len(excluded) or mask in seen:
            continue
        seen.add(mask)
        ok = sum(excluded[i]["ok"] for i in mask)
        lower = wilson(ok, len(mask))
        if lower <= baseline:
            continue
        rank = (lower, ok/len(mask), len(mask))
        if best is None or rank > best[0]:
            best = (rank, rule)
    print(f"[SEARCH] unique_candidates={len(seen)} excluded_baseline_wilson={baseline*100:.2f}%")
    return best[1] if best else None

def run():
    splits = split(load_v20())
    rule = choose(splits["TRAIN"])
    print("[FIXED]", label(FIXED))
    print("[COMPLEMENT TRAIN-ONLY]", label(rule) if rule else "NESSUNO")
    reports, drivers = [], []
    for part in ("TRAIN", "VALID", "TEST"):
        all_rows = splits[part]
        fixed = [r for r in all_rows if matches(r, FIXED)]
        excluded = [r for r in all_rows if not matches(r, FIXED)]
        extra = [r for r in excluded if matches(r, rule)] if rule else []
        groups = {"BASELINE_ALTA": all_rows, "FIXED_PROFILE": fixed,
                  "EXCLUDED": excluded, "COMPLEMENT_ONLY": extra,
                  "FIXED_PLUS_COMPLEMENT": fixed + extra}
        for name, rows in groups.items():
            ok, ko, n, pct = stats(rows)
            print(f"[{part}] {name}: OK={ok} KO={ko} Tot={n} Pct={pct:.2f}%")
            reports.append(dict(Split=part, Group=name, OK=ok, KO=ko, Totale=n,
                                Perc=pct, CoveragePct=round(100*n/len(all_rows),2),
                                WilsonLower=round(100*wilson(ok,n),2)))
            for idx, field in enumerate(DRIVERS):
                good = [r["features"][idx] for r in rows if r["ok"]]
                bad = [r["features"][idx] for r in rows if not r["ok"]]
                drivers.append(dict(Split=part, Group=name, Driver=field,
                                    OKMean=round(sum(good)/len(good),3) if good else "",
                                    KOMean=round(sum(bad)/len(bad),3) if bad else "",
                                    OKCount=len(good), KOCount=len(bad)))
    OUT.mkdir(parents=True, exist_ok=True)
    for filename, data in (("gm1_v20_complement_report.csv",reports),
                           ("gm1_v20_complement_drivers.csv",drivers)):
        path = OUT/filename
        with path.open("w",encoding="utf-8-sig",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=list(data[0]),delimiter=";")
            writer.writeheader()
            writer.writerows(data)
        print(f"[WRITE] {path}: {len(data)} righe")
    print("[NOTE] Complemento selezionato esclusivamente sul TRAIN. Nessun engine modificato.")

if __name__ == "__main__":
    run()
