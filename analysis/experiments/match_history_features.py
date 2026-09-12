from __future__ import annotations
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

RESULTS_DIR = Path("data/storico/risultati")

@dataclass(frozen=True)
class TeamGame:
    gf: int
    ga: int
    points: int
    @property
    def goals(self): return self.gf + self.ga
    @property
    def over25(self): return int(self.goals >= 3)
    @property
    def btts(self): return int(self.gf > 0 and self.ga > 0)

@dataclass(frozen=True)
class TeamStats:
    n: int
    gf_avg: float
    ga_avg: float
    goals_avg: float
    over_rate: float
    btts_rate: float
    ppg: float

def _text(value): return str(value or "").strip()
def _parse_date(value):
    try: return date.fromisoformat(_text(value))
    except ValueError: return None
def _parse_int(value):
    try: return int(_text(value))
    except ValueError: return None
def _team_key(value): return " ".join(_text(value).casefold().split())

def _stats(games, window=None):
    sample = games[-window:] if window else games
    if not sample: return None
    n = len(sample)
    return TeamStats(n,
        sum(g.gf for g in sample)/n,
        sum(g.ga for g in sample)/n,
        sum(g.goals for g in sample)/n,
        sum(g.over25 for g in sample)/n,
        sum(g.btts for g in sample)/n,
        sum(g.points for g in sample)/n)

def _add(row, prefix, stats, suffix):
    row[f"{prefix}Played{suffix}"] = stats.n
    row[f"{prefix}GF{suffix}"] = stats.gf_avg
    row[f"{prefix}GA{suffix}"] = stats.ga_avg
    row[f"{prefix}Goals{suffix}"] = stats.goals_avg
    row[f"{prefix}OverRate{suffix}"] = stats.over_rate
    row[f"{prefix}BTTSRate{suffix}"] = stats.btts_rate
    row[f"{prefix}PPG{suffix}"] = stats.ppg

def build_feature_rows(results_dir=RESULTS_DIR, min_history=5, windows=(5,7,8)):
    """Costruisce feature usando solo partite strettamente precedenti.

    Le partite della stessa MatchDate vengono valutate tutte prima di aggiornare
    lo storico: in questo modo non esiste look-ahead neppure nello stesso giorno.
    """
    rows = []
    windows = tuple(sorted(set(int(w) for w in windows if int(w) > 0)))
    for path in sorted(results_dir.glob("*.csv")):
        league_id = path.stem
        raw_matches = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=";")
            if {"MatchDate","Home","Away","HG","AG"}.difference(reader.fieldnames or []):
                continue
            for raw in reader:
                d = _parse_date(raw.get("MatchDate"))
                hg, ag = _parse_int(raw.get("HG")), _parse_int(raw.get("AG"))
                home, away = _text(raw.get("Home")), _text(raw.get("Away"))
                if d is None or hg is None or ag is None or not home or not away:
                    continue
                raw_matches.append({"MatchDate": d, "Round": _text(raw.get("Round")), "Home": home, "Away": away, "HG": hg, "AG": ag})
        raw_matches.sort(key=lambda x: (x["MatchDate"], x["Home"], x["Away"]))
        history = {}
        i = 0
        while i < len(raw_matches):
            d = raw_matches[i]["MatchDate"]
            day = []
            while i < len(raw_matches) and raw_matches[i]["MatchDate"] == d:
                day.append(raw_matches[i]); i += 1
            for m in day:
                hk, ak = _team_key(m["Home"]), _team_key(m["Away"])
                hgms, agms = history.get(hk, []), history.get(ak, [])
                if len(hgms) < min_history or len(agms) < min_history:
                    continue
                fh, fa = _stats(hgms), _stats(agms)
                row = {"LeagueId": league_id, "MatchDate": d.isoformat(), "Round": m["Round"], "Home": m["Home"], "Away": m["Away"],
                       "HG": m["HG"], "AG": m["AG"], "Goals": m["HG"]+m["AG"], "Over25": int(m["HG"]+m["AG"] >= 3),
                       "BTTS": int(m["HG"] > 0 and m["AG"] > 0), "HomePlayedBefore": len(hgms), "AwayPlayedBefore": len(agms),
                       "MinPlayedBefore": min(len(hgms),len(agms)), "MaxPlayedBefore": max(len(hgms),len(agms))}
                _add(row,"Home",fh,"Full"); _add(row,"Away",fa,"Full")
                for w in windows:
                    _add(row,"Home",_stats(hgms,w),f"L{w}"); _add(row,"Away",_stats(agms,w),f"L{w}")
                rows.append(row)
            for m in day:
                hk, ak = _team_key(m["Home"]), _team_key(m["Away"])
                hg, ag = m["HG"], m["AG"]
                hp = 3 if hg > ag else 1 if hg == ag else 0
                ap = 3 if ag > hg else 1 if hg == ag else 0
                history.setdefault(hk,[]).append(TeamGame(hg,ag,hp))
                history.setdefault(ak,[]).append(TeamGame(ag,hg,ap))
    return rows

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows: return
    fields = []
    for row in rows:
        for key in row:
            if key not in fields: fields.append(key)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
        writer.writeheader(); writer.writerows(rows)
