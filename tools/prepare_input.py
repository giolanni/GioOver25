"""Convert pasted football fixture/result text into GioOver25 CSV inputs."""
from __future__ import annotations
import argparse,csv,re,unicodedata
from dataclasses import dataclass
from datetime import datetime,timedelta
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEFAULT_REGISTRY=ROOT/"data"/"league_registry.csv"
TEAM_MAPPING_FILES=[
 ROOT/"docs"/"moldova_liga1_groups_2026.csv",
 ROOT/"docs"/"Portugal_Liga3_2026-27_team_mapping.csv",
 ROOT/"docs"/"Indonesia_Championship_2026-27_team_mapping.csv",
 ROOT/"docs"/"kolmonen_2026_team_league_map.csv",
 ROOT/"docs"/"mappa_teams_groups_peru_2liga..txt",
 ROOT/"docs"/"mappa_teams_league_mslnextpro.txt",
 ROOT/"docs"/"mappa_teams_league_usl2division.txt",
]
DATE_HEADER=re.compile(r"^(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?(?:\s+\S+)?$")
DATED_TIME_RE=re.compile(r"^(\d{1,2})\.(\d{1,2})\.\s+(\d{1,2}:\d{2})$")
ROUND_RE=re.compile(r"^Giornata\s+(\d+)$",re.I)
TIME_RE=re.compile(r"^\d{1,2}:\d{2}$"); INT_RE=re.compile(r"^\d+$")
COUNTRY_MAP={"ALBANIA":"Albania","ANDORRA":"Andorra","ARABIA SAUDITA":"Saudi Arabia","ARMENIA":"Armenia","AUSTRALIA":"Australia","AUSTRIA":"Austria","AZERBAIJAN":"Azerbaijan","BELGIO":"Belgium","BHUTAN":"Bhutan","BIELORUSSIA":"Belarus","BOLIVIA":"Bolivia","BOSNIA & HERZEGOVINA":"Bosnia & Herzegovina","BULGARIA":"Bulgaria","CROAZIA":"Croatia","DANIMARCA":"Denmark","ESTONIA":"Estonia","FINLANDIA":"Finland","FRANCIA":"France","GALLES":"Wales","GEORGIA":"Georgia","GERMANIA":"Germany","GIAPPONE":"Japan","INDONESIA":"Indonesia","INGHILTERRA":"England","IRLANDA DEL NORD":"Northern Ireland","ISLANDA":"Iceland","ISOLE FAR OER":"Faroe Islands","ITALIA":"Italy","KAZAKISTAN":"Kazakhstan","LETTONIA":"Latvia","LITUANIA":"Lithuania","MACEDONIA DEL NORD":"North Macedonia","MESSICO":"Mexico","MOLDAVIA":"Moldova","MONTENEGRO":"Montenegro","NORVEGIA":"Norway","OLANDA":"Netherlands","PARAGUAY":"Paraguay","PERU":"Peru","POLONIA":"Poland","PORTOGALLO":"Portugal","REPUBBLICA CECA":"Czech Republic","ROMANIA":"Romania","RUSSIA":"Russia","SCOZIA":"Scotland","SERBIA":"Serbia","SLOVACCHIA":"Slovakia","SLOVENIA":"Slovenia","SPAGNA":"Spain","SRI LANKA":"Sri Lanka","SUD COREA":"South Korea","SVEZIA":"Sweden","SVIZZERA":"Switzerland","TURCHIA":"Turkey","UCRAINA":"Ukraine","UNGHERIA":"Hungary","USA":"USA"}
IGNORE={"Tutte","LIVE","Conclusi","Programma","Classifiche","Classifiche Live","Tabellone"}; STATUS={"Finale","FT","Dopo Suppl.","Dopo Rigori","Posticipata","Rinviata","Sospesa"}; SKIP_STATUS={"Posticipata","Rinviata","Sospesa"}
@dataclass
class RegistryRow: league_id:str; country:str; league:str
@dataclass
class Match: league_id:str; date:str; home:str; away:str; hg:str=""; ag:str=""; status:str=""; notes:str=""; round:str=""
def norm(s): return re.sub(r"[^a-z0-9]+","",unicodedata.normalize("NFKD",s).encode("ascii","ignore").decode().casefold())
TEAM_ALIASES={
 "pargasif":"PIF","maskunpalloseura":"MaPS","nykarlebyik":"NIK",
 "lapuanvirkia":"Virkiä","vaasaifk":"VIFK","tampereunited2":"Tampere Utd/2",
 "kajaaninhaka":"KajHa","keminpalloseura":"KePS",
 "fckiisto":"Kiisto","fcsaaripotku":"Sääripotku",
 "riihimaenpalloseura":"RiPS","tipsu21":"TiPS/2 U21",
 "puotinkylanvaltti":"Valtti","vjsakatemia":"VJS 2",
 "pakkalanpalloseura":"PPS","fckontu":"Kontu",
 "atlantisfcakatemia":"Atlantis 2",
 "comod":"Como Women","fiorentinad":"Fiorentina","sassuolod":"Sassuolo","napolid":"Napoli",
 "ternanad":"Ternana","laziod":"Lazio","interd":"Inter","parmad":"Parma",
 "juventusd":"Juventus","como1907d":"Como 1907","romad":"Roma","miland":"Milan",
 "niemisenurheilijat":"NiemU","toivalanurheilijat":"ToU",
 "kotajarvenpallo":"KJP","savonlinnanseudunpalloseura":"STPS","mikkelinpallokissat":"MiPK",
 "gillafc":"Gilla","nummelanpalloseura":"NuPS","lohjanpallo":"LoPa","malminpalloseura":"MPS","mpsatleticomalmi":"MPS",
 "viktoriacolonia":"Viktoria Koln","raelingen":"Raelingen","rælingen":"Raelingen",
 "fcpelikarhut":"PeKa","kouvolanjalkapallo":"KoPa",
 "littoistentyovaenurheilijatU20".casefold():"LTU U20","ifkmariehamn2":"IFK 2",
}
def canonical_team(name):
 """Restituisce il nome squadra canonico noto a GioOver25, altrimenti l'originale."""
 return TEAM_ALIASES.get(norm(name),name.strip())
def load_registry(path):
 rows=[]
 with path.open(encoding="utf-8-sig",newline="") as f:
  for r in csv.DictReader(f,delimiter=";"):
   if r.get("LeagueId"): rows.append(RegistryRow(r["LeagueId"].strip(),r.get("Country","").strip(),r.get("League","").strip()))
 return rows
def load_team_mappings(paths=TEAM_MAPPING_FILES):
 """Carica i mapping squadra->LeagueId documentati in docs (CSV ';' o TXT team=LeagueId)."""
 groups={}
 for path in paths:
  if not path.exists():continue
  if path.suffix.casefold()==".csv":
   with path.open(encoding="utf-8-sig",newline="") as f:
    for r in csv.DictReader(f,delimiter=";"):
     team=r.get("Team") or r.get("SourceTeam") or r.get("CanonicalTeam")
     lid=r.get("LeagueId")
     if team and lid:groups.setdefault(norm(team),set()).add(lid.strip())
  else:
   for line in path.read_text(encoding="utf-8-sig").splitlines():
    line=line.strip()
    if not line or line.startswith("#") or "=" not in line:continue
    team,lid=line.split("=",1)
    if team.strip() and lid.strip():groups.setdefault(norm(team.strip()),set()).add(lid.strip())
 return groups

def resolve_team_mapping(reg,country,home,away):
 groups=load_team_mappings()
 valid={r.league_id for r in reg if norm(r.country)==norm(country)}
 h=groups.get(norm(home),set())&valid
 a=groups.get(norm(away),set())&valid
 common=h&a
 return next(iter(common)) if len(common)==1 else None
def aliases(s):
 x=s.casefold();vals={norm(s)}
 replacements={"ovest":"west","est":"east","sudwest":"southwest","sud":"south","nord":"north","gruppo":"group","fase vincitori":"winners phase","play-offs championship":"championship","play off promozione":"promotion playoff","division 3":"3rd division","besta deild femminile":"besta deild kvenna","women":"femminile","ligue 3":"national","jupiler league":"jupiler pro league"}
 for a,b in replacements.items():x=x.replace(a,b)
 vals.add(norm(x));return vals
def _has_competition_qualifier_gap(source, target):
 """True se il nome sorgente aggiunge qualificatori strutturali assenti nel target."""
 src=re.findall(r"[a-z]+|\d+",unicodedata.normalize("NFKD",source).encode("ascii","ignore").decode().casefold())
 dst=re.findall(r"[a-z]+|\d+",unicodedata.normalize("NFKD",target).encode("ascii","ignore").decode().casefold())
 structural={"group","gruppo","division","league","liga","national","fnl"}
 extra_numbers={x for x in src if x.isdigit()}-{x for x in dst if x.isdigit()}
 extra_structural={x for x in src if x in structural}-{x for x in dst if x in structural}
 return bool(extra_numbers or extra_structural)

def resolve(reg,country,league):
 c=COUNTRY_MAP.get(country.upper(),country.title());cand=[r for r in reg if norm(r.country)==norm(c)]
 # Barriera di genere: una competizione esplicitamente femminile non deve mai
 # ricadere per fuzzy matching su una lega maschile (es. Serie A Women -> Serie A).
 female_markers=("women","woman","femmin","femmen","damer","dam","frauen","femen","kvenna")
 league_norm=norm(league);is_female=any(marker in league_norm for marker in female_markers)
 if is_female:
  female_cand=[r for r in cand if any(marker in norm(r.league_id)+norm(r.league) for marker in female_markers)]
  if not female_cand:return None
  cand=female_cand
 target=aliases(league)
 exact=[r for r in cand if norm(r.league) in target or aliases(r.league)&target]
 if len(exact)==1:return exact[0].league_id
 alias_matches=[r for r in cand if aliases(r.league)&target]
 if len(alias_matches)==1:return alias_matches[0].league_id
 nl=norm(league);fuzzy=[r for r in cand if (norm(r.league) in nl or nl in norm(r.league)) and not _has_competition_qualifier_gap(league,r.league)]
 if len(fuzzy)==1:return fuzzy[0].league_id
 country_prefix=norm(c);by_id=[]
 for r in cand:
  rid=norm(r.league_id);suffix=rid[len(country_prefix):] if rid.startswith(country_prefix) else rid
  if (suffix==nl or suffix in nl or nl in suffix) and not _has_competition_qualifier_gap(league,r.league):by_id.append(r)
 if len(by_id)==1:return by_id[0].league_id
 explicit={("austria","oberosterreich"):"Austria_Oberosterreich",("austria","regionalligaest"):"Austria_Regionalliga_East",("belgium","jupilerleague"):"Belgium_JupilerProLeague",("france","ligue3"):"France_National",("hungary","nbi"):"Hungary_NBI",("iceland","bestadeildfemminile"):"Iceland_BestaDeildKvenna",("italy","seriea"):"Italy_SerieA",("iceland","bestadeildfemminileplayoffschampionship"):"Iceland_BestaDeildKvenna",("latvia","1liga"):"Latvia_NakotnesLiga",("norway","division2gruppo1"):"Norway_2ndDivision_Group1",("norway","division2gruppo2"):"Norway_2ndDivision_Group2"}
 wanted=explicit.get((norm(c),nl));return wanted if wanted and any(r.league_id==wanted for r in cand) else None
def _competition_markers(value):
 raw=unicodedata.normalize("NFKD",value).encode("ascii","ignore").decode().casefold()
 n=norm(value)
 markers=set()
 if any(x in n for x in ("women","woman","femmin","femmen","damer","frauen","femen","kvenna")) or re.search(r"(?:^|[\s._/-])d(?:$|[\s._/-])",raw):markers.add("female")
 if re.search(r"(?:u|under)(?:18|19|20|21|23)",n):markers.add("youth")
 if any(x in n for x in ("reserve","reserves","primavera","nextpro")):markers.add("reserve")
 return markers
def _exact_league_match(reg,country,league):
 c=COUNTRY_MAP.get(country.upper(),country.title())
 candidates=[r for r in reg if norm(r.country)==norm(c)]
 nl=norm(league)
 exact=[r for r in candidates if norm(r.league)==nl]
 return exact[0].league_id if len(exact)==1 else None

def resolve_match(reg,country,league,home,away):
 c=COUNTRY_MAP.get(country.upper(),country.title())
 mapped=resolve_team_mapping(reg,c,home,away)
 if mapped:return mapped
 # Se una competizione e' suddivisa in gruppi/serie documentati ma le due
 # squadre non convergono sullo stesso LeagueId, non forzare un fuzzy match.
 groups=load_team_mappings()
 h=groups.get(norm(home),set());a=groups.get(norm(away),set())
 if h or a:
  country_ids={r.league_id for r in reg if norm(r.country)==norm(c)}
  if (h|a)&country_ids:return None

 # Un Country+League esatto nel registry e' autoritativo: U19/U21/U23/Reserve
 # possono essere squadre legittime di campionati senior inferiori.
 exact_lid=_exact_league_match(reg,country,league)
 lid=exact_lid or resolve(reg,country,league)
 if not lid:return None

 target=next((r for r in reg if r.league_id==lid),None)
 league_markers=_competition_markers(league)
 target_markers=_competition_markers(lid)|(_competition_markers(target.league) if target else set())

 # La barriera female resta sempre attiva: una sorgente esplicitamente
 # femminile non puo' ricadere su una competizione maschile.
 if "female" in league_markers-target_markers:return None

 # Solo sui mapping non esatti usiamo i marker delle squadre come cintura di
 # sicurezza contro associazioni fuzzy tra senior e youth/reserve.
 if not exact_lid:
  source_markers=league_markers|_competition_markers(home)|_competition_markers(away)
  if source_markers-target_markers:return None

 # MLS senior: Flashscore puo' mescolare partite MLS Next Pro sotto un'etichetta
 # troppo generica. Questa protezione provider-specifica resta esplicita.
 if lid=="USA_MLS":
  n_home,n_away=norm(home),norm(away)
  raw_home,raw_away=home.casefold(),away.casefold()
  if re.search(r"(?:\\s|^)(?:2|ii)$",raw_home) or re.search(r"(?:\\s|^)(?:2|ii)$",raw_away):
   return None
  mls_next_pro_affiliates={"venturacounty","connecticutfc"}
  if n_home in mls_next_pro_affiliates or n_away in mls_next_pro_affiliates:
   return None
 return lid
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
def score_from_tokens(tokens,compact=False):
 if not tokens:return None
 first=tokens[0]
 # Nel formato Flashscore standard "35" significa 3-5; nei blocchi
 # alternativi/Kolmonen lo stesso token può essere il testo "3-5" collassato.
 if compact and len(first)==2 and first.isdigit():return first[0],first[1]
 if len(tokens)>=2 and len(first)==1 and len(tokens[1])==2 and tokens[1].isdigit():
  return tokens[1][0],tokens[1][1]
 if len(tokens)>=2 and first.isdigit() and tokens[1].isdigit():
  return first,tokens[1]
 return None
def collect_score_tokens(lines,start,limit=6):
 tokens=[];k=start
 while k<len(lines) and k<start+limit:
  value=lines[k]
  if value in STATUS or value=="Kolmonen" or parse_date(value,datetime.now().year):break
  if INT_RE.match(value):tokens.append(value)
  elif tokens:break
  k+=1
 return tokens,k
def parse_standard(lines,mode,reg,year,fallback_date):
 out=[];unresolved=set();current_date=fallback_date;league=country=None;current_round="";i=0
 while i<len(lines):
  line=lines[i]
  # I blocchi Kolmonen hanno un formato autonomo. Azzera il contesto standard
  # per evitare che vengano attribuiti all'ultima lega Flashscore precedente.
  if line=="Kolmonen":
   # Il resto del testo può contenere solo blocchi Kolmonen: il parser
   # dedicato li leggerà separatamente. Uscire evita qualsiasi ereditarietà
   # dell'ultima lega standard.
   break
  d=parse_date(line,year)
  if d:current_date=d;i+=1;continue
  rm=ROUND_RE.match(line)
  if rm:current_round=rm.group(1);i+=1;continue
  if line.endswith(":"):country=line[:-1].strip();i+=1;continue
  if line in IGNORE or line.startswith("mostra partite") or line=="SRF":i+=1;continue
  if i+1<len(lines) and lines[i+1].endswith(":"):league=line;i+=1;continue
  historical_date=parse_dated_time(line,year) if mode=="results" else None
  if historical_date and league and country:
   home,j=dedupe_pair(lines,i+1);away,j=dedupe_pair(lines,j)
   tokens,k=collect_score_tokens(lines,j)
   score=score_from_tokens(tokens,compact=True);lid=resolve_match(reg,country,league,home,away)
   if score:
    if lid:out.append(Match(lid,historical_date,home,away,score[0],score[1],"Finale","",current_round))
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
   tokens,k=collect_score_tokens(lines,j)
   score=score_from_tokens(tokens,compact=True)
   if status not in SKIP_STATUS and score:
    notes="ET" if status=="Dopo Suppl." else ("PEN" if status=="Dopo Rigori" else "")
    if lid:out.append(Match(lid,current_date,home,away,score[0],score[1],"Finale",notes,current_round))
    else:unresolved.add((country,league))
   i=max(k,j);continue
  i+=1
 return out,unresolved
def parse_kolmonen(lines,mode,reg,year):
 out=[];unresolved=set();i=0
 while i<len(lines):
  if i+5>=len(lines) or lines[i]!="Kolmonen" or not lines[i+1].startswith("Kolmonen,"):
   i+=1;continue
  league=lines[i+1].replace(","," ").replace("  "," ").strip()
  d=parse_date(lines[i+4],year);marker=lines[i+5];lid=resolve(reg,"Finland",league)
  # Il blocco termina al prossimo "Kolmonen" oppure dopo un piccolo margine.
  end=i+6
  while end<len(lines) and end<i+16 and lines[end]!="Kolmonen":end+=1
  block=lines[i+6:end]
  if not d or not lid:
   if not lid:unresolved.add(("Finland",league))
   i=max(end,i+1);continue
  if len(block)<2:
   i=max(end,i+1);continue
  # Prima dei punteggi ci sono home/alias e away/alias. Gli alias possono
  # coincidere col nome oppure essere diversi: per il CSV usiamo il primo
  # nome visualizzato di ciascuna squadra.
  numpos=next((n for n,v in enumerate(block) if INT_RE.match(v)),None)
  if numpos is None:
   i=max(end,i+1);continue
  names=block[:numpos];tokens=[v for v in block[numpos:] if INT_RE.match(v)]
  if len(names)>=4:
   home=dedupe_name(names[0]);away=dedupe_name(names[2])
  elif len(names)>=2:
   home=dedupe_name(names[0]);away=dedupe_name(names[1])
  else:
   i=max(end,i+1);continue
  if mode=="rank" and TIME_RE.match(marker):
   out.append(Match(lid,d,home,away))
  elif mode=="results" and marker in {"FT","Finale"}:
   # Nel dump Kolmonen esistono due forme:
   #   22 / 00  => FT 2-2, poi HT 0-0
   #   4 / 2    => FT 4-2
   if len(tokens)>=2 and len(tokens[0])==2 and len(tokens[1])==2:
    score=(tokens[0][0],tokens[0][1])
   else:
    score=score_from_tokens(tokens,compact=False)
   if score:out.append(Match(lid,d,home,away,score[0],score[1],"Finale",""))
  i=max(end,i+1)
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
