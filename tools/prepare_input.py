"""Convert pasted football fixture/result text into GioOver25 CSV inputs."""
from __future__ import annotations
import argparse,csv,re,unicodedata
from dataclasses import dataclass
from datetime import datetime,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY=ROOT/"data"/"league_registry.csv"
MOLDOVA_GROUP_MAP=ROOT/"docs"/"moldova_liga1_groups_2026.csv"
DATE_HEADER=re.compile(r"^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?(?:\s+\S+)?$")
DATED_TIME_RE=re.compile(r"^(\d{1,2})\.(\d{1,2})\.\s+(\d{1,2}:\d{2})$")
ROUND_RE=re.compile(r"^Giornata\s+(\d+)$",re.I)
TIME_RE=re.compile(r"^\d{1,2}:\d{2}$"); INT_RE=re.compile(r"^\d+$")
COUNTRY_MAP={"ALBANIA":"Albania","ANDORRA":"Andorra","ARABIA SAUDITA":"Saudi Arabia","ARMENIA":"Armenia","AUSTRALIA":"Australia","AUSTRIA":"Austria","AZERBAIJAN":"Azerbaijan","BELGIO":"Belgium","BHUTAN":"Bhutan","BIELORUSSIA":"Belarus","BOLIVIA":"Bolivia","BOSNIA & HERZEGOVINA":"Bosnia & Herzegovina","BULGARIA":"Bulgaria","CROAZIA":"Croatia","DANIMARCA":"Denmark","ESTONIA":"Estonia","FINLANDIA":"Finland","FRANCIA":"France","GALLES":"Wales","GEORGIA":"Georgia","GERMANIA":"Germany","GIAPPONE":"Japan","INDONESIA":"Indonesia","INGHILTERRA":"England","IRLANDA DEL NORD":"Northern Ireland","ISLANDA":"Iceland","ISOLE FAR OER":"Faroe Islands","ITALIA":"Italy","KAZAKISTAN":"Kazakhstan","LETTONIA":"Latvia","LITUANIA":"Lithuania","MACEDONIA DEL NORD":"North Macedonia","MESSICO":"Mexico","MOLDAVIA":"Moldova","MONTENEGRO":"Montenegro","NORVEGIA":"Norway","OLANDA":"Netherlands","PARAGUAY":"Paraguay","PERU":"Peru","POLONIA":"Poland","PORTOGALLO":"Portugal","REPUBBLICA CECA":"Czech Republic","ROMANIA":"Romania","RUSSIA":"Russia","SCOZIA":"Scotland","SERBIA":"Serbia","SLOVACCHIA":"Slovakia","SLOVENIA":"Slovenia","SPAGNA":"Spain","SRI LANKA":"Sri Lanka","SUD COREA":"South Korea","SVEZIA":"Sweden","SVIZZERA":"Switzerland","TURCHIA":"Turkey","UCRAINA":"Ukraine","UNGHERIA":"Hungary","USA":"USA"}
IGNORE={"Tutte","LIVE","Conclusi","Programma","Classifiche","Classifiche Live","Tabellone"}; STATUS={"Finale","FT","Dopo Suppl.","Posticipata","Rinviata","Sospesa"}; SKIP_STATUS={"Posticipata","Rinviata","Sospesa"}
@dataclass
class RegistryRow: league_id:str; country:str; league:str
@dataclass
class Match: league_id:str; date:str; home:str; away:str; hg:str=""; ag:str=""; status:str=""; notes:str=""; round:str=""
def norm(s): return re.sub(r"[^a-z0-9]+","",unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().casefold())
def load_registry(path):
 rows=[]
 with path.open(encoding="utf-8-sig",newline="") as f:
  for r in csv.DictReader(f,delimiter=";"):
   if r.get("LeagueId"): rows.append(RegistryRow(r["LeagueId"].strip(),r.get("Country","").strip(),r.get("League","").strip()))
 return rows
def load_moldova_groups(path=MOLDOVA_GROUP_MAP):
 groups={}
 if not path.exists():return groups
 with path.open(encoding="utf-8-sig",newline="") as f:
  for r in csv.DictReader(f,delimiter=";"):
   if r.get("Team") and r.get("LeagueId"):groups[norm(r["Team"])]=r["LeagueId"].strip()
 return groups
def aliases(s):
 x=s.casefold();vals={norm(s)}
 replacements={"ovest":"west","est":"east","sudwest":"southwest","sud":"south","nord":"north","gruppo":"group","fase vincitori":"winners phase","play-offs championship":"championship","play off promozione":"promotion playoff","division 3":"3rd division","besta deild femminile":"besta deild kvenna","ligue 3":"national","jupiler league":"jupiler pro league"}
 for a,b in replacements.items():x=x.replace(a,b)
 vals.add(norm(x));return vals
def resolve(reg,country,league):
 c=COUNTRY_MAP.get(country.upper(),country.title());cand=[r for r in reg if norm(r.country)==norm(c)];target=aliases(league)
 exact=[r for r in cand if norm(r.league) in target or aliases(r.league)&target]
 if len(exact)==1:return exact[0].league_id
 alias_matches=[r for r in cand if aliases(r.league)&target]
 if len(alias_matches)==1:return alias_matches[0].league_id
 nl=norm(league);fuzzy=[r for r in cand if norm(r.league) in nl or nl in norm(r.league)]
 if len(fuzzy)==1:return fuzzy[0].league_id
 country_prefix=norm(c);by_id=[]
 for r in cand:
  rid=norm(r.league_id);suffix=rid[len(country_prefix):] if rid.startswith(country_prefix) else rid
  if suffix==nl or suffix in nl or nl in suffix:by_id.append(r)
 if len(by_id)==1:return by_id[0].league_id
 explicit={("austria","oberosterreich"):"Austria_Oberosterreich",("austria","regionalligaest"):"Austria_Regionalliga_East",("belgium","jupilerleague"):"Belgium_JupilerProLeague",("france","ligue3"):"France_National",("hungary","nbi"):"Hungary_NBI",("iceland","bestadeildfemminile"):"Iceland_BestaDeildKvenna",("italy","seriea"):"Italy_SerieA"}
 wanted=explicit.get((norm(c),nl));return wanted if wanted and any(r.league_id==wanted for r in cand) else None
def resolve_match(reg,country,league,home,away):
 c=COUNTRY_MAP.get(country.upper(),country.title())
 if norm(c)=="moldova" and norm(league)=="liga1":
  groups=load_moldova_groups();h=groups.get(norm(home));a=groups.get(norm(away))
  if h and a and h==a:return h
  return None
 return resolve(reg,country,league)
def clean_lines(text):return [x.strip() for x in text.replace("\r","").split("\n") if x.strip()]
def parse_date(line,year):
 m=DATE_HEADER.match(line)
 if not m:return None
 d,mo,y=m.groups();y=int(y) if y else year;y=y+2000 if y<100 else y
 try:return datetime(y,int(mo),int(d)).strftime("%Y-%m-%d")
 except ValueError:return None
def parse_dated_time(line,year):
 m=DATED_TIME_RE.match(line)
 if not m:return None
 d,mo,_=m.groups()
 try:return datetime(year,int(mo),int(d)).strftime("%Y-%m-%d")
 except ValueError:return None
def dedupe_name(name):
 name=name.strip()
 if len(name)%2==0:
  half=len(name)//2
  if name[:half]==name[half:]:return name[:half]
 return name
def dedupe_pair(lines,i):
 if i>=len(lines):return None,i
 name=dedupe_name(lines[i]);i+=1
 if i<len(lines) and dedupe_name(lines[i])==name:i+=1
 return name,i
def parse_standard(lines,mode,reg,year,fallback_date):
 out=[];unresolved=set();current_date=fallback_date;league=country=None;current_round="";i=0
 while i<len(lines):
  line=lines[i];d=parse_date(line,year)
  if d:current_date=d;i+=1;continue
  rm=ROUND_RE.match(line)
  if rm:current_round=rm.group(1);i+=1;continue
  if line.endswith(":"):country=line[:-1].strip();i+=1;continue
  if line in IGNORE or line.startswith("mostra partite") or line=="SRF":i+=1;continue
  if i+1<len(lines) and lines[i+1].endswith(":"):league=line;i+=1;continue
  historical_date=parse_dated_time(line,year) if mode=="results" else None
  if historical_date and league and country:
   home,j=dedupe_pair(lines,i+1);away,j=dedupe_pair(lines,j);nums=[];k=j
   while k<len(lines) and len(nums)<2 and k<j+4:
    if INT_RE.match(lines[k]):nums.append(lines[k])
    else:break
    k+=1
   lid=resolve_match(reg,country,league,home,away)
   if len(nums)>=2:
    if lid:out.append(Match(lid,historical_date,home,away,nums[0],nums[1],"Finale","",current_round))
    else:unresolved.add((country,league))
   i=max(k,j);continue
  marker=(mode=="rank" and TIME_RE.match(line)) or (mode=="results" and line in STATUS)
  if marker and league and country and current_date:
   status=line if mode=="results" else "";start=i+1
   if mode=="rank" and start<len(lines) and lines[start]=="SRF":start+=1
   home,j=dedupe_pair(lines,start);away,j=dedupe_pair(lines,j);lid=resolve_match(reg,country,league,home,away)
   if mode=="rank":
    if lid:out.append(Match(lid,current_date,home,away))
    else:unresolved.add((country,league))
    i=j;continue
   nums=[];k=j
   while k<len(lines) and len(nums)<2 and k<j+5:
    if INT_RE.match(lines[k]):nums.append(lines[k])
    elif lines[k] not in {"-"}:break
    k+=1
   if status not in SKIP_STATUS and len(nums)>=2:
    if lid:out.append(Match(lid,current_date,home,away,nums[0],nums[1],"Finale","ET" if status=="Dopo Suppl." else "",current_round))
    else:unresolved.add((country,league))
   i=max(k,j);continue
  i+=1
 return out,unresolved
def parse_kolmonen(lines,mode,reg,year):
 out=[];unresolved=set();i=0
 while i+7<len(lines):
  if lines[i]!="Kolmonen" or not lines[i+1].startswith("Kolmonen,"):i+=1;continue
  league=lines[i+1].replace(","," ").replace("  "," ").strip();d=parse_date(lines[i+4],year);marker=lines[i+5];lid=resolve(reg,"Finland",league)
  if not d or not lid:i+=1;continue
  home=dedupe_name(lines[i+6]);away=dedupe_name(lines[i+8])
  if mode=="rank" and TIME_RE.match(marker):out.append(Match(lid,d,home,away))
  elif mode=="results" and marker in {"FT","Finale"} and i+11<len(lines) and INT_RE.match(lines[i+10]) and INT_RE.match(lines[i+11]):out.append(Match(lid,d,home,away,lines[i+10],lines[i+11],"Finale",""))
  i+=10
 return out,unresolved
def unique(ms):
 seen=set();out=[]
 for m in ms:
  k=(m.league_id,m.date,norm(m.home),norm(m.away))
  if k not in seen:seen.add(k);out.append(m)
 return out
def write_csv(path,mode,ms):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open("w",encoding="utf-8-sig",newline="") as f:
  w=csv.writer(f,delimiter=";",lineterminator="\n")
  if mode=="rank":w.writerow(["LeagueId","MatchDate","Home","Away"]);[w.writerow([m.league_id,m.date,m.home,m.away]) for m in ms]
  else:w.writerow(["LeagueId","Round","MatchDate","Home","Away","HG","AG","Status","Notes"]);[w.writerow([m.league_id,m.round,m.date,m.home,m.away,m.hg,m.ag,m.status,m.notes]) for m in ms]
def main():
 p=argparse.ArgumentParser();p.add_argument("mode",choices=["rank","results"]);p.add_argument("input",type=Path);p.add_argument("-o","--output",type=Path);p.add_argument("--registry",type=Path,default=DEFAULT_REGISTRY);p.add_argument("--year",type=int,default=datetime.now().year);p.add_argument("--date",help="Forza MatchDate (YYYY-MM-DD)");a=p.parse_args();now=datetime.now();fallback=a.date or (now+timedelta(days=1) if a.mode=="rank" else now).strftime("%Y-%m-%d")
 if a.date:
  try:datetime.strptime(a.date,"%Y-%m-%d")
  except ValueError:p.error("--date deve essere YYYY-MM-DD")
 lines=clean_lines(a.input.read_text(encoding="utf-8-sig"));reg=load_registry(a.registry);standard,u1=parse_standard(lines,a.mode,reg,a.year,fallback);kol,u2=parse_kolmonen(lines,a.mode,reg,a.year);ms=unique(standard+kol);output=a.output or (ROOT/"data"/"input_risultati"/"risultati.csv" if a.mode=="results" else ROOT/"data"/"input_partite"/"partite.csv");write_csv(output,a.mode,ms);print(f"[OK] {len(ms)} partite scritte in {output}");unresolved=sorted(u1|u2)
 if unresolved:
  print(f"[WARN] {len(unresolved)} competizioni non riconosciute/escluse:");[print(f"  - {c}: {l}") for c,l in unresolved]
if __name__=="__main__":main()
