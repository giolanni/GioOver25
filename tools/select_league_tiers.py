"""Seleziona dal discovery le competizioni nazionali maschili di livello 1-3.

Dry-run: non modifica registry o storici. La classificazione e' volutamente
conservativa: i nomi certi vengono assegnati a TIER1/2/3, gli altri NEW
potenzialmente nazionali finiscono in REVIEW.
"""
from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime
from pathlib import Path

from tools.prepare_input import ROOT, load_registry, norm
from tools.prepare_league_onboarding import proposed_league_id

EXCLUDE_KINDS = {"INTERNATIONAL", "TEMPORARY", "WOMEN_LEAGUE", "YOUTH"}

# Diretta localizza alcuni nomi paese in italiano, mentre registry/tier map
# usano prevalentemente denominazioni inglesi.
COUNTRY_ALIASES = {
    "brasile": "Brazil",
    "cile": "Chile",
    "cina": "China",
    "egitto": "Egypt",
    "emirati arabi": "United Arab Emirates",
    "grecia": "Greece",
    "irlanda": "Ireland",
    "islanda": "Iceland",
    "malesia": "Malaysia",
    "marocco": "Morocco",
    "messico": "Mexico",
    "paesi bassi": "Netherlands",
    "repubblica dominicana": "Dominican Republic",
    "sudafrica": "South Africa",
    "svizzera": "Switzerland",
    "tagikistan": "Tajikistan",
    "thailandia": "Thailand",
    "tunisia": "Tunisia",
    "turchia": "Turkey",
    "ucraina": "Ukraine",
    "uzbekistan": "Uzbekistan",
    "vietnam": "Vietnam",
}

# Pattern espliciti: evitare inferenze aggressive su nomi ambigui.
TIER_PATTERNS = {
    1: (
        r"\bpremier league\b", r"\bpremiership\b", r"\bsuperliga\b",
        r"\bsuper league\b", r"\bprimera division\b", r"\bdivision profesional\b",
        r"\bliga 1\b", r"\bligue 1\b", r"\bserie a\b", r"\bbundesliga\b",
        r"\bere(divisie|divisie)\b", r"\bvirsliga\b", r"\bmeistriliiga\b",
        r"\beliteserien\b", r"\bparva liga\b", r"\bprva liga\b",
        r"\b1\.?\s*(liga|division|divisio|mfl)\b", r"\bj1 league\b",
    ),
    2: (
        r"\bsecond division\b", r"\b2nd division\b", r"\bdivision 2\b",
        r"\b2\.?\s*(liga|division|bundesliga)\b", r"\bliga 2\b", r"\bligue 2\b",
        r"\bserie b\b", r"\bchampionship\b", r"\beerste divisie\b",
        r"\bfirst league\b", r"\b1\.? deild\b", r"\bprva nl\b",
        r"\bvtora liga\b", r"\bchallenger pro league\b", r"\bykkosliiga\b",
        r"\bobos.?ligaen\b",
    ),
    3: (
        r"\bthird division\b", r"\b3rd division\b", r"\bdivision 3\b",
        r"\b3\.?\s*(liga|division)\b", r"\bliga 3\b", r"\bserie c\b",
        r"\bnational\b", r"\b2nd division\b", r"\bkakkonen\b",
        r"\besiliiga b\b", r"\bregionalliga\b",
    ),
}

# Eccezioni note dove il nome non codifica intuitivamente il livello.
KNOWN = {
    ("england", "premier league"): 1,
    ("england", "championship"): 2,
    ("england", "league one"): 3,
    ("france", "national"): 3,
    ("germany", "3 liga"): 3,
    ("finland", "ykkonen"): 3,
    ("estonia", "esiliiga b"): 3,
}


def latest_discovery() -> Path:
    files = sorted((ROOT / "data" / "debug").glob("discover_leagues_*.csv"))
    if not files:
        raise SystemExit("Nessun discover_leagues_*.csv trovato")
    return files[-1]


def load_tier_map() -> dict[tuple[str, str], int]:
    path = ROOT / "data" / "league_tier_map.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        lines = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
        rows = csv.DictReader(lines, delimiter=";")
        return {(norm(r["Country"]), norm(r["League"])): int(r["Tier"]) for r in rows}


def tier(country: str, league: str, tier_map: dict[tuple[str, str], int]) -> int | None:
    mapped_country = COUNTRY_ALIASES.get(norm(country), country)
    return tier_map.get((norm(mapped_country), norm(league)))

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", help="CSV discovery; default: ultimo")
    args = p.parse_args()
    source = ROOT / args.input if args.input else latest_discovery()

    registry = load_registry(ROOT / "data" / "league_registry.csv")
    tier_map = load_tier_map()
    registry_ids = {r.league_id.casefold() for r in registry}
    rows = list(csv.DictReader(source.open(encoding="utf-8-sig", newline=""), delimiter=";"))

    selected = []
    for row in rows:
        # Considera l'intera piramide attiva: KNOWN, KNOWN_ALIAS e NEW.
        # Le categorie non appartenenti ai campionati nazionali senior restano escluse.
        if row["Status"] == "NEW" and row["KindOrLeagueId"] in EXCLUDE_KINDS:
            continue
        level = tier(row["Country"], row["League"], tier_map)
        proposed = proposed_league_id(row["Country"], row["League"])
        if row["Status"] in {"KNOWN", "KNOWN_ALIAS"}:
            registry_status = f"COVERED:{row['KindOrLeagueId']}"
        elif proposed.casefold() in registry_ids:
            # Il discovery puo' essere precedente all'onboarding: se il LeagueId
            # proposto ora esiste, la competizione e' coperta, non in collisione.
            registry_status = f"COVERED:{proposed}"
        else:
            registry_status = "MISSING"
        selected.append({
            **row,
            "Tier": f"TIER{level}" if level else "REVIEW",
            "ProposedLeagueId": proposed,
            "RegistryStatus": registry_status,
        })

    order = {"TIER1": 1, "TIER2": 2, "TIER3": 3, "REVIEW": 9}
    selected.sort(key=lambda r: (order[r["Tier"]], r["Country"].casefold(), r["League"].casefold()))

    out = ROOT / "data" / "debug" / f"league_tier123_{datetime.now():%Y%m%d-%H%M%S}.csv"
    fields = ["Tier","RegistryStatus","Country","League","ProposedLeagueId","Matches","FirstDate","LastDate",
              "TournamentId","TournamentStageId","SampleMatchId"]
    with out.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(selected)

    counts = {k: sum(r["Tier"] == k for r in selected) for k in ("TIER1","TIER2","TIER3","REVIEW")}
    tier123 = [r for r in selected if r["Tier"] != "REVIEW"]
    covered = sum(r["RegistryStatus"].startswith("COVERED:") for r in tier123)
    missing = sum(r["RegistryStatus"] == "MISSING" for r in tier123)
    collisions = sum(r["RegistryStatus"] == "ID_COLLISION" for r in tier123)
    missing_by_tier = {
        k: sum(r["Tier"] == k and r["RegistryStatus"] == "MISSING" for r in tier123)
        for k in ("TIER1", "TIER2", "TIER3")
    }
    print(f"[INPUT] {source}")
    print("[TIER123] " + " | ".join(f"{k}={v}" for k,v in counts.items()))
    print(f"[TIER123 REGISTRY] COVERED={covered} | MISSING={missing} | ID_COLLISION={collisions}")
    print("[TIER123 MISSING] " + " | ".join(f"{k}={v}" for k,v in missing_by_tier.items()))
    # Audit REVIEW: restringe i nomi non mappati che meritano controllo umano.
    # Non assegna automaticamente un tier: serve a trovare denominazioni non
    # convenzionali (es. Apertura/Clausura) senza introdurre falsi positivi.
    review_exclude = re.compile(
        r"\\b(cup|copa|coppa|coupe|pokal|trophy|super cup|supercup|"
        r"play.?off|relegation|promotion|qualification|qualifying|"
        r"women|woman|femeni|feminin|femenin|frauen|damer|kvinn|"
        r"u\\d{2}|under.?\\d{2}|youth|junior|reserve|reserves|primavera)\\b",
        re.IGNORECASE,
    )
    review_hints = re.compile(
        r"\\b(liga|league|division|divisao|divisão|divisie|divisio|"
        r"championship|national|serie|superliga|premier|premiership|"
        r"apertura|clausura|primera|segunda|tercera|first|second|third|"
        r"1\\.?|2\\.?|3\\.?)\\b",
        re.IGNORECASE,
    )
    # Per l'audit partiamo da tutti i REVIEW: KindOrLeagueId e i nomi locali
    # non sono abbastanza affidabili per prefiltrare una piramide nazionale.
    # Eliminiamo soltanto le esclusioni evidenti dal nome; la decisione sul tier
    # resta umana.
    review_candidates = [
        r for r in selected
        if r["Tier"] == "REVIEW"
        and not review_exclude.search(r["League"])
    ]
    review_out = ROOT / "data" / "debug" / f"league_tier_review_{datetime.now():%Y%m%d-%H%M%S}.csv"
    review_fields = ["Country","League","Status","KindOrLeagueId","Matches","FirstDate","LastDate",
                     "TournamentId","TournamentStageId","SampleMatchId"]
    with review_out.open("w", encoding="utf-8-sig", newline="") as h:
        w = csv.DictWriter(h, fieldnames=review_fields, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(review_candidates)

    print(f"[OUTPUT] {out}")
    print(f"[REVIEW AUDIT] candidates={len(review_candidates)} | {review_out}")
    print("[DRY-RUN] Nessuna modifica a league_registry.csv o agli storici.")


if __name__ == "__main__":
    main()
