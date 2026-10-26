"""Arricchisce i candidati onboarding usando il catalogo tornei SofaScore.

Una sola chiamata a /config/unique-tournaments/EN/football costruisce la cache
dei tornei. Il matching e' locale e conservativo: nessun ID viene inventato.
Non modifica registry o storici.
"""
from __future__ import annotations

import argparse
import csv
import re
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

from tools.prepare_input import ROOT, norm
from tools.sofascore import get_json

API = "https://api.sofascore.com/api/v1"

COUNTRY_ALIASES = {
    "brasile": "brazil", "cile": "chile", "cina": "china", "cipro": "cyprus",
    "costarica": "costa rica", "egitto": "egypt", "emirati arabi": "united arab emirates",
    "etiopia": "ethiopia", "filippine": "philippines", "giamaica": "jamaica",
    "giordania": "jordan", "grecia": "greece", "irlanda": "ireland",
    "israele": "israel", "malesia": "malaysia", "marocco": "morocco",
    "nuova zelanda": "new zealand", "repubblica dominicana": "dominican republic",
    "ruanda": "rwanda", "sudafrica": "south africa", "tagikistan": "tajikistan",
    "thailandia": "thailand",
}


@dataclass
class Tournament:
    id: int
    name: str
    slug: str
    country: str


def latest_onboarding() -> Path:
    files = sorted((ROOT / "data" / "debug").glob("league_onboarding_*.csv"))
    if not files:
        raise SystemExit("Nessun league_onboarding_*.csv trovato in data/debug")
    return files[-1]


def words(value: str) -> set[str]:
    stop = {"the", "de", "del", "di", "la", "le", "group", "gruppo"}
    return {x for x in re.split(r"[^a-z0-9]+", value.casefold()) if len(x) > 1 and x not in stop}


def country_key(value: str) -> str:
    n = value.casefold().strip()
    return norm(COUNTRY_ALIASES.get(n, value))


def load_sofascore_catalog() -> list[Tournament]:
    data = get_json(f"{API}/config/unique-tournaments/EN/football")
    out = []
    for item in data.get("uniqueTournaments", []):
        category = item.get("category") or {}
        tid = item.get("id")
        if tid is None:
            continue
        out.append(Tournament(
            id=int(tid),
            name=str(item.get("name") or ""),
            slug=str(item.get("slug") or ""),
            country=str(category.get("name") or ""),
        ))
    if not out:
        raise RuntimeError("Catalogo SofaScore vuoto")
    return out


def score_name(source: str, target: str) -> float:
    a, b = norm(source), norm(target)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ratio = SequenceMatcher(None, a, b).ratio()
    aw, bw = words(source), words(target)
    overlap = len(aw & bw) / max(1, len(aw | bw))
    return max(ratio, overlap)


def discover(country: str, league: str, catalog: list[Tournament]):
    same_country = [t for t in catalog if country_key(t.country) == country_key(country)]
    ranked = sorted(
        ((score_name(league, t.name), t) for t in same_country),
        key=lambda x: (-x[0], x[1].id),
    )
    if not ranked:
        return "NOT_FOUND", None, "country_not_in_catalog"
    best_score, best = ranked[0]
    second_score = ranked[1][0] if len(ranked) > 1 else 0.0

    # Auto-accept solo match forte e chiaramente separato dal secondo.
    if best_score >= 0.82 and (best_score - second_score >= 0.08 or best_score == 1.0):
        return "FOUND", best, f"score={best_score:.3f}"
    if best_score >= 0.55:
        return "AMBIGUOUS", best, f"score={best_score:.3f};second={second_score:.3f}"
    return "NOT_FOUND", None, f"best_score={best_score:.3f};best={best.name}"


def main() -> None:
    parser = argparse.ArgumentParser(description="SofaScore catalog discovery per onboarding GioOver25.")
    parser.add_argument("--input", help="CSV onboarding; default ultimo in data/debug")
    parser.add_argument("--limit", type=int, default=0, help="Limita i READY; 0=tutti")
    parser.add_argument("--output", help="CSV output")
    args = parser.parse_args()

    source = ROOT / args.input if args.input else latest_onboarding()
    with source.open(encoding="utf-8-sig", newline="") as handle:
        rows = [r for r in csv.DictReader(handle, delimiter=";") if r.get("Status") == "READY"]
    if args.limit > 0:
        rows = rows[:args.limit]

    print("[SOFASCORE] Carico catalogo tornei...")
    try:
        catalog = load_sofascore_catalog()
    except Exception as exc:
        raise SystemExit(f"[SOFASCORE ERROR] {exc.__class__.__name__}: {exc}") from exc
    print(f"[SOFASCORE] {len(catalog)} tornei nel catalogo")

    output = ROOT / args.output if args.output else ROOT / "data" / "debug" / f"league_enrichment_{datetime.now():%Y%m%d-%H%M%S}.csv"
    output.parent.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}

    fields = list(rows[0].keys()) + [
        "SourceStatus", "SofaTournamentId", "SofaTournamentName",
        "SofaCountry", "SourceDetail"
    ] if rows else []

    with output.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";")
        if fields:
            writer.writeheader()
        for index, row in enumerate(rows, 1):
            status, hit, detail = discover(row["Country"], row["League"], catalog)
            counts[status] = counts.get(status, 0) + 1
            row.update({
                "SourceStatus": status,
                "SofaTournamentId": hit.id if hit else "",
                "SofaTournamentName": hit.name if hit else "",
                "SofaCountry": hit.country if hit else "",
                "SourceDetail": detail,
            })
            writer.writerow(row)
            extra = f" id={hit.id} name={hit.name}" if hit else ""
            print(f"[{index}/{len(rows)}] {row['Country']};{row['League']} -> {status}{extra}")

    print("[ENRICHMENT] " + " | ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"[ENRICHMENT] output={output}")
    print("[DRY-RUN] Nessuna modifica a league_registry.csv o agli storici.")


if __name__ == "__main__":
    main()
