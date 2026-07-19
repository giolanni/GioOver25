"""
===============================================================================
GioOver2.5 - analysis/laboratory/candidate_rules.py
===============================================================================

SCOPO
-----
Generare il report 05 del Laboratory con due categorie di regole candidate:

1. REGOLE SEMPLICI

       Driver <= soglia
       Driver >= soglia

2. REGOLA COMPOSTA SULLA FORMA RECENTE

       HomePPGLast5 <= soglia
       AND
       AwayPPGLast5 <= soglia

La seconda regola rappresenta esattamente l'ipotesi da verificare:
quando entrambe le squadre hanno raccolto pochi punti nelle ultime cinque
partite, la gara potrebbe avere una probabilità maggiore di terminare KO
rispetto all'Over 2.5.

IMPORTANTE
----------
Questo script non modifica alcun engine e non applica penalità.
Si limita a misurare il comportamento delle quattro popolazioni ufficiali:

    ALTA_OK
    ALTA_KO
    MEDIA_OK
    MEDIA_KO

INPUT
-----
    analysis/laboratory/data/02_drivers.csv

OUTPUT
------
    analysis/laboratory/data/05_candidate_rules.csv

COMPATIBILITÀ
-------------
Le regole semplici conservano il formato già utilizzato dal Laboratory.
Le nuove colonne descrittive vengono aggiunte in coda e non modificano i dati
esistenti.
===============================================================================
"""

# `defaultdict` consente di raggruppare facilmente i valori per driver.
from collections import defaultdict

# `Path` gestisce i percorsi in modo compatibile con Windows e Linux.
from pathlib import Path

# `csv` serve per leggere e scrivere i file separati da punto e virgola.
import csv


# File prodotto dal report 02 del Laboratory.
INPUT = Path("analysis/laboratory/data/02_drivers.csv")

# File di destinazione del report 05.
OUTPUT = Path("analysis/laboratory/data/05_candidate_rules.csv")

# Nome dei due driver coinvolti nell'ipotesi specifica da verificare.
HOME_RECENT_PPG_DRIVER = "HomePPGLast5"
AWAY_RECENT_PPG_DRIVER = "AwayPPGLast5"


# Intestazione unica del file di output.
# Le prime colonne mantengono il vecchio formato; quelle finali descrivono
# esplicitamente le regole composte.
OUTPUT_FIELDNAMES = [
    "RuleType",
    "Driver",
    "Operator",
    "Threshold",
    "SecondDriver",
    "SecondOperator",
    "SecondThreshold",
    "RuleDescription",
    "Occurrences",
    "ALTA_OK",
    "ALTA_KO",
    "MEDIA_OK",
    "MEDIA_KO",
    "AltaHit",
    "MediaHit",
]


def to_float(value):
    """
    Converte un valore CSV in numero decimale.

    Viene accettata sia la virgola sia il punto come separatore decimale.
    Se il valore non è numerico viene restituito `None`, così la singola riga
    sporca non interrompe l'intera elaborazione.
    """
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def empty_counters():
    """Crea i contatori delle quattro popolazioni ufficiali del Laboratory."""
    return {
        "ALTA_OK": 0,
        "ALTA_KO": 0,
        "MEDIA_OK": 0,
        "MEDIA_KO": 0,
    }


def group_key(row):
    """Costruisce una chiave come `ALTA_OK` partendo da Band e Outcome."""
    return f'{row["Band"]}_{row["Outcome"]}'


def build_rule_result(
    *,
    rule_type,
    driver,
    operator,
    threshold,
    counters,
    occurrences,
    second_driver="",
    second_operator="",
    second_threshold="",
    description="",
):
    """
    Costruisce una riga uniforme del report 05.

    Oltre ai conteggi calcola:

    - `AltaHit`: ALTA_OK / (ALTA_OK + ALTA_KO)
    - `MediaHit`: MEDIA_OK / (MEDIA_OK + MEDIA_KO)

    Se una fascia non contiene partite, la relativa precisione resta vuota.
    """
    alta_total = counters["ALTA_OK"] + counters["ALTA_KO"]
    media_total = counters["MEDIA_OK"] + counters["MEDIA_KO"]

    return {
        "RuleType": rule_type,
        "Driver": driver,
        "Operator": operator,
        "Threshold": threshold,
        "SecondDriver": second_driver,
        "SecondOperator": second_operator,
        "SecondThreshold": second_threshold,
        "RuleDescription": description,
        "Occurrences": occurrences,
        **counters,
        "AltaHit": (
            round(counters["ALTA_OK"] / alta_total, 4)
            if alta_total
            else ""
        ),
        "MediaHit": (
            round(counters["MEDIA_OK"] / media_total, 4)
            if media_total
            else ""
        ),
    }


def read_driver_rows():
    """
    Legge `02_drivers.csv` e restituisce solo le righe con valore numerico.

    Ogni riga conserva MatchId, Driver, Value, Band e Outcome. `MatchId` è
    fondamentale per ricostruire sulla stessa partita HomePPGLast5 e
    AwayPPGLast5.
    """
    rows = []

    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")

        required = {"MatchId", "Driver", "Value", "Band", "Outcome"}
        missing = required.difference(reader.fieldnames or [])

        if missing:
            raise ValueError(
                "02_drivers.csv non valido. Mancano le colonne: "
                + ", ".join(sorted(missing))
            )

        for raw_row in reader:
            value = to_float(raw_row.get("Value"))

            if value is None:
                continue

            rows.append({
                "MatchId": str(raw_row.get("MatchId", "")).strip(),
                "Driver": str(raw_row.get("Driver", "")).strip(),
                "Value": value,
                "Band": str(raw_row.get("Band", "")).strip().upper(),
                "Outcome": str(raw_row.get("Outcome", "")).strip().upper(),
            })

    return rows


def generate_simple_rules(rows):
    """
    Genera le regole semplici già presenti nel Laboratory.

    Per ogni driver vengono provate tutte le soglie osservate e, per ciascuna,
    entrambe le direzioni `<=` e `>=`.
    """
    driver_values = defaultdict(list)

    for row in rows:
        driver_values[row["Driver"]].append(row["Value"])

    rules = []

    for driver, values in driver_values.items():
        thresholds = sorted(set(values))
        driver_rows = [row for row in rows if row["Driver"] == driver]

        for threshold in thresholds:
            for operator in ("<=", ">="):
                counters = empty_counters()
                occurrences = 0

                for row in driver_rows:
                    matches = (
                        row["Value"] <= threshold
                        if operator == "<="
                        else row["Value"] >= threshold
                    )

                    if not matches:
                        continue

                    occurrences += 1
                    key = group_key(row)

                    if key in counters:
                        counters[key] += 1

                if not occurrences:
                    continue

                rules.append(build_rule_result(
                    rule_type="SINGLE",
                    driver=driver,
                    operator=operator,
                    threshold=threshold,
                    counters=counters,
                    occurrences=occurrences,
                    description=f"{driver} {operator} {threshold}",
                ))

    return rules


def build_match_driver_index(rows):
    """
    Ricostruisce una sola riga logica per ogni partita.

    `02_drivers.csv` è in formato lungo: ogni MatchId compare una volta per
    ciascun driver. Questa funzione trasforma quel formato in un indice simile:

        indice[MatchId]["HomePPGLast5"] = 0.40
        indice[MatchId]["AwayPPGLast5"] = 0.60

    Band e Outcome vengono conservati una sola volta per partita.
    """
    match_index = {}

    for row in rows:
        match_id = row["MatchId"]

        if match_id not in match_index:
            match_index[match_id] = {
                "Band": row["Band"],
                "Outcome": row["Outcome"],
                "Drivers": {},
            }

        match_index[match_id]["Drivers"][row["Driver"]] = row["Value"]

    return match_index


def generate_both_teams_low_ppg_rules(rows):
    """
    Genera le regole che verificano la vera ipotesi dell'esperimento.

    Una partita viene inclusa quando entrambe le condizioni sono vere:

        HomePPGLast5 <= soglia
        AwayPPGLast5 <= soglia

    Le soglie provate sono tutti i valori osservati nei due driver. In questo
    modo il Laboratory può trovare il punto esatto in cui la precisione cambia,
    senza imporre in anticipo soglie arbitrarie come 0.60 o 0.80.
    """
    match_index = build_match_driver_index(rows)

    eligible_matches = []
    observed_values = set()

    for match_id, match_data in match_index.items():
        drivers = match_data["Drivers"]

        home_ppg = drivers.get(HOME_RECENT_PPG_DRIVER)
        away_ppg = drivers.get(AWAY_RECENT_PPG_DRIVER)

        # La partita è confrontabile solo quando entrambi i valori esistono.
        if home_ppg is None or away_ppg is None:
            continue

        eligible_matches.append({
            "MatchId": match_id,
            "Band": match_data["Band"],
            "Outcome": match_data["Outcome"],
            "HomePPGLast5": home_ppg,
            "AwayPPGLast5": away_ppg,
        })

        observed_values.add(home_ppg)
        observed_values.add(away_ppg)

    rules = []

    for threshold in sorted(observed_values):
        counters = empty_counters()
        occurrences = 0

        for match in eligible_matches:
            if not (
                match["HomePPGLast5"] <= threshold
                and match["AwayPPGLast5"] <= threshold
            ):
                continue

            occurrences += 1
            key = f'{match["Band"]}_{match["Outcome"]}'

            if key in counters:
                counters[key] += 1

        if not occurrences:
            continue

        rules.append(build_rule_result(
            rule_type="COMPOUND_AND",
            driver=HOME_RECENT_PPG_DRIVER,
            operator="<=",
            threshold=threshold,
            second_driver=AWAY_RECENT_PPG_DRIVER,
            second_operator="<=",
            second_threshold=threshold,
            counters=counters,
            occurrences=occurrences,
            description=(
                f"{HOME_RECENT_PPG_DRIVER} <= {threshold} AND "
                f"{AWAY_RECENT_PPG_DRIVER} <= {threshold}"
            ),
        ))

    return rules


def generate_candidate_rules():
    """Coordina lettura, generazione delle regole e scrittura del report 05."""
    if not INPUT.exists():
        raise FileNotFoundError(f"File Laboratory non trovato: {INPUT}")

    rows = read_driver_rows()

    simple_rules = generate_simple_rules(rows)
    compound_rules = generate_both_teams_low_ppg_rules(rows)
    rules = simple_rules + compound_rules

    # Ordinamento deterministico: prima le regole semplici, poi quelle composte.
    rules.sort(key=lambda item: (
        item["RuleType"],
        item["Driver"],
        item["SecondDriver"],
        item["Operator"],
        float(item["Threshold"]),
    ))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=OUTPUT_FIELDNAMES,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rules)

    print(f"{len(simple_rules)} regole semplici generate")
    print(f"{len(compound_rules)} regole PPG composte generate")
    print(f"{len(rules)} regole candidate totali")
    print(f"Report scritto: {OUTPUT.resolve()}")


def main():
    """Punto di ingresso usato da `python -m analysis.laboratory.run_all`."""
    generate_candidate_rules()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
