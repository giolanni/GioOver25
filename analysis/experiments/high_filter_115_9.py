"""
GioOver2.5 - Test filtro severo HomeAttack >= 11.5 AND AwayDefense >= 9

Obiettivo
---------
Applicare lo stesso filtro alle partite già classificate ALTA da ciascun engine
e misurare come cambia la precisione.

Filtro:
    HomeAttackScore >= 11.5
    AND
    AwayDefenseWeaknessScore >= 9.0

ATTENZIONE
----------
I valori HomeAttackScore e AwayDefenseWeaknessScore sono contributi PESATI
salvati nello storico ranking. Il loro massimo può cambiare tra engine.
Per questo motivo lo script produce anche un file diagnostico con i massimi
osservati per ogni engine.

Output:
analysis/experiments/high_filter_115_9/
    01_engine_overall.csv
    02_common_set.csv
    03_driver_ranges.csv
    04_filtered_matches.csv

Uso:
python -m analysis.experiments.high_filter_115_9
"""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


RANKING_ROOT = Path("data/storico/ranking")
OUTPUT_DIR = Path("analysis/experiments/high_filter_115_9")

HOME_ATTACK_MIN = 11.5
AWAY_DEFENSE_MIN = 7.0

VALID_OUTCOMES = {"OK", "KO"}

EXCLUDED_ENGINES = {"v251", "v26"}


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
    )


def normalize_text(value) -> str:
    return " ".join(
        str(value or "")
        .strip()
        .casefold()
        .split()
    )


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko
    if total == 0:
        return 0.0
    return round(ok / total * 100.0, 4)


def history_files() -> list[tuple[str, Path]]:
    files = []

    if not RANKING_ROOT.exists():
        return files

    for engine_dir in sorted(RANKING_ROOT.iterdir()):
        if not engine_dir.is_dir():
            continue

        engine = engine_dir.name

        if engine in EXCLUDED_ENGINES:
            continue

        path = engine_dir / f"storico_ranking_{engine}.csv"

        if path.exists():
            files.append((engine, path))

    return files


def prepare(df: pd.DataFrame, engine: str) -> pd.DataFrame:
    required = {
        "Home",
        "Away",
        "Band",
        "Over25",
        "HomeAttackScore",
        "AwayDefenseWeaknessScore",
    }

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
    out["BandNorm"] = (
        out["Band"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    out["HomeAttackScoreNum"] = pd.to_numeric(
        out["HomeAttackScore"],
        errors="coerce",
    )

    out["AwayDefenseScoreNum"] = pd.to_numeric(
        out["AwayDefenseWeaknessScore"],
        errors="coerce",
    )

    out = out[
        out["Outcome"].isin(VALID_OUTCOMES)
    ].copy()

    out["_PairKey"] = (
        out["Home"].map(normalize_text)
        + "||"
        + out["Away"].map(normalize_text)
    )

    # Stessa logica del set comune usata nel progetto:
    # Home + Away come chiave principale; duplicate reali mantenute separate.
    out["_Occurrence"] = (
        out.groupby("_PairKey")
        .cumcount()
    )

    out["_MatchKey"] = (
        out["_PairKey"]
        + "||"
        + out["_Occurrence"].astype(str)
    )

    return out


def evaluate(engine: str, rows: pd.DataFrame, scope: str) -> dict:
    alta = rows[
        rows["BandNorm"] == "ALTA"
    ].copy()

    base_ok = int((alta["Outcome"] == "OK").sum())
    base_ko = int((alta["Outcome"] == "KO").sum())

    filtered = alta[
        (alta["HomeAttackScoreNum"] >= HOME_ATTACK_MIN)
        & (alta["AwayDefenseScoreNum"] >= AWAY_DEFENSE_MIN)
    ].copy()

    filtered_ok = int(
        (filtered["Outcome"] == "OK").sum()
    )
    filtered_ko = int(
        (filtered["Outcome"] == "KO").sum()
    )

    return {
        "Scope": scope,
        "Engine": engine,
        "Filter": (
            f"HomeAttackScore>={HOME_ATTACK_MIN} AND "
            f"AwayDefenseWeaknessScore>={AWAY_DEFENSE_MIN}"
        ),
        "Base_OK": base_ok,
        "Base_KO": base_ko,
        "Base_Total": base_ok + base_ko,
        "Base_HitRate": safe_rate(base_ok, base_ko),
        "Filtered_OK": filtered_ok,
        "Filtered_KO": filtered_ko,
        "Filtered_Total": filtered_ok + filtered_ko,
        "Filtered_HitRate": safe_rate(
            filtered_ok,
            filtered_ko,
        ),
        "DeltaHitRate": round(
            safe_rate(filtered_ok, filtered_ko)
            - safe_rate(base_ok, base_ko),
            4,
        ),
        "OK_Removed": base_ok - filtered_ok,
        "KO_Removed": base_ko - filtered_ko,
        "CoveragePct": round(
            (
                (filtered_ok + filtered_ko)
                / (base_ok + base_ko)
                * 100.0
            )
            if (base_ok + base_ko)
            else 0.0,
            4,
        ),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    prepared: dict[str, pd.DataFrame] = {}
    overall_rows = []
    ranges = []
    filtered_match_frames = []

    for engine, path in history_files():
        data = prepare(
            read_csv(path),
            engine,
        )

        prepared[engine] = data

        overall_rows.append(
            evaluate(
                engine,
                data,
                "INDIVIDUAL_HISTORY",
            )
        )

        ranges.append(
            {
                "Engine": engine,
                "HomeAttackScore_Min": round(
                    data["HomeAttackScoreNum"].min(),
                    4,
                ),
                "HomeAttackScore_Max": round(
                    data["HomeAttackScoreNum"].max(),
                    4,
                ),
                "AwayDefenseScore_Min": round(
                    data["AwayDefenseScoreNum"].min(),
                    4,
                ),
                "AwayDefenseScore_Max": round(
                    data["AwayDefenseScoreNum"].max(),
                    4,
                ),
                "Rows": len(data),
            }
        )

        filtered = data[
            (data["BandNorm"] == "ALTA")
            & (
                data["HomeAttackScoreNum"]
                >= HOME_ATTACK_MIN
            )
            & (
                data["AwayDefenseScoreNum"]
                >= AWAY_DEFENSE_MIN
            )
        ].copy()

        if not filtered.empty:
            filtered_match_frames.append(
                filtered[
                    [
                        column
                        for column in [
                            "Engine",
                            "PredictionDate",
                            "MatchDate",
                            "LeagueId",
                            "Home",
                            "Away",
                            "Score",
                            "Band",
                            "Outcome",
                            "HomeAttackScore",
                            "AwayDefenseWeaknessScore",
                            "Reason",
                        ]
                        if column in filtered.columns
                    ]
                ]
            )

    overall_df = pd.DataFrame(overall_rows)

    overall_df = overall_df.sort_values(
        by=[
            "Filtered_HitRate",
            "Filtered_Total",
        ],
        ascending=[
            False,
            False,
        ],
    )

    overall_df.to_csv(
        OUTPUT_DIR / "01_engine_overall.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    # ---------------------------------------------------------------
    # SET COMUNE: intersezione di tutte le partite concluse presenti
    # negli engine caricati.
    # ---------------------------------------------------------------
    if prepared:
        common_keys = None

        for data in prepared.values():
            keys = set(data["_MatchKey"])

            common_keys = (
                keys
                if common_keys is None
                else common_keys & keys
            )

        common_rows = []

        for engine, data in prepared.items():
            common_data = data[
                data["_MatchKey"].isin(
                    common_keys or set()
                )
            ].copy()

            common_rows.append(
                evaluate(
                    engine,
                    common_data,
                    "COMMON_SET",
                )
            )

        common_df = pd.DataFrame(
            common_rows
        ).sort_values(
            by=[
                "Filtered_HitRate",
                "Filtered_Total",
            ],
            ascending=[
                False,
                False,
            ],
        )

        common_df.to_csv(
            OUTPUT_DIR / "02_common_set.csv",
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )

    pd.DataFrame(ranges).to_csv(
        OUTPUT_DIR / "03_driver_ranges.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    if filtered_match_frames:
        pd.concat(
            filtered_match_frames,
            ignore_index=True,
        ).to_csv(
            OUTPUT_DIR / "04_filtered_matches.csv",
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )
    else:
        pd.DataFrame().to_csv(
            OUTPUT_DIR / "04_filtered_matches.csv",
            sep=";",
            index=False,
            encoding="utf-8-sig",
        )

    print(
        f"Engine analizzati: {len(prepared)}"
    )
    print(
        f"Filtro: HomeAttack >= {HOME_ATTACK_MIN} "
        f"AND AwayDefense >= {AWAY_DEFENSE_MIN}"
    )
    print(
        f"Output: {OUTPUT_DIR}"
    )
    print()

    display = [
        "Engine",
        "Base_OK",
        "Base_KO",
        "Base_HitRate",
        "Filtered_OK",
        "Filtered_KO",
        "Filtered_Total",
        "Filtered_HitRate",
        "DeltaHitRate",
        "CoveragePct",
    ]

    print(
        overall_df[
            display
        ].to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
