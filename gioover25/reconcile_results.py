"""Reconcile past predictions without changing scores, bands or engine metrics."""
import csv
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import ranking_history as rh
from .history import MatchResult
from .team_names import normalize_team_name


def _rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle, delimiter=";")


def _key(row):
    league = row.get("LeagueId", "").strip()
    return (league, row.get("MatchDate", "").strip(),
            normalize_team_name(league, row.get("Home", "")),
            normalize_team_name(league, row.get("Away", "")))


def _past(row, today):
    try:
        return date.fromisoformat(row.get("MatchDate", "")) < today
    except ValueError:
        return False


def _score(row):
    try:
        goals = (int(row.get("HG", "")), int(row.get("AG", "")))
        return goals if min(goals) >= 0 else None
    except (ValueError, TypeError):
        return None


def reconcile_unresolved_matches(engine_names, input_file, today=None):
    # Lazy import avoids a module cycle and reuses the existing postponement registry.
    from . import append_results as ar
    today = today or datetime.now(ZoneInfo("Europe/Rome")).date()
    supplied = list(_rows(Path(input_file)))
    target_dates = {r["MatchDate"] for r in supplied if _past(r, today)}
    supplied_keys = {_key(r) for r in supplied}
    histories = {e: rh._read_history(e) for e in engine_names}
    finals = {}

    def add_final(row):
        score = _score(row)
        if score is not None:
            finals.setdefault(_key(row), set()).add(score)

    for rows in histories.values():
        for row in rows:
            add_final(row)
    for path in ar.RESULTS_DIR.glob("*.csv"):
        for row in _rows(path):
            row["LeagueId"] = path.stem
            # Result histories use MatchDate (older files may use Date).
            row["MatchDate"] = row.get("MatchDate") or row.get("Date", "")
            add_final(row)

    outputs = {}
    for path in Path("data/output_ranking").rglob("ranking_*.csv"):
        for row in _rows(path):
            if row.get("MatchDate") in target_dates and row.get("MatchStatus", "SCHEDULED").upper() == "SCHEDULED":
                outputs.setdefault(_key(row), row)

    postponed = ar._read_postponed()
    postponed_keys = {ar._postponed_key(r["LeagueId"], r["Home"], r["Away"]) for r in postponed}
    not_found = {}
    for key, row in outputs.items():
        fixture = ar._postponed_key(row["LeagueId"], row["Home"], row["Away"])
        if key in supplied_keys or key in finals or fixture in postponed_keys:
            continue
        entry = {**row, "Status": "NOT_FOUND", "Notes": "Rinvio presunto: assente dai risultati importati"}
        ar._register_postponed(postponed, entry)
        postponed_keys.add(fixture)
        not_found[key] = entry
    if not_found:
        ar._write_postponed(postponed)

    repaired = 0
    conflicts = {}
    for engine, rows in histories.items():
        changed = False
        for row in rows:
            if not _past(row, today) or _score(row) is not None:
                continue
            if row.get("MatchStatus", "").upper() not in {"SCHEDULED", "POSTPONED", "NOT_FOUND"}:
                continue
            key = _key(row)
            scores = finals.get(key, set())
            if len(scores) > 1:
                conflicts[key] = row
            elif len(scores) == 1:
                hg, ag = next(iter(scores))
                match = MatchResult("", "", ar._parse_round(row.get("Round")), key[1], row["Home"], row["Away"], hg, ag)
                rh._apply_final_result(row, match, date.fromisoformat(key[1]))
                repaired += 1
                changed = True
        if changed:
            rh._write_history(engine, rows)
    rh.sync_postponed_statuses_all_engines(engine_names)

    unresolved = {}
    for engine in engine_names:
        for row in rh._read_history(engine):
            if _past(row, today) and row.get("MatchStatus", "").upper() == "SCHEDULED" and _score(row) is None:
                key = _key(row)
                entry = unresolved.setdefault(key, {**row, "Engines": set()})
                entry["Engines"].add(engine)
    report = ar.DEBUG_DIR / "risultati_non_riconciliati.csv"
    report.parent.mkdir(parents=True, exist_ok=True)
    fields = ["LeagueId", "Round", "MatchDate", "Home", "Away", "Engines", "CurrentStatus", "Issue", "Notes"]
    with report.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        for key, row in sorted(not_found.items()):
            writer.writerow({**row, "CurrentStatus": "POSTPONED", "Issue": "NOT_FOUND"})
        for key, row in sorted(unresolved.items()):
            writer.writerow({**row, "Engines": ",".join(sorted(row["Engines"])), "CurrentStatus": "SCHEDULED", "Issue": "CONFLICTING_RESULTS" if key in conflicts else "MISSING_RESULT"})
    print(f"[RECONCILE] risultati propagati={repaired}; NOT_FOUND (rinvio presunto)={len(not_found)}")
    if not target_dates:
        print("[RECONCILE] Nessuna data passata nell'input: classificazione NOT_FOUND non eseguita.")
    print(f"[SCHEDULED SENZA ESITO] {len(unresolved)} partite uniche con MatchDate precedente a {today}")
    for key, row in sorted(unresolved.items()):
        print(f"  {key[0]};{row.get('Round', '')};{key[1]};{row['Home']};{row['Away']}")
    print(f"[RECONCILE] Report: {report}")
    return {"repaired": repaired, "not_found": len(not_found), "unresolved": len(unresolved)}
