"""
===============================================================================
GioOver2.5 - v201dev validation experiment
===============================================================================

OBIETTIVO
---------
Validare nel tempo TRE regole CONGELATE emerse dall'experiment precedente,
senza cercare nuove combinazioni.

REGOLE TESTATE
--------------

A) V201DEV_ORIGINAL
   v20 Band = MEDIA-ALTA
   v20 Score >= 71
   v22 Band = ALTA
   v25 Band = ALTA

B) V201DEV_NARROW_71_73
   v20 Band = MEDIA-ALTA
   71 <= v20 Score < 73
   v22 Band = ALTA
   v25 Band = ALTA

C) CONSENSUS_ALTA_NO_AUSTRALIA
   v20 Band = ALTA
   v22 Band = ALTA
   v25 Band = ALTA
   LeagueId NON inizia con Australia_

PRINCIPIO DEL PROGETTO
-----------------------
La priorità è massimizzare la percentuale OK.
La numerosità serve soltanto a giudicare la robustezza.

INPUT
-----
Usa direttamente:

    analysis/experiments/v201dev_extension/07_common_matches.csv

Questo evita di rifare il matching v20/v22/v25 e garantisce che il secondo
experiment lavori ESATTAMENTE sul dataset comune prodotto dal primo.

OUTPUT
------
analysis/experiments/v201dev_validation/

01_overall.csv
    Prestazione complessiva delle tre regole.

02_monthly.csv
    Prestazione mese per mese.

03_chronological_split.csv
    Validazione cronologica:
        TRAIN = prima parte del campione
        TEST  = parte finale del campione

04_rolling_periods.csv
    Prestazione su finestre temporali progressive/recenti.

05_rule_matches.csv
    Tutte le singole partite selezionate dalle tre regole.

06_overlap.csv
    Sovrapposizione tra le regole:
        A only
        B only
        C only
        A+B
        A+C
        B+C
        A+B+C

PARAMETRI MODIFICABILI
----------------------

TRAIN_RATIO = 0.70
    70% delle date iniziali = TRAIN
    30% finali = TEST

ROLLING_DAYS = (30, 60, 90)
    Finestre recenti usate in 04_rolling_periods.csv

MIN_MONTH_SAMPLE = 1
    Lasciato volutamente basso: non filtra i mesi piccoli, perché anche
    i piccoli campioni devono restare visibili.

ESECUZIONE
----------
python -m analysis.experiments.v201dev_validation_experiment

Lo script NON modifica alcun engine.
===============================================================================
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd


INPUT_FILE = Path(
    "analysis/experiments/v201dev_extension/07_common_matches.csv"
)

OUTPUT_DIR = Path(
    "analysis/experiments/v201dev_validation"
)

TRAIN_RATIO = 0.70
ROLLING_DAYS = (30, 60, 90)
MIN_MONTH_SAMPLE = 1


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko

    if total == 0:
        return 0.0

    return round(
        ok / total * 100.0,
        4,
    )


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


def load_common() -> pd.DataFrame:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File non trovato: {INPUT_FILE}\n"
            "Esegui prima v201dev_extension_experiment."
        )

    df = pd.read_csv(
        INPUT_FILE,
        sep=";",
        encoding="utf-8-sig",
        low_memory=False,
    )

    required = {
        "LeagueId",
        "MatchDate",
        "Home",
        "Away",
        "Band_v20",
        "Score_v20",
        "Band_v22",
        "Band_v25",
        "Outcome",
    }

    missing = (
        required
        - set(df.columns)
    )

    if missing:
        raise ValueError(
            "Colonne mancanti: "
            + ", ".join(
                sorted(missing)
            )
        )

    df = df.copy()

    df["Score_v20"] = pd.to_numeric(
        df["Score_v20"],
        errors="coerce",
    )

    df["MatchDateParsed"] = pd.to_datetime(
        df["MatchDate"],
        errors="coerce",
    )

    df["Band_v20"] = (
        df["Band_v20"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["Band_v22"] = (
        df["Band_v22"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["Band_v25"] = (
        df["Band_v25"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["Outcome"] = (
        df["Outcome"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df = df[
        df["Outcome"].isin(
            {
                "OK",
                "KO",
            }
        )
    ].copy()

    return df


def apply_rules(
    df: pd.DataFrame,
) -> dict[str, pd.DataFrame]:
    rule_a = df[
        (df["Band_v20"] == "MEDIA-ALTA")
        & (df["Score_v20"] >= 71)
        & (df["Band_v22"] == "ALTA")
        & (df["Band_v25"] == "ALTA")
    ].copy()

    rule_b = df[
        (df["Band_v20"] == "MEDIA-ALTA")
        & (df["Score_v20"] >= 71)
        & (df["Score_v20"] < 73)
        & (df["Band_v22"] == "ALTA")
        & (df["Band_v25"] == "ALTA")
    ].copy()

    rule_c = df[
        (df["Band_v20"] == "ALTA")
        & (df["Band_v22"] == "ALTA")
        & (df["Band_v25"] == "ALTA")
        & (
            ~df["LeagueId"]
            .fillna("")
            .astype(str)
            .str.startswith(
                "Australia_"
            )
        )
    ].copy()

    return {
        "A_V201DEV_ORIGINAL": rule_a,
        "B_V201DEV_NARROW_71_73": rule_b,
        "C_CONSENSUS_ALTA_NO_AUSTRALIA": rule_c,
    }


def overall_report(
    rules: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []

    for name, frame in rules.items():
        row = {
            "Rule": name,
        }

        row.update(
            stats(frame)
        )

        rows.append(row)

    return (
        pd.DataFrame(rows)
        .sort_values(
            by=[
                "HitRate",
                "KO",
                "Total",
            ],
            ascending=[
                False,
                True,
                False,
            ],
        )
        .reset_index(
            drop=True
        )
    )


def monthly_report(
    rules: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []

    for name, frame in rules.items():
        dated = frame[
            frame[
                "MatchDateParsed"
            ].notna()
        ].copy()

        if dated.empty:
            continue

        dated["Month"] = (
            dated[
                "MatchDateParsed"
            ]
            .dt.to_period("M")
            .astype(str)
        )

        for month, group in dated.groupby(
            "Month"
        ):
            if len(group) < MIN_MONTH_SAMPLE:
                continue

            row = {
                "Rule": name,
                "Month": month,
            }

            row.update(
                stats(group)
            )

            rows.append(row)

    result = pd.DataFrame(rows)

    if not result.empty:
        result = result.sort_values(
            by=[
                "Month",
                "HitRate",
                "KO",
                "Total",
            ],
            ascending=[
                True,
                False,
                True,
                False,
            ],
        )

    return result


def chronological_split_report(
    df: pd.DataFrame,
) -> pd.DataFrame:
    dated = df[
        df["MatchDateParsed"].notna()
    ].copy()

    if dated.empty:
        return pd.DataFrame()

    unique_dates = sorted(
        dated[
            "MatchDateParsed"
        ]
        .dt.normalize()
        .unique()
    )

    if len(unique_dates) < 2:
        return pd.DataFrame()

    split_index = int(
        len(unique_dates)
        * TRAIN_RATIO
    )

    split_index = max(
        1,
        min(
            split_index,
            len(unique_dates) - 1,
        ),
    )

    split_date = pd.Timestamp(
        unique_dates[
            split_index
        ]
    )

    train = dated[
        dated[
            "MatchDateParsed"
        ] < split_date
    ].copy()

    test = dated[
        dated[
            "MatchDateParsed"
        ] >= split_date
    ].copy()

    rows = []

    for split_name, split_df in (
        (
            "TRAIN",
            train,
        ),
        (
            "TEST",
            test,
        ),
    ):
        rules = apply_rules(
            split_df
        )

        for name, frame in rules.items():
            row = {
                "Split": split_name,
                "SplitDate": (
                    split_date.date()
                    .isoformat()
                ),
                "Rule": name,
                "StartDate": (
                    frame[
                        "MatchDateParsed"
                    ]
                    .min()
                    .date()
                    .isoformat()
                    if not frame.empty
                    else ""
                ),
                "EndDate": (
                    frame[
                        "MatchDateParsed"
                    ]
                    .max()
                    .date()
                    .isoformat()
                    if not frame.empty
                    else ""
                ),
            }

            row.update(
                stats(frame)
            )

            rows.append(row)

    return pd.DataFrame(
        rows
    )


def rolling_report(
    df: pd.DataFrame,
) -> pd.DataFrame:
    dated = df[
        df["MatchDateParsed"].notna()
    ].copy()

    if dated.empty:
        return pd.DataFrame()

    max_date = (
        dated[
            "MatchDateParsed"
        ]
        .max()
        .normalize()
    )

    rows = []

    for days in ROLLING_DAYS:
        start_date = (
            max_date
            - pd.Timedelta(
                days=days - 1
            )
        )

        window = dated[
            dated[
                "MatchDateParsed"
            ].dt.normalize()
            >= start_date
        ].copy()

        rules = apply_rules(
            window
        )

        for name, frame in rules.items():
            row = {
                "WindowDays": days,
                "WindowStart": (
                    start_date.date()
                    .isoformat()
                ),
                "WindowEnd": (
                    max_date.date()
                    .isoformat()
                ),
                "Rule": name,
            }

            row.update(
                stats(frame)
            )

            rows.append(row)

    return pd.DataFrame(
        rows
    )


def rule_matches_report(
    rules: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    frames = []

    wanted = [
        "LeagueId",
        "MatchDate",
        "Home",
        "Away",
        "Band_v20",
        "Score_v20",
        "Band_v22",
        "Band_v25",
        "Outcome",
    ]

    for name, frame in rules.items():
        temp = frame.copy()

        temp.insert(
            0,
            "Rule",
            name,
        )

        columns = [
            "Rule",
            *[
                column
                for column in wanted
                if column
                in temp.columns
            ],
        ]

        frames.append(
            temp[
                columns
            ]
        )

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
        ignore_index=True,
    )


def overlap_report(
    df: pd.DataFrame,
) -> pd.DataFrame:
    temp = df.copy()

    temp["A"] = (
        (temp["Band_v20"] == "MEDIA-ALTA")
        & (temp["Score_v20"] >= 71)
        & (temp["Band_v22"] == "ALTA")
        & (temp["Band_v25"] == "ALTA")
    )

    temp["B"] = (
        (temp["Band_v20"] == "MEDIA-ALTA")
        & (temp["Score_v20"] >= 71)
        & (temp["Score_v20"] < 73)
        & (temp["Band_v22"] == "ALTA")
        & (temp["Band_v25"] == "ALTA")
    )

    temp["C"] = (
        (temp["Band_v20"] == "ALTA")
        & (temp["Band_v22"] == "ALTA")
        & (temp["Band_v25"] == "ALTA")
        & (
            ~temp["LeagueId"]
            .fillna("")
            .astype(str)
            .str.startswith(
                "Australia_"
            )
        )
    )

    def label(row) -> str:
        active = [
            name
            for name in (
                "A",
                "B",
                "C",
            )
            if bool(
                row[name]
            )
        ]

        return (
            "+".join(active)
            if active
            else "NONE"
        )

    temp["Overlap"] = temp.apply(
        label,
        axis=1,
    )

    rows = []

    for overlap, group in temp.groupby(
        "Overlap"
    ):
        if overlap == "NONE":
            continue

        row = {
            "Overlap": overlap,
        }

        row.update(
            stats(group)
        )

        rows.append(row)

    result = pd.DataFrame(rows)

    if not result.empty:
        result = result.sort_values(
            by=[
                "HitRate",
                "KO",
                "Total",
            ],
            ascending=[
                False,
                True,
                False,
            ],
        )

    return result


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    common = load_common()

    rules = apply_rules(
        common
    )

    overall = overall_report(
        rules
    )

    monthly = monthly_report(
        rules
    )

    chrono = (
        chronological_split_report(
            common
        )
    )

    rolling = rolling_report(
        common
    )

    matches = rule_matches_report(
        rules
    )

    overlap = overlap_report(
        common
    )

    overall.to_csv(
        OUTPUT_DIR
        / "01_overall.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    monthly.to_csv(
        OUTPUT_DIR
        / "02_monthly.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    chrono.to_csv(
        OUTPUT_DIR
        / "03_chronological_split.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    rolling.to_csv(
        OUTPUT_DIR
        / "04_rolling_periods.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    matches.to_csv(
        OUTPUT_DIR
        / "05_rule_matches.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    overlap.to_csv(
        OUTPUT_DIR
        / "06_overlap.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        "=== V201DEV VALIDATION ==="
    )
    print(
        f"Partite comuni caricate: "
        f"{len(common)}"
    )
    print()
    print(
        "OVERALL:"
    )
    print(
        overall.to_string(
            index=False
        )
    )
    print()
    print(
        f"Output: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
