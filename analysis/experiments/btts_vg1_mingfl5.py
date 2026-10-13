"""Compare historical VG1 selections and MinGFL5 without modifying any engine.
Run: python -m analysis.experiments.btts_vg1_mingfl5 StoriciRanking.zip
NOTE: VG1 selection is only known for matches present in its own ranking history.
MinGFL5 reconstructed from preceding five matches per team; validate against VG1 Reason.
"""
import argparse
import collections
import csv
import datetime as dt
import io
import re
import zipfile

def main():
    p = argparse.ArgumentParser()
    p.add_argument("archive")
    p.add_argument("--threshold", type=float, default=2.2)
    args = p.parse_args()
    matches = {}
    with zipfile.ZipFile(args.archive) as z:
        for name in z.namelist():
            match = re.search(r"storico_ranking_([^/]+)\.csv$", name)
            if not match:
                continue
            engine = match.group(1)
            with io.TextIOWrapper(z.open(name), encoding="utf-8-sig") as f:
                for row in csv.DictReader(f, delimiter=";"):
                    try:
                        day = dt.date.fromisoformat(row["MatchDate"][:10])
                        key = (row["LeagueId"], day, row["Home"], row["Away"])
                    except (KeyError, ValueError):
                        continue
                    item = matches.setdefault(key, {"result": None, "vg1": None, "conflict": False})
                    try:
                        result = (int(row["HG"]), int(row["AG"]))
                        if min(result) < 0:
                            continue
                        if item["result"] is not None and item["result"] != result:
                            item["conflict"] = True
                        item["result"] = result
                    except (KeyError, ValueError, TypeError):
                        pass
                    if engine == "vg1":
                        item["vg1"] = row.get("Band", "").strip().upper() == "ALTA"
    days = collections.defaultdict(list)
    for key in matches:
        days[key[1]].append(key)
    history = collections.defaultdict(lambda: collections.deque(maxlen=5))
    stats = collections.defaultdict(lambda: [0, 0])
    for day in sorted(days):
        staged = []
        for key in days[day]:
            league, _, home, away = key
            item = matches[key]
            result = item["result"]
            if result is None or item["conflict"]:
                continue
            h, a = result
            hform, aform = history[(league, home)], history[(league, away)]
            mingfl5 = min(sum(hform)/5, sum(aform)/5) if len(hform) == len(aform) == 5 else None
            selected = item["vg1"]
            outcomes = {
                "VG1_recorded": selected is True,
                "VG1_plus_MinGFL5": selected is True and mingfl5 is not None and mingfl5 > args.threshold,
                "MinGFL5": mingfl5 is not None and mingfl5 > args.threshold,
            }
            for label, active in outcomes.items():
                if active:
                    stats[(label, day.strftime("%Y-%m"))][0 if h and a else 1] += 1
            staged.extend([((league, home), h), ((league, away), a)])
        for team, goals in staged:
            history[team].append(goals)
    print("Configuration;Month;OK;KO;Total;BTTS%")
    for (label, month), (ok, ko) in sorted(stats.items()):
        print(f"{label};{month};{ok};{ko};{ok+ko};{100*ok/(ok+ko):.2f}")
    print("WARNING: VG1_recorded is not a full VG1 replay on every historical match.")
    print("WARNING: reconstructed MinGFL5 may differ from original VG1 implementation.")

if __name__ == "__main__":
    main()
