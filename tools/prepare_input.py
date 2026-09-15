"""Convert pasted football fixture/result text into GioOver25 CSV inputs.

Usage:
  python tools/prepare_input.py rank input.txt
  python tools/prepare_input.py results input.txt
  python tools/prepare_input.py rank input.txt -o data/input_partite/partite.csv

The parser is deliberately conservative: competitions not matched to
league_registry.csv are reported and omitted rather than guessed.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY = ROOT / "data" / "league_registry.csv"
DATE_HEADER = re.compile(r"^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?(?:\s+\S+)?$")
TIME_RE = re.compile(r"^\d{1,2}:\d{2}$")
INT_RE = re.compile(r"^\d+$")

COUNTRY_MAP = {
    "ALBANIA":"Albania", "ANDORRA":"Andorra", "ARABIA SAUDITA":"Saudi Arabia",
    "ARMENIA":"Armenia", "AUSTRALIA":"Australia", "AUSTRIA":"Austria",
    "AZERBAIJAN":"Azerbaijan", "BELGIO":"Belgium", "BHUTAN":"Bhutan",
    "BIELORUSSIA":"Belarus", "BOLIVIA":"Bolivia", "BOSNIA & HERZEGOVINA":"Bosnia & Herzegovina",
    "BULGARIA":"Bulgaria", "CROAZIA":"Croatia", "DANIMARCA":"Denmark", "ESTONIA":"Estonia",
    "FINLANDIA":"Finland", "FRANCIA":"France", "GALLES":"Wales", "GEORGIA":"Georgia",
    "GERMANIA":"Germany", "GIAPPONE":"Japan", "INDONESIA":"Indonesia", "INGHILTERRA":"England",
    "ISLANDA":"Iceland", "ISOLE FAR OER":"Faroe Islands", "ITALIA":"Italy", "KAZAKISTAN":"Kazakhstan",
    "LETTONIA":"Latvia", "LITUANIA":"Lithuania", "MACEDONIA DEL NORD":"North Macedonia",
    "MESSICO":"Mexico", "MOLDAVIA":"Moldova", "MONTENEGRO":"Montenegro", "NORVEGIA":"Norway",
    "OLANDA":"Netherlands", "PARAGUAY":"Paraguay", "PERU":"Peru", "POLONIA":"Poland",
    "PORTOGALLO":"Portugal", "REPUBBLICA CECA":"Czech Republic", "ROMANIA":"Romania", "RUSSIA":"Russia",
    "SERBIA":"Serbia", "SLOVACCHIA":"Slovakia", "SLOVENIA":"Slovenia", "SPAGNA":"Spain",
    "SRI LANKA":"Sri Lanka", "SUD COREA":"South Korea", "SVEZIA":"Sweden", "SVIZZERA":"Switzerland",
    "TURCHIA":"Turkey", "UCRAINA":"Ukraine", "USA":"USA",
}

IGNORE = {"Tutte", "LIVE", "Conclusi", "Programma", "Classifiche", "Classifiche Live", "Tabellone"}
STATUS = {"Finale", "FT", "Dopo Suppl.", "Posticipata", "Rinviata", "Sospesa"}
SKIP_STATUS = {"Posticipata", "Rinviata", "Sospesa"}

@dataclass
class RegistryRow:
    league_id: str
    country: str
    league: str

@dataclass
class Match:
    league_id: str
    date: str
    home: str
    away: str
    hg: str = ""
    ag: str = ""
    status: str = ""
    notes: str = ""


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", "", s)


def load_registry(path: Path):
    rows=[]
    with path.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r.get("LeagueId"):
                rows.append(RegistryRow(r["LeagueId"].strip(), r.get("Country","").strip(), r.get("League","").strip()))
    return rows


def aliases(league: str):
    x=league.casefold()
    vals={norm(league)}
    replacements={"ovest":"west", "sudwest":"southwest", "sud":"south", "nord":"north",
                  "gruppo":"group", "fase vincitori":"winners phase", "play-offs championship":"championship",
                  "play off promozione":"promotion playoff"}
    for a,b in replacements.items(): x=x.replace(a,b)
    vals.add(norm(x))
    return vals


def resolve(registry, country, league):
    c=COUNTRY_MAP.get(country.upper(), country.title())
    nc=norm(c); candidates=[r for r in registry if norm(r.country)==nc]
    target=aliases(league)
    exact=[r for r in candidates if norm(r.league) in target or bool(aliases(r.league)&target)]
    if len(exact)==1: return exact[0].league_id
    # phase-aware fallback: require all meaningful registry tokens to occur in source or vice versa
    nl=norm(league)
    fuzzy=[r for r in candidates if norm(r.league) in nl or nl in norm(r.league)]
    return fuzzy[0].league_id if len(fuzzy)==1 else None


def clean_lines(text):
    return [x.strip() for x in text.replace("\r","").split("\n") if x.strip()]


def parse_date(line, default_year):
    m=DATE_HEADER.match(line)
    if not m: return None
    d,mo,y=m.groups(); y=int(y) if y else default_year
    if y<100: y+=2000
    try: return datetime(y,int(mo),int(d)).strftime("%Y-%m-%d")
    except ValueError: return None


def dedupe_pair(lines, i):
    """Flashscore usually repeats each team. Return displayed name and next index."""
    if i>=len(lines): return None,i
    name=lines[i]; i+=1
    if i<len(lines) and lines[i]==name: i+=1
    return name,i


def parse_standard(lines, mode, registry, default_year):
    out=[]; unresolved=set(); current_date=None; league=None; country=None; i=0
    while i<len(lines):
        line=lines[i]
        d=parse_date(line, default_year)
        if d: current_date=d; i+=1; continue
        if line.endswith(":"):
            country=line[:-1].strip(); i+=1; continue
        if line in IGNORE or line.startswith("mostra partite") or line=="SRF": i+=1; continue
        # League title is normally immediately before COUNTRY:
        if i+1<len(lines) and lines[i+1].endswith(":"):
            league=line; i+=1; continue
        if mode=="rank" and TIME_RE.match(line):
            if not (league and country and current_date): i+=1; continue
            home,j=dedupe_pair(lines,i+1); away,j=dedupe_pair(lines,j)
            if not home or not away: i+=1; continue
            lid=resolve(registry,country,league)
            if lid: out.append(Match(lid,current_date,home,away))
            else: unresolved.add((country,league))
            i=j
            while i<len(lines) and lines[i] in {"-"}: i+=1
            continue
        if mode=="results" and line in STATUS:
            status=line
            if not (league and country and current_date): i+=1; continue
            home,j=dedupe_pair(lines,i+1); away,j=dedupe_pair(lines,j)
            # Some source rows contain stray ranking/penalty numbers. Take first two consecutive numeric score lines.
            nums=[]; k=j
            while k<len(lines) and len(nums)<2 and k<j+5:
                if INT_RE.match(lines[k]): nums.append(lines[k])
                elif lines[k] not in {"-"}: break
                k+=1
            lid=resolve(registry,country,league)
            if status not in SKIP_STATUS and len(nums)>=2:
                if lid: out.append(Match(lid,current_date,home,away,nums[0],nums[1],"FINAL", "ET" if status=="Dopo Suppl." else ""))
                else: unresolved.add((country,league))
            i=max(k,j); continue
        i+=1
    return out,unresolved


def parse_kolmonen(lines, mode, registry, default_year):
    out=[]; unresolved=set(); i=0
    while i+7<len(lines):
        if lines[i]!="Kolmonen" or not lines[i+1].startswith("Kolmonen,"):
            i+=1; continue
        league=lines[i+1].replace(",", " ").replace("  "," ").strip()
        country="Finland"
        d=parse_date(lines[i+4],default_year)
        marker=lines[i+5]
        if not d or not (TIME_RE.match(marker) or marker in {"FT","Finale"}): i+=1; continue
        # In this format first value is full name, second may be source abbreviation: keep full names.
        home=lines[i+6]; away=lines[i+8] if i+8<len(lines) else ""
        lid=resolve(registry,country,league)
        if not lid: unresolved.add((country,league)); i+=1; continue
        if mode=="rank" and TIME_RE.match(marker): out.append(Match(lid,d,home,away))
        elif mode=="results" and marker in {"FT","Finale"}:
            # home, alias, away, alias, HG, AG; later numbers are not regulation score.
            score_i=i+10
            if score_i+1<len(lines) and INT_RE.match(lines[score_i]) and INT_RE.match(lines[score_i+1]):
                out.append(Match(lid,d,home,away,lines[score_i],lines[score_i+1],"FINAL",""))
        i+=10
    return out,unresolved


def unique(matches):
    seen=set(); out=[]
    for m in matches:
        key=(m.league_id,m.date,norm(m.home),norm(m.away))
        if key not in seen: seen.add(key); out.append(m)
    return out


def write_csv(path, mode, matches):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.writer(f,delimiter=";",lineterminator="\n")
        if mode=="rank":
            w.writerow(["LeagueId","MatchDate","Home","Away"])
            for m in matches: w.writerow([m.league_id,m.date,m.home,m.away])
        else:
            w.writerow(["LeagueId","Round","MatchDate","Home","Away","HG","AG","Status","Notes"])
            for m in matches: w.writerow([m.league_id,"",m.date,m.home,m.away,m.hg,m.ag,m.status,m.notes])


def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=["rank","results"])
    p.add_argument("input",type=Path)
    p.add_argument("-o","--output",type=Path)
    p.add_argument("--registry",type=Path,default=DEFAULT_REGISTRY)
    p.add_argument("--year",type=int,default=datetime.now().year)
    a=p.parse_args()
    text=a.input.read_text(encoding="utf-8-sig")
    lines=clean_lines(text); registry=load_registry(a.registry)
    standard,u1=parse_standard(lines,a.mode,registry,a.year)
    kolmonen,u2=parse_kolmonen(lines,a.mode,registry,a.year)
    matches=unique(standard+kolmonen)
    if a.output: output=a.output
    else:
        date=matches[0].date.replace("-","_") if matches else "unknown"
        folder=ROOT/"data"/("input_partite" if a.mode=="rank" else "input_risultati")
        output=folder/f"{'partite' if a.mode=='rank' else 'risultati'}_{date}.csv"
    write_csv(output,a.mode,matches)
    unresolved=sorted(u1|u2)
    print(f"[OK] {len(matches)} partite scritte in {output}")
    if unresolved:
        print(f"[WARN] {len(unresolved)} competizioni non riconosciute/escluse:")
        for c,l in unresolved: print(f"  - {c}: {l}")

if __name__=="__main__": main()
