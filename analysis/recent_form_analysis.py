"""
===============================================================================
GioOver2.5 - recent_form_analysis.py
===============================================================================

SCOPO
-----
Verificare se una bassa forma di risultato nelle ultime 5 partite, misurata
tramite punti per partita (PPG), è associata a una maggiore frequenza di KO
nelle fasce ALTA e MEDIA del motore v25.

Lo script NON modifica alcun engine e NON modifica gli storici.

INPUT PREDEFINITI
-----------------
    analysis/laboratory/data/01_matches.csv
    data/storico/risultati/*.csv

OUTPUT
------
    analysis/recent_form/data/01_recent_form_matches.csv
    analysis/recent_form/data/02_recent_form_summary.csv
    analysis/recent_form/data/03_recent_form_penalty_simulation.csv

ESECUZIONE
----------
    python -m analysis.recent_form_analysis

Opzioni principali:
    --engine-version 2.5.0
    --last-n 5
    --include-australia
===============================================================================
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MATCHES_FILE = PROJECT_ROOT / "analysis/laboratory/data/01_matches.csv"
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "data/storico/risultati"
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "analysis/recent_form/data"


DETAIL_FIELDS = [
    "MatchId", "PredictionDate", "MatchDate", "LeagueId", "Round",
    "Home", "Away", "Score", "Band", "Outcome", "HG", "AG", "Goals",
    "AlgorithmVersion", "ResolvedResultFile", "ResolvedMatchDate",
    "HomeRecentMatches", "HomeRecentPoints", "HomeRecentPPG5",
    "HomeRecentWins5", "HomeRecentDraws5", "HomeRecentLosses5",
    "HomeRecentGF5", "HomeRecentGA5", "HomeRecentOver25Rate5",
    "AwayRecentMatches", "AwayRecentPoints", "AwayRecentPPG5",
    "AwayRecentWins5", "AwayRecentDraws5", "AwayRecentLosses5",
    "AwayRecentGF5", "AwayRecentGA5", "AwayRecentOver25Rate5",
    "WorstRecentPPG5", "AverageRecentPPG5", "BothBelow080",
    "BothWinless5", "RecentFormBucket", "ProposedPenalty",
    "SimulatedScore", "SimulatedBand", "WouldLeaveAlta",
]

SUMMARY_FIELDS = [
    "Population", "RecentFormBucket", "Matches", "OK", "KO",
    "SuccessRate", "AverageOriginalScore", "AveragePenalty",
    "WouldLeaveAlta", "OKLostFromAlta", "KORemovedFromAlta",
]

PENALTY_SUMMARY_FIELDS = [
    "Population", "Matches", "OriginalOK", "OriginalKO",
    "OriginalSuccessRate", "SimulatedAltaMatches", "SimulatedAltaOK",
    "SimulatedAltaKO", "SimulatedAltaSuccessRate", "OKLostFromAlta",
    "KORemovedFromAlta", "NetKOAdvantage",
]


@dataclass(frozen=True)
class ResultRow:
    match_date: date
    home: str
    away: str
    home_goals: int
    away_goals: int


@dataclass(frozen=True)
class RecentForm:
    matches: int
    points: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    over25: int

    @property
    def ppg(self) -> float:
        return self.points / self.matches if self.matches else 0.0

    @property
    def over25_rate(self) -> float:
        return self.over25 / self.matches if self.matches else 0.0


def _text(value: object) -> str:
    return str(value or "").strip()


def _normalize(value: object) -> str:
    return " ".join(_text(value).casefold().split())


def _parse_date(value: object) -> date | None:
    raw = _text(value)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _to_int(value: object) -> int | None:
    raw = _text(value)
    if not raw:
        return None
    try:
        return int(float(raw.replace(",", ".")))
    except ValueError:
        return None


def _to_float(value: object) -> float:
    raw = _text(value).replace(",", ".")
    try:
        return float(raw) if raw else 0.0
    except ValueError:
        return 0.0


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def _write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _league_id_variants(league_id: str) -> list[str]:
    """Supporta sia il vecchio formato con anno sia quello seasonless."""
    variants = [league_id]
    parts = league_id.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit() and len(parts[1]) == 4:
        variants.append(parts[0])
    return list(dict.fromkeys(variants))


def _find_results_file(results_dir: Path, league_id: str) -> Path | None:
    for variant in _league_id_variants(league_id):
        candidate = results_dir / f"{variant}.csv"
        if candidate.exists():
            return candidate

    # Compatibilità inversa: ranking seasonless ma file non ancora migrato.
    candidates = sorted(results_dir.glob(f"{league_id}_20[0-9][0-9].csv"))
    return candidates[-1] if candidates else None


def _load_results(path: Path) -> list[ResultRow]:
    rows = _read_csv(path)
    results: list[ResultRow] = []

    for row in rows:
        match_date = _parse_date(row.get("Date") or row.get("MatchDate"))
        hg = _to_int(row.get("HG"))
        ag = _to_int(row.get("AG"))
        home = _text(row.get("Home"))
        away = _text(row.get("Away"))

        if match_date is None or hg is None or ag is None or not home or not away:
            continue

        results.append(ResultRow(match_date, home, away, hg, ag))

    results.sort(key=lambda item: item.match_date)
    return results


def _resolve_target_match(row: dict[str, str], results: list[ResultRow]) -> ResultRow | None:
    home = _normalize(row.get("Home"))
    away = _normalize(row.get("Away"))
    hg = _to_int(row.get("HG"))
    ag = _to_int(row.get("AG"))
    explicit_date = _parse_date(row.get("MatchDate"))
    prediction_date = _parse_date(row.get("PredictionDate"))

    candidates = [
        match
        for match in results
        if _normalize(match.home) == home and _normalize(match.away) == away
    ]

    if hg is not None and ag is not None:
        scored_candidates = [
            match for match in candidates
            if match.home_goals == hg and match.away_goals == ag
        ]
        if scored_candidates:
            candidates = scored_candidates

    if explicit_date is not None:
        exact = [match for match in candidates if match.match_date == explicit_date]
        if len(exact) == 1:
            return exact[0]

    if not candidates:
        return None

    reference = explicit_date or prediction_date
    if reference is None:
        return candidates[-1] if len(candidates) == 1 else None

    candidates.sort(key=lambda match: abs((match.match_date - reference).days))
    if len(candidates) > 1:
        first_distance = abs((candidates[0].match_date - reference).days)
        second_distance = abs((candidates[1].match_date - reference).days)
        if first_distance == second_distance:
            return None

    return candidates[0]


def _recent_form(
    results: list[ResultRow],
    team: str,
    before_date: date,
    last_n: int,
) -> RecentForm:
    normalized_team = _normalize(team)
    previous = [
        match
        for match in results
        if match.match_date < before_date
        and normalized_team in {_normalize(match.home), _normalize(match.away)}
    ][-last_n:]

    points = wins = draws = losses = goals_for = goals_against = over25 = 0

    for match in previous:
        is_home = _normalize(match.home) == normalized_team
        gf = match.home_goals if is_home else match.away_goals
        ga = match.away_goals if is_home else match.home_goals

        goals_for += gf
        goals_against += ga
        over25 += int(gf + ga >= 3)

        if gf > ga:
            wins += 1
            points += 3
        elif gf == ga:
            draws += 1
            points += 1
        else:
            losses += 1

    return RecentForm(
        matches=len(previous),
        points=points,
        wins=wins,
        draws=draws,
        losses=losses,
        goals_for=goals_for,
        goals_against=goals_against,
        over25=over25,
    )


def _bucket(worst_ppg: float) -> str:
    if worst_ppg < 0.40:
        return "<0.40"
    if worst_ppg < 0.80:
        return "0.40-0.79"
    if worst_ppg < 1.20:
        return "0.80-1.19"
    return ">=1.20"


def _proposed_penalty(home: RecentForm, away: RecentForm) -> int:
    if home.matches < 3 or away.matches < 3:
        return 0

    worst = min(home.ppg, away.ppg)

    if worst < 0.40:
        penalty = 3
    elif worst < 0.80:
        penalty = 2
    elif worst < 1.20:
        penalty = 1
    else:
        penalty = 0

    if home.ppg < 0.80 and away.ppg < 0.80:
        penalty += 1

    return min(penalty, 4)


def _band_from_score(score: float) -> str:
    # Soglie ricavate dagli engine correnti. La simulazione interessa
    # principalmente l'uscita dalla fascia ALTA.
    if score >= 75:
        return "ALTA"
    if score >= 60:
        return "MEDIA"
    return "BASSA"


def _build_details(
    matches_file: Path,
    results_dir: Path,
    engine_version: str,
    last_n: int,
    include_australia: bool,
) -> tuple[list[dict], int]:
    source_rows = _read_csv(matches_file)
    cache: dict[Path, list[ResultRow]] = {}
    details: list[dict] = []
    unresolved = 0

    for row in source_rows:
        if _text(row.get("Band")).upper() not in {"ALTA", "MEDIA"}:
            continue
        if _text(row.get("Outcome")).upper() not in {"OK", "KO"}:
            continue
        if engine_version and _text(row.get("AlgorithmVersion")) != engine_version:
            continue

        league_id = _text(row.get("LeagueId"))
        if not include_australia and league_id.startswith("Australia_"):
            continue

        results_file = _find_results_file(results_dir, league_id)
        if results_file is None:
            unresolved += 1
            continue

        results = cache.setdefault(results_file, _load_results(results_file))
        target = _resolve_target_match(row, results)
        if target is None:
            unresolved += 1
            continue

        home_form = _recent_form(results, row.get("Home", ""), target.match_date, last_n)
        away_form = _recent_form(results, row.get("Away", ""), target.match_date, last_n)

        # Escludiamo dal test principale i campioni troppo piccoli.
        if home_form.matches < 3 or away_form.matches < 3:
            unresolved += 1
            continue

        worst_ppg = min(home_form.ppg, away_form.ppg)
        avg_ppg = (home_form.ppg + away_form.ppg) / 2
        penalty = _proposed_penalty(home_form, away_form)
        original_score = _to_float(row.get("Score"))
        simulated_score = max(0.0, original_score - penalty)
        original_band = _text(row.get("Band")).upper()
        simulated_band = _band_from_score(simulated_score)
        would_leave_alta = original_band == "ALTA" and simulated_band != "ALTA"

        details.append({
            **row,
            "ResolvedResultFile": str(results_file.relative_to(PROJECT_ROOT)),
            "ResolvedMatchDate": target.match_date.isoformat(),
            "HomeRecentMatches": home_form.matches,
            "HomeRecentPoints": home_form.points,
            "HomeRecentPPG5": f"{home_form.ppg:.4f}",
            "HomeRecentWins5": home_form.wins,
            "HomeRecentDraws5": home_form.draws,
            "HomeRecentLosses5": home_form.losses,
            "HomeRecentGF5": home_form.goals_for,
            "HomeRecentGA5": home_form.goals_against,
            "HomeRecentOver25Rate5": f"{home_form.over25_rate:.4f}",
            "AwayRecentMatches": away_form.matches,
            "AwayRecentPoints": away_form.points,
            "AwayRecentPPG5": f"{away_form.ppg:.4f}",
            "AwayRecentWins5": away_form.wins,
            "AwayRecentDraws5": away_form.draws,
            "AwayRecentLosses5": away_form.losses,
            "AwayRecentGF5": away_form.goals_for,
            "AwayRecentGA5": away_form.goals_against,
            "AwayRecentOver25Rate5": f"{away_form.over25_rate:.4f}",
            "WorstRecentPPG5": f"{worst_ppg:.4f}",
            "AverageRecentPPG5": f"{avg_ppg:.4f}",
            "BothBelow080": int(home_form.ppg < 0.80 and away_form.ppg < 0.80),
            "BothWinless5": int(home_form.wins == 0 and away_form.wins == 0),
            "RecentFormBucket": _bucket(worst_ppg),
            "ProposedPenalty": penalty,
            "SimulatedScore": f"{simulated_score:.2f}",
            "SimulatedBand": simulated_band,
            "WouldLeaveAlta": int(would_leave_alta),
        })

    return details, unresolved


def _aggregate(details: list[dict]) -> list[dict]:
    populations = ["ALTA", "MEDIA", "ALL"]
    buckets = ["<0.40", "0.40-0.79", "0.80-1.19", ">=1.20", "ALL"]
    summary: list[dict] = []

    for population in populations:
        population_rows = [
            row for row in details
            if population == "ALL" or _text(row.get("Band")).upper() == population
        ]

        for bucket in buckets:
            rows = [
                row for row in population_rows
                if bucket == "ALL" or row.get("RecentFormBucket") == bucket
            ]
            if not rows:
                continue

            ok = sum(_text(row.get("Outcome")).upper() == "OK" for row in rows)
            ko = len(rows) - ok
            original_alta = [row for row in rows if _text(row.get("Band")).upper() == "ALTA"]
            leaving = [row for row in original_alta if int(row.get("WouldLeaveAlta", 0)) == 1]

            summary.append({
                "Population": population,
                "RecentFormBucket": bucket,
                "Matches": len(rows),
                "OK": ok,
                "KO": ko,
                "SuccessRate": f"{ok / len(rows):.4f}",
                "AverageOriginalScore": f"{sum(_to_float(r.get('Score')) for r in rows) / len(rows):.2f}",
                "AveragePenalty": f"{sum(_to_float(r.get('ProposedPenalty')) for r in rows) / len(rows):.2f}",
                "WouldLeaveAlta": len(leaving),
                "OKLostFromAlta": sum(_text(r.get("Outcome")).upper() == "OK" for r in leaving),
                "KORemovedFromAlta": sum(_text(r.get("Outcome")).upper() == "KO" for r in leaving),
            })

    return summary


def _penalty_summary(details: list[dict]) -> list[dict]:
    rows_out: list[dict] = []

    for population in ["ALTA", "ALTA_NO_AUSTRALIA"]:
        rows = [row for row in details if _text(row.get("Band")).upper() == "ALTA"]
        if population.endswith("NO_AUSTRALIA"):
            rows = [row for row in rows if not _text(row.get("LeagueId")).startswith("Australia_")]
        if not rows:
            continue

        original_ok = sum(_text(row.get("Outcome")).upper() == "OK" for row in rows)
        original_ko = len(rows) - original_ok
        kept = [row for row in rows if _text(row.get("SimulatedBand")).upper() == "ALTA"]
        kept_ok = sum(_text(row.get("Outcome")).upper() == "OK" for row in kept)
        kept_ko = len(kept) - kept_ok
        lost = [row for row in rows if _text(row.get("SimulatedBand")).upper() != "ALTA"]
        ok_lost = sum(_text(row.get("Outcome")).upper() == "OK" for row in lost)
        ko_removed = sum(_text(row.get("Outcome")).upper() == "KO" for row in lost)

        rows_out.append({
            "Population": population,
            "Matches": len(rows),
            "OriginalOK": original_ok,
            "OriginalKO": original_ko,
            "OriginalSuccessRate": f"{original_ok / len(rows):.4f}",
            "SimulatedAltaMatches": len(kept),
            "SimulatedAltaOK": kept_ok,
            "SimulatedAltaKO": kept_ko,
            "SimulatedAltaSuccessRate": f"{kept_ok / len(kept):.4f}" if kept else "",
            "OKLostFromAlta": ok_lost,
            "KORemovedFromAlta": ko_removed,
            "NetKOAdvantage": ko_removed - ok_lost,
        })

    return rows_out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analizza la relazione tra forma recente e risultati Over 2.5."
    )
    parser.add_argument("--matches-file", type=Path, default=DEFAULT_MATCHES_FILE)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_RESULTS_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--engine-version", default="2.5.0")
    parser.add_argument("--last-n", type=int, default=5)
    parser.add_argument("--include-australia", action="store_true")
    args = parser.parse_args()

    if args.last_n < 1:
        raise ValueError("--last-n deve essere almeno 1")
    if not args.matches_file.exists():
        raise FileNotFoundError(f"File Laboratory non trovato: {args.matches_file}")
    if not args.results_dir.exists():
        raise FileNotFoundError(f"Cartella risultati non trovata: {args.results_dir}")

    details, unresolved = _build_details(
        matches_file=args.matches_file,
        results_dir=args.results_dir,
        engine_version=args.engine_version,
        last_n=args.last_n,
        include_australia=args.include_australia,
    )
    summary = _aggregate(details)
    simulation = _penalty_summary(details)

    detail_path = args.output_dir / "01_recent_form_matches.csv"
    summary_path = args.output_dir / "02_recent_form_summary.csv"
    simulation_path = args.output_dir / "03_recent_form_penalty_simulation.csv"

    _write_csv(detail_path, details, DETAIL_FIELDS)
    _write_csv(summary_path, summary, SUMMARY_FIELDS)
    _write_csv(simulation_path, simulation, PENALTY_SUMMARY_FIELDS)

    print("=== RECENT FORM ANALYSIS ===")
    print(f"Partite analizzate : {len(details)}")
    print(f"Partite escluse/non risolte: {unresolved}")
    print(f"Dettaglio          : {detail_path.relative_to(PROJECT_ROOT)}")
    print(f"Riepilogo          : {summary_path.relative_to(PROJECT_ROOT)}")
    print(f"Simulazione        : {simulation_path.relative_to(PROJECT_ROOT)}")

    for row in simulation:
        print(
            f"[{row['Population']}] "
            f"ALTA originale {float(row['OriginalSuccessRate']) * 100:.2f}% "
            f"-> simulata "
            f"{(float(row['SimulatedAltaSuccessRate']) * 100):.2f}% "
            f"| OK persi {row['OKLostFromAlta']} "
            f"| KO rimossi {row['KORemovedFromAlta']}"
        )


if __name__ == "__main__":
    main()
