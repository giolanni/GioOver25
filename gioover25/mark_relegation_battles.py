"""
===============================================================================
GioOver2.5 - mark_relegation_battles.py  (v3)
===============================================================================

SCOPO
-----
Analizzare i ranking ATTIVI di tutti gli engine e marcare:

    PROX-RELEGATION

le partite in cui ENTRAMBE le squadre sono nelle ultime posizioni della
classifica.

Lo score NON viene modificato.

===============================================================================
PARAMETRI MODIFICABILI
===============================================================================

MIN_MATCHES_PLAYED = 10
    Entrambe le squadre devono avere almeno questo numero di gare giocate.

RELEGATION_PLACES = 4
    Numero di posizioni finali considerate "zona retrocessione".
    Con 12 squadre: posizioni 9-12.
    Con 10 squadre: posizioni 7-10.
    Con 14 squadre: posizioni 11-14.

FINAL_BAND = "PROX-RELEGATION"
    Etichetta finale assegnata.

USE_CALCULATED_STANDINGS_FIRST = True
    True  = prova PRIMA a leggere:
            data/storico/classifiche_calcolate/<LeagueId>.csv
            che è la fonte preferita per il run giornaliero.
    False = ricostruisce sempre la classifica dai risultati storici.

===============================================================================
PERCHE' QUESTA VERSIONE E' PIU' ROBUSTA
===============================================================================

La versione precedente ricostruiva sempre la classifica dai risultati e poteva
non coincidere con la classifica effettivamente usata/visualizzata nel progetto
(per tie-break, partite mancanti, rettifiche, nomi squadra, ecc.).

Questa versione:

1. prova a usare la classifica calcolata del progetto;
2. se non riesce a leggerla, ricostruisce dai risultati;
3. produce SEMPRE un file diagnostico per OGNI partita del ranking, anche se
   NON viene marcata, indicando il motivo.

===============================================================================
OUTPUT
===============================================================================

1) Partite trovate nell'ultimo run:
   data/debug/relegation_battle/relegation_battle_latest.csv

2) Storico cumulativo:
   data/debug/relegation_battle/relegation_battle_history.csv

3) Diagnostica completa:
   data/debug/relegation_battle/relegation_battle_diagnostics.csv

La diagnostica contiene anche le partite NON marcate e una colonna Decision:

    FLAGGED
    NO_STANDINGS
    HOME_NOT_FOUND
    AWAY_NOT_FOUND
    UNDER_MIN_MATCHES
    HOME_NOT_LAST_N
    AWAY_NOT_LAST_N
    INVALID_ROW

Se una partita che ti aspetti non viene marcata, cerca Home/Away in questo file:
vedrai subito il motivo.

===============================================================================
USO
===============================================================================

Dry-run:
    python -m gioover25.mark_relegation_battles

Applica:
    python -m gioover25.mark_relegation_battles --apply

Solo v25:
    python -m gioover25.mark_relegation_battles --engine v25

Solo v25 e applica:
    python -m gioover25.mark_relegation_battles --engine v25 --apply

===============================================================================
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from .team_names import normalize_team_name


OUTPUT_RANKING_ROOT = Path("data/output_ranking")
RESULTS_ROOT = Path("data/storico/risultati")
STANDINGS_ROOT = Path("data/storico/classifiche_calcolate")

DEBUG_DIR = Path("data/debug/relegation_battle")
LATEST_FILE = DEBUG_DIR / "relegation_battle_latest.csv"
HISTORY_FILE = DEBUG_DIR / "relegation_battle_history.csv"
DIAGNOSTICS_FILE = DEBUG_DIR / "relegation_battle_diagnostics.csv"


# ============================================================================
# PARAMETRI PRINCIPALI
# ============================================================================

MIN_MATCHES_PLAYED = 10
RELEGATION_PLACES = 4
FINAL_BAND = "PROX-RELEGATION"
USE_CALCULATED_STANDINGS_FIRST = True


FLAG_FIELDS = [
    "Engine",
    "SourceFile",
    "StandingsSource",
    "MatchDate",
    "LeagueId",
    "Home",
    "Away",
    "TeamsCount",
    "RelegationStartPosition",
    "HomePosition",
    "AwayPosition",
    "HomePlayed",
    "AwayPlayed",
    "HomePoints",
    "AwayPoints",
    "PointsGap",
    "OriginalBand",
    "FinalBand",
]

DIAGNOSTIC_FIELDS = FLAG_FIELDS + [
    "Decision",
]


def _detect_delimiter(path: Path) -> str:
    sample = path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    )[:4096]

    try:
        return csv.Sniffer().sniff(
            sample,
            delimiters=";,\t,",
        ).delimiter
    except csv.Error:
        return ";"


def _read_csv(path: Path) -> tuple[list[str], list[dict]]:
    if not path.exists():
        return [], []

    delimiter = _detect_delimiter(path)

    with path.open(
        "r",
        newline="",
        encoding="utf-8-sig",
    ) as handle:
        reader = csv.DictReader(
            handle,
            delimiter=delimiter,
        )
        return list(reader.fieldnames or []), list(reader)


def _write_csv(
    path: Path,
    fieldnames: list[str],
    rows: list[dict],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _parse_date(value) -> date | None:
    raw = str(value or "").strip()

    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _optional_int(value) -> int | None:
    raw = str(value or "").strip()

    if not raw:
        return None

    try:
        return int(float(raw))
    except (TypeError, ValueError):
        return None


def _first_value(row: dict, candidates: tuple[str, ...]):
    lookup = {
        str(key).strip().casefold(): value
        for key, value in row.items()
    }

    for candidate in candidates:
        key = candidate.casefold()
        if key in lookup:
            value = lookup[key]
            if str(value or "").strip() != "":
                return value

    return None


def _load_calculated_standings(
    league_id: str,
) -> dict[str, dict[str, int]] | None:
    """
    Legge in modo flessibile la classifica calcolata del progetto.

    Supporta nomi colonna comuni:
      Team / Squadra / Name
      Position / Pos / Rank
      Played / P / PG / Matches
      Points / Pts / PT / Punti

    Se Position non è presente ma Points sì, ricostruisce l'ordine per punti.
    """

    path = STANDINGS_ROOT / f"{league_id}.csv"

    if not path.exists():
        return None

    _, rows = _read_csv(path)

    if not rows:
        return None

    parsed: list[tuple[str, dict[str, int]]] = []

    for row in rows:
        team_raw = _first_value(
            row,
            (
                "Team",
                "Squadra",
                "Name",
                "Club",
            ),
        )

        if team_raw is None:
            continue

        position = _optional_int(
            _first_value(
                row,
                (
                    "Position",
                    "Pos",
                    "Rank",
                    "Posizione",
                ),
            )
        )

        played = _optional_int(
            _first_value(
                row,
                (
                    "Played",
                    "P",
                    "PG",
                    "Matches",
                    "Games",
                    "Giocate",
                ),
            )
        )

        points = _optional_int(
            _first_value(
                row,
                (
                    "Points",
                    "Pts",
                    "PT",
                    "Punti",
                ),
            )
        )

        if played is None or points is None:
            continue

        team = normalize_team_name(
            league_id,
            str(team_raw),
        )

        parsed.append(
            (
                team,
                {
                    "position": position or 0,
                    "played": played,
                    "points": points,
                },
            )
        )

    if not parsed:
        return None

    # Se tutte le posizioni sono valorizzate, manteniamo quelle.
    if all(
        values["position"] > 0
        for _, values in parsed
    ):
        return dict(parsed)

    # Fallback: ordina per punti.
    ordered = sorted(
        parsed,
        key=lambda item: (
            -item[1]["points"],
            item[0],
        ),
    )

    table = {}

    for position, (
        team,
        values,
    ) in enumerate(
        ordered,
        start=1,
    ):
        values["position"] = position
        table[team] = values

    return table


def _load_results(
    league_id: str,
) -> list[dict] | None:
    path = RESULTS_ROOT / f"{league_id}.csv"

    if not path.exists():
        return None

    _, rows = _read_csv(path)

    valid = []

    for row in rows:
        match_date = _parse_date(
            row.get("MatchDate")
        )

        hg = _optional_int(
            row.get("HG")
        )

        ag = _optional_int(
            row.get("AG")
        )

        if (
            match_date is None
            or hg is None
            or ag is None
        ):
            continue

        valid.append(
            {
                "date": match_date,
                "home": normalize_team_name(
                    league_id,
                    row.get("Home", ""),
                ),
                "away": normalize_team_name(
                    league_id,
                    row.get("Away", ""),
                ),
                "hg": hg,
                "ag": ag,
            }
        )

    valid.sort(
        key=lambda item: item["date"]
    )

    return valid


def _reconstruct_table(
    *,
    results: list[dict],
    before_date: date,
) -> dict[str, dict[str, int]]:
    table: dict[str, dict[str, int]] = {}

    def ensure(team: str) -> dict[str, int]:
        return table.setdefault(
            team,
            {
                "played": 0,
                "points": 0,
                "gf": 0,
                "ga": 0,
            },
        )

    for match in results:
        if match["date"] >= before_date:
            continue

        home = match["home"]
        away = match["away"]
        hg = match["hg"]
        ag = match["ag"]

        home_row = ensure(home)
        away_row = ensure(away)

        home_row["played"] += 1
        away_row["played"] += 1

        home_row["gf"] += hg
        home_row["ga"] += ag

        away_row["gf"] += ag
        away_row["ga"] += hg

        if hg > ag:
            home_row["points"] += 3
        elif hg < ag:
            away_row["points"] += 3
        else:
            home_row["points"] += 1
            away_row["points"] += 1

    ordered = sorted(
        table.items(),
        key=lambda item: (
            -item[1]["points"],
            -(item[1]["gf"] - item[1]["ga"]),
            -item[1]["gf"],
            item[0],
        ),
    )

    for position, (
        team,
        values,
    ) in enumerate(
        ordered,
        start=1,
    ):
        values["position"] = position

    return table


def _get_table(
    *,
    league_id: str,
    match_date: date,
    results_cache: dict[str, list[dict] | None],
    table_cache: dict[
        tuple[str, date],
        tuple[dict[str, dict[str, int]], str],
    ],
) -> tuple[
    dict[str, dict[str, int]] | None,
    str,
]:
    cache_key = (
        league_id,
        match_date,
    )

    if cache_key in table_cache:
        return table_cache[cache_key]

    if USE_CALCULATED_STANDINGS_FIRST:
        calculated = _load_calculated_standings(
            league_id
        )

        if calculated:
            result = (
                calculated,
                "CALCULATED_STANDINGS",
            )
            table_cache[cache_key] = result
            return result

    if league_id not in results_cache:
        results_cache[league_id] = _load_results(
            league_id
        )

    results = results_cache[league_id]

    if not results:
        return None, "NO_STANDINGS"

    reconstructed = _reconstruct_table(
        results=results,
        before_date=match_date,
    )

    if not reconstructed:
        return None, "NO_STANDINGS"

    result = (
        reconstructed,
        "RECONSTRUCTED_RESULTS",
    )

    table_cache[cache_key] = result

    return result


def _active_ranking_files(
    engine_filter: str | None,
) -> list[tuple[str, Path]]:
    files = []

    if not OUTPUT_RANKING_ROOT.exists():
        return files

    for engine_dir in sorted(
        OUTPUT_RANKING_ROOT.iterdir()
    ):
        if not engine_dir.is_dir():
            continue

        engine = engine_dir.name

        if (
            engine_filter
            and engine != engine_filter
        ):
            continue

        for path in sorted(
            engine_dir.glob("*.csv")
        ):
            files.append(
                (
                    engine,
                    path,
                )
            )

    return files


def _append_history(
    rows: list[dict],
) -> int:
    if not rows:
        return 0

    _, existing = _read_csv(
        HISTORY_FILE
    )

    existing_keys = {
        (
            str(row.get("Engine", "")).strip(),
            str(row.get("MatchDate", "")).strip(),
            str(row.get("LeagueId", "")).strip(),
            str(row.get("Home", "")).strip(),
            str(row.get("Away", "")).strip(),
        )
        for row in existing
    }

    added = 0

    for row in rows:
        key = (
            str(row.get("Engine", "")).strip(),
            str(row.get("MatchDate", "")).strip(),
            str(row.get("LeagueId", "")).strip(),
            str(row.get("Home", "")).strip(),
            str(row.get("Away", "")).strip(),
        )

        if key in existing_keys:
            continue

        existing.append(row)
        existing_keys.add(key)
        added += 1

    _write_csv(
        HISTORY_FILE,
        FLAG_FIELDS,
        existing,
    )

    return added


def _analyze_file(
    *,
    engine: str,
    path: Path,
    apply: bool,
    results_cache: dict[str, list[dict] | None],
    table_cache: dict,
) -> tuple[list[dict], list[dict]]:
    fieldnames, rows = _read_csv(path)

    if not rows:
        return [], []

    required = {
        "MatchDate",
        "LeagueId",
        "Home",
        "Away",
        "Band",
    }

    if not required.issubset(fieldnames):
        return [], []

    flagged_rows = []
    diagnostics = []
    changed = False

    for row in rows:
        league_id = str(
            row.get("LeagueId", "")
        ).strip()

        match_date = _parse_date(
            row.get("MatchDate")
        )

        home_raw = str(
            row.get("Home", "")
        ).strip()

        away_raw = str(
            row.get("Away", "")
        ).strip()

        original_band = str(
            row.get("Band", "")
        ).strip()

        base_diag = {
            "Engine": engine,
            "SourceFile": str(path),
            "StandingsSource": "",
            "MatchDate": (
                match_date.isoformat()
                if match_date
                else str(
                    row.get("MatchDate", "")
                )
            ),
            "LeagueId": league_id,
            "Home": home_raw,
            "Away": away_raw,
            "TeamsCount": "",
            "RelegationStartPosition": "",
            "HomePosition": "",
            "AwayPosition": "",
            "HomePlayed": "",
            "AwayPlayed": "",
            "HomePoints": "",
            "AwayPoints": "",
            "PointsGap": "",
            "OriginalBand": original_band,
            "FinalBand": original_band,
            "Decision": "",
        }

        if (
            not league_id
            or match_date is None
            or not home_raw
            or not away_raw
        ):
            base_diag["Decision"] = "INVALID_ROW"
            diagnostics.append(base_diag)
            continue

        table, source = _get_table(
            league_id=league_id,
            match_date=match_date,
            results_cache=results_cache,
            table_cache=table_cache,
        )

        base_diag["StandingsSource"] = source

        if not table:
            base_diag["Decision"] = "NO_STANDINGS"
            diagnostics.append(base_diag)
            continue

        home = normalize_team_name(
            league_id,
            home_raw,
        )

        away = normalize_team_name(
            league_id,
            away_raw,
        )

        home_row = table.get(home)
        away_row = table.get(away)

        teams_count = len(table)

        base_diag["TeamsCount"] = teams_count

        if home_row is None:
            base_diag["Decision"] = "HOME_NOT_FOUND"
            diagnostics.append(base_diag)
            continue

        if away_row is None:
            base_diag["Decision"] = "AWAY_NOT_FOUND"
            diagnostics.append(base_diag)
            continue

        relegation_start = (
            teams_count
            - RELEGATION_PLACES
            + 1
        )

        base_diag.update(
            {
                "RelegationStartPosition": (
                    relegation_start
                ),
                "HomePosition": (
                    home_row["position"]
                ),
                "AwayPosition": (
                    away_row["position"]
                ),
                "HomePlayed": (
                    home_row["played"]
                ),
                "AwayPlayed": (
                    away_row["played"]
                ),
                "HomePoints": (
                    home_row["points"]
                ),
                "AwayPoints": (
                    away_row["points"]
                ),
                "PointsGap": abs(
                    home_row["points"]
                    - away_row["points"]
                ),
            }
        )

        if (
            home_row["played"]
            < MIN_MATCHES_PLAYED
            or away_row["played"]
            < MIN_MATCHES_PLAYED
        ):
            base_diag["Decision"] = "UNDER_MIN_MATCHES"
            diagnostics.append(base_diag)
            continue

        if (
            home_row["position"]
            < relegation_start
        ):
            base_diag["Decision"] = "HOME_NOT_LAST_N"
            diagnostics.append(base_diag)
            continue

        if (
            away_row["position"]
            < relegation_start
        ):
            base_diag["Decision"] = "AWAY_NOT_LAST_N"
            diagnostics.append(base_diag)
            continue

        base_diag["FinalBand"] = FINAL_BAND
        base_diag["Decision"] = "FLAGGED"

        flag_row = {
            field: base_diag.get(
                field,
                "",
            )
            for field in FLAG_FIELDS
        }

        flagged_rows.append(flag_row)
        diagnostics.append(base_diag)

        if original_band != FINAL_BAND:
            row["Band"] = FINAL_BAND
            changed = True

    if apply and changed:
        _write_csv(
            path,
            fieldnames,
            rows,
        )

    return flagged_rows, diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Marca PROX-RELEGATION le partite "
            "tra due squadre nelle ultime posizioni."
        )
    )

    parser.add_argument(
        "--engine",
        default=None,
        help=(
            "Analizza soltanto un engine. "
            "Se omesso analizza tutti."
        ),
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Modifica realmente i ranking attivi. "
            "Senza --apply esegue solo il dry-run."
        ),
    )

    args = parser.parse_args()

    files = _active_ranking_files(
        args.engine
    )

    if not files:
        print(
            "Nessun ranking attivo trovato."
        )
        return 2

    results_cache = {}
    table_cache = {}

    all_flagged = []
    all_diagnostics = []

    for engine, path in files:
        flagged, diagnostics = _analyze_file(
            engine=engine,
            path=path,
            apply=args.apply,
            results_cache=results_cache,
            table_cache=table_cache,
        )

        all_flagged.extend(flagged)
        all_diagnostics.extend(diagnostics)

        print(
            f"[{engine}] {path.name}: "
            f"{len(flagged)} PROX-RELEGATION"
        )

    _write_csv(
        LATEST_FILE,
        FLAG_FIELDS,
        all_flagged,
    )

    _write_csv(
        DIAGNOSTICS_FILE,
        DIAGNOSTIC_FIELDS,
        all_diagnostics,
    )

    history_added = _append_history(
        all_flagged
    )

    print()
    print(
        f"Partite individuate: {len(all_flagged)}"
    )
    print(
        f"Nuove nello storico: {history_added}"
    )
    print(
        "Modalità: "
        + (
            "APPLICATA"
            if args.apply
            else "DRY-RUN"
        )
    )
    print(
        f"Partite trovate: {LATEST_FILE}"
    )
    print(
        f"Storico: {HISTORY_FILE}"
    )
    print(
        f"Diagnostica completa: {DIAGNOSTICS_FILE}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
