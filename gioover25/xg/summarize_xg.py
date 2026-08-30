from __future__ import annotations

import argparse
import csv
from collections import defaultdict, deque
from pathlib import Path


RAW_DIR = Path("data/xg/raw")
SUMMARY_DIR = Path("data/xg/summary")


def _f(value) -> float:
    return float(str(value).replace(",", "."))


def read_rows(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    seen = set()
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter=";"):
                key = (row.get("LeagueId"), row.get("MatchDate"), row.get("Home"), row.get("Away"))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
    rows.sort(key=lambda r: (r.get("MatchDate", ""), r.get("LeagueId", ""), r.get("Home", ""), r.get("Away", "")))
    return rows


def summarize(rows: list[dict], last_n: int = 5) -> list[dict]:
    season = defaultdict(lambda: {"played": 0, "xgf": 0.0, "xga": 0.0})
    recent = defaultdict(lambda: deque(maxlen=last_n))

    for row in rows:
        league = row["LeagueId"]
        hxg, axg = _f(row["HomeXG"]), _f(row["AwayXG"])
        home, away = row["Home"], row["Away"]

        for team, xgf, xga in ((home, hxg, axg), (away, axg, hxg)):
            key = (league, team)
            season[key]["played"] += 1
            season[key]["xgf"] += xgf
            season[key]["xga"] += xga
            recent[key].append((xgf, xga))

    output = []
    for (league, team), agg in sorted(season.items()):
        games = agg["played"]
        rec = list(recent[(league, team)])
        rxgf = sum(x[0] for x in rec) / len(rec)
        rxga = sum(x[1] for x in rec) / len(rec)
        sxgf = agg["xgf"] / games
        sxga = agg["xga"] / games
        output.append({
            "LeagueId": league,
            "Team": team,
            "XGPlayed": games,
            "XGF": round(agg["xgf"], 3),
            "XGA": round(agg["xga"], 3),
            "XGFAvg": round(sxgf, 3),
            "XGAAvg": round(sxga, 3),
            "XGDiffAvg": round(sxgf - sxga, 3),
            f"XGFLast{last_n}Avg": round(rxgf, 3),
            f"XGALast{last_n}Avg": round(rxga, 3),
            f"XGDiffLast{last_n}Avg": round(rxgf - rxga, 3),
            f"XGRecentGames": len(rec),
        })
    return output


def write_summary(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise ValueError("Nessun dato xG da sintetizzare")
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Sintetizza gli xG normalizzati per squadra")
    parser.add_argument("--league-id", help="Limita la sintesi a una lega")
    parser.add_argument("--last-n", type=int, default=5, help="Finestra recente, default 5")
    args = parser.parse_args()

    paths = sorted(RAW_DIR.glob("*/*.csv"))
    if args.league_id:
        paths = [p for p in paths if p.name.startswith(args.league_id)]
    rows = read_rows(paths)
    summary = summarize(rows, last_n=args.last_n)
    name = f"xg_summary_{args.league_id}.csv" if args.league_id else "xg_summary_all.csv"
    out = SUMMARY_DIR / name
    write_summary(summary, out)
    print(f"[OK] {len(summary)} righe squadra -> {out}")


if __name__ == "__main__":
    main()
