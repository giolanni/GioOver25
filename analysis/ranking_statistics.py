"""Statistiche operative sugli storici ranking di GioOver2.5.

Il comando confronta gli engine sulla loro popolazione completa (``overall``)
oppure sul set di fixture presente in tutti gli engine selezionati (``common``).
Le finestre temporali usano MatchDate; PredictionDate viene usata soltanto per
le vecchie righe che non hanno MatchDate.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Callable, Iterable, Sequence


DEFAULT_HISTORY_ROOT = Path("data/storico/ranking")
FixtureKey = tuple[str, date, str, str]


@dataclass(frozen=True)
class HistoryMatch:
    engine: str
    prediction_date: date | None
    match_date: date
    league_id: str
    home: str
    away: str
    band: str
    home_goals: int
    away_goals: int
    over25: str
    used_legacy_date: bool = False

    @property
    def key(self) -> FixtureKey:
        return (self.league_id, self.match_date, self.home, self.away)

    @property
    def goals(self) -> int:
        return self.home_goals + self.away_goals


@dataclass(frozen=True)
class Metric:
    key: str
    title: str
    includes: Callable[[HistoryMatch], bool]
    is_ok: Callable[[HistoryMatch], bool]


@dataclass(frozen=True)
class Stat:
    ok: int
    ko: int

    @property
    def total(self) -> int:
        return self.ok + self.ko

    @property
    def percentage(self) -> float | None:
        if not self.total:
            return None
        return self.ok / self.total * 100.0


@dataclass(frozen=True)
class ReportRow:
    scope: str
    league_view: str
    engine: str
    metric: str
    ok: int
    ko: int
    total: int
    percentage: float | None
    population: int


METRICS: tuple[Metric, ...] = (
    Metric(
        "alta_o25",
        "ALTA O2.5",
        lambda row: row.band == "ALTA",
        lambda row: row.over25 == "OK",
    ),
    Metric(
        "imm_alta_o25",
        "IMM-ALTA O2.5",
        lambda row: row.band.startswith("IMM-ALTA-"),
        lambda row: row.over25 == "OK",
    ),
    Metric(
        "media_o15",
        "MEDIA O1.5",
        lambda row: row.band == "MEDIA",
        lambda row: row.goals >= 2,
    ),
    Metric(
        "media_alta_o15",
        "MEDIA-ALTA O1.5",
        lambda row: row.band == "MEDIA-ALTA",
        lambda row: row.goals >= 2,
    ),
    Metric(
        "media_totale_o15",
        "MEDIA+M-ALTA O1.5",
        lambda row: row.band in {"MEDIA", "MEDIA-ALTA"},
        lambda row: row.goals >= 2,
    ),
)
METRIC_BY_KEY = {metric.key: metric for metric in METRICS}


def parse_date(value: str) -> date:
    value = value.strip()
    for pattern in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            pass
    raise ValueError(
        f"Data non valida: {value!r}. Usa AAAA-MM-GG oppure GG/MM/AAAA."
    )


def _parse_optional_date(value: str) -> date | None:
    return parse_date(value) if value.strip() else None


def discover_engines(history_root: Path) -> list[str]:
    engines = []
    if not history_root.exists():
        raise FileNotFoundError(f"Cartella storici non trovata: {history_root}")

    for directory in history_root.iterdir():
        if not directory.is_dir():
            continue
        if (directory / f"storico_ranking_{directory.name}.csv").exists():
            engines.append(directory.name)
    return sorted(engines)


def load_engine_history(
    history_root: Path, engine: str
) -> tuple[list[HistoryMatch], int, int]:
    """Carica le sole righe concluse e le deduplica per fixture.

    Ritorna ``(righe, righe_legacy, duplicati_scartati)``. In caso di doppia
    prediction per la stessa fixture viene conservata quella con PredictionDate
    più recente (e, a parità, l'ultima riga del file).
    """

    path = history_root / engine / f"storico_ranking_{engine}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Storico ranking non trovato: {path}")

    by_key: dict[FixtureKey, HistoryMatch] = {}
    legacy_rows = 0
    duplicates = 0

    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        required = {"PredictionDate", "MatchDate", "LeagueId", "Home", "Away", "Band", "HG", "AG", "Over25"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"{path}: colonne mancanti: {', '.join(sorted(missing))}"
            )

        for line_number, raw in enumerate(reader, start=2):
            over25 = (raw.get("Over25") or "").strip().upper()
            if over25 not in {"OK", "KO"}:
                continue

            try:
                home_goals = int((raw.get("HG") or "").strip())
                away_goals = int((raw.get("AG") or "").strip())
            except ValueError:
                continue

            match_date_text = (raw.get("MatchDate") or "").strip()
            prediction_text = (raw.get("PredictionDate") or "").strip()
            used_legacy_date = not bool(match_date_text)
            effective_date_text = match_date_text or prediction_text
            if not effective_date_text:
                continue

            try:
                match_date = parse_date(effective_date_text)
                prediction_date = _parse_optional_date(prediction_text)
            except ValueError as exc:
                raise ValueError(f"{path}:{line_number}: {exc}") from exc

            match = HistoryMatch(
                engine=engine,
                prediction_date=prediction_date,
                match_date=match_date,
                league_id=(raw.get("LeagueId") or "").strip(),
                home=(raw.get("Home") or "").strip(),
                away=(raw.get("Away") or "").strip(),
                band=(raw.get("Band") or "").strip().upper(),
                home_goals=home_goals,
                away_goals=away_goals,
                over25=over25,
                used_legacy_date=used_legacy_date,
            )

            if match.key in by_key:
                duplicates += 1
                previous = by_key[match.key]
                previous_date = previous.prediction_date or date.min
                current_date = match.prediction_date or date.min
                if current_date < previous_date:
                    continue
            by_key[match.key] = match
            legacy_rows += int(used_legacy_date)

    return list(by_key.values()), legacy_rows, duplicates


def filter_dates(
    rows: Iterable[HistoryMatch],
    dates: set[date] | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list[HistoryMatch]:
    output = []
    for row in rows:
        if dates is not None and row.match_date not in dates:
            continue
        if start_date is not None and row.match_date < start_date:
            continue
        if end_date is not None and row.match_date > end_date:
            continue
        output.append(row)
    return output


def remove_australia(rows: Iterable[HistoryMatch]) -> list[HistoryMatch]:
    return [row for row in rows if not row.league_id.startswith("Australia_")]


def common_keys(
    histories: dict[str, list[HistoryMatch]],
) -> tuple[set[FixtureKey], int]:
    if not histories:
        return set(), 0

    mappings = {
        engine: {row.key: row for row in rows}
        for engine, rows in histories.items()
    }
    keys = set.intersection(*(set(mapping) for mapping in mappings.values()))

    inconsistent: set[FixtureKey] = set()
    for key in keys:
        results = {
            (mapping[key].home_goals, mapping[key].away_goals)
            for mapping in mappings.values()
        }
        if len(results) != 1:
            inconsistent.add(key)
    return keys.difference(inconsistent), len(inconsistent)


def calculate_stat(rows: Iterable[HistoryMatch], metric: Metric) -> Stat:
    selected = [row for row in rows if metric.includes(row)]
    ok = sum(metric.is_ok(row) for row in selected)
    return Stat(ok=ok, ko=len(selected) - ok)


def build_report(
    histories: dict[str, list[HistoryMatch]],
    metrics: Sequence[Metric],
    scopes: Sequence[str],
    league_views: Sequence[str],
) -> tuple[list[ReportRow], dict[tuple[str, str], int], dict[str, int]]:
    report: list[ReportRow] = []
    populations: dict[tuple[str, str], int] = {}
    inconsistent_by_view: dict[str, int] = {}

    for league_view in league_views:
        visible = {
            engine: (
                remove_australia(rows)
                if league_view == "no-australia"
                else list(rows)
            )
            for engine, rows in histories.items()
        }
        shared_keys, inconsistent = common_keys(visible)
        inconsistent_by_view[league_view] = inconsistent

        for scope in scopes:
            for engine, rows in visible.items():
                population_rows = (
                    [row for row in rows if row.key in shared_keys]
                    if scope == "common"
                    else rows
                )
                populations[(f"{scope}:{league_view}", engine)] = len(population_rows)
                for metric in metrics:
                    stat = calculate_stat(population_rows, metric)
                    report.append(
                        ReportRow(
                            scope=scope,
                            league_view=league_view,
                            engine=engine,
                            metric=metric.key,
                            ok=stat.ok,
                            ko=stat.ko,
                            total=stat.total,
                            percentage=stat.percentage,
                            population=len(population_rows),
                        )
                    )

    return report, populations, inconsistent_by_view


def _format_stat(row: ReportRow | None) -> str:
    if row is None or row.percentage is None:
        return "-"
    return f"{row.ok}/{row.total} ({row.percentage:.2f}%)"


def _print_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> None:
    widths = [len(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(value))

    def render(row: Sequence[str]) -> str:
        return " | ".join(value.ljust(widths[index]) for index, value in enumerate(row))

    print(render(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(render(row))


def print_report(
    report: Sequence[ReportRow],
    metrics: Sequence[Metric],
    scopes: Sequence[str],
    league_views: Sequence[str],
    sort_by: str,
    period_label: str,
    inconsistent_by_view: dict[str, int],
) -> None:
    index = {
        (row.scope, row.league_view, row.engine, row.metric): row
        for row in report
    }
    engines = sorted({row.engine for row in report})

    print(f"\nPeriodo: {period_label}")
    for league_view in league_views:
        for scope in scopes:
            ranking = []
            for engine in engines:
                primary = index.get((scope, league_view, engine, sort_by))
                percentage = primary.percentage if primary and primary.percentage is not None else -1.0
                total = primary.total if primary else 0
                ranking.append((engine, percentage, total))
            ranking.sort(key=lambda item: (-item[1], -item[2], item[0]))

            label_scope = "SET COMUNE" if scope == "common" else "GLOBALE PER ENGINE"
            label_leagues = "NO AUSTRALIA" if league_view == "no-australia" else "TUTTE LE LEGHE"
            print(f"\n{label_scope} - {label_leagues}")
            if scope == "common" and engines:
                first = index.get((scope, league_view, engines[0], metrics[0].key))
                population = first.population if first else 0
                print(f"Fixture nel set comune: {population}")
            if inconsistent_by_view.get(league_view):
                print(
                    "ATTENZIONE: escluse dal set comune fixture con risultati "
                    f"discordanti: {inconsistent_by_view[league_view]}"
                )

            table_rows = []
            for engine, _, _ in ranking:
                table_rows.append(
                    [engine]
                    + [
                        _format_stat(index.get((scope, league_view, engine, metric.key)))
                        for metric in metrics
                    ]
                )
            _print_table(["Engine"] + [metric.title for metric in metrics], table_rows)


def export_report(
    path: Path,
    cumulative_report: Sequence[ReportRow],
    cumulative_label: str,
    daily_reports: Sequence[tuple[date, Sequence[ReportRow]]] = (),
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        fieldnames = [
            "PeriodType",
            "Period",
            "Scope",
            "LeagueView",
            "Engine",
            "Metric",
            "OK",
            "KO",
            "N",
            "Pct",
            "Population",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()

        def write_rows(
            period_type: str,
            period: str,
            rows: Sequence[ReportRow],
        ) -> None:
            for row in rows:
                writer.writerow(
                    {
                        "PeriodType": period_type,
                        "Period": period,
                        "Scope": row.scope,
                        "LeagueView": row.league_view,
                        "Engine": row.engine,
                        "Metric": row.metric,
                        "OK": row.ok,
                        "KO": row.ko,
                        "N": row.total,
                        "Pct": "" if row.percentage is None else f"{row.percentage:.2f}",
                        "Population": row.population,
                    }
                )

        write_rows("CUMULATIVE", cumulative_label, cumulative_report)
        for selected_day, daily_report in daily_reports:
            write_rows("DAILY", selected_day.isoformat(), daily_report)


def _scope_values(value: str) -> list[str]:
    return ["overall", "common"] if value == "both" else [value]


def _league_values(value: str) -> list[str]:
    return ["all", "no-australia"] if value == "both" else [value]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Statistiche ALTA O2.5 e MEDIA/MEDIA-ALTA O1.5 dagli storici ranking."
    )
    parser.add_argument(
        "--engines",
        nargs="+",
        help="Engine da confrontare (default: tutti gli storici disponibili).",
    )
    parser.add_argument(
        "--scope",
        choices=("overall", "common", "both"),
        default="both",
        help="Popolazione per engine, set comune o entrambe (default: both).",
    )
    parser.add_argument(
        "--dates",
        nargs="+",
        metavar="DATA",
        help="Date specifiche, formato AAAA-MM-GG o GG/MM/AAAA.",
    )
    parser.add_argument("--last-days", type=int, metavar="N", help="Ultimi N giorni di calendario con termine nell'ultima data disponibile.")
    parser.add_argument("--start-date", help="Inizio intervallo incluso.")
    parser.add_argument("--end-date", help="Fine intervallo incluso.")
    parser.add_argument(
        "--league-view",
        choices=("all", "no-australia", "both"),
        default="all",
        help="Tutte le leghe, senza Australia o entrambe (default: all).",
    )
    parser.add_argument(
        "--metrics",
        nargs="+",
        choices=tuple(METRIC_BY_KEY),
        default=[metric.key for metric in METRICS],
        help="Metriche da mostrare (default: tutte).",
    )
    parser.add_argument(
        "--sort-by",
        choices=tuple(METRIC_BY_KEY),
        default="alta_o25",
        help="Metrica primaria della classifica; percentuale prima, volume poi.",
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Mostra anche il dettaglio separato per ciascuna MatchDate selezionata.",
    )
    parser.add_argument("--csv", type=Path, help="Salva anche il dettaglio in CSV.")
    parser.add_argument(
        "--history-root",
        type=Path,
        default=DEFAULT_HISTORY_ROOT,
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.last_days is not None and args.last_days <= 0:
        parser.error("--last-days deve essere maggiore di zero")
    if args.dates and (args.last_days is not None or args.start_date or args.end_date):
        parser.error("--dates non può essere combinato con intervalli o --last-days")
    if args.last_days is not None and (args.start_date or args.end_date):
        parser.error("--last-days non può essere combinato con --start-date/--end-date")

    available = discover_engines(args.history_root)
    engines = args.engines or available
    unknown = sorted(set(engines).difference(available))
    if unknown:
        parser.error(f"Storici non trovati per: {', '.join(unknown)}")

    histories: dict[str, list[HistoryMatch]] = {}
    duplicate_total = 0
    for engine in engines:
        rows, _, duplicates = load_engine_history(args.history_root, engine)
        histories[engine] = rows
        duplicate_total += duplicates

    explicit_dates = {parse_date(value) for value in args.dates} if args.dates else None
    start_date = parse_date(args.start_date) if args.start_date else None
    end_date = parse_date(args.end_date) if args.end_date else None
    if start_date and end_date and start_date > end_date:
        parser.error("--start-date non può essere successiva a --end-date")

    if args.last_days is not None:
        latest = max(
            (row.match_date for rows in histories.values() for row in rows),
            default=None,
        )
        if latest is None:
            parser.error("Nessuna partita conclusa negli storici selezionati")
        end_date = latest
        start_date = latest - timedelta(days=args.last_days - 1)

    histories = {
        engine: filter_dates(rows, explicit_dates, start_date, end_date)
        for engine, rows in histories.items()
    }
    legacy_total = sum(
        row.used_legacy_date for rows in histories.values() for row in rows
    )

    if explicit_dates is not None:
        period_label = ", ".join(value.isoformat() for value in sorted(explicit_dates))
    elif start_date or end_date:
        period_label = f"{start_date.isoformat() if start_date else 'inizio'} -> {end_date.isoformat() if end_date else 'ultima data'}"
    else:
        period_label = "intero storico di ciascun engine"

    metrics = [METRIC_BY_KEY[key] for key in args.metrics]
    if args.sort_by not in args.metrics:
        parser.error("--sort-by deve essere compreso nelle metriche richieste con --metrics")
    scopes = _scope_values(args.scope)
    league_views = _league_values(args.league_view)
    report, _, inconsistent = build_report(histories, metrics, scopes, league_views)

    print_report(
        report,
        metrics,
        scopes,
        league_views,
        args.sort_by,
        period_label,
        inconsistent,
    )
    daily_reports: list[tuple[date, Sequence[ReportRow]]] = []
    if args.daily:
        selected_days = (
            sorted(explicit_dates)
            if explicit_dates is not None
            else sorted({row.match_date for rows in histories.values() for row in rows})
        )
        for selected_day in selected_days:
            daily_histories = {
                engine: [row for row in rows if row.match_date == selected_day]
                for engine, rows in histories.items()
            }
            daily_report, _, daily_inconsistent = build_report(
                daily_histories, metrics, scopes, league_views
            )
            daily_reports.append((selected_day, daily_report))
            if len(selected_days) > 1:
                print_report(
                    daily_report,
                    metrics,
                    scopes,
                    league_views,
                    args.sort_by,
                    selected_day.isoformat(),
                    daily_inconsistent,
                )
    if legacy_total:
        print(f"\nNota: {legacy_total} righe legacy hanno usato PredictionDate perché MatchDate era vuota.")
    if duplicate_total:
        print(f"Nota: {duplicate_total} duplicati di fixture sono stati deduplicati.")
    if args.csv:
        export_report(args.csv, report, period_label, daily_reports)
        print(f"\nCSV creato: {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
