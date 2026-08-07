"""
GioOver2.5 - Experiment severità v20 -> v25

Obiettivo:
partire dalle ALTA di v25 nel set comune v20/v25 e testare filtri più severi,
ispirati ai driver principali usati da v20.

Output:
analysis/experiments/v20_v25_severity/
    01_baseline.csv
    02_configurations.csv
    03_best_tradeoffs.csv
    04_match_details.csv

Uso:
python -m analysis.experiments.v20_v25_severity
"""

from __future__ import annotations

import csv
import itertools
from pathlib import Path

import pandas as pd


V20_FILE = Path("data/storico/ranking/v20/storico_ranking_v20.csv")
V25_FILE = Path("data/storico/ranking/v25/storico_ranking_v25.csv")
OUTPUT_DIR = Path("analysis/experiments/v20_v25_severity")

VALID_OUTCOMES = {"OK", "KO"}

HOME_ATTACK_THRESHOLDS = (6.5, 7.5, 8.5, 9.5, 10.5)
AWAY_DEFENSE_THRESHOLDS = (5.0, 6.0, 7.0, 8.0, 9.0)
HOME_LAST10_THRESHOLDS = (6.0, 7.2, 8.4, 9.6)
AWAY_LAST10_THRESHOLDS = (6.0, 7.2, 8.4, 9.6)
MIN_STRONG_COUNTS = (2, 3, 4)


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


def read_history(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=detect_delimiter(path),
        encoding="utf-8-sig",
        low_memory=False,
    )


def normalize_text(value) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .casefold()
        .split()
    )


def prepare_history(df: pd.DataFrame, engine: str) -> pd.DataFrame:
    required = {"Home", "Away", "Band", "Over25"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"{engine}: colonne mancanti: "
            + ", ".join(sorted(missing))
        )

    out = df.copy()
    out["Engine"] = engine
    out["Outcome"] = (
        out["Over25"]
        .astype(str)
        .str.strip()
        .str.upper()
    )
    out["Band"] = (
        out["Band"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    out = out[
        out["Outcome"].isin(VALID_OUTCOMES)
    ].copy()

    out["_HomeKey"] = out["Home"].map(normalize_text)
    out["_AwayKey"] = out["Away"].map(normalize_text)
    out["_PairKey"] = out["_HomeKey"] + "||" + out["_AwayKey"]

    # Mantiene occorrenze duplicate della stessa coppia Home/Away.
    out["_Occurrence"] = out.groupby("_PairKey").cumcount()
    out["_MatchKey"] = (
        out["_PairKey"]
        + "||"
        + out["_Occurrence"].astype(str)
    )

    return out


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(
        series,
        errors="coerce",
    ).fillna(0.0)


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko
    if total == 0:
        return 0.0
    return round(ok / total * 100.0, 4)


def build_common_set() -> pd.DataFrame:
    v20 = prepare_history(
        read_history(V20_FILE),
        "v20",
    )
    v25 = prepare_history(
        read_history(V25_FILE),
        "v25",
    )

    common_keys = set(v20["_MatchKey"]) & set(v25["_MatchKey"])

    v20_common = (
        v20[v20["_MatchKey"].isin(common_keys)]
        .copy()
        .set_index("_MatchKey")
    )

    v25_common = (
        v25[v25["_MatchKey"].isin(common_keys)]
        .copy()
        .set_index("_MatchKey")
    )

    common = v25_common.copy()
    common["V20Band"] = v20_common["Band"]
    common["V20Outcome"] = v20_common["Outcome"]

    # Mantiene solo righe con esito coerente nei due storici.
    common = common[
        common["Outcome"] == common["V20Outcome"]
    ].copy()

    common.reset_index(inplace=True)
    return common


def evaluate_mask(
    alta_rows: pd.DataFrame,
    mask: pd.Series,
    config: dict,
) -> dict:
    selected = alta_rows[mask]

    original_ok = int((alta_rows["Outcome"] == "OK").sum())
    original_ko = int((alta_rows["Outcome"] == "KO").sum())
    selected_ok = int((selected["Outcome"] == "OK").sum())
    selected_ko = int((selected["Outcome"] == "KO").sum())

    original_total = original_ok + original_ko
    selected_total = selected_ok + selected_ko

    ok_sacrificed = original_ok - selected_ok
    ko_eliminated = original_ko - selected_ko

    result = {
        **config,
        "Original_OK": original_ok,
        "Original_KO": original_ko,
        "Original_Total": original_total,
        "Original_HitRate": safe_rate(original_ok, original_ko),
        "Selected_OK": selected_ok,
        "Selected_KO": selected_ko,
        "Selected_Total": selected_total,
        "Selected_HitRate": safe_rate(selected_ok, selected_ko),
        "OK_Sacrificed": ok_sacrificed,
        "KO_Eliminated": ko_eliminated,
        "CoveragePct": round(
            selected_total / original_total * 100.0
            if original_total
            else 0.0,
            4,
        ),
        "PurityGain": round(
            safe_rate(selected_ok, selected_ko)
            - safe_rate(original_ok, original_ko),
            4,
        ),
        "NetRescue": ko_eliminated - ok_sacrificed,
        "KO_per_OK_Sacrificed": (
            round(ko_eliminated / ok_sacrificed, 4)
            if ok_sacrificed > 0
            else (999.0 if ko_eliminated > 0 else 0.0)
        ),
    }

    return result


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    common = build_common_set()

    alta_v25 = common[
        common["Band"] == "ALTA"
    ].copy()

    if alta_v25.empty:
        raise RuntimeError("Nessuna ALTA v25 nel set comune.")

    required_driver_columns = [
        "HomeAttackScore",
        "AwayDefenseWeaknessScore",
        "HomeLast10OverScore",
        "AwayLast10OverScore",
    ]

    for column in required_driver_columns:
        if column not in alta_v25.columns:
            raise ValueError(
                f"Colonna mancante nello storico v25: {column}"
            )
        alta_v25[column] = numeric(alta_v25[column])

    baseline_ok = int((alta_v25["Outcome"] == "OK").sum())
    baseline_ko = int((alta_v25["Outcome"] == "KO").sum())

    baseline = pd.DataFrame(
        [{
            "CommonFinishedMatches": len(common),
            "V25_ALTA_OK": baseline_ok,
            "V25_ALTA_KO": baseline_ko,
            "V25_ALTA_Total": baseline_ok + baseline_ko,
            "V25_ALTA_HitRate": safe_rate(
                baseline_ok,
                baseline_ko,
            ),
            "V20_ALTA_in_Common": int(
                (common["V20Band"] == "ALTA").sum()
            ),
        }]
    )

    baseline.to_csv(
        OUTPUT_DIR / "01_baseline.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    configurations = []

    single_configs = [
        ("HOME_ATTACK", "HomeAttackScore", HOME_ATTACK_THRESHOLDS),
        ("AWAY_DEFENSE", "AwayDefenseWeaknessScore", AWAY_DEFENSE_THRESHOLDS),
        ("HOME_LAST10", "HomeLast10OverScore", HOME_LAST10_THRESHOLDS),
        ("AWAY_LAST10", "AwayLast10OverScore", AWAY_LAST10_THRESHOLDS),
    ]

    for label, column, thresholds in single_configs:
        for threshold in thresholds:
            mask = alta_v25[column] >= threshold
            configurations.append(
                evaluate_mask(
                    alta_v25,
                    mask,
                    {
                        "ConfigType": "SINGLE",
                        "ConfigName": f"{label}>={threshold}",
                    },
                )
            )

    pair_specs = [
        ("HomeAttackScore", HOME_ATTACK_THRESHOLDS),
        ("AwayDefenseWeaknessScore", AWAY_DEFENSE_THRESHOLDS),
        ("HomeLast10OverScore", HOME_LAST10_THRESHOLDS),
        ("AwayLast10OverScore", AWAY_LAST10_THRESHOLDS),
    ]

    for (col1, thresholds1), (col2, thresholds2) in itertools.combinations(
        pair_specs,
        2,
    ):
        for threshold1 in thresholds1:
            for threshold2 in thresholds2:
                mask = (
                    (alta_v25[col1] >= threshold1)
                    & (alta_v25[col2] >= threshold2)
                )
                configurations.append(
                    evaluate_mask(
                        alta_v25,
                        mask,
                        {
                            "ConfigType": "PAIR_AND",
                            "ConfigName": (
                                f"{col1}>={threshold1} AND "
                                f"{col2}>={threshold2}"
                            ),
                        },
                    )
                )

    strong_flags = pd.DataFrame(
        {
            "HomeAttackStrong": alta_v25["HomeAttackScore"] >= 8.5,
            "AwayDefenseStrong": alta_v25["AwayDefenseWeaknessScore"] >= 7.0,
            "HomeLast10Strong": alta_v25["HomeLast10OverScore"] >= 7.2,
            "AwayLast10Strong": alta_v25["AwayLast10OverScore"] >= 7.2,
        },
        index=alta_v25.index,
    )

    strong_count = strong_flags.sum(axis=1)

    for min_count in MIN_STRONG_COUNTS:
        configurations.append(
            evaluate_mask(
                alta_v25,
                strong_count >= min_count,
                {
                    "ConfigType": "STRONG_COUNT",
                    "ConfigName": f"StrongDrivers>={min_count}",
                },
            )
        )

    configurations_df = pd.DataFrame(configurations)

    configurations_df = configurations_df[
        configurations_df["Selected_Total"] > 0
    ].copy()

    configurations_df.to_csv(
        OUTPUT_DIR / "02_configurations.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    eligible = configurations_df[
        configurations_df["CoveragePct"] >= 20.0
    ].copy()

    eligible["RescueRatio"] = (
        eligible["KO_Eliminated"]
        / (eligible["OK_Sacrificed"] + 1)
    ).round(4)

    best_rescue = (
        eligible.sort_values(
            by=[
                "KO_Eliminated",
                "OK_Sacrificed",
                "Selected_HitRate",
                "CoveragePct",
            ],
            ascending=[False, True, False, False],
        )
        .head(30)
        .copy()
    )
    best_rescue.insert(0, "RankingType", "KO_RESCUE")

    best_efficiency = (
        eligible.sort_values(
            by=[
                "RescueRatio",
                "KO_Eliminated",
                "Selected_HitRate",
                "CoveragePct",
            ],
            ascending=[False, False, False, False],
        )
        .head(30)
        .copy()
    )
    best_efficiency.insert(0, "RankingType", "EFFICIENCY")

    high_coverage = eligible[
        eligible["CoveragePct"] >= 50.0
    ].copy()

    best_purity = (
        high_coverage.sort_values(
            by=[
                "Selected_HitRate",
                "KO_Eliminated",
                "Selected_OK",
            ],
            ascending=[False, False, False],
        )
        .head(30)
        .copy()
    )
    best_purity.insert(0, "RankingType", "PURITY_50PLUS")

    best_tradeoffs = pd.concat(
        [best_rescue, best_efficiency, best_purity],
        ignore_index=True,
    )

    best_tradeoffs.to_csv(
        OUTPUT_DIR / "03_best_tradeoffs.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    detail_columns = [
        column
        for column in [
            "PredictionDate",
            "MatchDate",
            "LeagueId",
            "Home",
            "Away",
            "Score",
            "Band",
            "V20Band",
            "Outcome",
            "HomeAttackScore",
            "AwayDefenseWeaknessScore",
            "HomeLast10OverScore",
            "AwayLast10OverScore",
            "Reason",
        ]
        if column in alta_v25.columns
    ]

    alta_v25[detail_columns].to_csv(
        OUTPUT_DIR / "04_match_details.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"Partite concluse comuni v20/v25: {len(common)}"
    )
    print(
        f"ALTA v25 nel set comune: {len(alta_v25)}"
    )
    print(
        f"Baseline v25: {baseline_ok} OK / {baseline_ko} KO / "
        f"{safe_rate(baseline_ok, baseline_ko):.2f}%"
    )
    print(
        f"Configurazioni testate: {len(configurations_df)}"
    )
    print(f"Output: {OUTPUT_DIR}")
    print()

    display_columns = [
        "ConfigType",
        "ConfigName",
        "Selected_OK",
        "Selected_KO",
        "Selected_Total",
        "Selected_HitRate",
        "OK_Sacrificed",
        "KO_Eliminated",
        "CoveragePct",
    ]

    print(
        best_purity[
            display_columns
        ]
        .head(10)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
