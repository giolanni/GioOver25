"""
===============================================================================
GioOver2.5 - Loader doppia fonte con fallback MatchDate/PredictionDate
===============================================================================

SCOPO
-----
Unire storico ranking e ranking originali mantenendo i driver ex ante.

MATCHING
--------
Per ogni riga:
- se MatchDate è presente, usa LeagueId + MatchDate + Home + Away;
- altrimenti usa LeagueId + PredictionDate + Home + Away.

Il tipo di matching viene salvato in MatchMode.

FILE LETTI
----------
- data/storico/ranking/v25/storico_ranking_v25.csv
- data/output_ranking/v25/**/*.csv

LIMITAZIONI
-----------
Il fallback su PredictionDate è compatibilità legacy e potrà essere rimosso
quando tutti i ranking conterranno MatchDate.
===============================================================================
"""

from pathlib import Path
import csv
from typing import Dict, Iterable, List, Any, Tuple


COLUMN_ALIASES = {
    "leagueid": "LeagueId", "league_id": "LeagueId",
    "matchdate": "MatchDate", "match_date": "MatchDate",
    "predictiondate": "PredictionDate", "prediction_date": "PredictionDate",
    "home": "Home", "home_team": "Home",
    "away": "Away", "away_team": "Away",
    "band": "Band", "fascia": "Band", "ranking_band": "Band",
    "over25": "Outcome", "esito": "Outcome", "outcome": "Outcome",
    "score": "Score", "hg": "HG", "ag": "AG",
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
    "reason": "Reason",
}


def _canonical_name(name: str) -> str:
    clean = (name or "").strip().replace("\ufeff", "")
    return COLUMN_ALIASES.get(clean.lower(), clean)


def _detect_delimiter(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
    return ";" if sample.count(";") >= sample.count(",") else ","


def _iter_csv_files(input_path: Path) -> Iterable[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() == ".csv":
            yield input_path
        return
    if input_path.is_dir():
        yield from sorted(input_path.rglob("*.csv"))


def load_csv_records(input_path: Path) -> List[Dict[str, Any]]:
    records = []
    files = list(_iter_csv_files(input_path))
    if not files:
        raise FileNotFoundError(f"Nessun CSV trovato in: {input_path}")

    for path in files:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=_detect_delimiter(path))
            if not reader.fieldnames:
                continue
            for raw in reader:
                row = {
                    _canonical_name(k): (v.strip() if isinstance(v, str) else v)
                    for k, v in raw.items() if k is not None
                }
                row["SourceFile"] = str(path)
                records.append(row)
    return records


def _norm_text(value: Any) -> str:
    return str(value or "").strip()


def _key_and_mode(row: Dict[str, Any]) -> Tuple[Tuple[str, str, str, str], str]:
    match_date = _norm_text(row.get("MatchDate"))
    prediction_date = _norm_text(row.get("PredictionDate"))
    date_value = match_date or prediction_date
    mode = "MATCH_DATE" if match_date else "PREDICTION_DATE"
    return (
        _norm_text(row.get("LeagueId")),
        date_value,
        _norm_text(row.get("Home")),
        _norm_text(row.get("Away")),
    ), mode


def merge_history_with_rankings(history_rows, ranking_rows):
    ranking_index = {}
    ranking_modes = {}

    for row in ranking_rows:
        key, mode = _key_and_mode(row)
        ranking_index.setdefault(key, []).append(row)
        ranking_modes[id(row)] = mode

    merged = []
    unmatched_history = []
    matched_ranking_ids = set()

    for hrow in history_rows:
        key, history_mode = _key_and_mode(hrow)
        candidates = ranking_index.get(key, [])
        if not candidates:
            unmatched_history.append(hrow)
            continue

        rrow = candidates[0]
        matched_ranking_ids.add(id(rrow))
        combined = dict(rrow)

        for field in (
            "PredictionDate", "MatchDate", "LeagueId", "Round", "Home", "Away",
            "Score", "Band", "HG", "AG", "Goals", "Outcome", "BTTS", "Reason",
            "AlgorithmVersion"
        ):
            if field in hrow and _norm_text(hrow.get(field)):
                combined[field] = hrow[field]

        combined["HistorySourceFile"] = hrow.get("SourceFile", "")
        combined["RankingSourceFile"] = rrow.get("SourceFile", "")
        combined["SourceFile"] = hrow.get("SourceFile", "")
        combined["MatchMode"] = history_mode
        merged.append(combined)

    unmatched_rankings = [
        row for row in ranking_rows if id(row) not in matched_ranking_ids
    ]
    return merged, unmatched_history, unmatched_rankings
