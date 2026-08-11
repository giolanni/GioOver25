"""
===============================================================================
GioOver2.5 - EXPERIMENT v20 RECENT WINDOWS
===============================================================================

OBIETTIVO
---------
Confrontare lo stesso v20 usando, come unico cambiamento, finestre recenti:

    Last10  <- baseline reale v20
    Last9
    Last8
    Last7
    Last6
    Last5

Tutti gli altri driver e pesi restano IDENTICI.

IMPORTANTE
----------
Lo script ricalcola DAVVERO il v20 storico dai risultati precedenti alla
MatchDate. Non dipende dai vecchi campi score eventualmente vuoti nello
storico_ranking.

PARAMETRI MODIFICABILI
----------------------
WINDOWS = (10, 9, 8, 7, 6, 5)

Puoi aggiungere, ad esempio, Last4:
    WINDOWS = (10, 9, 8, 7, 6, 5, 4)

ESECUZIONE
----------
python -m analysis.experiments.v20_recent_windows_experiment

OUTPUT
------
analysis/experiments/v20_recent_windows/

01_window_overall.csv
    Classifica delle finestre per %OK ALTA.

02_window_no_australia.csv
    Stesso confronto senza Australia_*.

03_transitions_vs_last10.csv
    Per ogni finestra: ALTA mantenute, eliminate, aggiunte.

04_removed_from_alta.csv
    Dettaglio partite ALTA Last10 che ogni finestra elimina.

05_added_to_alta.csv
    Dettaglio nuove ALTA introdotte da ogni finestra.

06_match_details.csv
    Tutti gli score/band per ogni finestra.

07_unmatched.csv
    Partite non ricostruibili.

08_parity_check.csv
    Score storico v20 vs Last10 ricalcolato.

CRITERIO
--------
L'output 01 viene ordinato:
    1. % OK ALTA decrescente
    2. KO crescente
    3. totale decrescente
===============================================================================
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pandas as pd

from gioover25.match_statistics import build_match_statistics
from gioover25.registry import get_league_info
from gioover25.scoring_v2 import calculate_score_v2, band_from_score
from gioover25.rank_matches_v2 import (
    read_registry,
    get_competition_group,
    get_group_league_ids,
    load_group_histories,
    find_team_source_league,
    infer_next_round,
)
from gioover25.team_names import normalize_team_name


V20_HISTORY = Path("data/storico/ranking/v20/storico_ranking_v20.csv")
VALID_OUTCOMES = {"OK", "KO"}


def detect_delimiter(path: Path) -> str:
    sample = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )[:4096]
    try:
        return csv.Sniffer().sniff(
            sample,
            delimiters=";,\t,",
        ).delimiter
    except csv.Error:
        return ";"


def read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=detect_delimiter(path),
        encoding="utf-8-sig",
        low_memory=False,
        dtype=str,
    )


def parse_date(value) -> date | None:
    raw = str(value or "").strip()
    if not raw or raw.lower() == "nan":
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def optional_int(value) -> int | None:
    raw = str(value or "").strip()
    if not raw or raw.lower() == "nan":
        return None
    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return None


def safe_float(value, default=0.0) -> float:
    raw = str(value or "").strip().replace(",", ".")
    if not raw or raw.lower() == "nan":
        return default
    try:
        return float(raw)
    except (TypeError, ValueError):
        return default


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko
    return round(ok / total * 100.0, 4) if total else 0.0


def match_date_of(match) -> date | None:
    return parse_date(getattr(match, "date", ""))


def outcome_from_row(row: pd.Series) -> str:
    raw = str(row.get("Over25", "")).strip().upper()
    if raw in VALID_OUTCOMES:
        return raw

    hg = optional_int(row.get("HG"))
    ag = optional_int(row.get("AG"))

    if hg is None or ag is None:
        return ""

    return "OK" if hg + ag >= 3 else "KO"


def filter_histories_before(histories: dict[str, list], before_date: date) -> dict[str, list]:
    filtered: dict[str, list] = {}

    for league_id, matches in histories.items():
        previous = []
        for match in matches:
            current_date = match_date_of(match)
            if current_date is not None and current_date < before_date:
                previous.append(match)

        if previous:
            filtered[league_id] = previous

    return filtered


def goal_pair(match) -> tuple[int, int] | None:
    pairs = (
        ("home_goals", "away_goals"),
        ("hg", "ag"),
        ("home_score", "away_score"),
    )

    for home_field, away_field in pairs:
        hg = getattr(match, home_field, None)
        ag = getattr(match, away_field, None)

        if hg in (None, "") or ag in (None, ""):
            continue

        try:
            return int(hg), int(ag)
        except (TypeError, ValueError):
            continue

    return None


def recent_over_rate_from_source(
    *,
    source_league_id: str,
    team: str,
    histories_before: dict[str, list],
    last_n: int,
) -> tuple[float, int, str]:
    matches = histories_before.get(source_league_id, [])
    canonical_team = normalize_team_name(source_league_id, team)

    sequence: list[int] = []

    for match in sorted(
        matches,
        key=lambda item: match_date_of(item) or date.min,
    ):
        home = normalize_team_name(
            source_league_id,
            getattr(match, "home", ""),
        )
        away = normalize_team_name(
            source_league_id,
            getattr(match, "away", ""),
        )

        if canonical_team not in {home, away}:
            continue

        goals = goal_pair(match)
        if goals is None:
            continue

        hg, ag = goals
        sequence.append(1 if hg + ag >= 3 else 0)

    selected = sequence[-last_n:]

    if not selected:
        return 0.0, 0, ""

    return (
        sum(selected) / len(selected),
        len(selected),
        "".join(str(value) for value in selected),
    )


def build_historical_v20_base(
    *,
    league_id: str,
    home: str,
    away: str,
    match_date: date,
    registry_rows: list[dict],
    history_cache: dict[str, dict[str, list]],
):
    """
    Ricostruisce DAVVERO lo score v20 alla data della prediction.

    Non usa i contributi eventualmente mancanti nello storico_ranking.
    Ricarica gli storici risultati, elimina tutte le gare >= MatchDate,
    ricostruisce MatchStatistics e richiama calculate_score_v2().
    """
    league_info = get_league_info(league_id)

    competition_group = get_competition_group(
        league_id,
        registry_rows,
    )

    group_league_ids = get_group_league_ids(
        league_id,
        competition_group,
        registry_rows,
    )

    cache_key = "||".join(group_league_ids)

    if cache_key not in history_cache:
        history_cache[cache_key] = load_group_histories(
            group_league_ids
        )

    all_histories = history_cache[cache_key]

    if not all_histories:
        raise FileNotFoundError(
            f"Nessuno storico risultati per {league_id}"
        )

    histories_before = filter_histories_before(
        all_histories,
        match_date,
    )

    if not histories_before:
        raise ValueError(
            f"Nessuno storico precedente al {match_date} per {league_id}"
        )

    fallback_league_id = (
        league_id
        if not competition_group
        else None
    )

    home_source = find_team_source_league(
        home,
        all_histories,
        match_date,
        fallback_league_id=fallback_league_id,
    )

    away_source = find_team_source_league(
        away,
        all_histories,
        match_date,
        fallback_league_id=fallback_league_id,
    )

    statistics_matches = [
        match
        for source_matches in histories_before.values()
        for match in source_matches
    ]

    if not statistics_matches:
        raise ValueError(
            f"Nessuna partita precedente utilizzabile per {league_id}"
        )

    before_round = infer_next_round(
        statistics_matches
    )

    match_stats = build_match_statistics(
        matches=statistics_matches,
        home_team=home,
        away_team=away,
        before_round=before_round,
    )

    score = calculate_score_v2(
        match_stats,
        league_info,
    )

    return (
        score,
        histories_before,
        home_source,
        away_source,
    )


def simulate_window(
    *,
    base_score,
    histories_before: dict[str, list],
    home_source: str,
    away_source: str,
    home: str,
    away: str,
    window: int,
) -> dict:
    home_rate, home_count, home_seq = recent_over_rate_from_source(
        source_league_id=home_source,
        team=home,
        histories_before=histories_before,
        last_n=window,
    )

    away_rate, away_count, away_seq = recent_over_rate_from_source(
        source_league_id=away_source,
        team=away,
        histories_before=histories_before,
        last_n=window,
    )

    # I primi tre contributi vengono dal ricalcolo reale di v20.
    total = (
        float(base_score.ranking_gap_score)
        + float(base_score.home_attack_score)
        + float(base_score.away_defense_weakness_score)
        + home_rate * 15.0
        + away_rate * 15.0
    )

    score = round(total, 2)

    return {
        "score": score,
        "band": band_from_score(score),
        "home_rate": round(home_rate, 6),
        "away_rate": round(away_rate, 6),
        "home_count": home_count,
        "away_count": away_count,
        "home_seq": home_seq,
        "away_seq": away_seq,
    }


def summarize_alta(df: pd.DataFrame, band_column: str) -> dict:
    alta = df[df[band_column] == "ALTA"]

    ok = int((alta["Outcome"] == "OK").sum())
    ko = int((alta["Outcome"] == "KO").sum())

    return {
        "OK": ok,
        "KO": ko,
        "Total": ok + ko,
        "HitRate": safe_rate(ok, ko),
    }

OUTPUT_DIR = Path("analysis/experiments/v20_recent_windows")
WINDOWS = (10, 9, 8, 7, 6, 5)
PARITY_TOLERANCE = 0.15


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    history = read_csv(V20_HISTORY)
    registry_rows = read_registry()

    history_cache: dict[str, dict[str, list]] = {}
    detail_rows = []
    unmatched = []

    for _, row in history.iterrows():
        outcome = outcome_from_row(row)

        if outcome not in VALID_OUTCOMES:
            continue

        league_id = str(row.get("LeagueId", "")).strip()
        home = str(row.get("Home", "")).strip()
        away = str(row.get("Away", "")).strip()
        match_date = (
            parse_date(row.get("MatchDate"))
            or parse_date(row.get("PredictionDate"))
        )

        if not league_id or not home or not away or match_date is None:
            unmatched.append({
                "LeagueId": league_id,
                "Home": home,
                "Away": away,
                "Reason": "Dati chiave non validi",
            })
            continue

        try:
            (
                base_score,
                histories_before,
                home_source,
                away_source,
            ) = build_historical_v20_base(
                league_id=league_id,
                home=home,
                away=away,
                match_date=match_date,
                registry_rows=registry_rows,
                history_cache=history_cache,
            )

            simulations = {
                window: simulate_window(
                    base_score=base_score,
                    histories_before=histories_before,
                    home_source=home_source,
                    away_source=away_source,
                    home=home,
                    away=away,
                    window=window,
                )
                for window in WINDOWS
            }

        except Exception as exc:
            unmatched.append({
                "LeagueId": league_id,
                "MatchDate": match_date.isoformat(),
                "Home": home,
                "Away": away,
                "Reason": f"{type(exc).__name__}: {exc}",
            })
            continue

        stored_score = safe_float(
            row.get("Score"),
            default=float("nan"),
        )

        parity_delta = (
            round(float(base_score.score) - stored_score, 4)
            if pd.notna(stored_score)
            else float("nan")
        )

        output = {
            "MatchDate": match_date.isoformat(),
            "LeagueId": league_id,
            "Home": home,
            "Away": away,
            "Outcome": outcome,
            "StoredV20Score": stored_score,
            "RecomputedLast10Score": float(base_score.score),
            "RecomputedLast10Band": str(base_score.band),
            "ParityDelta": parity_delta,
            "ParityOK": (
                abs(parity_delta) <= PARITY_TOLERANCE
                if pd.notna(parity_delta)
                else False
            ),
            "RankingGapScore": float(base_score.ranking_gap_score),
            "HomeAttackScore": float(base_score.home_attack_score),
            "AwayDefenseWeaknessScore": float(
                base_score.away_defense_weakness_score
            ),
        }

        for window, sim in simulations.items():
            output[f"Last{window}Score"] = sim["score"]
            output[f"Last{window}Band"] = sim["band"]
            output[f"HomeLast{window}Rate"] = sim["home_rate"]
            output[f"AwayLast{window}Rate"] = sim["away_rate"]
            output[f"HomeLast{window}Sequence"] = sim["home_seq"]
            output[f"AwayLast{window}Sequence"] = sim["away_seq"]

        detail_rows.append(output)

    details = pd.DataFrame(detail_rows)

    if details.empty:
        raise RuntimeError("Nessuna partita ricalcolata.")

    overall_rows = []
    no_au_rows = []
    transition_rows = []
    removed_frames = []
    added_frames = []

    no_au = details[
        ~details["LeagueId"].astype(str).str.startswith("Australia_")
    ].copy()

    baseline_col = "Last10Band"

    for window in WINDOWS:
        band_col = f"Last{window}Band"

        summary = summarize_alta(
            details,
            band_col,
        )

        overall_rows.append({
            "Window": f"Last{window}",
            **summary,
        })

        summary_no_au = summarize_alta(
            no_au,
            band_col,
        )

        no_au_rows.append({
            "Window": f"Last{window}",
            **summary_no_au,
        })

        if window == 10:
            continue

        base_alta = details[baseline_col] == "ALTA"
        current_alta = details[band_col] == "ALTA"

        groups = {
            "ALTA_TO_ALTA": base_alta & current_alta,
            "ALTA_TO_NON_ALTA": base_alta & ~current_alta,
            "NON_ALTA_TO_ALTA": ~base_alta & current_alta,
            "NON_ALTA_TO_NON_ALTA": ~base_alta & ~current_alta,
        }

        for transition, mask in groups.items():
            group = details[mask]
            ok = int((group["Outcome"] == "OK").sum())
            ko = int((group["Outcome"] == "KO").sum())

            transition_rows.append({
                "Window": f"Last{window}",
                "Transition": transition,
                "OK": ok,
                "KO": ko,
                "Total": ok + ko,
                "HitRate": safe_rate(ok, ko),
            })

        removed = details[
            base_alta & ~current_alta
        ].copy()

        if not removed.empty:
            removed.insert(
                0,
                "Window",
                f"Last{window}",
            )
            removed_frames.append(removed)

        added = details[
            ~base_alta & current_alta
        ].copy()

        if not added.empty:
            added.insert(
                0,
                "Window",
                f"Last{window}",
            )
            added_frames.append(added)

    overall = pd.DataFrame(overall_rows).sort_values(
        by=["HitRate", "KO", "Total"],
        ascending=[False, True, False],
    )

    no_au_summary = pd.DataFrame(no_au_rows).sort_values(
        by=["HitRate", "KO", "Total"],
        ascending=[False, True, False],
    )

    transitions = pd.DataFrame(transition_rows)

    removed_all = (
        pd.concat(removed_frames, ignore_index=True)
        if removed_frames
        else pd.DataFrame()
    )

    added_all = (
        pd.concat(added_frames, ignore_index=True)
        if added_frames
        else pd.DataFrame()
    )

    parity = details[
        [
            "MatchDate",
            "LeagueId",
            "Home",
            "Away",
            "StoredV20Score",
            "RecomputedLast10Score",
            "ParityDelta",
            "ParityOK",
        ]
    ].copy()

    overall.to_csv(
        OUTPUT_DIR / "01_window_overall.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    no_au_summary.to_csv(
        OUTPUT_DIR / "02_window_no_australia.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    transitions.to_csv(
        OUTPUT_DIR / "03_transitions_vs_last10.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    removed_all.to_csv(
        OUTPUT_DIR / "04_removed_from_alta.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    added_all.to_csv(
        OUTPUT_DIR / "05_added_to_alta.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    details.to_csv(
        OUTPUT_DIR / "06_match_details.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    pd.DataFrame(unmatched).to_csv(
        OUTPUT_DIR / "07_unmatched.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    parity.to_csv(
        OUTPUT_DIR / "08_parity_check.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print("=== V20 RECENT WINDOWS ===")
    print(f"Partite ricalcolate: {len(details)}")
    print(f"Non ricostruite: {len(unmatched)}")
    print(
        f"Parity entro ±{PARITY_TOLERANCE}: "
        f"{int(details['ParityOK'].sum())}/{len(details)}"
    )
    print()
    print(overall.to_string(index=False))
    print()
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
