"""
===============================================================================
GioOver2.5 - analysis/laboratory/writer.py
===============================================================================

SCOPO
-----
Scrivere i dataset principali del laboratorio:

    01_matches.csv
    02_drivers.csv

CORREZIONE
----------
L'header di 01_matches.csv viene costruito usando l'unione ordinata di tutte
le colonne presenti nelle righe, non soltanto quelle della prima riga.

In questo modo non vengono persi campi come:

    MatchDate
    MatchMode
    DateDifferenceDays
    CompetitionGroup
    HomeSourceLeagueId
    AwaySourceLeagueId

FILE LETTI
----------
Nessuno direttamente.

FILE SCRITTI
-------------
analysis/laboratory/data/01_matches.csv
analysis/laboratory/data/02_drivers.csv

LIMITAZIONI
-----------
02_drivers.csv continua a contenere soltanto i driver esplicitamente elencati
in DRIVERS.
===============================================================================
"""

import csv

from .recent_form_drivers import RECENT_FORM_DRIVERS


DRIVERS = [
    "RankingGapScore",
    "HomeAttackScore",
    "AwayAttackScore",
    "HomeDefenseWeaknessScore",
    "AwayDefenseWeaknessScore",
    "HomeLast10OverScore",
    "AwayLast10OverScore",
    "HomeVenueOverScore",
    "AwayVenueOverScore",
    "BTTSProfileScore",
    *RECENT_FORM_DRIVERS,
]


PREFERRED_MATCH_FIELDS = [
    "MatchId",
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
    "BTTS",
    "Reason",
    "RankingGapScore",
    "HomeAttackScore",
    "AwayAttackScore",
    "HomeDefenseWeaknessScore",
    "AwayDefenseWeaknessScore",
    "HomeLast10OverScore",
    "AwayLast10OverScore",
    "HomeVenueOverScore",
    "AwayVenueOverScore",
    "BTTSProfileScore",
    *RECENT_FORM_DRIVERS,
    "AlgorithmVersion",
    "CompetitionGroup",
    "HomeSourceLeagueId",
    "AwaySourceLeagueId",
    "MatchMode",
    "DateDifferenceDays",
    "HistorySource",
    "RankingSource",
]


def _collect_fieldnames(rows: list[dict]) -> list[str]:
    """
    Costruisce l'header come unione ordinata di tutte le colonne.

    Le colonne principali vengono mantenute all'inizio; eventuali colonne
    aggiuntive vengono accodate nell'ordine di prima apparizione.
    """
    discovered = []

    for row in rows:
        for field_name in row.keys():
            if field_name not in discovered:
                discovered.append(field_name)

    fieldnames = [
        field_name
        for field_name in PREFERRED_MATCH_FIELDS
        if field_name in discovered
    ]

    for field_name in discovered:
        if field_name not in fieldnames:
            fieldnames.append(field_name)

    return fieldnames


def write_matches(matches, output_file):
    """
    Scrive una riga per prediction in 01_matches.csv.
    """
    if not matches:
        return

    fields = _collect_fieldnames(matches)

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:
        writer = csv.DictWriter(
            file_handle,
            fieldnames=fields,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(matches)


def write_drivers(matches, output_file):
    """
    Scrive una riga per driver e per prediction in 02_drivers.csv.
    """
    header = [
        "MatchId",
        "LeagueId",
        "PredictionDate",
        "MatchDate",
        "Home",
        "Away",
        "Band",
        "Outcome",
        "Score",
        "Driver",
        "Value",
    ]

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as file_handle:
        writer = csv.writer(
            file_handle,
            delimiter=";",
        )

        writer.writerow(header)

        for row in matches:
            for driver in DRIVERS:
                writer.writerow([
                    row.get("MatchId", ""),
                    row.get("LeagueId", ""),
                    row.get("PredictionDate", ""),
                    row.get("MatchDate", ""),
                    row.get("Home", ""),
                    row.get("Away", ""),
                    row.get("Band", ""),
                    row.get("Outcome", ""),
                    row.get("Score", ""),
                    driver,
                    row.get(driver, ""),
                ])
