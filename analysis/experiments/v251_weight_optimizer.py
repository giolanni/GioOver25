"""
===============================================================================
GioOver2.5 - v251_weight_optimizer.py
===============================================================================

SCOPO
-----
Questo script misura retroattivamente l'effetto di pesi diversi applicati alle
micro-correzioni sperimentali della v251.

La v25 rimane la baseline stabile.
La v251 rimane l'engine sperimentale realmente eseguito.
Questo script NON modifica nessun engine e NON riscrive gli storici ranking.

Lo script:

1. legge lo storico ranking v25;
2. legge lo storico ranking v251;
3. abbina le stesse partite presenti nei due file;
4. recupera dal campo Reason della v251 i segnali diagnostici:
   - StrongDefense;
   - RecentForm;
   - Restart;
   - eventuali bonus futuri;
5. prova automaticamente molte combinazioni di pesi;
6. ricalcola Score e Band in modo virtuale;
7. misura:
   - ALTA OK;
   - ALTA KO;
   - precisione ALTA;
   - copertura ALTA;
   - KO evitati rispetto alla v25;
   - OK persi rispetto alla v25;
   - ProtectiveBalance = KO evitati - OK persi;
   - MEDIA OK e KO;
8. salva una classifica delle configurazioni;
9. produce il dettaglio delle partite cambiate dalla configurazione migliore.

IMPORTANTE
----------
Lo script utilizza soltanto partite concluse con Over25 valorizzato come OK o KO.

I bonus sono già supportati dall'architettura, ma non vengono inventati.
Entreranno nella simulazione soltanto quando il Reason della v251 conterrà
diagnostiche positive esplicite, per esempio:

    StrongAttack=1.00
    RecentFormBonus=1.00
    RestartBonus=1.00

Finché tali segnali non esistono, i relativi pesi rimangono automaticamente
inattivi.

INPUT PREDEFINITI
-----------------
    data/storico/ranking/v25/storico_ranking_v25.csv
    data/storico/ranking/v251/storico_ranking_v251.csv

OUTPUT
------
    analysis/metrics/output/v251_weight_optimizer/
        01_weight_configurations.csv
        02_best_configuration_summary.csv
        03_best_configuration_changes.csv
        04_adjustment_activation_summary.csv
        05_optimizer_notes.txt

ESEMPI
------
Esecuzione standard:

    python -m analysis.metrics.v251_weight_optimizer

Escludendo le leghe australiane:

    python -m analysis.metrics.v251_weight_optimizer --exclude-australia

Con percorsi personalizzati:

    python -m analysis.metrics.v251_weight_optimizer ^
        --v25-file percorso\v25.csv ^
        --v251-file percorso\v251.csv

Con soglie fascia personalizzate:

    python -m analysis.metrics.v251_weight_optimizer ^
        --alta-threshold 75 ^
        --media-threshold 65

===============================================================================
"""

# argparse permette di gestire i parametri passati dalla riga di comando.
import argparse

# csv viene utilizzato per leggere e scrivere file separati da punto e virgola.
import csv

# itertools.product genera tutte le combinazioni possibili dei pesi.
from itertools import product

# pathlib.Path rende più sicura e leggibile la gestione dei percorsi.
from pathlib import Path

# re serve a estrarre i valori dal blocco V251_DIAGNOSTICS contenuto in Reason.
import re

# statistics.mean calcola medie senza dipendenze esterne.
from statistics import mean


# ---------------------------------------------------------------------------
# PERCORSI PREDEFINITI
# ---------------------------------------------------------------------------

# Storico ranking dell'engine stabile v25.
DEFAULT_V25_FILE = Path(
    "data/storico/ranking/v25/storico_ranking_v25.csv"
)

# Storico ranking dell'engine sperimentale v251.
DEFAULT_V251_FILE = Path(
    "data/storico/ranking/v251/storico_ranking_v251.csv"
)

# Cartella nella quale vengono scritti tutti i risultati dell'ottimizzazione.
DEFAULT_OUTPUT_DIR = Path(
    "analysis/metrics/output/v251_weight_optimizer"
)


# ---------------------------------------------------------------------------
# SOGLIE PREDEFINITE DELLE FASCE
# ---------------------------------------------------------------------------

# Una partita con Score uguale o superiore a questa soglia è FASCIA ALTA.
DEFAULT_ALTA_THRESHOLD = 75.0

# Una partita sotto ALTA ma uguale o superiore a questa soglia è FASCIA MEDIA.
DEFAULT_MEDIA_THRESHOLD = 65.0


# ---------------------------------------------------------------------------
# SPAZI DI RICERCA DEI PESI
# ---------------------------------------------------------------------------

# Pesi assoluti provati per ogni livello del segnale StrongDefense.
#
# Se nel Reason originale StrongDefense vale -2, significa che il segnale ha
# livello 2. Con peso 1.5 la penalità simulata diventa:
#
#     -2 * 1.5 = -3
#
# In questo modo conserviamo la distinzione tra difesa solida e molto solida.
STRONG_DEFENSE_WEIGHTS = (0.0, 0.5, 1.0, 1.5, 2.0)

# Pesi provati per il segnale RecentForm.
RECENT_FORM_WEIGHTS = (0.0, 0.5, 1.0, 1.5, 2.0)

# Pesi provati per il segnale Restart.
RESTART_WEIGHTS = (0.0, 0.5, 1.0, 1.5, 2.0)

# Penalità massime complessive provate.
#
# Il cap evita che la somma di più segnali deboli distrugga completamente
# il punteggio originale della v25.
MAX_TOTAL_PENALTIES = (2.0, 3.0, 4.0, 5.0, 6.0)

# Pesi predisposti per bonus futuri.
#
# Al momento il valore 0.0 mantiene i bonus disattivati.
# Quando il Laboratory definirà segnali positivi reali, sarà sufficiente
# ampliare queste tuple, ad esempio:
#
#     STRONG_ATTACK_BONUS_WEIGHTS = (0.0, 0.5, 1.0, 1.5)
#
STRONG_ATTACK_BONUS_WEIGHTS = (0.0,)
RECENT_FORM_BONUS_WEIGHTS = (0.0,)
RESTART_BONUS_WEIGHTS = (0.0,)


# ---------------------------------------------------------------------------
# CAMPI CHE IDENTIFICANO UNA PARTITA
# ---------------------------------------------------------------------------

# Questa chiave permette di abbinare la stessa prediction tra v25 e v251.
MATCH_KEY_FIELDS = (
    "MatchDate",
    "LeagueId",
    "Home",
    "Away",
)


# ---------------------------------------------------------------------------
# ESPRESSIONE REGOLARE PER LE DIAGNOSTICHE V251
# ---------------------------------------------------------------------------

# Cerca il contenuto racchiuso tra:
#
#     V251_DIAGNOSTICS[
#     ...
#     ]
#
DIAGNOSTIC_BLOCK_PATTERN = re.compile(
    r"V251_DIAGNOSTICS\[(.*?)\]",
    flags=re.IGNORECASE,
)


def text(value) -> str:
    """
    Converte un valore in testo pulito.

    Serve a evitare errori quando una cella CSV è vuota o vale None.
    """

    return str(value or "").strip()


def parse_float(value, default: float = 0.0) -> float:
    """
    Converte un valore in float.

    Se la conversione non è possibile, restituisce il valore di default.
    Accetta anche la virgola come separatore decimale.
    """

    raw = text(value).replace(",", ".")

    if not raw:
        return default

    try:
        return float(raw)
    except ValueError:
        return default


def read_csv_rows(path: Path) -> list[dict]:
    """
    Legge un CSV GioOver2.5 delimitato da punto e virgola.

    Restituisce una lista di dizionari, uno per ogni riga.
    """

    if not path.exists():
        raise FileNotFoundError(
            f"File non trovato: {path}"
        )

    with path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:

        reader = csv.DictReader(
            file_handle,
            delimiter=";",
        )

        if not reader.fieldnames:
            raise ValueError(
                f"Header assente nel file: {path}"
            )

        return list(reader)


def make_match_key(row: dict) -> tuple[str, ...]:
    """
    Costruisce la chiave univoca usata per abbinare v25 e v251.

    I nomi delle squadre vengono normalizzati in minuscolo per ridurre
    problemi dovuti soltanto a maiuscole o spazi.
    """

    return (
        text(row.get("MatchDate")),
        text(row.get("LeagueId")),
        " ".join(text(row.get("Home")).casefold().split()),
        " ".join(text(row.get("Away")).casefold().split()),
    )


def parse_diagnostics(reason: str) -> dict[str, float]:
    """
    Estrae le diagnostiche numeriche dal campo Reason della v251.

    Esempio di input:

        V251_DIAGNOSTICS[
            BaseScore=75.17;
            StrongDefense=-1.00;
            RecentForm=0.00;
            Restart=0.00;
            Total=-1.00
        ]

    Esempio di output:

        {
            "BaseScore": 75.17,
            "StrongDefense": -1.0,
            "RecentForm": 0.0,
            "Restart": 0.0,
            "Total": -1.0,
        }

    La funzione supporta automaticamente anche futuri segnali bonus.
    """

    match = DIAGNOSTIC_BLOCK_PATTERN.search(
        text(reason)
    )

    if not match:
        return {}

    values = {}

    # Il contenuto viene diviso sulle occorrenze del punto e virgola.
    for item in match.group(1).split(";"):

        # Le parti prive del simbolo "=" non rappresentano una coppia chiave-valore.
        if "=" not in item:
            continue

        key, raw_value = item.split(
            "=",
            maxsplit=1,
        )

        clean_key = text(key)

        if not clean_key:
            continue

        values[clean_key] = parse_float(
            raw_value,
            default=0.0,
        )

    return values


def score_to_band(
    score: float,
    alta_threshold: float,
    media_threshold: float,
) -> str:
    """
    Converte uno Score nella fascia corrispondente.

    Le tre possibili fasce sono:
    - ALTA;
    - MEDIA;
    - BASSA.

    BASSA indica una partita sotto la soglia operativa della fascia MEDIA.
    """

    if score >= alta_threshold:
        return "ALTA"

    if score >= media_threshold:
        return "MEDIA"

    return "BASSA"


def build_dataset(
    v25_rows: list[dict],
    v251_rows: list[dict],
    exclude_australia: bool,
) -> list[dict]:
    """
    Costruisce il dataset comune tra v25 e v251.

    Vengono mantenute soltanto:
    - partite presenti in entrambi gli storici;
    - partite concluse con Over25 uguale a OK oppure KO;
    - partite non australiane quando è attivo --exclude-australia.

    Per ogni riga vengono estratti anche i livelli dei segnali sperimentali.
    """

    # Indicizza la v251 per chiave partita, così l'abbinamento è rapido.
    v251_index = {
        make_match_key(row): row
        for row in v251_rows
    }

    dataset = []

    for v25_row in v25_rows:

        key = make_match_key(
            v25_row
        )

        v251_row = v251_index.get(
            key
        )

        # Se la partita non esiste nella v251, non è confrontabile.
        if v251_row is None:
            continue

        league_id = text(
            v25_row.get("LeagueId")
        )

        # Esclude le leghe australiane quando richiesto.
        if (
            exclude_australia
            and league_id.startswith("Australia_")
        ):
            continue

        # Cerca il risultato prima nella v25 e poi nella v251.
        result = (
            text(v25_row.get("Over25")).upper()
            or text(v251_row.get("Over25")).upper()
        )

        # Le partite senza esito non devono influenzare l'ottimizzazione.
        if result not in {"OK", "KO"}:
            continue

        diagnostics = parse_diagnostics(
            v251_row.get("Reason", "")
        )

        # Preferisce BaseScore presente nelle diagnostiche.
        # Se manca, utilizza direttamente lo Score della v25.
        base_score = diagnostics.get(
            "BaseScore",
            parse_float(v25_row.get("Score")),
        )

        # I segnali di penalità vengono trasformati in livelli positivi.
        #
        # Esempio:
        # StrongDefense=-2 diventa livello 2.
        strong_defense_level = abs(
            diagnostics.get(
                "StrongDefense",
                0.0,
            )
        )

        recent_form_level = abs(
            diagnostics.get(
                "RecentForm",
                0.0,
            )
        )

        restart_level = abs(
            diagnostics.get(
                "Restart",
                0.0,
            )
        )

        # I bonus futuri restano a zero finché non appariranno nel Reason.
        strong_attack_bonus_level = max(
            0.0,
            diagnostics.get(
                "StrongAttack",
                0.0,
            ),
        )

        recent_form_bonus_level = max(
            0.0,
            diagnostics.get(
                "RecentFormBonus",
                0.0,
            ),
        )

        restart_bonus_level = max(
            0.0,
            diagnostics.get(
                "RestartBonus",
                0.0,
            ),
        )

        dataset.append(
            {
                "MatchDate": text(v25_row.get("MatchDate")),
                "LeagueId": league_id,
                "Home": text(v25_row.get("Home")),
                "Away": text(v25_row.get("Away")),
                "Result": result,
                "BaseScore": base_score,
                "BaseBand": text(v25_row.get("Band")).upper(),
                "StrongDefenseLevel": strong_defense_level,
                "RecentFormLevel": recent_form_level,
                "RestartLevel": restart_level,
                "StrongAttackBonusLevel": strong_attack_bonus_level,
                "RecentFormBonusLevel": recent_form_bonus_level,
                "RestartBonusLevel": restart_bonus_level,
            }
        )

    return dataset


def simulate_row(
    row: dict,
    configuration: dict,
    alta_threshold: float,
    media_threshold: float,
) -> dict:
    """
    Applica virtualmente una configurazione di pesi a una singola partita.

    La funzione non modifica la riga originale.

    Le penalità vengono prima sommate e poi limitate dal cap massimo.
    I bonus vengono sommati separatamente.
    """

    strong_defense_penalty = (
        row["StrongDefenseLevel"]
        * configuration["StrongDefenseWeight"]
    )

    recent_form_penalty = (
        row["RecentFormLevel"]
        * configuration["RecentFormWeight"]
    )

    restart_penalty = (
        row["RestartLevel"]
        * configuration["RestartWeight"]
    )

    raw_penalty = (
        strong_defense_penalty
        + recent_form_penalty
        + restart_penalty
    )

    # Il cap limita la penalità complessiva.
    total_penalty = min(
        raw_penalty,
        configuration["MaxTotalPenalty"],
    )

    strong_attack_bonus = (
        row["StrongAttackBonusLevel"]
        * configuration["StrongAttackBonusWeight"]
    )

    recent_form_bonus = (
        row["RecentFormBonusLevel"]
        * configuration["RecentFormBonusWeight"]
    )

    restart_bonus = (
        row["RestartBonusLevel"]
        * configuration["RestartBonusWeight"]
    )

    total_bonus = (
        strong_attack_bonus
        + recent_form_bonus
        + restart_bonus
    )

    simulated_score = (
        row["BaseScore"]
        - total_penalty
        + total_bonus
    )

    simulated_band = score_to_band(
        score=simulated_score,
        alta_threshold=alta_threshold,
        media_threshold=media_threshold,
    )

    return {
        **row,
        "StrongDefensePenalty": round(strong_defense_penalty, 4),
        "RecentFormPenalty": round(recent_form_penalty, 4),
        "RestartPenalty": round(restart_penalty, 4),
        "TotalPenalty": round(total_penalty, 4),
        "TotalBonus": round(total_bonus, 4),
        "SimulatedScore": round(simulated_score, 4),
        "SimulatedBand": simulated_band,
    }


def evaluate_configuration(
    dataset: list[dict],
    configuration: dict,
    alta_threshold: float,
    media_threshold: float,
) -> tuple[dict, list[dict]]:
    """
    Valuta una configurazione sull'intero dataset.

    Restituisce:
    1. il riepilogo statistico;
    2. tutte le righe simulate.
    """

    simulated_rows = [
        simulate_row(
            row=row,
            configuration=configuration,
            alta_threshold=alta_threshold,
            media_threshold=media_threshold,
        )
        for row in dataset
    ]

    # Popolazione ALTA della baseline v25.
    baseline_alta = [
        row
        for row in simulated_rows
        if row["BaseBand"] == "ALTA"
    ]

    # Popolazione ALTA dopo la simulazione.
    simulated_alta = [
        row
        for row in simulated_rows
        if row["SimulatedBand"] == "ALTA"
    ]

    baseline_alta_ok = sum(
        row["Result"] == "OK"
        for row in baseline_alta
    )

    baseline_alta_ko = sum(
        row["Result"] == "KO"
        for row in baseline_alta
    )

    simulated_alta_ok = sum(
        row["Result"] == "OK"
        for row in simulated_alta
    )

    simulated_alta_ko = sum(
        row["Result"] == "KO"
        for row in simulated_alta
    )

    # KO ALTA della v25 che non sono più ALTA nella simulazione.
    alta_ko_avoided = sum(
        row["BaseBand"] == "ALTA"
        and row["Result"] == "KO"
        and row["SimulatedBand"] != "ALTA"
        for row in simulated_rows
    )

    # OK ALTA della v25 che non sono più ALTA nella simulazione.
    alta_ok_lost = sum(
        row["BaseBand"] == "ALTA"
        and row["Result"] == "OK"
        and row["SimulatedBand"] != "ALTA"
        for row in simulated_rows
    )

    # OK che partono da MEDIA/BASSA e salgono in ALTA grazie a futuri bonus.
    alta_ok_promoted = sum(
        row["BaseBand"] != "ALTA"
        and row["Result"] == "OK"
        and row["SimulatedBand"] == "ALTA"
        for row in simulated_rows
    )

    # KO che partono da MEDIA/BASSA e salgono in ALTA: effetto negativo dei bonus.
    alta_ko_promoted = sum(
        row["BaseBand"] != "ALTA"
        and row["Result"] == "KO"
        and row["SimulatedBand"] == "ALTA"
        for row in simulated_rows
    )

    simulated_alta_total = (
        simulated_alta_ok
        + simulated_alta_ko
    )

    baseline_alta_total = (
        baseline_alta_ok
        + baseline_alta_ko
    )

    simulated_alta_precision = (
        simulated_alta_ok
        / simulated_alta_total
        * 100.0
        if simulated_alta_total
        else 0.0
    )

    baseline_alta_precision = (
        baseline_alta_ok
        / baseline_alta_total
        * 100.0
        if baseline_alta_total
        else 0.0
    )

    alta_coverage = (
        simulated_alta_total
        / baseline_alta_total
        * 100.0
        if baseline_alta_total
        else 0.0
    )

    protective_balance = (
        alta_ko_avoided
        - alta_ok_lost
    )

    promotion_balance = (
        alta_ok_promoted
        - alta_ko_promoted
    )

    # Il punteggio di ottimizzazione privilegia:
    # 1. saldo protettivo positivo;
    # 2. saldo promozionale positivo;
    # 3. precisione;
    # 4. copertura.
    #
    # I coefficienti non modificano l'engine: servono soltanto a ordinare
    # la classifica delle configurazioni.
    objective_score = (
        protective_balance * 1000.0
        + promotion_balance * 500.0
        + simulated_alta_precision * 10.0
        + alta_coverage
    )

    summary = {
        **configuration,
        "BaselineAltaOK": baseline_alta_ok,
        "BaselineAltaKO": baseline_alta_ko,
        "BaselineAltaTotal": baseline_alta_total,
        "BaselineAltaPrecision": round(baseline_alta_precision, 4),
        "SimulatedAltaOK": simulated_alta_ok,
        "SimulatedAltaKO": simulated_alta_ko,
        "SimulatedAltaTotal": simulated_alta_total,
        "SimulatedAltaPrecision": round(simulated_alta_precision, 4),
        "AltaCoverage": round(alta_coverage, 4),
        "AltaKOAvoided": alta_ko_avoided,
        "AltaOKLost": alta_ok_lost,
        "ProtectiveBalance": protective_balance,
        "AltaOKPromoted": alta_ok_promoted,
        "AltaKOPromoted": alta_ko_promoted,
        "PromotionBalance": promotion_balance,
        "ObjectiveScore": round(objective_score, 4),
    }

    return summary, simulated_rows


def generate_configurations() -> list[dict]:
    """
    Genera tutte le combinazioni dei pesi definiti nelle costanti iniziali.
    """

    configurations = []

    configuration_id = 0

    for (
        strong_defense_weight,
        recent_form_weight,
        restart_weight,
        max_total_penalty,
        strong_attack_bonus_weight,
        recent_form_bonus_weight,
        restart_bonus_weight,
    ) in product(
        STRONG_DEFENSE_WEIGHTS,
        RECENT_FORM_WEIGHTS,
        RESTART_WEIGHTS,
        MAX_TOTAL_PENALTIES,
        STRONG_ATTACK_BONUS_WEIGHTS,
        RECENT_FORM_BONUS_WEIGHTS,
        RESTART_BONUS_WEIGHTS,
    ):

        configuration_id += 1

        configurations.append(
            {
                "ConfigurationId": configuration_id,
                "StrongDefenseWeight": strong_defense_weight,
                "RecentFormWeight": recent_form_weight,
                "RestartWeight": restart_weight,
                "MaxTotalPenalty": max_total_penalty,
                "StrongAttackBonusWeight": strong_attack_bonus_weight,
                "RecentFormBonusWeight": recent_form_bonus_weight,
                "RestartBonusWeight": restart_bonus_weight,
            }
        )

    return configurations


def write_csv(
    path: Path,
    rows: list[dict],
    fieldnames: list[str] | None = None,
) -> None:
    """
    Scrive una lista di dizionari in formato CSV con delimitatore ";".
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if fieldnames is None:

        fieldnames = []

        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)

    with path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:

        writer = csv.DictWriter(
            file_handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def build_activation_summary(
    dataset: list[dict],
) -> list[dict]:
    """
    Riassume quante volte ogni segnale viene attivato e con quale esito.

    Questo report aiuta a capire se l'ottimizzatore sta lavorando su campioni
    reali o su segnali troppo rari.
    """

    definitions = (
        ("StrongDefense", "StrongDefenseLevel"),
        ("RecentForm", "RecentFormLevel"),
        ("Restart", "RestartLevel"),
        ("StrongAttackBonus", "StrongAttackBonusLevel"),
        ("RecentFormBonus", "RecentFormBonusLevel"),
        ("RestartBonus", "RestartBonusLevel"),
    )

    rows = []

    for adjustment_name, field_name in definitions:

        activated = [
            row
            for row in dataset
            if row[field_name] > 0
        ]

        ok_count = sum(
            row["Result"] == "OK"
            for row in activated
        )

        ko_count = sum(
            row["Result"] == "KO"
            for row in activated
        )

        total = (
            ok_count
            + ko_count
        )

        precision = (
            ok_count
            / total
            * 100.0
            if total
            else 0.0
        )

        rows.append(
            {
                "Adjustment": adjustment_name,
                "Occurrences": total,
                "OK": ok_count,
                "KO": ko_count,
                "Precision": round(precision, 4),
                "AverageLevel": round(
                    mean(
                        row[field_name]
                        for row in activated
                    ),
                    4,
                )
                if activated
                else 0.0,
            }
        )

    return rows


def select_changed_rows(
    simulated_rows: list[dict],
) -> list[dict]:
    """
    Estrae soltanto le partite la cui fascia cambia rispetto alla v25.
    """

    changed = [
        row
        for row in simulated_rows
        if row["BaseBand"] != row["SimulatedBand"]
    ]

    # Ordina prima per data e poi per Score originale decrescente.
    changed.sort(
        key=lambda row: (
            row["MatchDate"],
            -row["BaseScore"],
            row["LeagueId"],
            row["Home"],
            row["Away"],
        )
    )

    return changed


def write_notes(
    path: Path,
    dataset: list[dict],
    configurations_count: int,
    best_summary: dict,
    exclude_australia: bool,
) -> None:
    """
    Scrive una spiegazione leggibile del test appena eseguito.
    """

    lines = [
        "GioOver2.5 - v251 Weight Optimizer",
        "=" * 44,
        "",
        f"Partite concluse analizzate: {len(dataset)}",
        f"Configurazioni provate: {configurations_count}",
        f"Australia esclusa: {'SI' if exclude_australia else 'NO'}",
        "",
        "Migliore configurazione trovata:",
        (
            "  StrongDefenseWeight = "
            f"{best_summary['StrongDefenseWeight']}"
        ),
        (
            "  RecentFormWeight = "
            f"{best_summary['RecentFormWeight']}"
        ),
        (
            "  RestartWeight = "
            f"{best_summary['RestartWeight']}"
        ),
        (
            "  MaxTotalPenalty = "
            f"{best_summary['MaxTotalPenalty']}"
        ),
        "",
        "Risultato fascia ALTA:",
        (
            "  Precisione baseline = "
            f"{best_summary['BaselineAltaPrecision']}%"
        ),
        (
            "  Precisione simulata = "
            f"{best_summary['SimulatedAltaPrecision']}%"
        ),
        (
            "  KO evitati = "
            f"{best_summary['AltaKOAvoided']}"
        ),
        (
            "  OK persi = "
            f"{best_summary['AltaOKLost']}"
        ),
        (
            "  ProtectiveBalance = "
            f"{best_summary['ProtectiveBalance']}"
        ),
        (
            "  Copertura residua = "
            f"{best_summary['AltaCoverage']}%"
        ),
        "",
        "AVVERTENZA:",
        (
            "La configurazione migliore sullo storico non deve essere "
            "adottata automaticamente."
        ),
        (
            "Va verificata su un periodo successivo non usato durante "
            "l'ottimizzazione, per ridurre il rischio di overfitting."
        ),
        "",
        "BONUS:",
        (
            "L'architettura è predisposta, ma i bonus rimangono inattivi "
            "finché il Laboratory non definisce segnali positivi espliciti."
        ),
    ]

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    """
    Punto di ingresso dello script.

    Legge gli argomenti, costruisce il dataset, prova tutte le configurazioni
    e salva i report.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Ottimizza retroattivamente i pesi sperimentali della v251 "
            "senza modificare gli engine."
        )
    )

    parser.add_argument(
        "--v25-file",
        type=Path,
        default=DEFAULT_V25_FILE,
        help="Percorso dello storico ranking v25.",
    )

    parser.add_argument(
        "--v251-file",
        type=Path,
        default=DEFAULT_V251_FILE,
        help="Percorso dello storico ranking v251.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Cartella di destinazione dei report.",
    )

    parser.add_argument(
        "--alta-threshold",
        type=float,
        default=DEFAULT_ALTA_THRESHOLD,
        help="Soglia minima della fascia ALTA.",
    )

    parser.add_argument(
        "--media-threshold",
        type=float,
        default=DEFAULT_MEDIA_THRESHOLD,
        help="Soglia minima della fascia MEDIA.",
    )

    parser.add_argument(
        "--exclude-australia",
        action="store_true",
        help="Esclude tutte le LeagueId che iniziano con Australia_.",
    )

    args = parser.parse_args()

    # Legge entrambi gli storici.
    v25_rows = read_csv_rows(
        args.v25_file
    )

    v251_rows = read_csv_rows(
        args.v251_file
    )

    # Costruisce l'intersezione valida e conclusa.
    dataset = build_dataset(
        v25_rows=v25_rows,
        v251_rows=v251_rows,
        exclude_australia=args.exclude_australia,
    )

    if not dataset:
        raise ValueError(
            "Nessuna partita conclusa e abbinabile trovata tra v25 e v251."
        )

    configurations = generate_configurations()

    summaries = []

    best_summary = None
    best_simulated_rows = None

    for configuration in configurations:

        summary, simulated_rows = evaluate_configuration(
            dataset=dataset,
            configuration=configuration,
            alta_threshold=args.alta_threshold,
            media_threshold=args.media_threshold,
        )

        summaries.append(
            summary
        )

        if (
            best_summary is None
            or summary["ObjectiveScore"]
            > best_summary["ObjectiveScore"]
        ):
            best_summary = summary
            best_simulated_rows = simulated_rows

    # Ordina dalla configurazione migliore alla peggiore.
    summaries.sort(
        key=lambda row: (
            -row["ObjectiveScore"],
            -row["ProtectiveBalance"],
            -row["SimulatedAltaPrecision"],
            -row["AltaCoverage"],
        )
    )

    output_dir = args.output_dir

    write_csv(
        output_dir / "01_weight_configurations.csv",
        summaries,
    )

    write_csv(
        output_dir / "02_best_configuration_summary.csv",
        [best_summary],
    )

    changed_rows = select_changed_rows(
        best_simulated_rows
    )

    write_csv(
        output_dir / "03_best_configuration_changes.csv",
        changed_rows,
    )

    activation_summary = build_activation_summary(
        dataset
    )

    write_csv(
        output_dir / "04_adjustment_activation_summary.csv",
        activation_summary,
    )

    write_notes(
        path=output_dir / "05_optimizer_notes.txt",
        dataset=dataset,
        configurations_count=len(configurations),
        best_summary=best_summary,
        exclude_australia=args.exclude_australia,
    )

    print()
    print("=== V251 WEIGHT OPTIMIZER ===")
    print(f"Partite analizzate     : {len(dataset)}")
    print(f"Configurazioni provate : {len(configurations)}")
    print(
        "Miglior ProtectiveBalance: "
        f"{best_summary['ProtectiveBalance']}"
    )
    print(
        "Precisione ALTA: "
        f"{best_summary['BaselineAltaPrecision']}% -> "
        f"{best_summary['SimulatedAltaPrecision']}%"
    )
    print(
        "Copertura ALTA residua: "
        f"{best_summary['AltaCoverage']}%"
    )
    print(f"Report salvati in      : {output_dir.resolve()}")


# Questo controllo esegue main() soltanto quando il file viene avviato
# direttamente come modulo Python.
if __name__ == "__main__":
    main()
