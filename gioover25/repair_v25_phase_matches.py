"""
===============================================================================
GioOver2.5 - repair_v25_phase_matches.py
===============================================================================

SCOPO
-----
Bonificare esclusivamente le prediction v25 relative a fasi PlayIn/PlayOff
già presenti nello storico risultati con LeagueId dedicata.

Lo script:
- legge i risultati delle fasi;
- trova la prediction v25 corrispondente ancora salvata con la LeagueId
  della divisione regolare;
- corregge la LeagueId della partita;
- conserva la divisione di origine delle squadre;
- aggiorna MatchDate e risultato reale;
- modifica soltanto:
    data/output_ranking/v25/
    data/storico/ranking/v25/storico_ranking_v25.csv

NON modifica v13-v24.

FONTI
-----
Risultati di fase:
    data/storico/risultati/*PlayIn*.csv
    data/storico/risultati/*PlayOff*.csv

Compatibilità con snapshot/cartelle alternative:
    data/risultati/
    risultati/

TARGET
------
    data/output_ranking/v25/**/*.csv
    data/storico/ranking/v25/storico_ranking_v25.csv

MATCHING
--------
La prediction candidata deve avere:
- stessa Home;
- stessa Away;
- LeagueId USL League Two diversa dalla LeagueId di fase;
- PredictionDate o MatchDate entro ±2 giorni dalla data della fase.

Deve esistere una sola prediction candidata nello storico ranking.
Nei file output v25 possono esistere copie della stessa prediction: vengono
aggiornate tutte, purché la chiave sia identica.

CAMPI AGGIORNATI
----------------
- LeagueId = LeagueId della fase;
- MatchDate = data effettiva della fase;
- HomeSourceLeagueId = LeagueId originaria della squadra di casa;
- AwaySourceLeagueId = divisione originaria ricavata dagli storici risultati;
- CompetitionGroup = USA_USLLeagueTwo_2026;
- HG, AG, Goals, Over25, BTTS nello storico ranking.

SICUREZZA
---------
Senza --apply esegue soltanto il dry run.

Con --apply:
- applica solo se Errors = 0;
- crea backup dei file modificati;
- non modifica righe ambigue.

USO
---
Dry run:

    python -m gioover25.repair_v25_phase_matches

Applicazione:

    python -m gioover25.repair_v25_phase_matches --apply

Dopo l'applicazione:

    python -m analysis.laboratory.run_all
    python -m analysis.metrics.analyze_metrics
===============================================================================
"""

from __future__ import annotations

import argparse
import csv
import shutil
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable


PHASE_MARKERS = ("PlayIn", "PlayOff", "Play_In", "Play_Off")
COMPETITION_GROUP = "USA_USLLeagueTwo_2026"
MAX_DAYS = 2

OUTPUT_V25 = Path("data/output_ranking/v25")
HISTORY_V25 = Path(
    "data/storico/ranking/v25/storico_ranking_v25.csv"
)
DEBUG_DIR = Path("data/debug/repair_v25_phases")
BACKUP_DIR = Path("data/backup/repair_v25_phases")


ALIASES = {
    "date": "MatchDate",
    "matchdate": "MatchDate",
    "predictiondate": "PredictionDate",
    "leagueid": "LeagueId",
    "home": "Home",
    "away": "Away",
    "hg": "HG",
    "ag": "AG",
    "over25": "Over25",
}


FINAL_FIELDS = ["HG", "AG", "Goals", "Over25", "BTTS"]


@dataclass(frozen=True)
class PhaseMatch:
    league_id: str
    match_date: date
    home: str
    away: str
    hg: int
    ag: int
    source_file: str


def _text(value: Any) -> str:
    return str(value or "").strip()


def _team(value: Any) -> str:
    return " ".join(_text(value).casefold().split())


def _canonical(name: str) -> str:
    clean = _text(name).replace("\ufeff", "")
    return ALIASES.get(clean.lower(), clean)


def _parse_date(value: Any) -> date | None:
    raw = _text(value)
    if not raw:
        return None

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass

    return None


def _detect_delimiter(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
    return ";" if sample.count(";") >= sample.count(",") else ","


def _read_csv(path: Path) -> tuple[list[dict], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(
            handle,
            delimiter=_detect_delimiter(path),
        )

        fieldnames = [
            _canonical(name)
            for name in (reader.fieldnames or [])
        ]

        rows = []

        for raw in reader:
            row = {}

            for key, value in raw.items():
                if key is None:
                    continue

                field = _canonical(key)
                incoming = value.strip() if isinstance(value, str) else value

                # Evita che una seconda colonna alias vuota cancelli un valore.
                if field in row:
                    existing = _text(row[field])
                    if existing and not _text(incoming):
                        continue

                row[field] = incoming

            rows.append(row)

    return rows, fieldnames


def _union_fields(
    original: list[str],
    rows: Iterable[dict],
) -> list[str]:
    fields = list(original)

    preferred_new = [
        "CompetitionGroup",
        "HomeSourceLeagueId",
        "AwaySourceLeagueId",
    ]

    for field in preferred_new:
        if field not in fields:
            fields.append(field)

    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)

    return fields


def _write_csv(
    path: Path,
    rows: list[dict],
    fields: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def _find_results_dir() -> Path:
    candidates = [
        Path("data/storico/risultati"),
        Path("data/risultati"),
        Path("risultati"),
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "Cartella storico risultati non trovata."
    )


def _is_phase_file(path: Path) -> bool:
    name = path.stem.casefold()
    return any(
        marker.casefold() in name
        for marker in PHASE_MARKERS
    )


def _load_phase_matches(results_dir: Path) -> list[PhaseMatch]:
    matches = []

    for path in sorted(results_dir.glob("*.csv")):
        if not _is_phase_file(path):
            continue

        rows, _ = _read_csv(path)
        league_id = path.stem

        for row in rows:
            match_date = _parse_date(
                row.get("MatchDate")
            )

            try:
                hg = int(_text(row.get("HG")))
                ag = int(_text(row.get("AG")))
            except ValueError:
                continue

            if (
                match_date is None
                or not _text(row.get("Home"))
                or not _text(row.get("Away"))
            ):
                continue

            matches.append(
                PhaseMatch(
                    league_id=league_id,
                    match_date=match_date,
                    home=_text(row.get("Home")),
                    away=_text(row.get("Away")),
                    hg=hg,
                    ag=ag,
                    source_file=str(path),
                )
            )

    return matches


def _ranking_date(row: dict) -> date | None:
    return (
        _parse_date(row.get("MatchDate"))
        or _parse_date(row.get("PredictionDate"))
    )


def _is_regular_usl2(league_id: str) -> bool:
    return (
        league_id.startswith("USA_USLLeagueTwo_")
        and not any(
            marker.casefold() in league_id.casefold()
            for marker in PHASE_MARKERS
        )
    )


def _candidate_rows(
    rows: list[dict],
    phase_match: PhaseMatch,
) -> list[tuple[int, int, dict]]:
    candidates = []

    for index, row in enumerate(rows):
        if _team(row.get("Home")) != _team(phase_match.home):
            continue

        if _team(row.get("Away")) != _team(phase_match.away):
            continue

        old_league = _text(row.get("LeagueId"))

        if not _is_regular_usl2(old_league):
            continue

        row_date = _ranking_date(row)

        if row_date is None:
            continue

        difference = abs(
            (phase_match.match_date - row_date).days
        )

        if difference <= MAX_DAYS:
            candidates.append(
                (difference, index, row)
            )

    candidates.sort(key=lambda item: item[0])
    return candidates


def _team_league_index(
    results_dir: Path,
) -> dict[str, list[tuple[date, str]]]:
    index: dict[str, list[tuple[date, str]]] = defaultdict(list)

    for path in sorted(results_dir.glob("USA_USLLeagueTwo_*.csv")):
        if _is_phase_file(path):
            continue

        rows, _ = _read_csv(path)

        for row in rows:
            match_date = _parse_date(
                row.get("MatchDate")
            )

            if match_date is None:
                continue

            for field in ("Home", "Away"):
                team_name = _team(row.get(field))
                if team_name:
                    index[team_name].append(
                        (match_date, path.stem)
                    )

    for values in index.values():
        values.sort(
            key=lambda item: item[0],
            reverse=True,
        )

    return index


def _source_league(
    team_name: str,
    before_date: date,
    team_index: dict[str, list[tuple[date, str]]],
) -> tuple[str, str]:
    candidates = [
        item
        for item in team_index.get(
            _team(team_name),
            [],
        )
        if item[0] < before_date
    ]

    if not candidates:
        return "", "SOURCE_LEAGUE_NOT_FOUND"

    newest_date = candidates[0][0]

    newest_leagues = sorted({
        league
        for candidate_date, league in candidates
        if candidate_date == newest_date
    })

    if len(newest_leagues) != 1:
        return "", "SOURCE_LEAGUE_AMBIGUOUS"

    return newest_leagues[0], ""


def _update_phase_row(
    row: dict,
    phase_match: PhaseMatch,
    home_source: str,
    away_source: str,
    include_result: bool,
) -> dict:
    updated = dict(row)

    updated["LeagueId"] = phase_match.league_id
    updated["MatchDate"] = phase_match.match_date.isoformat()
    updated["CompetitionGroup"] = COMPETITION_GROUP
    updated["HomeSourceLeagueId"] = home_source
    updated["AwaySourceLeagueId"] = away_source

    if include_result:
        goals = phase_match.hg + phase_match.ag

        updated["HG"] = str(phase_match.hg)
        updated["AG"] = str(phase_match.ag)
        updated["Goals"] = str(goals)
        updated["Over25"] = "OK" if goals >= 3 else "KO"
        updated["BTTS"] = (
            "OK"
            if phase_match.hg > 0 and phase_match.ag > 0
            else "KO"
        )

    return updated


def _backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    relative = path.as_posix().replace("/", "__")

    destination = (
        BACKUP_DIR
        / timestamp
        / relative
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(path, destination)
    return destination


def _report(
    phase_matches: list[PhaseMatch],
    plans: list[dict],
    errors: list[dict],
    apply: bool,
) -> None:
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    _write_csv(
        DEBUG_DIR / "phase_repair_plan.csv",
        plans,
        [
            "PhaseLeagueId",
            "MatchDate",
            "Home",
            "Away",
            "OldLeagueId",
            "HomeSourceLeagueId",
            "AwaySourceLeagueId",
            "HistoryRow",
            "OutputFiles",
            "HG",
            "AG",
        ],
    )

    _write_csv(
        DEBUG_DIR / "phase_repair_errors.csv",
        errors,
        [
            "PhaseLeagueId",
            "MatchDate",
            "Home",
            "Away",
            "Error",
            "Candidates",
            "SourceFile",
        ],
    )

    summary = [{
        "Mode": "APPLY" if apply else "DRY_RUN",
        "PhaseMatches": len(phase_matches),
        "PlannedRepairs": len(plans),
        "Errors": len(errors),
        "Result": (
            "SUCCESS"
            if not errors and len(plans) == len(phase_matches)
            else "FAILED"
        ),
    }]

    _write_csv(
        DEBUG_DIR / "phase_repair_summary.csv",
        summary,
        [
            "Mode",
            "PhaseMatches",
            "PlannedRepairs",
            "Errors",
            "Result",
        ],
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Bonifica mirata delle partite PlayIn/PlayOff v25."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Applica le modifiche dopo il dry run.",
    )

    args = parser.parse_args()

    results_dir = _find_results_dir()
    phase_matches = _load_phase_matches(
        results_dir
    )

    if not phase_matches:
        print("Nessuna partita di fase trovata.")
        return 1

    if not HISTORY_V25.exists():
        raise FileNotFoundError(
            f"Storico v25 non trovato: {HISTORY_V25}"
        )

    history_rows, history_fields = _read_csv(
        HISTORY_V25
    )

    output_files = sorted(
        OUTPUT_V25.rglob("*.csv")
    )

    output_data = {}
    for path in output_files:
        output_data[path] = _read_csv(path)

    team_index = _team_league_index(
        results_dir
    )

    plans = []
    errors = []
    history_updates = {}
    output_updates: dict[Path, dict[int, dict]] = defaultdict(dict)

    for phase_match in phase_matches:
        history_candidates = _candidate_rows(
            history_rows,
            phase_match,
        )

        if len(history_candidates) != 1:
            errors.append({
                "PhaseLeagueId": phase_match.league_id,
                "MatchDate": phase_match.match_date.isoformat(),
                "Home": phase_match.home,
                "Away": phase_match.away,
                "Error": (
                    "HISTORY_CANDIDATE_NOT_UNIQUE"
                ),
                "Candidates": len(history_candidates),
                "SourceFile": phase_match.source_file,
            })
            continue

        _, history_index, history_row = history_candidates[0]

        old_league = _text(
            history_row.get("LeagueId")
        )

        home_source = old_league
        away_source, away_error = _source_league(
            phase_match.away,
            phase_match.match_date,
            team_index,
        )

        if not home_source:
            home_source, home_error = _source_league(
                phase_match.home,
                phase_match.match_date,
                team_index,
            )
        else:
            home_error = ""

        source_errors = [
            error
            for error in (home_error, away_error)
            if error
        ]

        if source_errors:
            errors.append({
                "PhaseLeagueId": phase_match.league_id,
                "MatchDate": phase_match.match_date.isoformat(),
                "Home": phase_match.home,
                "Away": phase_match.away,
                "Error": "|".join(source_errors),
                "Candidates": 1,
                "SourceFile": phase_match.source_file,
            })
            continue

        matching_output_rows = []

        for output_path, (rows, _) in output_data.items():
            candidates = _candidate_rows(
                rows,
                phase_match,
            )

            for _, row_index, row in candidates:
                if (
                    _text(row.get("PredictionDate"))
                    == _text(
                        history_row.get("PredictionDate")
                    )
                    and _text(row.get("Score"))
                    == _text(history_row.get("Score"))
                ):
                    matching_output_rows.append(
                        (
                            output_path,
                            row_index,
                            row,
                        )
                    )

        if not matching_output_rows:
            errors.append({
                "PhaseLeagueId": phase_match.league_id,
                "MatchDate": phase_match.match_date.isoformat(),
                "Home": phase_match.home,
                "Away": phase_match.away,
                "Error": "OUTPUT_RANKING_NOT_FOUND",
                "Candidates": 0,
                "SourceFile": phase_match.source_file,
            })
            continue

        history_updates[history_index] = _update_phase_row(
            history_row,
            phase_match,
            home_source,
            away_source,
            include_result=True,
        )

        for output_path, row_index, row in matching_output_rows:
            output_updates[output_path][row_index] = _update_phase_row(
                row,
                phase_match,
                home_source,
                away_source,
                include_result=False,
            )

        plans.append({
            "PhaseLeagueId": phase_match.league_id,
            "MatchDate": phase_match.match_date.isoformat(),
            "Home": phase_match.home,
            "Away": phase_match.away,
            "OldLeagueId": old_league,
            "HomeSourceLeagueId": home_source,
            "AwaySourceLeagueId": away_source,
            "HistoryRow": history_index + 2,
            "OutputFiles": "|".join(
                sorted({
                    str(path)
                    for path, _, _ in matching_output_rows
                })
            ),
            "HG": phase_match.hg,
            "AG": phase_match.ag,
        })

    _report(
        phase_matches,
        plans,
        errors,
        args.apply,
    )

    success = (
        not errors
        and len(plans) == len(phase_matches)
    )

    print(
        f"Modalità: {'APPLY' if args.apply else 'DRY RUN'}"
    )
    print(f"Partite di fase: {len(phase_matches)}")
    print(f"Riparazioni pianificate: {len(plans)}")
    print(f"Errori: {len(errors)}")
    print(f"Esito: {'SUCCESS' if success else 'FAILED'}")
    print(f"Report: {DEBUG_DIR.resolve()}")

    if not success:
        print("Nessun file modificato.")
        return 1

    if not args.apply:
        print(
            "Dry run completato. "
            "Per applicare: aggiungere --apply"
        )
        return 0

    _backup(HISTORY_V25)

    for index, updated_row in history_updates.items():
        history_rows[index] = updated_row

    _write_csv(
        HISTORY_V25,
        history_rows,
        _union_fields(
            history_fields,
            history_rows,
        ),
    )

    for output_path, updates in output_updates.items():
        rows, fields = output_data[output_path]

        _backup(output_path)

        for index, updated_row in updates.items():
            rows[index] = updated_row

        _write_csv(
            output_path,
            rows,
            _union_fields(fields, rows),
        )

    print(
        "Riparazione applicata. "
        "Rigenerare laboratory e metrics."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
