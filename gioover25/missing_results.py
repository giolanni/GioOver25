from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


EMPTY_VALUES = {"", "nan", "none", "null", "n/a", "na", "-"}
VALID_RESULTS = {"OK", "KO"}

COLUMN_ALIASES = {
    "league_id": ("LeagueId", "league_id", "League", "league"),
    "season": ("Season", "season"),
    "round": ("Round", "round", "MatchRound", "match_round"),
    "match_date": ("MatchDate", "Date", "match_date", "date"),
    "prediction_date": ("PredictionDate", "prediction_date"),
    "home": ("Home", "home", "HomeTeam", "home_team"),
    "away": ("Away", "away", "AwayTeam", "away_team"),
    "band": ("Band", "band", "Fascia", "fascia"),
    "result": ("Over25", "over25", "Result", "result", "Esito", "esito"),
    "home_goals": ("HG", "home_goals", "HomeGoals", "home_score"),
    "away_goals": ("AG", "away_goals", "AwayGoals", "away_score"),
}


@dataclass(frozen=True)
class MissingMatch:
    league_id: str
    season: str
    round: str
    match_date: str
    prediction_date: str
    home: str
    away: str
    band: str
    source_file: str

    @property
    def identity(self) -> Tuple[str, str, str, str]:
        return (
            self.league_id.strip().casefold(),
            self.season.strip().casefold(),
            self.home.strip().casefold(),
            self.away.strip().casefold(),
        )


def normalize(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def is_empty(value: object) -> bool:
    return normalize(value).casefold() in EMPTY_VALUES


def resolve_column(fieldnames: Sequence[str], logical_name: str) -> Optional[str]:
    lookup = {name.casefold(): name for name in fieldnames if name}
    for alias in COLUMN_ALIASES[logical_name]:
        if alias.casefold() in lookup:
            return lookup[alias.casefold()]
    return None


def detect_delimiter(path: Path) -> str:
    sample = path.read_text(encoding="utf-8-sig", errors="replace")[:4096]
    try:
        return csv.Sniffer().sniff(sample, delimiters=";,\t,").delimiter
    except csv.Error:
        return ";"


def read_missing_from_file(path: Path) -> List[MissingMatch]:
    delimiter = detect_delimiter(path)

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if not reader.fieldnames:
            return []

        columns: Dict[str, Optional[str]] = {
            key: resolve_column(reader.fieldnames, key)
            for key in COLUMN_ALIASES
        }

        required = ("home", "away", "result")
        missing_required = [key for key in required if not columns[key]]
        if missing_required:
            print(
                f"[AVVISO] Ignorato {path}: colonne mancanti "
                f"{', '.join(missing_required)}",
                file=sys.stderr,
            )
            return []

        rows: List[MissingMatch] = []

        for row in reader:
            result = normalize(row.get(columns["result"] or "", "")).upper()

            # Si considerano mancanti solo le righe senza OK/KO.
            if result in VALID_RESULTS:
                continue

            # Se HG e AG sono entrambi valorizzati, il risultato potrebbe non essere
            # stato ancora trasformato in OK/KO: lo segnaliamo comunque.
            home = normalize(row.get(columns["home"] or "", ""))
            away = normalize(row.get(columns["away"] or "", ""))

            if not home or not away:
                continue

            rows.append(
                MissingMatch(
                    league_id=normalize(row.get(columns["league_id"] or "", "")),
                    season=normalize(row.get(columns["season"] or "", "")),
                    round=normalize(row.get(columns["round"] or "", "")),
                    match_date=normalize(row.get(columns["match_date"] or "", "")),
                    prediction_date=normalize(
                        row.get(columns["prediction_date"] or "", "")
                    ),
                    home=home,
                    away=away,
                    band=normalize(row.get(columns["band"] or "", "")),
                    source_file=str(path),
                )
            )

        return rows


def find_csv_files(root: Path, pattern: str) -> List[Path]:
    if root.is_file():
        return [root] if root.suffix.lower() == ".csv" else []
    return sorted(path for path in root.rglob(pattern) if path.is_file())


def deduplicate(matches: Iterable[MissingMatch]) -> List[MissingMatch]:
    unique: Dict[Tuple[str, str, str, str], MissingMatch] = {}

    for match in matches:
        current = unique.get(match.identity)
        if current is None:
            unique[match.identity] = match
            continue

        # Preferisce la riga con data partita valorizzata; altrimenti l'ultima letta.
        if not current.match_date and match.match_date:
            unique[match.identity] = match
        elif current.match_date == match.match_date:
            unique[match.identity] = match

    return sorted(
        unique.values(),
        key=lambda item: (
            item.match_date or item.prediction_date,
            item.league_id,
            item.home,
            item.away,
        ),
    )


def filter_matches(
    matches: Iterable[MissingMatch],
    band: Optional[str],
    exclude_australia: bool,
) -> List[MissingMatch]:
    wanted_band = normalize(band).upper()

    output: List[MissingMatch] = []
    for match in matches:
        if wanted_band and normalize(match.band).upper() != wanted_band:
            continue
        if exclude_australia and match.league_id.casefold().startswith("australia_"):
            continue
        output.append(match)

    return output


def print_table(matches: Sequence[MissingMatch]) -> None:
    if not matches:
        print("Nessuna partita senza esito trovata.")
        return

    headers = (
        "MatchDate",
        "PredictionDate",
        "LeagueId",
        "Round",
        "Home",
        "Away",
        "Band",
    )

    rows = [
        (
            match.match_date,
            match.prediction_date,
            match.league_id,
            match.round,
            match.home,
            match.away,
            match.band,
        )
        for match in matches
    ]

    widths = [
        min(max(len(headers[i]), *(len(row[i]) for row in rows)), 42)
        for i in range(len(headers))
    ]

    def render(values: Sequence[str]) -> str:
        cells = []
        for index, value in enumerate(values):
            display = value
            if len(display) > widths[index]:
                display = display[: widths[index] - 1] + "…"
            cells.append(display.ljust(widths[index]))
        return " | ".join(cells)

    print(render(headers))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(render(row))

    print(f"\nTotale partite senza esito: {len(matches)}")


def export_csv(matches: Sequence[MissingMatch], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(
            [
                "LeagueId",
                "Season",
                "Round",
                "MatchDate",
                "PredictionDate",
                "Home",
                "Away",
                "Band",
                "SourceFile",
            ]
        )
        for match in matches:
            writer.writerow(
                [
                    match.league_id,
                    match.season,
                    match.round,
                    match.match_date,
                    match.prediction_date,
                    match.home,
                    match.away,
                    match.band,
                    match.source_file,
                ]
            )

    print(f"CSV creato: {output_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Elenca le partite presenti negli storici ranking che non hanno "
            "ancora esito Over25 = OK/KO."
        )
    )
    parser.add_argument(
        "--input",
        default="data/storico/ranking",
        help=(
            "Cartella o file CSV da analizzare. "
            "Default: data/storico/ranking"
        ),
    )
    parser.add_argument(
        "--pattern",
        default="storico_ranking*.csv",
        help="Pattern dei file CSV da cercare ricorsivamente.",
    )
    parser.add_argument(
        "--band",
        choices=("ALTA", "MEDIA", "BASSA"),
        help="Mostra solo una fascia specifica.",
    )
    parser.add_argument(
        "--exclude-australia",
        action="store_true",
        help="Esclude i LeagueId che iniziano con Australia_.",
    )
    parser.add_argument(
        "--no-deduplicate",
        action="store_true",
        help="Non elimina i duplicati della stessa partita tra più storici.",
    )
    parser.add_argument(
        "--csv",
        dest="csv_output",
        help="Esporta l'elenco in un file CSV separato da punto e virgola.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    root = Path(args.input)
    if not root.exists():
        print(f"Percorso non trovato: {root}", file=sys.stderr)
        return 2

    files = find_csv_files(root, args.pattern)
    if not files:
        print(
            f"Nessun file trovato in {root} con pattern {args.pattern}",
            file=sys.stderr,
        )
        return 3

    all_matches: List[MissingMatch] = []
    for path in files:
        all_matches.extend(read_missing_from_file(path))

    matches = (
        all_matches
        if args.no_deduplicate
        else deduplicate(all_matches)
    )
    matches = filter_matches(
        matches,
        band=args.band,
        exclude_australia=args.exclude_australia,
    )

    print_table(matches)

    if args.csv_output:
        export_csv(matches, Path(args.csv_output))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
