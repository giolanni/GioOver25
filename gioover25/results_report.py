"""Post-results PDF, GS1 frozen tickets and historical ALTA leaderboards."""
from __future__ import annotations

import csv
from datetime import date,timedelta
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from . import daily_report as dr
from .team_names import normalize_team_name

TICKETS=Path("data/storico/gs1_over/schedine_gs1.csv")
FIELDS=["MatchDate","Rank","LeagueId","Home","Away","Band","MinOverRateFull","DeltaGA","Status","HG","AG","Outcome"]
STAKE=5.0
ODDS=2.0
INITIAL=100.0

def matchkey(r):
    league=str(r.get("LeagueId","")).strip()
    return (league,str(r.get("MatchDate","")).strip(),normalize_team_name(league,r.get("Home","")),normalize_team_name(league,r.get("Away","")))

def _num(v):
    try:return float(v)
    except (ValueError,TypeError):return 0.0

def freeze_tickets():
    """Persist ticket before results; never replace already frozen choices."""
    existing=dr._read_csv(TICKETS)
    frozen_dates={r["MatchDate"] for r in existing}
    official=dr._read_csv(Path("data/storico/gs1_over/storico_gs1_over.csv"))
    near=dr._read_csv(Path("data/storico/gs1_over/storico_gs1_over_near.csv"))
    by_date={}
    for row in official+near:
        by_date.setdefault(row["MatchDate"],[]).append(row)
    added=0
    for day,rows in sorted(by_date.items()):
        if day in frozen_dates:continue
        # Do not reconstruct past tickets from hindsight. Only freeze today/future.
        if day<date.today().isoformat():continue
        unique={}
        for row in rows:unique.setdefault(matchkey(row),row)
        priority={"ALTA":0,"MEDIA":1,"PROX-ALTA":2,"PROX-MEDIA-DELTA":3,"PROX-MEDIA-OVER":4,"NEAR":3}
        picks=sorted(unique.values(),key=lambda r:(priority.get(r.get("Band"),9),-_num(r.get("MinOverRateFull")),-_num(r.get("DeltaGA")),matchkey(r)))[:3]
        if len(picks)!=3:continue
        for i,row in enumerate(picks,1):
            existing.append({**{k:row.get(k,"") for k in FIELDS},"Rank":str(i)})
            added+=1
    if added:
        TICKETS.parent.mkdir(parents=True,exist_ok=True)
        with TICKETS.open("w",newline="",encoding="utf-8-sig") as fh:
            writer=csv.DictWriter(fh,fieldnames=FIELDS,delimiter=";",extrasaction="ignore")
            writer.writeheader();writer.writerows(existing)
    return added

def ticket_summary():
    tickets=dr._read_csv(TICKETS)
    official=dr._read_csv(Path("data/storico/gs1_over/storico_gs1_over.csv"))
    near=dr._read_csv(Path("data/storico/gs1_over/storico_gs1_over_near.csv"))
    lookup={matchkey(r):r for r in official+near}
    days={}
    for r in tickets:
        actual=lookup.get(matchkey(r),{})
        days.setdefault(r["MatchDate"],[]).append({**r,"Outcome":actual.get("Outcome",""),"HG":actual.get("HG",""),"AG":actual.get("AG","")})
    wins=losses=pending=0
    outcomes={}
    for day,rows in sorted(days.items()):
        if len(rows)!=3:continue
        statuses=[r["Outcome"] for r in rows]
        if "KO" in statuses:status="PERSA";losses+=1
        elif all(x=="OK" for x in statuses):status="VINTA";wins+=1
        else:status="IN ATTESA";pending+=1
        outcomes[day]=(status,sorted(rows,key=lambda r:int(r["Rank"])))
    profit=STAKE*(wins-losses)
    return outcomes,{"wins":wins,"losses":losses,"pending":pending,"profit":profit,"balance":INITIAL+profit}

def leaderboard(day,market,weekly=False):
    start=day-timedelta(days=6) if weekly else day
    stats=[]
    for folder in sorted(dr.HISTORY_DIR.glob("*")):
        if not folder.is_dir():continue
        engine=folder.name
        if market=="BTTS" and not engine.startswith("vg"):continue
        if market=="Over25" and engine.startswith("vg"):continue
        rows=dr._history(engine)
        ok=ko=0
        for r in rows:
            d=dr._parse_date(r.get("MatchDate"))
            if d is None or not(start<=d<=day):continue
            if str(r.get("Band","")).upper()!="ALTA":continue
            outcome=str(r.get(market,"")).strip().upper()
            if outcome=="OK":ok+=1
            elif outcome=="KO":ko+=1
        if ok+ko:stats.append((engine,ok,ko,ok+ko,100*ok/(ok+ko)))
    return sorted(stats,key=lambda x:(-x[4],-x[3],x[0]))

def _results_table(rows,market,styles,gs1=False):
    headers=["Lega","Partita","Fascia","Ris.","Esito"]
    data=[headers]
    for r in rows:
        outcome=str(r.get("Outcome" if gs1 else market,"")).upper()
        hg,ag=r.get("HG",""),r.get("AG","")
        score=f"{hg}-{ag}" if str(hg).strip() and str(ag).strip() else "-"
        data.append([dr._p(r.get("LeagueId",""),styles["cell"]),
                     dr._p(dr._match(r),styles["cell_bold"]),
                     dr._p(r.get("Band",""),styles["cell"]),
                     score,outcome if outcome in ("OK","KO") else "ATTESA"])
    if len(data)==1:return dr._p("Nessuna selezione.",styles["empty"])
    table=Table(data,colWidths=[37*mm,85*mm,23*mm,14*mm,16*mm],repeatRows=1)
    commands=[("BACKGROUND",(0,0),(-1,0),dr.INK),("TEXTCOLOR",(0,0),(-1,0),colors.white),
              ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),7),
              ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("GRID",(0,0),(-1,-1),.25,dr.LINE)]
    for i,r in enumerate(rows,1):
        outcome=str(r.get("Outcome" if gs1 else market,"")).upper()
        shade=colors.HexColor("#D1FADF") if outcome=="OK" else colors.HexColor("#FEE4E2") if outcome=="KO" else dr.LIGHT
        commands.append(("BACKGROUND",(0,i),(-1,i),shade))
    table.setStyle(TableStyle(commands))
    return table

def _ranking_table(rows,styles):
    if not rows:return dr._p("Nessun esito ALTA definitivo.",styles["empty"])
    data=[["Engine","OK","KO","Totale","% OK"]]
    for e,ok,ko,total,pct in rows:
        data.append([e,str(ok),str(ko),str(total),f"{pct:.2f}%"])
    t=Table(data,colWidths=[70*mm,25*mm,25*mm,25*mm,30*mm],repeatRows=1)
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),dr.INK),("TEXTCOLOR",(0,0),(-1,0),colors.white),
                          ("GRID",(0,0),(-1,-1),.25,dr.LINE),("FONTSIZE",(0,0),(-1,-1),8),
                          ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,dr.LIGHT])]))
    return t

def generate_results_report(day:date):
    styles=dr._styles()
    path=dr.OUTPUT_DIR/f"GioOver_Risultati_{day.isoformat()}.pdf"
    path.parent.mkdir(parents=True,exist_ok=True)
    story=[dr._p("GioOver - Consuntivo risultati",styles["title"]),
           dr._p(day.strftime("%d/%m/%Y"),styles["subtitle"]),Spacer(1,4*mm)]
    def section(title,content):
        story.extend([dr._p(title,styles["section"]),content,Spacer(1,3*mm)])
    # Reuse the morning report's sections, filtering by the original PredictionDate.
    cautious=dr._best_engine(dr.V20_FAMILY,day)
    permissive=dr._best_engine(dr._permissive_candidates(),day)
    def engine_section(title,engine,market="Over25",minimum=None):
        if not engine:return
        rows=[r for r in dr._history(engine) if r.get("MatchDate")==day.isoformat()
              and r.get("PredictionDate","")<=day.isoformat()
              and (minimum is None or _num(r.get("Score"))>minimum)]
        section(f"{title} - {engine}",_results_table(rows,market,styles))
    engine_section("ALGORITMO CAUTO",cautious["engine"],minimum=70)
    engine_section("ALGORITMO PERMISSIVO",permissive["engine"],minimum=70)
    engine_section("GOL - VG1","vg1","BTTS",minimum=65)
    for engine in dr.SPECIAL_ENGINES:
        engine_section(engine.upper(),engine,"BTTS" if engine.startswith("vg") else "Over25")
    for label,file in [("GS1 - OVER 2.5",Path("data/storico/gs1_over/storico_gs1_over.csv")),
                       ("GS1 - NEAR",Path("data/storico/gs1_over/storico_gs1_over_near.csv"))]:
        rows=[r for r in dr._read_csv(file) if r.get("MatchDate")==day.isoformat()]
        section(label,_results_table(rows,"Outcome",styles,gs1=True))
    tickets,summary=ticket_summary()
    state,rows=tickets.get(day.isoformat(),("NON FORMATA",[]))
    section("GS1 - SCHEDINA",dr._p(f"Esito: {state}. Prime 3 gare congelate prima dei risultati.",styles["meta"]))
    if rows:story.extend([_results_table(rows,"Outcome",styles,gs1=True),Spacer(1,3*mm)])
    section("GS1 - BILANCIO VIRTUALE",dr._p(
        f"Vinte {summary['wins']} | Perse {summary['losses']} | In attesa {summary['pending']} | "
        f"Puntata EUR {STAKE:.2f} | Quota schedina {ODDS:.2f} | "
        f"Utile EUR {summary['profit']:+.2f} | Saldo EUR {summary['balance']:.2f}. "
        "Quote ipotetiche, non quote bookmaker.",styles["meta"]))
    for market,title in [("Over25","OVER 2.5"),("BTTS","BTTS")]:
        section(f"CLASSIFICA {title} - GIORNATA",_ranking_table(leaderboard(day,market),styles))
        section(f"CLASSIFICA {title} - 7 GIORNI",_ranking_table(leaderboard(day,market,weekly=True),styles))
    doc=SimpleDocTemplate(str(path),pagesize=A4,rightMargin=10*mm,leftMargin=10*mm,
                          topMargin=10*mm,bottomMargin=11*mm)
    doc.build(story)
    print(f"[REPORT] Consuntivo generato: {path}")
    return path

def update_reports(input_file):
    # Snapshot only future/current fixtures; no retroactive ticket construction.
    freeze_tickets()
    dates=set()
    for r in dr._read_csv(Path(input_file)):
        d=dr._parse_date(r.get("MatchDate"))
        if d:dates.add(d)
    for day in sorted(dates):generate_results_report(day)
