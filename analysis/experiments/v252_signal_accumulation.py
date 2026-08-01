"""
===============================================================================
GioOver2.5 - v252 signal accumulation replay
===============================================================================

SCOPO
-----
Misurare l'effetto dell'accumulo simultaneo dei segnali di rischio emersi dal
Laboratory, invece di applicare soltanto pesi indipendenti ai singoli driver.

Lo script parte dallo Score storico già presente in:

    analysis/laboratory/data/01_matches.csv

Per ogni partita:

1. conta quanti segnali di rischio sono attivi;
2. applica una penalità crescente in base al numero di segnali;
3. ricalcola lo Score e la fascia;
4. misura KO evitati, OK persi, promozioni e cambi fascia;
5. confronta diverse configurazioni di penalità cumulative.

INPUT
-----
analysis/laboratory/data/01_matches.csv

OUTPUT
------
analysis/experiments/v252_signal_accumulation/

    01_profile_summary.csv
    02_signal_count_performance.csv
    03_band_transitions.csv
    04_match_details.csv
    05_best_profiles.csv

USO
---
python -m analysis.experiments.v252_signal_accumulation

LIMITI
------
Lo script non ricostruisce lo Score originale. Parte dallo Score storico e
simula soltanto l'effetto delle nuove penalità cumulative.
===============================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


INPUT_FILE = Path(
    "analysis/laboratory/data/01_matches.csv"
)

OUTPUT_DIR = Path(
    "analysis/experiments/v252_signal_accumulation"
)

ALTA_THRESHOLD = 75.0
MEDIA_THRESHOLD = 60.0

VALID_OUTCOMES = {
    "OK",
    "KO",
}


@dataclass(frozen=True)
class AccumulationProfile:
    """
    Configurazione delle penalità applicate in base al numero di segnali.

    Esempio:
        penalties={0: 0, 1: 0, 2: -2, 3: -5, 4: -8}

    significa:
        0 segnali -> nessuna penalità
        1 segnale -> nessuna penalità
        2 segnali -> -2 punti
        3 segnali -> -5 punti
        4 o più   -> -8 punti
    """

    name: str
    description: str
    penalties: dict[int, float]
    minimum_signals: int = 0


def _num(
    row: pd.Series,
    field: str,
) -> float | None:
    """
    Converte in float il valore di una colonna.

    Restituisce None quando il valore è assente o non numerico.
    """

    value = row.get(field)

    if pd.isna(value):
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _flag(
    row: pd.Series,
    field: str,
) -> bool:
    """
    Interpreta una colonna binaria come True quando il valore è almeno 1.
    """

    value = _num(
        row,
        field,
    )

    return (
        value is not None
        and value >= 1.0
    )


def band_from_score(
    score: float,
) -> str:
    """
    Traduce lo score simulato nella fascia corrispondente.
    """

    if score >= ALTA_THRESHOLD:
        return "ALTA"

    if score >= MEDIA_THRESHOLD:
        return "MEDIA"

    return "BASSA"


def safe_rate(
    ok: int,
    ko: int,
) -> float:
    """
    Calcola la percentuale OK sul totale OK + KO.
    """

    total = ok + ko

    if total == 0:
        return 0.0

    return round(
        ok / total * 100.0,
        4,
    )


def evaluate_signals(
    row: pd.Series,
) -> dict[str, bool]:
    """
    Valuta i segnali di rischio individuati dalle metriche.

    Ogni segnale è esplicito e modificabile separatamente.
    """

    ranking_gap = _num(
        row,
        "RankingGapScore",
    )

    home_ppg = _num(
        row,
        "HomePPGLast5",
    )

    worst_ppg = _num(
        row,
        "WorstPPGLast5",
    )

    home_wins = _num(
        row,
        "HomeWinsLast5",
    )

    home_restart_gf = _num(
        row,
        "HomeGFAvgSinceRestart",
    )

    return {
        "RankingGapHigh": (
            ranking_gap is not None
            and ranking_gap >= 4.0
        ),
        "HomePPGLow": (
            home_ppg is not None
            and home_ppg < 1.0
        ),
        "WorstPPGLow": (
            worst_ppg is not None
            and worst_ppg < 0.8
        ),
        "HomeWinsLow": (
            home_wins is not None
            and home_wins <= 1.0
        ),
        "HomeRestartGFLow": (
            home_restart_gf is not None
            and home_restart_gf < 1.2
        ),
        "HomeRestartNotReady": _flag(
            row,
            "HomeRestartNotReady",
        ),
        "BothTeamsRestartNotReady": _flag(
            row,
            "BothTeamsRestartNotReady",
        ),
    }


def build_profiles() -> list[AccumulationProfile]:
    """
    Crea profili con penalità cumulative progressivamente più severe.

    La baseline non modifica lo score.
    """

    return [
        AccumulationProfile(
            name="BASELINE",
            description=(
                "Score originale senza penalità cumulative"
            ),
            penalties={
                0: 0.0,
            },
        ),
        AccumulationProfile(
            name="ACCUMULATION_LIGHT",
            description=(
                "Penalità leggere solo da due segnali in poi"
            ),
            penalties={
                0: 0.0,
                1: 0.0,
                2: -1.0,
                3: -2.0,
                4: -3.0,
                5: -4.0,
                6: -5.0,
                7: -6.0,
            },
            minimum_signals=2,
        ),
        AccumulationProfile(
            name="ACCUMULATION_MEDIUM",
            description=(
                "Penalità medie da due segnali in poi"
            ),
            penalties={
                0: 0.0,
                1: 0.0,
                2: -2.0,
                3: -4.0,
                4: -6.0,
                5: -8.0,
                6: -10.0,
                7: -12.0,
            },
            minimum_signals=2,
        ),
        AccumulationProfile(
            name="ACCUMULATION_STRONG",
            description=(
                "Penalità forti da due segnali in poi"
            ),
            penalties={
                0: 0.0,
                1: 0.0,
                2: -3.0,
                3: -6.0,
                4: -9.0,
                5: -12.0,
                6: -15.0,
                7: -18.0,
            },
            minimum_signals=2,
        ),
        AccumulationProfile(
            name="THREE_SIGNALS_LIGHT",
            description=(
                "Nessuna penalità fino a due segnali; "
                "penalità leggere da tre segnali"
            ),
            penalties={
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: -2.0,
                4: -4.0,
                5: -6.0,
                6: -8.0,
                7: -10.0,
            },
            minimum_signals=3,
        ),
        AccumulationProfile(
            name="THREE_SIGNALS_MEDIUM",
            description=(
                "Nessuna penalità fino a due segnali; "
                "penalità medie da tre segnali"
            ),
            penalties={
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: -4.0,
                4: -7.0,
                5: -10.0,
                6: -13.0,
                7: -16.0,
            },
            minimum_signals=3,
        ),
        AccumulationProfile(
            name="THREE_SIGNALS_STRONG",
            description=(
                "Nessuna penalità fino a due segnali; "
                "penalità forti da tre segnali"
            ),
            penalties={
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: -6.0,
                4: -10.0,
                5: -14.0,
                6: -18.0,
                7: -22.0,
            },
            minimum_signals=3,
        ),
        AccumulationProfile(
            name="FOUR_SIGNALS_MEDIUM",
            description=(
                "Penalità solo quando si accumulano almeno quattro segnali"
            ),
            penalties={
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: -5.0,
                5: -8.0,
                6: -11.0,
                7: -14.0,
            },
            minimum_signals=4,
        ),
        AccumulationProfile(
            name="FOUR_SIGNALS_STRONG",
            description=(
                "Penalità forti solo da quattro segnali in poi"
            ),
            penalties={
                0: 0.0,
                1: 0.0,
                2: 0.0,
                3: 0.0,
                4: -8.0,
                5: -12.0,
                6: -16.0,
                7: -20.0,
            },
            minimum_signals=4,
        ),
    ]


def penalty_for_signal_count(
    profile: AccumulationProfile,
    signal_count: int,
) -> float:
    """
    Restituisce la penalità associata al numero di segnali.

    Se il numero supera l'ultima chiave disponibile, usa la penalità massima.
    """

    if signal_count in profile.penalties:
        return profile.penalties[
            signal_count
        ]

    maximum_key = max(
        profile.penalties
    )

    return profile.penalties[
        maximum_key
    ]


def summarize_profile(
    profile_rows: pd.DataFrame,
    profile: AccumulationProfile,
) -> dict:
    """
    Calcola le metriche riassuntive di un profilo.
    """

    summary = {
        "Profile": profile.name,
        "Description": profile.description,
        "MinimumSignals": profile.minimum_signals,
        "TotalMatches": len(profile_rows),
    }

    for band in (
        "ALTA",
        "MEDIA",
        "BASSA",
    ):
        rows = profile_rows[
            profile_rows["NewBand"] == band
        ]

        ok = int(
            (
                rows["Outcome"] == "OK"
            ).sum()
        )

        ko = int(
            (
                rows["Outcome"] == "KO"
            ).sum()
        )

        summary[
            f"{band}_OK"
        ] = ok

        summary[
            f"{band}_KO"
        ] = ko

        summary[
            f"{band}_Total"
        ] = ok + ko

        summary[
            f"{band}_Hit"
        ] = safe_rate(
            ok,
            ko,
        )

    original_alta = profile_rows[
        profile_rows["OriginalBand"]
        == "ALTA"
    ]

    summary["AltaKOAvoided"] = int(
        (
            (
                original_alta["Outcome"]
                == "KO"
            )
            & (
                original_alta["NewBand"]
                != "ALTA"
            )
        ).sum()
    )

    summary["AltaOKLost"] = int(
        (
            (
                original_alta["Outcome"]
                == "OK"
            )
            & (
                original_alta["NewBand"]
                != "ALTA"
            )
        ).sum()
    )

    summary["OKPromotedToAlta"] = int(
        (
            (
                profile_rows["Outcome"]
                == "OK"
            )
            & (
                profile_rows["OriginalBand"]
                != "ALTA"
            )
            & (
                profile_rows["NewBand"]
                == "ALTA"
            )
        ).sum()
    )

    summary["KOPromotedToAlta"] = int(
        (
            (
                profile_rows["Outcome"]
                == "KO"
            )
            & (
                profile_rows["OriginalBand"]
                != "ALTA"
            )
            & (
                profile_rows["NewBand"]
                == "ALTA"
            )
        ).sum()
    )

    summary["BandChanges"] = int(
        (
            profile_rows["OriginalBand"]
            != profile_rows["NewBand"]
        ).sum()
    )

    summary["Utility"] = (
        summary["AltaKOAvoided"] * 2
        + summary["OKPromotedToAlta"]
        - summary["AltaOKLost"]
        - summary["KOPromotedToAlta"] * 2
    )

    return summary


def main() -> None:
    """
    Esegue l'intero replay storico.
    """

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

    required_columns = {
        "MatchId",
        "Score",
        "Band",
        "Outcome",
        "LeagueId",
        "Home",
        "Away",
        "PredictionDate",
    }

    missing_columns = (
        required_columns
        - set(matches.columns)
    )

    if missing_columns:
        raise ValueError(
            "01_matches.csv non contiene: "
            + ", ".join(
                sorted(missing_columns)
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

    profiles = build_profiles()

    detail_rows = []

    for _, row in matches.iterrows():
        signals = evaluate_signals(
            row
        )

        active_signals = [
            name
            for name, active in signals.items()
            if active
        ]

        signal_count = len(
            active_signals
        )

        for profile in profiles:
            penalty = penalty_for_signal_count(
                profile,
                signal_count,
            )

            original_score = float(
                row["Score"]
            )

            new_score = round(
                original_score + penalty,
                4,
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
                    "OriginalScore": original_score,
                    "NewScore": new_score,
                    "ScoreDelta": penalty,
                    "OriginalBand": row["Band"],
                    "NewBand": band_from_score(
                        new_score
                    ),
                    "SignalCount": signal_count,
                    "ActiveSignals": " | ".join(
                        active_signals
                    ),
                }
            )

    details = pd.DataFrame(
        detail_rows
    )

    details.to_csv(
        OUTPUT_DIR
        / "04_match_details.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    summaries = []

    for profile in profiles:
        profile_rows = details[
            details["Profile"]
            == profile.name
        ]

        summaries.append(
            summarize_profile(
                profile_rows,
                profile,
            )
        )

    summary_df = pd.DataFrame(
        summaries
    )

    summary_df = summary_df.sort_values(
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

    summary_df.to_csv(
        OUTPUT_DIR
        / "01_profile_summary.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    baseline_rows = details[
        details["Profile"]
        == "BASELINE"
    ]

    signal_performance = (
        baseline_rows.groupby(
            [
                "SignalCount",
                "OriginalBand",
                "Outcome",
            ],
            dropna=False,
        )
        .size()
        .reset_index(
            name="Matches"
        )
    )

    signal_performance.to_csv(
        OUTPUT_DIR
        / "02_signal_count_performance.csv",
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
        OUTPUT_DIR
        / "03_band_transitions.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    summary_df.head(
        10
    ).to_csv(
        OUTPUT_DIR
        / "05_best_profiles.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        "Partite concluse analizzate: "
        f"{len(matches)}"
    )

    print(
        "Profili cumulativi testati: "
        f"{len(profiles)}"
    )

    print(
        f"Output: {OUTPUT_DIR}"
    )

    print()

    print(
        summary_df[
            [
                "Profile",
                "ALTA_OK",
                "ALTA_KO",
                "ALTA_Total",
                "ALTA_Hit",
                "AltaKOAvoided",
                "AltaOKLost",
                "BandChanges",
                "Utility",
            ]
        ]
        .head(
            10
        )
        .to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()
