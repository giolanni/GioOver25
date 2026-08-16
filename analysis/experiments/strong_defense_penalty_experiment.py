"""
===============================================================================
GioOver2.5 - STRONG DEFENSE PENALTY OPTIMIZER
===============================================================================

OBIETTIVO
---------
Secondo experiment sul fenomeno "difesa forte".

Il primo experiment ha verificato se le ALTA diventano meno affidabili quando
una o entrambe le squadre concedono pochi gol.

Questo secondo experiment cerca automaticamente la combinazione migliore di:

    1) metrica difensiva
    2) lato/condizione
    3) soglia
    4) penalità da sottrarre allo score

Lo script NON modifica alcun engine.

===============================================================================
INPUT
===============================================================================

Usa direttamente l'output del primo experiment:

    analysis/experiments/strong_defense/06_match_details.csv

Quel file contiene esclusivamente partite che erano originariamente ALTA e,
per ciascuna, le metriche difensive ricostruite SENZA lookahead.

===============================================================================
METRICHE TESTATE
===============================================================================

SEASON
    HomeGApg
    AwayGApg

LAST5
    HomeGALast5Avg
    AwayGALast5Avg

===============================================================================
CONDIZIONI TESTATE
===============================================================================

HOME_STRONG
    Home GA <= soglia

AWAY_STRONG
    Away GA <= soglia

AT_LEAST_ONE_STRONG
    almeno una delle due difese <= soglia

BOTH_STRONG
    entrambe le difese <= soglia

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

===============================================================================
PENALITÀ TESTATE
===============================================================================

PENALTIES = (
    1, 2, 3, 4, 5,
    6, 7, 8, 9, 10,
    11, 12, 13, 14, 15,
)

Esempio:

    Score originale = 81
    Away Last5 GA = 1.00
    soglia = 1.10
    penalità = 7

    nuovo score = 74
    la partita non è più ALTA.

===============================================================================
COME VIENE VALUTATA UNA CONFIGURAZIONE
===============================================================================

Per ogni partita originariamente ALTA:

    se la condizione NON scatta:
        AdjustedScore = Score originale

    se la condizione scatta:
        AdjustedScore = Score originale - Penalità

    AdjustedBand = ALTA se AdjustedScore >= 75
                   NON_ALTA altrimenti

Quindi questo experiment studia una PENALITÀ PURA:
può soltanto rimuovere ALTA rischiose, non crearne di nuove.

===============================================================================
CRITERIO DI CLASSIFICA
===============================================================================

Priorità GioOver2.5:

    1. % OK delle ALTA rimaste
    2. meno KO
    3. numerosità soltanto come robustezza

ATTENZIONE:
la classifica completa include anche configurazioni con campioni piccoli.

Per evitare di scambiare un 5/5 per una regola già affidabile, viene prodotto
anche un file "stable" con campione minimo configurabile.

===============================================================================
VALIDAZIONE TEMPORALE
===============================================================================

TRAIN_RATIO = 0.70

Per ciascun engine:
    TRAIN = primo 70% delle date
    TEST  = ultimo 30%

Questo NON viene usato per alterare i pesi.
Serve a verificare se la configurazione trovata regge nel periodo più recente.

===============================================================================
OUTPUT
===============================================================================

analysis/experiments/strong_defense_penalty/

01_baseline.csv
    Baseline ALTA originale per engine.

02_all_configs.csv
    Tutte le combinazioni soglia/regola/penalità.

03_best_by_engine.csv
    Migliore configurazione per engine, ordinata prima per TEST % OK e poi
    per Overall % OK.

04_stable_configs.csv
    Configurazioni con almeno MIN_STABLE_TOTAL ALTA overall e
    MIN_STABLE_TEST_TOTAL ALTA nel test cronologico.

05_top_stable_by_engine.csv
    Top configurazioni stabili di ogni engine.

06_no_australia.csv
    Tutte le configurazioni con metriche NO Australia.

07_removed_matches.csv
    Partite che ogni configurazione TOP stabile toglierebbe dalla ALTA.

08_kept_matches.csv
    Partite mantenute ALTA dalle configurazioni TOP stabili.

09_engine_comparison.csv
    Baseline vs best stabile per ciascun engine.

===============================================================================
PARAMETRI MODIFICABILI
===============================================================================

ALTA_THRESHOLD = 75.0

TRAIN_RATIO = 0.70

MIN_STABLE_TOTAL = 30
    minimo di ALTA rimaste overall per considerare la configurazione "stabile"

MIN_STABLE_TEST_TOTAL = 10
    minimo di ALTA rimaste nel periodo TEST

TOP_STABLE_PER_ENGINE = 10
    quante configurazioni esportare nel dettaglio partite

===============================================================================
ESECUZIONE
===============================================================================

python -m analysis.experiments.strong_defense_penalty_experiment

===============================================================================
STEP SUCCESSIVO
===============================================================================

Se una configurazione resta superiore alla baseline:

1. creare un engine sperimentale dedicato;
2. farlo girare quotidianamente insieme agli engine ufficiali;
3. confrontarlo nel tempo;
4. promuoverlo a riferimento solo se il vantaggio resta stabile.

===============================================================================
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np


INPUT_FILE = Path(
    "analysis/experiments/strong_defense/06_match_details.csv"
)

OUTPUT_DIR = Path(
    "analysis/experiments/strong_defense_penalty"
)

ALTA_THRESHOLD = 75.0
TRAIN_RATIO = 0.70

MIN_STABLE_TOTAL = 30
MIN_STABLE_TEST_TOTAL = 10
TOP_STABLE_PER_ENGINE = 10

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

PENALTIES = tuple(range(1, 16))

METRICS = {
    "SEASON": (
        "HomeGApg",
        "AwayGApg",
    ),
    "LAST5": (
        "HomeGALast5Avg",
        "AwayGALast5Avg",
    ),
}

RULES = (
    "HOME_STRONG",
    "AWAY_STRONG",
    "AT_LEAST_ONE_STRONG",
    "BOTH_STRONG",
)


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko
    return round(
        ok / total * 100.0,
        4,
    ) if total else 0.0


def stats(
    df: pd.DataFrame,
) -> dict:
    ok = int(
        (df["Outcome"] == "OK").sum()
    )
    ko = int(
        (df["Outcome"] == "KO").sum()
    )

    return {
        "OK": ok,
        "KO": ko,
        "Total": ok + ko,
        "HitRate": safe_rate(
            ok,
            ko,
        ),
    }


def load_data() -> pd.DataFrame:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File non trovato: {INPUT_FILE}\n"
            "Esegui prima strong_defense_experiment."
        )

    df = pd.read_csv(
        INPUT_FILE,
        sep=";",
        encoding="utf-8-sig",
        low_memory=False,
    )

    required = {
        "Engine",
        "MatchDate",
        "LeagueId",
        "Home",
        "Away",
        "Outcome",
        "Score",
        "HomeGApg",
        "AwayGApg",
        "HomeGALast5Avg",
        "AwayGALast5Avg",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            "Colonne mancanti: "
            + ", ".join(
                sorted(missing)
            )
        )

    df = df.copy()

    df["Score"] = pd.to_numeric(
        df["Score"],
        errors="coerce",
    )

    for column in (
        "HomeGApg",
        "AwayGApg",
        "HomeGALast5Avg",
        "AwayGALast5Avg",
    ):
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce",
        )

    df["MatchDateParsed"] = pd.to_datetime(
        df["MatchDate"],
        errors="coerce",
    )

    df["Outcome"] = (
        df["Outcome"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df = df[
        df["Outcome"].isin(
            {"OK", "KO"}
        )
        & df["Score"].notna()
    ].copy()

    return df


def split_masks(
    engine_df: pd.DataFrame,
) -> tuple[pd.Series, pd.Series, str]:
    dates = (
        engine_df[
            "MatchDateParsed"
        ]
        .dropna()
        .dt.normalize()
        .sort_values()
        .unique()
    )

    if len(dates) < 2:
        train_mask = pd.Series(
            False,
            index=engine_df.index,
        )
        test_mask = pd.Series(
            True,
            index=engine_df.index,
        )

        return (
            train_mask,
            test_mask,
            "",
        )

    split_index = int(
        len(dates)
        * TRAIN_RATIO
    )

    split_index = max(
        1,
        min(
            split_index,
            len(dates) - 1,
        ),
    )

    split_date = pd.Timestamp(
        dates[split_index]
    )

    train_mask = (
        engine_df[
            "MatchDateParsed"
        ].notna()
        & (
            engine_df[
                "MatchDateParsed"
            ]
            < split_date
        )
    )

    test_mask = (
        engine_df[
            "MatchDateParsed"
        ].notna()
        & (
            engine_df[
                "MatchDateParsed"
            ]
            >= split_date
        )
    )

    return (
        train_mask,
        test_mask,
        split_date.date().isoformat(),
    )


def build_condition(
    df: pd.DataFrame,
    *,
    home_col: str,
    away_col: str,
    rule: str,
    threshold: float,
) -> pd.Series:
    valid_home = df[
        home_col
    ].notna()

    valid_away = df[
        away_col
    ].notna()

    home_strong = (
        valid_home
        & (
            df[home_col]
            <= threshold
        )
    )

    away_strong = (
        valid_away
        & (
            df[away_col]
            <= threshold
        )
    )

    if rule == "HOME_STRONG":
        return home_strong

    if rule == "AWAY_STRONG":
        return away_strong

    if rule == "AT_LEAST_ONE_STRONG":
        return (
            home_strong
            | away_strong
        )

    if rule == "BOTH_STRONG":
        return (
            home_strong
            & away_strong
        )

    raise ValueError(
        f"Regola sconosciuta: {rule}"
    )


def evaluate_one(
    engine_df: pd.DataFrame,
    *,
    metric: str,
    rule: str,
    threshold: float,
    penalty: int,
    train_mask: pd.Series,
    test_mask: pd.Series,
    split_date: str,
) -> tuple[dict, pd.Series, pd.Series]:
    home_col, away_col = (
        METRICS[metric]
    )

    condition = build_condition(
        engine_df,
        home_col=home_col,
        away_col=away_col,
        rule=rule,
        threshold=threshold,
    )

    adjusted_score = (
        engine_df["Score"]
        - condition.astype(int)
        * penalty
    )

    kept_mask = (
        adjusted_score
        >= ALTA_THRESHOLD
    )

    kept = engine_df[
        kept_mask
    ]

    removed = engine_df[
        ~kept_mask
    ]

    overall = stats(
        kept
    )

    train = stats(
        engine_df[
            kept_mask
            & train_mask
        ]
    )

    test = stats(
        engine_df[
            kept_mask
            & test_mask
        ]
    )

    no_au_mask = (
        ~engine_df[
            "LeagueId"
        ]
        .fillna("")
        .astype(str)
        .str.startswith(
            "Australia_"
        )
    )

    no_au = stats(
        engine_df[
            kept_mask
            & no_au_mask
        ]
    )

    removed_stats = stats(
        removed
    )

    affected = int(
        condition.sum()
    )

    row = {
        "Engine": (
            engine_df[
                "Engine"
            ].iloc[0]
        ),
        "Metric": metric,
        "Rule": rule,
        "Threshold": threshold,
        "Penalty": penalty,

        "Affected": affected,

        "Overall_OK": (
            overall["OK"]
        ),
        "Overall_KO": (
            overall["KO"]
        ),
        "Overall_Total": (
            overall["Total"]
        ),
        "Overall_HitRate": (
            overall["HitRate"]
        ),

        "Removed_OK": (
            removed_stats["OK"]
        ),
        "Removed_KO": (
            removed_stats["KO"]
        ),
        "Removed_Total": (
            removed_stats["Total"]
        ),
        "Removed_HitRate": (
            removed_stats["HitRate"]
        ),

        "Train_OK": (
            train["OK"]
        ),
        "Train_KO": (
            train["KO"]
        ),
        "Train_Total": (
            train["Total"]
        ),
        "Train_HitRate": (
            train["HitRate"]
        ),

        "Test_OK": (
            test["OK"]
        ),
        "Test_KO": (
            test["KO"]
        ),
        "Test_Total": (
            test["Total"]
        ),
        "Test_HitRate": (
            test["HitRate"]
        ),

        "NoAU_OK": (
            no_au["OK"]
        ),
        "NoAU_KO": (
            no_au["KO"]
        ),
        "NoAU_Total": (
            no_au["Total"]
        ),
        "NoAU_HitRate": (
            no_au["HitRate"]
        ),

        "SplitDate": (
            split_date
        ),
    }

    return (
        row,
        condition,
        kept_mask,
    )


def baseline_report(
    df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for engine, group in df.groupby(
        "Engine"
    ):
        train_mask, test_mask, split_date = (
            split_masks(
                group
            )
        )

        overall = stats(
            group
        )

        train = stats(
            group[
                train_mask
            ]
        )

        test = stats(
            group[
                test_mask
            ]
        )

        no_au = stats(
            group[
                ~group[
                    "LeagueId"
                ]
                .fillna("")
                .astype(str)
                .str.startswith(
                    "Australia_"
                )
            ]
        )

        rows.append(
            {
                "Engine": engine,
                "Overall_OK": (
                    overall["OK"]
                ),
                "Overall_KO": (
                    overall["KO"]
                ),
                "Overall_Total": (
                    overall["Total"]
                ),
                "Overall_HitRate": (
                    overall["HitRate"]
                ),
                "Train_OK": (
                    train["OK"]
                ),
                "Train_KO": (
                    train["KO"]
                ),
                "Train_Total": (
                    train["Total"]
                ),
                "Train_HitRate": (
                    train["HitRate"]
                ),
                "Test_OK": (
                    test["OK"]
                ),
                "Test_KO": (
                    test["KO"]
                ),
                "Test_Total": (
                    test["Total"]
                ),
                "Test_HitRate": (
                    test["HitRate"]
                ),
                "NoAU_OK": (
                    no_au["OK"]
                ),
                "NoAU_KO": (
                    no_au["KO"]
                ),
                "NoAU_Total": (
                    no_au["Total"]
                ),
                "NoAU_HitRate": (
                    no_au["HitRate"]
                ),
                "SplitDate": (
                    split_date
                ),
            }
        )

    return pd.DataFrame(
        rows
    )


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = load_data()

    baseline = baseline_report(
        data
    )

    baseline_lookup = (
        baseline
        .set_index(
            "Engine"
        )
        .to_dict(
            orient="index"
        )
    )

    config_rows = []

    # Conserviamo questi dati per esportare il dettaglio dei top.
    mask_cache = {}

    for engine, engine_df in data.groupby(
        "Engine"
    ):
        engine_df = (
            engine_df
            .copy()
        )

        train_mask, test_mask, split_date = (
            split_masks(
                engine_df
            )
        )

        for metric in METRICS:
            for rule in RULES:
                for threshold in THRESHOLDS:
                    for penalty in PENALTIES:
                        (
                            row,
                            condition,
                            kept_mask,
                        ) = evaluate_one(
                            engine_df,
                            metric=metric,
                            rule=rule,
                            threshold=threshold,
                            penalty=penalty,
                            train_mask=train_mask,
                            test_mask=test_mask,
                            split_date=split_date,
                        )

                        base = baseline_lookup[
                            engine
                        ]

                        row[
                            "DeltaOverallVsBaseline"
                        ] = round(
                            row[
                                "Overall_HitRate"
                            ]
                            - base[
                                "Overall_HitRate"
                            ],
                            4,
                        )

                        row[
                            "DeltaTestVsBaseline"
                        ] = round(
                            row[
                                "Test_HitRate"
                            ]
                            - base[
                                "Test_HitRate"
                            ],
                            4,
                        )

                        row[
                            "DeltaNoAUVsBaseline"
                        ] = round(
                            row[
                                "NoAU_HitRate"
                            ]
                            - base[
                                "NoAU_HitRate"
                            ],
                            4,
                        )

                        config_id = (
                            f"{engine}|{metric}|{rule}|"
                            f"{threshold:.2f}|P{penalty}"
                        )

                        row[
                            "ConfigId"
                        ] = config_id

                        config_rows.append(
                            row
                        )

                        mask_cache[
                            config_id
                        ] = (
                            engine_df.index,
                            condition,
                            kept_mask,
                            adjusted_score := (
                                engine_df[
                                    "Score"
                                ]
                                - condition.astype(int)
                                * penalty
                            ),
                        )

    all_configs = pd.DataFrame(
        config_rows
    )

    # Classifica completa secondo la filosofia GioOver2.5.
    all_configs = all_configs.sort_values(
        by=[
            "Engine",
            "Test_HitRate",
            "Test_KO",
            "Overall_HitRate",
            "Overall_KO",
            "Overall_Total",
        ],
        ascending=[
            True,
            False,
            True,
            False,
            True,
            False,
        ],
    ).reset_index(
        drop=True
    )

    stable = all_configs[
        (
            all_configs[
                "Overall_Total"
            ]
            >= MIN_STABLE_TOTAL
        )
        & (
            all_configs[
                "Test_Total"
            ]
            >= MIN_STABLE_TEST_TOTAL
        )
    ].copy()

    stable = stable.sort_values(
        by=[
            "Engine",
            "Test_HitRate",
            "Test_KO",
            "Overall_HitRate",
            "Overall_KO",
            "Overall_Total",
        ],
        ascending=[
            True,
            False,
            True,
            False,
            True,
            False,
        ],
    )

    best_by_engine = (
        all_configs
        .groupby(
            "Engine",
            as_index=False,
            sort=False,
        )
        .head(1)
        .copy()
    )

    top_stable = (
        stable
        .groupby(
            "Engine",
            group_keys=False,
            sort=False,
        )
        .head(
            TOP_STABLE_PER_ENGINE
        )
        .copy()
    )

    # Confronto baseline vs miglior configurazione stabile.
    comparison_rows = []

    for _, base in baseline.iterrows():
        engine = base[
            "Engine"
        ]

        engine_best = stable[
            stable[
                "Engine"
            ]
            == engine
        ].head(
            1
        )

        comparison_rows.append(
            {
                "Engine": engine,
                "Role": "BASELINE",
                "ConfigId": "BASELINE",
                "Metric": "",
                "Rule": "",
                "Threshold": "",
                "Penalty": 0,
                "Overall_OK": (
                    base[
                        "Overall_OK"
                    ]
                ),
                "Overall_KO": (
                    base[
                        "Overall_KO"
                    ]
                ),
                "Overall_Total": (
                    base[
                        "Overall_Total"
                    ]
                ),
                "Overall_HitRate": (
                    base[
                        "Overall_HitRate"
                    ]
                ),
                "Test_OK": (
                    base[
                        "Test_OK"
                    ]
                ),
                "Test_KO": (
                    base[
                        "Test_KO"
                    ]
                ),
                "Test_Total": (
                    base[
                        "Test_Total"
                    ]
                ),
                "Test_HitRate": (
                    base[
                        "Test_HitRate"
                    ]
                ),
                "NoAU_HitRate": (
                    base[
                        "NoAU_HitRate"
                    ]
                ),
            }
        )

        if not engine_best.empty:
            best = engine_best.iloc[
                0
            ]

            comparison_rows.append(
                {
                    "Engine": engine,
                    "Role": (
                        "BEST_STABLE"
                    ),
                    "ConfigId": (
                        best[
                            "ConfigId"
                        ]
                    ),
                    "Metric": (
                        best[
                            "Metric"
                        ]
                    ),
                    "Rule": (
                        best[
                            "Rule"
                        ]
                    ),
                    "Threshold": (
                        best[
                            "Threshold"
                        ]
                    ),
                    "Penalty": (
                        best[
                            "Penalty"
                        ]
                    ),
                    "Overall_OK": (
                        best[
                            "Overall_OK"
                        ]
                    ),
                    "Overall_KO": (
                        best[
                            "Overall_KO"
                        ]
                    ),
                    "Overall_Total": (
                        best[
                            "Overall_Total"
                        ]
                    ),
                    "Overall_HitRate": (
                        best[
                            "Overall_HitRate"
                        ]
                    ),
                    "Test_OK": (
                        best[
                            "Test_OK"
                        ]
                    ),
                    "Test_KO": (
                        best[
                            "Test_KO"
                        ]
                    ),
                    "Test_Total": (
                        best[
                            "Test_Total"
                        ]
                    ),
                    "Test_HitRate": (
                        best[
                            "Test_HitRate"
                        ]
                    ),
                    "NoAU_HitRate": (
                        best[
                            "NoAU_HitRate"
                        ]
                    ),
                }
            )

    engine_comparison = pd.DataFrame(
        comparison_rows
    )

    # No-Australia ordinato secondo % NO-AU.
    no_au = all_configs.sort_values(
        by=[
            "Engine",
            "NoAU_HitRate",
            "NoAU_KO",
            "NoAU_Total",
        ],
        ascending=[
            True,
            False,
            True,
            False,
        ],
    ).copy()

    # Dettaglio partite dei top stabili.
    removed_frames = []
    kept_frames = []

    for _, config in top_stable.iterrows():
        config_id = config[
            "ConfigId"
        ]

        (
            indexes,
            condition,
            kept_mask,
            adjusted_score,
        ) = mask_cache[
            config_id
        ]

        source = data.loc[
            indexes
        ].copy()

        source[
            "ConditionTriggered"
        ] = condition.values

        source[
            "AdjustedScore"
        ] = adjusted_score.values

        source.insert(
            0,
            "ConfigId",
            config_id,
        )

        source.insert(
            1,
            "Metric",
            config[
                "Metric"
            ],
        )

        source.insert(
            2,
            "Rule",
            config[
                "Rule"
            ],
        )

        source.insert(
            3,
            "Threshold",
            config[
                "Threshold"
            ],
        )

        source.insert(
            4,
            "Penalty",
            config[
                "Penalty"
            ],
        )

        removed = source[
            ~kept_mask.values
        ].copy()

        kept = source[
            kept_mask.values
        ].copy()

        removed_frames.append(
            removed
        )

        kept_frames.append(
            kept
        )

    removed_matches = (
        pd.concat(
            removed_frames,
            ignore_index=True,
        )
        if removed_frames
        else pd.DataFrame()
    )

    kept_matches = (
        pd.concat(
            kept_frames,
            ignore_index=True,
        )
        if kept_frames
        else pd.DataFrame()
    )

    baseline.to_csv(
        OUTPUT_DIR
        / "01_baseline.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    all_configs.to_csv(
        OUTPUT_DIR
        / "02_all_configs.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    best_by_engine.to_csv(
        OUTPUT_DIR
        / "03_best_by_engine.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    stable.to_csv(
        OUTPUT_DIR
        / "04_stable_configs.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    top_stable.to_csv(
        OUTPUT_DIR
        / "05_top_stable_by_engine.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    no_au.to_csv(
        OUTPUT_DIR
        / "06_no_australia.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    removed_matches.to_csv(
        OUTPUT_DIR
        / "07_removed_matches.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    kept_matches.to_csv(
        OUTPUT_DIR
        / "08_kept_matches.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    engine_comparison.to_csv(
        OUTPUT_DIR
        / "09_engine_comparison.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        "=== STRONG DEFENSE PENALTY OPTIMIZER ==="
    )

    print(
        f"Partite ALTA analizzate: "
        f"{len(data)}"
    )

    print(
        f"Configurazioni testate: "
        f"{len(all_configs)}"
    )

    print()
    print(
        "BASELINE vs BEST STABLE"
    )

    print(
        engine_comparison.to_string(
            index=False
        )
    )

    print()
    print(
        f"Output: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
