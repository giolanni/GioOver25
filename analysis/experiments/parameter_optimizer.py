"""
GioOver2.5 - parameter_optimizer.py

Scopo
-----
Ottimizza in modo iterativo soglie e pesi sperimentali su uno storico ranking,
senza modificare l'engine. Usa lo storico dell'engine scelto e i driver del
Laboratory, divide cronologicamente i dati in TRAIN e VALIDATION e produce un
report per ogni fase.

Esecuzione
----------
python -m analysis.experiments.parameter_optimizer --engine v25
python -m analysis.experiments.parameter_optimizer --engine v25 --exclude-australia
"""

import argparse
import csv
from copy import deepcopy
from pathlib import Path


DEFAULT_DRIVERS = Path("analysis/laboratory/data/02_drivers.csv")
ALTA_THRESHOLD = 75.0
MEDIA_THRESHOLD = 65.0
MIN_COVERAGE = 75.0

REQUIRED_DRIVERS = {
    "HomeDefenseWeaknessScore",
    "AwayDefenseWeaknessScore",
    "HomePPGLast5",
    "AwayPPGLast5",
    "HomeLongBreakDetected",
    "AwayLongBreakDetected",
    "HomeRestartReady",
    "AwayRestartReady",
    "HomeRestartNotReady",
    "AwayRestartNotReady",
}

STAGES = [
    ("strong_defense", "02_strong_defense.csv"),
    ("recent_form", "03_recent_form.csv"),
    ("restart", "04_restart.csv"),
    ("vulnerable_defenses_bonus", "05_vulnerable_defenses_bonus.csv"),
    ("strong_recent_form_bonus", "06_strong_recent_form_bonus.csv"),
    ("max_penalty", "07_max_penalty.csv"),
    ("max_bonus", "08_max_bonus.csv"),
]


def text(value) -> str:
    """Restituisce testo pulito anche per celle vuote."""
    return str(value or "").strip()


def norm_team(value) -> str:
    """Normalizza il nome squadra per gli abbinamenti."""
    return " ".join(text(value).casefold().split())


def to_float(value, default=0.0):
    """Converte una cella in float accettando anche la virgola."""
    raw = text(value).replace(",", ".")
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def to_optional_float(value):
    """Converte una cella in float o restituisce None."""
    raw = text(value).replace(",", ".")
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def read_csv(path: Path) -> list[dict]:
    """Legge un CSV GioOver2.5 delimitato da punto e virgola."""
    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if not reader.fieldnames:
            raise ValueError(f"Header assente: {path}")
        return list(reader)


def write_csv(path: Path, rows: list[dict]) -> None:
    """Scrive una lista di dizionari in CSV UTF-8 con BOM."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)

    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def effective_date(row: dict) -> str:
    """Usa MatchDate e, se assente, PredictionDate."""
    return text(row.get("MatchDate")) or text(row.get("PredictionDate"))


def key_for(row: dict):
    """Costruisce la chiave comune tra ranking e Laboratory."""
    return (
        effective_date(row),
        text(row.get("LeagueId")),
        norm_team(row.get("Home")),
        norm_team(row.get("Away")),
    )


def outcome_for(row: dict) -> str:
    """Recupera l'esito OK/KO da Outcome oppure Over25."""
    for field in ("Outcome", "Over25"):
        value = text(row.get(field)).upper()
        if value in {"OK", "KO"}:
            return value
    return ""


def score_to_band(score: float) -> str:
    """Converte lo score in ALTA, MEDIA o BASSA."""
    if score >= ALTA_THRESHOLD:
        return "ALTA"
    if score >= MEDIA_THRESHOLD:
        return "MEDIA"
    return "BASSA"


def pivot_drivers(rows: list[dict]) -> dict:
    """Trasforma 02_drivers.csv da formato lungo a formato largo."""
    output = {}

    for row in rows:
        driver = text(row.get("Driver"))
        if not driver:
            continue

        record = output.setdefault(key_for(row), {})
        record[driver] = to_optional_float(row.get("Value"))

    return output


def build_dataset(
    ranking_rows: list[dict],
    drivers_index: dict,
    exclude_australia: bool,
):
    """Abbina ranking e Laboratory e restituisce dati validi e righe saltate."""
    dataset = []
    skipped = []

    for row in ranking_rows:
        outcome = outcome_for(row)

        if outcome not in {"OK", "KO"}:
            skipped.append({
                "Reason": "OUTCOME_MISSING",
                "MatchDate": effective_date(row),
                "LeagueId": text(row.get("LeagueId")),
                "Home": text(row.get("Home")),
                "Away": text(row.get("Away")),
            })
            continue

        league_id = text(row.get("LeagueId"))

        if exclude_australia and league_id.startswith("Australia_"):
            continue

        drivers = drivers_index.get(key_for(row))

        if drivers is None:
            skipped.append({
                "Reason": "LABORATORY_MATCH_NOT_FOUND",
                "MatchDate": effective_date(row),
                "LeagueId": league_id,
                "Home": text(row.get("Home")),
                "Away": text(row.get("Away")),
            })
            continue

        missing = sorted(name for name in REQUIRED_DRIVERS if name not in drivers)

        if missing:
            skipped.append({
                "Reason": "MISSING_DRIVERS:" + ",".join(missing),
                "MatchDate": effective_date(row),
                "LeagueId": league_id,
                "Home": text(row.get("Home")),
                "Away": text(row.get("Away")),
            })
            continue

        dataset.append({
            "EffectiveDate": effective_date(row),
            "MatchDate": text(row.get("MatchDate")),
            "PredictionDate": text(row.get("PredictionDate")),
            "LeagueId": league_id,
            "Home": text(row.get("Home")),
            "Away": text(row.get("Away")),
            "BaseScore": to_float(row.get("Score")),
            "BaseBand": text(row.get("Band")).upper(),
            "Outcome": outcome,
            "HomeDefenseWeaknessScore": drivers["HomeDefenseWeaknessScore"],
            "AwayDefenseWeaknessScore": drivers["AwayDefenseWeaknessScore"],
            "HomePPGLast5": drivers["HomePPGLast5"],
            "AwayPPGLast5": drivers["AwayPPGLast5"],
            "HomeLongBreakDetected": int(drivers["HomeLongBreakDetected"] or 0),
            "AwayLongBreakDetected": int(drivers["AwayLongBreakDetected"] or 0),
            "HomeRestartReady": int(drivers["HomeRestartReady"] or 0),
            "AwayRestartReady": int(drivers["AwayRestartReady"] or 0),
            "HomeRestartNotReady": int(drivers["HomeRestartNotReady"] or 0),
            "AwayRestartNotReady": int(drivers["AwayRestartNotReady"] or 0),
        })

    dataset.sort(
        key=lambda row: (
            row["EffectiveDate"],
            row["LeagueId"],
            row["Home"],
            row["Away"],
        )
    )

    return dataset, skipped


def default_config() -> dict:
    """Configurazione neutra iniziale."""
    return {
        "StrongDefenseThreshold": 4.5,
        "LowRecentPPGThreshold": 0.60,
        "VulnerableDefenseThreshold": 8.0,
        "HighRecentPPGThreshold": 1.40,
        "StrongDefenseWeight": 0.0,
        "RecentFormWeight": 0.0,
        "RestartWeight": 0.0,
        "VulnerableDefensesBonusWeight": 0.0,
        "StrongRecentFormBonusWeight": 0.0,
        "RestartReadyBonusWeight": 0.0,
        "MaxTotalPenalty": 4.0,
        "MaxTotalBonus": 2.0,
    }


def simulate(row: dict, config: dict) -> dict:
    """Applica soglie e pesi a una prediction storica."""
    home_def = row["HomeDefenseWeaknessScore"]
    away_def = row["AwayDefenseWeaknessScore"]
    home_ppg = row["HomePPGLast5"]
    away_ppg = row["AwayPPGLast5"]

    strong_defense_signal = float(
        home_def is not None
        and away_def is not None
        and min(home_def, away_def) <= config["StrongDefenseThreshold"]
    )

    recent_form_signal = float(
        home_ppg is not None
        and away_ppg is not None
        and home_ppg <= config["LowRecentPPGThreshold"]
        and away_ppg <= config["LowRecentPPGThreshold"]
    )

    restart_signal = float(
        min(
            row["HomeRestartNotReady"] + row["AwayRestartNotReady"],
            2,
        )
    )

    vulnerable_defenses_signal = float(
        home_def is not None
        and away_def is not None
        and home_def >= config["VulnerableDefenseThreshold"]
        and away_def >= config["VulnerableDefenseThreshold"]
    )

    strong_recent_form_signal = float(
        home_ppg is not None
        and away_ppg is not None
        and home_ppg >= config["HighRecentPPGThreshold"]
        and away_ppg >= config["HighRecentPPGThreshold"]
    )

    restart_ready_signal = float(
        row["HomeLongBreakDetected"] == 1
        and row["AwayLongBreakDetected"] == 1
        and row["HomeRestartReady"] == 1
        and row["AwayRestartReady"] == 1
    )

    strong_defense_penalty = (
        strong_defense_signal * config["StrongDefenseWeight"]
    )
    recent_form_penalty = (
        recent_form_signal * config["RecentFormWeight"]
    )
    restart_penalty = (
        restart_signal * config["RestartWeight"]
    )

    total_penalty = min(
        strong_defense_penalty + recent_form_penalty + restart_penalty,
        config["MaxTotalPenalty"],
    )

    vulnerable_defenses_bonus = (
        vulnerable_defenses_signal
        * config["VulnerableDefensesBonusWeight"]
    )
    strong_recent_form_bonus = (
        strong_recent_form_signal
        * config["StrongRecentFormBonusWeight"]
    )
    restart_ready_bonus = (
        restart_ready_signal
        * config["RestartReadyBonusWeight"]
    )

    total_bonus = min(
        vulnerable_defenses_bonus
        + strong_recent_form_bonus
        + restart_ready_bonus,
        config["MaxTotalBonus"],
    )

    simulated_score = round(
        row["BaseScore"] - total_penalty + total_bonus,
        4,
    )

    return {
        **row,
        "StrongDefenseSignal": strong_defense_signal,
        "RecentFormSignal": recent_form_signal,
        "RestartSignal": restart_signal,
        "VulnerableDefensesBonusSignal": vulnerable_defenses_signal,
        "StrongRecentFormBonusSignal": strong_recent_form_signal,
        "RestartReadyBonusSignal": restart_ready_signal,
        "TotalPenalty": round(total_penalty, 4),
        "TotalBonus": round(total_bonus, 4),
        "SimulatedScore": simulated_score,
        "SimulatedBand": score_to_band(simulated_score),
    }


def evaluate(dataset: list[dict], config: dict):
    """Calcola precisione, copertura e cambi di fascia."""
    rows = [simulate(row, config) for row in dataset]

    baseline_alta = [row for row in rows if row["BaseBand"] == "ALTA"]
    simulated_alta = [row for row in rows if row["SimulatedBand"] == "ALTA"]

    def counts(selected):
        ok = sum(row["Outcome"] == "OK" for row in selected)
        ko = sum(row["Outcome"] == "KO" for row in selected)
        total = ok + ko
        precision = ok / total * 100.0 if total else 0.0
        return ok, ko, total, precision

    b_ok, b_ko, b_total, b_precision = counts(baseline_alta)
    s_ok, s_ko, s_total, s_precision = counts(simulated_alta)

    ko_avoided = sum(
        row["BaseBand"] == "ALTA"
        and row["Outcome"] == "KO"
        and row["SimulatedBand"] != "ALTA"
        for row in rows
    )

    ok_lost = sum(
        row["BaseBand"] == "ALTA"
        and row["Outcome"] == "OK"
        and row["SimulatedBand"] != "ALTA"
        for row in rows
    )

    ok_promoted = sum(
        row["BaseBand"] != "ALTA"
        and row["Outcome"] == "OK"
        and row["SimulatedBand"] == "ALTA"
        for row in rows
    )

    ko_promoted = sum(
        row["BaseBand"] != "ALTA"
        and row["Outcome"] == "KO"
        and row["SimulatedBand"] == "ALTA"
        for row in rows
    )

    protective_balance = ko_avoided - ok_lost
    promotion_balance = ok_promoted - ko_promoted
    net_gain = protective_balance + promotion_balance
    coverage = s_total / b_total * 100.0 if b_total else 0.0

    return {
        **config,
        "BaselineAltaOK": b_ok,
        "BaselineAltaKO": b_ko,
        "BaselineAltaTotal": b_total,
        "BaselineAltaPrecision": round(b_precision, 4),
        "SimulatedAltaOK": s_ok,
        "SimulatedAltaKO": s_ko,
        "SimulatedAltaTotal": s_total,
        "SimulatedAltaPrecision": round(s_precision, 4),
        "AltaCoverage": round(coverage, 4),
        "AltaKOAvoided": ko_avoided,
        "AltaOKLost": ok_lost,
        "ProtectiveBalance": protective_balance,
        "AltaOKPromoted": ok_promoted,
        "AltaKOPromoted": ko_promoted,
        "PromotionBalance": promotion_balance,
        "NetGain": net_gain,
    }, rows


def better(candidate: dict, current: dict) -> bool:
    """Decide se una configurazione migliora abbastanza la precedente."""
    if candidate["AltaCoverage"] < MIN_COVERAGE:
        return False

    gain_delta = candidate["NetGain"] - current["NetGain"]
    precision_delta = (
        candidate["SimulatedAltaPrecision"]
        - current["SimulatedAltaPrecision"]
    )

    return (
        gain_delta >= 1
        or (gain_delta >= 0 and precision_delta >= 0.25)
    )


def stage_candidates(stage: str, current: dict) -> list[dict]:
    """Genera poche configurazioni per una singola fase."""
    result = []

    if stage == "strong_defense":
        for threshold in (3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0):
            for weight in (0.0, 0.5, 1.0, 1.5, 2.0):
                cfg = deepcopy(current)
                cfg["StrongDefenseThreshold"] = threshold
                cfg["StrongDefenseWeight"] = weight
                result.append(cfg)

    elif stage == "recent_form":
        for threshold in (0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00):
            for weight in (0.0, 0.5, 1.0, 1.5, 2.0):
                cfg = deepcopy(current)
                cfg["LowRecentPPGThreshold"] = threshold
                cfg["RecentFormWeight"] = weight
                result.append(cfg)

    elif stage == "restart":
        for weight in (0.0, 0.5, 1.0, 1.5, 2.0):
            cfg = deepcopy(current)
            cfg["RestartWeight"] = weight
            result.append(cfg)

    elif stage == "vulnerable_defenses_bonus":
        for threshold in (7.0, 7.5, 8.0, 8.5, 9.0):
            for weight in (0.0, 0.5, 1.0):
                cfg = deepcopy(current)
                cfg["VulnerableDefenseThreshold"] = threshold
                cfg["VulnerableDefensesBonusWeight"] = weight
                result.append(cfg)

    elif stage == "strong_recent_form_bonus":
        for threshold in (1.20, 1.40, 1.60, 1.80, 2.00):
            for weight in (0.0, 0.5, 1.0):
                cfg = deepcopy(current)
                cfg["HighRecentPPGThreshold"] = threshold
                cfg["StrongRecentFormBonusWeight"] = weight
                result.append(cfg)

    elif stage == "max_penalty":
        for value in (2.0, 3.0, 4.0, 5.0):
            cfg = deepcopy(current)
            cfg["MaxTotalPenalty"] = value
            result.append(cfg)

    elif stage == "max_bonus":
        for value in (1.0, 2.0, 3.0):
            cfg = deepcopy(current)
            cfg["MaxTotalBonus"] = value
            result.append(cfg)

    return result


def run_stage(stage: str, train: list[dict], current_cfg: dict, current_sum: dict):
    """Ottimizza una sola fase e restituisce anche il report completo."""
    results = []

    for cfg in stage_candidates(stage, current_cfg):
        summary, _ = evaluate(train, cfg)
        summary["Stage"] = stage
        results.append(summary)

    results.sort(
        key=lambda row: (
            -row["NetGain"],
            -row["ProtectiveBalance"],
            -row["PromotionBalance"],
            -row["SimulatedAltaPrecision"],
            -row["AltaCoverage"],
        )
    )

    best = results[0]
    accepted = better(best, current_sum)

    for row in results:
        row["Accepted"] = "YES" if accepted and row is best else "NO"

    if accepted:
        next_cfg = {key: best[key] for key in current_cfg}
        return next_cfg, best, results

    return current_cfg, current_sum, results


def main() -> None:
    """Esegue il processo completo."""
    parser = argparse.ArgumentParser()

    parser.add_argument("--engine", required=True)
    parser.add_argument("--ranking-file", type=Path)
    parser.add_argument("--drivers-file", type=Path, default=DEFAULT_DRIVERS)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--train-ratio", type=float, default=0.70)
    parser.add_argument("--exclude-australia", action="store_true")

    args = parser.parse_args()

    engine = text(args.engine)

    ranking_file = args.ranking_file or Path(
        f"data/storico/ranking/{engine}/storico_ranking_{engine}.csv"
    )

    output_dir = args.output_dir or Path(
        f"analysis/experiments/output/parameter_optimizer_{engine}"
    )

    ranking_rows = read_csv(ranking_file)
    driver_rows = read_csv(args.drivers_file)
    drivers_index = pivot_drivers(driver_rows)

    dataset, skipped = build_dataset(
        ranking_rows,
        drivers_index,
        args.exclude_australia,
    )

    if len(dataset) < 20:
        raise ValueError("Campione utilizzabile troppo piccolo.")

    split_index = int(len(dataset) * args.train_ratio)
    split_index = max(1, min(split_index, len(dataset) - 1))

    train = dataset[:split_index]
    validation = dataset[split_index:]

    current_cfg = default_config()
    current_sum, _ = evaluate(train, current_cfg)

    write_csv(output_dir / "01_baseline.csv", [current_sum])

    accepted_stages = []
    rejected_stages = []

    for stage, filename in STAGES:
        next_cfg, next_sum, rows = run_stage(
            stage,
            train,
            current_cfg,
            current_sum,
        )

        write_csv(output_dir / filename, rows)

        if next_cfg != current_cfg:
            accepted_stages.append(stage)
            current_cfg = next_cfg
            current_sum = next_sum
        else:
            rejected_stages.append(stage)

    train_summary, _ = evaluate(train, current_cfg)
    validation_summary, validation_rows = evaluate(validation, current_cfg)

    final_row = {
        **current_cfg,
        **{f"Train{key}": value for key, value in train_summary.items()
           if key not in current_cfg},
        **{f"Validation{key}": value for key, value in validation_summary.items()
           if key not in current_cfg},
    }

    write_csv(output_dir / "09_final_configuration.csv", [final_row])
    write_csv(output_dir / "10_validation_summary.csv", [validation_summary])

    changed = [
        row for row in validation_rows
        if row["BaseBand"] != row["SimulatedBand"]
    ]
    write_csv(output_dir / "11_changed_matches_validation.csv", changed)

    signal_fields = [
        ("StrongDefense", "StrongDefenseSignal"),
        ("RecentForm", "RecentFormSignal"),
        ("Restart", "RestartSignal"),
        ("VulnerableDefensesBonus", "VulnerableDefensesBonusSignal"),
        ("StrongRecentFormBonus", "StrongRecentFormBonusSignal"),
        ("RestartReadyBonus", "RestartReadyBonusSignal"),
    ]

    all_simulated = [simulate(row, current_cfg) for row in dataset]
    activation_rows = []

    for signal, field in signal_fields:
        active = [row for row in all_simulated if row[field] > 0]
        ok_count = sum(row["Outcome"] == "OK" for row in active)
        ko_count = sum(row["Outcome"] == "KO" for row in active)
        total = ok_count + ko_count

        activation_rows.append({
            "Signal": signal,
            "Occurrences": total,
            "OK": ok_count,
            "KO": ko_count,
            "Precision": round(ok_count / total * 100.0, 4) if total else 0.0,
        })

    write_csv(
        output_dir / "12_signal_activation_summary.csv",
        activation_rows,
    )
    write_csv(output_dir / "13_skipped_matches.csv", skipped)

    notes = [
        f"GioOver2.5 Parameter Optimizer - {engine}",
        "",
        f"Dataset: {len(dataset)}",
        f"TRAIN: {len(train)}",
        f"VALIDATION: {len(validation)}",
        "",
        "Fasi accettate: "
        + (", ".join(accepted_stages) if accepted_stages else "nessuna"),
        "Fasi respinte: "
        + (", ".join(rejected_stages) if rejected_stages else "nessuna"),
        "",
        "VALIDATION",
        f"NetGain: {validation_summary['NetGain']}",
        (
            "Precisione ALTA: "
            f"{validation_summary['BaselineAltaPrecision']}% -> "
            f"{validation_summary['SimulatedAltaPrecision']}%"
        ),
        f"Copertura ALTA: {validation_summary['AltaCoverage']}%",
        "",
        "Una configurazione positiva solo sul TRAIN non va adottata.",
    ]

    (output_dir / "14_optimizer_notes.txt").write_text(
        "\n".join(notes),
        encoding="utf-8",
    )

    print()
    print("=== PARAMETER OPTIMIZER ===")
    print(f"Engine               : {engine}")
    print(f"Dataset              : {len(dataset)}")
    print(f"TRAIN                : {len(train)}")
    print(f"VALIDATION           : {len(validation)}")
    print(f"Fasi accettate       : {', '.join(accepted_stages) or 'nessuna'}")
    print(f"Fasi respinte        : {', '.join(rejected_stages) or 'nessuna'}")
    print(f"VALIDATION NetGain   : {validation_summary['NetGain']}")
    print(
        "Precisione ALTA     : "
        f"{validation_summary['BaselineAltaPrecision']}% -> "
        f"{validation_summary['SimulatedAltaPrecision']}%"
    )
    print(f"Copertura ALTA       : {validation_summary['AltaCoverage']}%")
    print(f"Output               : {output_dir.resolve()}")


if __name__ == "__main__":
    main()
