from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REGISTRY_FILE = Path("data/league_registry.csv")
RESULTS_DIR = Path("data/storico/risultati")
STANDINGS_DIR = Path("data/storico/classifiche_calcolate")
RANKING_ROOT = Path("data/storico/ranking")
POSTPONED_FILE = Path("data/storico/partite_posticipate.csv")

AGGREGATES_DIR = Path("data/storico/aggregati_reset")
LEAGUE_STATS_FILE = AGGREGATES_DIR / "league_stats.csv"
ENGINE_STATS_FILE = AGGREGATES_DIR / "engine_league_stats.csv"
RESET_LOG_FILE = AGGREGATES_DIR / "reset_log.csv"

LEAGUE_STATS_FIELDS = [
    "ResetId", "ResetAt", "TargetMode", "TargetValue", "Country", "LeagueId",
    "CompletedMatches", "Over15", "Under15", "Over15Pct",
    "Over25", "Under25", "Over25Pct",
]

ENGINE_STATS_FIELDS = [
    "ResetId", "ResetAt", "TargetMode", "TargetValue", "Engine",
    "Country", "LeagueId", "Band", "OK", "KO", "Total", "HitRate",
]

RESET_LOG_FIELDS = [
    "ResetId", "ResetAt", "TargetMode", "TargetValue", "Country", "LeagueId",
    "CompletedMatchesArchived", "RankingRowsRemoved", "PostponedRowsRemoved",
    "ResultsFileRemoved", "StandingsFileRemoved",
]


@dataclass
class Plan:
    league_id: str
    country: str
    completed_matches: int
    results_exists: bool
    standings_exists: bool
    ranking_rows_by_engine: dict[str, int]
    postponed_rows: int

    @property
    def ranking_rows_total(self) -> int:
        return sum(self.ranking_rows_by_engine.values())


def text(value) -> str:
    return str(value or "").strip()


def detect_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,\t,").delimiter
    except csv.Error:
        return ";"


def read_csv(path: Path) -> tuple[list[str], list[dict]]:
    if not path.exists():
        return [], []

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=detect_delimiter(path))
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
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


def append_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    if not rows:
        return

    _, existing = read_csv(path)
    write_csv(path, fieldnames, existing + rows)


def row_value(row: dict, *names: str) -> str:
    lookup = {str(key).casefold(): value for key, value in row.items()}

    for name in names:
        if name.casefold() in lookup:
            return text(lookup[name.casefold()])

    return ""


def registry_rows() -> list[dict]:
    return read_csv(REGISTRY_FILE)[1]


def country_for_league(league_id: str, rows: list[dict]) -> str:
    for row in rows:
        current = row_value(row, "LeagueId", "league_id")

        if current.casefold() == league_id.casefold():
            return row_value(row, "Country", "country") or league_id.split("_", 1)[0]

    return league_id.split("_", 1)[0]


def engine_history_files() -> list[tuple[str, Path]]:
    histories: list[tuple[str, Path]] = []

    if not RANKING_ROOT.exists():
        return histories

    for engine_dir in sorted(RANKING_ROOT.iterdir()):
        if not engine_dir.is_dir():
            continue

        engine = engine_dir.name
        history_file = engine_dir / f"storico_ranking_{engine}.csv"

        if history_file.exists():
            histories.append((engine, history_file))

    return histories


def known_league_ids() -> set[str]:
    league_ids: set[str] = set()
    registry = registry_rows()

    for row in registry:
        league_id = row_value(row, "LeagueId", "league_id")
        if league_id:
            league_ids.add(league_id)

    for root in (RESULTS_DIR, STANDINGS_DIR):
        if root.exists():
            league_ids.update(path.stem for path in root.glob("*.csv"))

    if POSTPONED_FILE.exists():
        for row in read_csv(POSTPONED_FILE)[1]:
            league_id = text(row.get("LeagueId"))
            if league_id:
                league_ids.add(league_id)

    for _, history_file in engine_history_files():
        for row in read_csv(history_file)[1]:
            league_id = text(row.get("LeagueId"))
            if league_id:
                league_ids.add(league_id)

    return league_ids


def resolve_targets(
    league: str | None,
    group: str | None,
    country: str | None,
) -> list[tuple[str, str]]:
    registry = registry_rows()
    all_leagues = known_league_ids()

    if league:
        league_id = league.strip()
        return [(league_id, country_for_league(league_id, registry))]

    if group:
        prefix = group.strip().casefold()
        matching = sorted(
            league_id
            for league_id in all_leagues
            if league_id.casefold().startswith(prefix)
        )
        return [
            (league_id, country_for_league(league_id, registry))
            for league_id in matching
        ]

    assert country is not None
    wanted = country.strip()

    targets = []
    for league_id in sorted(all_leagues):
        resolved_country = country_for_league(league_id, registry)

        if (
            league_id.casefold().startswith(wanted.casefold() + "_")
            or resolved_country.casefold() == wanted.casefold()
        ):
            targets.append((league_id, resolved_country))

    return targets


def optional_int(value) -> int | None:
    raw = text(value)

    if not raw:
        return None

    try:
        return int(float(raw))
    except ValueError:
        return None


def calculate_league_stats(
    league_id: str,
    country: str,
    reset_id: str,
    reset_at: str,
    mode: str,
    target: str,
) -> dict | None:
    rows = read_csv(RESULTS_DIR / f"{league_id}.csv")[1]

    completed = 0
    over15 = 0
    over25 = 0

    for row in rows:
        hg = optional_int(row.get("HG"))
        ag = optional_int(row.get("AG"))

        if hg is None or ag is None:
            continue

        goals = hg + ag
        completed += 1
        over15 += int(goals >= 2)
        over25 += int(goals >= 3)

    if completed == 0:
        return None

    return {
        "ResetId": reset_id,
        "ResetAt": reset_at,
        "TargetMode": mode,
        "TargetValue": target,
        "Country": country,
        "LeagueId": league_id,
        "CompletedMatches": completed,
        "Over15": over15,
        "Under15": completed - over15,
        "Over15Pct": round(over15 / completed * 100, 2),
        "Over25": over25,
        "Under25": completed - over25,
        "Over25Pct": round(over25 / completed * 100, 2),
    }


def outcome_from_row(row: dict) -> str:
    outcome = text(row.get("Over25")).upper()

    if outcome in {"OK", "KO"}:
        return outcome

    hg = optional_int(row.get("HG"))
    ag = optional_int(row.get("AG"))

    if hg is None or ag is None:
        return ""

    return "OK" if hg + ag >= 3 else "KO"


def calculate_engine_stats(
    league_id: str,
    country: str,
    reset_id: str,
    reset_at: str,
    mode: str,
    target: str,
) -> tuple[list[dict], dict[str, int]]:
    aggregate_rows: list[dict] = []
    counts: dict[str, int] = {}

    for engine, history_file in engine_history_files():
        league_rows = [
            row
            for row in read_csv(history_file)[1]
            if text(row.get("LeagueId")).casefold() == league_id.casefold()
        ]

        counts[engine] = len(league_rows)

        by_band: dict[str, list[str]] = {}
        overall: list[str] = []

        for row in league_rows:
            outcome = outcome_from_row(row)
            if outcome not in {"OK", "KO"}:
                continue

            band = text(row.get("Band")).upper() or "SENZA_FASCIA"
            overall.append(outcome)
            by_band.setdefault(band, []).append(outcome)

        scopes = {"OVERALL": overall, **by_band}

        for band, outcomes in scopes.items():
            if not outcomes:
                continue

            ok = outcomes.count("OK")
            ko = outcomes.count("KO")
            total = ok + ko

            aggregate_rows.append(
                {
                    "ResetId": reset_id,
                    "ResetAt": reset_at,
                    "TargetMode": mode,
                    "TargetValue": target,
                    "Engine": engine,
                    "Country": country,
                    "LeagueId": league_id,
                    "Band": band,
                    "OK": ok,
                    "KO": ko,
                    "Total": total,
                    "HitRate": round(ok / total * 100, 2),
                }
            )

    return aggregate_rows, counts


def count_postponed(league_id: str) -> int:
    return sum(
        1
        for row in read_csv(POSTPONED_FILE)[1]
        if text(row.get("LeagueId")).casefold() == league_id.casefold()
    )


def build_plan(
    league_id: str,
    country: str,
    reset_id: str,
    reset_at: str,
    mode: str,
    target: str,
) -> tuple[Plan, dict | None, list[dict]]:
    league_stats = calculate_league_stats(
        league_id, country, reset_id, reset_at, mode, target
    )

    engine_stats, counts = calculate_engine_stats(
        league_id, country, reset_id, reset_at, mode, target
    )

    return (
        Plan(
            league_id=league_id,
            country=country,
            completed_matches=(
                int(league_stats["CompletedMatches"]) if league_stats else 0
            ),
            results_exists=(RESULTS_DIR / f"{league_id}.csv").exists(),
            standings_exists=(STANDINGS_DIR / f"{league_id}.csv").exists(),
            ranking_rows_by_engine=counts,
            postponed_rows=count_postponed(league_id),
        ),
        league_stats,
        engine_stats,
    )


def remove_from_rankings(league_id: str) -> int:
    removed_total = 0

    for _, history_file in engine_history_files():
        fieldnames, rows = read_csv(history_file)
        kept = [
            row
            for row in rows
            if text(row.get("LeagueId")).casefold() != league_id.casefold()
        ]

        removed = len(rows) - len(kept)

        if removed:
            write_csv(history_file, fieldnames, kept)
            removed_total += removed

    return removed_total


def remove_from_postponed(league_id: str) -> int:
    fieldnames, rows = read_csv(POSTPONED_FILE)

    if not rows:
        return 0

    kept = [
        row
        for row in rows
        if text(row.get("LeagueId")).casefold() != league_id.casefold()
    ]

    removed = len(rows) - len(kept)

    if removed:
        write_csv(POSTPONED_FILE, fieldnames, kept)

    return removed


def apply_one(
    plan: Plan,
    league_stats: dict | None,
    engine_stats: list[dict],
    reset_id: str,
    reset_at: str,
    mode: str,
    target: str,
) -> None:
    if league_stats:
        append_rows(LEAGUE_STATS_FILE, LEAGUE_STATS_FIELDS, [league_stats])

    if engine_stats:
        append_rows(ENGINE_STATS_FILE, ENGINE_STATS_FIELDS, engine_stats)

    results_file = RESULTS_DIR / f"{plan.league_id}.csv"
    standings_file = STANDINGS_DIR / f"{plan.league_id}.csv"

    results_removed = results_file.exists()
    standings_removed = standings_file.exists()

    if results_removed:
        results_file.unlink()

    if standings_removed:
        standings_file.unlink()

    ranking_removed = remove_from_rankings(plan.league_id)
    postponed_removed = remove_from_postponed(plan.league_id)

    append_rows(
        RESET_LOG_FILE,
        RESET_LOG_FIELDS,
        [
            {
                "ResetId": reset_id,
                "ResetAt": reset_at,
                "TargetMode": mode,
                "TargetValue": target,
                "Country": plan.country,
                "LeagueId": plan.league_id,
                "CompletedMatchesArchived": plan.completed_matches,
                "RankingRowsRemoved": ranking_removed,
                "PostponedRowsRemoved": postponed_removed,
                "ResultsFileRemoved": "SI" if results_removed else "NO",
                "StandingsFileRemoved": "SI" if standings_removed else "NO",
            }
        ],
    )


def print_plan(
    plans: list[Plan],
    reset_id: str,
    mode: str,
    target: str,
    apply: bool,
) -> None:
    print()
    print("=" * 68)
    print("RESET DATI GIOOVER2.5")
    print("=" * 68)
    print(f"ResetId: {reset_id}")
    print(f"Target: {mode} = {target}")
    print(f"Modalità: {'APPLICAZIONE REALE' if apply else 'DRY-RUN'}")
    print(f"Leghe selezionate: {len(plans)}")
    print()

    for plan in plans:
        print(f"- {plan.league_id}")
        print(f"  Nazione: {plan.country}")
        print(f"  Partite concluse da aggregare: {plan.completed_matches}")
        print(f"  File risultati presente: {'SI' if plan.results_exists else 'NO'}")
        print(f"  Classifica presente: {'SI' if plan.standings_exists else 'NO'}")
        print(f"  Righe ranking da rimuovere: {plan.ranking_rows_total}")
        print(f"  Righe posticipate da rimuovere: {plan.postponed_rows}")

        details = [
            f"{engine}={count}"
            for engine, count in plan.ranking_rows_by_engine.items()
            if count
        ]

        if details:
            print("  Breakdown ranking: " + ", ".join(details))

        print()

    if not apply:
        print("Nessun file è stato modificato.")
        print("Per eseguire davvero, rilancia con --apply.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Salva statistiche aggregate e resetta i dati attivi "
            "di una lega, di un gruppo di LeagueId o di una nazione."
        )
    )

    target_group = parser.add_mutually_exclusive_group(required=True)

    target_group.add_argument("--league", help="Una LeagueId esatta.")
    target_group.add_argument(
        "--group",
        help="Prefisso comune delle LeagueId, ad esempio Finland_Kolmonen.",
    )
    target_group.add_argument(
        "--country",
        help="Nazione da resettare completamente.",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Applica davvero il reset. Senza questa opzione esegue il dry-run.",
    )

    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.league:
        mode = "LEAGUE"
        target = args.league
    elif args.group:
        mode = "GROUP"
        target = args.group
    else:
        mode = "COUNTRY"
        target = args.country

    targets = resolve_targets(args.league, args.group, args.country)

    if not targets:
        print("Nessuna lega trovata per il target indicato.")
        return 2

    now = datetime.now()
    reset_id = now.strftime("%Y%m%d_%H%M%S")
    reset_at = now.isoformat(timespec="seconds")

    prepared = [
        build_plan(
            league_id,
            country,
            reset_id,
            reset_at,
            mode,
            str(target),
        )
        for league_id, country in targets
    ]

    plans = [item[0] for item in prepared]

    print_plan(plans, reset_id, mode, str(target), args.apply)

    if not args.apply:
        return 0

    for plan, league_stats, engine_stats in prepared:
        apply_one(
            plan,
            league_stats,
            engine_stats,
            reset_id,
            reset_at,
            mode,
            str(target),
        )
        print(f"[OK] Reset completato: {plan.league_id}")

    print()
    print("Reset completato.")
    print(f"Statistiche aggregate: {AGGREGATES_DIR}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
