"""Importa lo storico Serie D attraverso append_results, senza creare pronostici passati.

Dopo aver eseguito import_storico_serie_d --write:
  python -m tools.applica_storico_serie_d
  python -m tools.applica_storico_serie_d --apply
"""
from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from collections import Counter
from pathlib import Path

from gioover25.registry import load_league_registry
from gioover25.history import read_results_file
from gioover25.team_names import normalize_team_name
from tools.prepare_input import ROOT

FIELDS = ["LeagueId", "Round", "MatchDate", "Home", "Away", "HG", "AG", "Status", "Notes"]


def key(row):
    lid = row["LeagueId"].strip()
    return (lid, row["MatchDate"].strip(),
            normalize_team_name(lid, row["Home"]),
            normalize_team_name(lid, row["Away"]))


def prepare(proposal_dir: Path, archive_dir: Path, registry):
    paths = sorted(proposal_dir.glob("proposta_serie_d_girone_?.csv"))
    if len(paths) != 9:
        raise ValueError(f"Attesi 9 CSV di proposta, trovati {len(paths)}")
    rows, seen = [], {}
    for path in paths:
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            if not set(FIELDS) <= set(reader.fieldnames or []):
                raise ValueError(f"Colonne mancanti: {path}")
            for row in reader:
                lid = row["LeagueId"].strip()
                if lid not in registry or not lid.startswith("Italy_SerieD_Girone"):
                    raise ValueError(f"LeagueId non valido: {lid}")
                if row["Status"].strip().upper() not in {"FINALE", "FINAL", "FT"}:
                    raise ValueError(f"Stato non finale: {lid} {row['MatchDate']}")
                if not (row["HG"].strip().isdigit() and row["AG"].strip().isdigit()):
                    raise ValueError(f"Risultato non numerico: {lid} {row['MatchDate']}")
                k = key(row)
                if k in seen:
                    raise ValueError(f"Partita duplicata nelle proposte: {k}")
                seen[k] = row
                rows.append(row)
    if len({row["LeagueId"] for row in rows}) != 9:
        raise ValueError("Le proposte non coprono tutti e nove i gironi")
    new = []
    existing_count = 0
    for lid in sorted({r["LeagueId"] for r in rows}):
        path = archive_dir / f"{lid}.csv"
        old = {}
        if path.exists():
            for match in read_results_file(path):
                k = (lid, match.date,
                     normalize_team_name(lid, match.home),
                     normalize_team_name(lid, match.away))
                if k in old:
                    raise ValueError(f"Duplicato nello storico: {k}")
                old[k] = (str(match.home_goals), str(match.away_goals))
        for row in (r for r in rows if r["LeagueId"] == lid):
            k = key(row)
            if k in old:
                if old[k] != (row["HG"], row["AG"]):
                    raise ValueError(f"CONFLITTO RISULTATO: {k}: storico={old[k]}, proposta={row['HG']}-{row['AG']}")
                existing_count += 1
            else:
                new.append(row)
    return new, existing_count, len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal-dir", type=Path, default=ROOT / "data/debug/storico_serie_d")
    parser.add_argument("--apply", action="store_true", help="Esegue davvero append_results")
    args = parser.parse_args()
    registry = load_league_registry(ROOT / "data/league_registry.csv")
    try:
        new, already, total = prepare(args.proposal_dir, ROOT / "data/storico/risultati", registry)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"[SERIE D] Proposte={total} | già presenti={already} | da importare={len(new)}")
    if not new:
        print("[SERIE D] Nessuna nuova partita: nessuna modifica")
        return
    if not args.apply:
        print("[DRY-RUN] Nessuna modifica. Per importare: aggiungere --apply")
        return
    stage = ROOT / "data/debug/storico_serie_d/input_importazione_verificato.csv"
    stage.parent.mkdir(parents=True, exist_ok=True)
    with stage.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(new)
    print(f"[SERIE D] Importazione con pipeline ufficiale append_results: {stage}", flush=True)
    completed = subprocess.run([sys.executable, "-m", "gioover25.append_results", str(stage)],
                               cwd=ROOT, check=False)
    if completed.returncode:
        raise SystemExit(f"[ERRORE] append_results terminato con codice {completed.returncode}; verificare gli archivi")
    print("[SERIE D] Importazione terminata. Nessun ranking storico creato retroattivamente.")


if __name__ == "__main__":
    main()
