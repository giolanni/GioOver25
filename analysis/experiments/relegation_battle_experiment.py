"""
===============================================================================
GioOver2.5 - Experiment RELEGATION-BATTLE
===============================================================================

OBIETTIVO
---------
Studiare ESCLUSIVAMENTE le partite tra DUE squadre entrambe nelle ULTIME 4
posizioni della classifica al momento della partita.

L'ipotesi è che uno scontro diretto per la salvezza possa avere una dinamica
più prudente del normale: pareggio o vittoria di misura possono essere risultati
utili e quindi una partita statisticamente da Over può essere meno affidabile.

Non si usa più una percentuale generica di "parte bassa" della classifica.

Lo script NON modifica gli engine.

TESTA LE ULTIME 4 DELLA CLASSIFICA
-----------------------------------
Condizioni fisse:
    HomePlayed >= 10
    AwayPlayed >= 10
    HomePosition nelle ultime 4
    AwayPosition nelle ultime 4

Per capire se la vicinanza in punti rafforza il fenomeno vengono confrontati:
    nessun limite di gap punti
    gap <= 3
    gap <= 6
    gap <= 9
    gap <= 12

Una partita ALTA viene marcata RelegationBattle se entrambe le squadre sono
nelle ultime 4. Il gap punti è una dimensione di analisi, non la definizione
principale della lotta retrocessione.

CRITERIO DI VALUTAZIONE
-----------------------
L'obiettivo principale è MASSIMIZZARE la percentuale OK della fascia ALTA
rimanente dopo l'esclusione delle BottomClose.

La numerosità viene riportata per valutare la robustezza, ma NON viene usata
per penalizzare automaticamente una configurazione più selettiva.

ENGINE
------
Per default vengono esclusi:
    v251
    v26

Modificare EXCLUDED_ENGINES se necessario.

INPUT
-----
data/storico/ranking/<engine>/storico_ranking_<engine>.csv
data/storico/risultati/<LeagueId>.csv

OUTPUT
------
analysis/experiments/relegation_battle/

    01_summary.csv
    02_best_by_engine.csv
    03_flagged_matches.csv
    04_unmatched.csv

USO
---
python -m analysis.experiments.relegation_battle_experiment
===============================================================================
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pandas as pd

from gioover25.team_names import normalize_team_name


RANKING_ROOT = Path("data/storico/ranking")
RESULTS_ROOT = Path("data/storico/risultati")
OUTPUT_DIR = Path("analysis/experiments/relegation_battle")

EXCLUDED_ENGINES = {
    "v251",
    "v26",
}

MIN_MATCHES_PLAYED = 10

RELEGATION_PLACES = 4

# None = tutte le sfide tra squadre nelle ultime 4, senza limite di punti.
POINT_GAPS = (
    None,
    3,
    6,
    9,
    12,
)

VALID_OUTCOMES = {
    "OK",
    "KO",
}

VALID_BANDS = {
    "ALTA",
    "MEDIA",
    "BASSA",
}


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

    return round(
        ok / total * 100.0,
        4,
    )


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

    return (
        "OK"
        if hg + ag >= 3
        else "KO"
    )


def engine_history_files() -> list[tuple[str, Path]]:
    files: list[tuple[str, Path]] = []

    if not RANKING_ROOT.exists():
        return files

    for engine_dir in sorted(
        RANKING_ROOT.iterdir()
    ):
        if not engine_dir.is_dir():
            continue

        engine = engine_dir.name

        if engine in EXCLUDED_ENGINES:
            continue

        history = (
            engine_dir
            / f"storico_ranking_{engine}.csv"
        )

        if history.exists():
            files.append(
                (
                    engine,
                    history,
                )
            )

    return files


def load_results(
    league_id: str,
) -> pd.DataFrame | None:
    path = (
        RESULTS_ROOT
        / f"{league_id}.csv"
    )

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

    if not required.issubset(
        results.columns
    ):
        return None

    results = results.copy()

    results["_Date"] = (
        results["MatchDate"]
        .map(parse_date)
    )

    results["_HG"] = (
        results["HG"]
        .map(optional_int)
    )

    results["_AG"] = (
        results["AG"]
        .map(optional_int)
    )

    results = results[
        results["_Date"].notna()
        & results["_HG"].notna()
        & results["_AG"].notna()
    ].copy()

    results["_HomeCanonical"] = (
        results["Home"].map(
            lambda value: normalize_team_name(
                league_id,
                value,
            )
        )
    )

    results["_AwayCanonical"] = (
        results["Away"].map(
            lambda value: normalize_team_name(
                league_id,
                value,
            )
        )
    )

    return results.sort_values(
        "_Date"
    )


def reconstruct_table(
    results: pd.DataFrame,
    before_date: date,
) -> dict[str, dict[str, int]]:
    """
    Ricostruisce la classifica PRIMA della partita.

    Ordinamento:
    1. punti;
    2. differenza reti;
    3. gol fatti;
    4. nome squadra.

    Serve solo a stimare la posizione relativa storica.
    """

    previous = results[
        results["_Date"] < before_date
    ]

    table: dict[
        str,
        dict[str, int],
    ] = {}

    def ensure(
        team: str,
    ) -> dict[str, int]:
        return table.setdefault(
            team,
            {
                "played": 0,
                "points": 0,
                "gf": 0,
                "ga": 0,
            },
        )

    for _, match in previous.iterrows():
        home = match["_HomeCanonical"]
        away = match["_AwayCanonical"]

        hg = int(
            match["_HG"]
        )

        ag = int(
            match["_AG"]
        )

        home_row = ensure(home)
        away_row = ensure(away)

        home_row["played"] += 1
        away_row["played"] += 1

        home_row["gf"] += hg
        home_row["ga"] += ag

        away_row["gf"] += ag
        away_row["ga"] += hg

        if hg > ag:
            home_row["points"] += 3
        elif hg < ag:
            away_row["points"] += 3
        else:
            home_row["points"] += 1
            away_row["points"] += 1

    ordered = sorted(
        table.items(),
        key=lambda item: (
            -item[1]["points"],
            -(
                item[1]["gf"]
                - item[1]["ga"]
            ),
            -item[1]["gf"],
            item[0],
        ),
    )

    for position, (
        team,
        values,
    ) in enumerate(
        ordered,
        start=1,
    ):
        values["position"] = position

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

    for (
        engine,
        history_file,
    ) in engine_history_files():
        history = read_csv(
            history_file
        )

        required = {
            "LeagueId",
            "Home",
            "Away",
            "Band",
        }

        if not required.issubset(
            history.columns
        ):
            continue

        for _, row in history.iterrows():
            outcome = outcome_from_row(
                row
            )

            band = str(
                row.get(
                    "Band",
                    "",
                )
            ).strip().upper()

            if (
                outcome not in VALID_OUTCOMES
                or band not in VALID_BANDS
            ):
                continue

            league_id = str(
                row.get(
                    "LeagueId",
                    "",
                )
            ).strip()

            match_date = (
                parse_date(
                    row.get(
                        "MatchDate"
                    )
                )
                or parse_date(
                    row.get(
                        "PredictionDate"
                    )
                )
            )

            if (
                not league_id
                or match_date is None
            ):
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": league_id,
                        "Home": row.get(
                            "Home",
                            "",
                        ),
                        "Away": row.get(
                            "Away",
                            "",
                        ),
                        "Reason": (
                            "LeagueId o data non valida"
                        ),
                    }
                )
                continue

            if league_id not in result_cache:
                result_cache[
                    league_id
                ] = load_results(
                    league_id
                )

            results = result_cache[
                league_id
            ]

            if results is None:
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": league_id,
                        "Home": row.get(
                            "Home",
                            "",
                        ),
                        "Away": row.get(
                            "Away",
                            "",
                        ),
                        "Reason": (
                            "File risultati assente "
                            "o non valido"
                        ),
                    }
                )
                continue

            cache_key = (
                league_id,
                match_date,
            )

            if cache_key not in table_cache:
                table_cache[
                    cache_key
                ] = reconstruct_table(
                    results,
                    match_date,
                )

            table = table_cache[
                cache_key
            ]

            home = normalize_team_name(
                league_id,
                row.get(
                    "Home",
                    "",
                ),
            )

            away = normalize_team_name(
                league_id,
                row.get(
                    "Away",
                    "",
                ),
            )

            home_row = table.get(
                home
            )

            away_row = table.get(
                away
            )

            if (
                home_row is None
                or away_row is None
            ):
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": league_id,
                        "Home": row.get(
                            "Home",
                            "",
                        ),
                        "Away": row.get(
                            "Away",
                            "",
                        ),
                        "Reason": (
                            "Squadra non trovata nella "
                            "classifica ricostruita"
                        ),
                    }
                )
                continue

            teams_count = len(
                table
            )

            if teams_count <= 1:
                continue

            matches.append(
                {
                    "Engine": engine,
                    "LeagueId": league_id,
                    "MatchDate": (
                        match_date.isoformat()
                    ),
                    "Home": row.get(
                        "Home",
                        "",
                    ),
                    "Away": row.get(
                        "Away",
                        "",
                    ),
                    "Band": band,
                    "Outcome": outcome,

                    "TeamsCount": teams_count,

                    "HomePlayed": (
                        home_row["played"]
                    ),
                    "AwayPlayed": (
                        away_row["played"]
                    ),

                    "HomePoints": (
                        home_row["points"]
                    ),
                    "AwayPoints": (
                        away_row["points"]
                    ),

                    "PointsGap": abs(
                        home_row["points"]
                        - away_row["points"]
                    ),

                    "HomePosition": (
                        home_row["position"]
                    ),
                    "AwayPosition": (
                        away_row["position"]
                    ),
                }
            )

    return (
        pd.DataFrame(matches),
        pd.DataFrame(unmatched),
    )


def summarize_configuration(
    rows: pd.DataFrame,
    engine: str,
    max_points_gap: int | None,
) -> tuple[dict, pd.DataFrame]:
    current = rows.copy()

    # La soglia dipende dal numero di squadre presenti nella classifica
    # ricostruita in quel preciso momento.
    #
    # Esempio: campionato a 12 squadre -> ultime 4 = posizioni 9,10,11,12.
    relegation_start = (
        current["TeamsCount"] - RELEGATION_PLACES + 1
    )

    in_last_four = (
        (current["HomePlayed"] >= MIN_MATCHES_PLAYED)
        & (current["AwayPlayed"] >= MIN_MATCHES_PLAYED)
        & (current["HomePosition"] >= relegation_start)
        & (current["AwayPosition"] >= relegation_start)
    )

    if max_points_gap is None:
        gap_condition = pd.Series(
            True,
            index=current.index,
        )
        gap_label = "ANY"
    else:
        gap_condition = (
            current["PointsGap"] <= max_points_gap
        )
        gap_label = str(max_points_gap)

    current["IsRelegationBattle"] = (
        in_last_four & gap_condition
    )

    alta = current[
        current["Band"] == "ALTA"
    ]

    flagged = alta[
        alta["IsRelegationBattle"]
    ]

    remaining = alta[
        ~alta["IsRelegationBattle"]
    ]

    original_ok = int(
        (alta["Outcome"] == "OK").sum()
    )
    original_ko = int(
        (alta["Outcome"] == "KO").sum()
    )

    flagged_ok = int(
        (flagged["Outcome"] == "OK").sum()
    )
    flagged_ko = int(
        (flagged["Outcome"] == "KO").sum()
    )

    remaining_ok = int(
        (remaining["Outcome"] == "OK").sum()
    )
    remaining_ko = int(
        (remaining["Outcome"] == "KO").sum()
    )

    summary = {
        "Engine": engine,
        "Rule": "BOTH_LAST_4",
        "MaxPointsGap": gap_label,
        "MinMatchesPlayed": MIN_MATCHES_PLAYED,

        "Original_ALTA_OK": original_ok,
        "Original_ALTA_KO": original_ko,
        "Original_ALTA_Total": original_ok + original_ko,
        "Original_ALTA_HitRate": safe_rate(
            original_ok,
            original_ko,
        ),

        "RELEGATION_OK": flagged_ok,
        "RELEGATION_KO": flagged_ko,
        "RELEGATION_Total": flagged_ok + flagged_ko,
        "RELEGATION_HitRate": safe_rate(
            flagged_ok,
            flagged_ko,
        ),

        "Remaining_ALTA_OK": remaining_ok,
        "Remaining_ALTA_KO": remaining_ko,
        "Remaining_ALTA_Total": remaining_ok + remaining_ko,
        "Remaining_ALTA_HitRate": safe_rate(
            remaining_ok,
            remaining_ko,
        ),

        "DeltaHitRate": round(
            safe_rate(remaining_ok, remaining_ko)
            - safe_rate(original_ok, original_ko),
            4,
        ),

        "OK_Removed": flagged_ok,
        "KO_Removed": flagged_ko,
    }

    return summary, flagged.copy()


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
    flagged_frames: list[pd.DataFrame] = []

    for engine, engine_rows in matches.groupby("Engine"):
        for max_points_gap in POINT_GAPS:
            summary, flagged = summarize_configuration(
                engine_rows,
                engine,
                max_points_gap,
            )

            summary_rows.append(summary)

            if not flagged.empty:
                flagged = flagged.copy()
                flagged["TestMaxPointsGap"] = (
                    "ANY"
                    if max_points_gap is None
                    else max_points_gap
                )
                flagged_frames.append(flagged)

    summary_df = pd.DataFrame(summary_rows)

    # Criterio GioOver2.5:
    # prima massimizzare la percentuale OK della ALTA rimanente.
    # La numerosità serve solo a giudicare la robustezza.
    summary_df = summary_df.sort_values(
        by=[
            "Engine",
            "Remaining_ALTA_HitRate",
            "Remaining_ALTA_Total",
        ],
        ascending=[
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

    best_by_engine = (
        summary_df
        .groupby(
            "Engine",
            as_index=False,
            sort=False,
        )
        .head(1)
        .copy()
    )

    best_by_engine.to_csv(
        OUTPUT_DIR / "02_best_by_engine.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    if flagged_frames:
        pd.concat(
            flagged_frames,
            ignore_index=True,
        ).to_csv(
            OUTPUT_DIR / "03_flagged_matches.csv",
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )
    else:
        pd.DataFrame().to_csv(
            OUTPUT_DIR / "03_flagged_matches.csv",
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
        f"Engine analizzati: {matches['Engine'].nunique()}"
    )
    print(
        "Regola base: entrambe nelle ultime 4 "
        f"con almeno {MIN_MATCHES_PLAYED} partite giocate"
    )
    print(
        "Gap testati: ANY, <=3, <=6, <=9, <=12"
    )
    print(
        f"Righe non abbinate: {len(unmatched)}"
    )
    print(
        f"Output: {OUTPUT_DIR}"
    )
    print()

    display_columns = [
        "Engine",
        "MaxPointsGap",
        "Original_ALTA_HitRate",
        "RELEGATION_OK",
        "RELEGATION_KO",
        "RELEGATION_Total",
        "RELEGATION_HitRate",
        "Remaining_ALTA_OK",
        "Remaining_ALTA_KO",
        "Remaining_ALTA_Total",
        "Remaining_ALTA_HitRate",
        "DeltaHitRate",
    ]

    print(
        best_by_engine[
            display_columns
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
