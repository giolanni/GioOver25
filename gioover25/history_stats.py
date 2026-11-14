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


def compute(histories, period, today=None):
    """Return one result per engine; only OK/KO outcomes count.

    Set comune uses the intersection of fixture identities within each market,
    independently for OVER25 and BTTS. All bands use the same denominator rules.
    """
    today = today or date.today()
    common = {}
    for market in ("OVER25", "BTTS"):
        sets = [set(rows) for name, rows in histories.items()
                if market_for(name) == market]
        common[market] = set.intersection(*sets) if sets else set()
    result = []
    for engine, rows in histories.items():
        market = market_for(engine)
        eligible = common[market] if period == "Set comune" else rows.keys()
        alta_ok = alta_ko = other_ok = other_ko = 0
        for key in eligible:
            row = rows.get(key)
            if row is None or not in_period((row.get("MatchDate") or "").strip(), period, today):
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
