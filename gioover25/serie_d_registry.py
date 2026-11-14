"""Verified Serie D 2026/27 competition labels and public source pages.

This registry deliberately does not invent Flashscore feed IDs. Integrators
must resolve each provider competition ID before enabling automatic ingestion.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SerieDGroup:
    league_id: str
    group: str
    source_title: str
    source_url: str


SERIE_D_GROUPS = {
    letter: SerieDGroup(
        league_id=f"Italy_SerieD_Girone{letter}",
        group=letter,
        source_title=f"Serie D - Girone {letter}",
        source_url=f"https://www.diretta.it/calcio/italia/serie-d-girone-{letter.lower()}/risultati/",
    )
    for letter in "ABCDEFGHI"
}


def league_id_for_title(title: str) -> str | None:
    """Resolve a *complete* Serie D group title; never guess from 'Serie D'."""
    import re
    normalized = " ".join(str(title).strip().casefold().split())
    match = re.fullmatch(r"(?:italia\s*[:/-]\s*)?serie\s*d\s*[-–]?\s*girone\s*([a-i])", normalized)
    if not match:
        return None
    return SERIE_D_GROUPS[match.group(1).upper()].league_id


def validate_registry(registry_path):
    """Return missing Serie D IDs without modifying any data."""
    import csv
    from pathlib import Path
    with Path(registry_path).open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh, delimiter=";"))
    present = {row["LeagueId"] for row in rows}
    return [item.league_id for item in SERIE_D_GROUPS.values() if item.league_id not in present]
