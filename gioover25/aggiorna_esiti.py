import argparse
import csv
from pathlib import Path


def calcola_esito_over25(risultato: str) -> str:
    valore = (risultato or "").strip().upper()

    if valore == "":
        return ""

    if valore in {"RINVIATA", "RINV", "POSTPONED", "ANNULLATA", "ANNULLATO"}:
        return "RINVIATA"

    separatori = ["-", "–", "—", ":"]

    for sep in separatori:
        if sep in valore:
            parti = valore.split(sep)

            if len(parti) != 2:
                return "ERRORE"

            try:
                gol_casa = int(parti[0].strip())
                gol_trasferta = int(parti[1].strip())
            except ValueError:
                return "ERRORE"

            return "OK" if gol_casa + gol_trasferta >= 3 else "KO"

    return "ERRORE"


def aggiorna_esiti(storico_file: str) -> None:
    storico_path = Path(storico_file)

    if not storico_path.exists():
        print(f"File storico non trovato: {storico_path}")
        return

    with open(storico_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if not rows:
        print("Storico vuoto.")
        return

    if "risultato" not in fieldnames:
        fieldnames.append("risultato")
        for row in rows:
            row["risultato"] = ""

    if "ESITO" not in fieldnames:
        fieldnames.append("ESITO")
        for row in rows:
            row["ESITO"] = ""

    aggiornate = 0
    errori = 0

    for row in rows:
        risultato = row.get("risultato", "").strip()
        esito_attuale = row.get("ESITO", "").strip()

        if risultato and not esito_attuale:
            esito = calcola_esito_over25(risultato)
            row["ESITO"] = esito

            if esito == "ERRORE":
                errori += 1
            else:
                aggiornate += 1

    with open(storico_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"File aggiornato: {storico_path.resolve()}")
    print(f"Righe aggiornate: {aggiornate}")
    print(f"Righe con errore risultato: {errori}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Aggiorna automaticamente ESITO nello storico GioOver2.5 partendo dalla colonna risultato."
    )
    parser.add_argument(
        "--storico",
        default="data/storico/storico_risultati.csv",
        help="Percorso file storico CSV"
    )

    args = parser.parse_args()
    aggiorna_esiti(args.storico)


if __name__ == "__main__":
    main()