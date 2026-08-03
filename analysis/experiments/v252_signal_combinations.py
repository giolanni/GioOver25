"""
===============================================================================
GioOver2.5 - Analisi combinazioni di segnali di rischio
===============================================================================

SCOPO
-----
Misurare quali COPPIE e TRIPLE di segnali di rischio sono realmente associate
a una riduzione della percentuale di Over 2.5.

A differenza dell'esperimento basato sul semplice conteggio dei segnali, questo
script verifica l'identità precisa dei segnali che compaiono insieme.

INPUT
-----
analysis/laboratory/data/01_matches.csv

OUTPUT
------
analysis/experiments/v252_signal_combinations/

    01_pair_results.csv
    02_triple_results.csv
    03_all_combinations.csv
    04_best_risk_combinations.csv
    05_match_details.csv

USO
---
python -m analysis.experiments.v252_signal_combinations

INTERPRETAZIONE
---------------
- HitRate: percentuale OK nella combinazione.
- BaselineHitRate: percentuale OK della stessa fascia sull'intero campione.
- LiftVsBaseline: HitRate - BaselineHitRate.
  Un valore negativo indica una combinazione più rischiosa della baseline.
- Support: numero di partite in cui tutti i segnali della combinazione sono
  contemporaneamente attivi.
===============================================================================
"""

from __future__ import annotations

import itertools
from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "analysis/laboratory/data/01_matches.csv"
)

OUTPUT_DIR = Path(
    "analysis/experiments/v252_signal_combinations"
)

VALID_OUTCOMES = {
    "OK",
    "KO",
}

SIGNALS = {
    "RankingGapHigh": (
        "RankingGapScore",
        lambda value: value >= 4.0,
    ),
    "HomePPGLow": (
        "HomePPGLast5",
        lambda value: value < 1.0,
    ),
    "WorstPPGLow": (
        "WorstPPGLast5",
        lambda value: value < 0.8,
    ),
    "HomeWinsLow": (
        "HomeWinsLast5",
        lambda value: value <= 1.0,
    ),
    "HomeRestartGFLow": (
        "HomeGFAvgSinceRestart",
        lambda value: value < 1.2,
    ),
    "HomeRestartNotReady": (
        "HomeRestartNotReady",
        lambda value: value >= 1.0,
    ),
    "BothTeamsRestartNotReady": (
        "BothTeamsRestartNotReady",
        lambda value: value >= 1.0,
    ),
}

MIN_SUPPORT_PAIRS = 10
MIN_SUPPORT_TRIPLES = 8


def safe_rate(
    ok: int,
    ko: int,
) -> float:
    total = ok + ko

    if total == 0:
        return 0.0

    return round(
        ok / total * 100.0,
        4,
    )


def prepare_signal_columns(
    matches: pd.DataFrame,
) -> pd.DataFrame:
    """
    Crea una colonna booleana per ciascun segnale.
    """

    prepared = matches.copy()

    for signal_name, (
        source_column,
        predicate,
    ) in SIGNALS.items():
        if source_column not in prepared.columns:
            prepared[signal_name] = False
            continue

        numeric_values = pd.to_numeric(
            prepared[source_column],
            errors="coerce",
        )

        prepared[signal_name] = (
            numeric_values
            .map(
                lambda value: (
                    False
                    if pd.isna(value)
                    else bool(predicate(float(value)))
                )
            )
        )

    return prepared


def build_baselines(
    matches: pd.DataFrame,
) -> dict[str, float]:
    """
    Calcola la percentuale OK complessiva e per fascia.
    """

    baselines = {
        "ALL": safe_rate(
            int(
                (
                    matches["Outcome"] == "OK"
                ).sum()
            ),
            int(
                (
                    matches["Outcome"] == "KO"
                ).sum()
            ),
        )
    }

    for band in sorted(
        matches["Band"]
        .dropna()
        .astype(str)
        .unique()
    ):
        band_rows = matches[
            matches["Band"] == band
        ]

        baselines[band] = safe_rate(
            int(
                (
                    band_rows["Outcome"] == "OK"
                ).sum()
            ),
            int(
                (
                    band_rows["Outcome"] == "KO"
                ).sum()
            ),
        )

    return baselines


def analyze_combination(
    matches: pd.DataFrame,
    combination: tuple[str, ...],
    combination_type: str,
    baselines: dict[str, float],
) -> list[dict]:
    """
    Analizza una combinazione sull'intero campione e separatamente per fascia.

    Una partita appartiene alla combinazione quando TUTTI i segnali indicati
    sono attivi. La presenza di ulteriori segnali non la esclude.
    """

    mask = pd.Series(
        True,
        index=matches.index,
    )

    for signal_name in combination:
        mask &= matches[
            signal_name
        ]

    selected = matches[
        mask
    ]

    result_rows = []

    scopes = [
        (
            "ALL",
            selected,
        )
    ]

    for band in sorted(
        matches["Band"]
        .dropna()
        .astype(str)
        .unique()
    ):
        scopes.append(
            (
                band,
                selected[
                    selected["Band"] == band
                ],
            )
        )

    for scope, scope_rows in scopes:
        ok = int(
            (
                scope_rows["Outcome"] == "OK"
            ).sum()
        )

        ko = int(
            (
                scope_rows["Outcome"] == "KO"
            ).sum()
        )

        support = ok + ko
        hit_rate = safe_rate(
            ok,
            ko,
        )

        baseline = baselines.get(
            scope,
            baselines["ALL"],
        )

        result_rows.append(
            {
                "CombinationType": combination_type,
                "Signals": " + ".join(
                    combination
                ),
                "Signal1": combination[0],
                "Signal2": combination[1],
                "Signal3": (
                    combination[2]
                    if len(combination) == 3
                    else ""
                ),
                "Scope": scope,
                "Support": support,
                "OK": ok,
                "KO": ko,
                "HitRate": hit_rate,
                "KORate": round(
                    100.0 - hit_rate,
                    4,
                ) if support else 0.0,
                "BaselineHitRate": baseline,
                "LiftVsBaseline": round(
                    hit_rate - baseline,
                    4,
                ),
            }
        )

    return result_rows


def build_match_details(
    matches: pd.DataFrame,
    combinations: list[
        tuple[str, ...]
    ],
) -> pd.DataFrame:
    """
    Produce il dettaglio delle partite associate a ciascuna combinazione.
    """

    detail_rows = []

    for combination in combinations:
        mask = pd.Series(
            True,
            index=matches.index,
        )

        for signal_name in combination:
            mask &= matches[
                signal_name
            ]

        selected = matches[
            mask
        ]

        for _, row in selected.iterrows():
            detail_rows.append(
                {
                    "CombinationType": (
                        "PAIR"
                        if len(combination) == 2
                        else "TRIPLE"
                    ),
                    "Signals": " + ".join(
                        combination
                    ),
                    "MatchId": row.get(
                        "MatchId",
                        "",
                    ),
                    "PredictionDate": row.get(
                        "PredictionDate",
                        "",
                    ),
                    "MatchDate": row.get(
                        "MatchDate",
                        "",
                    ),
                    "LeagueId": row.get(
                        "LeagueId",
                        "",
                    ),
                    "Home": row.get(
                        "Home",
                        "",
                    ),
                    "Away": row.get(
                        "Away",
                        "",
                    ),
                    "Band": row.get(
                        "Band",
                        "",
                    ),
                    "Score": row.get(
                        "Score",
                        "",
                    ),
                    "Outcome": row.get(
                        "Outcome",
                        "",
                    ),
                }
            )

    return pd.DataFrame(
        detail_rows
    )


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File Laboratory non trovato: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    matches = pd.read_csv(
        INPUT_FILE,
        sep=";",
        encoding="utf-8-sig",
        low_memory=False,
    )

    required = {
        "MatchId",
        "Band",
        "Outcome",
        "LeagueId",
        "Home",
        "Away",
    }

    missing = (
        required
        - set(matches.columns)
    )

    if missing:
        raise ValueError(
            "01_matches.csv non contiene: "
            + ", ".join(
                sorted(missing)
            )
        )

    matches = matches[
        matches["Outcome"]
        .astype(str)
        .str.upper()
        .isin(VALID_OUTCOMES)
    ].copy()

    matches["Outcome"] = (
        matches["Outcome"]
        .astype(str)
        .str.upper()
    )

    matches["Band"] = (
        matches["Band"]
        .astype(str)
        .str.upper()
    )

    matches = prepare_signal_columns(
        matches
    )

    baselines = build_baselines(
        matches
    )

    signal_names = list(
        SIGNALS
    )

    pairs = list(
        itertools.combinations(
            signal_names,
            2,
        )
    )

    triples = list(
        itertools.combinations(
            signal_names,
            3,
        )
    )

    result_rows = []

    for combination in pairs:
        result_rows.extend(
            analyze_combination(
                matches,
                combination,
                "PAIR",
                baselines,
            )
        )

    for combination in triples:
        result_rows.extend(
            analyze_combination(
                matches,
                combination,
                "TRIPLE",
                baselines,
            )
        )

    results = pd.DataFrame(
        result_rows
    )

    pairs_df = results[
        results["CombinationType"]
        == "PAIR"
    ].copy()

    triples_df = results[
        results["CombinationType"]
        == "TRIPLE"
    ].copy()

    pairs_df.to_csv(
        OUTPUT_DIR
        / "01_pair_results.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    triples_df.to_csv(
        OUTPUT_DIR
        / "02_triple_results.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    results.to_csv(
        OUTPUT_DIR
        / "03_all_combinations.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    eligible_pairs = pairs_df[
        (
            (
                pairs_df["Scope"] == "ALTA"
            )
            & (
                pairs_df["Support"]
                >= MIN_SUPPORT_PAIRS
            )
        )
    ]

    eligible_triples = triples_df[
        (
            (
                triples_df["Scope"] == "ALTA"
            )
            & (
                triples_df["Support"]
                >= MIN_SUPPORT_TRIPLES
            )
        )
    ]

    best_risk = pd.concat(
        [
            eligible_pairs,
            eligible_triples,
        ],
        ignore_index=True,
    )

    best_risk = best_risk.sort_values(
        by=[
            "LiftVsBaseline",
            "Support",
            "KORate",
        ],
        ascending=[
            True,
            False,
            False,
        ],
    )

    best_risk.to_csv(
        OUTPUT_DIR
        / "04_best_risk_combinations.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    details = build_match_details(
        matches,
        pairs + triples,
    )

    details.to_csv(
        OUTPUT_DIR
        / "05_match_details.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"Partite concluse analizzate: {len(matches)}"
    )

    print(
        f"Coppie analizzate: {len(pairs)}"
    )

    print(
        f"Triple analizzate: {len(triples)}"
    )

    print(
        f"Output: {OUTPUT_DIR}"
    )

    print()

    columns = [
        "CombinationType",
        "Signals",
        "Support",
        "OK",
        "KO",
        "HitRate",
        "BaselineHitRate",
        "LiftVsBaseline",
    ]

    if best_risk.empty:
        print(
            "Nessuna combinazione supera "
            "le soglie minime di campione."
        )
    else:
        print(
            best_risk[
                columns
            ]
            .head(15)
            .to_string(
                index=False
            )
        )


if __name__ == "__main__":
    main()
