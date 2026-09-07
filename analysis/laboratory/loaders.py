"""
===============================================================================
GioOver2.5 - analysis/laboratory/loaders.py
===============================================================================

Caricamento dei file di input del laboratorio.

Legge:

- storico_ranking_v25.csv
- tutti i ranking presenti in data/output_ranking/v25

Normalizza le intestazioni.

Supporta anche gli storici ranking legacy privi di header.
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
    "outcome": "Outcome",
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
    "goals": "Goals",
    "matchstatus": "MatchStatus",
    "competitiongroup": "CompetitionGroup",
    "homesourceleagueid": "HomeSourceLeagueId",
    "awaysourceleagueid": "AwaySourceLeagueId",
    "matchmode": "MatchMode",
    "datedifferencedays": "DateDifferenceDays",
    "historysource": "HistorySource",
    "rankingsource": "RankingSource",
}


# Schema degli storici ranking prodotti dal sistema prima dell'introduzione
# degli header. L'ordine corrisponde esattamente alle colonne dei CSV legacy.
HEADERLESS_HISTORY_FIELDS = [
    "PredictionDate",
    "MatchDate",
    "LeagueId",
    "Round",
    "Home",
    "Away",
    "Score",
    "Band",
    "MatchStatus",
    "HG",
    "AG",
    "Goals",
    "Over25",
    "Outcome",
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
    "AlgorithmVersion",
    "CompetitionGroup",
    "HomeSourceLeagueId",
    "AwaySourceLeagueId",
]


def normalize(name):
    if name is None:
        return ""

    key = name.replace("\ufeff", "").strip()
    return ALIASES.get(key.lower(), key)


def detect_delimiter(path):
    with open(path, encoding="utf-8-sig") as f:
        sample = f.read(4096)

    if sample.count(";") >= sample.count(","):
        return ";"

    return ","


def _looks_like_header(fieldnames):
    normalized = {
        normalize(name)
        for name in (fieldnames or [])
    }
    return {
        "LeagueId",
        "PredictionDate",
        "MatchDate",
        "Home",
        "Away",
    }.issubset(normalized)


def load_csv(path, headerless_fields=None):
    rows = []
    delimiter = detect_delimiter(path)

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=delimiter)
        first = next(reader, None)

        if first is None:
            return rows

        # Gli storici ranking v25 presenti nel repository sono legacy e privi
        # di header. Se il primo record non è un'intestazione, lo interpretiamo
        # con lo schema storico canonico invece di perderlo come header.
        if headerless_fields and not _looks_like_header(first):
            records = [first]
            records.extend(reader)
            fieldnames = headerless_fields
        else:
            fieldnames = [normalize(name) for name in first]
            records = reader

        for values in records:
            current = {}

            for index, value in enumerate(values):
                if index >= len(fieldnames):
                    break

                field = normalize(fieldnames[index])
                value = value.strip() if isinstance(value, str) else value

                if field in current:
                    existing = str(current.get(field, "") or "").strip()
                    incoming = str(value or "").strip()
                    if existing and not incoming:
                        continue

                current[field] = value

            current["SourceFile"] = str(path)
            rows.append(current)

    return rows


def load_history(path):
    print(f"History : {path}")
    return load_csv(path, headerless_fields=HEADERLESS_HISTORY_FIELDS)


def load_rankings(folder):
    rows = []
    seen = set()

    files = sorted(folder.rglob("*.csv"))
    print(f"Ranking files : {len(files)}")

    for file in files:
        for row in load_csv(file):
            fingerprint = (
                row.get("PredictionDate", ""),
                row.get("MatchDate", ""),
                row.get("LeagueId", ""),
                row.get("Round", ""),
                row.get("Home", ""),
                row.get("Away", ""),
                row.get("Score", ""),
                row.get("Band", ""),
                row.get("AlgorithmVersion", ""),
            )

            if fingerprint in seen:
                continue

            seen.add(fingerprint)
            rows.append(row)

    print(f"Ranking unici : {len(rows)}")
    return rows
