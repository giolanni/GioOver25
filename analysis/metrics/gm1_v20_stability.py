"""GM1: audit di stabilita' del profilo V20 congelato.

Nessuna ricerca/ottimizzazione di soglie: profilo fissato sul TRAIN precedente.
Uso: python -m analysis.metrics.gm1_v20_stability
"""
from __future__ import annotations

import csv
from collections import defaultdict
from datetime import date
from pathlib import Path

from .gm1_v20_profiles import load_v20, split, describe, wilson
from .gm1_build_dataset import OUTPUT as DATASET

OUT = Path("data/analysis")
CONDITION = "AwayDefenseWeaknessScore>=25 & AwayLast10OverScore>=13.5"
KEY = ("LeagueId", "MatchDate", "Home", "Away")
REPORT_FIELDS = ("Dimension", "Group", "Split", "Profile", "OK", "KO", "Totale",
                 "Perc", "WilsonLower", "BaselineOK", "BaselineKO",
                 "BaselineTotale", "BaselinePct", "CoveragePct")
DETAIL_FIELDS = (*KEY, "Split", "Profile", "Result", "LeagueIdGroup",
                 "HomePlayed", "AwayPlayed", "MinPlayed", "Maturity",
                 "AwayDefenseWeaknessScore", "AwayLast10OverScore")


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def is_profile(row):
    # Same two original score components, same frozen thresholds.
    return row["features"][2] >= 25 and row["features"][4] >= 13.5


def maturity(n):
    if n is None:
        return "UNKNOWN"
    if n < 5:
        return "0-4"
    if n < 10:
        return "5-9"
    if n < 20:
        return "10-19"
    return "20+"


def read_played():
    # Match identity uses raw ranking team names as in V20 history.
    # If names differ between ranking/dataset, mark UNKNOWN rather than infer.
    lookup = {}
    duplicates = set()
    with DATASET.open(encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f, delimiter=";"):
            if row.get("Engine") != "v20":
                continue
            key = tuple((row.get(k) or "").strip() for k in KEY)
            hp, ap = number(row.get("HomePlayed")), number(row.get("AwayPlayed"))
            val = (hp, ap)
            if key in lookup and lookup[key] != val:
                duplicates.add(key)
            else:
                lookup[key] = val
    for key in duplicates:
        lookup.pop(key, None)
    print(f"[MATURITY] matched_keys={len(lookup)} conflicting_keys={len(duplicates)}")
    return lookup


def stats(rows):
    n = len(rows)
    ok = sum(r["ok"] for r in rows)
    return ok, n-ok, n, round(100*ok/n, 2) if n else 0


def add_report(output, dimension, group, period, rows):
    selected = [r for r in rows if r["profile"]]
    ok, ko, n, pct = stats(selected)
    bok, bko, bn, bpct = stats(rows)
    output.append({"Dimension": dimension, "Group": group, "Split": period,
                   "Profile": CONDITION, "OK": ok, "KO": ko, "Totale": n,
                   "Perc": pct, "WilsonLower": round(100*wilson(ok, n), 2),
                   "BaselineOK": bok, "BaselineKO": bko,
                   "BaselineTotale": bn, "BaselinePct": bpct,
                   "CoveragePct": round(100*n/bn, 2) if bn else 0})


def write(name, fields, rows):
    path = OUT / name
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")


def run():
    records = load_v20()
    periods = split(records)
    played = read_played()
    decorated = []
    for period, rows in periods.items():
        for row in rows:
            key = row["key"]
            hp, ap = played.get(key, (None, None))
            min_played = min(hp, ap) if hp is not None and ap is not None else None
            league = key[0]
            # Country-level grouping is descriptive only.
            country = league.split("_", 1)[0] if "_" in league else league
            decorated.append({**row, "period": period,
                              "profile": is_profile(row), "country": country,
                              "maturity": maturity(min_played),
                              "home_played": hp, "away_played": ap,
                              "min_played": min_played})
    reports = []
    for period in ("TRAIN", "VALID", "TEST"):
        group = [r for r in decorated if r["period"] == period]
        add_report(reports, "OVERALL", "ALL", period, group)
        for dimension, attr in (("LEAGUE", "key"), ("COUNTRY", "country"),
                                ("MATURITY", "maturity"), ("MONTH", "day")):
            grouped = defaultdict(list)
            for r in group:
                if dimension == "LEAGUE":
                    value = r["key"][0]
                elif dimension == "MONTH":
                    value = r["day"].strftime("%Y-%m")
                else:
                    value = r[attr]
                grouped[value].append(r)
            for value, subrows in grouped.items():
                add_report(reports, dimension, value, period, subrows)
    reports.sort(key=lambda r: (r["Dimension"], r["Group"],
                                ("TRAIN", "VALID", "TEST").index(r["Split"])))
    details = []
    for r in decorated:
        key = r["key"]
        details.append(dict(zip(KEY, key), Split=r["period"],
                            Profile="YES" if r["profile"] else "NO",
                            Result="OK" if r["ok"] else "KO",
                            LeagueIdGroup=r["country"],
                            HomePlayed="" if r["home_played"] is None else r["home_played"],
                            AwayPlayed="" if r["away_played"] is None else r["away_played"],
                            MinPlayed="" if r["min_played"] is None else r["min_played"],
                            Maturity=r["maturity"],
                            AwayDefenseWeaknessScore=r["features"][2],
                            AwayLast10OverScore=r["features"][4]))
    OUT.mkdir(parents=True, exist_ok=True)
    write("gm1_v20_stability_groups.csv", REPORT_FIELDS, reports)
    write("gm1_v20_stability_matches.csv", DETAIL_FIELDS, details)
    print("\n[V20-STABILITY] Profilo congelato:", CONDITION)
    for period in ("TRAIN", "VALID", "TEST"):
        sub = [r for r in decorated if r["period"] == period]
        selected = [r for r in sub if r["profile"]]
        ok, ko, n, pct = stats(selected)
        print(f"[{period}] profile OK={ok} KO={ko} Tot={n} "
              f"Pct={pct:.2f}% coverage={100*n/len(sub):.2f}%")
    print("\n[VALIDATION KO BY LEAGUE]")
    valid_ko = [r for r in decorated if r["period"] == "VALID"
                and r["profile"] and not r["ok"]]
    for league in sorted({r["key"][0] for r in valid_ko}):
        print(f"  {league}: {sum(r['key'][0] == league for r in valid_ko)} KO")
    print("\n[VALIDATION KO BY MATURITY]")
    for category in ("UNKNOWN", "0-4", "5-9", "10-19", "20+"):
        n = sum(r["maturity"] == category for r in valid_ko)
        if n:
            print(f"  {category}: {n} KO")
    print("[NOTE] Solo analisi descrittiva: non selezionare esclusioni "
          "di leghe/mesi/fasce dopo aver osservato VALID/TEST e "
          "presentarle come risultati out-of-sample.")


if __name__ == "__main__":
    run()
