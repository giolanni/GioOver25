"""
===============================================================================
GioOver2.5 - analysis/laboratory/writer.py
===============================================================================

Scrittura del database del laboratorio.

Output:

01_matches.csv
02_drivers.csv

01_matches.csv
---------------
Una riga = una prediction.

02_drivers.csv
--------------
Una riga = un driver appartenente ad una prediction.

===============================================================================
"""

import csv


# ---------------------------------------------------------------------------


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

]


# ---------------------------------------------------------------------------


def write_matches(matches, output_file):

    if not matches:
        return

    #
    # Costruisce automaticamente l'header
    #

    fields = list(matches[0].keys())

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.DictWriter(

            f,

            fieldnames=fields,

            delimiter=";",

            extrasaction="ignore"

        )

        writer.writeheader()

        for row in matches:

            writer.writerow(row)


# ---------------------------------------------------------------------------


def write_drivers(matches, output_file):

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

        encoding="utf-8-sig"

    ) as f:

        writer = csv.writer(

            f,

            delimiter=";"

        )

        writer.writerow(header)

        for row in matches:

            for driver in DRIVERS:

                writer.writerow([

                    row.get("MatchId"),

                    row.get("LeagueId"),

                    row.get("PredictionDate"),

                    row.get("MatchDate"),

                    row.get("Home"),

                    row.get("Away"),

                    row.get("Band"),

                    row.get("Outcome"),

                    row.get("Score"),

                    driver,

                    row.get(driver),

                ])