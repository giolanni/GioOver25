"""Experimental BTTS replay using the actual VG1 signal rules.

All engines' ranking CSVs define the match universe, deduplicated by
LeagueId, MatchDate, Home, Away. Historical matches strictly before the
fixture date build the features; same-day results are never used.

IMPORTANT: rankings may not contain complete season histories. Thus
overall BTTS/Over/PPG here are reconstructed from *observed* prior matches
in the supplied archive, NOT necessarily the original VG1 pre-match
statistics. Supply a full historical results CSV via --history to improve
coverage; compare replay with recorded VG1 before trusting accuracy.
"""
import argparse
import collections
import csv
import datetime as dt
import io
import pathlib
import re
import zipfile


def parse_row(row):
    try:
        day = dt.date.fromisoformat(row["MatchDate"][:10])
        key = (row["LeagueId"], day, row["Home"], row["Away"])
        h, a = int(row["HG"]), int(row["AG"])
        if h < 0 or a < 0:
            return None
        return key, (h, a)
    except (KeyError, ValueError, TypeError):
        return None


def load_archive(path):
    matches = {}
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not re.search(r"storico_ranking_[^/]+\.csv$", name):
                continue
            with io.TextIOWrapper(archive.open(name), encoding="utf-8-sig") as file:
                for row in csv.DictReader(file, delimiter=";"):
                    try:
                        key = (row["LeagueId"], dt.date.fromisoformat(row["MatchDate"][:10]),
                               row["Home"], row["Away"])
                    except (KeyError, ValueError):
                        continue
                    item = matches.setdefault(key, {"result": None, "conflict": False})
                    parsed = parse_row(row)
                    if parsed is None:
                        continue
                    result = parsed[1]
                    if item["result"] is not None and item["result"] != result:
                        item["conflict"] = True
                    item["result"] = result
    return matches


def _read_results_file(path, matches, target_keys):
    """Import resolved fixtures from the canonical results store.

    LeagueId may be a CSV column or derived from Country_League_Season.csv.
    Files with unknown schema are skipped and reported, never silently counted.
    """
    imported = 0
    with open(path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        if not reader.fieldnames:
            return 0, "empty header"
        headers = {x.strip().lower(): x for x in reader.fieldnames if x}
        def get(row, *names):
            for name in names:
                col = headers.get(name.lower())
                if col and row.get(col) is not None:
                    return row[col].strip()
            return ""
        if not any(x in headers for x in ("matchdate", "date", "data")):
            return 0, "missing date column"
        if not any(x in headers for x in ("hg", "homegoals", "home_score", "fthg")):
            return 0, "missing home goals column"
        if not any(x in headers for x in ("ag", "awaygoals", "away_score", "ftag")):
            return 0, "missing away goals column"
        fallback_league = re.sub(r"_\\d{4}(?:_\\d{4})?$", "", path.stem)
        for row in reader:
            league = get(row, "LeagueId") or fallback_league
            home = get(row, "Home", "HomeTeam", "SquadraCasa")
            away = get(row, "Away", "AwayTeam", "SquadraOspite")
            raw_date = get(row, "MatchDate", "Date", "Data")
            if not (league and home and away and raw_date):
                continue
            try:
                date = dt.date.fromisoformat(raw_date[:10])
                hg = int(get(row, "HG", "HomeGoals", "Home_Score", "FTHG"))
                ag = int(get(row, "AG", "AwayGoals", "Away_Score", "FTAG"))
                if min(hg, ag) < 0:
                    continue
            except (ValueError, TypeError):
                continue
            key = (league, date, home, away)
            item = matches.setdefault(key, {"result": None, "conflict": False})
            if item["result"] is not None and item["result"] != (hg, ag):
                item["conflict"] = True
            item["result"] = (hg, ag)
            imported += 1
    return imported, None


def load_history(source, matches, target_keys):
    source = pathlib.Path(source)
    if not source.exists():
        raise FileNotFoundError(f"Historical results not found: {source}")
    files = sorted(source.rglob("*.csv")) if source.is_dir() else [source]
    loaded, skipped, total = 0, [], 0
    for path in files:
        count, error = _read_results_file(path, matches, target_keys)
        total += count
        if error:
            skipped.append((str(path), error))
        else:
            loaded += 1
    print(f"History source: {source} | files read: {loaded} | rows imported: {total} | files skipped: {len(skipped)}")
    for name, error in skipped[:10]:
        print(f"  SKIPPED {name}: {error}")
    if not loaded:
        raise ValueError("No valid historical results CSV files were loaded")


def features(history, league, home, away, min_played):
    h = history[(league, home)]
    a = history[(league, away)]
    if min(len(h), len(a)) < max(5, min_played):
        return None
    def rate(rows, pred):
        return sum(bool(pred(x)) for x in rows) / len(rows)
    def team_ppg(rows):
        return sum(3 if gf > ga else 1 if gf == ga else 0 for gf, ga in rows) / len(rows)
    hb, ab = rate(h, lambda x: x[0] > 0 and x[1] > 0), rate(a, lambda x: x[0] > 0 and x[1] > 0)
    hl, al = h[-5:], a[-5:]
    recent_btts = (rate(hl, lambda x: x[0] > 0 and x[1] > 0) +
                   rate(al, lambda x: x[0] > 0 and x[1] > 0)) / 2
    full_btts = (hb + ab) / 2
    return {
        "min_btts_full": min(hb, ab),
        "min_gf_l5": min(sum(x[0] for x in hl) / 5, sum(x[0] for x in al) / 5),
        "ppg_gap_full": abs(team_ppg(h) - team_ppg(a)),
        "delta_btts_l5": recent_btts - full_btts,
        "min_over_full": min(rate(h, lambda x: sum(x) > 2),
                             rate(a, lambda x: sum(x) > 2)),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("archive", help="ZIP containing all engine ranking CSVs")
    parser.add_argument("--threshold", type=float, default=2.2)
    parser.add_argument("--history", default="data/storico/risultati",
                        help="Historical results CSV or directory (default: data/storico/risultati)")
    parser.add_argument("--ranking-only", action="store_true",
                        help="Explicitly disable canonical history loading; limited coverage")
    parser.add_argument("--min-played", type=int, default=5,
                        help="Minimum preceding matches per team (default 5)")
    parser.add_argument("--output", help="Optional match-level audit CSV path")
    args = parser.parse_args()

    matches = load_archive(args.archive)
    target_keys = set(matches)
    if not args.ranking_only:
        load_history(args.history, matches, target_keys)
    by_day = collections.defaultdict(list)
    for key in matches:
        by_day[key[1]].append(key)
    history = collections.defaultdict(list)
    stats = collections.defaultdict(lambda: [0, 0])
    audit = []
    coverage = collections.Counter()
    strategies = ("VG1_replayed", "VG1_plus_MinGFL5", "MinGFL5_only")
    for day in sorted(by_day):
        staged = []
        for key in sorted(by_day[day]):
            league, _, home, away = key
            item = matches[key]
            if item["conflict"] or item["result"] is None:
                coverage["unresolved_or_conflict"] += key in target_keys
                continue
            hg, ag = item["result"]
            if key in target_keys:
                f = features(history, league, home, away, args.min_played)
                if f is None:
                    coverage["insufficient_prior_history"] += 1
                else:
                    coverage["evaluated"] += 1
                    base = f["min_btts_full"] >= .70 and f["min_gf_l5"] >= 1.80
                    vg1 = base and f["ppg_gap_full"] <= 1.00 and f["delta_btts_l5"] >= 0
                    selected = (vg1, vg1 and f["min_gf_l5"] > args.threshold,
                                f["min_gf_l5"] > args.threshold)
                    for strategy, active in zip(strategies, selected):
                        if active:
                            stats[(strategy, day.strftime("%Y-%m"))][0 if hg > 0 and ag > 0 else 1] += 1
                    audit.append([day.isoformat(), league, home, away, hg, ag,
                                  int(hg > 0 and ag > 0), *(round(f[k], 5) for k in
                                  ("min_btts_full", "min_gf_l5", "ppg_gap_full",
                                   "delta_btts_l5", "min_over_full")),
                                  *(int(x) for x in selected)])
            staged.extend([((league, home), (hg, ag)),
                           ((league, away), (ag, hg))])
        for team, result in staged:
            history[team].append(result)

    print("Configuration;Month;OK;KO;Total;BTTS%")
    for strategy in strategies:
        overall = [0, 0]
        for month in sorted({month for _, month in stats}):
            ok, ko = stats[(strategy, month)]
            overall[0] += ok
            overall[1] += ko
            if ok + ko:
                print(f"{strategy};{month};{ok};{ko};{ok+ko};{100*ok/(ok+ko):.2f}")
        ok, ko = overall
        if ok + ko:
            print(f"{strategy};TOTAL;{ok};{ko};{ok+ko};{100*ok/(ok+ko):.2f}")
    print(f"Universe: {len(target_keys)} unique ranking matches; coverage: {dict(coverage)}")
    print("CAUTION: VG1 conditions are exact, but feature parity requires matching "
          "the original engine historical windows, team aliases and PPG semantics.")
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["MatchDate", "LeagueId", "Home", "Away", "HG", "AG", "BTTS",
                             "MinBTTSFull", "MinGFL5", "PPGGapFull", "DeltaBTTSL5",
                             "MinOverFull", *strategies])
            writer.writerows(audit)


if __name__ == "__main__":
    main()
