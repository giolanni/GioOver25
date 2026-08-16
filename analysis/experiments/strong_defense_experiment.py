"""
===============================================================================
GioOver2.5 - EXPERIMENT STRONG DEFENSE
===============================================================================

OBIETTIVO
---------
Verificare su TUTTO lo storico se le partite classificate ALTA diventano meno
affidabili quando una o entrambe le squadre possiedono una difesa molto forte.

Il test NON modifica alcun engine.

ENGINE ANALIZZATI
-----------------
Per default:

    v20
    v22
    v25
    v26

Puoi modificare:

    ENGINES = ("v20", "v22", "v25", "v26")

===============================================================================
COSA MISURA
===============================================================================

Per ogni partita ALTA conclusa ricostruisce, PRIMA della MatchDate:

1) HomeGApg
   Gol subiti medi stagionali dalla squadra di casa.

2) AwayGApg
   Gol subiti medi stagionali dalla squadra ospite.

3) BestDefenseGApg
   La migliore delle due difese:
       min(HomeGApg, AwayGApg)

4) WorstDefenseGApg
   La peggiore delle due:
       max(HomeGApg, AwayGApg)

5) HomeGALast5Avg / AwayGALast5Avg
   Gol subiti medi nelle ultime 5 gare precedenti.

6) BestDefenseLast5GA
   min(HomeGALast5Avg, AwayGALast5Avg)

7) WorstDefenseLast5GA
   max(HomeGALast5Avg, AwayGALast5Avg)

===============================================================================
SOGLIE TESTATE
===============================================================================

THRESHOLDS = (
    0.80,
    1.00,
    1.10,
    1.20,
    1.30,
    1.40,
    1.50,
    1.60,
)

Per ogni soglia vengono studiate separatamente:

    AT_LEAST_ONE_STRONG
        almeno una delle due difese ha GA/match <= soglia

    BOTH_STRONG
        entrambe le difese hanno GA/match <= soglia

    HOME_STRONG
        solo condizione sulla squadra di casa

    AWAY_STRONG
        solo condizione sulla squadra ospite

Lo stesso viene fatto sia su GA stagionale sia su GA ultime 5.

===============================================================================
CRITERIO
===============================================================================

Non cerchiamo la configurazione con più partite.

Cerchiamo evidenza che il gruppo "difesa forte" abbia una % OK nettamente
PEGGIORE della normale fascia ALTA.

Esempio:

    ALTA baseline                    75%
    almeno una difesa GA <= 1.10    61%

sarebbe un segnale forte per un secondo experiment dedicato alla PENALITÀ.

===============================================================================
ANTI-LOOKAHEAD
===============================================================================

Sono usati esclusivamente risultati con data STRETTAMENTE precedente alla
MatchDate della prediction.

Per CompetitionGroup / playoff viene usato HomeSourceLeagueId /
AwaySourceLeagueId quando disponibile; altrimenti LeagueId.

===============================================================================
CAMPIONE MINIMO
===============================================================================

MIN_SEASON_MATCHES = 5

La metrica stagionale viene considerata solo quando la squadra dispone di
almeno 5 gare precedenti.

Per Last5 servono esattamente almeno 5 gare precedenti.

===============================================================================
OUTPUT
===============================================================================

analysis/experiments/strong_defense/

01_baseline_by_engine.csv
    Precisione ALTA originale di ciascun engine.

02_thresholds_season.csv
    Test soglie sulla media gol subiti stagionale.

03_thresholds_last5.csv
    Test soglie sui gol subiti medi nelle ultime 5.

04_buckets_season.csv
    Distribuzione per fasce GA stagionali.

05_buckets_last5.csv
    Distribuzione per fasce GA Last5.

06_match_details.csv
    Tutte le ALTA ricostruite con metriche difensive.

07_candidate_signals.csv
    Segnali più interessanti ordinati per:
        - peggioramento rispetto alla baseline;
        - KO rate;
        - numerosità.

08_no_australia.csv
    Stesse candidate escludendo Australia_*.

09_unmatched.csv
    Righe non ricostruibili.

===============================================================================
ESECUZIONE
===============================================================================

python -m analysis.experiments.strong_defense_experiment

===============================================================================
SECONDO STEP
===============================================================================

Se questo experiment mostra un segnale stabile, NON cambiare subito gli engine.

Il secondo experiment dovrà cercare il peso/penalità ottimale, ad esempio:

    -2
    -3
    -4
    -5
    -6
    -8
    -10

combinando:
    soglia GA
    una/entrambe le difese
    stagionale/Last5
    penalità

===============================================================================
"""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import pandas as pd


ENGINES = (
    "v20",
    "v22",
    "v25",
    "v26",
)

RANKING_ROOT = Path("data/storico/ranking")
RESULTS_ROOT = Path("data/storico/risultati")
OUTPUT_DIR = Path("analysis/experiments/strong_defense")

THRESHOLDS = (
    0.80,
    1.00,
    1.10,
    1.20,
    1.30,
    1.40,
    1.50,
    1.60,
)

GA_BUCKETS = (
    (0.00, 0.80),
    (0.80, 1.00),
    (1.00, 1.10),
    (1.10, 1.20),
    (1.20, 1.30),
    (1.30, 1.40),
    (1.40, 1.50),
    (1.50, 1.60),
    (1.60, 1.80),
    (1.80, 2.00),
    (2.00, None),
)

MIN_SEASON_MATCHES = 5
RECENT_N = 5

VALID_OUTCOMES = {
    "OK",
    "KO",
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


def text(value) -> str:
    return str(
        value or ""
    ).strip()


def normalize_team(value) -> str:
    return " ".join(
        text(value)
        .casefold()
        .split()
    )


def parse_date(value) -> date | None:
    raw = text(value)

    if not raw or raw.lower() == "nan":
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def to_int(value) -> int | None:
    raw = text(value)

    if not raw or raw.lower() == "nan":
        return None

    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return None


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko

    return round(
        ok / total * 100.0,
        4,
    ) if total else 0.0


def find_history(engine: str) -> Path | None:
    candidates = (
        RANKING_ROOT
        / engine
        / f"storico_ranking_{engine}.csv",
        RANKING_ROOT
        / f"storico_ranking_{engine}.csv",
    )

    for path in candidates:
        if path.exists():
            return path

    found = [
        path
        for path in RANKING_ROOT.rglob(
            f"storico_ranking*{engine}*.csv"
        )
        if "old" not in path.name.casefold()
        and "bak" not in path.name.casefold()
    ]

    if not found:
        return None

    found.sort(
        key=lambda path: (
            len(str(path)),
            str(path),
        )
    )

    return found[0]


def outcome_from_row(row: pd.Series) -> str:
    for column in (
        "Over25",
        "Outcome",
        "Esito",
        "Result",
    ):
        if column not in row.index:
            continue

        value = text(
            row.get(column)
        ).upper()

        if value in VALID_OUTCOMES:
            return value

    hg = to_int(
        row.get("HG")
    )

    ag = to_int(
        row.get("AG")
    )

    if hg is None or ag is None:
        return ""

    return (
        "OK"
        if hg + ag >= 3
        else "KO"
    )


def source_league_id(
    row: pd.Series,
    side: str,
) -> str:
    source_col = (
        f"{side}SourceLeagueId"
    )

    if source_col in row.index:
        source = text(
            row.get(source_col)
        )

        if source:
            return source

    return text(
        row.get("LeagueId")
    )


def load_results(
    league_id: str,
    cache: dict[str, pd.DataFrame | None],
) -> pd.DataFrame | None:
    if league_id in cache:
        return cache[
            league_id
        ]

    path = (
        RESULTS_ROOT
        / f"{league_id}.csv"
    )

    if not path.exists():
        cache[
            league_id
        ] = None
        return None

    df = read_csv(
        path
    )

    date_col = (
        "MatchDate"
        if "MatchDate" in df.columns
        else "Date"
        if "Date" in df.columns
        else None
    )

    required = {
        "Home",
        "Away",
        "HG",
        "AG",
    }

    if (
        date_col is None
        or not required.issubset(
            df.columns
        )
    ):
        cache[
            league_id
        ] = None

        return None

    clean = pd.DataFrame()

    clean["Date"] = df[
        date_col
    ].map(
        parse_date
    )

    clean["Home"] = df[
        "Home"
    ].map(
        normalize_team
    )

    clean["Away"] = df[
        "Away"
    ].map(
        normalize_team
    )

    clean["HG"] = df[
        "HG"
    ].map(
        to_int
    )

    clean["AG"] = df[
        "AG"
    ].map(
        to_int
    )

    clean = clean[
        clean["Date"].notna()
        & clean["HG"].notna()
        & clean["AG"].notna()
    ].copy()

    clean = clean.sort_values(
        "Date"
    ).reset_index(
        drop=True
    )

    cache[
        league_id
    ] = clean

    return clean


def team_defense_snapshot(
    *,
    league_id: str,
    team: str,
    before_date: date,
    cache: dict[str, pd.DataFrame | None],
) -> dict | None:
    results = load_results(
        league_id,
        cache,
    )

    if results is None:
        return None

    canonical = normalize_team(
        team
    )

    games = []

    for _, match in results.iterrows():
        match_date = match[
            "Date"
        ]

        if match_date >= before_date:
            continue

        home = match[
            "Home"
        ]

        away = match[
            "Away"
        ]

        if canonical == home:
            ga = int(
                match["AG"]
            )

        elif canonical == away:
            ga = int(
                match["HG"]
            )

        else:
            continue

        games.append(
            ga
        )

    played = len(
        games
    )

    if played == 0:
        return {
            "Played": 0,
            "GApg": None,
            "GALast5Avg": None,
        }

    gapg = (
        sum(games)
        / played
    )

    recent = games[
        -RECENT_N:
    ]

    recent_ga = (
        sum(recent)
        / len(recent)
        if len(recent)
        >= RECENT_N
        else None
    )

    return {
        "Played": played,
        "GApg": round(
            gapg,
            4,
        ),
        "GALast5Avg": (
            round(
                recent_ga,
                4,
            )
            if recent_ga
            is not None
            else None
        ),
    }


def prepare_matches() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    cache: dict[
        str,
        pd.DataFrame | None,
    ] = {}

    rows = []
    unmatched = []

    for engine in ENGINES:
        history_path = find_history(
            engine
        )

        if history_path is None:
            unmatched.append(
                {
                    "Engine": engine,
                    "Reason": (
                        "Storico ranking non trovato"
                    ),
                }
            )
            continue

        history = read_csv(
            history_path
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
            unmatched.append(
                {
                    "Engine": engine,
                    "Reason": (
                        "Colonne ranking obbligatorie mancanti"
                    ),
                }
            )
            continue

        for _, row in history.iterrows():
            band = text(
                row.get("Band")
            ).upper()

            if band != "ALTA":
                continue

            outcome = outcome_from_row(
                row
            )

            if outcome not in VALID_OUTCOMES:
                continue

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

            if match_date is None:
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": text(
                            row.get(
                                "LeagueId"
                            )
                        ),
                        "Home": text(
                            row.get(
                                "Home"
                            )
                        ),
                        "Away": text(
                            row.get(
                                "Away"
                            )
                        ),
                        "Reason": (
                            "Data non valida"
                        ),
                    }
                )
                continue

            home_source = source_league_id(
                row,
                "Home",
            )

            away_source = source_league_id(
                row,
                "Away",
            )

            home = text(
                row.get("Home")
            )

            away = text(
                row.get("Away")
            )

            home_def = team_defense_snapshot(
                league_id=home_source,
                team=home,
                before_date=match_date,
                cache=cache,
            )

            away_def = team_defense_snapshot(
                league_id=away_source,
                team=away,
                before_date=match_date,
                cache=cache,
            )

            if (
                home_def is None
                or away_def is None
            ):
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": text(
                            row.get(
                                "LeagueId"
                            )
                        ),
                        "Home": home,
                        "Away": away,
                        "Reason": (
                            "Storico risultati non disponibile"
                        ),
                    }
                )
                continue

            if (
                home_def[
                    "Played"
                ]
                < MIN_SEASON_MATCHES
                or away_def[
                    "Played"
                ]
                < MIN_SEASON_MATCHES
            ):
                unmatched.append(
                    {
                        "Engine": engine,
                        "LeagueId": text(
                            row.get(
                                "LeagueId"
                            )
                        ),
                        "Home": home,
                        "Away": away,
                        "HomePlayed": (
                            home_def[
                                "Played"
                            ]
                        ),
                        "AwayPlayed": (
                            away_def[
                                "Played"
                            ]
                        ),
                        "Reason": (
                            "Meno di 5 gare precedenti"
                        ),
                    }
                )
                continue

            home_ga = home_def[
                "GApg"
            ]

            away_ga = away_def[
                "GApg"
            ]

            home_last5 = home_def[
                "GALast5Avg"
            ]

            away_last5 = away_def[
                "GALast5Avg"
            ]

            rows.append(
                {
                    "Engine": engine,
                    "MatchDate": (
                        match_date
                        .isoformat()
                    ),
                    "LeagueId": text(
                        row.get(
                            "LeagueId"
                        )
                    ),
                    "Home": home,
                    "Away": away,
                    "Outcome": outcome,
                    "Score": row.get(
                        "Score",
                        "",
                    ),
                    "HomeSourceLeagueId": (
                        home_source
                    ),
                    "AwaySourceLeagueId": (
                        away_source
                    ),
                    "HomePlayed": (
                        home_def[
                            "Played"
                        ]
                    ),
                    "AwayPlayed": (
                        away_def[
                            "Played"
                        ]
                    ),
                    "HomeGApg": (
                        home_ga
                    ),
                    "AwayGApg": (
                        away_ga
                    ),
                    "BestDefenseGApg": min(
                        home_ga,
                        away_ga,
                    ),
                    "WorstDefenseGApg": max(
                        home_ga,
                        away_ga,
                    ),
                    "HomeGALast5Avg": (
                        home_last5
                    ),
                    "AwayGALast5Avg": (
                        away_last5
                    ),
                    "BestDefenseLast5GA": (
                        min(
                            home_last5,
                            away_last5,
                        )
                        if (
                            home_last5
                            is not None
                            and away_last5
                            is not None
                        )
                        else None
                    ),
                    "WorstDefenseLast5GA": (
                        max(
                            home_last5,
                            away_last5,
                        )
                        if (
                            home_last5
                            is not None
                            and away_last5
                            is not None
                        )
                        else None
                    ),
                }
            )

    return (
        pd.DataFrame(
            rows
        ),
        pd.DataFrame(
            unmatched
        ),
    )


def group_stats(
    frame: pd.DataFrame,
) -> dict:
    ok = int(
        (
            frame[
                "Outcome"
            ]
            == "OK"
        ).sum()
    )

    ko = int(
        (
            frame[
                "Outcome"
            ]
            == "KO"
        ).sum()
    )

    return {
        "OK": ok,
        "KO": ko,
        "Total": (
            ok + ko
        ),
        "HitRate": (
            safe_rate(
                ok,
                ko,
            )
        ),
    }


def baseline_report(
    details: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for engine, group in details.groupby(
        "Engine"
    ):
        row = {
            "Engine": engine,
        }

        row.update(
            group_stats(
                group
            )
        )

        rows.append(
            row
        )

    return pd.DataFrame(
        rows
    ).sort_values(
        "HitRate",
        ascending=False,
    )


def threshold_report(
    details: pd.DataFrame,
    *,
    metric_type: str,
) -> pd.DataFrame:
    rows = []

    if metric_type == "SEASON":
        home_col = "HomeGApg"
        away_col = "AwayGApg"
    else:
        home_col = (
            "HomeGALast5Avg"
        )
        away_col = (
            "AwayGALast5Avg"
        )

    for engine, engine_df in details.groupby(
        "Engine"
    ):
        baseline = group_stats(
            engine_df
        )

        valid = engine_df[
            engine_df[
                home_col
            ].notna()
            & engine_df[
                away_col
            ].notna()
        ].copy()

        for threshold in THRESHOLDS:
            rules = {
                "AT_LEAST_ONE_STRONG": (
                    (valid[home_col] <= threshold)
                    | (valid[away_col] <= threshold)
                ),
                "BOTH_STRONG": (
                    (valid[home_col] <= threshold)
                    & (valid[away_col] <= threshold)
                ),
                "HOME_STRONG": (
                    valid[home_col] <= threshold
                ),
                "AWAY_STRONG": (
                    valid[away_col] <= threshold
                ),
            }

            for rule_name, mask in rules.items():
                subset = valid[
                    mask
                ]

                stats = group_stats(
                    subset
                )

                rows.append(
                    {
                        "Engine": (
                            engine
                        ),
                        "Metric": (
                            metric_type
                        ),
                        "Rule": (
                            rule_name
                        ),
                        "Threshold": (
                            threshold
                        ),
                        "Baseline_OK": (
                            baseline[
                                "OK"
                            ]
                        ),
                        "Baseline_KO": (
                            baseline[
                                "KO"
                            ]
                        ),
                        "Baseline_Total": (
                            baseline[
                                "Total"
                            ]
                        ),
                        "Baseline_HitRate": (
                            baseline[
                                "HitRate"
                            ]
                        ),
                        **stats,
                        "DeltaVsBaseline": round(
                            stats[
                                "HitRate"
                            ]
                            - baseline[
                                "HitRate"
                            ],
                            4,
                        ),
                        "KO_Rate": round(
                            (
                                stats[
                                    "KO"
                                ]
                                / stats[
                                    "Total"
                                ]
                                * 100
                            )
                            if stats[
                                "Total"
                            ]
                            else 0.0,
                            4,
                        ),
                    }
                )

    return pd.DataFrame(
        rows
    )


def bucket_report(
    details: pd.DataFrame,
    *,
    metric_type: str,
) -> pd.DataFrame:
    rows = []

    if metric_type == "SEASON":
        metric_col = (
            "BestDefenseGApg"
        )
    else:
        metric_col = (
            "BestDefenseLast5GA"
        )

    for engine, engine_df in details.groupby(
        "Engine"
    ):
        valid = engine_df[
            engine_df[
                metric_col
            ].notna()
        ].copy()

        for low, high in GA_BUCKETS:
            if high is None:
                mask = (
                    valid[
                        metric_col
                    ]
                    >= low
                )

                label = (
                    f">={low:.2f}"
                )
            else:
                mask = (
                    (
                        valid[
                            metric_col
                        ]
                        >= low
                    )
                    & (
                        valid[
                            metric_col
                        ]
                        < high
                    )
                )

                label = (
                    f"{low:.2f}-{high:.2f}"
                )

            subset = valid[
                mask
            ]

            stats = group_stats(
                subset
            )

            rows.append(
                {
                    "Engine": engine,
                    "Metric": (
                        metric_type
                    ),
                    "Bucket": label,
                    **stats,
                }
            )

    return pd.DataFrame(
        rows
    )


def candidate_report(
    season: pd.DataFrame,
    last5: pd.DataFrame,
) -> pd.DataFrame:
    all_rows = pd.concat(
        [
            season,
            last5,
        ],
        ignore_index=True,
    )

    candidates = all_rows[
        all_rows[
            "Total"
        ]
        > 0
    ].copy()

    candidates[
        "AbsoluteDrop"
    ] = (
        -candidates[
            "DeltaVsBaseline"
        ]
    )

    return candidates.sort_values(
        by=[
            "AbsoluteDrop",
            "KO_Rate",
            "Total",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    ).reset_index(
        drop=True
    )


def no_australia_candidates(
    details: pd.DataFrame,
) -> pd.DataFrame:
    no_au = details[
        ~details[
            "LeagueId"
        ]
        .fillna("")
        .astype(str)
        .str.startswith(
            "Australia_"
        )
    ].copy()

    season = threshold_report(
        no_au,
        metric_type="SEASON",
    )

    last5 = threshold_report(
        no_au,
        metric_type="LAST5",
    )

    return candidate_report(
        season,
        last5,
    )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    details, unmatched = (
        prepare_matches()
    )

    if details.empty:
        raise RuntimeError(
            "Nessuna ALTA ricostruibile."
        )

    baseline = baseline_report(
        details
    )

    season_thresholds = (
        threshold_report(
            details,
            metric_type="SEASON",
        )
    )

    last5_thresholds = (
        threshold_report(
            details,
            metric_type="LAST5",
        )
    )

    season_buckets = (
        bucket_report(
            details,
            metric_type="SEASON",
        )
    )

    last5_buckets = (
        bucket_report(
            details,
            metric_type="LAST5",
        )
    )

    candidates = candidate_report(
        season_thresholds,
        last5_thresholds,
    )

    no_au = (
        no_australia_candidates(
            details
        )
    )

    outputs = {
        "01_baseline_by_engine.csv": (
            baseline
        ),
        "02_thresholds_season.csv": (
            season_thresholds
        ),
        "03_thresholds_last5.csv": (
            last5_thresholds
        ),
        "04_buckets_season.csv": (
            season_buckets
        ),
        "05_buckets_last5.csv": (
            last5_buckets
        ),
        "06_match_details.csv": (
            details
        ),
        "07_candidate_signals.csv": (
            candidates
        ),
        "08_no_australia.csv": (
            no_au
        ),
        "09_unmatched.csv": (
            unmatched
        ),
    }

    for filename, frame in outputs.items():
        frame.to_csv(
            OUTPUT_DIR
            / filename,
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )

    print(
        "=== STRONG DEFENSE EXPERIMENT ==="
    )

    print(
        f"ALTA ricostruite: "
        f"{len(details)}"
    )

    print(
        f"Non ricostruite: "
        f"{len(unmatched)}"
    )

    print()
    print(
        "BASELINE"
    )
    print(
        baseline.to_string(
            index=False
        )
    )

    print()
    print(
        "TOP 20 SEGNALI DI RISCHIO"
    )

    display = [
        "Engine",
        "Metric",
        "Rule",
        "Threshold",
        "OK",
        "KO",
        "Total",
        "HitRate",
        "Baseline_HitRate",
        "DeltaVsBaseline",
    ]

    print(
        candidates[
            display
        ].head(
            20
        ).to_string(
            index=False
        )
    )

    print()
    print(
        f"Output: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
