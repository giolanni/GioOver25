"""Merge v25 predictions with the canonical match-results history."""

from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any
import csv

UNMATCHED_FILE = Path("analysis/laboratory/data/06_unmatched_matches.csv")


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_team(value: Any) -> str:
    # Keep the laboratory matching consistent with the project canonical form:
    # reserve-team suffix II is represented as 2.
    value = _text(value).replace("II", "2")
    return " ".join(value.casefold().split())


def _parse_date(value: Any) -> date | None:
    raw = _text(value)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _key(row: dict) -> tuple[str, str, str, str]:
    return (
        _text(row.get("LeagueId")),
        _text(row.get("MatchDate")),
        _normalize_team(row.get("Home")),
        _normalize_team(row.get("Away")),
    )


def _outcome(hg: Any, ag: Any) -> str:
    h, a = _text(hg), _text(ag)
    if not h or not a:
        return ""
    try:
        total = int(float(h.replace(",", "."))) + int(float(a.replace(",", ".")))
    except ValueError:
        return ""
    return "OK" if total >= 3 else "KO"


def _result_index(results: list[dict]) -> dict[tuple[str, str, str, str], dict]:
    index = {}
    for result in results:
        if _parse_date(result.get("MatchDate")) is None:
            continue
        if not _text(result.get("HG")) or not _text(result.get("AG")):
            continue
        index[_key(result)] = result
    return index


def _write_unmatched(rows: list[dict]) -> None:
    fields = [
        "LeagueId", "PredictionDate", "MatchDate", "Round", "Home", "Away",
        "Band", "Score", "Reason", "RankingSource", "ReasonUnmatched",
    ]
    UNMATCHED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with UNMATCHED_FILE.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def merge_matches(predictions: list[dict], results: list[dict]) -> list[dict]:
    """Attach the real result to every v25 prediction when an exact match exists.

    Match identity is strictly LeagueId + MatchDate + Home + Away. No league,
    date or team-pair fallback is used: a fallback could attach a result from a
    different fixture and silently corrupt the laboratory.
    """
    result_index = _result_index(results)
    merged = []
    unmatched = []
    concluded = 0
    scheduled = 0

    for prediction in predictions:
        row = deepcopy(prediction)
        result = result_index.get(_key(prediction))

        if result is not None:
            hg, ag = _text(result.get("HG")), _text(result.get("AG"))
            row["HG"] = hg
            row["AG"] = ag
            row["Goals"] = str(int(float(hg)) + int(float(ag)))
            row["Outcome"] = _outcome(hg, ag)
            row["MatchStatus"] = "FINAL"
            row["ResultSource"] = result.get("SourceFile", "")
            concluded += 1
        else:
            row["HG"] = ""
            row["AG"] = ""
            row["Goals"] = ""
            row["Outcome"] = ""
            row["MatchStatus"] = "SCHEDULED"
            row["ResultSource"] = ""
            scheduled += 1
            unmatched.append({
                "LeagueId": prediction.get("LeagueId", ""),
                "PredictionDate": prediction.get("PredictionDate", ""),
                "MatchDate": prediction.get("MatchDate", ""),
                "Round": prediction.get("Round", ""),
                "Home": prediction.get("Home", ""),
                "Away": prediction.get("Away", ""),
                "Band": prediction.get("Band", ""),
                "Score": prediction.get("Score", ""),
                "Reason": prediction.get("Reason", ""),
                "RankingSource": prediction.get("SourceFile", ""),
                "ReasonUnmatched": "NO_EXACT_RESULT",
            })

        row["MatchId"] = len(merged) + 1
        row["HistorySource"] = row.get("ResultSource", "")
        row["RankingSource"] = prediction.get("SourceFile", "")
        row["MatchMode"] = "EXACT_RESULT_KEY" if result is not None else "NO_RESULT"
        row["DateDifferenceDays"] = 0 if result is not None else ""
        merged.append(row)

    _write_unmatched(unmatched)

    print()
    print("===== LABORATORY MERGE =====")
    print(f"Predizioni caricate:       {len(predictions)}")
    print(f"Risultati caricati:        {len(results)}")
    print(f"Predizioni abbinate:       {concluded}")
    print(f"Match conclusi:             {concluded}")
    print(f"Match senza risultato:      {scheduled}")
    print(f"Righe non abbinate:         {scheduled}")
    print(f"Diagnostica:                {UNMATCHED_FILE}")
    print()
    return merged
