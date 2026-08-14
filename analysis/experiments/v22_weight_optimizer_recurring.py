"""
GioOver2.5 - V22 Weight Optimizer Recurring

Scopo:
ripesare i 10 driver dello scoring v22 e ripetere lo stesso test nel tempo,
riusando sempre le stesse configurazioni candidate.

Base v22:
RankingGap 6
HomeAttack 13
AwayAttack 13
HomeDefenseWeakness 8
AwayDefenseWeakness 10
HomeLast10Over 12
AwayLast10Over 12
HomeVenueOver 10
AwayVenueOver 10
BTTSProfile 12
Totale = 106

Principio:
1) massimizzare % OK in ALTA
2) minimizzare KO
3) numerosità solo come misura di robustezza

Output:
analysis/experiments/v22_weight_optimizer/
  configurations.csv
  latest/
  snapshots/YYYYMMDD_HHMMSS/
  runs_history.csv

Uso:
python -m analysis.experiments.v22_weight_optimizer_recurring
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


HISTORY_CANDIDATES = (
    Path("data/storico/ranking/v22/storico_ranking_v22.csv"),
    Path("data/storico/ranking/storico_ranking_v22.csv"),
)

OUTPUT_ROOT = Path("analysis/experiments/v22_weight_optimizer")
CONFIG_FILE = OUTPUT_ROOT / "configurations.csv"
LATEST_DIR = OUTPUT_ROOT / "latest"
RUNS_HISTORY_FILE = OUTPUT_ROOT / "runs_history.csv"

ALTA_THRESHOLD = 75.0
N_LOCAL_CONFIGS = 3000
N_GLOBAL_CONFIGS = 2000
TRAIN_RATIO = 0.70
TOP_TO_STORE = 50
MIN_TEST_SAMPLE_FOR_STABLE = 20
RANDOM_SEED = 20260815

DRIVERS = (
    "RankingGap",
    "HomeAttack",
    "AwayAttack",
    "HomeDefenseWeakness",
    "AwayDefenseWeakness",
    "HomeLast10Over",
    "AwayLast10Over",
    "HomeVenueOver",
    "AwayVenueOver",
    "BTTSProfile",
)

BASE_WEIGHTS = {
    "RankingGap": 6.0,
    "HomeAttack": 13.0,
    "AwayAttack": 13.0,
    "HomeDefenseWeakness": 8.0,
    "AwayDefenseWeakness": 10.0,
    "HomeLast10Over": 12.0,
    "AwayLast10Over": 12.0,
    "HomeVenueOver": 10.0,
    "AwayVenueOver": 10.0,
    "BTTSProfile": 12.0,
}

SCORE_COLUMNS = {
    "RankingGap": "RankingGapScore",
    "HomeAttack": "HomeAttackScore",
    "AwayAttack": "AwayAttackScore",
    "HomeDefenseWeakness": "HomeDefenseWeaknessScore",
    "AwayDefenseWeakness": "AwayDefenseWeaknessScore",
    "HomeLast10Over": "HomeLast10OverScore",
    "AwayLast10Over": "AwayLast10OverScore",
    "HomeVenueOver": "HomeVenueOverScore",
    "AwayVenueOver": "AwayVenueOverScore",
    "BTTSProfile": "BTTSProfileScore",
}

TOTAL_WEIGHT = sum(BASE_WEIGHTS.values())


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


def find_history() -> Path:
    for path in HISTORY_CANDIDATES:
        if path.exists():
            return path

    found = [
        p
        for p in Path("data").rglob("storico_ranking_v22*.csv")
        if "old" not in p.name.casefold()
        and "bak" not in p.name.casefold()
    ]

    if not found:
        raise FileNotFoundError(
            "Impossibile trovare storico_ranking_v22.csv"
        )

    found.sort(key=lambda p: (len(str(p)), str(p)))
    return found[0]


def read_history(path: Path) -> pd.DataFrame:
    return pd.read_csv(
        path,
        sep=detect_delimiter(path),
        encoding="utf-8-sig",
        low_memory=False,
    )


def normalize_weights(values: np.ndarray) -> np.ndarray:
    values = np.maximum(values.astype(float), 0.20)
    return values / values.sum() * TOTAL_WEIGHT


def config_signature(weights: np.ndarray) -> tuple:
    return tuple(round(float(v), 4) for v in weights)


def generate_configurations() -> pd.DataFrame:
    rng = np.random.default_rng(RANDOM_SEED)

    baseline = np.array(
        [BASE_WEIGHTS[d] for d in DRIVERS],
        dtype=float,
    )

    configs = [("BASE_V22", baseline, "BASELINE")]
    signatures = {config_signature(baseline)}

    local_count = 0
    while local_count < N_LOCAL_CONFIGS:
        noise = rng.normal(
            loc=0.0,
            scale=0.25,
            size=len(DRIVERS),
        )
        candidate = normalize_weights(
            baseline * (1.0 + noise)
        )
        sig = config_signature(candidate)
        if sig in signatures:
            continue
        signatures.add(sig)
        local_count += 1
        configs.append(
            (f"LOC_{local_count:04d}", candidate, "LOCAL")
        )

    base_share = baseline / TOTAL_WEIGHT
    alpha = base_share * 18.0 + 0.35

    global_count = 0
    while global_count < N_GLOBAL_CONFIGS:
        candidate = rng.dirichlet(alpha) * TOTAL_WEIGHT
        sig = config_signature(candidate)
        if sig in signatures:
            continue
        signatures.add(sig)
        global_count += 1
        configs.append(
            (f"GLOB_{global_count:04d}", candidate, "GLOBAL")
        )

    rows = []

    for config_id, weights, kind in configs:
        row = {
            "ConfigId": config_id,
            "Type": kind,
            "TotalWeight": round(
                float(weights.sum()),
                6,
            ),
        }

        for driver, weight in zip(DRIVERS, weights):
            row[f"W_{driver}"] = round(
                float(weight),
                6,
            )

        rows.append(row)

    result = pd.DataFrame(rows)

    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    result.to_csv(
        CONFIG_FILE,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    return result


def load_or_create_configurations() -> pd.DataFrame:
    if CONFIG_FILE.exists():
        return pd.read_csv(
            CONFIG_FILE,
            sep=";",
            encoding="utf-8-sig",
        )

    return generate_configurations()


def outcome_column(df: pd.DataFrame) -> str:
    for column in (
        "Over25",
        "Outcome",
        "Esito",
        "Result",
    ):
        if column in df.columns:
            return column

    raise ValueError(
        "Nessuna colonna esito trovata."
    )


def prepare_history(history: pd.DataFrame) -> pd.DataFrame:
    missing = [
        column
        for column in SCORE_COLUMNS.values()
        if column not in history.columns
    ]

    if missing:
        raise ValueError(
            "Colonne driver mancanti nello storico v22: "
            + ", ".join(missing)
        )

    df = history.copy()

    outcome_col = outcome_column(df)

    df["Outcome"] = (
        df[outcome_col]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df = df[
        df["Outcome"].isin({"OK", "KO"})
    ].copy()

    if "MatchDate" in df.columns:
        df["_Date"] = pd.to_datetime(
            df["MatchDate"],
            errors="coerce",
        )
    elif "PredictionDate" in df.columns:
        df["_Date"] = pd.to_datetime(
            df["PredictionDate"],
            errors="coerce",
        )
    else:
        df["_Date"] = pd.NaT

    for driver in DRIVERS:
        weighted = pd.to_numeric(
            df[SCORE_COLUMNS[driver]],
            errors="coerce",
        ).fillna(0.0)

        df[f"RAW_{driver}"] = (
            weighted / BASE_WEIGHTS[driver]
        )

    return df


def split_masks(df: pd.DataFrame):
    valid_dates = (
        df["_Date"]
        .dropna()
        .dt.normalize()
        .sort_values()
        .unique()
    )

    if len(valid_dates) < 2:
        return (
            np.zeros(len(df), dtype=bool),
            np.ones(len(df), dtype=bool),
        )

    split_index = int(
        len(valid_dates) * TRAIN_RATIO
    )

    split_index = max(
        1,
        min(split_index, len(valid_dates) - 1),
    )

    split_date = pd.Timestamp(
        valid_dates[split_index]
    )

    dates = df["_Date"]

    train_mask = (
        dates.notna()
        & (dates < split_date)
    ).to_numpy()

    test_mask = (
        dates.notna()
        & (dates >= split_date)
    ).to_numpy()

    return train_mask, test_mask


def metrics(selected, ok_mask, ko_mask):
    ok = int(np.sum(selected & ok_mask))
    ko = int(np.sum(selected & ko_mask))
    total = ok + ko
    rate = (
        ok / total * 100.0
        if total
        else 0.0
    )
    return ok, ko, total, round(rate, 4)


def sample_class(total: int) -> str:
    if total < 10:
        return "<10"
    if total < 20:
        return "10-19"
    if total < 50:
        return "20-49"
    if total < 100:
        return "50-99"
    return "100+"


def evaluate_configs(
    df: pd.DataFrame,
    configs: pd.DataFrame,
) -> pd.DataFrame:
    raw_matrix = df[
        [f"RAW_{d}" for d in DRIVERS]
    ].to_numpy(dtype=float)

    ok_mask = (
        df["Outcome"].eq("OK").to_numpy()
    )
    ko_mask = (
        df["Outcome"].eq("KO").to_numpy()
    )

    league_series = (
        df["LeagueId"]
        if "LeagueId" in df.columns
        else pd.Series("", index=df.index)
    )

    no_au_mask = (
        ~league_series
        .fillna("")
        .astype(str)
        .str.startswith("Australia_")
    ).to_numpy()

    train_mask, test_mask = split_masks(df)

    rows = []

    for _, config in configs.iterrows():
        weights = np.array(
            [
                float(config[f"W_{d}"])
                for d in DRIVERS
            ],
            dtype=float,
        )

        scores = raw_matrix @ weights
        alta = scores >= ALTA_THRESHOLD

        overall = metrics(
            alta,
            ok_mask,
            ko_mask,
        )
        no_au = metrics(
            alta & no_au_mask,
            ok_mask,
            ko_mask,
        )
        train = metrics(
            alta & train_mask,
            ok_mask,
            ko_mask,
        )
        test = metrics(
            alta & test_mask,
            ok_mask,
            ko_mask,
        )

        row = {
            "ConfigId": config["ConfigId"],
            "Type": config["Type"],

            "Overall_OK": overall[0],
            "Overall_KO": overall[1],
            "Overall_Total": overall[2],
            "Overall_HitRate": overall[3],
            "Overall_SampleClass": sample_class(
                overall[2]
            ),

            "NoAU_OK": no_au[0],
            "NoAU_KO": no_au[1],
            "NoAU_Total": no_au[2],
            "NoAU_HitRate": no_au[3],

            "Train_OK": train[0],
            "Train_KO": train[1],
            "Train_Total": train[2],
            "Train_HitRate": train[3],

            "Test_OK": test[0],
            "Test_KO": test[1],
            "Test_Total": test[2],
            "Test_HitRate": test[3],
            "Test_SampleClass": sample_class(
                test[2]
            ),

            "TrainTestDelta": round(
                test[3] - train[3],
                4,
            ),
        }

        for driver in DRIVERS:
            row[f"W_{driver}"] = config[
                f"W_{driver}"
            ]

        rows.append(row)

    return pd.DataFrame(rows)


def sort_overall(df: pd.DataFrame):
    return df.sort_values(
        by=[
            "Overall_HitRate",
            "Overall_KO",
            "Overall_Total",
        ],
        ascending=[
            False,
            True,
            False,
        ],
    ).reset_index(drop=True)


def sort_validation(df: pd.DataFrame):
    return df.sort_values(
        by=[
            "Test_HitRate",
            "Test_KO",
            "Overall_HitRate",
            "Overall_KO",
            "Test_Total",
        ],
        ascending=[
            False,
            True,
            False,
            True,
            False,
        ],
    ).reset_index(drop=True)


def write_outputs(
    evaluated: pd.DataFrame,
    history_path: Path,
    sample_rows: int,
):
    run_stamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    snapshot_dir = (
        OUTPUT_ROOT
        / "snapshots"
        / run_stamp
    )

    for directory in (
        LATEST_DIR,
        snapshot_dir,
    ):
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    baseline = evaluated[
        evaluated["ConfigId"] == "BASE_V22"
    ].copy()

    overall = sort_overall(evaluated)
    validation = sort_validation(evaluated)

    stable = validation[
        validation["Test_Total"]
        >= MIN_TEST_SAMPLE_FOR_STABLE
    ].copy()

    best = validation.head(1).copy()

    comparison = pd.concat(
        [
            baseline.assign(
                ComparisonRole="BASELINE"
            ),
            best.assign(
                ComparisonRole="BEST_VALIDATION"
            ),
        ],
        ignore_index=True,
    )

    files = {
        "01_baseline.csv": baseline,
        "02_all_configs_overall.csv": overall,
        "03_all_configs_validation.csv": validation,
        "04_top_stable.csv": stable,
        "05_baseline_vs_best.csv": comparison,
    }

    for filename, frame in files.items():
        for directory in (
            LATEST_DIR,
            snapshot_dir,
        ):
            frame.to_csv(
                directory / filename,
                sep=";",
                index=False,
                encoding="utf-8-sig",
            )

    top = validation.head(TOP_TO_STORE).copy()

    top = pd.concat(
        [
            baseline,
            top[
                top["ConfigId"] != "BASE_V22"
            ],
        ],
        ignore_index=True,
    )

    top.insert(0, "RunStamp", run_stamp)
    top.insert(1, "HistoryRows", sample_rows)
    top.insert(2, "HistoryFile", str(history_path))

    if RUNS_HISTORY_FILE.exists():
        previous = pd.read_csv(
            RUNS_HISTORY_FILE,
            sep=";",
            encoding="utf-8-sig",
            low_memory=False,
        )
        combined = pd.concat(
            [previous, top],
            ignore_index=True,
        )
    else:
        combined = top

    combined.to_csv(
        RUNS_HISTORY_FILE,
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(f"Snapshot: {snapshot_dir}")


def main():
    OUTPUT_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    history_path = find_history()
    history = prepare_history(
        read_history(history_path)
    )

    configs = load_or_create_configurations()

    evaluated = evaluate_configs(
        history,
        configs,
    )

    write_outputs(
        evaluated,
        history_path,
        len(history),
    )

    baseline = evaluated[
        evaluated["ConfigId"] == "BASE_V22"
    ]

    best_validation = sort_validation(
        evaluated
    ).head(10)

    print(
        "=== V22 WEIGHT OPTIMIZER RECURRING ==="
    )
    print(f"Storico: {history_path}")
    print(
        f"Partite concluse analizzate: {len(history)}"
    )
    print(
        f"Configurazioni: {len(configs)}"
    )

    print()
    print("BASELINE V22")
    print(
        baseline[
            [
                "Overall_OK",
                "Overall_KO",
                "Overall_Total",
                "Overall_HitRate",
                "Test_OK",
                "Test_KO",
                "Test_Total",
                "Test_HitRate",
                "NoAU_HitRate",
            ]
        ].to_string(index=False)
    )

    print()
    print("TOP 10 VALIDATION")
    print(
        best_validation[
            [
                "ConfigId",
                "Type",
                "Overall_OK",
                "Overall_KO",
                "Overall_HitRate",
                "Test_OK",
                "Test_KO",
                "Test_HitRate",
                "Test_Total",
                "NoAU_HitRate",
            ]
        ].to_string(index=False)
    )

    print()
    print(f"Output: {OUTPUT_ROOT}")


if __name__ == "__main__":
    main()
