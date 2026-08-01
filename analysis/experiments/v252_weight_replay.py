"""
===============================================================================
GioOver2.5 - v252 historical weight replay
===============================================================================

SCOPO
-----
Riprodurre sullo storico del Laboratory configurazioni alternative di pesi
applicate allo Score originale, senza modificare gli engine di produzione.

INPUT
-----
analysis/laboratory/data/01_matches.csv

Il file contiene già:
- Score originale;
- Band originale;
- Outcome OK/KO;
- driver strutturali;
- driver recent-form;
- driver restart.

OUTPUT
------
analysis/experiments/v252_weight_replay/
    01_profile_summary.csv
    02_band_transitions.csv
    03_match_details.csv
    04_best_profiles.csv

USO
---
python -m analysis.experiments.v252_weight_replay

NOTE
----
- Non ricostruisce lo Score base: parte dallo Score storico già prodotto.
- Applica soltanto penalità/bonus sperimentali ai driver disponibili.
- Le soglie fascia restano:
      ALTA  >= 75
      MEDIA >= 60
      BASSA < 60
===============================================================================
"""

from __future__ import annotations

import csv
import itertools
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd


INPUT_FILE = Path(
    "analysis/laboratory/data/01_matches.csv"
)

OUTPUT_DIR = Path(
    "analysis/experiments/v252_weight_replay"
)

ALTA_THRESHOLD = 75.0
MEDIA_THRESHOLD = 60.0

VALID_OUTCOMES = {"OK", "KO"}


@dataclass(frozen=True)
class Rule:
    name: str
    predicate: Callable[[pd.Series], bool]
    weight: float


@dataclass(frozen=True)
class Profile:
    name: str
    description: str
    rules: tuple[Rule, ...]


def _num(row: pd.Series, field: str) -> float | None:
    value = row.get(field)

    if pd.isna(value):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _flag(row: pd.Series, field: str) -> bool:
    value = _num(row, field)
    return value is not None and value >= 1.0


def band_from_score(score: float) -> str:
    if score >= ALTA_THRESHOLD:
        return "ALTA"

    if score >= MEDIA_THRESHOLD:
        return "MEDIA"

    return "BASSA"


def build_profiles() -> list[Profile]:
    """
    Profili iniziali volutamente leggibili.

    I pesi negativi sono penalità.
    I pesi positivi sono bonus.
    """

    base_rules = {
        "gap_high": lambda row: (
            (_num(row, "RankingGapScore") or 0.0) >= 4.0
        ),
        "home_ppg_low": lambda row: (
            (_num(row, "HomePPGLast5") is not None)
            and (_num(row, "HomePPGLast5") < 1.0)
        ),
        "worst_ppg_low": lambda row: (
            (_num(row, "WorstPPGLast5") is not None)
            and (_num(row, "WorstPPGLast5") < 0.8)
        ),
        "home_wins_low": lambda row: (
            (_num(row, "HomeWinsLast5") is not None)
            and (_num(row, "HomeWinsLast5") <= 1.0)
        ),
        "home_restart_gf_low": lambda row: (
            (_num(row, "HomeGFAvgSinceRestart") is not None)
            and (_num(row, "HomeGFAvgSinceRestart") < 1.2)
        ),
        "home_restart_not_ready": lambda row: _flag(
            row,
            "HomeRestartNotReady",
        ),
        "both_restart_not_ready": lambda row: _flag(
            row,
            "BothTeamsRestartNotReady",
        ),
        "home_ppg_good": lambda row: (
            (_num(row, "HomePPGLast5") is not None)
            and (_num(row, "HomePPGLast5") >= 1.8)
        ),
        "worst_ppg_good": lambda row: (
            (_num(row, "WorstPPGLast5") is not None)
            and (_num(row, "WorstPPGLast5") >= 1.4)
        ),
        "home_restart_gf_good": lambda row: (
            (_num(row, "HomeGFAvgSinceRestart") is not None)
            and (_num(row, "HomeGFAvgSinceRestart") >= 2.0)
        ),
    }

    profiles = [
        Profile(
            name="BASELINE",
            description="Score originale senza modifiche",
            rules=(),
        ),
        Profile(
            name="LIGHT",
            description="Penalità leggere sui segnali principali",
            rules=(
                Rule("gap_high", base_rules["gap_high"], -1.0),
                Rule("home_ppg_low", base_rules["home_ppg_low"], -1.0),
                Rule("worst_ppg_low", base_rules["worst_ppg_low"], -1.0),
                Rule("home_wins_low", base_rules["home_wins_low"], -0.5),
                Rule(
                    "home_restart_gf_low",
                    base_rules["home_restart_gf_low"],
                    -1.0,
                ),
                Rule(
                    "home_restart_not_ready",
                    base_rules["home_restart_not_ready"],
                    -1.0,
                ),
                Rule(
                    "both_restart_not_ready",
                    base_rules["both_restart_not_ready"],
                    -2.0,
                ),
            ),
        ),
        Profile(
            name="MEDIUM",
            description="Penalità medie sui segnali principali",
            rules=(
                Rule("gap_high", base_rules["gap_high"], -2.0),
                Rule("home_ppg_low", base_rules["home_ppg_low"], -2.0),
                Rule("worst_ppg_low", base_rules["worst_ppg_low"], -2.0),
                Rule("home_wins_low", base_rules["home_wins_low"], -1.0),
                Rule(
                    "home_restart_gf_low",
                    base_rules["home_restart_gf_low"],
                    -2.0,
                ),
                Rule(
                    "home_restart_not_ready",
                    base_rules["home_restart_not_ready"],
                    -2.0,
                ),
                Rule(
                    "both_restart_not_ready",
                    base_rules["both_restart_not_ready"],
                    -4.0,
                ),
            ),
        ),
        Profile(
            name="STRONG",
            description="Penalità forti sui segnali principali",
            rules=(
                Rule("gap_high", base_rules["gap_high"], -3.0),
                Rule("home_ppg_low", base_rules["home_ppg_low"], -3.0),
                Rule("worst_ppg_low", base_rules["worst_ppg_low"], -3.0),
                Rule("home_wins_low", base_rules["home_wins_low"], -1.5),
                Rule(
                    "home_restart_gf_low",
                    base_rules["home_restart_gf_low"],
                    -3.0,
                ),
                Rule(
                    "home_restart_not_ready",
                    base_rules["home_restart_not_ready"],
                    -3.0,
                ),
                Rule(
                    "both_restart_not_ready",
                    base_rules["both_restart_not_ready"],
                    -6.0,
                ),
            ),
        ),
        Profile(
            name="BALANCED_BONUS",
            description="Penalità medie più bonus sui segnali contrari",
            rules=(
                Rule("gap_high", base_rules["gap_high"], -2.0),
                Rule("home_ppg_low", base_rules["home_ppg_low"], -2.0),
                Rule("worst_ppg_low", base_rules["worst_ppg_low"], -2.0),
                Rule("home_wins_low", base_rules["home_wins_low"], -1.0),
                Rule(
                    "home_restart_gf_low",
                    base_rules["home_restart_gf_low"],
                    -2.0,
                ),
                Rule(
                    "home_restart_not_ready",
                    base_rules["home_restart_not_ready"],
                    -2.0,
                ),
                Rule(
                    "both_restart_not_ready",
                    base_rules["both_restart_not_ready"],
                    -4.0,
                ),
                Rule("home_ppg_good", base_rules["home_ppg_good"], 1.0),
                Rule("worst_ppg_good", base_rules["worst_ppg_good"], 1.0),
                Rule(
                    "home_restart_gf_good",
                    base_rules["home_restart_gf_good"],
                    1.5,
                ),
            ),
        ),
    ]

    # Piccola griglia automatica: stessa struttura, intensità differenti.
    for gap_weight, ppg_weight, restart_weight in itertools.product(
        (-1.0, -2.0, -3.0),
        (-1.0, -2.0, -3.0),
        (-2.0, -4.0, -6.0),
    ):
        name = (
            "GRID_"
            f"G{abs(int(gap_weight))}_"
            f"P{abs(int(ppg_weight))}_"
            f"R{abs(int(restart_weight))}"
        )

        profiles.append(
            Profile(
                name=name,
                description=(
                    "Griglia automatica: "
                    f"gap={gap_weight}, "
                    f"ppg={ppg_weight}, "
                    f"restart={restart_weight}"
                ),
                rules=(
                    Rule("gap_high", base_rules["gap_high"], gap_weight),
                    Rule(
                        "home_ppg_low",
                        base_rules["home_ppg_low"],
                        ppg_weight,
                    ),
                    Rule(
                        "worst_ppg_low",
                        base_rules["worst_ppg_low"],
                        ppg_weight,
                    ),
                    Rule(
                        "both_restart_not_ready",
                        base_rules["both_restart_not_ready"],
                        restart_weight,
                    ),
                ),
            )
        )

    return profiles


def apply_profile(
    row: pd.Series,
    profile: Profile,
) -> tuple[float, list[str]]:
    score = float(row["Score"])
    applied_rules = []

    for rule in profile.rules:
        if rule.predicate(row):
            score += rule.weight
            applied_rules.append(
                f"{rule.name}:{rule.weight:+.2f}"
            )

    return round(score, 4), applied_rules


def safe_rate(ok: int, ko: int) -> float:
    total = ok + ko

    if total == 0:
        return 0.0

    return round(
        ok / total * 100.0,
        4,
    )


def summarize_profile(
    details: pd.DataFrame,
    profile: Profile,
) -> dict:
    profile_rows = details[
        details["Profile"] == profile.name
    ]

    summary = {
        "Profile": profile.name,
        "Description": profile.description,
        "TotalMatches": len(profile_rows),
    }

    for band in ("ALTA", "MEDIA", "BASSA"):
        band_rows = profile_rows[
            profile_rows["NewBand"] == band
        ]

        ok = int(
            (band_rows["Outcome"] == "OK").sum()
        )
        ko = int(
            (band_rows["Outcome"] == "KO").sum()
        )

        summary[f"{band}_OK"] = ok
        summary[f"{band}_KO"] = ko
        summary[f"{band}_Total"] = ok + ko
        summary[f"{band}_Hit"] = safe_rate(ok, ko)

    alta_original = profile_rows[
        profile_rows["OriginalBand"] == "ALTA"
    ]

    summary["AltaKOAvoided"] = int(
        (
            (alta_original["Outcome"] == "KO")
            & (alta_original["NewBand"] != "ALTA")
        ).sum()
    )

    summary["AltaOKLost"] = int(
        (
            (alta_original["Outcome"] == "OK")
            & (alta_original["NewBand"] != "ALTA")
        ).sum()
    )

    summary["OKPromotedToAlta"] = int(
        (
            (profile_rows["Outcome"] == "OK")
            & (profile_rows["OriginalBand"] != "ALTA")
            & (profile_rows["NewBand"] == "ALTA")
        ).sum()
    )

    summary["KOPromotedToAlta"] = int(
        (
            (profile_rows["Outcome"] == "KO")
            & (profile_rows["OriginalBand"] != "ALTA")
            & (profile_rows["NewBand"] == "ALTA")
        ).sum()
    )

    summary["BandChanges"] = int(
        (
            profile_rows["OriginalBand"]
            != profile_rows["NewBand"]
        ).sum()
    )

    # Indice semplice, non decisione automatica:
    # premia KO evitati e OK promossi;
    # penalizza OK persi e KO promossi.
    summary["Utility"] = (
        summary["AltaKOAvoided"] * 2
        + summary["OKPromotedToAlta"]
        - summary["AltaOKLost"]
        - summary["KOPromotedToAlta"] * 2
    )

    return summary


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
        "Score",
        "Band",
        "Outcome",
        "LeagueId",
        "Home",
        "Away",
        "PredictionDate",
    }

    missing = required - set(matches.columns)

    if missing:
        raise ValueError(
            "01_matches.csv non contiene: "
            + ", ".join(sorted(missing))
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

    profiles = build_profiles()
    detail_rows = []

    for profile in profiles:
        for _, row in matches.iterrows():
            new_score, applied = apply_profile(
                row,
                profile,
            )

            detail_rows.append(
                {
                    "Profile": profile.name,
                    "MatchId": row["MatchId"],
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
                    "Outcome": row["Outcome"],
                    "OriginalScore": row["Score"],
                    "NewScore": new_score,
                    "OriginalBand": row["Band"],
                    "NewBand": band_from_score(
                        new_score
                    ),
                    "ScoreDelta": round(
                        new_score - float(row["Score"]),
                        4,
                    ),
                    "AppliedRules": " | ".join(applied),
                }
            )

    details = pd.DataFrame(
        detail_rows
    )

    details.to_csv(
        OUTPUT_DIR / "03_match_details.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    summaries = pd.DataFrame(
        [
            summarize_profile(
                details,
                profile,
            )
            for profile in profiles
        ]
    )

    summaries = summaries.sort_values(
        by=[
            "Utility",
            "ALTA_Hit",
            "ALTA_Total",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    )

    summaries.to_csv(
        OUTPUT_DIR / "01_profile_summary.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    transitions = (
        details.groupby(
            [
                "Profile",
                "OriginalBand",
                "NewBand",
                "Outcome",
            ],
            dropna=False,
        )
        .size()
        .reset_index(
            name="Matches"
        )
    )

    transitions.to_csv(
        OUTPUT_DIR / "02_band_transitions.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    summaries.head(10).to_csv(
        OUTPUT_DIR / "04_best_profiles.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"Partite concluse analizzate: {len(matches)}"
    )
    print(
        f"Profili testati: {len(profiles)}"
    )
    print(
        f"Output: {OUTPUT_DIR}"
    )
    print()
    print(
        summaries[
            [
                "Profile",
                "ALTA_OK",
                "ALTA_KO",
                "ALTA_Total",
                "ALTA_Hit",
                "AltaKOAvoided",
                "AltaOKLost",
                "OKPromotedToAlta",
                "KOPromotedToAlta",
                "BandChanges",
                "Utility",
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
