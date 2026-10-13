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


def load_history(path, matches):
    with open(path, encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        for row in reader:
            parsed = parse_row(row)
            if parsed is None:
                continue
            key, result = parsed
            item = matches.setdefault(key, {"result": None, "conflict": False, "history_only": True})
            if item["result"] is not None and item["result"] != result:
                item["conflict"] = True
            item["result"] = result


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
    parser.add_argument("--history", help="Optional full historical results CSV: LeagueId;MatchDate;Home;Away;HG;AG")
    parser.add_argument("--min-played", type=int, default=5,
                        help="Minimum preceding matches per team (default 5)")
    parser.add_argument("--output", help="Optional match-level audit CSV path")
    args = parser.parse_args()

    matches = load_archive(args.archive)
    target_keys = set(matches)
    if args.history:
        load_history(args.history, matches)
    by_day = collections.defaultdict(list)
    for key in matches:
        by_day[key[1]].append(key)
    history = collections.defaultdict(list)
    stats = collections.defaultdict(lambda: [0, 0])
    audit = []
    coverage = collections.Counter()
    strategies = ("VG1_replayed", "VG1_plus_MinGFL5", "MinGFL5")
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
    print(f"Coverage: {dict(coverage)}")
    print("CAUTION: VG1 conditions are exact, but input features are reconstructed "
          "from available past results; complete season history is needed for "
          "a faithful VG1 replay.")
    if args.output:
        with open(args.output, "w", newline="", encoding="utf-8-sig") as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow(["MatchDate", "LeagueId", "Home", "Away", "HG", "AG", "BTTS",
                             "MinBTTSFull", "MinGFL5", "PPGGapFull", "DeltaBTTSL5",
                             "MinOverFull", *strategies])
            writer.writerows(audit)


if __name__ == "__main__":
    main()
