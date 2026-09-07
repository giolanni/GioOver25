"""
GioOver2.5 - Laboratory candidate rules across all engines

SCOPO
-----
Applica agli storici ranking di TUTTI gli engine le 15 regole candidate emerse
nel laboratory v25, senza modificare gli engine operativi.

Per ogni engine e per ogni regola:
- considera soltanto le ALTA concluse con esito OK/KO;
- confronta il sottoinsieme selezionato con la baseline ALTA VALUTABILE per
  quella stessa regola (quindi solo righe con entrambi i driver disponibili);
- calcola overall, no-Australia, train/test temporale 70/30 e copertura;
- salva anche le partite selezionate.

Questo evita confronti falsati dai valori mancanti e permette di capire se una
regola nata su v25 conserva potere anche sugli altri engine.

USO
---
    python -m analysis.experiments.lab_rules_all_engines

Opzioni:
    --min-sample 10
    --train-ratio 0.70
    --top 10

OUTPUT
------
analysis/experiments/lab_rules_all_engines/output/
    all_engine_rule_results.csv
    top_rules_by_engine.csv
    selected_matches.csv
    summary.txt
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from gioover25.team_names import normalize_team_name


ROOT = Path(".")
RANKING_ROOT = ROOT / "data" / "storico" / "ranking"
OUTPUT_DIR = ROOT / "analysis" / "experiments" / "lab_rules_all_engines" / "output"

VALID_OUTCOMES = {"OK", "KO"}


@dataclass(frozen=True)
class Rule:
    name: str
    description: str
    required_fields: tuple[str, str]
    predicate: Callable[[dict[str, float]], bool]


RULES = (
    Rule(
        "away_attack_le_10_0__home_restart_gf_ge_2_5",
        "AwayAttackScore <= 10.0 AND HomeGFAvgSinceRestart >= 2.5",
        ("AwayAttackScore", "HomeGFAvgSinceRestart"),
        lambda v: v["AwayAttackScore"] <= 10.0 and v["HomeGFAvgSinceRestart"] >= 2.5,
    ),
    Rule(
        "away_ga_l5_ge_2_0__home_restart_over_ge_1_0",
        "AwayGALast5Avg >= 2.0 AND HomeOverRateSinceRestart >= 1.0",
        ("AwayGALast5Avg", "HomeOverRateSinceRestart"),
        lambda v: v["AwayGALast5Avg"] >= 2.0 and v["HomeOverRateSinceRestart"] >= 1.0,
    ),
    Rule(
        "away_ga_l5_ge_2_0__home_restart_gf_ge_2_5",
        "AwayGALast5Avg >= 2.0 AND HomeGFAvgSinceRestart >= 2.5",
        ("AwayGALast5Avg", "HomeGFAvgSinceRestart"),
        lambda v: v["AwayGALast5Avg"] >= 2.0 and v["HomeGFAvgSinceRestart"] >= 2.5,
    ),
    Rule(
        "worst_ppg_l5_le_0_8__home_restart_gf_ge_2_5",
        "WorstPPGLast5 <= 0.8 AND HomeGFAvgSinceRestart >= 2.5",
        ("WorstPPGLast5", "HomeGFAvgSinceRestart"),
        lambda v: v["WorstPPGLast5"] <= 0.8 and v["HomeGFAvgSinceRestart"] >= 2.5,
    ),
    Rule(
        "away_ga_l5_ge_2_0__home_restart_over_ge_0_8",
        "AwayGALast5Avg >= 2.0 AND HomeOverRateSinceRestart >= 0.8",
        ("AwayGALast5Avg", "HomeOverRateSinceRestart"),
        lambda v: v["AwayGALast5Avg"] >= 2.0 and v["HomeOverRateSinceRestart"] >= 0.8,
    ),
    Rule(
        "away_ga_l5_ge_1_8__home_restart_gf_ge_2_5",
        "AwayGALast5Avg >= 1.8 AND HomeGFAvgSinceRestart >= 2.5",
        ("AwayGALast5Avg", "HomeGFAvgSinceRestart"),
        lambda v: v["AwayGALast5Avg"] >= 1.8 and v["HomeGFAvgSinceRestart"] >= 2.5,
    ),
    Rule(
        "away_attack_le_11_0__home_restart_gf_ge_2_5",
        "AwayAttackScore <= 11.0 AND HomeGFAvgSinceRestart >= 2.5",
        ("AwayAttackScore", "HomeGFAvgSinceRestart"),
        lambda v: v["AwayAttackScore"] <= 11.0 and v["HomeGFAvgSinceRestart"] >= 2.5,
    ),
    Rule(
        "away_def_weak_ge_8_0__home_restart_gf_ge_2_5",
        "AwayDefenseWeaknessScore >= 8.0 AND HomeGFAvgSinceRestart >= 2.5",
        ("AwayDefenseWeaknessScore", "HomeGFAvgSinceRestart"),
        lambda v: v["AwayDefenseWeaknessScore"] >= 8.0 and v["HomeGFAvgSinceRestart"] >= 2.5,
    ),
    Rule(
        "away_ga_l5_ge_1_8__home_restart_over_ge_1_0",
        "AwayGALast5Avg >= 1.8 AND HomeOverRateSinceRestart >= 1.0",
        ("AwayGALast5Avg", "HomeOverRateSinceRestart"),
        lambda v: v["AwayGALast5Avg"] >= 1.8 and v["HomeOverRateSinceRestart"] >= 1.0,
    ),
    Rule(
        "home_restart_gf_ge_2_5__home_restart_over_ge_0_8",
        "HomeGFAvgSinceRestart >= 2.5 AND HomeOverRateSinceRestart >= 0.8",
        ("HomeGFAvgSinceRestart", "HomeOverRateSinceRestart"),
        lambda v: v["HomeGFAvgSinceRestart"] >= 2.5 and v["HomeOverRateSinceRestart"] >= 0.8,
    ),
    Rule(
        "home_restart_gf_ge_2_0__home_restart_over_ge_0_8",
        "HomeGFAvgSinceRestart >= 2.0 AND HomeOverRateSinceRestart >= 0.8",
        ("HomeGFAvgSinceRestart", "HomeOverRateSinceRestart"),
        lambda v: v["HomeGFAvgSinceRestart"] >= 2.0 and v["HomeOverRateSinceRestart"] >= 0.8,
    ),
    Rule(
        "away_def_weak_ge_9_0__home_restart_gf_ge_2_5",
        "AwayDefenseWeaknessScore >= 9.0 AND HomeGFAvgSinceRestart >= 2.5",
        ("AwayDefenseWeaknessScore", "HomeGFAvgSinceRestart"),
        lambda v: v["AwayDefenseWeaknessScore"] >= 9.0 and v["HomeGFAvgSinceRestart"] >= 2.5,
    ),
    Rule(
        "away_attack_le_10_0__home_restart_gf_ge_2_0",
        "AwayAttackScore <= 10.0 AND HomeGFAvgSinceRestart >= 2.0",
        ("AwayAttackScore", "HomeGFAvgSinceRestart"),
        lambda v: v["AwayAttackScore"] <= 10.0 and v["HomeGFAvgSinceRestart"] >= 2.0,
    ),
    Rule(
        "home_restart_gf_ge_2_0__home_restart_over_ge_1_0",
        "HomeGFAvgSinceRestart >= 2.0 AND HomeOverRateSinceRestart >= 1.0",
        ("HomeGFAvgSinceRestart", "HomeOverRateSinceRestart"),
        lambda v: v["HomeGFAvgSinceRestart"] >= 2.0 and v["HomeOverRateSinceRestart"] >= 1.0,
    ),
    Rule(
        "away_def_weak_ge_8_0__home_restart_over_ge_1_0",
        "AwayDefenseWeaknessScore >= 8.0 AND HomeOverRateSinceRestart >= 1.0",
        ("AwayDefenseWeaknessScore", "HomeOverRateSinceRestart"),
        lambda v: v["AwayDefenseWeaknessScore"] >= 8.0 and v["HomeOverRateSinceRestart"] >= 1.0,
    ),
)


def text(value) -> str:
    return str(value or "").strip()


def to_float(value) -> float | None:
    raw = text(value).replace(",", ".")
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def outcome_for(row: dict) -> str:
    value = text(row.get("Over25") or row.get("Outcome")).upper()
    if value in VALID_OUTCOMES:
        return value

    hg = to_float(row.get("HG"))
    ag = to_float(row.get("AG"))
    if hg is not None and ag is not None:
        return "OK" if hg + ag >= 3 else "KO"
    return ""


def band_for(row: dict) -> str:
    return text(row.get("Band") or row.get("Fascia")).upper()


def match_key(row: dict) -> tuple[str, str, str, str]:
    league = text(row.get("LeagueId"))
    return (
        text(row.get("MatchDate")),
        league,
        normalize_team_name(league, row.get("Home")),
        normalize_team_name(league, row.get("Away")),
    )


def read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        return list(reader)


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


def discover_engine_histories() -> list[tuple[str, Path]]:
    output: list[tuple[str, Path]] = []
    if not RANKING_ROOT.exists():
        return output

    for engine_dir in sorted(path for path in RANKING_ROOT.iterdir() if path.is_dir()):
        path = engine_dir / f"storico_ranking_{engine_dir.name}.csv"
        if path.exists():
            output.append((engine_dir.name, path))
    return output


def load_engine_alta(path: Path) -> list[dict]:
    rows = []
    for row in read_csv(path):
        if band_for(row) != "ALTA":
            continue
        outcome = outcome_for(row)
        if outcome not in VALID_OUTCOMES:
            continue
        if not text(row.get("MatchDate")):
            continue
        copy = dict(row)
        copy["_Outcome"] = outcome
        rows.append(copy)

    # Un solo record per partita: in caso di duplicato preferiamo la prediction
    # più antica, coerentemente con gli altri esperimenti GioOver2.5.
    rows.sort(key=lambda r: (text(r.get("PredictionDate")) or "9999-99-99", text(r.get("MatchDate"))))
    unique: dict[tuple, dict] = {}
    for row in rows:
        unique.setdefault(match_key(row), row)
    return list(unique.values())


def stats(rows: list[dict]) -> tuple[int, int, int, float]:
    total = len(rows)
    ok = sum(1 for row in rows if row["_Outcome"] == "OK")
    ko = total - ok
    pct = round(ok * 100.0 / total, 2) if total else 0.0
    return total, ok, ko, pct


def split_dates(rows: list[dict], ratio: float) -> tuple[set[str], set[str]]:
    dates = sorted({text(row.get("MatchDate")) for row in rows if text(row.get("MatchDate"))})
    if len(dates) <= 1:
        return set(dates), set()
    cut = int(round(len(dates) * ratio))
    cut = max(1, min(cut, len(dates) - 1))
    return set(dates[:cut]), set(dates[cut:])


def rule_values(row: dict, rule: Rule) -> dict[str, float] | None:
    values: dict[str, float] = {}
    for field in rule.required_fields:
        value = to_float(row.get(field))
        if value is None:
            return None
        values[field] = value
    return values


def pct_delta(selected_pct: float, baseline_pct: float) -> float:
    return round(selected_pct - baseline_pct, 2)


def evaluate_rule(engine: str, rows: list[dict], rule: Rule, train_ratio: float) -> tuple[dict, list[dict]]:
    evaluable: list[dict] = []
    selected: list[dict] = []

    for row in rows:
        values = rule_values(row, rule)
        if values is None:
            continue
        evaluable.append(row)
        if rule.predicate(values):
            selected.append(row)

    b_total, b_ok, b_ko, b_pct = stats(evaluable)
    s_total, s_ok, s_ko, s_pct = stats(selected)

    base_no_au = [r for r in evaluable if not text(r.get("LeagueId")).startswith("Australia_")]
    sel_no_au = [r for r in selected if not text(r.get("LeagueId")).startswith("Australia_")]
    bn_total, bn_ok, bn_ko, bn_pct = stats(base_no_au)
    sn_total, sn_ok, sn_ko, sn_pct = stats(sel_no_au)

    train_dates, test_dates = split_dates(evaluable, train_ratio)
    base_train = [r for r in evaluable if text(r.get("MatchDate")) in train_dates]
    sel_train = [r for r in selected if text(r.get("MatchDate")) in train_dates]
    base_test = [r for r in evaluable if text(r.get("MatchDate")) in test_dates]
    sel_test = [r for r in selected if text(r.get("MatchDate")) in test_dates]

    bt_total, bt_ok, bt_ko, bt_pct = stats(base_train)
    st_total, st_ok, st_ko, st_pct = stats(sel_train)
    bv_total, bv_ok, bv_ko, bv_pct = stats(base_test)
    sv_total, sv_ok, sv_ko, sv_pct = stats(sel_test)

    result = {
        "Engine": engine,
        "Rule": rule.name,
        "Description": rule.description,
        "BaselineEvaluableTotal": b_total,
        "BaselineEvaluableOK": b_ok,
        "BaselineEvaluableKO": b_ko,
        "BaselineEvaluablePct": b_pct,
        "SelectedTotal": s_total,
        "SelectedOK": s_ok,
        "SelectedKO": s_ko,
        "SelectedPct": s_pct,
        "DeltaVsBaseline": pct_delta(s_pct, b_pct) if s_total else 0.0,
        "CoveragePct": round(s_total * 100.0 / b_total, 2) if b_total else 0.0,
        "BaselineNoAUTotal": bn_total,
        "BaselineNoAUPct": bn_pct,
        "SelectedNoAUTotal": sn_total,
        "SelectedNoAUOK": sn_ok,
        "SelectedNoAUKO": sn_ko,
        "SelectedNoAUPct": sn_pct,
        "DeltaNoAU": pct_delta(sn_pct, bn_pct) if sn_total else 0.0,
        "TrainBaselineTotal": bt_total,
        "TrainBaselinePct": bt_pct,
        "TrainSelectedTotal": st_total,
        "TrainSelectedOK": st_ok,
        "TrainSelectedKO": st_ko,
        "TrainSelectedPct": st_pct,
        "TrainDelta": pct_delta(st_pct, bt_pct) if st_total else 0.0,
        "TestBaselineTotal": bv_total,
        "TestBaselinePct": bv_pct,
        "TestSelectedTotal": sv_total,
        "TestSelectedOK": sv_ok,
        "TestSelectedKO": sv_ko,
        "TestSelectedPct": sv_pct,
        "TestDelta": pct_delta(sv_pct, bv_pct) if sv_total else 0.0,
    }

    selected_export = []
    for row in selected:
        selected_export.append({
            "Engine": engine,
            "Rule": rule.name,
            "MatchDate": text(row.get("MatchDate")),
            "PredictionDate": text(row.get("PredictionDate")),
            "LeagueId": text(row.get("LeagueId")),
            "Home": text(row.get("Home")),
            "Away": text(row.get("Away")),
            "Score": text(row.get("Score")),
            "Band": band_for(row),
            "Outcome": row["_Outcome"],
            "HG": text(row.get("HG")),
            "AG": text(row.get("AG")),
        })

    return result, selected_export


def rank_for_engine(rows: list[dict], min_sample: int) -> list[dict]:
    eligible = [row for row in rows if int(row["SelectedTotal"]) >= min_sample]
    pool = eligible if eligible else [row for row in rows if int(row["SelectedTotal"]) > 0]

    # Precisione prima del volume: test temporale, overall, no-AU, quindi sample.
    return sorted(
        pool,
        key=lambda row: (
            float(row["TestSelectedPct"]) if int(row["TestSelectedTotal"]) else -1.0,
            float(row["SelectedPct"]),
            float(row["SelectedNoAUPct"]),
            float(row["DeltaVsBaseline"]),
            int(row["SelectedTotal"]),
        ),
        reverse=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Testa le regole laboratory v25 su tutti gli engine")
    parser.add_argument("--min-sample", type=int, default=10)
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--top", type=int, default=10)
    args = parser.parse_args()

    if not 0.1 <= args.train_ratio <= 0.9:
        raise ValueError("--train-ratio deve essere compreso tra 0.1 e 0.9")

    histories = discover_engine_histories()
    if not histories:
        raise FileNotFoundError(f"Nessuno storico engine trovato in {RANKING_ROOT}")

    all_results: list[dict] = []
    all_selected: list[dict] = []
    engine_alta_counts: dict[str, int] = {}

    for engine, path in histories:
        rows = load_engine_alta(path)
        engine_alta_counts[engine] = len(rows)
        if not rows:
            continue

        for rule in RULES:
            result, selected = evaluate_rule(engine, rows, rule, args.train_ratio)
            all_results.append(result)
            all_selected.extend(selected)

    if not all_results:
        raise RuntimeError("Nessun engine contiene ALTA concluse valutabili")

    top_rows: list[dict] = []
    for engine in sorted({row["Engine"] for row in all_results}):
        ranked = rank_for_engine([row for row in all_results if row["Engine"] == engine], args.min_sample)
        for rank, row in enumerate(ranked[: args.top], start=1):
            top_rows.append({"Rank": rank, **row})

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "all_engine_rule_results.csv", all_results)
    write_csv(OUTPUT_DIR / "top_rules_by_engine.csv", top_rows)
    write_csv(OUTPUT_DIR / "selected_matches.csv", all_selected)

    lines = [
        "LABORATORY RULES - ALL ENGINES",
        "==============================",
        "",
        "Le 15 regole candidate v25 sono state applicate ESPLICITAMENTE a tutti",
        "gli storici engine disponibili. Nessun engine operativo viene modificato.",
        "",
        f"Engine trovati: {len(histories)}",
        f"Regole testate: {len(RULES)}",
        f"Min sample per classifica: {args.min_sample}",
        f"Split temporale train/test: {args.train_ratio:.0%}/{1-args.train_ratio:.0%}",
        "",
        "ALTA CON ESITO PER ENGINE",
        "------------------------",
    ]

    for engine in sorted(engine_alta_counts):
        lines.append(f"{engine}: {engine_alta_counts[engine]}")

    lines += ["", "MIGLIORI REGOLE PER ENGINE", "---------------------------"]

    for engine in sorted({row["Engine"] for row in top_rows}):
        lines.append("")
        lines.append(engine.upper())
        for row in [r for r in top_rows if r["Engine"] == engine][:5]:
            lines.append(
                f"  #{row['Rank']} {row['Rule']}: "
                f"{row['SelectedOK']}/{row['SelectedTotal']}={row['SelectedPct']:.2f}% "
                f"| test {row['TestSelectedOK']}/{row['TestSelectedTotal']}={row['TestSelectedPct']:.2f}% "
                f"| noAU {row['SelectedNoAUPct']:.2f}% "
                f"| delta {row['DeltaVsBaseline']:+.2f}"
            )

    lines += [
        "",
        "NOTE",
        "----",
        "- La baseline è specifica per regola: usa solo ALTA dove entrambi i driver sono disponibili.",
        "- Questo rende DeltaVsBaseline confrontabile e non premia artificialmente i missing.",
        "- Per la scelta finale guardare soprattutto precisione, test temporale e no-Australia;",
        "  il volume resta un indicatore di robustezza, non il criterio principale.",
    ]

    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nOutput: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
