"""
===============================================================================
GioOver2.5 - backfill_ranking_history_data.py
===============================================================================

SCOPO
-----
Bonificare lo storico ranking v25 copiando nei record storici i dati ex ante
presenti nei file ranking originali.

FILE LETTI
----------
- data/storico/ranking/v25/storico_ranking_v25.csv
- data/output_ranking/v25/**/*.csv

FILE SCRITTI
-------------
- data/storico/ranking/v25/storico_ranking_v25_backfilled.csv
- data/debug/history_backfill/matched.csv
- data/debug/history_backfill/unmatched.csv
- data/debug/history_backfill/ambiguous.csv
- data/debug/history_backfill/conflicts.csv

LOGICA DI MATCHING
------------------
LeagueId + Home + Away e una data entro una finestra configurabile.
Usa MatchDate quando presente, altrimenti PredictionDate.
Default: ±2 giorni.

MODALITÀ D'USO
--------------
python -m analysis.history.backfill_ranking_history_data
python -m analysis.history.backfill_ranking_history_data --days 3
python -m analysis.history.backfill_ranking_history_data --replace
===============================================================================
"""

from __future__ import annotations

from argparse import ArgumentParser
from collections import defaultdict
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import csv
import shutil

DEFAULT_HISTORY = Path("data/storico/ranking/v25/storico_ranking_v25.csv")
DEFAULT_RANKINGS = Path("data/output_ranking/v25")
DEFAULT_OUTPUT = Path("data/storico/ranking/v25/storico_ranking_v25_backfilled.csv")
DEFAULT_DEBUG = Path("data/debug/history_backfill")

FINAL_FIELDS = {"HG", "AG", "Goals", "Outcome", "Over25", "BTTS"}
KEY_FIELDS = {"LeagueId", "Home", "Away"}

ALIASES = {
    "leagueid": "LeagueId", "league_id": "LeagueId",
    "matchdate": "MatchDate", "match_date": "MatchDate",
    "predictiondate": "PredictionDate", "prediction_date": "PredictionDate",
    "home": "Home", "home_team": "Home",
    "away": "Away", "away_team": "Away",
    "band": "Band", "fascia": "Band",
    "over25": "Outcome", "outcome": "Outcome", "esito": "Outcome",
    "score": "Score", "round": "Round", "hg": "HG", "ag": "AG",
    "goals": "Goals", "btts": "BTTS", "reason": "Reason",
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
}

@dataclass
class MatchCandidate:
    row: Dict[str, Any]
    source_file: str
    date_value: datetime
    distance_days: int


def _canonical(name: str) -> str:
    clean = (name or "").replace("\ufeff", "").strip()
    return ALIASES.get(clean.lower(), clean)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _norm_name(value: Any) -> str:
    return " ".join(_text(value).casefold().split())


def _detect_delimiter(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
    return ";" if sample.count(";") >= sample.count(",") else ","


def _iter_csv_files(path: Path) -> Iterable[Path]:
    if path.is_file():
        if path.suffix.lower() == ".csv":
            yield path
        return
    if path.is_dir():
        yield from sorted(path.rglob("*.csv"))


def load_csv(path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    rows: List[Dict[str, Any]] = []
    delimiter = _detect_delimiter(path)
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        fields = [_canonical(x) for x in (reader.fieldnames or [])]
        for raw in reader:
            row = {
                _canonical(k): (v.strip() if isinstance(v, str) else v)
                for k, v in raw.items() if k is not None
            }
            row["__SourceFile"] = str(path)
            rows.append(row)
    return rows, fields


def load_many(path: Path) -> List[Dict[str, Any]]:
    files = list(_iter_csv_files(path))
    if not files:
        raise FileNotFoundError(f"Nessun CSV trovato in: {path}")
    rows: List[Dict[str, Any]] = []
    for file in files:
        current, _ = load_csv(file)
        rows.extend(current)
    return rows


def parse_date(value: Any) -> Optional[datetime]:
    text = _text(value)
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass
    return None


def row_date(row: Dict[str, Any]) -> Optional[datetime]:
    return parse_date(row.get("MatchDate")) or parse_date(row.get("PredictionDate"))


def base_key(row: Dict[str, Any]) -> Tuple[str, str, str]:
    return (_norm_name(row.get("LeagueId")), _norm_name(row.get("Home")), _norm_name(row.get("Away")))


def build_index(rows: List[Dict[str, Any]]) -> Dict[Tuple[str, str, str], List[Dict[str, Any]]]:
    index: Dict[Tuple[str, str, str], List[Dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if all(_text(row.get(f)) for f in KEY_FIELDS):
            index[base_key(row)].append(row)
    return index


def find_candidate(history_row: Dict[str, Any], index, max_days: int):
    hdate = row_date(history_row)
    if hdate is None:
        return "NO_HISTORY_DATE", None, []
    candidates: List[MatchCandidate] = []
    for r in index.get(base_key(history_row), []):
        rdate = row_date(r)
        if rdate is None:
            continue
        distance = abs((hdate.date() - rdate.date()).days)
        if distance <= max_days:
            candidates.append(MatchCandidate(r, _text(r.get("__SourceFile")), rdate, distance))
    if not candidates:
        return "UNMATCHED", None, []
    candidates.sort(key=lambda x: (x.distance_days, x.date_value, x.source_file))
    best_distance = candidates[0].distance_days
    best = [x for x in candidates if x.distance_days == best_distance]
    if len(best) > 1:
        return "AMBIGUOUS", None, best
    return "MATCHED", best[0], candidates


def merge_row(history_row, ranking_row, overwrite: bool):
    merged = deepcopy(history_row)
    conflicts = []
    copied = 0
    for field, value in ranking_row.items():
        if field.startswith("__") or field in FINAL_FIELDS or field in KEY_FIELDS:
            continue
        source = _text(value)
        if not source:
            continue
        current = _text(merged.get(field))
        if not current:
            merged[field] = value
            copied += 1
        elif current != source:
            conflicts.append((field, current, source))
            if overwrite:
                merged[field] = value
                copied += 1
    return merged, conflicts, copied


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def output_fields(history_fields, ranking_rows):
    fields = list(history_fields)
    for row in ranking_rows:
        for field in row:
            if not field.startswith("__") and field not in fields:
                fields.append(field)
    return fields


def backup_history(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder = path.parent / "backup"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"{path.stem}_{stamp}.csv"
    shutil.copy2(path, target)
    return target


def build_parser():
    p = ArgumentParser()
    p.add_argument("--history", type=Path, default=DEFAULT_HISTORY)
    p.add_argument("--rankings", type=Path, default=DEFAULT_RANKINGS)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--debug", type=Path, default=DEFAULT_DEBUG)
    p.add_argument("--days", type=int, default=2)
    p.add_argument("--replace", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    return p


def main() -> int:
    args = build_parser().parse_args()
    history_rows, history_fields = load_csv(args.history)
    ranking_rows = load_many(args.rankings)
    index = build_index(ranking_rows)

    output_rows = []
    matched = []
    unmatched = []
    ambiguous = []
    conflicts_report = []
    copied_total = 0

    for row_id, hrow in enumerate(history_rows, start=1):
        status, candidate, considered = find_candidate(hrow, index, args.days)
        if status == "MATCHED":
            merged, conflicts, copied = merge_row(hrow, candidate.row, args.overwrite)
            output_rows.append(merged)
            copied_total += copied
            matched.append({
                "RowId": row_id, "LeagueId": hrow.get("LeagueId", ""), "Home": hrow.get("Home", ""),
                "Away": hrow.get("Away", ""), "HistoryDate": hrow.get("MatchDate") or hrow.get("PredictionDate", ""),
                "RankingDate": candidate.row.get("MatchDate") or candidate.row.get("PredictionDate", ""),
                "DistanceDays": candidate.distance_days, "RankingSource": candidate.source_file,
                "CopiedFields": copied,
            })
            for field, old, new in conflicts:
                conflicts_report.append({
                    "RowId": row_id, "LeagueId": hrow.get("LeagueId", ""), "Home": hrow.get("Home", ""),
                    "Away": hrow.get("Away", ""), "Field": field, "HistoryValue": old,
                    "RankingValue": new, "RankingSource": candidate.source_file,
                    "Overwritten": "YES" if args.overwrite else "NO",
                })
        else:
            output_rows.append(deepcopy(hrow))
            if status == "AMBIGUOUS":
                for item in considered:
                    ambiguous.append({
                        "RowId": row_id, "LeagueId": hrow.get("LeagueId", ""), "Home": hrow.get("Home", ""),
                        "Away": hrow.get("Away", ""), "CandidateDate": item.row.get("MatchDate") or item.row.get("PredictionDate", ""),
                        "DistanceDays": item.distance_days, "RankingSource": item.source_file,
                    })
            else:
                unmatched.append({
                    "RowId": row_id, "Status": status, "LeagueId": hrow.get("LeagueId", ""),
                    "Home": hrow.get("Home", ""), "Away": hrow.get("Away", ""),
                    "MatchDate": hrow.get("MatchDate", ""), "PredictionDate": hrow.get("PredictionDate", ""),
                })

    write_csv(args.output, output_rows, output_fields(history_fields, ranking_rows))
    write_csv(args.debug / "matched.csv", matched, ["RowId","LeagueId","Home","Away","HistoryDate","RankingDate","DistanceDays","RankingSource","CopiedFields"])
    write_csv(args.debug / "unmatched.csv", unmatched, ["RowId","Status","LeagueId","Home","Away","MatchDate","PredictionDate"])
    write_csv(args.debug / "ambiguous.csv", ambiguous, ["RowId","LeagueId","Home","Away","CandidateDate","DistanceDays","RankingSource"])
    write_csv(args.debug / "conflicts.csv", conflicts_report, ["RowId","LeagueId","Home","Away","Field","HistoryValue","RankingValue","RankingSource","Overwritten"])

    if args.replace:
        backup = backup_history(args.history)
        shutil.copy2(args.output, args.history)
        print(f"Backup creato: {backup}")

    print(f"Righe storico: {len(history_rows)}")
    print(f"Righe ranking: {len(ranking_rows)}")
    print(f"Righe abbinate: {len(matched)}")
    print(f"Campi copiati: {copied_total}")
    print(f"Non abbinate: {len(unmatched)}")
    print(f"Ambigue: {len(ambiguous)}")
    print(f"Conflitti: {len(conflicts_report)}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
