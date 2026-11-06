"""Bonifica conservativa degli storici e ranking VG1.2/1.3/1.4.

Per ciascuna variante conserva solo le selezioni incrementali:
score nella finestra e partita NON ALTA nello storico VG1 originale.
Default: sola anteprima. --apply crea backup e riscrive i CSV.
"""
from __future__ import annotations
import argparse
import csv
import shutil
from datetime import datetime
from pathlib import Path
from gioover25.team_names import normalize_team_name

ROOT=Path("data")
BANDS={"vg1.2":(65.0,70.0),"vg1.3":(68.0,72.0),"vg1.4":(65.0,72.0)}

def read(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        rd=csv.DictReader(f,delimiter=";")
        return list(rd.fieldnames or []),list(rd)

def key(r):
    league=r.get("LeagueId","").strip()
    return (league,r.get("MatchDate","").strip(),
            normalize_team_name(league,r.get("Home","")),
            normalize_team_name(league,r.get("Away","")))

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--apply",action="store_true",help="Esegue dopo anteprima; backup obbligatorio")
    args=parser.parse_args()
    vg_path=ROOT/"storico/ranking/vg1/storico_ranking_vg1.csv"
    if not vg_path.exists():
        raise SystemExit(f"Storico VG1 necessario per la bonifica: {vg_path}")
    _,base=read(vg_path)
    lookup={}
    for row in base:
        k=key(row)
        if k in lookup and lookup[k].get("Band")!=row.get("Band"):
            raise SystemExit(f"VG1 contiene fasce discordanti: {k}")
        lookup[k]=row
    files=[]
    for engine in BANDS:
        files.extend(sorted((ROOT/"storico/ranking"/engine).glob("storico_ranking_*.csv")))
        files.extend(sorted((ROOT/"output_ranking"/engine).glob("*.csv")))
    planned=[]
    for path in files:
        fields,rows=read(path)
        if not fields or "Score" not in fields or "Band" not in fields:
            raise SystemExit(f"Formato inatteso: {path}")
        engine=path.parent.name
        lo,hi=BANDS[engine]
        keep=[]
        missing=[]
        seen=set()
        for r in rows:
            try: score=float(r.get("Score",""))
            except (ValueError,TypeError):continue
            if not lo<=score<hi:continue
            base_row=lookup.get(key(r))
            if base_row is None:
                missing.append(key(r));continue
            if base_row.get("Band","").strip().upper()=="ALTA":continue
            if key(r) in seen:continue
            seen.add(key(r))
            # Only selected entries remain. Preserve scores, results and prediction snapshots.
            r["Band"]="ALTA"
            keep.append(r)
        if missing:
            raise SystemExit(f"Bonifica BLOCCATA: {path}: {len(missing)} partite senza riferimento VG1, es. {missing[:3]}")
        planned.append((path,fields,rows,keep))
        print(f"[AUDIT] {path}: prima={len(rows)} dopo={len(keep)} escluse={len(rows)-len(keep)}")
    if not args.apply:
        print("[DRY RUN] Nessun file modificato. Per applicare: --apply")
        return
    backup=ROOT/"backup_bonifica_vg1"/datetime.now().strftime("%Y%m%d-%H%M%S")
    for path,fields,rows,keep in planned:
        destination=backup/path
        destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(path,destination)
    for path,fields,rows,keep in planned:
        tmp=path.with_suffix(path.suffix+".tmp")
        with tmp.open("w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields,delimiter=";",extrasaction="ignore")
            w.writeheader();w.writerows(keep)
        tmp.replace(path)
    print(f"[DONE] Bonifica completata. Backup integrale: {backup}")

if __name__=="__main__":
    main()
