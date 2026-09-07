"""
GioOver2.5 - Cross-engine Laboratory rules experiment

Applica agli ALTA di tutti gli engine le regole candidate emerse dal Laboratory
senza modificare gli engine operativi. Per ogni engine/regola misura baseline,
subset selezionato, delta, no-Australia e split temporale train/test.

Esecuzione:
    python -m analysis.experiments.cross_engine_laboratory_rules

Output:
    analysis/experiments/cross_engine_laboratory_rules/output/
        rule_results.csv
        selected_matches.csv
        summary.txt
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from analysis.laboratory.recent_form_drivers import enrich_matches_with_recent_form
from gioover25.engines.factory import get_available_engines
from gioover25.team_names import normalize_team_name

ROOT = Path(".")
RANKING_ROOT = ROOT / "data" / "storico" / "ranking"
OUTPUT_DIR = ROOT / "analysis" / "experiments" / "cross_engine_laboratory_rules" / "output"


def text(value) -> str:
    return str(value or "").strip()


def num(row: dict, field: str) -> float | None:
    raw = text(row.get(field)).replace(",", ".")
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def outcome(row: dict) -> str:
    value = text(row.get("Over25") or row.get("Outcome")).upper()
    if value in {"OK", "KO"}:
        return value
    try:
        hg = int(float(text(row.get("HG"))))
        ag = int(float(text(row.get("AG"))))
    except ValueError:
        return ""
    return "OK" if hg + ag >= 3 else "KO"


def is_high_band(value: str, include_contextual: bool) -> bool:
    band = text(value).upper()
    if band == "ALTA":
        return True
    if not include_contextual:
        return False
    return band.startswith("IMM-ALTA-") or band == "PROX-ALTA"


def match_key(row: dict) -> tuple[str, str, str, str]:
    league = text(row.get("LeagueId"))
    return (
        text(row.get("MatchDate")) or text(row.get("PredictionDate")),
        league,
        normalize_team_name(league, row.get("Home", "")),
        normalize_team_name(league, row.get("Away", "")),
    )


def read_engine_rows(engine: str, include_contextual: bool) -> list[dict]:
    path = RANKING_ROOT / engine / f"storico_ranking_{engine}.csv"
    if not path.exists():
        return []

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        rows = list(reader)

    # Un pronostico per partita; preferiamo la PredictionDate più antica.
    valid = []
    for row in rows:
        if not is_high_band(row.get("Band", ""), include_contextual):
            continue
        if outcome(row) not in {"OK", "KO"}:
            continue
        if not (text(row.get("MatchDate")) or text(row.get("PredictionDate"))):
            continue
        copy = dict(row)
        copy["Outcome"] = outcome(row)
        copy["Engine"] = engine
        valid.append(copy)

    valid.sort(key=lambda r: (text(r.get("PredictionDate")) or "9999-99-99", match_key(r)))
    unique: dict[tuple[str, str, str, str], dict] = {}
    for row in valid:
        unique.setdefault(match_key(row), row)

    result = list(unique.values())
    result.sort(key=lambda r: match_key(r))
    return enrich_matches_with_recent_form(result)


@dataclass(frozen=True)
class Rule:
    name: str
    label: str
    predicate: Callable[[dict], bool]


def ge(field: str, threshold: float) -> Callable[[dict], bool]:
    return lambda row: (num(row, field) is not None and num(row, field) >= threshold)


def le(field: str, threshold: float) -> Callable[[dict], bool]:
    return lambda row: (num(row, field) is not None and num(row, field) <= threshold)


def both(a: Callable[[dict], bool], b: Callable[[dict], bool]) -> Callable[[dict], bool]:
    return lambda row: a(row) and b(row)


RULES = [
    Rule("away_attack_le_10_0__home_restart_gf_ge_2_5", "AwayAttackScore<=10 AND HomeGFAvgSinceRestart>=2.5", both(le("AwayAttackScore", 10.0), ge("HomeGFAvgSinceRestart", 2.5))),
    Rule("away_ga_l5_ge_2_0__home_restart_over_ge_1_0", "AwayGALast5Avg>=2.0 AND HomeOverRateSinceRestart>=1.0", both(ge("AwayGALast5Avg", 2.0), ge("HomeOverRateSinceRestart", 1.0))),
    Rule("away_ga_l5_ge_2_0__home_restart_gf_ge_2_5", "AwayGALast5Avg>=2.0 AND HomeGFAvgSinceRestart>=2.5", both(ge("AwayGALast5Avg", 2.0), ge("HomeGFAvgSinceRestart", 2.5))),
    Rule("worst_ppg_l5_le_0_8__home_restart_gf_ge_2_5", "WorstPPGLast5<=0.8 AND HomeGFAvgSinceRestart>=2.5", both(le("WorstPPGLast5", 0.8), ge("HomeGFAvgSinceRestart", 2.5))),
    Rule("away_ga_l5_ge_2_0__home_restart_over_ge_0_8", "AwayGALast5Avg>=2.0 AND HomeOverRateSinceRestart>=0.8", both(ge("AwayGALast5Avg", 2.0), ge("HomeOverRateSinceRestart", 0.8))),
    Rule("away_ga_l5_ge_1_8__home_restart_gf_ge_2_5", "AwayGALast5Avg>=1.8 AND HomeGFAvgSinceRestart>=2.5", both(ge("AwayGALast5Avg", 1.8), ge("HomeGFAvgSinceRestart", 2.5))),
    Rule("away_attack_le_11_0__home_restart_gf_ge_2_5", "AwayAttackScore<=11 AND HomeGFAvgSinceRestart>=2.5", both(le("AwayAttackScore", 11.0), ge("HomeGFAvgSinceRestart", 2.5))),
    Rule("away_def_weak_ge_8_0__home_restart_gf_ge_2_5", "AwayDefenseWeaknessScore>=8 AND HomeGFAvgSinceRestart>=2.5", both(ge("AwayDefenseWeaknessScore", 8.0), ge("HomeGFAvgSinceRestart", 2.5))),
    Rule("away_ga_l5_ge_1_8__home_restart_over_ge_1_0", "AwayGALast5Avg>=1.8 AND HomeOverRateSinceRestart>=1.0", both(ge("AwayGALast5Avg", 1.8), ge("HomeOverRateSinceRestart", 1.0))),
    Rule("home_restart_gf_ge_2_5__home_restart_over_ge_0_8", "HomeGFAvgSinceRestart>=2.5 AND HomeOverRateSinceRestart>=0.8", both(ge("HomeGFAvgSinceRestart", 2.5), ge("HomeOverRateSinceRestart", 0.8))),
    Rule("home_restart_gf_ge_2_0__home_restart_over_ge_0_8", "HomeGFAvgSinceRestart>=2.0 AND HomeOverRateSinceRestart>=0.8", both(ge("HomeGFAvgSinceRestart", 2.0), ge("HomeOverRateSinceRestart", 0.8))),
    Rule("away_def_weak_ge_9_0__home_restart_gf_ge_2_5", "AwayDefenseWeaknessScore>=9 AND HomeGFAvgSinceRestart>=2.5", both(ge("AwayDefenseWeaknessScore", 9.0), ge("HomeGFAvgSinceRestart", 2.5))),
    Rule("away_attack_le_10_0__home_restart_gf_ge_2_0", "AwayAttackScore<=10 AND HomeGFAvgSinceRestart>=2.0", both(le("AwayAttackScore", 10.0), ge("HomeGFAvgSinceRestart", 2.0))),
    Rule("home_restart_gf_ge_2_0__home_restart_over_ge_1_0", "HomeGFAvgSinceRestart>=2.0 AND HomeOverRateSinceRestart>=1.0", both(ge("HomeGFAvgSinceRestart", 2.0), ge("HomeOverRateSinceRestart", 1.0))),
    Rule("away_def_weak_ge_8_0__home_restart_over_ge_1_0", "AwayDefenseWeaknessScore>=8 AND HomeOverRateSinceRestart>=1.0", both(ge("AwayDefenseWeaknessScore", 8.0), ge("HomeOverRateSinceRestart", 1.0))),
]


def stats(rows: list[dict]) -> tuple[int, int, int, float]:
    total = len(rows)
    ok = sum(1 for r in rows if r["Outcome"] == "OK")
    ko = total - ok
    pct = ok * 100.0 / total if total else 0.0
    return total, ok, ko, pct


def split_dates(rows: list[dict], train_ratio: float) -> tuple[set[str], set[str]]:
    dates = sorted({text(r.get("MatchDate")) or text(r.get("PredictionDate")) for r in rows})
    if len(dates) <= 1:
        return set(dates), set()
    cut = int(len(dates) * train_ratio)
    cut = max(1, min(cut, len(dates) - 1))
    return set(dates[:cut]), set(dates[cut:])


def date_of(row: dict) -> str:
    return text(row.get("MatchDate")) or text(row.get("PredictionDate"))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Testa le regole Laboratory sugli ALTA di tutti gli engine")
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--include-contextual-high", action="store_true", help="Include anche IMM-ALTA-* e PROX-ALTA")
    args = parser.parse_args()

    if not 0.1 <= args.train_ratio <= 0.9:
        raise ValueError("--train-ratio deve essere tra 0.1 e 0.9")

    result_rows: list[dict] = []
    selected_rows: list[dict] = []

    for engine in get_available_engines():
        rows = read_engine_rows(engine, args.include_contextual_high)
        if not rows:
            continue

        train_dates, test_dates = split_dates(rows, args.train_ratio)
        base_total, base_ok, base_ko, base_pct = stats(rows)
        base_no_au = [r for r in rows if not text(r.get("LeagueId")).startswith("Australia_")]
        _, _, _, base_no_au_pct = stats(base_no_au)
        base_train = [r for r in rows if date_of(r) in train_dates]
        base_test = [r for r in rows if date_of(r) in test_dates]
        _, _, _, base_train_pct = stats(base_train)
        _, _, _, base_test_pct = stats(base_test)

        for rule in RULES:
            chosen = [r for r in rows if rule.predicate(r)]
            total, ok, ko, pct = stats(chosen)
            no_au = [r for r in chosen if not text(r.get("LeagueId")).startswith("Australia_")]
            no_au_total, no_au_ok, no_au_ko, no_au_pct = stats(no_au)
            train = [r for r in chosen if date_of(r) in train_dates]
            test = [r for r in chosen if date_of(r) in test_dates]
            train_total, train_ok, train_ko, train_pct = stats(train)
            test_total, test_ok, test_ko, test_pct = stats(test)

            result_rows.append({
                "Engine": engine,
                "Rule": rule.name,
                "Description": rule.label,
                "BaselineTot": base_total,
                "BaselineOK": base_ok,
                "BaselineKO": base_ko,
                "BaselinePct": round(base_pct, 2),
                "BaselineNoAUPct": round(base_no_au_pct, 2),
                "BaselineTrainPct": round(base_train_pct, 2),
                "BaselineTestPct": round(base_test_pct, 2),
                "SelectedTot": total,
                "SelectedOK": ok,
                "SelectedKO": ko,
                "SelectedPct": round(pct, 2),
                "DeltaVsBaseline": round(pct - base_pct, 2) if total else 0.0,
                "CoveragePct": round(total * 100.0 / base_total, 2) if base_total else 0.0,
                "NoAUTot": no_au_total,
                "NoAUOK": no_au_ok,
                "NoAUKO": no_au_ko,
                "NoAUPct": round(no_au_pct, 2),
                "TrainTot": train_total,
                "TrainOK": train_ok,
                "TrainKO": train_ko,
                "TrainPct": round(train_pct, 2),
                "TestTot": test_total,
                "TestOK": test_ok,
                "TestKO": test_ko,
                "TestPct": round(test_pct, 2),
                "TestDeltaVsBaseline": round(test_pct - base_test_pct, 2) if test_total else 0.0,
            })

            for row in chosen:
                selected_rows.append({
                    "Engine": engine,
                    "Rule": rule.name,
                    "MatchDate": date_of(row),
                    "LeagueId": text(row.get("LeagueId")),
                    "Home": text(row.get("Home")),
                    "Away": text(row.get("Away")),
                    "Score": text(row.get("Score")),
                    "Band": text(row.get("Band")),
                    "Outcome": row["Outcome"],
                    "HG": text(row.get("HG")),
                    "AG": text(row.get("AG")),
                    "AwayAttackScore": text(row.get("AwayAttackScore")),
                    "AwayDefenseWeaknessScore": text(row.get("AwayDefenseWeaknessScore")),
                    "AwayGALast5Avg": text(row.get("AwayGALast5Avg")),
                    "WorstPPGLast5": text(row.get("WorstPPGLast5")),
                    "HomeGFAvgSinceRestart": text(row.get("HomeGFAvgSinceRestart")),
                    "HomeOverRateSinceRestart": text(row.get("HomeOverRateSinceRestart")),
                })

    result_rows.sort(key=lambda r: (r["Engine"], -float(r["TestPct"]), -float(r["SelectedPct"]), -int(r["SelectedTot"])))
    write_csv(OUTPUT_DIR / "rule_results.csv", result_rows)
    write_csv(OUTPUT_DIR / "selected_matches.csv", selected_rows)

    lines = [
        "CROSS-ENGINE LABORATORY RULES",
        "=============================",
        "",
        "Popolazione: fascia ALTA di ciascun engine" + (" + contextual high" if args.include_contextual_high else ""),
        f"Split temporale: {args.train_ratio:.0%} train / {1-args.train_ratio:.0%} test per engine",
        "",
    ]

    engines = sorted({r["Engine"] for r in result_rows})
    for engine in engines:
        rows = [r for r in result_rows if r["Engine"] == engine and int(r["SelectedTot"]) > 0]
        rows.sort(key=lambda r: (float(r["TestPct"]), float(r["SelectedPct"]), int(r["SelectedTot"])), reverse=True)
        if not rows:
            continue
        base = rows[0]
        lines += [
            engine.upper(),
            "-" * len(engine),
            f"Baseline ALTA: {base['BaselineOK']}/{base['BaselineTot']} = {base['BaselinePct']}% | test {base['BaselineTestPct']}%",
        ]
        for row in rows[:5]:
            lines.append(
                f"  {row['Rule']}: {row['SelectedOK']}/{row['SelectedTot']} = {row['SelectedPct']}% "
                f"| test {row['TestOK']}/{row['TestTot']} = {row['TestPct']}% "
                f"| noAU {row['NoAUPct']}% | delta {row['DeltaVsBaseline']:+.2f}"
            )
        lines.append("")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"Output: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
