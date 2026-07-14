"""
===============================================================================
GioOver2.5 - analysis/laboratory/loaders.py
===============================================================================

Caricamento dei file di input del laboratorio.

Legge:

- storico_ranking_v25.csv
- tutti i ranking presenti in data/output_ranking/v25

Normalizza le intestazioni.

Non effettua alcun matching.
===============================================================================
"""

from pathlib import Path
import csv


ALIASES = {

    "leagueid": "LeagueId",

    "predictiondate": "PredictionDate",
    "matchdate": "MatchDate",

    "round": "Round",

    "home": "Home",
    "away": "Away",

    "score": "Score",

    "band": "Band",

    "over25": "Outcome",

    "reason": "Reason",

    "rankinggapscore": "RankingGapScore",

    "homeattackscore": "HomeAttackScore",
    "awayattackscore": "AwayAttackScore",

    "homedefenseweaknessscore": "HomeDefenseWeaknessScore",
    "awaydefenseweaknessscore": "AwayDefenseWeaknessScore",

    "homelast10overscore": "HomeLast10OverScore",
    "awaylast10overscore": "AwayLast10OverScore",

    "homevenueoverscore": "HomeVenueOverScore",
    "awayvenueoverscore": "AwayVenueOverScore",

    "bttsprofilescore": "BTTSProfileScore",

    "algorithmversion": "AlgorithmVersion",

    "hg": "HG",
    "ag": "AG",

}


# ------------------------------------------------------------------


def normalize(name):

    if name is None:
        return ""

    key = name.replace("\ufeff", "").strip()

    return ALIASES.get(key.lower(), key)


# ------------------------------------------------------------------


def detect_delimiter(path):

    with open(path, encoding="utf-8-sig") as f:

        sample = f.read(4096)

    if sample.count(";") >= sample.count(","):
        return ";"

    return ","


# ------------------------------------------------------------------


def load_csv(path):

    rows = []

    delimiter = detect_delimiter(path)

    with open(path, encoding="utf-8-sig", newline="") as f:

        reader = csv.DictReader(f, delimiter=delimiter)

        for row in reader:

            current = {}

            for k, v in row.items():
                field = normalize(k)
                value = v.strip() if isinstance(v, str) else v

                # Non sovrascrive un valore già presente con un campo vuoto.
                if field in current:
                    existing = str(current.get(field, "") or "").strip()
                    incoming = str(value or "").strip()

                    if existing and not incoming:
                        continue

                current[field] = value

            current["SourceFile"] = str(path)

            rows.append(current)

    return rows


# ------------------------------------------------------------------


def load_history(path):

    print(f"History : {path}")

    return load_csv(path)


# ------------------------------------------------------------------


def load_rankings(folder):

    rows = []

    files = sorted(folder.rglob("*.csv"))

    print(f"Ranking files : {len(files)}")

    for file in files:

        rows.extend(load_csv(file))

    return rows