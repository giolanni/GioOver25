"""
GioOver2.5 - Retroactive DEF band backtest

SCOPO
-----
Ricostruisce retroattivamente gli score che avrebbero prodotto v20def,
v22def e v25def su TUTTI i pronostici storici disponibili dei rispettivi
engine base (v20, v22, v25), anche prima della nascita degli engine DEF.

Il test NON parte da v20def >= 71 e NON assume che la fascia ALTA debba
iniziare a 71 o 75. Per ogni engine analizza l'intero spettro degli score e
calcola quali percentuali di OK avrebbe prodotto ogni possibile nuova soglia
ALTA.

ANTI-LEAKAGE
------------
La metrica Strong Defense viene ricostruita usando esclusivamente risultati
con MatchDate STRETTAMENTE precedente alla partita analizzata. Le partite
dello stesso giorno non vengono usate, perché non conosciamo l'ordine/orario
con sufficiente affidabilità.

REGOLE DEF RIPRODOTTE
---------------------
v20def:
    se almeno una squadra ha GA medio ultime 5 <= 1.60: -3 punti

v22def:
    se la squadra ospite ha GA medio ultime 5 <= 1.60: -13 punti

v25def:
    se la squadra ospite ha GA medio ultime 5 <= 1.60: -13 punti

Se una squadra non dispone di almeno 5 gare precedenti, il relativo GA Last5
è None e non attiva la penalità, come negli engine reali.

OUTPUT
------
analysis/experiments/def_retro_band/output/
    summary.txt
    all_retro_scores.csv
    new_alta_thresholds.csv
    score_buckets.csv
    top_thresholds.csv
    monthly_by_threshold.csv

ESECUZIONE
----------
python -m analysis.experiments.def_retro_band_backtest

Opzioni utili:
    --min-sample 20
    --threshold-min 0
    --threshold-max 100
    --threshold-step 1
    --bucket-size 5

NOTE DI LETTURA
---------------
- new_alta_thresholds.csv è il file principale: per ogni engine e per ogni
  soglia candidata mostra Tot, OK, KO e PercentOK, sia overall sia senza AU.
- score_buckets.csv serve a trovare eventuali sweet spot non monotoni.
- top_thresholds.csv NON decide automaticamente quale soglia adottare:
  ordina solo le soglie che superano il campione minimo.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

from gioover25.team_names import normalize_team_name


ROOT = Path(".")
RANKING_ROOT = ROOT / "data" / "storico" / "ranking"
RESULTS_ROOT = ROOT / "data" / "storico" / "risultati"
OUTPUT_DIR = ROOT / "analysis" / "experiments" / "def_retro_band" / "output"

ENGINE_RULES = {
    "v20def": {
        "base_engine": "v20",
        "rule": "AT_LEAST_ONE_STRONG",
        "defense_threshold": 1.60,
        "penalty": 3.0,
    },
    "v22def": {
        "base_engine": "v22",
        "rule": "AWAY_STRONG",
        "defense_threshold": 1.60,
        "penalty": 13.0,
    },
    "v25def": {
        "base_engine": "v25",
        "rule": "AWAY_STRONG",
        "defense_threshold": 1.60,
        "penalty": 13.0,
    },
}


@dataclass(frozen=True)
class TeamResult:
    match_date: date
    ga: int


def text(value) -> str:
    return str(value or "").strip()


def to_float(value, default=None):
    raw = text(value).replace(",", ".")
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def to_int(value, default=None):
    raw = text(value)
    if not raw:
        return default
    try:
        return int(float(raw.replace(",", ".")))
    except ValueError:
        return default


def parse_date(value) -> date | None:
    raw = text(value)
    if not raw:
        return None

    raw = raw[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if not reader.fieldnames:
            raise ValueError(f"Header assente: {path}")
        return list(reader)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = []
        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def effective_date(row: dict) -> str:
    return text(row.get("MatchDate")) or text(row.get("PredictionDate"))


def outcome_for(row: dict) -> str:
    for field in ("Outcome", "Over25"):
        value = text(row.get(field)).upper()
        if value in {"OK", "KO"}:
            return value
    goals = to_int(row.get("Goals"))
    if goals is not None:
        return "OK" if goals >= 3 else "KO"
    hg = to_int(row.get("HG"))
    ag = to_int(row.get("AG"))
    if hg is not None and ag is not None:
        return "OK" if hg + ag >= 3 else "KO"
    return ""


def match_key(row: dict):
    league_id = text(row.get("LeagueId"))
    return (
        effective_date(row),
        league_id,
        normalize_team_name(league_id, row.get("Home")),
        normalize_team_name(league_id, row.get("Away")),
    )


def ranking_path(engine: str) -> Path:
    return RANKING_ROOT / engine / f"storico_ranking_{engine}.csv"


def load_unique_predictions(engine: str) -> tuple[list[dict], int]:
    """Carica un pronostico per partita, preferendo la PredictionDate più antica."""
    rows = read_csv(ranking_path(engine))
    valid = []
    for row in rows:
        if outcome_for(row) not in {"OK", "KO"}:
            continue
        if to_float(row.get("Score")) is None:
            continue
        if parse_date(effective_date(row)) is None:
            continue
        valid.append(row)

    valid.sort(key=lambda r: (text(r.get("PredictionDate")) or "9999-99-99", effective_date(r)))
    unique = {}
    duplicates = 0
    for row in valid:
        key = match_key(row)
        if key in unique:
            duplicates += 1
            continue
        unique[key] = row

    output = list(unique.values())
    output.sort(key=lambda r: (effective_date(r), text(r.get("LeagueId")), text(r.get("Home")), text(r.get("Away"))))
    return output, duplicates


def load_results_index() -> dict[tuple[str, str], list[TeamResult]]:
    """Indicizza GA per squadra e LeagueId da tutti gli storici risultati."""
    index: dict[tuple[str, str], list[TeamResult]] = defaultdict(list)

    if not RESULTS_ROOT.exists():
        raise FileNotFoundError(f"Cartella risultati non trovata: {RESULTS_ROOT}")

    for path in sorted(RESULTS_ROOT.glob("*.csv")):
        league_from_file = path.stem
        try:
            rows = read_csv(path)
        except Exception as exc:
            print(f"[WARN] salto {path}: {exc}")
            continue

        for row in rows:
            match_date = parse_date(row.get("MatchDate"))
            hg = to_int(row.get("HG"))
            ag = to_int(row.get("AG"))
            if match_date is None or hg is None or ag is None:
                continue

            status = text(row.get("Status")).upper()
            if status and status not in {"FINAL", "FINISHED", "FT", "PLAYED", "OK"}:
                continue

            league_id = text(row.get("LeagueId")) or league_from_file
            home = normalize_team_name(league_id, row.get("Home"))
            away = normalize_team_name(league_id, row.get("Away"))
            if not home or not away:
                continue

            index[(league_id, home)].append(TeamResult(match_date, ag))
            index[(league_id, away)].append(TeamResult(match_date, hg))

    for values in index.values():
        values.sort(key=lambda item: item.match_date)
    return index


def source_league_for(row: dict, side: str) -> str:
    candidate = text(row.get(f"{side}SourceLeagueId"))
    return candidate or text(row.get("LeagueId"))


def last5_ga(
    results_index: dict[tuple[str, str], list[TeamResult]],
    league_id: str,
    team_name: str,
    before_date: date,
) -> float | None:
    normalized = normalize_team_name(league_id, team_name)
    games = [item for item in results_index.get((league_id, normalized), []) if item.match_date < before_date]
    if len(games) < 5:
        return None
    last = games[-5:]
    return round(sum(item.ga for item in last) / 5.0, 4)


def find_last5_ga(
    results_index: dict[tuple[str, str], list[TeamResult]],
    source_league: str,
    fallback_league: str,
    team_name: str,
    before_date: date,
) -> tuple[float | None, str]:
    value = last5_ga(results_index, source_league, team_name, before_date)
    if value is not None:
        return value, source_league
    if fallback_league != source_league:
        value = last5_ga(results_index, fallback_league, team_name, before_date)
        if value is not None:
            return value, fallback_league
    return None, source_league


def retro_score(engine: str, base_score: float, home_ga: float | None, away_ga: float | None) -> tuple[float, bool]:
    cfg = ENGINE_RULES[engine]
    threshold = cfg["defense_threshold"]

    if cfg["rule"] == "AT_LEAST_ONE_STRONG":
        active = (home_ga is not None and home_ga <= threshold) or (away_ga is not None and away_ga <= threshold)
    elif cfg["rule"] == "AWAY_STRONG":
        active = away_ga is not None and away_ga <= threshold
    else:
        raise ValueError(f"Regola DEF sconosciuta: {cfg['rule']}")

    score = max(0.0, round(base_score - (cfg["penalty"] if active else 0.0), 2))
    return score, active


def build_retro_dataset(results_index) -> tuple[list[dict], dict]:
    all_rows = []
    stats = {}

    for def_engine, cfg in ENGINE_RULES.items():
        base_engine = cfg["base_engine"]
        predictions, duplicate_count = load_unique_predictions(base_engine)
        missing_home = 0
        missing_away = 0

        for row in predictions:
            match_date = parse_date(effective_date(row))
            if match_date is None:
                continue

            league_id = text(row.get("LeagueId"))
            home_source = source_league_for(row, "Home")
            away_source = source_league_for(row, "Away")

            home_ga, home_used_league = find_last5_ga(
                results_index, home_source, league_id, text(row.get("Home")), match_date
            )
            away_ga, away_used_league = find_last5_ga(
                results_index, away_source, league_id, text(row.get("Away")), match_date
            )

            if home_ga is None:
                missing_home += 1
            if away_ga is None:
                missing_away += 1

            base_score = float(to_float(row.get("Score"), 0.0))
            score, penalty_active = retro_score(def_engine, base_score, home_ga, away_ga)
            outcome = outcome_for(row)

            all_rows.append({
                "Engine": def_engine,
                "BaseEngine": base_engine,
                "PredictionDate": text(row.get("PredictionDate")),
                "MatchDate": effective_date(row),
                "LeagueId": league_id,
                "Round": text(row.get("Round")),
                "Home": text(row.get("Home")),
                "Away": text(row.get("Away")),
                "Outcome": outcome,
                "BaseScore": f"{base_score:.2f}",
                "BaseBand": text(row.get("Band")),
                "HomeGALast5": "" if home_ga is None else f"{home_ga:.4f}",
                "AwayGALast5": "" if away_ga is None else f"{away_ga:.4f}",
                "HomeHistoryLeagueId": home_used_league,
                "AwayHistoryLeagueId": away_used_league,
                "DefensePenaltyActive": int(penalty_active),
                "DefensePenalty": f"{cfg['penalty'] if penalty_active else 0.0:.2f}",
                "RetroDEFScore": f"{score:.2f}",
                "Australia": int(league_id.startswith("Australia_")),
            })

        stats[def_engine] = {
            "base_engine": base_engine,
            "predictions": len(predictions),
            "duplicates_removed": duplicate_count,
            "home_last5_missing": missing_home,
            "away_last5_missing": missing_away,
        }

    all_rows.sort(key=lambda r: (r["Engine"], r["MatchDate"], r["LeagueId"], r["Home"], r["Away"]))
    return all_rows, stats


def pct(ok: int, total: int) -> float:
    return round(ok * 100.0 / total, 2) if total else 0.0


def evaluate(rows: Iterable[dict]) -> tuple[int, int, int, float]:
    rows = list(rows)
    total = len(rows)
    ok = sum(1 for row in rows if row["Outcome"] == "OK")
    ko = total - ok
    return total, ok, ko, pct(ok, total)


def score_value(row: dict) -> float:
    return float(row["RetroDEFScore"])


def wilson_lower(ok: int, total: int, z: float = 1.96) -> float:
    if total <= 0:
        return 0.0
    phat = ok / total
    denominator = 1 + z * z / total
    centre = phat + z * z / (2 * total)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
    return (centre - margin) / denominator


def threshold_rows(dataset: list[dict], tmin: float, tmax: float, step: float) -> list[dict]:
    output = []
    thresholds = []
    value = tmin
    while value <= tmax + 1e-9:
        thresholds.append(round(value, 4))
        value += step

    for engine in ENGINE_RULES:
        engine_rows = [r for r in dataset if r["Engine"] == engine]
        for threshold in thresholds:
            selected = [r for r in engine_rows if score_value(r) >= threshold]
            selected_no_au = [r for r in selected if r["Australia"] == 0]
            total, ok, ko, rate = evaluate(selected)
            total_no_au, ok_no_au, ko_no_au, rate_no_au = evaluate(selected_no_au)
            output.append({
                "Engine": engine,
                "NewAltaThreshold": f"{threshold:.2f}",
                "Tot": total,
                "OK": ok,
                "KO": ko,
                "PercentOK": f"{rate:.2f}",
                "WilsonLower95": f"{wilson_lower(ok, total) * 100:.2f}",
                "TotNoAU": total_no_au,
                "OKNoAU": ok_no_au,
                "KONoAU": ko_no_au,
                "PercentOKNoAU": f"{rate_no_au:.2f}",
                "WilsonLower95NoAU": f"{wilson_lower(ok_no_au, total_no_au) * 100:.2f}",
            })
    return output


def bucket_rows(dataset: list[dict], bucket_size: float) -> list[dict]:
    output = []
    for engine in ENGINE_RULES:
        rows = [r for r in dataset if r["Engine"] == engine]
        max_score = max([score_value(r) for r in rows], default=100.0)
        upper_limit = max(100.0, math.ceil(max_score / bucket_size) * bucket_size)
        low = 0.0
        while low < upper_limit:
            high = low + bucket_size
            selected = [r for r in rows if low <= score_value(r) < high]
            selected_no_au = [r for r in selected if r["Australia"] == 0]
            total, ok, ko, rate = evaluate(selected)
            total_no_au, ok_no_au, ko_no_au, rate_no_au = evaluate(selected_no_au)
            output.append({
                "Engine": engine,
                "ScoreFrom": f"{low:.2f}",
                "ScoreToExclusive": f"{high:.2f}",
                "Tot": total,
                "OK": ok,
                "KO": ko,
                "PercentOK": f"{rate:.2f}",
                "TotNoAU": total_no_au,
                "OKNoAU": ok_no_au,
                "KONoAU": ko_no_au,
                "PercentOKNoAU": f"{rate_no_au:.2f}",
            })
            low = high
    return output


def monthly_threshold_rows(dataset: list[dict], thresholds: list[float]) -> list[dict]:
    output = []
    for engine in ENGINE_RULES:
        rows = [r for r in dataset if r["Engine"] == engine]
        months = sorted({r["MatchDate"][:7] for r in rows if len(r["MatchDate"]) >= 7})
        for threshold in thresholds:
            for month in months:
                selected = [r for r in rows if r["MatchDate"].startswith(month) and score_value(r) >= threshold]
                total, ok, ko, rate = evaluate(selected)
                output.append({
                    "Engine": engine,
                    "Threshold": f"{threshold:.2f}",
                    "Month": month,
                    "Tot": total,
                    "OK": ok,
                    "KO": ko,
                    "PercentOK": f"{rate:.2f}",
                })
    return output


def best_thresholds(threshold_data: list[dict], min_sample: int) -> list[dict]:
    output = []
    for engine in ENGINE_RULES:
        candidates = [
            row for row in threshold_data
            if row["Engine"] == engine and int(row["Tot"]) >= min_sample
        ]
        # Prima robustezza statistica (Wilson), poi % OK, poi copertura.
        candidates.sort(
            key=lambda r: (
                float(r["WilsonLower95"]),
                float(r["PercentOK"]),
                int(r["Tot"]),
                -float(r["NewAltaThreshold"]),
            ),
            reverse=True,
        )
        for rank, row in enumerate(candidates[:20], start=1):
            copy = dict(row)
            copy["Rank"] = rank
            output.append(copy)
    return output


def threshold_lookup(threshold_data: list[dict], engine: str, threshold: float) -> dict | None:
    for row in threshold_data:
        if row["Engine"] == engine and abs(float(row["NewAltaThreshold"]) - threshold) < 1e-9:
            return row
    return None


def write_summary(dataset, stats, threshold_data, top_data, args) -> None:
    lines = [
        "RETROACTIVE DEF BAND BACKTEST",
        "============================",
        "",
        "Obiettivo: simulare v20def, v22def e v25def su tutti i pronostici",
        "storici dei rispettivi engine base, senza imporre a priori 71 o 75.",
        "",
        "ANTI-LEAKAGE",
        "------------",
        "Strong Defense usa solo partite con data strettamente precedente.",
        "",
    ]

    for engine, cfg in ENGINE_RULES.items():
        rows = [r for r in dataset if r["Engine"] == engine]
        total, ok, ko, rate = evaluate(rows)
        penalty_count = sum(int(r["DefensePenaltyActive"]) for r in rows)
        st = stats[engine]
        lines.extend([
            engine.upper(),
            "-" * len(engine),
            f"Base: {cfg['base_engine']}",
            f"Pronostici unici con esito: {total}",
            f"Esito intero universo: {ok}/{total} = {rate:.2f}% (KO {ko})",
            f"Penalità DEF attiva: {penalty_count}/{total}",
            f"Duplicati storici rimossi: {st['duplicates_removed']}",
            f"Home GA Last5 non disponibile: {st['home_last5_missing']}",
            f"Away GA Last5 non disponibile: {st['away_last5_missing']}",
            "",
            "Confronto soglie ALTA:",
        ])

        for threshold in (60.0, 65.0, 70.0, 71.0, 72.0, 73.0, 74.0, 75.0, 80.0, 85.0, 90.0):
            row = threshold_lookup(threshold_data, engine, threshold)
            if row:
                lines.append(
                    f"  >= {threshold:>5.1f}: {row['OK']}/{row['Tot']} = {row['PercentOK']}% "
                    f"| no AU {row['OKNoAU']}/{row['TotNoAU']} = {row['PercentOKNoAU']}%"
                )

        tops = [r for r in top_data if r["Engine"] == engine]
        lines.append("")
        if tops:
            best = tops[0]
            lines.extend([
                f"Migliore soglia robusta (min sample {args.min_sample}, ordinata per Wilson 95%):",
                f"  >= {best['NewAltaThreshold']}: {best['OK']}/{best['Tot']} = {best['PercentOK']}%",
                f"  senza AU: {best['OKNoAU']}/{best['TotNoAU']} = {best['PercentOKNoAU']}%",
            ])
        else:
            lines.append(f"Nessuna soglia raggiunge min sample {args.min_sample}.")
        lines.append("")

    lines.extend([
        "LETTURA",
        "-------",
        "new_alta_thresholds.csv contiene la percentuale OK di OGNI nuova ALTA.",
        "score_buckets.csv mostra eventuali sweet spot per intervallo di score.",
        "top_thresholds.csv usa Wilson 95% per evitare di premiare troppo campioni piccoli.",
        "Nessuna soglia deve essere adottata automaticamente: va valutata anche la",
        "stabilità mensile e la copertura rispetto alla soglia attuale >=75.",
    ])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest retroattivo delle fasce v20def/v22def/v25def")
    parser.add_argument("--min-sample", type=int, default=20)
    parser.add_argument("--threshold-min", type=float, default=0.0)
    parser.add_argument("--threshold-max", type=float, default=100.0)
    parser.add_argument("--threshold-step", type=float, default=1.0)
    parser.add_argument("--bucket-size", type=float, default=5.0)
    args = parser.parse_args()

    if args.threshold_step <= 0:
        raise ValueError("--threshold-step deve essere > 0")
    if args.bucket_size <= 0:
        raise ValueError("--bucket-size deve essere > 0")
    if args.threshold_max < args.threshold_min:
        raise ValueError("--threshold-max deve essere >= --threshold-min")

    print("[1/6] Carico e indicizzo gli storici risultati...")
    results_index = load_results_index()

    print("[2/6] Ricostruisco gli score DEF retroattivi...")
    dataset, stats = build_retro_dataset(results_index)

    print("[3/6] Calcolo tutte le possibili nuove soglie ALTA...")
    thresholds = threshold_rows(dataset, args.threshold_min, args.threshold_max, args.threshold_step)

    print("[4/6] Calcolo bucket/sweet spot...")
    buckets = bucket_rows(dataset, args.bucket_size)
    tops = best_thresholds(thresholds, args.min_sample)

    chosen_thresholds = sorted({75.0} | {
        float(row["NewAltaThreshold"])
        for row in tops
        if int(row.get("Rank", 999)) <= 5
    })
    monthly = monthly_threshold_rows(dataset, chosen_thresholds)

    print("[5/6] Scrivo i report...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "all_retro_scores.csv", dataset)
    write_csv(OUTPUT_DIR / "new_alta_thresholds.csv", thresholds)
    write_csv(OUTPUT_DIR / "score_buckets.csv", buckets)
    write_csv(OUTPUT_DIR / "top_thresholds.csv", tops)
    write_csv(OUTPUT_DIR / "monthly_by_threshold.csv", monthly)
    write_summary(dataset, stats, thresholds, tops, args)

    print("[6/6] Completato.")
    print(f"Output: {OUTPUT_DIR}")
    print("File principale: new_alta_thresholds.csv")
    print("Sintesi: summary.txt")


if __name__ == "__main__":
    main()
