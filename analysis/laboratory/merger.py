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
    return (_text(row.get("LeagueId")), _text(row.get("MatchDate")),
            _normalize_team(row.get("Home")), _normalize_team(row.get("Away")))


def _round_team_key(row: dict) -> tuple[str, str, str, str]:
    return (_text(row.get("LeagueId")), _text(row.get("Round")),
            _normalize_team(row.get("Home")), _normalize_team(row.get("Away")))


def _outcome(hg: Any, ag: Any) -> str:
    h, a = _text(hg), _text(ag)
    if not h or not a:
        return ""
    try:
        total = int(float(h.replace(",", "."))) + int(float(a.replace(",", ".")))
    except ValueError:
        return ""
    return "OK" if total >= 3 else "KO"


def _result_index(results: list[dict]) -> tuple[dict, dict]:
    """Build exact and safe fallback indexes.

    The primary identity is LeagueId + MatchDate + Home + Away. A secondary
    index is retained only when LeagueId + Round + Home + Away identifies one
    and only one concluded result. It is used only when MatchDate is missing
    from the prediction, so old ranking rows can be recovered without guessing.
    """
    exact: dict[tuple[str, str, str, str], dict] = {}
    by_round: dict[tuple[str, str, str, str], list[dict]] = {}
    for result in results:
        if _parse_date(result.get("MatchDate")) is None:
            continue
        if not _text(result.get("HG")) or not _text(result.get("AG")):
            continue
        exact[_key(result)] = result
        by_round.setdefault(_round_team_key(result), []).append(result)
    unique_round = {key: rows[0] for key, rows in by_round.items() if len(rows) == 1}
    return exact, unique_round


def _write_unmatched(rows: list[dict]) -> None:
    fields = ["LeagueId", "PredictionDate", "MatchDate", "Round", "Home", "Away",
              "Band", "Score", "Reason", "RankingSource", "ReasonUnmatched"]
    UNMATCHED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with UNMATCHED_FILE.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def merge_matches(predictions: list[dict], results: list[dict]) -> list[dict]:
    """Attach real results using exact identity plus safe missing-date recovery."""
    exact_index, round_index = _result_index(results)
    merged, unmatched = [], []
    concluded = scheduled = exact_matches = round_fallback_matches = 0

    for prediction in predictions:
        row = deepcopy(prediction)
        result = exact_index.get(_key(prediction))
        match_mode = "EXACT_RESULT_KEY"

        if result is None and not _text(prediction.get("MatchDate")):
            result = round_index.get(_round_team_key(prediction))
            if result is not None:
                match_mode = "ROUND_TEAM_FALLBACK"

        if result is not None:
            hg, ag = _text(result.get("HG")), _text(result.get("AG"))
            row["HG"], row["AG"] = hg, ag
            row["Goals"] = str(int(float(hg)) + int(float(ag)))
            row["Outcome"] = _outcome(hg, ag)
            row["MatchStatus"] = "FINAL"
            row["ResultSource"] = result.get("SourceFile", "")
            row["MatchMode"] = match_mode
            row["DateDifferenceDays"] = 0 if match_mode == "EXACT_RESULT_KEY" else ""
            if match_mode == "ROUND_TEAM_FALLBACK":
                row["MatchDate"] = result.get("MatchDate", "")
                round_fallback_matches += 1
            else:
                exact_matches += 1
            concluded += 1
        else:
            row["HG"] = row["AG"] = row["Goals"] = row["Outcome"] = ""
            row["MatchStatus"] = "SCHEDULED"
            row["ResultSource"] = ""
            row["MatchMode"] = "NO_RESULT"
            row["DateDifferenceDays"] = ""
            scheduled += 1
            reason = ("NO_EXACT_RESULT_AND_NO_UNIQUE_ROUND_MATCH"
                      if not _text(prediction.get("MatchDate")) else "NO_EXACT_RESULT")
            unmatched.append({
                "LeagueId": prediction.get("LeagueId", ""),
                "PredictionDate": prediction.get("PredictionDate", ""),
                "MatchDate": prediction.get("MatchDate", ""),
                "Round": prediction.get("Round", ""),
                "Home": prediction.get("Home", ""), "Away": prediction.get("Away", ""),
                "Band": prediction.get("Band", ""), "Score": prediction.get("Score", ""),
                "Reason": prediction.get("Reason", ""),
                "RankingSource": prediction.get("SourceFile", ""),
                "ReasonUnmatched": reason,
            })

        row["MatchId"] = len(merged) + 1
        row["HistorySource"] = row.get("ResultSource", "")
        row["RankingSource"] = prediction.get("SourceFile", "")
        merged.append(row)

    _write_unmatched(unmatched)
    print()
    print("===== LABORATORY MERGE =====")
    print(f"Predizioni caricate:       {len(predictions)}")
    print(f"Risultati caricati:        {len(results)}")
    print(f"Predizioni abbinate:       {concluded}")
    print(f"  Exact MatchDate:         {exact_matches}")
    print(f"  Fallback Round+Teams:    {round_fallback_matches}")
    print(f"Match conclusi:             {concluded}")
    print(f"Match senza risultato:      {scheduled}")
    print(f"Righe non abbinate:         {scheduled}")
    print(f"Diagnostica:                {UNMATCHED_FILE}")
    print()
    return merged
