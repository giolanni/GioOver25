"""Backfill/onboarding della stagione corrente da pagina risultati Diretta.

Default dry-run. Con --apply crea lo storico risultati e aggiunge al registry
solo le competizioni esplicitamente configurate in ONBOARDING.
"""
from __future__ import annotations

import argparse
import csv
import re
import unicodedata

from tools.flashscore_history import fetch_embedded_results
from tools.prepare_input import ROOT

ONBOARDING = {
    ("Australia", "A-League"): ("Australia_ALeague", 12, 26, "No",
        "2026/27: 12 club; 26 partite per club, con alcuni avversari affrontati tre volte"),
    ("India", "ISL"): ("India_ISL", 13, 26, "Yes",
        "2026/27: 13 club; doppio round-robin, 24 partite per club e turni di riposo"),
    ("Qatar", "QSL"): ("Qatar_QSL", 12, 22, "Yes",
        "2026/27: 12 club; doppio round-robin su 22 giornate"),
}


def slug(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def write_results(path, country, league, matches):
    if path.exists():
        raise SystemExit(f"[ABORT] Storico gia' esistente: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.writer(h, delimiter=";", lineterminator="\n")
        w.writerow(["Country","League","Round","MatchDate","Home","Away","HG","AG","Notes"])
        for m in matches:
            w.writerow([country, league, m.round, m.date, m.home, m.away, m.hg, m.ag, ""])


def add_registry(path, country, league, spec):
    league_id, teams, rounds, home_away, notes = spec
    with path.open(encoding="utf-8-sig", newline="") as h:
        rows = list(csv.DictReader(h, delimiter=";"))
    if any((r.get("LeagueId") or "").strip() == league_id for r in rows):
        raise SystemExit(f"[ABORT] LeagueId gia' presente nel registry: {league_id}")
    if any((r.get("Country") or "").strip() == country and (r.get("League") or "").strip() == league for r in rows):
        raise SystemExit(f"[ABORT] Country+League gia' presente nel registry: {country};{league}")

    fieldnames = list(rows[0].keys()) if rows else [
        "LeagueId","Country","League","Teams","ExpectedRounds","HomeAway","Notes","CompetitionGroup",""
    ]
    new = {k: "" for k in fieldnames}
    new.update({
        "LeagueId": league_id, "Country": country, "League": league,
        "Teams": str(teams), "ExpectedRounds": str(rounds),
        "HomeAway": home_away, "Notes": notes, "CompetitionGroup": "",
    })
    rows.append(new)
    rows.sort(key=lambda r: (r.get("LeagueId") or "").casefold())
    with path.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fieldnames, delimiter=";", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--country", required=True)
    ap.add_argument("--league", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    key = (args.country, args.league)
    spec = ONBOARDING.get(key)
    if args.apply and spec is None:
        raise SystemExit("[ABORT] --apply consentito solo per leghe configurate in ONBOARDING")

    url = f"https://www.diretta.it/calcio/{slug(args.country)}/{slug(args.league)}/risultati/"
    try:
        ids, matches, payload = fetch_embedded_results(url)
    except Exception as exc:
        raise SystemExit(f"[ERROR] {url}: {type(exc).__name__}: {exc}")

    matches.sort(key=lambda m: (m.date, int(m.round) if m.round.isdigit() else 9999, m.home, m.away))
    safe = "".join(ch if ch.isalnum() else "_" for ch in f"{args.country}_{args.league}").strip("_")
    debug_out = ROOT / "data" / "debug" / f"backfill_{safe}.csv"
    debug_out.parent.mkdir(parents=True, exist_ok=True)
    with debug_out.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.writer(h, delimiter=";")
        w.writerow(["Round","MatchDate","Home","Away","HG","AG","MatchId"])
        for m in matches:
            w.writerow([m.round, m.date, m.home, m.away, m.hg, m.ag, m.match_id])

    first = matches[0].date if matches else "-"
    last = matches[-1].date if matches else "-"
    print(f"[SOURCE] {url}")
    print(f"[IDS] template={ids.get('template_id') or '-'} | tournament={ids.get('tournament_id') or '-'} | stage={ids.get('stage_id') or '-'}")
    print(f"[BACKFILL] {args.country}: {args.league} | matches={len(matches)} | {first} -> {last} | payload={len(payload)}")
    print(f"[OUTPUT] {debug_out}")

    if not args.apply:
        print("[DRY-RUN] Nessuna modifica a registry o storici.")
        return
    if not matches:
        raise SystemExit("[ABORT] Nessun risultato concluso: onboarding non applicato")

    league_id = spec[0]
    registry = ROOT / "data" / "league_registry.csv"
    result_path = ROOT / "data" / "storico" / "risultati" / f"{league_id}.csv"

    # Preflight: nessuna scrittura se uno dei due target esiste gia'.
    with registry.open(encoding="utf-8-sig", newline="") as h:
        existing = list(csv.DictReader(h, delimiter=";"))
    if result_path.exists():
        raise SystemExit(f"[ABORT] Storico gia' esistente: {result_path}")
    if any((r.get("LeagueId") or "").strip() == league_id for r in existing):
        raise SystemExit(f"[ABORT] LeagueId gia' presente: {league_id}")

    write_results(result_path, args.country, args.league, matches)
    try:
        add_registry(registry, args.country, args.league, spec)
    except Exception:
        result_path.unlink(missing_ok=True)
        raise

    print(f"[APPLY] registry + storico creati per {league_id}: {len(matches)} risultati")


if __name__ == "__main__":
    main()
