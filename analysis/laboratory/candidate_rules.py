"""
===============================================================================
GioOver2.5 - analysis/laboratory/candidate_rules.py
===============================================================================

SCOPO
-----
Genera automaticamente tutte le regole semplici del tipo

Driver >= soglia

Driver <= soglia

e ne misura l'efficacia.

INPUT

analysis/laboratory/data/02_drivers.csv

OUTPUT

analysis/laboratory/data/05_candidate_rules.csv

===============================================================================
"""

from collections import defaultdict
import csv
from pathlib import Path


INPUT = Path("analysis/laboratory/data/02_drivers.csv")

OUTPUT = Path("analysis/laboratory/data/05_candidate_rules.csv")


# ------------------------------------------------------------------


def to_float(v):

    try:

        return float(str(v).replace(",", "."))

    except:

        return None


# ------------------------------------------------------------------


rows = []

with open(INPUT, encoding="utf-8-sig") as f:

    reader = csv.DictReader(f, delimiter=";")

    for r in reader:

        value = to_float(r["Value"])

        if value is None:
            continue

        rows.append({

            "MatchId": r["MatchId"],

            "Driver": r["Driver"],

            "Value": value,

            "Band": r["Band"],

            "Outcome": r["Outcome"],

        })


# ------------------------------------------------------------------


driver_values = defaultdict(list)

for r in rows:

    driver_values[r["Driver"]].append(r["Value"])


# ------------------------------------------------------------------


rules = []


for driver, values in driver_values.items():

    thresholds = sorted(set(values))

    data = [x for x in rows if x["Driver"] == driver]

    for threshold in thresholds:

        #
        # <=
        #

        counters = {

            "ALTA_OK": 0,
            "ALTA_KO": 0,

            "MEDIA_OK": 0,
            "MEDIA_KO": 0,

        }

        occ = 0

        for r in data:

            if r["Value"] <= threshold:

                occ += 1

                key = f'{r["Band"]}_{r["Outcome"]}'

                if key in counters:

                    counters[key] += 1

        if occ:

            alta = counters["ALTA_OK"] + counters["ALTA_KO"]

            media = counters["MEDIA_OK"] + counters["MEDIA_KO"]

            rules.append({

                "Driver": driver,

                "Operator": "<=",

                "Threshold": threshold,

                "Occurrences": occ,

                **counters,

                "AltaHit":

                    round(
                        counters["ALTA_OK"] / alta,
                        4
                    ) if alta else "",

                "MediaHit":

                    round(
                        counters["MEDIA_OK"] / media,
                        4
                    ) if media else "",

            })

        #
        # >=
        #

        counters = {

            "ALTA_OK": 0,
            "ALTA_KO": 0,

            "MEDIA_OK": 0,
            "MEDIA_KO": 0,

        }

        occ = 0

        for r in data:

            if r["Value"] >= threshold:

                occ += 1

                key = f'{r["Band"]}_{r["Outcome"]}'

                if key in counters:

                    counters[key] += 1

        if occ:

            alta = counters["ALTA_OK"] + counters["ALTA_KO"]

            media = counters["MEDIA_OK"] + counters["MEDIA_KO"]

            rules.append({

                "Driver": driver,

                "Operator": ">=",

                "Threshold": threshold,

                "Occurrences": occ,

                **counters,

                "AltaHit":

                    round(
                        counters["ALTA_OK"] / alta,
                        4
                    ) if alta else "",

                "MediaHit":

                    round(
                        counters["MEDIA_OK"] / media,
                        4
                    ) if media else "",

            })


# ------------------------------------------------------------------


rules.sort(

    key=lambda x: (

        x["Driver"],

        x["Operator"],

        x["Threshold"],

    )

)


# ------------------------------------------------------------------


with open(

    OUTPUT,

    "w",

    newline="",

    encoding="utf-8-sig"

) as f:

    writer = csv.DictWriter(

        f,

        fieldnames=[

            "Driver",

            "Operator",

            "Threshold",

            "Occurrences",

            "ALTA_OK",

            "ALTA_KO",

            "MEDIA_OK",

            "MEDIA_KO",

            "AltaHit",

            "MediaHit",

        ],

        delimiter=";"

    )

    writer.writeheader()

    writer.writerows(rules)


print(len(rules), "candidate rules generated")