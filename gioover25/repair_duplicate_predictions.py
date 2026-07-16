"""
===============================================================================
GioOver2.5 - repair_duplicate_predictions.py
===============================================================================

SCOPO
-----
Bonificare esclusivamente lo storico ranking v25 eliminando prediction
duplicate riferite alla stessa partita.

FILE LETTO E MODIFICATO
-----------------------
    data/storico/ranking/v25/storico_ranking_v25.csv

FILE NON MODIFICATI
-------------------
- output ranking originali;
- storici ranking v13-v24;
- storico risultati;
- laboratory;
- metrics.

CRITERIO DI DUPLICATO
---------------------
Due righe vengono considerate candidate duplicate se hanno:

- stessa LeagueId;
- stessa Home;
- stessa Away;
- data di riferimento distante al massimo 2 giorni.

La data di riferimento è:

- MatchDate, se presente;
- altrimenti PredictionDate.

REGOLE DI SCELTA
----------------
1. Se una sola riga ha HG/AG valorizzati, viene mantenuta quella.
2. Se entrambe hanno risultato:
   - se HG/AG coincidono, viene mantenuta la PredictionDate più recente;
   - se HG/AG differiscono, il gruppo è un conflitto e non viene modificato.
3. Se nessuna ha risultato, viene mantenuta la PredictionDate più recente.
4. A parità di PredictionDate viene mantenuta la riga con più campi valorizzati.
5. A ulteriore parità viene mantenuta la riga più recente nel file.

SICUREZZA
---------
Senza --apply viene eseguito soltanto un dry run.

Con --apply:
- applica solo se non esistono conflitti;
- crea un backup automatico;
- scrive i report diagnostici;
- conserva sempre almeno una riga per gruppo.

REPORT
------
    data/debug/repair_duplicate_predictions/
        duplicate_predictions_summary.csv
        duplicate_predictions_removed.csv
        duplicate_predictions_conflicts.csv
        duplicate_predictions_groups.csv

BACKUP
------
    data/backup/repair_duplicate_predictions/<timestamp>/
        storico_ranking_v25.csv

USO
---
Dry run:

    python -m gioover25.repair_duplicate_predictions

Applicazione:

    python -m gioover25.repair_duplicate_predictions --apply

Dopo l'applicazione:

    python -m analysis.laboratory.run_all
    python -m analysis.metrics.analyze_metrics

LIMITAZIONI
-----------
Lo script non modifica gruppi con risultati finali discordanti.
===============================================================================
"""

from __future__ import annotations

import argparse
import csv
import shutil
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any


HISTORY_FILE = Path(
    "data/storico/ranking/v25/storico_ranking_v25.csv"
)

DEBUG_DIR = Path(
    "data/debug/repair_duplicate_predictions"
)

BACKUP_DIR = Path(
    "data/backup/repair_duplicate_predictions"
)

MAX_DATE_DIFFERENCE_DAYS = 2


def _text(value: Any) -> str:
    return str(value or "").strip()


def _team(value: Any) -> str:
    return " ".join(
        _text(value)
        .casefold()
        .split()
    )


def _parse_date(value: Any) -> date | None:
    raw = _text(value)

    if not raw:
        return None

    try:
        return date.fromisoformat(raw)
    except ValueError:
        return None


def _reference_date(row: dict) -> date | None:
    return (
        _parse_date(row.get("MatchDate"))
        or _parse_date(row.get("PredictionDate"))
    )


def _prediction_date(row: dict) -> date:
    return (
        _parse_date(row.get("PredictionDate"))
        or date.min
    )


def _base_key(row: dict) -> tuple[str, str, str]:
    return (
        _text(row.get("LeagueId")),
        _team(row.get("Home")),
        _team(row.get("Away")),
    )


def _has_result(row: dict) -> bool:
    return (
        _text(row.get("HG")) != ""
        and _text(row.get("AG")) != ""
    )


def _result_key(row: dict) -> tuple[str, str] | None:
    if not _has_result(row):
        return None

    return (
        _text(row.get("HG")),
        _text(row.get("AG")),
    )


def _filled_fields(row: dict) -> int:
    return sum(
        1
        for value in row.values()
        if _text(value) != ""
    )


def _detect_delimiter(path: Path) -> str:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        sample = handle.read(4096)

    return (
        ";"
        if sample.count(";") >= sample.count(",")
        else ","
    )


def _read_csv(
    path: Path,
) -> tuple[list[dict], list[str]]:
    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        reader = csv.DictReader(
            handle,
            delimiter=_detect_delimiter(path),
        )

        rows = []

        for index, row in enumerate(reader):
            current = dict(row)
            current["__OriginalIndex"] = index
            rows.append(current)

        return rows, list(reader.fieldnames or [])


def _write_csv(
    path: Path,
    rows: list[dict],
    fieldnames: list[str],
) -> None:
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(rows)


def _cluster_rows(
    rows: list[dict],
) -> list[list[dict]]:
    """
    Divide le righe dello stesso matchup in gruppi temporali.

    Ogni gruppo contiene righe collegate da differenze di data
    non superiori a MAX_DATE_DIFFERENCE_DAYS.
    """
    dated_rows = [
        row
        for row in rows
        if _reference_date(row) is not None
    ]

    undated_rows = [
        row
        for row in rows
        if _reference_date(row) is None
    ]

    dated_rows.sort(
        key=lambda row: (
            _reference_date(row),
            int(row["__OriginalIndex"]),
        )
    )

    clusters = []
    current = []

    for row in dated_rows:
        if not current:
            current = [row]
            continue

        previous_date = _reference_date(
            current[-1]
        )
        current_date = _reference_date(row)

        if (
            previous_date is not None
            and current_date is not None
            and (
                current_date
                - previous_date
            ).days <= MAX_DATE_DIFFERENCE_DAYS
        ):
            current.append(row)
        else:
            clusters.append(current)
            current = [row]

    if current:
        clusters.append(current)

    # Le righe senza data non vengono unite automaticamente.
    for row in undated_rows:
        clusters.append([row])

    return clusters


def _choose_keep_row(
    cluster: list[dict],
) -> tuple[dict | None, list[dict], str]:
    """
    Restituisce:
        riga da mantenere;
        righe da rimuovere;
        eventuale motivo di conflitto.
    """
    if len(cluster) <= 1:
        return cluster[0], [], ""

    completed = [
        row
        for row in cluster
        if _has_result(row)
    ]

    if len(completed) >= 2:
        results = {
            _result_key(row)
            for row in completed
        }

        if len(results) > 1:
            return (
                None,
                [],
                "CONFLICTING_RESULTS",
            )

    candidates = (
        completed
        if completed
        else cluster
    )

    keep = max(
        candidates,
        key=lambda row: (
            _prediction_date(row),
            _filled_fields(row),
            int(row["__OriginalIndex"]),
        ),
    )

    removed = [
        row
        for row in cluster
        if row is not keep
    ]

    return keep, removed, ""


def _clean_row(row: dict) -> dict:
    return {
        key: value
        for key, value in row.items()
        if not key.startswith("__")
    }


def _backup(path: Path) -> Path:
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    destination = (
        BACKUP_DIR
        / timestamp
        / path.name
    )

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        path,
        destination,
    )

    return destination


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Bonifica prediction duplicate "
            "nello storico ranking v25."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Applica le modifiche dopo il dry run.",
    )

    args = parser.parse_args()

    if not HISTORY_FILE.exists():
        raise FileNotFoundError(
            f"Storico v25 non trovato: {HISTORY_FILE}"
        )

    rows, fieldnames = _read_csv(
        HISTORY_FILE
    )

    by_matchup: dict[
        tuple[str, str, str],
        list[dict]
    ] = defaultdict(list)

    for row in rows:
        by_matchup[
            _base_key(row)
        ].append(row)

    indexes_to_remove = set()

    removed_report = []
    conflicts_report = []
    groups_report = []

    duplicate_groups = 0

    for key, matchup_rows in by_matchup.items():
        if len(matchup_rows) <= 1:
            continue

        clusters = _cluster_rows(
            matchup_rows
        )

        for cluster in clusters:
            if len(cluster) <= 1:
                continue

            duplicate_groups += 1

            (
                keep,
                removed,
                conflict,
            ) = _choose_keep_row(
                cluster
            )

            league_id, home, away = key

            groups_report.append({
                "LeagueId": league_id,
                "Home": cluster[0].get("Home", ""),
                "Away": cluster[0].get("Away", ""),
                "Rows": len(cluster),
                "Dates": "|".join(
                    _text(
                        row.get("MatchDate")
                        or row.get("PredictionDate")
                    )
                    for row in cluster
                ),
                "Results": "|".join(
                    (
                        f"{_text(row.get('HG'))}-"
                        f"{_text(row.get('AG'))}"
                    )
                    if _has_result(row)
                    else ""
                    for row in cluster
                ),
                "Status": (
                    "CONFLICT"
                    if conflict
                    else "REMOVABLE"
                ),
            })

            if conflict:
                conflicts_report.append({
                    "LeagueId": league_id,
                    "Home": cluster[0].get("Home", ""),
                    "Away": cluster[0].get("Away", ""),
                    "Reason": conflict,
                    "Rows": len(cluster),
                    "PredictionDates": "|".join(
                        _text(
                            row.get("PredictionDate")
                        )
                        for row in cluster
                    ),
                    "MatchDates": "|".join(
                        _text(
                            row.get("MatchDate")
                        )
                        for row in cluster
                    ),
                    "Results": "|".join(
                        (
                            f"{_text(row.get('HG'))}-"
                            f"{_text(row.get('AG'))}"
                        )
                        if _has_result(row)
                        else ""
                        for row in cluster
                    ),
                })
                continue

            if keep is None:
                continue

            for row in removed:
                indexes_to_remove.add(
                    int(row["__OriginalIndex"])
                )

                removed_report.append({
                    "LeagueId": league_id,
                    "Home": row.get("Home", ""),
                    "Away": row.get("Away", ""),
                    "RemovedPredictionDate": row.get(
                        "PredictionDate",
                        "",
                    ),
                    "RemovedMatchDate": row.get(
                        "MatchDate",
                        "",
                    ),
                    "RemovedHG": row.get("HG", ""),
                    "RemovedAG": row.get("AG", ""),
                    "KeptPredictionDate": keep.get(
                        "PredictionDate",
                        "",
                    ),
                    "KeptMatchDate": keep.get(
                        "MatchDate",
                        "",
                    ),
                    "KeptHG": keep.get("HG", ""),
                    "KeptAG": keep.get("AG", ""),
                    "RemovedOriginalRow": (
                        int(row["__OriginalIndex"])
                        + 2
                    ),
                    "KeptOriginalRow": (
                        int(keep["__OriginalIndex"])
                        + 2
                    ),
                })

    success = len(
        conflicts_report
    ) == 0

    summary = [{
        "Mode": (
            "APPLY"
            if args.apply
            else "DRY_RUN"
        ),
        "HistoryRows": len(rows),
        "DuplicateGroups": duplicate_groups,
        "RowsToRemove": len(indexes_to_remove),
        "Conflicts": len(conflicts_report),
        "Result": (
            "SUCCESS"
            if success
            else "FAILED"
        ),
    }]

    _write_csv(
        DEBUG_DIR
        / "duplicate_predictions_summary.csv",
        summary,
        [
            "Mode",
            "HistoryRows",
            "DuplicateGroups",
            "RowsToRemove",
            "Conflicts",
            "Result",
        ],
    )

    _write_csv(
        DEBUG_DIR
        / "duplicate_predictions_removed.csv",
        removed_report,
        [
            "LeagueId",
            "Home",
            "Away",
            "RemovedPredictionDate",
            "RemovedMatchDate",
            "RemovedHG",
            "RemovedAG",
            "KeptPredictionDate",
            "KeptMatchDate",
            "KeptHG",
            "KeptAG",
            "RemovedOriginalRow",
            "KeptOriginalRow",
        ],
    )

    _write_csv(
        DEBUG_DIR
        / "duplicate_predictions_conflicts.csv",
        conflicts_report,
        [
            "LeagueId",
            "Home",
            "Away",
            "Reason",
            "Rows",
            "PredictionDates",
            "MatchDates",
            "Results",
        ],
    )

    _write_csv(
        DEBUG_DIR
        / "duplicate_predictions_groups.csv",
        groups_report,
        [
            "LeagueId",
            "Home",
            "Away",
            "Rows",
            "Dates",
            "Results",
            "Status",
        ],
    )

    print(
        f"Modalità: "
        f"{'APPLY' if args.apply else 'DRY RUN'}"
    )
    print(
        f"Righe storico: {len(rows)}"
    )
    print(
        f"Gruppi duplicati: "
        f"{duplicate_groups}"
    )
    print(
        f"Righe da rimuovere: "
        f"{len(indexes_to_remove)}"
    )
    print(
        f"Conflitti: "
        f"{len(conflicts_report)}"
    )
    print(
        f"Esito: "
        f"{'SUCCESS' if success else 'FAILED'}"
    )
    print(
        f"Report: {DEBUG_DIR.resolve()}"
    )

    if not success:
        print(
            "Nessun file modificato."
        )
        return 1

    if not args.apply:
        print(
            "Dry run completato. "
            "Per applicare aggiungere --apply."
        )
        return 0

    backup_path = _backup(
        HISTORY_FILE
    )

    cleaned_rows = [
        _clean_row(row)
        for row in rows
        if int(
            row["__OriginalIndex"]
        ) not in indexes_to_remove
    ]

    _write_csv(
        HISTORY_FILE,
        cleaned_rows,
        fieldnames,
    )

    print(
        f"Backup creato: {backup_path}"
    )
    print(
        f"Storico bonificato: "
        f"{HISTORY_FILE}"
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
