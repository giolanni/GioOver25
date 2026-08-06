"""
GioOver2.5 - Distribuzione PROX PPG

Legge:
analysis/experiments/prox_ppg/02_prox_matches.csv

Considera solo:
- Engine = v25
- MaxPPGGap = 0.30
- Band = ALTA

Produce:
analysis/experiments/prox_ppg_distribution/
    01_league_distribution.csv
    02_country_distribution.csv
    03_top_concentrations.csv

Uso:
python -m analysis.experiments.prox_ppg_distribution
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "analysis/experiments/prox_ppg/02_prox_matches.csv"
)

OUTPUT_DIR = Path(
    "analysis/experiments/prox_ppg_distribution"
)

ENGINE = "v25"
PPG_GAP = 0.30
BAND = "ALTA"


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko

    if total == 0:
        return 0.0

    return round(
        ok / total * 100.0,
        2,
    )


def country_from_league_id(
    league_id: str,
) -> str:
    value = str(
        league_id or ""
    ).strip()

    if not value:
        return ""

    return value.split(
        "_",
        1,
    )[0]


def summarize(
    rows: pd.DataFrame,
    group_field: str,
) -> pd.DataFrame:
    summary_rows = []

    for group_value, group_rows in rows.groupby(
        group_field,
        dropna=False,
    ):
        ok = int(
            (
                group_rows["Outcome"]
                == "OK"
            ).sum()
        )

        ko = int(
            (
                group_rows["Outcome"]
                == "KO"
            ).sum()
        )

        summary_rows.append(
            {
                group_field: group_value,
                "PROX_ALTA": ok + ko,
                "OK": ok,
                "KO": ko,
                "HitRate": safe_rate(
                    ok,
                    ko,
                ),
                "ShareOfTotalPct": 0.0,
            }
        )

    summary = pd.DataFrame(
        summary_rows
    )

    total = int(
        summary["PROX_ALTA"].sum()
    )

    if total:
        summary["ShareOfTotalPct"] = (
            summary["PROX_ALTA"]
            / total
            * 100.0
        ).round(
            2
        )

    return summary.sort_values(
        by=[
            "PROX_ALTA",
            "HitRate",
            group_field,
        ],
        ascending=[
            False,
            False,
            True,
        ],
    ).reset_index(
        drop=True
    )


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"File non trovato: {INPUT_FILE}"
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = pd.read_csv(
        INPUT_FILE,
        sep=";",
        encoding="utf-8-sig",
        low_memory=False,
    )

    required = {
        "Engine",
        "MaxPPGGap",
        "Band",
        "Outcome",
        "LeagueId",
    }

    missing = (
        required
        - set(data.columns)
    )

    if missing:
        raise ValueError(
            "Colonne mancanti: "
            + ", ".join(
                sorted(missing)
            )
        )

    data["Engine"] = (
        data["Engine"]
        .astype(str)
        .str.strip()
    )

    data["Band"] = (
        data["Band"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    data["Outcome"] = (
        data["Outcome"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    data["MaxPPGGap"] = pd.to_numeric(
        data["MaxPPGGap"],
        errors="coerce",
    )

    selected = data[
        (
            data["Engine"] == ENGINE
        )
        & (
            data["Band"] == BAND
        )
        & (
            data["MaxPPGGap"].round(2)
            == round(PPG_GAP, 2)
        )
        & (
            data["Outcome"].isin(
                {
                    "OK",
                    "KO",
                }
            )
        )
    ].copy()

    if selected.empty:
        raise RuntimeError(
            "Nessuna riga trovata per "
            f"Engine={ENGINE}, "
            f"Band={BAND}, "
            f"MaxPPGGap={PPG_GAP}"
        )

    selected["Country"] = (
        selected["LeagueId"]
        .map(
            country_from_league_id
        )
    )

    league_distribution = summarize(
        selected,
        "LeagueId",
    )

    country_distribution = summarize(
        selected,
        "Country",
    )

    league_distribution.to_csv(
        OUTPUT_DIR
        / "01_league_distribution.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    country_distribution.to_csv(
        OUTPUT_DIR
        / "02_country_distribution.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    concentration_rows = []

    for label, frame in (
        (
            "TOP_1_LEAGUE",
            league_distribution.head(1),
        ),
        (
            "TOP_3_LEAGUES",
            league_distribution.head(3),
        ),
        (
            "TOP_5_LEAGUES",
            league_distribution.head(5),
        ),
        (
            "TOP_1_COUNTRY",
            country_distribution.head(1),
        ),
        (
            "TOP_3_COUNTRIES",
            country_distribution.head(3),
        ),
        (
            "TOP_5_COUNTRIES",
            country_distribution.head(5),
        ),
    ):
        concentration_rows.append(
            {
                "Group": label,
                "PROX_ALTA": int(
                    frame["PROX_ALTA"].sum()
                ),
                "ShareOfTotalPct": round(
                    frame["PROX_ALTA"].sum()
                    / len(selected)
                    * 100.0,
                    2,
                ),
            }
        )

    pd.DataFrame(
        concentration_rows
    ).to_csv(
        OUTPUT_DIR
        / "03_top_concentrations.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    total_ok = int(
        (
            selected["Outcome"] == "OK"
        ).sum()
    )

    total_ko = int(
        (
            selected["Outcome"] == "KO"
        ).sum()
    )

    print(
        f"Engine: {ENGINE}"
    )

    print(
        f"Soglia PPG: {PPG_GAP:.2f}"
    )

    print(
        f"PROX-ALTA analizzate: "
        f"{len(selected)}"
    )

    print(
        f"OK: {total_ok}"
    )

    print(
        f"KO: {total_ko}"
    )

    print(
        f"Hit rate: "
        f"{safe_rate(total_ok, total_ko):.2f}%"
    )

    print(
        f"Leghe coinvolte: "
        f"{selected['LeagueId'].nunique()}"
    )

    print(
        f"Nazioni coinvolte: "
        f"{selected['Country'].nunique()}"
    )

    print(
        f"Output: {OUTPUT_DIR}"
    )


if __name__ == "__main__":
    main()
