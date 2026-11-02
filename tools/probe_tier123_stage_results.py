"""Probe read-only dei feed Livesport stage per risultati Tier1-3."""
from __future__ import annotations
import csv
from tools.bulk_onboard_tier123 import latest_plan
from tools.bonifica_storici_diretta import parse_results_feed
from analysis.audit_diretta_standings import _request_text

PATTERNS = [
    "https://global.flashscore.ninja/323/x/feed/tr_1_{tid}_{stage}_0_2_it_1",
    "https://global.flashscore.ninja/323/x/feed/tr_1_{tid}_{stage}_0_2",
    "https://global.flashscore.ninja/323/x/feed/tr_1_{tid}_{stage}_0_1_it_1",
    "https://global.flashscore.ninja/323/x/feed/tr_1_{tid}_{stage}_0_1",
]

def split(v):
    return [x.strip() for x in (v or "").split("|") if x.strip()]

def main():
    with latest_plan().open(encoding="utf-8-sig",newline="") as h:
        rows=[r for r in csv.DictReader(h,delimiter=";") if r.get("Action")=="CREATE"]
    preferred=["Argentina_LigaProfesionalClausura","Colombia_PrimeraAClausura","Uruguay_LigaAUFUruguayaClausura"]
    chosen=[next(r for r in rows if r["LeagueId"]==lid) for lid in preferred]
    for r in chosen:
        template_ids=split(r.get("TournamentIds"))
        tids=split(r.get("TournamentCurrentIds"))
        stages=split(r.get("TournamentStageIds"))
        print(f"\n[{r['LeagueId']}] template={template_ids} current={tids} stages={stages}")
        for tid in tids[:1]:
            for stage in stages:
                for pattern in PATTERNS:
                    url=pattern.format(tid=tid,stage=stage)
                    try:
                        payload=_request_text(url,15,None)
                        matches=parse_results_feed(payload)
                        print(f"  {url} | bytes={len(payload)} | matches={len(matches)}")
                        if matches:
                            dates=sorted({m.date for m in matches})
                            print(f"    RANGE={dates[0]}..{dates[-1]}")
                            break
                    except Exception as e:
                        print(f"  {url} | {type(e).__name__}")
                else:
                    continue
                break

if __name__=="__main__":
    main()
