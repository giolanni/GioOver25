"""Read-only historical ALTA statistics, separated by Over 2.5 and BTTS."""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

PERIODS = ("Ieri", "Ultimi 7 giorni", "Ultimi 15 giorni", "Mese precedente",
           "Set comune", "Dall'inizio")


def market_for(engine: str) -> str:
    return "BTTS" if engine.lower().startswith("vg") else "OVER25"


def fixture_key(row):
    return tuple((row.get(k) or "").strip().casefold()
                 for k in ("LeagueId", "MatchDate", "Home", "Away"))


def read_histories(folder: Path):
    histories = {}
    for path in sorted(folder.glob("*/storico_ranking_*.csv")):
        engine = path.parent.name
        rows = {}
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream, delimiter=";")
            for row in reader:
                key = fixture_key(row)
                if not all(key):
                    continue
                rows[key] = row
        histories[engine] = rows
    return histories


def in_period(day: str, period: str, today: date):
    try:
        d = date.fromisoformat(day)
    except ValueError:
        return False
    if period == "Ieri":
        return d == today - timedelta(days=1)
    if period == "Ultimi 7 giorni":
        return today - timedelta(days=7) <= d < today
    if period == "Ultimi 15 giorni":
        return today - timedelta(days=15) <= d < today
    if period == "Mese precedente":
        first = today.replace(day=1)
        last_month = (first - timedelta(days=1)).replace(day=1)
        return last_month <= d < first
    return d <= today


def common_start_dates(histories):
    """First shared operating date per market (latest engine start date).

    Each engine keeps its own selections. A shared fixture is NOT required.
    """
    starts = {}
    for market in ("OVER25", "BTTS"):
        first_dates = []
        for engine, rows in histories.items():
            if market_for(engine) != market:
                continue
            dates = [key[1] for key in rows if key[1] and
                     len(key[1]) == 10 and key[1][4] == "-" and key[1][7] == "-"]
            if dates:
                first_dates.append(min(dates))
        starts[market] = max(first_dates) if first_dates else None
    return starts


def common_size(histories, market):
    """Number of unique fixtures on/after the common start (not an intersection)."""
    start = common_start_dates(histories).get(market)
    if not start:
        return 0
    return len({key for engine, rows in histories.items()
                if market_for(engine) == market for key in rows if key[1] >= start})


def compute(histories, period, today=None):
    """Read-only ALTA OK/KO per engine; common set means a common start date."""
    today = today or date.today()
    starts = common_start_dates(histories)
    result = []
    for engine, rows in histories.items():
        market = market_for(engine)
        start = starts[market] if period == "Set comune" else None
        alta_ok = alta_ko = other_ok = other_ko = 0
        for key, row in rows.items():
            day = (row.get("MatchDate") or "").strip()
            if start and day < start:
                continue
            if period == "Set comune" and start is None:
                continue
            if not in_period(day, period, today):
                continue
            outcome = (row.get("BTTS" if market == "BTTS" else "Over25") or "").strip().upper()
            if outcome not in ("OK", "KO"):
                continue
            band = (row.get("Band") or "").strip().upper()
            if band == "ALTA":
                if outcome == "OK":
                    alta_ok += 1
                else:
                    alta_ko += 1
            else:
                if outcome == "OK":
                    other_ok += 1
                else:
                    other_ko += 1
        total = alta_ok + alta_ko
        result.append({"engine": engine, "market": market, "ok": alta_ok,
                       "ko": alta_ko, "total": total,
                       "rate": 100.0 * alta_ok / total if total else None,
                       "other_ok": other_ok, "other_ko": other_ko})
    return sorted(result, key=lambda r: (
        r["market"], r["rate"] is None,
        -(r["rate"] if r["rate"] is not None else 0), -r["total"], r["engine"]))


def rate_text(row):
    return f"{row['rate']:.2f}%" if row["rate"] is not None else "n.d."
