"""
GioOver2.5 - PROX PPG Experiment

Regola testata:
- entrambe le squadre hanno almeno 10 partite giocate;
- differenza PPG <= soglia.

PPG = punti / partite giocate

Soglie:
0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50

Criterio di scelta:
1. percentuale ALTA rimanente più alta;
2. meno KO in ALTA rimanente;
3. più OK in ALTA rimanente;
4. percentuale MEDIA rimanente più alta.

Quindi, coerentemente con la preferenza del progetto:
10/10 viene classificato sopra 65/80.

Input:
- data/storico/ranking/<engine>/storico_ranking_<engine>.csv
- data/storico/risultati/<LeagueId>.csv

Output:
analysis/experiments/prox_ppg/
    01_summary.csv
    02_prox_matches.csv
    03_recommendations.csv
    04_unmatched.csv

Uso:
python -m analysis.experiments.prox_ppg_experiment
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pandas as pd

from gioover25.team_names import normalize_team_name


RANKING_ROOT = Path("data/storico/ranking")
RESULTS_ROOT = Path("data/storico/risultati")
OUTPUT_DIR = Path("analysis/experiments/prox_ppg")

MIN_MATCHES_PLAYED = 10
PPG_GAPS = (
    0.05,
    0.10,
    0.15,
    0.20,
    0.25,
    0.30,
    0.40,
    0.50,
)

VALID_BANDS = {"ALTA", "MEDIA", "BASSA"}
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
        dtype=str,
        low_memory=False,
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
    except ValueError:
        return None


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko

    if total == 0:
        return 0.0

    return round(ok / total * 100.0, 4)


def outcome_from_row(row: pd.Series) -> str:
    outcome = str(
        row.get("Over25", "")
    ).strip().upper()

    if outcome in VALID_OUTCOMES:
        return outcome

    hg = optional_int(row.get("HG"))
    ag = optional_int(row.get("AG"))

    if hg is None or ag is None:
        return ""

    return "OK" if hg + ag >= 3 else "KO"


def engine_history_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []

    if not RANKING_ROOT.exists():
        return files

    for engine_dir in sorted(RANKING_ROOT.iterdir()):
        if not engine_dir.is_dir():
            continue

        engine = engine_dir.name
        history_file = (
            engine_dir
            / f"storico_ranking_{engine}.csv"
        )

        if history_file.exists():
            files.append((engine, history_file))

    return files


def load_results(
    league_id: str,
) -> pd.DataFrame | None:
    path = RESULTS_ROOT / f"{league_id}.csv"

    if not path.exists():
        return None

    results = read_csv(path)

    required = {
        "MatchDate",
        "Home",
        "Away",
        "HG",
        "AG",
    }

    if not required.issubset(results.columns):
        return None

    results = results.copy()

    results["_Date"] = results["MatchDate"].map(
        parse_date
    )

    results["_HG"] = results["HG"].map(
        optional_int
    )

    results["_AG"] = results["AG"].map(
        optional_int
    )

    results = results[
        results["_Date"].notna()
        & results["_HG"].notna()
        & results["_AG"].notna()
    ].copy()

    results["_HomeCanonical"] = results["Home"].map(
        lambda value: normalize_team_name(
            league_id,
            value,
        )
    )

    results["_AwayCanonical"] = results["Away"].map(
        lambda value: normalize_team_name(
            league_id,
            value,
        )
    )

    return results.sort_values("_Date")


def reconstruct_table(
    results: pd.DataFrame,
    before_date: date,
) -> dict[str, dict[str, int]]:
    previous = results[
        results["_Date"] < before_date
    ]

    table: dict[str, dict[str, int]] = {}

    def ensure(team: str) -> dict[str, int]:
        return table.setdefault(
            team,
            {
                "played": 0,
                "points": 0,
            },
        )

    for _, match in previous.iterrows():
        home = match["_HomeCanonical"]
        away = match["_AwayCanonical"]

        hg = int(match["_HG"])
        ag = int(match["_AG"])

        home_row = ensure(home)
        away_row = ensure(away)

        home_row["played"] += 1
        away_row["played"] += 1

        if hg > ag:
            home_row["points"] += 3
        elif hg < ag:
            away_row["points"] += 3
        else:
            home_row["points"] += 1
            away_row["points"] += 1

    return table


def build_base_matches() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    result_cache: dict[
        str,
        pd.DataFrame | None,
    ] = {}

    table_cache: dict[
        tuple[str, date],
        dict[str, dict[str, int]],
    ] = {}

    matches: list[dict] = []
    unmatched: list[dict] = []

    for engine, history_file in engine_history_files():
        history = read_csv(history_file)

        required = {
            "LeagueId",
            "Home",
            "Away",
            "Band",
        }

        if not required.issubset(history.columns):
            continue

        for _, row in history.iterrows():
            outcome = outcome_from_row(row)

            band = str(
                row.get("Band", "")
            ).strip().upper()

            if (
                outcome not in VALID_OUTCOMES
                or band not in VALID_BANDS
            ):
                continue

            league_id = str(
                row.get("LeagueId", "")
            ).strip()

            match_date = (
                parse_date(row.get("MatchDate"))
                or parse_date(row.get("PredictionDate"))
            )

            if not league_id or match_date is None:
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": league_id,
                        "Home": row.get("Home", ""),
                        "Away": row.get("Away", ""),
                        "Reason": "LeagueId o data non valida",
                    }
                )
                continue

            if league_id not in result_cache:
                result_cache[league_id] = load_results(
                    league_id
                )

            results = result_cache[league_id]

            if results is None:
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": league_id,
                        "Home": row.get("Home", ""),
                        "Away": row.get("Away", ""),
                        "Reason": "File risultati assente o non valido",
                    }
                )
                continue

            cache_key = (
                league_id,
                match_date,
            )

            if cache_key not in table_cache:
                table_cache[cache_key] = reconstruct_table(
                    results,
                    match_date,
                )

            table = table_cache[cache_key]

            home = normalize_team_name(
                league_id,
                row.get("Home", ""),
            )

            away = normalize_team_name(
                league_id,
                row.get("Away", ""),
            )

            home_row = table.get(home)
            away_row = table.get(away)

            if home_row is None or away_row is None:
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": league_id,
                        "Home": row.get("Home", ""),
                        "Away": row.get("Away", ""),
                        "Reason": (
                            "Squadra non trovata nella "
                            "classifica ricostruita"
                        ),
                    }
                )
                continue

            home_played = home_row["played"]
            away_played = away_row["played"]

            home_ppg = (
                home_row["points"] / home_played
                if home_played
                else 0.0
            )

            away_ppg = (
                away_row["points"] / away_played
                if away_played
                else 0.0
            )

            matches.append(
                {
                    "Engine": engine,
                    "LeagueId": league_id,
                    "MatchDate": match_date.isoformat(),
                    "Home": row.get("Home", ""),
                    "Away": row.get("Away", ""),
                    "Band": band,
                    "Outcome": outcome,
                    "HomePlayed": home_played,
                    "AwayPlayed": away_played,
                    "HomePoints": home_row["points"],
                    "AwayPoints": away_row["points"],
                    "HomePPG": round(home_ppg, 6),
                    "AwayPPG": round(away_ppg, 6),
                    "PPGGap": round(
                        abs(home_ppg - away_ppg),
                        6,
                    ),
                }
            )

    return (
        pd.DataFrame(matches),
        pd.DataFrame(unmatched),
    )


def summarize(
    rows: pd.DataFrame,
    engine: str,
    max_ppg_gap: float,
) -> tuple[
    dict,
    pd.DataFrame,
]:
    current = rows.copy()

    current["IsProx"] = (
        (current["HomePlayed"] >= MIN_MATCHES_PLAYED)
        & (current["AwayPlayed"] >= MIN_MATCHES_PLAYED)
        & (current["PPGGap"] <= max_ppg_gap)
    )

    prox = current[
        current["IsProx"]
    ]

    prox_ok = int(
        (prox["Outcome"] == "OK").sum()
    )

    prox_ko = int(
        (prox["Outcome"] == "KO").sum()
    )

    summary = {
        "Engine": engine,
        "MaxPPGGap": max_ppg_gap,
        "MinMatchesPlayed": MIN_MATCHES_PLAYED,
        "PROX_OK": prox_ok,
        "PROX_KO": prox_ko,
        "PROX_Total": prox_ok + prox_ko,
        "PROX_HitRate": safe_rate(
            prox_ok,
            prox_ko,
        ),
    }

    for band in (
        "ALTA",
        "MEDIA",
        "BASSA",
    ):
        original = current[
            current["Band"] == band
        ]

        prox_band = current[
            (current["Band"] == band)
            & current["IsProx"]
        ]

        remaining = current[
            (current["Band"] == band)
            & (~current["IsProx"])
        ]

        original_ok = int(
            (original["Outcome"] == "OK").sum()
        )

        original_ko = int(
            (original["Outcome"] == "KO").sum()
        )

        prox_ok = int(
            (prox_band["Outcome"] == "OK").sum()
        )

        prox_ko = int(
            (prox_band["Outcome"] == "KO").sum()
        )

        remaining_ok = int(
            (remaining["Outcome"] == "OK").sum()
        )

        remaining_ko = int(
            (remaining["Outcome"] == "KO").sum()
        )

        original_rate = safe_rate(
            original_ok,
            original_ko,
        )

        remaining_rate = safe_rate(
            remaining_ok,
            remaining_ko,
        )

        summary[f"{band}_OriginalOK"] = original_ok
        summary[f"{band}_OriginalKO"] = original_ko
        summary[
            f"{band}_OriginalHitRate"
        ] = original_rate

        summary[f"PROX_{band}_OK"] = prox_ok
        summary[f"PROX_{band}_KO"] = prox_ko
        summary[
            f"PROX_{band}_Total"
        ] = prox_ok + prox_ko
        summary[
            f"PROX_{band}_HitRate"
        ] = safe_rate(
            prox_ok,
            prox_ko,
        )

        summary[
            f"Remaining{band}OK"
        ] = remaining_ok
        summary[
            f"Remaining{band}KO"
        ] = remaining_ko
        summary[
            f"Remaining{band}Total"
        ] = remaining_ok + remaining_ko
        summary[
            f"Remaining{band}HitRate"
        ] = remaining_rate
        summary[
            f"{band}Delta"
        ] = round(
            remaining_rate - original_rate,
            4,
        )

    return (
        summary,
        current[
            current["IsProx"]
        ].copy(),
    )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    matches, unmatched = build_base_matches()

    if matches.empty:
        raise RuntimeError(
            "Nessuna partita analizzabile trovata."
        )

    summary_rows: list[dict] = []
    prox_rows: list[pd.DataFrame] = []

    for engine, engine_rows in matches.groupby("Engine"):
        for max_ppg_gap in PPG_GAPS:
            summary, prox = summarize(
                engine_rows,
                engine,
                max_ppg_gap,
            )

            summary_rows.append(summary)

            if not prox.empty:
                prox = prox.copy()
                prox["MaxPPGGap"] = max_ppg_gap
                prox_rows.append(prox)

    summary_df = pd.DataFrame(
        summary_rows
    )

    summary_df = summary_df.sort_values(
        by=[
            "Engine",
            "RemainingALTAHitRate",
            "RemainingALTAKO",
            "RemainingALTAOK",
            "RemainingMEDIAHitRate",
        ],
        ascending=[
            True,
            False,
            True,
            False,
            False,
        ],
    )

    summary_df.to_csv(
        OUTPUT_DIR / "01_summary.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    prox_output = (
        pd.concat(
            prox_rows,
            ignore_index=True,
        )
        if prox_rows
        else pd.DataFrame()
    )

    prox_output.to_csv(
        OUTPUT_DIR / "02_prox_matches.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    recommendations = (
        summary_df.groupby(
            "Engine",
            as_index=False,
            sort=False,
        )
        .head(1)
        .copy()
    )

    recommendations.insert(
        0,
        "RankWithinEngine",
        1,
    )

    recommendations.to_csv(
        OUTPUT_DIR / "03_recommendations.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    unmatched.to_csv(
        OUTPUT_DIR / "04_unmatched.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"Partite analizzate: {len(matches)}"
    )

    print(
        "Engine analizzati: "
        f"{matches['Engine'].nunique()}"
    )

    print(
        f"Soglie testate: {len(PPG_GAPS)}"
    )

    print(
        f"Righe non abbinate: {len(unmatched)}"
    )

    print(
        f"Output: {OUTPUT_DIR}"
    )

    print()

    columns = [
        "Engine",
        "MaxPPGGap",
        "PROX_ALTA_OK",
        "PROX_ALTA_KO",
        "PROX_ALTA_Total",
        "PROX_ALTA_HitRate",
        "RemainingALTAOK",
        "RemainingALTAKO",
        "RemainingALTATotal",
        "RemainingALTAHitRate",
        "ALTADelta",
        "RemainingMEDIAHitRate",
        "MEDIADelta",
    ]

    print(
        recommendations[
            columns
        ].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
