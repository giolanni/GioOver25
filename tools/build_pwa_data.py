"""Build the static JSON consumed by the GioOver PWA.

The script only reads repository outputs; it does not scrape or alter rankings.
"""

from __future__ import annotations

import csv
import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "pwa" / "data" / "current.json"
HISTORY_DAYS = 2
STATS_DAYS = 30
FINAL_STATUSES = {"FINAL", "FT", "FINALE", "FINISHED"}
RUNNING_STATUSES = {"LIVE", "IN_PLAY", "1H", "2H", "HT"}


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def match_key(row: dict[str, str]) -> tuple[str, str, str, str]:
    return tuple((row.get(name) or "").strip() for name in ("MatchDate", "LeagueId", "Home", "Away"))


def as_number(value: str | None, *, integer: bool = False):
    if value in (None, ""):
        return None
    try:
        return int(float(value)) if integer else round(float(value), 2)
    except ValueError:
        return None


def resolved_result(engine: str, row: dict[str, str]) -> str:
    status = (row.get("MatchStatus") or row.get("Status") or "").upper()
    if status and status not in {"FINAL", "FINALE"}:
        return ""
    field = "BTTS" if engine.lower().startswith("vg") else "Outcome"
    value = (row.get(field) or "").upper()
    if value not in {"OK", "KO"} and field == "Outcome":
        value = (row.get("Over25") or "").upper()
    return value if value in {"OK", "KO"} else ""


def live_outcome(engine: str, status: str, hg: int | None, ag: int | None) -> str:
    status = status.upper()
    if status not in FINAL_STATUSES | RUNNING_STATUSES or hg is None or ag is None:
        return "UNKNOWN"
    reached = (hg > 0 and ag > 0) if engine.lower().startswith("vg") else (hg + ag > 2)
    if reached:
        return "OK"
    return "KO" if status in FINAL_STATUSES else "PENDING"


def prefer(new: dict[str, str], old: dict[str, str] | None, engine: str) -> bool:
    if old is None:
        return True
    new_final = bool(resolved_result(engine, new))
    old_final = bool(resolved_result(engine, old))
    if new_final != old_final:
        return new_final
    return (new.get("PredictionDate") or "") >= (old.get("PredictionDate") or "")


def main() -> None:
    ranking_root = ROOT / "data" / "output_ranking"
    history_root = ROOT / "data" / "storico" / "ranking"

    current: dict[tuple[str, tuple[str, str, str, str]], dict[str, str]] = {}
    for path in sorted(ranking_root.glob("*/ranking_*.csv")):
        engine = path.parent.name
        for row in read_csv(path):
            current[(engine, match_key(row))] = row

    gs1_outputs = (
        ("gs1_over", ROOT / "data" / "output_gs1_over" / "ranking_gs1_over.csv"),
        ("gs1_near", ROOT / "data" / "output_gs1_over" / "ranking_gs1_over_near.csv"),
    )
    for engine, path in gs1_outputs:
        for row in read_csv(path):
            current[(engine, match_key(row))] = row

    dates = [key[1][0] for key in current if key[1][0]]
    reference = date.fromisoformat(max(dates)) if dates else date.today()
    history_from = reference - timedelta(days=HISTORY_DAYS)
    stats_from = reference - timedelta(days=STATS_DAYS - 1)

    histories: dict[str, dict[tuple[str, str, str, str], dict[str, str]]] = {}
    stats: dict[str, list[int]] = {}
    all_rows: dict[tuple[str, tuple[str, str, str, str]], dict[str, str]] = dict(current)

    for path in sorted(history_root.glob("*/storico_ranking_*.csv")):
        engine = path.parent.name
        engine_history = histories.setdefault(engine, {})
        for row in read_csv(path):
            key = match_key(row)
            try:
                match_date = date.fromisoformat(key[0])
            except ValueError:
                continue
            if match_date >= stats_from and (row.get("Band") or "").strip().upper() == "ALTA":
                result = resolved_result(engine, row)
                if result:
                    counts = stats.setdefault(engine, [0, 0])
                    counts[0 if result == "OK" else 1] += 1
            if match_date < history_from:
                continue
            if prefer(row, engine_history.get(key), engine):
                engine_history[key] = row
                all_rows[(engine, key)] = row

    gs1_histories = (
        ("gs1_over", ROOT / "data" / "storico" / "gs1_over" / "storico_gs1_over.csv"),
        ("gs1_near", ROOT / "data" / "storico" / "gs1_over" / "storico_gs1_over_near.csv"),
    )
    for engine, path in gs1_histories:
        engine_history = histories.setdefault(engine, {})
        for row in read_csv(path):
            key = match_key(row)
            try:
                match_date = date.fromisoformat(key[0])
            except ValueError:
                continue
            if match_date >= stats_from and (row.get("Band") or "").strip().upper() == "ALTA":
                result = resolved_result(engine, row)
                if result:
                    counts = stats.setdefault(engine, [0, 0])
                    counts[0 if result == "OK" else 1] += 1
            if match_date < history_from:
                continue
            if prefer(row, engine_history.get(key), engine):
                engine_history[key] = row
                all_rows[(engine, key)] = row

    kickoff = {
        match_key(row): (row.get("Kickoff") or "").strip()
        for row in read_csv(ROOT / "data" / "operational" / "kickoff_times.csv")
    }
    live_rows = read_csv(ROOT / "data" / "live" / "partite_live.csv")
    live_index = {match_key(row): row for row in live_rows}

    matches = []
    for (engine, key), base_row in all_rows.items():
        row = base_row
        history_row = histories.get(engine, {}).get(key)
        if history_row and prefer(history_row, row, engine):
            row = history_row
        match_date, league, home, away = key
        if not all(key):
            continue
        band = (row.get("Band") or "").strip()
        # The mobile page is for playable selections, not the thousands of
        # diagnostic BASSA/PROX rows produced by every engine.
        playable_band = band == "MEDIA" or "ALTA" in band
        gs1_near_band = engine == "gs1_near" and band.upper() in {"NEAR", "OSSERVAZIONE"}
        if not playable_band and not gs1_near_band:
            continue
        live = live_index.get(key, {})
        live_hg = as_number(live.get("HG"), integer=True)
        live_ag = as_number(live.get("AG"), integer=True)
        live_status = (live.get("Status") or "").strip().upper()
        matches.append(
            {
                "match_date": match_date,
                "league_id": league,
                "home": home,
                "away": away,
                "start_time": kickoff.get(key, ""),
                "engine": engine,
                "band": band,
                "score": as_number(row.get("Score")),
                "expected_goals": as_number(row.get("ExpectedGoals")),
                "result": resolved_result(engine, row),
                "home_goals": as_number(row.get("HG"), integer=True),
                "away_goals": as_number(row.get("AG"), integer=True),
                "live_status": live_status,
                "live_minute": (live.get("Minute") or "").strip(),
                "live_home_goals": live_hg,
                "live_away_goals": live_ag,
                "live_outcome": live_outcome(engine, live_status, live_hg, live_ag),
                "live_updated_at": (live.get("LastUpdate") or "").strip(),
            }
        )

    matches.sort(key=lambda x: (x["match_date"], x["start_time"] or "99:99", x["league_id"], x["home"], x["engine"]))
    engines = []
    for engine in sorted(set(stats) | {item["engine"] for item in matches}):
        ok, ko = stats.get(engine, [0, 0])
        total = ok + ko
        engines.append(
            {"name": engine, "ok": ok, "ko": ko, "total": total, "hit_rate": round(ok * 100 / total, 1) if total else 0.0}
        )

    now = datetime.now(ZoneInfo("Europe/Rome"))
    live_updates = []
    for row in live_rows:
        raw = (row.get("LastUpdate") or "").strip()
        if not raw:
            continue
        try:
            live_updates.append(datetime.fromisoformat(raw.replace("Z", "+00:00")))
        except ValueError:
            continue
    live_updated_at = ""
    if live_updates:
        latest = max(live_updates)
        if latest.tzinfo is None:
            latest = latest.replace(tzinfo=timezone.utc)
        live_updated_at = latest.astimezone(ZoneInfo("Europe/Rome")).strftime("%d/%m/%Y %H:%M")
    payload = {
        "meta": {
            "match_date": reference.isoformat(),
            "updated_at": now.strftime("%d/%m/%Y %H:%M"),
            "history_days": HISTORY_DAYS,
            "stats_days": STATS_DAYS,
            "live_updated_at": live_updated_at,
        },
        "matches": matches,
        "engines": engines,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"PWA: {len(matches)} righe, {len(engines)} engine -> {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
