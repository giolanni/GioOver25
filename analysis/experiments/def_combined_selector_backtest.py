"""
GioOver2.5 - Combined retrospective DEF selector backtest

SCOPO
-----
Usa il backtest retroattivo point-in-time di v20def, v22def e v25def e cerca
la migliore combinazione di soglie per una ALTA congiunta:

    v20def >= X  AND  v22def >= Y  AND  v25def >= Z

Non assume che X/Y/Z siano 71 o 75. Le tre soglie vengono ottimizzate in
modo indipendente. Il test confronta esplicitamente:

- BASELINE ATTUALE: 71 / 75 / 75
- IPOTESI EMERSA DAL BACKTEST INDIVIDUALE: 70 / 80 / 80
- tutte le combinazioni comprese nel range configurato.

ANTI-LEAKAGE
------------
Gli score DEF sono ricostruiti da def_retro_band_backtest.py usando soltanto
risultati con data strettamente precedente alla partita analizzata.

NOTA IMPORTANTE
---------------
La combinazione richiede che la stessa partita esista negli storici base di
tutti e tre gli engine (v20, v22, v25). Il report mostra quindi anche quante
partite entrano nel SET COMUNE.

OUTPUT
------
analysis/experiments/def_combined_selector/output/
    summary.txt
    common_matches.csv
    combination_grid.csv
    top_combinations.csv
    monthly_top_combinations.csv
    selected_matches_best.csv
    selected_matches_baseline.csv
    selected_matches_70_80_80.csv

ESECUZIONE
----------
python -m analysis.experiments.def_combined_selector_backtest

Opzioni:
    --threshold-min 60
    --threshold-max 90
    --threshold-step 1
    --min-sample 20
    --top 30

LETTURA
-------
- PercentOK è la percentuale Over 2.5 che la nuova ALTA combinata avrebbe
  prodotto retroattivamente.
- Wilson95Lower serve a non premiare automaticamente campioni minuscoli.
- WorstMonthPercentOK e MonthsBelow70 aiutano a distinguere una configurazione
  stabile da una che vive di un solo periodo fortunato.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path

from gioover25.team_names import normalize_team_name
from analysis.experiments.def_retro_band_backtest import (
    build_retro_dataset,
    load_results_index,
)

OUTPUT_DIR = Path("analysis/experiments/def_combined_selector/output")

BASELINE = (71.0, 75.0, 75.0)
PROPOSED = (70.0, 80.0, 80.0)
ENGINES = ("v20def", "v22def", "v25def")


def text(value) -> str:
    return str(value or "").strip()


def pct(ok: int, total: int) -> float:
    return round(ok * 100.0 / total, 2) if total else 0.0


def wilson_lower(ok: int, total: int, z: float = 1.96) -> float:
    if total <= 0:
        return 0.0
    phat = ok / total
    den = 1 + z * z / total
    centre = phat + z * z / (2 * total)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
    return round((centre - margin) / den * 100.0, 4)


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


def key_for(row: dict):
    league = text(row.get("LeagueId"))
    return (
        text(row.get("MatchDate")),
        league,
        normalize_team_name(league, row.get("Home")),
        normalize_team_name(league, row.get("Away")),
    )


def build_common_dataset(all_rows: list[dict]) -> list[dict]:
    by_engine: dict[str, dict[tuple, dict]] = {engine: {} for engine in ENGINES}
    for row in all_rows:
        engine = text(row.get("Engine"))
        if engine in by_engine:
            by_engine[engine][key_for(row)] = row

    common_keys = set(by_engine[ENGINES[0]])
    for engine in ENGINES[1:]:
        common_keys &= set(by_engine[engine])

    output: list[dict] = []
    for key in sorted(common_keys):
        r20 = by_engine["v20def"][key]
        r22 = by_engine["v22def"][key]
        r25 = by_engine["v25def"][key]

        outcomes = {text(r20.get("Outcome")), text(r22.get("Outcome")), text(r25.get("Outcome"))}
        if len(outcomes) != 1 or next(iter(outcomes)) not in {"OK", "KO"}:
            continue

        output.append({
            "MatchDate": key[0],
            "LeagueId": text(r20.get("LeagueId")),
            "Home": text(r20.get("Home")),
            "Away": text(r20.get("Away")),
            "Outcome": text(r20.get("Outcome")),
            "Australia": int(text(r20.get("LeagueId")).startswith("Australia_")),
            "v20defScore": float(r20["RetroDEFScore"]),
            "v22defScore": float(r22["RetroDEFScore"]),
            "v25defScore": float(r25["RetroDEFScore"]),
            "v20BaseScore": r20.get("BaseScore", ""),
            "v22BaseScore": r22.get("BaseScore", ""),
            "v25BaseScore": r25.get("BaseScore", ""),
            "v20DefensePenaltyActive": r20.get("DefensePenaltyActive", ""),
            "v22DefensePenaltyActive": r22.get("DefensePenaltyActive", ""),
            "v25DefensePenaltyActive": r25.get("DefensePenaltyActive", ""),
        })
    return output


def thresholds(start: float, stop: float, step: float) -> list[float]:
    values = []
    current = start
    while current <= stop + 1e-9:
        values.append(round(current, 6))
        current += step
    return values


def selected(rows: list[dict], combo: tuple[float, float, float]) -> list[dict]:
    a, b, c = combo
    return [
        row for row in rows
        if row["v20defScore"] >= a
        and row["v22defScore"] >= b
        and row["v25defScore"] >= c
    ]


def stats_for(rows: list[dict]) -> tuple[int, int, int, float]:
    total = len(rows)
    ok = sum(1 for row in rows if row["Outcome"] == "OK")
    ko = total - ok
    return total, ok, ko, pct(ok, total)


def monthly_stats(rows: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        month = text(row.get("MatchDate"))[:7]
        groups[month].append(row)
    result = []
    for month in sorted(groups):
        total, ok, ko, percent = stats_for(groups[month])
        result.append({"Month": month, "Tot": total, "OK": ok, "KO": ko, "PercentOK": percent})
    return result


def evaluate_combo(rows: list[dict], combo: tuple[float, float, float]) -> dict:
    chosen = selected(rows, combo)
    total, ok, ko, percent = stats_for(chosen)
    no_au = [row for row in chosen if not row["Australia"]]
    n_total, n_ok, n_ko, n_percent = stats_for(no_au)

    months = monthly_stats(chosen)
    nonempty = [m for m in months if m["Tot"] > 0]
    worst = min((m["PercentOK"] for m in nonempty), default=0.0)
    below70 = sum(1 for m in nonempty if m["PercentOK"] < 70.0)

    return {
        "v20defThreshold": combo[0],
        "v22defThreshold": combo[1],
        "v25defThreshold": combo[2],
        "Tot": total,
        "OK": ok,
        "KO": ko,
        "PercentOK": percent,
        "Wilson95Lower": wilson_lower(ok, total),
        "NoAUTot": n_total,
        "NoAUOK": n_ok,
        "NoAUKO": n_ko,
        "NoAUPercentOK": n_percent,
        "NoAUWilson95Lower": wilson_lower(n_ok, n_total),
        "Months": len(nonempty),
        "WorstMonthPercentOK": round(worst, 2),
        "MonthsBelow70": below70,
    }


def precompute_sets(rows: list[dict], values: list[float]):
    universe = list(range(len(rows)))
    sets = {engine: {} for engine in ENGINES}
    field = {"v20def": "v20defScore", "v22def": "v22defScore", "v25def": "v25defScore"}
    for engine in ENGINES:
        score_field = field[engine]
        for threshold in values:
            sets[engine][threshold] = {i for i in universe if rows[i][score_field] >= threshold}
    return sets


def evaluate_grid(rows: list[dict], values: list[float], min_sample: int) -> list[dict]:
    sets = precompute_sets(rows, values)
    output: list[dict] = []

    # L'intersezione di set evita di riesaminare migliaia di righe per ogni
    # combinazione e rende praticabile la griglia tridimensionale.
    for t20 in values:
        s20 = sets["v20def"][t20]
        for t22 in values:
            s2022 = s20 & sets["v22def"][t22]
            if len(s2022) < min_sample:
                # alzare t25 può soltanto ridurre ulteriormente il campione
                continue
            for t25 in values:
                idx = s2022 & sets["v25def"][t25]
                if len(idx) < min_sample:
                    continue
                chosen = [rows[i] for i in idx]
                output.append(evaluate_combo(chosen, (float("-inf"), float("-inf"), float("-inf"))) | {
                    "v20defThreshold": t20,
                    "v22defThreshold": t22,
                    "v25defThreshold": t25,
                })
    return output


def add_rank(rows: list[dict]) -> list[dict]:
    ordered = sorted(
        rows,
        key=lambda r: (
            -float(r["Wilson95Lower"]),
            -float(r["PercentOK"]),
            -int(r["Tot"]),
            -float(r["NoAUWilson95Lower"]),
            float(r["v20defThreshold"]),
            float(r["v22defThreshold"]),
            float(r["v25defThreshold"]),
        ),
    )
    for pos, row in enumerate(ordered, 1):
        row["Rank"] = pos
    return ordered


def label_selected(rows: list[dict], combo: tuple[float, float, float]) -> list[dict]:
    return selected(rows, combo)


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest combinato soglie v20def/v22def/v25def")
    parser.add_argument("--threshold-min", type=float, default=60.0)
    parser.add_argument("--threshold-max", type=float, default=90.0)
    parser.add_argument("--threshold-step", type=float, default=1.0)
    parser.add_argument("--min-sample", type=int, default=20)
    parser.add_argument("--top", type=int, default=30)
    args = parser.parse_args()

    if args.threshold_step <= 0:
        raise ValueError("--threshold-step deve essere > 0")
    if args.threshold_max < args.threshold_min:
        raise ValueError("--threshold-max deve essere >= --threshold-min")

    print("[1/5] Carico risultati e ricostruisco gli score DEF point-in-time...")
    results_index = load_results_index()
    all_rows, retro_stats = build_retro_dataset(results_index)

    print("[2/5] Costruisco il set comune v20def/v22def/v25def...")
    common = build_common_dataset(all_rows)
    if not common:
        raise RuntimeError("Nessuna partita comune tra v20def, v22def e v25def")
    write_csv(OUTPUT_DIR / "common_matches.csv", common)

    values = thresholds(args.threshold_min, args.threshold_max, args.threshold_step)
    # Garantisce che baseline e proposta siano sempre valutabili anche se il
    # range scelto dall'utente non contiene uno dei loro valori.
    eval_values = sorted(set(values + list(BASELINE) + list(PROPOSED)))

    print(f"[3/5] Valuto {len(values) ** 3:,} combinazioni teoriche (campione minimo {args.min_sample})...")
    grid = evaluate_grid(common, values, args.min_sample)
    ranked = add_rank(grid)
    write_csv(OUTPUT_DIR / "combination_grid.csv", sorted(grid, key=lambda r: (r["v20defThreshold"], r["v22defThreshold"], r["v25defThreshold"])))
    write_csv(OUTPUT_DIR / "top_combinations.csv", ranked[: args.top])

    baseline_stats = evaluate_combo(common, BASELINE)
    proposed_stats = evaluate_combo(common, PROPOSED)
    best = ranked[0] if ranked else None
    best_combo = (
        float(best["v20defThreshold"]),
        float(best["v22defThreshold"]),
        float(best["v25defThreshold"]),
    ) if best else PROPOSED

    print("[4/5] Calcolo stabilità mensile e partite selezionate...")
    monthly_rows = []
    named = [("BASELINE_71_75_75", BASELINE), ("PROPOSTA_70_80_80", PROPOSED), ("BEST_WILSON", best_combo)]
    for name, combo in named:
        for row in monthly_stats(selected(common, combo)):
            monthly_rows.append({
                "Config": name,
                "v20defThreshold": combo[0],
                "v22defThreshold": combo[1],
                "v25defThreshold": combo[2],
                **row,
            })
    write_csv(OUTPUT_DIR / "monthly_top_combinations.csv", monthly_rows)
    write_csv(OUTPUT_DIR / "selected_matches_baseline.csv", label_selected(common, BASELINE))
    write_csv(OUTPUT_DIR / "selected_matches_70_80_80.csv", label_selected(common, PROPOSED))
    write_csv(OUTPUT_DIR / "selected_matches_best.csv", label_selected(common, best_combo))

    print("[5/5] Scrivo summary...")
    universe_total, universe_ok, universe_ko, universe_pct = stats_for(common)
    no_au_common = [row for row in common if not row["Australia"]]
    nu_total, nu_ok, nu_ko, nu_pct = stats_for(no_au_common)

    lines = [
        "COMBINED RETROACTIVE DEF SELECTOR BACKTEST",
        "==========================================",
        "",
        "Regola simulata:",
        "  v20def >= X AND v22def >= Y AND v25def >= Z",
        "",
        "Gli score DEF sono ricostruiti point-in-time; nessun dato della stessa",
        "giornata o successivo viene usato per la Strong Defense.",
        "",
        "SET COMUNE",
        "----------",
        f"Partite comuni con esito: {universe_total}",
        f"Esito universo comune: {universe_ok}/{universe_total} = {universe_pct:.2f}% (KO {universe_ko})",
        f"Senza Australia: {nu_ok}/{nu_total} = {nu_pct:.2f}% (KO {nu_ko})",
        "",
        "BASELINE ATTUALE 71 / 75 / 75",
        "-----------------------------",
        f"{baseline_stats['OK']}/{baseline_stats['Tot']} = {baseline_stats['PercentOK']:.2f}% | no AU {baseline_stats['NoAUOK']}/{baseline_stats['NoAUTot']} = {baseline_stats['NoAUPercentOK']:.2f}%",
        f"Wilson95Lower: {baseline_stats['Wilson95Lower']:.2f}% | worst month {baseline_stats['WorstMonthPercentOK']:.2f}% | mesi <70%: {baseline_stats['MonthsBelow70']}",
        "",
        "IPOTESI 70 / 80 / 80",
        "--------------------",
        f"{proposed_stats['OK']}/{proposed_stats['Tot']} = {proposed_stats['PercentOK']:.2f}% | no AU {proposed_stats['NoAUOK']}/{proposed_stats['NoAUTot']} = {proposed_stats['NoAUPercentOK']:.2f}%",
        f"Wilson95Lower: {proposed_stats['Wilson95Lower']:.2f}% | worst month {proposed_stats['WorstMonthPercentOK']:.2f}% | mesi <70%: {proposed_stats['MonthsBelow70']}",
        "",
        f"GRIGLIA: {args.threshold_min:g}..{args.threshold_max:g} step {args.threshold_step:g}; min sample {args.min_sample}",
        f"Combinazioni con campione sufficiente: {len(grid)}",
        "",
    ]

    if best:
        lines += [
            "MIGLIORE COMBINAZIONE ROBUSTA (WILSON 95%)",
            "------------------------------------------",
            f"v20def >= {best['v20defThreshold']}",
            f"v22def >= {best['v22defThreshold']}",
            f"v25def >= {best['v25defThreshold']}",
            f"Overall: {best['OK']}/{best['Tot']} = {best['PercentOK']:.2f}%",
            f"No AU: {best['NoAUOK']}/{best['NoAUTot']} = {best['NoAUPercentOK']:.2f}%",
            f"Wilson95Lower: {best['Wilson95Lower']:.2f}%",
            f"Worst month: {best['WorstMonthPercentOK']:.2f}% | mesi <70%: {best['MonthsBelow70']}",
            "",
        ]

    lines += [
        "TOP 10",
        "------",
    ]
    for row in ranked[:10]:
        lines.append(
            f"#{row['Rank']} {row['v20defThreshold']}/{row['v22defThreshold']}/{row['v25defThreshold']}: "
            f"{row['OK']}/{row['Tot']} = {row['PercentOK']:.2f}% | "
            f"no AU {row['NoAUPercentOK']:.2f}% | Wilson {row['Wilson95Lower']:.2f}%"
        )

    lines += [
        "",
        "LETTURA CORRETTA",
        "----------------",
        "La migliore combinazione statistica NON va adottata automaticamente.",
        "Confrontare soprattutto baseline, 70/80/80, numerosità, no-AU e",
        "stabilità mensile prima di creare/modificare un engine operativo.",
        "",
        "File principali: combination_grid.csv e top_combinations.csv.",
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nOutput: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
