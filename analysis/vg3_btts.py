"""Laboratorio e ranking sperimentale VG3. Eseguire dalla radice del repository."""
import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import date, timedelta
from itertools import groupby
from pathlib import Path

ROOT = Path("data/storico")
MODEL = Path(__file__).with_name("vg3_btts_model.json")
TRAIN_END = date(2026, 9, 23)
VALID_END = date(2026, 10, 23)
TEST_END = date(2026, 11, 22)
WINDOW = timedelta(days=180)
FEATURES = ["gol_incrociato", "gol_incrociato_sede", "btts_squadre", "btts_recente", "btts_lega"]


def rows(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        yield from csv.DictReader(handle, delimiter=";")


def key(row, league):
    return date.fromisoformat(row["MatchDate"].strip()), league.strip(), row["Home"].strip(), row["Away"].strip()


def archive():
    scores = defaultdict(set)
    vg1 = defaultdict(set)
    banned = set()
    audit = Counter()
    sources = {}
    for folder in ("risultati", "ranking", "gs1_over"):
        paths = sorted((ROOT / folder).rglob("*.csv"))
        audit[folder + "_files"] = len(paths)
        source_keys = set()
        for path in paths:
            for row in rows(path):
                audit[folder + "_rows"] += 1
                league = row.get("LeagueId", path.stem)
                try:
                    k = key(row, league)
                except (ValueError, AttributeError):
                    audit["invalid_key_rows"] += 1
                    continue
                if league.startswith("Australia_") or k[0].year < 2025 or not all(k[1:]):
                    continue
                if "award" in (row.get("Notes") or "").lower():
                    banned.add(k)
                if folder != "risultati" and row.get("MatchStatus", row.get("Status")) not in {"FINAL", "FINALE"}:
                    continue
                if not all((row[c] or "").strip().isdigit() for c in ("HG", "AG")):
                    audit["invalid_scores"] += 1
                    continue
                scores[k].add((int(row["HG"]), int(row["AG"])))
                source_keys.add(k)
                if path.parent.name == "vg1" and row.get("PredictionDate") and row["PredictionDate"] <= k[0].isoformat():
                    vg1[k].add(row["Band"])
        sources[folder] = source_keys
    audit["ranking_or_gs1_only"] = len((sources["ranking"] | sources["gs1_over"]) - sources["risultati"])
    audit["conflicting_scores"] = sum(len(v) > 1 for v in scores.values())
    audit["awarded"] = len(banned)
    finals = {k: next(iter(v)) for k, v in scores.items() if len(v) == 1 and k not in banned}
    audit["finals"] = len(finals)
    return finals, {k: next(iter(v)) for k, v in vg1.items() if len(v) == 1}, audit


def rate(history, idx, prior):
    return (sum(x[idx] for x in history) + 5 * prior) / (len(history) + 5)


def features(k, teams, leagues):
    day, league, home, away = k
    after = day - WINDOW
    def recent(team):
        return [x for x in teams[league, team] if x[0] >= after]
    h, a = recent(home), recent(away)
    if min(len(h), len(a)) < 5:
        return None
    def crossed(hh, aa):
        ph = (rate(hh, 1, .75) + rate(aa, 2, .75)) / 2
        pa = (rate(aa, 1, .70) + rate(hh, 2, .70)) / 2
        return ph * pa
    def btts(hh, aa):
        return (rate(hh, 3, .55) + rate(aa, 3, .55)) / 2
    lg = [x for x in leagues[league] if x[0] >= after]
    return [crossed(h, a), crossed([x for x in h if x[4]], [x for x in a if not x[4]]),
            btts(h, a), btts(h[-8:], a[-8:]), (sum(x[1] for x in lg) + 11) / (len(lg) + 20)]


def replay(finals, targets):
    teams, leagues = defaultdict(list), defaultdict(list)
    for day, group in groupby(sorted(finals.keys() | targets), key=lambda k: k[0]):
        fixtures = list(group)
        for k in fixtures:
            if k in targets:
                yield k, features(k, teams, leagues)
        for k in fixtures:
            if k in finals:
                _, league, home, away = k
                h, a = finals[k]
                both = h > 0 and a > 0
                teams[league, home].append((day, h > 0, a > 0, both, True))
                teams[league, away].append((day, a > 0, h > 0, both, False))
                leagues[league].append((day, both))


def probability(x, model):
    z = model["intercept"] + sum(v * w for v, w in zip(x, model["weights"]))
    return 1 / (1 + math.exp(-z))


def tally(frame):
    n = len(frame)
    ok = int(frame.y.sum())
    daily = frame.groupby("day").y.agg(["sum", "count"])
    return dict(ok=ok, ko=n-ok, total=n, percent=round(100*ok/n, 2) if n else None,
                days=len(daily), perfect_days=int((daily["sum"] == daily["count"]).sum()))


def train(finals, vg1):
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    records = []
    for k, x in replay(finals, set(finals)):
        if x is not None and k[0] <= TEST_END:
            records.append([*k, min(finals[k]) > 0, vg1.get(k), *x])
    frame = pd.DataFrame(records, columns=["day", "league", "home", "away", "y", "vg1", *FEATURES])
    tr = frame[frame.day <= TRAIN_END]
    fit = LogisticRegression(C=1, max_iter=1000).fit(tr[FEATURES], tr.y)
    model = dict(features=FEATURES, weights=fit.coef_[0].tolist(), intercept=float(fit.intercept_[0]))
    frame["p"] = [probability(x, model) for x in frame[FEATURES].itertuples(index=False, name=None)]
    val = frame[(frame.day > TRAIN_END) & (frame.day <= VALID_END)]
    test = frame[frame.day > VALID_END]
    candidates = []
    for t in range(60, 86):
        chosen = val[val.p >= t/100]
        if len(chosen) >= 50 and chosen.day.nunique() >= 8:
            n, p = len(chosen), chosen.y.mean()
            z = 1.96
            lower = (p+z*z/(2*n)-z*math.sqrt(p*(1-p)/n+z*z/(4*n*n)))/(1+z*z/n)
            candidates.append((lower, t))
    model["alta"] = max(candidates)[1] / 100
    MODEL.write_text(json.dumps(model, indent=2) + "\n")
    print("model", model)
    for label, part in [("train", tr), ("validation", val), ("test", test)]:
        print(label, "mature", tally(part))
        if label == "train":
            continue
        alta = part.p >= model["alta"]
        common = part.vg1.notna()
        for name, mask in [("VG3", alta), ("common", common), ("VG3 common", common & alta),
                           ("VG1 common", common & part.vg1.eq("ALTA"))]:
            print(label, name, tally(part[mask]))
        ordered = part[alta].sort_values(["day", "p", "league", "home", "away"],
                                                  ascending=[True, False, True, True, True])
        for limit in (1, 2):
            print(label, f"VG3 TOP{limit}", tally(ordered.groupby("day").head(limit)))
            common_ordered = ordered[ordered.vg1.notna()]
            print(label, f"VG3 common TOP{limit}", tally(common_ordered.groupby("day").head(limit)))
    for start, end in [(TRAIN_END, VALID_END), (VALID_END, TEST_END)]:
        actual = [min(finals[k]) > 0 for k, band in vg1.items() if k in finals and start < k[0] <= end and band == "ALTA"]
        print("VG1 archived ALTA", start, end, sum(actual), len(actual))


def rank(finals, path, output):
    model = json.loads(MODEL.read_text())
    targets = {key(row, row["LeagueId"]) for row in rows(path)}
    result = []
    for k, x in replay(finals, targets):
        p = probability(x, model) if x is not None and not k[1].startswith("Australia_") else None
        band = "NESSUN-SEGNALE" if p is None else "ALTA" if p >= model["alta"] else "BASSA"
        result.append((k, p, band))
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["MatchDate", "LeagueId", "Home", "Away", "Score", "Band"])
        for k, p, band in sorted(result, key=lambda r: (r[0][0], -(r[1] or 0), r[0])):
            writer.writerow([*k, "" if p is None else round(100*p, 3), band])
    print(output, Counter(r[2] for r in result))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--train", action="store_true")
    mode.add_argument("--rank", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/output_ranking/vg3/ranking_vg3.csv"))
    args = parser.parse_args()
    finals, vg1, audit = archive()
    print(dict(audit))
    if args.train:
        train(finals, vg1)
    else:
        rank(finals, args.rank, args.output)
