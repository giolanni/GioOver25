"""
GioOver2.5 - v20 PROX-ALTA retroactive backtest

SCOPO
-----
Verifica retroattivamente se applicare a v20 lo stesso controllo PROX di v26
migliora o peggiora l'affidabilita' della fascia ALTA.

Regola PROX v26 riprodotta:
- entrambe le squadre devono avere almeno 10 partite precedenti;
- gap PPG <= 0.30;
- se la partita v20 e' ALTA viene marcata PROX-ALTA;
- lo score numerico non cambia.

Il test confronta:
1. V20_ALTA_BASELINE: tutte le ALTA originali di v20;
2. V20_ALTA_NO_PROX: ALTA originali escluse quelle che sarebbero PROX-ALTA;
3. V20_PROX_ALTA: solo il sottoinsieme che sarebbe stato marcato PROX-ALTA.

ANTI-LEAKAGE
------------
Played, punti e PPG sono ricostruiti usando esclusivamente risultati con
MatchDate STRETTAMENTE precedente alla partita analizzata. Le partite dello
stesso giorno non vengono usate.

In aggiunta viene prodotta una sensitivity analysis sul limite PPG e sul
numero minimo di partite, senza modificare l'engine.

ESECUZIONE
----------
python -m analysis.experiments.v20_prox_alta_backtest

OUTPUT
------
analysis/experiments/v20_prox_alta/output/
    summary.txt
    v20_alta_with_prox.csv
    comparison.csv
    monthly_comparison.csv
    sensitivity.csv
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from gioover25.team_names import normalize_team_name

ROOT = Path(".")
RANKING_PATH = ROOT / "data" / "storico" / "ranking" / "v20" / "storico_ranking_v20.csv"
RESULTS_ROOT = ROOT / "data" / "storico" / "risultati"
OUTPUT_DIR = ROOT / "analysis" / "experiments" / "v20_prox_alta" / "output"

# Parametri IDENTICI a v26
PROX_MIN_MATCHES = 10
PROX_PPG_THRESHOLD = 0.30


@dataclass(frozen=True)
class TeamMatch:
    match_date: date
    points: int


def text(value) -> str:
    return str(value or "").strip()


def to_int(value, default=None):
    raw = text(value)
    if not raw:
        return default
    try:
        return int(float(raw.replace(",", ".")))
    except ValueError:
        return default


def parse_date(value) -> date | None:
    raw = text(value)
    if not raw:
        return None
    raw = raw[:10]
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    return None


def read_csv(path: Path) -> list[dict]:
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if not reader.fieldnames:
            raise ValueError(f"Header assente: {path}")
        return list(reader)


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def effective_date(row: dict) -> str:
    return text(row.get("MatchDate")) or text(row.get("PredictionDate"))


def outcome_for(row: dict) -> str:
    for field in ("Outcome", "Over25"):
        value = text(row.get(field)).upper()
        if value in {"OK", "KO"}:
            return value
    goals = to_int(row.get("Goals"))
    if goals is not None:
        return "OK" if goals >= 3 else "KO"
    hg = to_int(row.get("HG"))
    ag = to_int(row.get("AG"))
    if hg is not None and ag is not None:
        return "OK" if hg + ag >= 3 else "KO"
    return ""


def band_for(row: dict) -> str:
    return text(row.get("Band") or row.get("Fascia")).upper()


def match_key(row: dict):
    league = text(row.get("LeagueId"))
    return (
        effective_date(row),
        league,
        normalize_team_name(league, row.get("Home")),
        normalize_team_name(league, row.get("Away")),
    )


def load_v20_alta() -> list[dict]:
    if not RANKING_PATH.exists():
        raise FileNotFoundError(f"Storico v20 non trovato: {RANKING_PATH}")

    rows = read_csv(RANKING_PATH)
    candidates = []
    for row in rows:
        if band_for(row) != "ALTA":
            continue
        if outcome_for(row) not in {"OK", "KO"}:
            continue
        if parse_date(effective_date(row)) is None:
            continue
        candidates.append(row)

    # Un solo pronostico per partita, preferendo la PredictionDate piu' antica.
    candidates.sort(key=lambda r: (text(r.get("PredictionDate")) or "9999-99-99", effective_date(r)))
    unique = {}
    for row in candidates:
        unique.setdefault(match_key(row), row)

    result = list(unique.values())
    result.sort(key=lambda r: (effective_date(r), text(r.get("LeagueId")), text(r.get("Home")), text(r.get("Away"))))
    return result


def load_points_index() -> dict[tuple[str, str], list[TeamMatch]]:
    """Crea storico point-in-time di partite e punti per squadra/LeagueId."""
    index: dict[tuple[str, str], list[TeamMatch]] = defaultdict(list)

    for path in sorted(RESULTS_ROOT.glob("*.csv")):
        league_from_file = path.stem
        try:
            rows = read_csv(path)
        except Exception as exc:
            print(f"[WARN] salto {path}: {exc}")
            continue

        for row in rows:
            match_date = parse_date(row.get("MatchDate"))
            hg = to_int(row.get("HG"))
            ag = to_int(row.get("AG"))
            if match_date is None or hg is None or ag is None:
                continue

            status = text(row.get("Status")).upper()
            if status and status not in {"FINAL", "FINISHED", "FT", "PLAYED", "OK"}:
                continue

            league = text(row.get("LeagueId")) or league_from_file
            home = normalize_team_name(league, row.get("Home"))
            away = normalize_team_name(league, row.get("Away"))
            if not home or not away:
                continue

            if hg > ag:
                hp, ap = 3, 0
            elif hg < ag:
                hp, ap = 0, 3
            else:
                hp, ap = 1, 1

            index[(league, home)].append(TeamMatch(match_date, hp))
            index[(league, away)].append(TeamMatch(match_date, ap))

    for matches in index.values():
        matches.sort(key=lambda x: x.match_date)
    return index


def prior_record(index, league: str, team: str, before: date) -> tuple[int, int, float | None]:
    played = 0
    points = 0
    for item in index.get((league, team), []):
        if item.match_date >= before:
            break
        played += 1
        points += item.points
    ppg = (points / played) if played else None
    return played, points, ppg


def is_prox(home_played: int, away_played: int, home_ppg: float | None, away_ppg: float | None,
            *, min_matches: int = PROX_MIN_MATCHES, ppg_threshold: float = PROX_PPG_THRESHOLD) -> bool:
    if home_played < min_matches or away_played < min_matches:
        return False
    if home_ppg is None or away_ppg is None:
        return False
    return abs(home_ppg - away_ppg) <= ppg_threshold


def stats(rows: list[dict]) -> dict:
    ok = sum(1 for r in rows if r["Outcome"] == "OK")
    ko = sum(1 for r in rows if r["Outcome"] == "KO")
    total = ok + ko
    pct = (ok / total * 100.0) if total else 0.0
    no_au = [r for r in rows if not text(r.get("LeagueId")).startswith("Australia_")]
    ok_no_au = sum(1 for r in no_au if r["Outcome"] == "OK")
    ko_no_au = sum(1 for r in no_au if r["Outcome"] == "KO")
    tot_no_au = ok_no_au + ko_no_au
    pct_no_au = (ok_no_au / tot_no_au * 100.0) if tot_no_au else 0.0
    return {
        "Tot": total,
        "OK": ok,
        "KO": ko,
        "PercentOK": round(pct, 2),
        "TotNoAU": tot_no_au,
        "OKNoAU": ok_no_au,
        "KONoAU": ko_no_au,
        "PercentOKNoAU": round(pct_no_au, 2),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    predictions = load_v20_alta()
    points_index = load_points_index()

    enriched: list[dict] = []
    missing_context = 0

    for row in predictions:
        match_date = parse_date(effective_date(row))
        league = text(row.get("LeagueId"))
        home = normalize_team_name(league, row.get("Home"))
        away = normalize_team_name(league, row.get("Away"))
        hp, hpts, hppg = prior_record(points_index, league, home, match_date)
        ap, apts, appg = prior_record(points_index, league, away, match_date)

        if hp == 0 and ap == 0:
            missing_context += 1

        prox = is_prox(hp, ap, hppg, appg)
        enriched.append({
            "MatchDate": effective_date(row),
            "LeagueId": league,
            "Home": text(row.get("Home")),
            "Away": text(row.get("Away")),
            "Score": text(row.get("Score")),
            "OriginalBand": "ALTA",
            "ProxBand": "PROX-ALTA" if prox else "ALTA",
            "Outcome": outcome_for(row),
            "HomePlayedBefore": hp,
            "AwayPlayedBefore": ap,
            "HomePointsBefore": hpts,
            "AwayPointsBefore": apts,
            "HomePPG": "" if hppg is None else round(hppg, 4),
            "AwayPPG": "" if appg is None else round(appg, 4),
            "PPGGap": "" if hppg is None or appg is None else round(abs(hppg - appg), 4),
            "IsProx": "YES" if prox else "NO",
        })

    baseline = enriched
    prox_rows = [r for r in enriched if r["IsProx"] == "YES"]
    no_prox = [r for r in enriched if r["IsProx"] == "NO"]

    comparison = []
    for name, rows in (
        ("V20_ALTA_BASELINE", baseline),
        ("V20_ALTA_NO_PROX", no_prox),
        ("V20_PROX_ALTA", prox_rows),
    ):
        comparison.append({"Segment": name, **stats(rows)})

    monthly = []
    months = sorted({text(r["MatchDate"])[:7] for r in enriched if len(text(r["MatchDate"])) >= 7})
    for month in months:
        month_rows = [r for r in enriched if text(r["MatchDate"]).startswith(month)]
        for name, rows in (
            ("V20_ALTA_BASELINE", month_rows),
            ("V20_ALTA_NO_PROX", [r for r in month_rows if r["IsProx"] == "NO"]),
            ("V20_PROX_ALTA", [r for r in month_rows if r["IsProx"] == "YES"]),
        ):
            monthly.append({"Month": month, "Segment": name, **stats(rows)})

    sensitivity = []
    for min_matches in (5, 7, 8, 9, 10, 11, 12):
        for threshold in (0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50):
            prox_s = []
            no_prox_s = []
            for r in enriched:
                hp = int(r["HomePlayedBefore"])
                ap = int(r["AwayPlayedBefore"])
                hppg = None if r["HomePPG"] == "" else float(r["HomePPG"])
                appg = None if r["AwayPPG"] == "" else float(r["AwayPPG"])
                if is_prox(hp, ap, hppg, appg, min_matches=min_matches, ppg_threshold=threshold):
                    prox_s.append(r)
                else:
                    no_prox_s.append(r)
            prox_stats = stats(prox_s)
            keep_stats = stats(no_prox_s)
            sensitivity.append({
                "MinMatches": min_matches,
                "PPGThreshold": threshold,
                "KeptTot": keep_stats["Tot"],
                "KeptOK": keep_stats["OK"],
                "KeptKO": keep_stats["KO"],
                "KeptPercentOK": keep_stats["PercentOK"],
                "ProxTot": prox_stats["Tot"],
                "ProxOK": prox_stats["OK"],
                "ProxKO": prox_stats["KO"],
                "ProxPercentOK": prox_stats["PercentOK"],
                "KeptPercentOKNoAU": keep_stats["PercentOKNoAU"],
                "ProxPercentOKNoAU": prox_stats["PercentOKNoAU"],
            })

    write_csv(OUTPUT_DIR / "v20_alta_with_prox.csv", enriched)
    write_csv(OUTPUT_DIR / "comparison.csv", comparison)
    write_csv(OUTPUT_DIR / "monthly_comparison.csv", monthly)
    write_csv(OUTPUT_DIR / "sensitivity.csv", sensitivity)

    base_s = stats(baseline)
    keep_s = stats(no_prox)
    prox_s = stats(prox_rows)
    delta = keep_s["PercentOK"] - base_s["PercentOK"]
    delta_no_au = keep_s["PercentOKNoAU"] - base_s["PercentOKNoAU"]

    lines = [
        "V20 PROX-ALTA RETROACTIVE BACKTEST",
        "=================================",
        "",
        f"Regola v26: min partite per squadra = {PROX_MIN_MATCHES}; PPG gap <= {PROX_PPG_THRESHOLD:.2f}",
        "Il PROX non modifica lo score: separa le ALTA equilibrate per PPG.",
        "",
        f"Pronostici ALTA v20 con esito: {base_s['Tot']}",
        f"Contesto completamente assente (0 gare entrambe): {missing_context}",
        "",
        f"BASELINE v20 ALTA      : {base_s['OK']}/{base_s['Tot']} = {base_s['PercentOK']:.2f}%  (no AU {base_s['PercentOKNoAU']:.2f}%)",
        f"ALTA escludendo PROX   : {keep_s['OK']}/{keep_s['Tot']} = {keep_s['PercentOK']:.2f}%  (no AU {keep_s['PercentOKNoAU']:.2f}%)",
        f"solo PROX-ALTA         : {prox_s['OK']}/{prox_s['Tot']} = {prox_s['PercentOK']:.2f}%  (no AU {prox_s['PercentOKNoAU']:.2f}%)",
        "",
        f"Delta ALTA_NO_PROX vs baseline: {delta:+.2f} punti percentuali",
        f"Delta no AU                  : {delta_no_au:+.2f} punti percentuali",
        "",
        "LETTURA:",
        "- delta positivo: separare PROX-ALTA rende la ALTA residua piu' affidabile;",
        "- delta negativo: il controllo PROX peggiora la selezione se le PROX vengono escluse;",
        "- confrontare anche il rendimento del solo segmento PROX e la stabilita' mensile.",
        "",
        "Vedi sensitivity.csv per capire se 10 gare / 0.30 e' davvero la parametrizzazione migliore per v20.",
    ]
    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\n".join(lines))
    print(f"\nOutput: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
