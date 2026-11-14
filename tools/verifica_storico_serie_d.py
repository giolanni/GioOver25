"""Confronta le proposte Serie D con un CSV risultati esistente; non modifica l'originale.

python -m tools.verifica_storico_serie_d --existing data/input_partite/risultati.csv
python -m tools.verifica_storico_serie_d --existing PERCORSO_REALE --write
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

from tools.import_storico_diretta import FIELDS
from tools.prepare_input import ROOT, norm


def read_csv(path: Path):
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def identity(row):
    return (row["LeagueId"].strip(), row["MatchDate"].strip(),
            norm(row["Home"]), norm(row["Away"]))


def result(row):
    return ((row.get("HG") or "").strip(), (row.get("AG") or "").strip())


def reconcile(proposals, existing):
    known = {}
    duplicates = []
    for row in existing:
        key = identity(row)
        if key in known:
            duplicates.append(("ESISTENTE_DUPLICATO", row))
        else:
            known[key] = row
    seen = {}
    report, missing = [], []
    for row in proposals:
        key = identity(row)
        if key in seen:
            status = "PROPOSTA_DUPLICATA"
        elif key not in known:
            status = "NUOVA"
            missing.append(row)
        elif result(known[key]) == result(row):
            status = "GIA_PRESENTE"
        elif all(result(known[key])):
            status = "CONFLITTO_RISULTATO"
        else:
            status = "ESISTENTE_SENZA_RISULTATO"
        seen[key] = row
        report.append({"Esito": status, "LeagueId": row["LeagueId"],
                       "MatchDate": row["MatchDate"], "Home": row["Home"],
                       "Away": row["Away"], "HG_Proposta": row["HG"],
                       "AG_Proposta": row["AG"],
                       "HG_Esistente": result(known[key])[0] if key in known else "",
                       "AG_Esistente": result(known[key])[1] if key in known else ""})
    for _, row in duplicates:
        report.append({"Esito": "ESISTENTE_DUPLICATO", "LeagueId": row["LeagueId"],
                       "MatchDate": row["MatchDate"], "Home": row["Home"],
                       "Away": row["Away"], "HG_Proposta": "", "AG_Proposta": "",
                       "HG_Esistente": result(row)[0], "AG_Esistente": result(row)[1]})
    return report, missing


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--existing", type=Path, default=ROOT / "data/storico/risultati",
                        help="Cartella degli storici per lega o singolo CSV (sola lettura)")
    parser.add_argument("--proposal-dir", type=Path, default=ROOT / "data/debug/storico_serie_d")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "data/debug/verifica_serie_d")
    parser.add_argument("--write", action="store_true", help="Esporta report e sole nuove partite")
    args = parser.parse_args()
    if not args.existing.is_file():
        parser.error(f"CSV esistente non trovato: {args.existing}")
    paths = sorted(args.proposal_dir.glob("proposta_serie_d_girone_?.csv"))
    if len(paths) != 9:
        parser.error(f"Attesi 9 CSV di proposta in {args.proposal_dir}; trovati {len(paths)}. "
                     "Eseguire prima import_storico_serie_d --write")
    proposals = [r for path in paths for r in read_csv(path)]
    if args.existing.is_dir():
        expected = {f"{r['LeagueId']}.csv" for r in proposals}
        paths_existing = sorted(args.existing / name for name in expected)
        existing = [row for path in paths_existing if path.is_file() for row in read_csv(path)]
        print(f"[VERIFICA] Archivi per lega trovati: {sum(p.is_file() for p in paths_existing)}/{len(paths_existing)}")
    else:
        existing = read_csv(args.existing)
    required = {"LeagueId", "MatchDate", "Home", "Away", "HG", "AG"}
    if any(not required <= set(row) for row in proposals + existing):
        parser.error(f"Colonne richieste: {sorted(required)}")
    report, missing = reconcile(proposals, existing)
    counts = Counter(r["Esito"] for r in report)
    print(f"[VERIFICA] Proposte={len(proposals)} | Esistenti={len(existing)}")
    for status, count in sorted(counts.items()):
        print(f"[VERIFICA] {status}: {count}")
    blocking = {"CONFLITTO_RISULTATO", "PROPOSTA_DUPLICATA", "ESISTENTE_DUPLICATO",
                "ESISTENTE_SENZA_RISULTATO"}
    if any(counts[s] for s in blocking):
        print("[ATTENZIONE] Anomalie presenti: verificare il report prima di qualsiasi integrazione")
    if args.write:
        write_csv(args.output_dir / "confronto.csv", report,
                  ["Esito", "LeagueId", "MatchDate", "Home", "Away",
                   "HG_Proposta", "AG_Proposta", "HG_Esistente", "AG_Esistente"])
        write_csv(args.output_dir / "solo_nuove.csv", missing, FIELDS)
        print(f"[VERIFICA] Report e nuove partite in {args.output_dir}")
        print("[SICUREZZA] Nessun file ufficiale modificato; nessun ranking retroattivo")
    else:
        print("[DRY-RUN] Nessun file modificato")


if __name__ == "__main__":
    main()
