"""Diagnostica compatta metadata Livesport per onboarding Tier1-3 CREATE."""
from __future__ import annotations
import csv, json
from tools.prepare_input import ROOT
from tools.bulk_onboard_tier123 import latest_plan, _walk_values
from analysis.audit_diretta_standings import search_tournaments

def vals(obj, fragment):
    out=[]
    for v in _walk_values(obj, fragment):
        if isinstance(v,(str,int)) and str(v).strip():
            out.append(str(v).strip())
    return list(dict.fromkeys(out))

def main():
    plan=latest_plan()
    with plan.open(encoding="utf-8-sig",newline="") as h:
        rows=[r for r in csv.DictReader(h,delimiter=";") if r.get("Action")=="CREATE"]
    print(f"[INPUT] {plan}")
    for r in rows:
        sources=[x.strip() for x in r["SourceLeagues"].split("|") if x.strip()]
        wanted={x.strip() for x in r.get("TournamentIds","").split("|") if x.strip()}
        print(f"\n[{r['LeagueId']}]")
        for source in sources:
            try:
                found=search_tournaments(source,20)
            except Exception as e:
                print(f"  {source}: ERROR {type(e).__name__}: {e}")
                continue
            compatible=[]
            for raw in found:
                t=raw.get("defaultTournament") or {}
                tid=str(t.get("id","")).strip()
                raw_id=str(raw.get("id","")).strip()
                if wanted and tid not in wanted and raw_id not in wanted:
                    continue
                compatible.append(raw)
            print(f"  {source}: search={len(found)} compatible={len(compatible)}")
            for raw in compatible[:3]:
                t=raw.get("defaultTournament") or {}
                print("    "
                    f"raw.id={raw.get('id','')} default.id={t.get('id','')} "
                    f"name={raw.get('name','') or t.get('name','')} "
                    f"country={(raw.get('defaultCountry') or {}).get('name','')}")
                print(f"    stages={t.get('stageWithStatsDataIds') or []}")
                print(f"    seasons={vals(raw,'season')[:10] or '-'}")
                print(f"    urls={vals(raw,'url')[:10] or '-'}")
                print(f"    paths={vals(raw,'path')[:10] or '-'}")

if __name__=="__main__":
    main()
