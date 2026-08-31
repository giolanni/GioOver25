from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict, deque
from pathlib import Path


RAW_DIR = Path("data/xg/raw")
SUMMARY_DIR = Path("data/xg/summary")


def _f(value) -> float:
    return float(str(value).replace(",", "."))


def _season_from_path(path: Path, league_id: str) -> str:
    match = re.match(rf"^{re.escape(league_id)}_(\d{{4}})\.csv$", path.name)
    return match.group(1) if match else ""


def read_rows(paths: list[Path]) -> list[dict]:
    rows: list[dict] = []
    seen = set()
    for path in paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle, delimiter=";"):
                row = dict(row)
                league_id = str(row.get("LeagueId") or "").strip()
                row["Season"] = str(row.get("Season") or _season_from_path(path, league_id)).strip()
                key = (
                    row.get("LeagueId"), row.get("Season"), row.get("MatchDate"),
                    row.get("Home"), row.get("Away"),
                )
                if key in seen:
                    continue
                seen.add(key)
                rows.append(row)
    rows.sort(key=lambda r: (
        r.get("Season", ""), r.get("MatchDate", ""), r.get("LeagueId", ""),
        r.get("Home", ""), r.get("Away", ""),
    ))
    return rows


def summarize(rows: list[dict], last_n: int = 5) -> list[dict]:
    """Sintesi per squadra e stagione.

    La stagione fa parte della chiave: i dati 2024, per esempio, non vengono
    sommati ai dati 2025. Questo rende la sintesi coerente con le feature
    point-in-time e con i futuri backtest.
    """
    season_stats = defaultdict(lambda: {"played": 0, "xgf": 0.0, "xga": 0.0})
    recent = defaultdict(lambda: deque(maxlen=last_n))

    for row in rows:
        league = row["LeagueId"]
        season = str(row.get("Season") or "")
        hxg, axg = _f(row["HomeXG"]), _f(row["AwayXG"])
        home, away = row["Home"], row["Away"]

        for team, xgf, xga in ((home, hxg, axg), (away, axg, hxg)):
            key = (league, season, team)
            season_stats[key]["played"] += 1
            season_stats[key]["xgf"] += xgf
            season_stats[key]["xga"] += xga
            recent[key].append((xgf, xga))

    output = []
    for (league, season, team), agg in sorted(season_stats.items()):
        games = agg["played"]
        rec = list(recent[(league, season, team)])
        rxgf = sum(x[0] for x in rec) / len(rec)
        rxga = sum(x[1] for x in rec) / len(rec)
        sxgf = agg["xgf"] / games
        sxga = agg["xga"] / games
        output.append({
            "LeagueId": league,
            "Season": season,
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
    parser = argparse.ArgumentParser(description="Sintetizza gli xG normalizzati per squadra/stagione")
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
    seasons = sorted({str(row.get("Season") or "") for row in summary})
    print(f"[OK] {len(summary)} righe squadra/stagione ({', '.join(seasons)}) -> {out}")


if __name__ == "__main__":
    main()
