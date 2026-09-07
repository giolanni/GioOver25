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
    return (_text(row.get("LeagueId")), _normalize_team(row.get("Home")), _normalize_team(row.get("Away")))


def _teams_key(row: dict) -> tuple[str, str]:
    return (_normalize_team(row.get("Home")), _normalize_team(row.get("Away")))


def _has_result(row: dict) -> bool:
    return bool(_text(row.get("HG")) and _text(row.get("AG")))


def _outcome(row: dict) -> str:
    """Restituisce sempre l'esito canonico OK/KO quando il risultato esiste."""
    hg, ag = _text(row.get("HG")), _text(row.get("AG"))
    if hg and ag:
        try:
            total = int(float(hg.replace(",", "."))) + int(float(ag.replace(",", ".")))
            return "OK" if total >= 3 else "KO"
        except ValueError:
            pass

    explicit = _text(row.get("Outcome") or row.get("Over25")).upper()
    if explicit in {"OK", "KO"}:
        return explicit
    return ""


def _band(row: dict) -> str:
    """Normalizza le varianti di fascia usate dai ranking nel dataset del laboratorio."""
    raw = _text(row.get("Band")).upper().replace(" ", "_").replace("-", "_")
    if raw in {"ALTA", "HIGH", "HA", "FASCIA_ALTA"} or raw.startswith("ALTA_") or raw.startswith("HIGH_"):
        return "ALTA"
    if raw in {"MEDIA", "MEDIUM", "M", "FASCIA_MEDIA"} or raw.startswith("MEDIA_") or raw.startswith("MEDIUM_"):
        return "MEDIA"
    return _text(row.get("Band"))


def _status(row: dict) -> str:
    return _text(row.get("MatchStatus")).upper()


def _date_distance(a: dict, b: dict) -> int:
    da, db = _reference_date(a), _reference_date(b)
    if da is None or db is None:
        return 999999
    return abs((da - db).days)


def build_index(rankings: list[dict]) -> dict[tuple[str, str, str], list[dict]]:
    index: dict[tuple[str, str, str], list[dict]] = {}
    for ranking in rankings:
        index.setdefault(_base_key(ranking), []).append(ranking)
    return index


def _score_candidate(history: dict, ranking: dict, fallback: bool = False) -> tuple:
    hs, rs = _status(history), _status(ranking)
    history_final = hs == "FINAL" or _has_result(history)
    history_postponed = hs == "POSTPONED"
    status_penalty = int(rs == "POSTPONED") if history_final else int(rs != "POSTPONED") if history_postponed else 0
    hr, rr = _text(history.get("Round")), _text(ranking.get("Round"))
    hpd, rpd = _text(history.get("PredictionDate")), _text(ranking.get("PredictionDate"))
    hmd, rmd = _text(history.get("MatchDate")), _text(ranking.get("MatchDate"))
    hscore, rscore = _text(history.get("Score")), _text(ranking.get("Score"))
    hband, rband = _text(history.get("Band")), _text(ranking.get("Band"))
    halg, ralg = _text(history.get("AlgorithmVersion")), _text(ranking.get("AlgorithmVersion"))
    return (
        1 if fallback else 0,
        status_penalty,
        int(not (hr and rr and hr == rr)),
        int(not (hpd and rpd and hpd == rpd)),
        int(not (hmd and rmd and hmd == rmd)),
        int(not (hscore and rscore and hscore == rscore)),
        int(not (hband and rband and hband == rband)),
        int(not (halg and ralg and halg == ralg)),
        _date_distance(history, ranking),
    )


def _match_mode(history: dict, ranking: dict) -> str:
    if _text(history.get("PredictionDate")) and _text(history.get("PredictionDate")) == _text(ranking.get("PredictionDate")):
        return "PREDICTION_DATE"
    if _text(history.get("MatchDate")) and _text(history.get("MatchDate")) == _text(ranking.get("MatchDate")):
        return "MATCH_DATE"
    if _text(history.get("Round")) and _text(history.get("Round")) == _text(ranking.get("Round")):
        return "ROUND"
    return "DETERMINISTIC_TIEBREAK"


def _choose(scored: list[tuple[tuple, dict]]) -> dict | None:
    scored.sort(key=lambda item: item[0])
    best_score = scored[0][0]
    best = [ranking for score, ranking in scored if score == best_score]
    return best[0] if len(best) == 1 else None


def _find_ranking(history: dict, ranking_index: dict, team_index: dict) -> tuple[dict | None, str, int | None, str, int]:
    exact = ranking_index.get(_base_key(history), [])
    if exact:
        ranking = _choose([(_score_candidate(history, r, False), r) for r in exact])
        if ranking is not None:
            distance = _date_distance(history, ranking)
            return ranking, _match_mode(history, ranking), None if distance == 999999 else distance, "", len(exact)

    candidates = team_index.get(_teams_key(history), [])
    if candidates:
        scored = [(_score_candidate(history, r, True), r) for r in candidates]
        scored.sort(key=lambda item: item[0])
        best_score = scored[0][0]
        best = [r for score, r in scored if score == best_score]
        if len(best) == 1:
            ranking = best[0]
            distance = _date_distance(history, ranking)
            if distance == 999999 or distance <= 14:
                return ranking, "LEAGUE_FALLBACK_" + _match_mode(history, ranking), None if distance == 999999 else distance, "", len(candidates)

    return None, "", None, "NO_RANKING_CANDIDATE", len(candidates) if candidates else len(exact)


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

    merged, unmatched = [], []
    counters = {"PREDICTION_DATE": 0, "MATCH_DATE": 0, "ROUND": 0, "DETERMINISTIC_TIEBREAK": 0, "LEAGUE_FALLBACK": 0}

    for history_row in history:
        ranking, mode, distance, reason, candidates = _find_ranking(history_row, ranking_index, team_index)
        if ranking is None:
            unmatched.append({
                "LeagueId": history_row.get("LeagueId", ""), "PredictionDate": history_row.get("PredictionDate", ""),
                "MatchDate": history_row.get("MatchDate", ""), "Round": history_row.get("Round", ""),
                "Home": history_row.get("Home", ""), "Away": history_row.get("Away", ""), "Band": _band(history_row),
                "Outcome": _outcome(history_row), "HG": history_row.get("HG", ""), "AG": history_row.get("AG", ""),
                "MatchStatus": history_row.get("MatchStatus", ""), "Reason": reason, "BaseCandidates": candidates,
                "HistorySource": history_row.get("SourceFile", ""),
            })
            continue

        row = deepcopy(ranking)
        for field in ("PredictionDate", "MatchDate", "LeagueId", "Round", "Home", "Away", "Score", "HG", "AG", "Goals", "BTTS", "Reason", "AlgorithmVersion", "MatchStatus", "CompetitionGroup", "HomeSourceLeagueId", "AwaySourceLeagueId"):
            value = history_row.get(field, "")
            if _text(value):
                row[field] = value

        # Canonical values are required by all downstream Laboratory reports.
        row["Band"] = _band(history_row) or _band(ranking)
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
