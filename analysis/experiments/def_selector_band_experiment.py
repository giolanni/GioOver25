"""
GioOver2.5 - DEF selector band experiment
=========================================

SCOPO
-----
Verificare se la regola corrente di v20defselect/v20defplus:

    v20def = MEDIA-ALTA con score >= 71
    + v22def = ALTA
    + v25def = ALTA

sta usando davvero le fasce migliori di v22def e v25def.

Il punto chiave e' questo: la soglia ALTA di v22def/v25def e' >= 75,
ma quella soglia nasce dallo scoring generale e non e' mai stata ottimizzata
specificamente per il ruolo di "conferma" dentro v20defselect.

Questo esperimento mantiene FISSA la base v20def, per confrontare solo la
parte che ci interessa:

    BASE CANDIDATI = v20def MEDIA-ALTA con score >= 71

Su quei candidati testa poi:

1) SOGLIE MINIME indipendenti per v22def e v25def
   Esempio: v22def >= 73 e v25def >= 79.

2) FASCE A INTERVALLI di score, per scoprire eventuali sweet spot.
   Esempio: v22def 75-79.99 + v25def 80-84.99.

3) ROBUSTEZZA TEMPORALE train/test.
   Le configurazioni vengono ordinate usando la parte piu' vecchia dello
   storico (train) e poi misurate separatamente sulla parte piu' recente
   (test), per evitare di scegliere una soglia solo perche' fortunata sullo
   stesso campione usato per trovarla.

INPUT
-----
Usa gli storici ranking gia' prodotti:

    data/storico/ranking/v20def/storico_ranking_v20def.csv
    data/storico/ranking/v22def/storico_ranking_v22def.csv
    data/storico/ranking/v25def/storico_ranking_v25def.csv

Non ricalcola gli engine: analizza esattamente cio' che gli engine hanno
prodotto nel tempo.

PARAMETRI MODIFICABILI
----------------------
BASE_MIN_V20DEF_SCORE = 71.0
    Soglia attuale di v20defselect. Per questo esperimento resta 71 di default.

GRID_MIN_SCORE = 55
GRID_MAX_SCORE = 95
GRID_STEP = 1
    Range delle soglie minime da provare per v22def e v25def.

BAND_WIDTH = 5
    Ampiezza delle fasce a intervalli.

MIN_SAMPLE = 20
    Numero minimo consigliato di gare per considerare una configurazione
    abbastanza leggibile. Le configurazioni piu' piccole vengono comunque
    esportate, ma non entrano nella classifica principale se esistono
    configurazioni con campione >= MIN_SAMPLE.

TRAIN_RATIO = 0.70
    70% delle date piu' vecchie = train, 30% piu' recenti = test.

USO
---
Dalla root del progetto:

    python -m analysis.experiments.def_selector_band_experiment

Opzioni principali:

    --min-sample 15
    --grid-min 50
    --grid-max 95
    --grid-step 1
    --base-min 71
    --train-ratio 0.70

OUTPUT
------
Scrive in:

    analysis/experiments/def_selector_band/output/

File:
    threshold_grid.csv
    band_matrix.csv
    top_configs.csv
    monthly_top_configs.csv
    candidate_matches.csv
    summary.txt

IMPORTANTE
----------
Questo script NON modifica gli engine. Serve esclusivamente a decidere se la
regola v22def=ALTA + v25def=ALTA vada mantenuta oppure sostituita da soglie o
fasce piu' efficaci e stabili.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


# ---------------------------------------------------------------------------
# PARAMETRI PRINCIPALI - MODIFICABILI ANCHE DA RIGA DI COMANDO
# ---------------------------------------------------------------------------
BASE_MIN_V20DEF_SCORE = 71.0
GRID_MIN_SCORE = 55
GRID_MAX_SCORE = 95
GRID_STEP = 1
BAND_WIDTH = 5
MIN_SAMPLE = 20
TRAIN_RATIO = 0.70

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "analysis" / "experiments" / "def_selector_band" / "output"

INPUTS = {
    "v20def": ROOT / "data" / "storico" / "ranking" / "v20def" / "storico_ranking_v20def.csv",
    "v22def": ROOT / "data" / "storico" / "ranking" / "v22def" / "storico_ranking_v22def.csv",
    "v25def": ROOT / "data" / "storico" / "ranking" / "v25def" / "storico_ranking_v25def.csv",
}


@dataclass(frozen=True)
class MatchRow:
    match_date: str
    league_id: str
    home: str
    away: str
    score: float
    band: str
    over25: str
    hg: str
    ag: str

    @property
    def key(self) -> tuple[str, str, str, str]:
        return (self.match_date, self.league_id, self.home, self.away)

    @property
    def is_ok(self) -> bool:
        return self.over25 == "OK"

    @property
    def is_australia(self) -> bool:
        return self.league_id.upper().startswith("AUSTRALIA_")


@dataclass(frozen=True)
class Candidate:
    match_date: str
    league_id: str
    home: str
    away: str
    v20_score: float
    v20_band: str
    v22_score: float
    v22_band: str
    v25_score: float
    v25_band: str
    over25: str
    hg: str
    ag: str

    @property
    def is_ok(self) -> bool:
        return self.over25 == "OK"

    @property
    def is_australia(self) -> bool:
        return self.league_id.upper().startswith("AUSTRALIA_")


@dataclass(frozen=True)
class Stats:
    total: int
    ok: int
    ko: int
    pct: float


@dataclass(frozen=True)
class ConfigResult:
    v22_min: float
    v25_min: float
    all_stats: Stats
    no_au_stats: Stats
    train_stats: Stats
    test_stats: Stats


def _clean(value: object) -> str:
    return str(value or "").strip()


def _float(value: object) -> float | None:
    try:
        return float(_clean(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _norm_band(value: object) -> str:
    return _clean(value).upper()


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _read_engine(path: Path) -> dict[tuple[str, str, str, str], MatchRow]:
    if not path.exists():
        raise FileNotFoundError(f"Storico non trovato: {path}")

    rows: dict[tuple[str, str, str, str], MatchRow] = {}

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")

        required = {"MatchDate", "LeagueId", "Home", "Away", "Score", "Band", "Over25"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise KeyError(f"Colonne mancanti in {path}: {sorted(missing)}")

        for raw in reader:
            score = _float(raw.get("Score"))
            if score is None:
                continue

            match_date = _clean(raw.get("MatchDate"))
            league_id = _clean(raw.get("LeagueId"))
            home = _clean(raw.get("Home"))
            away = _clean(raw.get("Away"))
            over25 = _norm_band(raw.get("Over25"))
            status = _norm_band(raw.get("MatchStatus"))

            # Per il test servono solo gare con esito definitivo O2.5 leggibile.
            if not match_date or not league_id or not home or not away:
                continue
            if over25 not in {"OK", "KO"}:
                continue
            if status and status not in {"FINAL", "FT", "FINISHED"}:
                continue

            row = MatchRow(
                match_date=match_date,
                league_id=league_id,
                home=home,
                away=away,
                score=score,
                band=_norm_band(raw.get("Band")),
                over25=over25,
                hg=_clean(raw.get("HG")),
                ag=_clean(raw.get("AG")),
            )

            # In caso di duplicato storico, l'ultima occorrenza prevale.
            rows[row.key] = row

    return rows


def build_candidates(base_min: float) -> list[Candidate]:
    datasets = {name: _read_engine(path) for name, path in INPUTS.items()}

    common_keys = (
        set(datasets["v20def"])
        & set(datasets["v22def"])
        & set(datasets["v25def"])
    )

    candidates: list[Candidate] = []

    for key in common_keys:
        v20 = datasets["v20def"][key]
        v22 = datasets["v22def"][key]
        v25 = datasets["v25def"][key]

        # Questa e' intenzionalmente la stessa base di v20defselect.
        if v20.band != "MEDIA-ALTA":
            continue
        if v20.score < base_min:
            continue

        # Tutti e tre gli storici devono concordare sull'esito della partita.
        # Se non concordano, il record viene escluso dal test per evitare
        # contaminazioni dovute a storici non sincronizzati.
        if len({v20.over25, v22.over25, v25.over25}) != 1:
            continue

        candidates.append(
            Candidate(
                match_date=v20.match_date,
                league_id=v20.league_id,
                home=v20.home,
                away=v20.away,
                v20_score=v20.score,
                v20_band=v20.band,
                v22_score=v22.score,
                v22_band=v22.band,
                v25_score=v25.score,
                v25_band=v25.band,
                over25=v20.over25,
                hg=v20.hg,
                ag=v20.ag,
            )
        )

    candidates.sort(key=lambda r: (_parse_date(r.match_date), r.league_id, r.home, r.away))
    return candidates


def calc_stats(rows: Iterable[Candidate]) -> Stats:
    materialized = list(rows)
    total = len(materialized)
    ok = sum(1 for row in materialized if row.is_ok)
    ko = total - ok
    pct = (ok / total * 100.0) if total else 0.0
    return Stats(total=total, ok=ok, ko=ko, pct=pct)


def split_by_date(candidates: list[Candidate], train_ratio: float) -> tuple[set[str], set[str]]:
    dates = sorted({row.match_date for row in candidates})
    if len(dates) <= 1:
        return set(dates), set()

    cut = int(round(len(dates) * train_ratio))
    cut = max(1, min(cut, len(dates) - 1))
    return set(dates[:cut]), set(dates[cut:])


def select_threshold(candidates: Iterable[Candidate], v22_min: float, v25_min: float) -> list[Candidate]:
    return [
        row
        for row in candidates
        if row.v22_score >= v22_min and row.v25_score >= v25_min
    ]


def threshold_grid(
    candidates: list[Candidate],
    grid_min: int,
    grid_max: int,
    grid_step: int,
    train_dates: set[str],
    test_dates: set[str],
) -> list[ConfigResult]:
    results: list[ConfigResult] = []

    for v22_min in range(grid_min, grid_max + 1, grid_step):
        for v25_min in range(grid_min, grid_max + 1, grid_step):
            selected = select_threshold(candidates, v22_min, v25_min)
            no_au = [row for row in selected if not row.is_australia]
            train = [row for row in selected if row.match_date in train_dates]
            test = [row for row in selected if row.match_date in test_dates]

            results.append(
                ConfigResult(
                    v22_min=float(v22_min),
                    v25_min=float(v25_min),
                    all_stats=calc_stats(selected),
                    no_au_stats=calc_stats(no_au),
                    train_stats=calc_stats(train),
                    test_stats=calc_stats(test),
                )
            )

    return results


def _intervals(grid_min: int, grid_max: int, width: int) -> list[tuple[int, int]]:
    result = []
    start = grid_min
    while start <= grid_max:
        end = start + width - 1
        result.append((start, end))
        start += width
    return result


def band_matrix(candidates: list[Candidate], grid_min: int, grid_max: int, width: int) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    intervals = _intervals(grid_min, grid_max, width)

    for v22_lo, v22_hi in intervals:
        for v25_lo, v25_hi in intervals:
            selected = [
                row
                for row in candidates
                if v22_lo <= row.v22_score < (v22_hi + 1)
                and v25_lo <= row.v25_score < (v25_hi + 1)
            ]
            stats = calc_stats(selected)
            no_au = calc_stats(row for row in selected if not row.is_australia)

            output.append(
                {
                    "V22Range": f"{v22_lo}-{v22_hi}.99",
                    "V25Range": f"{v25_lo}-{v25_hi}.99",
                    "Total": stats.total,
                    "OK": stats.ok,
                    "KO": stats.ko,
                    "PctOK": round(stats.pct, 2),
                    "NoAUTotal": no_au.total,
                    "NoAUOK": no_au.ok,
                    "NoAUKO": no_au.ko,
                    "NoAUPctOK": round(no_au.pct, 2),
                }
            )

    return output


def _write_csv(path: Path, fieldnames: list[str], rows: Iterable[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def _config_row(result: ConfigResult) -> dict[str, object]:
    return {
        "V22Min": result.v22_min,
        "V25Min": result.v25_min,
        "Total": result.all_stats.total,
        "OK": result.all_stats.ok,
        "KO": result.all_stats.ko,
        "PctOK": round(result.all_stats.pct, 2),
        "NoAUTotal": result.no_au_stats.total,
        "NoAUOK": result.no_au_stats.ok,
        "NoAUKO": result.no_au_stats.ko,
        "NoAUPctOK": round(result.no_au_stats.pct, 2),
        "TrainTotal": result.train_stats.total,
        "TrainOK": result.train_stats.ok,
        "TrainKO": result.train_stats.ko,
        "TrainPctOK": round(result.train_stats.pct, 2),
        "TestTotal": result.test_stats.total,
        "TestOK": result.test_stats.ok,
        "TestKO": result.test_stats.ko,
        "TestPctOK": round(result.test_stats.pct, 2),
    }


def rank_configs(results: list[ConfigResult], min_sample: int) -> list[ConfigResult]:
    eligible = [row for row in results if row.all_stats.total >= min_sample]
    pool = eligible if eligible else [row for row in results if row.all_stats.total > 0]

    # Prima stabilita' out-of-sample, poi precisione complessiva, poi volume.
    # La precisione train non viene usata come criterio primario proprio per
    # ridurre il rischio di overfitting.
    return sorted(
        pool,
        key=lambda row: (
            row.test_stats.pct if row.test_stats.total else -1.0,
            row.all_stats.pct,
            row.no_au_stats.pct,
            row.all_stats.total,
        ),
        reverse=True,
    )


def monthly_rows(candidates: list[Candidate], configs: list[ConfigResult]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    months = sorted({row.match_date[:7] for row in candidates})

    for rank, config in enumerate(configs[:10], start=1):
        selected = select_threshold(candidates, config.v22_min, config.v25_min)
        for month in months:
            month_rows = [row for row in selected if row.match_date.startswith(month)]
            stats = calc_stats(month_rows)
            rows.append(
                {
                    "Rank": rank,
                    "V22Min": config.v22_min,
                    "V25Min": config.v25_min,
                    "Month": month,
                    "Total": stats.total,
                    "OK": stats.ok,
                    "KO": stats.ko,
                    "PctOK": round(stats.pct, 2),
                }
            )

    return rows


def write_outputs(
    candidates: list[Candidate],
    grid_results: list[ConfigResult],
    matrix_rows: list[dict[str, object]],
    ranked: list[ConfigResult],
    min_sample: int,
    train_dates: set[str],
    test_dates: set[str],
    base_min: float,
) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    candidate_rows = [
        {
            "MatchDate": row.match_date,
            "LeagueId": row.league_id,
            "Home": row.home,
            "Away": row.away,
            "V20DEFScore": row.v20_score,
            "V20DEFBand": row.v20_band,
            "V22DEFScore": row.v22_score,
            "V22DEFBand": row.v22_band,
            "V25DEFScore": row.v25_score,
            "V25DEFBand": row.v25_band,
            "HG": row.hg,
            "AG": row.ag,
            "Over25": row.over25,
            "Australia": "YES" if row.is_australia else "NO",
        }
        for row in candidates
    ]

    _write_csv(
        OUTPUT_DIR / "candidate_matches.csv",
        list(candidate_rows[0].keys()) if candidate_rows else [
            "MatchDate", "LeagueId", "Home", "Away", "V20DEFScore", "V20DEFBand",
            "V22DEFScore", "V22DEFBand", "V25DEFScore", "V25DEFBand", "HG", "AG",
            "Over25", "Australia"
        ],
        candidate_rows,
    )

    config_fields = [
        "V22Min", "V25Min", "Total", "OK", "KO", "PctOK",
        "NoAUTotal", "NoAUOK", "NoAUKO", "NoAUPctOK",
        "TrainTotal", "TrainOK", "TrainKO", "TrainPctOK",
        "TestTotal", "TestOK", "TestKO", "TestPctOK",
    ]

    _write_csv(
        OUTPUT_DIR / "threshold_grid.csv",
        config_fields,
        (_config_row(row) for row in grid_results),
    )

    _write_csv(
        OUTPUT_DIR / "top_configs.csv",
        ["Rank"] + config_fields,
        (
            {"Rank": rank, **_config_row(row)}
            for rank, row in enumerate(ranked[:100], start=1)
        ),
    )

    matrix_fields = [
        "V22Range", "V25Range", "Total", "OK", "KO", "PctOK",
        "NoAUTotal", "NoAUOK", "NoAUKO", "NoAUPctOK",
    ]
    _write_csv(OUTPUT_DIR / "band_matrix.csv", matrix_fields, matrix_rows)

    monthly = monthly_rows(candidates, ranked)
    _write_csv(
        OUTPUT_DIR / "monthly_top_configs.csv",
        ["Rank", "V22Min", "V25Min", "Month", "Total", "OK", "KO", "PctOK"],
        monthly,
    )

    baseline_selected = select_threshold(candidates, 75.0, 75.0)
    baseline_all = calc_stats(baseline_selected)
    baseline_no_au = calc_stats(row for row in baseline_selected if not row.is_australia)

    candidate_stats = calc_stats(candidates)
    best = ranked[0] if ranked else None

    lines = [
        "DEF SELECTOR BAND EXPERIMENT",
        "============================",
        "",
        f"Base candidati: v20def MEDIA-ALTA con score >= {base_min:.2f}",
        f"Candidati comuni con esito: {candidate_stats.total}",
        f"Esito candidati grezzi: {candidate_stats.ok} OK / {candidate_stats.ko} KO = {candidate_stats.pct:.2f}%",
        "",
        "BASELINE ATTUALE",
        "----------------",
        "Regola: v22def >= 75 (ALTA) + v25def >= 75 (ALTA)",
        f"Tutte le leghe: {baseline_all.ok}/{baseline_all.total} = {baseline_all.pct:.2f}%",
        f"Senza Australia: {baseline_no_au.ok}/{baseline_no_au.total} = {baseline_no_au.pct:.2f}%",
        "",
        f"Min sample classifica: {min_sample}",
        f"Date train: {min(train_dates) if train_dates else '-'} -> {max(train_dates) if train_dates else '-'}",
        f"Date test: {min(test_dates) if test_dates else '-'} -> {max(test_dates) if test_dates else '-'}",
        "",
    ]

    if best:
        lines.extend(
            [
                "MIGLIORE CONFIGURAZIONE SECONDO IL TEST TEMPORALE",
                "-------------------------------------------------",
                f"v22def >= {best.v22_min:.0f}",
                f"v25def >= {best.v25_min:.0f}",
                f"Overall: {best.all_stats.ok}/{best.all_stats.total} = {best.all_stats.pct:.2f}%",
                f"No AU: {best.no_au_stats.ok}/{best.no_au_stats.total} = {best.no_au_stats.pct:.2f}%",
                f"Train: {best.train_stats.ok}/{best.train_stats.total} = {best.train_stats.pct:.2f}%",
                f"Test: {best.test_stats.ok}/{best.test_stats.total} = {best.test_stats.pct:.2f}%",
                "",
            ]
        )

    lines.extend(
        [
            "LETTURA CORRETTA",
            "-----------------",
            "Una soglia migliore della baseline NON va adottata automaticamente.",
            "Va considerata interessante se mantiene un campione sufficiente e",
            "resta superiore o almeno stabile anche nel blocco temporale TEST.",
            "",
            "band_matrix.csv serve invece a capire se esistono sweet spot:",
            "potrebbe emergere, per esempio, che 80-84.99 funzioni meglio di 90+.",
        ]
    )

    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ottimizza le fasce v22def/v25def usate da v20defselect.")
    parser.add_argument("--base-min", type=float, default=BASE_MIN_V20DEF_SCORE)
    parser.add_argument("--grid-min", type=int, default=GRID_MIN_SCORE)
    parser.add_argument("--grid-max", type=int, default=GRID_MAX_SCORE)
    parser.add_argument("--grid-step", type=int, default=GRID_STEP)
    parser.add_argument("--band-width", type=int, default=BAND_WIDTH)
    parser.add_argument("--min-sample", type=int, default=MIN_SAMPLE)
    parser.add_argument("--train-ratio", type=float, default=TRAIN_RATIO)
    args = parser.parse_args()

    if args.grid_step <= 0:
        raise ValueError("--grid-step deve essere > 0")
    if args.band_width <= 0:
        raise ValueError("--band-width deve essere > 0")
    if args.grid_max < args.grid_min:
        raise ValueError("--grid-max deve essere >= --grid-min")
    if not 0.1 <= args.train_ratio <= 0.9:
        raise ValueError("--train-ratio deve essere compreso tra 0.1 e 0.9")

    candidates = build_candidates(args.base_min)
    if not candidates:
        raise RuntimeError(
            "Nessun candidato trovato. Verifica che gli storici v20def/v22def/v25def "
            "abbiano partite comuni con esito e che v20def contenga MEDIA-ALTA >= soglia."
        )

    train_dates, test_dates = split_by_date(candidates, args.train_ratio)

    grid_results = threshold_grid(
        candidates,
        args.grid_min,
        args.grid_max,
        args.grid_step,
        train_dates,
        test_dates,
    )
    matrix_rows = band_matrix(candidates, args.grid_min, args.grid_max, args.band_width)
    ranked = rank_configs(grid_results, args.min_sample)

    write_outputs(
        candidates,
        grid_results,
        matrix_rows,
        ranked,
        args.min_sample,
        train_dates,
        test_dates,
        args.base_min,
    )

    baseline = calc_stats(select_threshold(candidates, 75.0, 75.0))
    best = ranked[0] if ranked else None

    print("DEF selector band experiment completato")
    print(f"Candidati v20def: {len(candidates)}")
    print(f"Baseline 75/75: {baseline.ok}/{baseline.total} = {baseline.pct:.2f}%")
    if best:
        print(
            f"Top: v22def>={best.v22_min:.0f}, v25def>={best.v25_min:.0f} | "
            f"overall {best.all_stats.ok}/{best.all_stats.total}={best.all_stats.pct:.2f}% | "
            f"test {best.test_stats.ok}/{best.test_stats.total}={best.test_stats.pct:.2f}%"
        )
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
