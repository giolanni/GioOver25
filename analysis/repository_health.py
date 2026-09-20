"""Controllo leggero della dimensione dei file del repository GioOver25."""
from __future__ import annotations
import argparse
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SKIP_DIRS={".git",".venv","__pycache__"}
def human_size(n):
 v=float(n)
 for u in ("B","KB","MB","GB"):
  if v<1024 or u=="GB": return f"{v:.1f} {u}"
  v/=1024
def scan():
 out=[]
 for p in ROOT.rglob("*"):
  if p.is_file() and not any(x in SKIP_DIRS for x in p.parts):
   try: out.append((p.stat().st_size,p))
   except OSError: pass
 return sorted(out,reverse=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--warn-mb",type=float,default=5.0);ap.add_argument("--top",type=int,default=20);a=ap.parse_args()
 files=scan(); threshold=int(a.warn_mb*1024*1024)
 total=sum(s for s,_ in files); data=sum(s for s,p in files if "data" in p.relative_to(ROOT).parts)
 ar=ROOT/"data"/"archive"; archive=sum(p.stat().st_size for p in ar.rglob("*") if p.is_file()) if ar.exists() else 0
 print("="*72);print("GIOOVER25 - REPOSITORY HEALTH");print("="*72)
 print(f"File analizzati: {len(files)}");print(f"Working tree: {human_size(total)}");print(f"data/: {human_size(data)}");print(f"data/archive/: {human_size(archive)} (locale, ignorata da Git)")
 warnings=[x for x in files if x[0]>=threshold]
 print(f"\n[{'WARN' if warnings else 'OK'}] File oltre {a.warn_mb:g} MB: {len(warnings)}")
 for s,p in warnings: print(f"  {human_size(s):>10}  {p.relative_to(ROOT)}")
 print(f"\nTop {min(a.top,len(files))} file più grandi:")
 for s,p in files[:a.top]: print(f"  {human_size(s):>10}  {p.relative_to(ROOT)}")
 if ar.exists():
  print("\nArchivio per anno:")
  for y in sorted(p for p in ar.iterdir() if p.is_dir()):
   size=sum(p.stat().st_size for p in y.rglob("*") if p.is_file());print(f"  {y.name}: {human_size(size)}")
 return 1 if warnings else 0
if __name__=="__main__": raise SystemExit(main())
