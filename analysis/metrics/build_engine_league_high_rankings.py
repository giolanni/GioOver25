"""
===============================================================================
GioOver2.5 - Classifica leghe per risultati in fascia ALTA
===============================================================================

SCOPO
-----
Mantenere una classifica aggiornata delle leghe che hanno prodotto più esiti
OK in fascia ALTA, separatamente per ciascun engine.

Lo script legge gli storici ranking di tutti gli engine presenti in:

    data/storico/ranking/<engine>/storico_ranking_<engine>.csv

Per ogni lega calcola:

- OK in fascia ALTA;
- KO in fascia ALTA;
- totale concluso;
- percentuale OK;
- data della prima e dell'ultima partita conclusa;
- posizione nella classifica dell'engine.

OUTPUT
------
data/debug/league_high_rankings/

    <engine>/league_high_ranking.csv
    all_engines_league_high_ranking.csv

ORDINAMENTO
-----------
1. numero di OK decrescente;
2. percentuale OK decrescente;
3. totale partite decrescente;
4. LeagueId alfabetico.

USO
---
python -m analysis.metrics.build_engine_league_high_rankings
===============================================================================
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


RANKING_ROOT = Path(
    "data/storico/ranking"
)

OUTPUT_ROOT = Path(
    "data/debug/league_high_rankings"
)

VALID_OUTCOMES = {
    "OK",
    "KO",
}


def find_engine_histories() -> list[
    tuple[str, Path]
]:
    """
    Trova tutti gli storici ranking disponibili sul disco.
    """

    histories = []

    if not RANKING_ROOT.exists():
        return histories

    for engine_dir in sorted(
        RANKING_ROOT.iterdir()
    ):
        if not engine_dir.is_dir():
            continue

        engine_name = engine_dir.name

        history_file = (
            engine_dir
            / f"storico_ranking_{engine_name}.csv"
        )

        if history_file.exists():
            histories.append(
                (
                    engine_name,
                    history_file,
                )
            )

    return histories


def detect_delimiter(
    path: Path,
) -> str:
    """
    Rileva il separatore, con fallback al punto e virgola.
    """

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


def build_engine_ranking(
    engine_name: str,
    history_file: Path,
) -> pd.DataFrame:
    """
    Costruisce la classifica delle leghe di un singolo engine.
    """

    delimiter = detect_delimiter(
        history_file
    )

    history = pd.read_csv(
        history_file,
        sep=delimiter,
        encoding="utf-8-sig",
        low_memory=False,
        dtype=str,
    )

    required = {
        "LeagueId",
        "Band",
        "Over25",
    }

    missing = (
        required
        - set(history.columns)
    )

    if missing:
        print(
            f"[WARN] {engine_name}: "
            "colonne mancanti: "
            + ", ".join(
                sorted(missing)
            )
        )

        return pd.DataFrame()

    history["LeagueId"] = (
        history["LeagueId"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    history["Band"] = (
        history["Band"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    history["Over25"] = (
        history["Over25"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    alta = history[
        (
            history["Band"] == "ALTA"
        )
        & (
            history["Over25"].isin(
                VALID_OUTCOMES
            )
        )
        & (
            history["LeagueId"] != ""
        )
    ].copy()

    if alta.empty:
        return pd.DataFrame(
            columns=[
                "Rank",
                "Engine",
                "LeagueId",
                "OK",
                "KO",
                "Total",
                "HitRate",
                "FirstMatchDate",
                "LastMatchDate",
            ]
        )

    date_column = (
        "MatchDate"
        if "MatchDate" in alta.columns
        else (
            "PredictionDate"
            if "PredictionDate" in alta.columns
            else None
        )
    )

    if date_column is not None:
        alta["_ResolvedDate"] = pd.to_datetime(
            alta[date_column],
            errors="coerce",
        )
    else:
        alta["_ResolvedDate"] = pd.NaT

    grouped = (
        alta.groupby(
            "LeagueId",
            dropna=False,
        )
        .agg(
            OK=(
                "Over25",
                lambda values: int(
                    (
                        values == "OK"
                    ).sum()
                ),
            ),
            KO=(
                "Over25",
                lambda values: int(
                    (
                        values == "KO"
                    ).sum()
                ),
            ),
            FirstMatchDate=(
                "_ResolvedDate",
                "min",
            ),
            LastMatchDate=(
                "_ResolvedDate",
                "max",
            ),
        )
        .reset_index()
    )

    grouped["Total"] = (
        grouped["OK"]
        + grouped["KO"]
    )

    grouped["HitRate"] = (
        grouped["OK"]
        / grouped["Total"]
        * 100.0
    ).round(2)

    grouped.insert(
        0,
        "Engine",
        engine_name,
    )

    grouped = grouped.sort_values(
        by=[
            "OK",
            "HitRate",
            "Total",
            "LeagueId",
        ],
        ascending=[
            False,
            False,
            False,
            True,
        ],
    ).reset_index(
        drop=True
    )

    grouped.insert(
        0,
        "Rank",
        range(
            1,
            len(grouped) + 1,
        ),
    )

    for column in (
        "FirstMatchDate",
        "LastMatchDate",
    ):
        grouped[column] = (
            grouped[column]
            .dt.strftime("%Y-%m-%d")
            .fillna("")
        )

    return grouped


def main() -> None:
    """
    Rigenera tutte le classifiche.
    """

    histories = find_engine_histories()

    if not histories:
        print(
            "Nessuno storico ranking trovato."
        )
        return

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    all_rankings = []

    for engine_name, history_file in histories:
        ranking = build_engine_ranking(
            engine_name,
            history_file,
        )

        engine_output_dir = (
            OUTPUT_ROOT
            / engine_name
        )

        engine_output_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            engine_output_dir
            / "league_high_ranking.csv"
        )

        ranking.to_csv(
            output_file,
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )

        if not ranking.empty:
            all_rankings.append(
                ranking
            )

        print(
            f"[{engine_name}] "
            f"Leghe classificate: {len(ranking)} | "
            f"Output: {output_file}"
        )

    combined = (
        pd.concat(
            all_rankings,
            ignore_index=True,
        )
        if all_rankings
        else pd.DataFrame()
    )

    combined_file = (
        OUTPUT_ROOT
        / "all_engines_league_high_ranking.csv"
    )

    combined.to_csv(
        combined_file,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        "Classifica combinata aggiornata: "
        f"{combined_file}"
    )


if __name__ == "__main__":
    main()
