"""Weekly VEG90 report based exclusively on frozen prediction history."""
import csv
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

HISTORY = Path("data/storico/ranking/veg90/storico_ranking_veg90.csv")
OUTPUT = Path("data/analysis/veg90_weekly.csv")

def main():
    if not HISTORY.exists():
        raise SystemExit("No VEG90 history yet. Run python -m analysis.veg90 first.")
    with HISTORY.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    grouped = defaultdict(list)
    for r in rows:
        if r.get("Outcome") not in ("OK", "KO"):
            continue
        day = date.fromisoformat(r["MatchDate"])
        monday = day - timedelta(days=day.weekday())
        for group in ("ALL", "EX_AUSTRALIA"):
            if group == "EX_AUSTRALIA" and r["LeagueId"].lower().startswith("australia_"):
                continue
            grouped[(monday.isoformat(), group)].append(r)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for (week, group), items in grouped.items():
        ok = sum(r["Outcome"] == "OK" for r in items)
        ko = len(items) - ok
        records.append((week, group, ok, ko, len(items), round(ok / len(items) * 100, 2)))
    records.sort(key=lambda x: (x[0], x[5]), reverse=True)
    with OUTPUT.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["WeekMonday", "Scope", "OK", "KO", "Total", "Pct"])
        w.writerows(records)
    print("VEG90 weekly results:")
    for week, group, ok, ko, n, pct in records[:20]:
        print(f"{week} {group}: OK={ok} KO={ko} Tot={n} %={pct:.2f}")
    print(f"[WRITE] {OUTPUT}")

if __name__ == "__main__":
    main()
