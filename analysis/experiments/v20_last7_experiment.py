"""
===============================================================================
GioOver2.5 - v20 Last7 vs Last10 CORRETTO
===============================================================================

CORREZIONE PRINCIPALE
---------------------
La versione precedente riutilizzava RankingGapScore / HomeAttackScore /
AwayDefenseWeaknessScore dallo storico_ranking. Alcune vecchie righe avevano
questi campi vuoti/zero, falsando lo score simulato.

Questa versione NON usa quei campi per ricalcolare v20.

Per ogni partita:
1. carica i risultati storici reali;
2. prende SOLO le partite precedenti alla MatchDate;
3. ricostruisce MatchStatistics;
4. richiama calculate_score_v2() per ottenere il vero v20 Last10;
5. mantiene identici i 3 driver strutturali appena ricalcolati;
6. sostituisce soltanto Last10 con Last7.

In questo modo il confronto Last10 vs Last7 è omogeneo.

PARAMETRI
---------
LAST_N = 7
PARITY_TOLERANCE = 0.15

PARITY_TOLERANCE serve solo a segnalare differenze fra Score storico e Score
v20 ricalcolato. L'analisi usa sempre lo score RICALCOLATO.

ESECUZIONE
----------
python -m analysis.experiments.v20_last7_experiment

OUTPUT
------
analysis/experiments/v20_last7_corrected/
01_overall.csv
02_band_transitions.csv
03_changed_matches.csv
04_alta_removed.csv
05_alta_added.csv
06_match_details.csv
07_no_australia.csv
08_unmatched.csv
09_parity_check.csv
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

OUTPUT_DIR = Path("analysis/experiments/v20_last7_corrected")
LAST_N = 7
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

            last7 = simulate_window(
                base_score=base_score,
                histories_before=histories_before,
                home_source=home_source,
                away_source=away_source,
                home=home,
                away=away,
                window=LAST_N,
            )

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

        detail_rows.append({
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

            "Last7Score": last7["score"],
            "Last7Band": last7["band"],
            "ScoreDeltaLast7VsLast10": round(
                last7["score"] - float(base_score.score),
                4,
            ),

            "RankingGapScore": float(base_score.ranking_gap_score),
            "HomeAttackScore": float(base_score.home_attack_score),
            "AwayDefenseWeaknessScore": float(
                base_score.away_defense_weakness_score
            ),

            "HomeLast10Score": float(base_score.home_last10_over_score),
            "AwayLast10Score": float(base_score.away_last10_over_score),

            "HomeLast7Rate": last7["home_rate"],
            "AwayLast7Rate": last7["away_rate"],
            "HomeLast7Count": last7["home_count"],
            "AwayLast7Count": last7["away_count"],
            "HomeLast7Sequence": last7["home_seq"],
            "AwayLast7Sequence": last7["away_seq"],
        })

    details = pd.DataFrame(detail_rows)

    if details.empty:
        raise RuntimeError("Nessuna partita ricalcolata.")

    details["Transition"] = "NON_ALTA_TO_NON_ALTA"

    details.loc[
        (details["RecomputedLast10Band"] == "ALTA")
        & (details["Last7Band"] == "ALTA"),
        "Transition",
    ] = "ALTA_TO_ALTA"

    details.loc[
        (details["RecomputedLast10Band"] == "ALTA")
        & (details["Last7Band"] != "ALTA"),
        "Transition",
    ] = "ALTA_TO_NON_ALTA"

    details.loc[
        (details["RecomputedLast10Band"] != "ALTA")
        & (details["Last7Band"] == "ALTA"),
        "Transition",
    ] = "NON_ALTA_TO_ALTA"

    transition_rows = []

    for transition, group in details.groupby("Transition"):
        ok = int((group["Outcome"] == "OK").sum())
        ko = int((group["Outcome"] == "KO").sum())

        transition_rows.append({
            "Transition": transition,
            "OK": ok,
            "KO": ko,
            "Total": ok + ko,
            "HitRate": safe_rate(ok, ko),
        })

    base = summarize_alta(
        details,
        "RecomputedLast10Band",
    )

    alt = summarize_alta(
        details,
        "Last7Band",
    )

    overall = pd.DataFrame([{
        "Baseline": "RECOMPUTED_LAST10",
        "Last10_OK": base["OK"],
        "Last10_KO": base["KO"],
        "Last10_Total": base["Total"],
        "Last10_HitRate": base["HitRate"],
        "Last7_OK": alt["OK"],
        "Last7_KO": alt["KO"],
        "Last7_Total": alt["Total"],
        "Last7_HitRate": alt["HitRate"],
        "DeltaHitRate": round(
            alt["HitRate"] - base["HitRate"],
            4,
        ),
    }])

    no_au = details[
        ~details["LeagueId"].astype(str).str.startswith("Australia_")
    ].copy()

    base_no_au = summarize_alta(
        no_au,
        "RecomputedLast10Band",
    )

    alt_no_au = summarize_alta(
        no_au,
        "Last7Band",
    )

    no_au_summary = pd.DataFrame([{
        "Last10_OK": base_no_au["OK"],
        "Last10_KO": base_no_au["KO"],
        "Last10_Total": base_no_au["Total"],
        "Last10_HitRate": base_no_au["HitRate"],
        "Last7_OK": alt_no_au["OK"],
        "Last7_KO": alt_no_au["KO"],
        "Last7_Total": alt_no_au["Total"],
        "Last7_HitRate": alt_no_au["HitRate"],
        "DeltaHitRate": round(
            alt_no_au["HitRate"] - base_no_au["HitRate"],
            4,
        ),
    }])

    changed = details[
        details["RecomputedLast10Band"] != details["Last7Band"]
    ].copy()

    removed = details[
        details["Transition"] == "ALTA_TO_NON_ALTA"
    ].copy()

    added = details[
        details["Transition"] == "NON_ALTA_TO_ALTA"
    ].copy()

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
        OUTPUT_DIR / "01_overall.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    pd.DataFrame(transition_rows).to_csv(
        OUTPUT_DIR / "02_band_transitions.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    changed.to_csv(
        OUTPUT_DIR / "03_changed_matches.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    removed.to_csv(
        OUTPUT_DIR / "04_alta_removed.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    added.to_csv(
        OUTPUT_DIR / "05_alta_added.csv",
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

    no_au_summary.to_csv(
        OUTPUT_DIR / "07_no_australia.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    pd.DataFrame(unmatched).to_csv(
        OUTPUT_DIR / "08_unmatched.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    parity.to_csv(
        OUTPUT_DIR / "09_parity_check.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print("=== V20 LAST7 CORRETTO ===")
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
