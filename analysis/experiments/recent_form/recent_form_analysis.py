"""
===============================================================================
GioOver2.5 - recent_form_threshold_analysis.py
===============================================================================

SCOPO
-----
Questo script verifica se il rendimento recente delle squadre, misurato tramite
PPG (Points Per Game) nelle ultime 5 partite, può aiutare a riconoscere partite
ALTA o MEDIA con maggiore rischio di KO sull'Over 2.5.

Lo script NON modifica alcun engine, NON modifica gli storici e NON assegna
ancora una penalità definitiva. Esegue soltanto una simulazione statistica.

COSA CALCOLA
------------
Per ogni partita conclusa presente nel Laboratory calcola, usando solo gare
precedenti alla partita analizzata:

    HomePPGLast5
    AwayPPGLast5
    WorstPPGLast5
    AveragePPGLast5
    HomeWinsLast5
    AwayWinsLast5

Successivamente prova molte soglie di WorstPPGLast5 e misura:

    OK eliminati
    KO eliminati
    saldo netto
    precisione originale
    precisione dopo il filtro
    numero di partite residue

INPUT
-----
    analysis/laboratory/data/01_matches.csv
    data/storico/risultati/*.csv

OUTPUT
------
    analysis/experiments/recent_form/outputs/01_recent_form_matches.csv
    analysis/experiments/recent_form/outputs/02_recent_form_distribution.csv
    analysis/experiments/recent_form/outputs/03_recent_form_thresholds.csv
    analysis/experiments/recent_form/outputs/04_recent_form_recommendation.txt

ESECUZIONE
----------
Dalla cartella principale del progetto:

    python -m analysis.experiments.recent_form.recent_form_analysis

Opzioni utili:

    --engine-version 2.5.0
    --last-n 5
    --include-australia

===============================================================================
"""

# Permette di usare annotazioni di tipo moderne senza problemi di valutazione
# immediata nelle versioni Python supportate dal progetto.
from __future__ import annotations

# argparse serve per leggere le opzioni passate da riga di comando.
import argparse

# csv serve per leggere e scrivere i file separati da punto e virgola.
import csv

# dataclass permette di rappresentare risultati e forma recente con strutture
# semplici, leggibili e immutabili.
from dataclasses import dataclass

# date serve per confrontare correttamente le date delle partite.
from datetime import date

# Path gestisce i percorsi in modo compatibile con Windows e altri sistemi.
from pathlib import Path

# Iterable viene usato soltanto nelle annotazioni della funzione di scrittura.
from typing import Iterable


# Individua la radice del progetto risalendo di quattro livelli dal file:
# recent_form_analysis.py -> recent_form -> experiments -> analysis -> progetto.
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# File del Laboratory che contiene una riga per ogni prediction analizzata.
DEFAULT_MATCHES_FILE = PROJECT_ROOT / "analysis/laboratory/data/01_matches.csv"

# Cartella che contiene gli storici risultati, uno per LeagueId.
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "data/storico/risultati"

# Cartella dove verranno prodotti i quattro report dell'esperimento.
DEFAULT_OUTPUT_DIR = (
    PROJECT_ROOT / "analysis/experiments/recent_form/outputs"
)


# Colonne del file dettagliato, una riga per ogni partita utilizzata nel test.
DETAIL_FIELDS = [
    "PredictionDate",
    "MatchDate",
    "LeagueId",
    "Round",
    "Home",
    "Away",
    "Score",
    "Band",
    "Outcome",
    "HG",
    "AG",
    "Goals",
    "AlgorithmVersion",
    "HomeMatchesLast5",
    "HomePointsLast5",
    "HomePPGLast5",
    "HomeWinsLast5",
    "AwayMatchesLast5",
    "AwayPointsLast5",
    "AwayPPGLast5",
    "AwayWinsLast5",
    "WorstPPGLast5",
    "AveragePPGLast5",
    "BothBelow080",
    "BothWinlessLast5",
    "PPGBucket",
]

# Colonne del report per intervalli di PPG.
DISTRIBUTION_FIELDS = [
    "Population",
    "PPGBucket",
    "Matches",
    "OK",
    "KO",
    "SuccessRate",
]

# Colonne del report che simula ogni possibile soglia.
THRESHOLD_FIELDS = [
    "Population",
    "Threshold",
    "OriginalMatches",
    "OriginalOK",
    "OriginalKO",
    "OriginalSuccessRate",
    "RemovedMatches",
    "OKRemoved",
    "KORemoved",
    "NetAdvantage",
    "RemainingMatches",
    "RemainingOK",
    "RemainingKO",
    "RemainingSuccessRate",
    "PrecisionDelta",
    "CoverageRemaining",
]


@dataclass(frozen=True)
class ResultRow:
    """Rappresenta una partita conclusa letta dallo storico risultati."""

    # Data reale in cui la partita è stata disputata.
    match_date: date

    # Squadra di casa.
    home: str

    # Squadra ospite.
    away: str

    # Gol segnati dalla squadra di casa.
    home_goals: int

    # Gol segnati dalla squadra ospite.
    away_goals: int


@dataclass(frozen=True)
class RecentForm:
    """Riepiloga il rendimento di una squadra nelle ultime N gare."""

    # Numero di partite effettivamente disponibili prima del match analizzato.
    matches: int

    # Punti ottenuti nelle partite considerate.
    points: int

    # Numero di vittorie nelle partite considerate.
    wins: int

    @property
    def ppg(self) -> float:
        """Restituisce i punti medi per partita; zero se non ci sono gare."""

        return self.points / self.matches if self.matches else 0.0



def _text(value: object) -> str:
    """Converte qualsiasi valore in testo pulito, evitando valori None."""

    return str(value or "").strip()



def _normalize_team(value: object) -> str:
    """Normalizza il nome squadra per rendere affidabili i confronti."""

    return " ".join(_text(value).casefold().split())



def _parse_date(value: object) -> date | None:
    """Converte una data ISO YYYY-MM-DD in date; restituisce None se invalida."""

    # Recupera il valore testuale ripulito.
    raw = _text(value)

    # Se il campo è vuoto non esiste una data utilizzabile.
    if not raw:
        return None

    # Prova a interpretare la data nel formato ISO usato dal progetto.
    try:
        return date.fromisoformat(raw)

    # Se il formato è errato, la riga verrà esclusa senza bloccare lo script.
    except ValueError:
        return None



def _to_int(value: object) -> int | None:
    """Converte un valore numerico in intero; restituisce None se invalido."""

    # Pulisce il testo ricevuto.
    raw = _text(value)

    # Un valore vuoto non è convertibile.
    if not raw:
        return None

    # Accetta anche numeri scritti con virgola o come decimali interi.
    try:
        return int(float(raw.replace(",", ".")))

    # Una conversione fallita rende la riga non utilizzabile.
    except ValueError:
        return None



def _to_float(value: object) -> float:
    """Converte un valore in float; restituisce zero se non è valido."""

    # Uniforma il separatore decimale.
    raw = _text(value).replace(",", ".")

    # Prova a convertire il valore.
    try:
        return float(raw) if raw else 0.0

    # In caso di errore usa zero, sufficiente per le statistiche aggregate.
    except ValueError:
        return 0.0



def _read_csv(path: Path) -> list[dict[str, str]]:
    """Legge un CSV con separatore ';' e restituisce tutte le righe."""

    # utf-8-sig gestisce correttamente anche file con BOM prodotti da Excel.
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle, delimiter=";"))



def _write_csv(
    path: Path,
    rows: Iterable[dict],
    fieldnames: list[str],
) -> None:
    """Scrive un report CSV creando prima la cartella di destinazione."""

    # Crea le cartelle mancanti senza errore se esistono già.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Apre il file in scrittura usando lo standard del progetto.
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        # Configura lo scrittore con separatore ';'.
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )

        # Scrive l'intestazione.
        writer.writeheader()

        # Scrive tutte le righe ricevute.
        writer.writerows(rows)



def _find_results_file(results_dir: Path, league_id: str) -> Path | None:
    """Trova lo storico risultati relativo al LeagueId della prediction."""

    # Primo tentativo: nuovo formato seasonless, ad esempio Germany_Bundesliga.csv.
    direct_file = results_dir / f"{league_id}.csv"

    # Se il file esiste, è quello corretto.
    if direct_file.exists():
        return direct_file

    # Compatibilità temporanea con vecchi nomi che terminano con _YYYY.
    legacy_files = sorted(results_dir.glob(f"{league_id}_20[0-9][0-9].csv"))

    # Usa il file più recente se la migrazione non è ancora completa.
    return legacy_files[-1] if legacy_files else None



def _load_results(path: Path) -> list[ResultRow]:
    """Carica e valida tutte le partite concluse di uno storico risultati."""

    # Legge le righe grezze del CSV.
    rows = _read_csv(path)

    # Lista finale delle partite valide.
    results: list[ResultRow] = []

    # Analizza una riga alla volta.
    for row in rows:
        # MatchDate è il formato attuale; Date resta supportato per il pregresso.
        match_date = _parse_date(row.get("MatchDate") or row.get("Date"))

        # Converte i gol in numeri interi.
        home_goals = _to_int(row.get("HG"))
        away_goals = _to_int(row.get("AG"))

        # Legge i nomi delle squadre.
        home = _text(row.get("Home"))
        away = _text(row.get("Away"))

        # Ignora righe incomplete o non concluse.
        if (
            match_date is None
            or home_goals is None
            or away_goals is None
            or not home
            or not away
        ):
            continue

        # Aggiunge la partita validata alla lista.
        results.append(
            ResultRow(
                match_date=match_date,
                home=home,
                away=away,
                home_goals=home_goals,
                away_goals=away_goals,
            )
        )

    # Ordina cronologicamente per rendere corretto il calcolo delle ultime gare.
    results.sort(key=lambda result: result.match_date)

    # Restituisce lo storico pronto per l'analisi.
    return results



def _resolve_target_match(
    ranking_row: dict[str, str],
    results: list[ResultRow],
) -> ResultRow | None:
    """Associa una prediction del Laboratory alla partita reale conclusa."""

    # Normalizza le due squadre della prediction.
    home = _normalize_team(ranking_row.get("Home"))
    away = _normalize_team(ranking_row.get("Away"))

    # Legge, quando disponibili, il risultato già riportato nel Laboratory.
    expected_hg = _to_int(ranking_row.get("HG"))
    expected_ag = _to_int(ranking_row.get("AG"))

    # Legge la data prevista della partita.
    expected_date = _parse_date(ranking_row.get("MatchDate"))

    # Cerca tutte le partite con le stesse squadre e lo stesso verso casa/trasferta.
    candidates = [
        result
        for result in results
        if _normalize_team(result.home) == home
        and _normalize_team(result.away) == away
    ]

    # Se il Laboratory contiene già HG e AG, restringe ai risultati identici.
    if expected_hg is not None and expected_ag is not None:
        same_score = [
            result
            for result in candidates
            if result.home_goals == expected_hg
            and result.away_goals == expected_ag
        ]

        # Usa il filtro soltanto se produce almeno un candidato.
        if same_score:
            candidates = same_score

    # Se esiste una data esatta e un solo candidato coincide, il matching è certo.
    if expected_date is not None:
        exact_matches = [
            result for result in candidates if result.match_date == expected_date
        ]

        if len(exact_matches) == 1:
            return exact_matches[0]

    # Nessun candidato significa che la partita non è risolvibile.
    if not candidates:
        return None

    # Senza data accettiamo soltanto un candidato univoco.
    if expected_date is None:
        return candidates[0] if len(candidates) == 1 else None

    # Ordina i candidati per distanza dalla data della prediction.
    candidates.sort(
        key=lambda result: abs((result.match_date - expected_date).days)
    )

    # Se i due candidati migliori hanno la stessa distanza il matching è ambiguo.
    if len(candidates) > 1:
        first_distance = abs((candidates[0].match_date - expected_date).days)
        second_distance = abs((candidates[1].match_date - expected_date).days)

        if first_distance == second_distance:
            return None

    # Restituisce il candidato temporalmente più vicino.
    return candidates[0]



def _calculate_recent_form(
    results: list[ResultRow],
    team: str,
    before_date: date,
    last_n: int,
) -> RecentForm:
    """Calcola punti, vittorie e PPG nelle ultime N gare prima del match."""

    # Normalizza il nome della squadra da cercare.
    normalized_team = _normalize_team(team)

    # Seleziona soltanto le gare precedenti alla data del match analizzato.
    previous_matches = [
        result
        for result in results
        if result.match_date < before_date
        and normalized_team
        in {
            _normalize_team(result.home),
            _normalize_team(result.away),
        }
    ]

    # Mantiene soltanto le ultime N gare disponibili.
    previous_matches = previous_matches[-last_n:]

    # Inizializza punti e vittorie.
    points = 0
    wins = 0

    # Calcola il risultato dal punto di vista della squadra analizzata.
    for result in previous_matches:
        # Verifica se la squadra giocava in casa.
        is_home = _normalize_team(result.home) == normalized_team

        # Determina gol fatti e subiti dal punto di vista corretto.
        goals_for = result.home_goals if is_home else result.away_goals
        goals_against = result.away_goals if is_home else result.home_goals

        # Una vittoria assegna tre punti.
        if goals_for > goals_against:
            points += 3
            wins += 1

        # Un pareggio assegna un punto.
        elif goals_for == goals_against:
            points += 1

        # Una sconfitta non assegna punti e non richiede modifiche.

    # Restituisce il riepilogo della forma recente.
    return RecentForm(
        matches=len(previous_matches),
        points=points,
        wins=wins,
    )



def _ppg_bucket(ppg: float) -> str:
    """Assegna WorstPPGLast5 a intervalli regolari di 0,20 punti."""

    # Definisce l'estremo inferiore dell'intervallo.
    lower = int(ppg / 0.20) * 0.20

    # Evita di superare il massimo teorico di 3 PPG.
    lower = min(lower, 2.80)

    # Calcola l'estremo superiore.
    upper = min(lower + 0.20, 3.00)

    # Restituisce un'etichetta ordinabile e leggibile.
    return f"{lower:.2f}-{upper:.2f}"



def _population(row: dict) -> str:
    """Combina fascia ed esito nelle quattro popolazioni ufficiali."""

    # Legge la fascia in maiuscolo.
    band = _text(row.get("Band")).upper()

    # Legge l'esito in maiuscolo.
    outcome = _text(row.get("Outcome")).upper()

    # Restituisce valori come ALTA_OK, ALTA_KO, MEDIA_OK o MEDIA_KO.
    return f"{band}_{outcome}"



def _build_details(
    matches_file: Path,
    results_dir: Path,
    engine_version: str,
    last_n: int,
    include_australia: bool,
) -> tuple[list[dict], int]:
    """Costruisce il dataset dettagliato usato da tutti gli altri report."""

    # Legge tutte le partite prodotte dal Laboratory.
    source_rows = _read_csv(matches_file)

    # Cache per evitare di rileggere lo stesso storico molte volte.
    results_cache: dict[Path, list[ResultRow]] = {}

    # Lista delle righe valide che entreranno nell'analisi.
    details: list[dict] = []

    # Conta le partite escluse perché non risolvibili o con dati insufficienti.
    unresolved = 0

    # Analizza ogni riga del Laboratory.
    for row in source_rows:
        # Considera soltanto le fasce ALTA e MEDIA.
        band = _text(row.get("Band")).upper()
        if band not in {"ALTA", "MEDIA"}:
            continue

        # Considera soltanto partite già concluse e classificate OK o KO.
        outcome = _text(row.get("Outcome")).upper()
        if outcome not in {"OK", "KO"}:
            continue

        # Se richiesto, limita l'analisi a una specifica versione dell'engine.
        if engine_version and _text(row.get("AlgorithmVersion")) != engine_version:
            continue

        # Recupera il LeagueId della partita.
        league_id = _text(row.get("LeagueId"))

        # Per impostazione predefinita esclude le leghe australiane, già note
        # per avere un comportamento meno coerente con l'algoritmo generale.
        if not include_australia and league_id.startswith("Australia_"):
            continue

        # Cerca il file risultati della lega.
        results_file = _find_results_file(results_dir, league_id)

        # Se il file non esiste la prediction non può essere analizzata.
        if results_file is None:
            unresolved += 1
            continue

        # Carica lo storico una sola volta e poi lo riutilizza dalla cache.
        if results_file not in results_cache:
            results_cache[results_file] = _load_results(results_file)

        results = results_cache[results_file]

        # Associa la prediction alla partita reale conclusa.
        target_match = _resolve_target_match(row, results)

        # Se il matching non è affidabile, la riga viene esclusa.
        if target_match is None:
            unresolved += 1
            continue

        # Calcola la forma recente della squadra di casa.
        home_form = _calculate_recent_form(
            results=results,
            team=_text(row.get("Home")),
            before_date=target_match.match_date,
            last_n=last_n,
        )

        # Calcola la forma recente della squadra ospite.
        away_form = _calculate_recent_form(
            results=results,
            team=_text(row.get("Away")),
            before_date=target_match.match_date,
            last_n=last_n,
        )

        # Per un vero PPG Last 5 richiede cinque gare precedenti per entrambe.
        if home_form.matches < last_n or away_form.matches < last_n:
            unresolved += 1
            continue

        # La metrica più prudente è il PPG peggiore tra le due squadre.
        worst_ppg = min(home_form.ppg, away_form.ppg)

        # La media descrive invece la qualità recente complessiva del match.
        average_ppg = (home_form.ppg + away_form.ppg) / 2

        # Costruisce la riga dettagliata mantenendo anche i dati originali.
        details.append(
            {
                **row,
                "HomeMatchesLast5": home_form.matches,
                "HomePointsLast5": home_form.points,
                "HomePPGLast5": f"{home_form.ppg:.4f}",
                "HomeWinsLast5": home_form.wins,
                "AwayMatchesLast5": away_form.matches,
                "AwayPointsLast5": away_form.points,
                "AwayPPGLast5": f"{away_form.ppg:.4f}",
                "AwayWinsLast5": away_form.wins,
                "WorstPPGLast5": f"{worst_ppg:.4f}",
                "AveragePPGLast5": f"{average_ppg:.4f}",
                "BothBelow080": int(
                    home_form.ppg < 0.80 and away_form.ppg < 0.80
                ),
                "BothWinlessLast5": int(
                    home_form.wins == 0 and away_form.wins == 0
                ),
                "PPGBucket": _ppg_bucket(worst_ppg),
            }
        )

    # Restituisce dataset valido e numero di esclusioni.
    return details, unresolved



def _build_distribution(details: list[dict]) -> list[dict]:
    """Raggruppa le partite per fascia e intervallo di WorstPPGLast5."""

    # Popolazioni aggregate che vogliamo confrontare.
    populations = ["ALTA", "MEDIA", "ALL"]

    # Raccoglie dinamicamente tutti i bucket presenti nel dataset.
    buckets = sorted({row["PPGBucket"] for row in details})

    # Lista finale del report.
    output: list[dict] = []

    # Costruisce una sezione per ogni popolazione.
    for population in populations:
        # Filtra ALTA, MEDIA oppure mantiene tutto.
        population_rows = [
            row
            for row in details
            if population == "ALL" or _text(row.get("Band")).upper() == population
        ]

        # Analizza ciascun intervallo di PPG.
        for bucket in buckets:
            # Seleziona le partite appartenenti all'intervallo corrente.
            rows = [
                row for row in population_rows if row["PPGBucket"] == bucket
            ]

            # Salta bucket vuoti.
            if not rows:
                continue

            # Conta gli OK.
            ok = sum(_text(row.get("Outcome")).upper() == "OK" for row in rows)

            # I restanti sono KO perché il dataset contiene solo OK e KO.
            ko = len(rows) - ok

            # Aggiunge il riepilogo al report.
            output.append(
                {
                    "Population": population,
                    "PPGBucket": bucket,
                    "Matches": len(rows),
                    "OK": ok,
                    "KO": ko,
                    "SuccessRate": f"{ok / len(rows):.4f}",
                }
            )

    # Restituisce il report completo.
    return output



def _threshold_values() -> list[float]:
    """Genera soglie da 0,20 a 2,00 con incrementi di 0,05."""

    # Usa interi per evitare piccoli errori dei numeri floating point.
    return [value / 100 for value in range(20, 201, 5)]



def _build_threshold_analysis(details: list[dict]) -> list[dict]:
    """Simula l'esclusione delle partite sotto ogni soglia di WorstPPGLast5."""

    # Analizza separatamente le fasce ALTA e MEDIA.
    populations = ["ALTA", "MEDIA"]

    # Lista finale delle simulazioni.
    output: list[dict] = []

    # Esegue la simulazione per ciascuna fascia.
    for population in populations:
        # Seleziona le partite della fascia corrente.
        rows = [
            row
            for row in details
            if _text(row.get("Band")).upper() == population
        ]

        # Se la fascia non ha dati, passa alla successiva.
        if not rows:
            continue

        # Calcola i risultati originali prima di applicare qualsiasi soglia.
        original_ok = sum(
            _text(row.get("Outcome")).upper() == "OK" for row in rows
        )
        original_ko = len(rows) - original_ok
        original_rate = original_ok / len(rows)

        # Prova tutte le soglie previste.
        for threshold in _threshold_values():
            # Le partite sotto soglia verrebbero penalizzate o escluse.
            removed = [
                row
                for row in rows
                if _to_float(row.get("WorstPPGLast5")) < threshold
            ]

            # Le partite sopra soglia resterebbero nella fascia.
            remaining = [
                row
                for row in rows
                if _to_float(row.get("WorstPPGLast5")) >= threshold
            ]

            # Conta gli OK eliminati dal filtro.
            ok_removed = sum(
                _text(row.get("Outcome")).upper() == "OK" for row in removed
            )

            # Conta i KO eliminati dal filtro.
            ko_removed = len(removed) - ok_removed

            # Conta gli OK rimasti.
            remaining_ok = sum(
                _text(row.get("Outcome")).upper() == "OK" for row in remaining
            )

            # Conta i KO rimasti.
            remaining_ko = len(remaining) - remaining_ok

            # Calcola la nuova precisione; resta vuota se non rimane alcuna gara.
            remaining_rate = (
                remaining_ok / len(remaining) if remaining else None
            )

            # Il saldo netto è positivo soltanto se vengono eliminati più KO che OK.
            net_advantage = ko_removed - ok_removed

            # La copertura indica quanta parte delle selezioni originarie rimane.
            coverage = len(remaining) / len(rows)

            # Aggiunge i risultati della soglia al report.
            output.append(
                {
                    "Population": population,
                    "Threshold": f"{threshold:.2f}",
                    "OriginalMatches": len(rows),
                    "OriginalOK": original_ok,
                    "OriginalKO": original_ko,
                    "OriginalSuccessRate": f"{original_rate:.4f}",
                    "RemovedMatches": len(removed),
                    "OKRemoved": ok_removed,
                    "KORemoved": ko_removed,
                    "NetAdvantage": net_advantage,
                    "RemainingMatches": len(remaining),
                    "RemainingOK": remaining_ok,
                    "RemainingKO": remaining_ko,
                    "RemainingSuccessRate": (
                        f"{remaining_rate:.4f}" if remaining_rate is not None else ""
                    ),
                    "PrecisionDelta": (
                        f"{remaining_rate - original_rate:.4f}"
                        if remaining_rate is not None
                        else ""
                    ),
                    "CoverageRemaining": f"{coverage:.4f}",
                }
            )

    # Restituisce tutte le simulazioni.
    return output



def _choose_best_threshold(
    threshold_rows: list[dict],
    population: str,
) -> dict | None:
    """Sceglie la soglia più utile con criteri prudenti e trasparenti."""

    # Mantiene soltanto la fascia richiesta.
    candidates = [
        row for row in threshold_rows if row["Population"] == population
    ]

    # Richiede almeno dieci partite residue e almeno il 60% di copertura.
    candidates = [
        row
        for row in candidates
        if int(row["RemainingMatches"]) >= 10
        and _to_float(row["CoverageRemaining"]) >= 0.60
    ]

    # Richiede una precisione realmente migliore dell'originale.
    candidates = [
        row for row in candidates if _to_float(row["PrecisionDelta"]) > 0
    ]

    # Se nessuna soglia supera i controlli, non viene data una raccomandazione.
    if not candidates:
        return None

    # Ordina prima per incremento di precisione, poi per KO rimossi e infine
    # per maggiore copertura, così evita soglie troppo aggressive.
    candidates.sort(
        key=lambda row: (
            _to_float(row["PrecisionDelta"]),
            int(row["KORemoved"]),
            _to_float(row["CoverageRemaining"]),
        ),
        reverse=True,
    )

    # Restituisce il candidato migliore.
    return candidates[0]



def _write_recommendation(
    path: Path,
    threshold_rows: list[dict],
    unresolved: int,
) -> None:
    """Scrive una conclusione leggibile basata sui risultati delle soglie."""

    # Crea la cartella di destinazione se necessario.
    path.parent.mkdir(parents=True, exist_ok=True)

    # Cerca la migliore soglia per la fascia ALTA, che è la priorità del test.
    best_alta = _choose_best_threshold(threshold_rows, "ALTA")

    # Prepara le righe del report testuale.
    lines = [
        "GioOver2.5 - Raccomandazione esperimento Recent Form",
        "====================================================",
        "",
        f"Partite escluse o non risolte: {unresolved}",
        "",
    ]

    # Se non esiste una soglia valida, sconsiglia per ora il nuovo driver.
    if best_alta is None:
        lines.extend(
            [
                "ESITO: DRIVER NON ANCORA CONSIGLIATO",
                "",
                "Nessuna soglia mantiene almeno il 60% delle partite ALTA",
                "e contemporaneamente migliora la precisione in modo positivo.",
                "",
                "Il PPG Last 5 resta disponibile nel report dettagliato per",
                "ulteriori analisi, ma non va ancora inserito nell'engine.",
            ]
        )

    # Se esiste una soglia utile, ne riporta tutti gli effetti osservati.
    else:
        original_rate = _to_float(best_alta["OriginalSuccessRate"]) * 100
        remaining_rate = _to_float(best_alta["RemainingSuccessRate"]) * 100
        delta = _to_float(best_alta["PrecisionDelta"]) * 100
        coverage = _to_float(best_alta["CoverageRemaining"]) * 100

        lines.extend(
            [
                "ESITO: SOGLIA CANDIDATA INDIVIDUATA",
                "",
                f"WorstPPGLast5 minimo: {best_alta['Threshold']}",
                f"Partite ALTA originali: {best_alta['OriginalMatches']}",
                f"Partite eliminate: {best_alta['RemovedMatches']}",
                f"OK eliminati: {best_alta['OKRemoved']}",
                f"KO eliminati: {best_alta['KORemoved']}",
                f"Saldo netto KO-OK: {best_alta['NetAdvantage']}",
                f"Precisione originale: {original_rate:.2f}%",
                f"Precisione dopo il filtro: {remaining_rate:.2f}%",
                f"Incremento precisione: {delta:.2f} punti percentuali",
                f"Copertura residua: {coverage:.2f}%",
                "",
                "Questa soglia è soltanto una candidata statistica.",
                "Prima di creare v26 va verificata su un campione più ampio",
                "e confrontata anche per lega e periodo temporale.",
            ]
        )

    # Scrive il testo usando UTF-8 standard.
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")



def main() -> None:
    """Coordina lettura, analisi, produzione dei report e riepilogo finale."""

    # Crea il parser degli argomenti da riga di comando.
    parser = argparse.ArgumentParser(
        description=(
            "Analizza il PPG delle ultime partite e simula soglie di esclusione."
        )
    )

    # Permette di usare un file Laboratory diverso da quello predefinito.
    parser.add_argument(
        "--matches-file",
        type=Path,
        default=DEFAULT_MATCHES_FILE,
    )

    # Permette di indicare una cartella risultati diversa.
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
    )

    # Permette di scegliere una cartella output diversa.
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )

    # Filtra una specifica versione dell'algoritmo; vuoto significa tutte.
    parser.add_argument(
        "--engine-version",
        default="2.5.0",
    )

    # Numero di gare recenti da utilizzare; per questo esperimento il default è 5.
    parser.add_argument(
        "--last-n",
        type=int,
        default=5,
    )

    # Include esplicitamente le leghe australiane, escluse per impostazione standard.
    parser.add_argument(
        "--include-australia",
        action="store_true",
    )

    # Legge gli argomenti effettivamente passati dall'utente.
    args = parser.parse_args()

    # Impedisce valori non validi per il numero di partite recenti.
    if args.last_n < 1:
        raise ValueError("--last-n deve essere almeno 1")

    # Verifica che il file del Laboratory esista prima di iniziare.
    if not args.matches_file.exists():
        raise FileNotFoundError(
            f"File Laboratory non trovato: {args.matches_file}"
        )

    # Verifica che la cartella degli storici risultati esista.
    if not args.results_dir.exists():
        raise FileNotFoundError(
            f"Cartella risultati non trovata: {args.results_dir}"
        )

    # Costruisce il dataset dettagliato con PPG Last 5.
    details, unresolved = _build_details(
        matches_file=args.matches_file,
        results_dir=args.results_dir,
        engine_version=args.engine_version,
        last_n=args.last_n,
        include_australia=args.include_australia,
    )

    # Produce la distribuzione per bucket di PPG.
    distribution = _build_distribution(details)

    # Simula tutte le soglie previste.
    thresholds = _build_threshold_analysis(details)

    # Definisce i quattro percorsi output.
    detail_path = args.output_dir / "01_recent_form_matches.csv"
    distribution_path = args.output_dir / "02_recent_form_distribution.csv"
    thresholds_path = args.output_dir / "03_recent_form_thresholds.csv"
    recommendation_path = args.output_dir / "04_recent_form_recommendation.txt"

    # Scrive il dettaglio partita per partita.
    _write_csv(detail_path, details, DETAIL_FIELDS)

    # Scrive la distribuzione per intervalli di PPG.
    _write_csv(distribution_path, distribution, DISTRIBUTION_FIELDS)

    # Scrive la simulazione delle soglie.
    _write_csv(thresholds_path, thresholds, THRESHOLD_FIELDS)

    # Scrive la raccomandazione automatica.
    _write_recommendation(recommendation_path, thresholds, unresolved)

    # Stampa un riepilogo finale chiaro nella console.
    print("=== RECENT FORM THRESHOLD ANALYSIS ===")
    print(f"Partite analizzate          : {len(details)}")
    print(f"Partite escluse/non risolte : {unresolved}")
    print(f"Dettaglio                   : {detail_path.relative_to(PROJECT_ROOT)}")
    print(
        "Distribuzione               : "
        f"{distribution_path.relative_to(PROJECT_ROOT)}"
    )
    print(f"Soglie                     : {thresholds_path.relative_to(PROJECT_ROOT)}")
    print(
        "Raccomandazione             : "
        f"{recommendation_path.relative_to(PROJECT_ROOT)}"
    )


# Esegue main soltanto quando il file viene avviato direttamente come modulo.
if __name__ == "__main__":
    main()
