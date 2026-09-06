"""Merge v25 history with original rankings for Laboratory."""

from copy import deepcopy
from datetime import date
from pathlib import Path
from typing import Any
import csv

UNMATCHED_FILE = Path("analysis/laboratory/data/06_unmatched_matches.csv")


def _text(value: Any) -> str:
    return str(value or "").strip()


def _normalize_team(value: Any) -> str:
    return " ".join(_text(value).casefold().split())


def _parse_date(value: Any) -> date | None:
    raw = _text(value)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _reference_date(row: dict) -> date | None:
    return _parse_date(row.get("MatchDate")) or _parse_date(row.get("PredictionDate"))


def _base_key(row: dict) -> tuple[str, str, str]:
    return (
        _text(row.get("LeagueId")),
        _normalize_team(row.get("Home")),
        _normalize_team(row.get("Away")),
    )


def _teams_key(row: dict) -> tuple[str, str]:
    return (_normalize_team(row.get("Home")), _normalize_team(row.get("Away")))


def _has_result(row: dict) -> bool:
    return bool(_text(row.get("HG")) and _text(row.get("AG")))


def _outcome(row: dict) -> str:
    explicit = _text(row.get("Outcome") or row.get("Over25")).upper()
    if explicit in {"OK", "KO"}:
        return explicit
    hg = _text(row.get("HG"))
    ag = _text(row.get("AG"))
    if hg and ag:
        try:
            return "OK" if int(float(hg.replace(",", "."))) + int(float(ag.replace(",", "."))) >= 3 else "KO"
        except ValueError:
            pass
    goals = _text(row.get("Goals"))
    if goals:
        try:
            return "OK" if float(goals.replace(",", ".")) >= 3 else "KO"
        except ValueError:
            pass
    return ""


def _status(row: dict) -> str:
    return _text(row.get("MatchStatus")).upper()


def _date_distance(a: dict, b: dict) -> int:
    da = _reference_date(a)
    db = _reference_date(b)
    if da is None or db is None:
        return 999999
    return abs((da - db).days)


def build_index(rankings: list[dict]) -> dict[tuple[str, str, str], list[dict]]:
    index: dict[tuple[str, str, str], list[dict]] = {}
    for ranking in rankings:
        index.setdefault(_base_key(ranking), []).append(ranking)
    return index


def _score_candidate(history: dict, ranking: dict, fallback: bool = False) -> tuple:
    hs = _status(history)
    rs = _status(ranking)
    history_final = hs == "FINAL" or _has_result(history)
    history_postponed = hs == "POSTPONED"

    if history_final:
        status_penalty = int(rs == "POSTPONED")
    elif history_postponed:
        status_penalty = int(rs != "POSTPONED")
    else:
        status_penalty = 0

    hr = _text(history.get("Round"))
    rr = _text(ranking.get("Round"))
    hpd = _text(history.get("PredictionDate"))
    rpd = _text(ranking.get("PredictionDate"))
    hmd = _text(history.get("MatchDate"))
    rmd = _text(ranking.get("MatchDate"))
    hscore = _text(history.get("Score"))
    rscore = _text(ranking.get("Score"))
    hband = _text(history.get("Band"))
    rband = _text(ranking.get("Band"))
    halg = _text(history.get("AlgorithmVersion"))
    ralg = _text(ranking.get("AlgorithmVersion"))

    # Exact league matches always outrank fallback team/date matches.
    league_penalty = int(_text(history.get("LeagueId")) != _text(ranking.get("LeagueId")))

    return (
        league_penalty if not fallback else 1,
        status_penalty,
        int(not (hr and rr and hr == rr)),
        int(not (hpd and rpd and hpd == rpd)),
        int(not (hmd and rmd and hmd == rmd)),
        int(not (hscore and rscore and hscore == rscore)),
        int(not (hband and rband and hband == rband)),
        int(not (halg and ralg and halg == ralg)),
        _date_distance(history, ranking),
    )


def _find_ranking(history: dict, ranking_index: dict, team_index: dict) -> tuple[dict | None, str, int | None, str, int]:
    exact = ranking_index.get(_base_key(history), [])

    if exact:
        scored = sorted((_score_candidate(history, r, False), r) for r in exact)
        best_score = scored[0][0]
        best = [r for score, r in scored if score == best_score]
        if len(best) == 1:
            r = best[0]
            distance = _date_distance(history, r)
            return r, _match_mode(history, r), None if distance == 999999 else distance, "", len(exact)

    # IMPORTANT: historical LeagueIds can differ from the canonical registry IDs.
    # If exact LeagueId matching fails, recover the prediction by Home/Away and
    # temporal identity. This is the critical fallback for migrated registry IDs.
    candidates = team_index.get(_teams_key(history), [])
    if candidates:
        scored = sorted((_score_candidate(history, r, True), r) for r in candidates)
        best_score = scored[0][0]
        best = [r for score, r in scored if score == best_score]
        if len(best) == 1:
            r = best[0]
            distance = _date_distance(history, r)
            # Do not accept a completely unrelated prediction when dates exist.
            if distance == 999999 or distance <= 14:
                return r, "LEAGUE_FALLBACK_" + _match_mode(history, r), None if distance == 999999 else distance, "", len(candidates)
        
    return None, "", None, "NO_RANKING_CANDIDATE", len(candidates) if candidates else len(exact)


def _match_mode(history: dict, ranking: dict) -> str:
    if _text(history.get("PredictionDate")) and _text(history.get("PredictionDate")) == _text(ranking.get("PredictionDate")):
        return "PREDICTION_DATE"
    if _text(history.get("MatchDate")) and _text(history.get("MatchDate")) == _text(ranking.get("MatchDate")):
        return "MATCH_DATE"
    if _text(history.get("Round")) and _text(history.get("Round")) == _text(ranking.get("Round")):
        return "ROUND"
    return "DETERMINISTIC_TIEBREAK"


def _write_unmatched(rows: list[dict]) -> None:
    fields = ["LeagueId", "PredictionDate", "MatchDate", "Round", "Home", "Away", "Band", "Outcome", "HG", "AG", "MatchStatus", "Reason", "BaseCandidates", "HistorySource"]
    UNMATCHED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with UNMATCHED_FILE.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def merge_matches(history: list[dict], rankings: list[dict]) -> list[dict]:
    ranking_index = build_index(rankings)
    team_index: dict[tuple[str, str], list[dict]] = {}
    for ranking in rankings:
        team_index.setdefault(_teams_key(ranking), []).append(ranking)

    merged: list[dict] = []
    unmatched: list[dict] = []
    counters = {"PREDICTION_DATE": 0, "MATCH_DATE": 0, "ROUND": 0, "DETERMINISTIC_TIEBREAK": 0, "LEAGUE_FALLBACK": 0}

    for history_row in history:
        ranking, mode, distance, reason, candidates = _find_ranking(history_row, ranking_index, team_index)
        if ranking is None:
            unmatched.append({
                "LeagueId": history_row.get("LeagueId", ""),
                "PredictionDate": history_row.get("PredictionDate", ""),
                "MatchDate": history_row.get("MatchDate", ""),
                "Round": history_row.get("Round", ""),
                "Home": history_row.get("Home", ""),
                "Away": history_row.get("Away", ""),
                "Band": history_row.get("Band", ""),
                "Outcome": _outcome(history_row),
                "HG": history_row.get("HG", ""),
                "AG": history_row.get("AG", ""),
                "MatchStatus": history_row.get("MatchStatus", ""),
                "Reason": reason,
                "BaseCandidates": candidates,
                "HistorySource": history_row.get("SourceFile", ""),
            })
            continue

        row = deepcopy(ranking)
        for field in (
            "PredictionDate", "MatchDate", "LeagueId", "Round", "Home", "Away", "Score", "Band",
            "HG", "AG", "Goals", "BTTS", "Reason", "AlgorithmVersion", "MatchStatus",
            "CompetitionGroup", "HomeSourceLeagueId", "AwaySourceLeagueId",
        ):
            value = history_row.get(field, "")
            if _text(value):
                row[field] = value

        # Always provide Outcome. Prefer the stored result, then derive it from HG/AG.
        row["Outcome"] = _outcome(history_row)
        row["HistorySource"] = history_row.get("SourceFile", "")
        row["RankingSource"] = ranking.get("SourceFile", "")
        row["MatchMode"] = mode
        row["DateDifferenceDays"] = "" if distance is None else distance
        row["MatchId"] = len(merged) + 1
        merged.append(row)

        base_mode = mode.replace("LEAGUE_FALLBACK_", "")
        counters[base_mode] = counters.get(base_mode, 0) + 1
        if mode.startswith("LEAGUE_FALLBACK_"):
            counters["LEAGUE_FALLBACK"] += 1

    _write_unmatched(unmatched)

    print()
    print("===== LABORATORY MERGE =====")
    print(f"Storico caricato:          {len(history)}")
    print(f"Ranking caricati:          {len(rankings)}")
    print(f"Righe abbinate:            {len(merged)}")
    print(f"Match PredictionDate:      {counters.get('PREDICTION_DATE', 0)}")
    print(f"Match MatchDate:           {counters.get('MATCH_DATE', 0)}")
    print(f"Match Round:               {counters.get('ROUND', 0)}")
    print(f"Match tie-break:           {counters.get('DETERMINISTIC_TIEBREAK', 0)}")
    print(f"Match fallback LeagueId:   {counters.get('LEAGUE_FALLBACK', 0)}")
    print(f"Righe non abbinate:        {len(unmatched)}")
    print(f"Diagnostica:               {UNMATCHED_FILE}")
    print()
    return merged
