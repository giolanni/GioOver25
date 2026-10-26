"""Catalogo dei provider per il backfill iniziale delle nuove leghe.

Il backfill e' separato dalla manutenzione giornaliera: dopo l'onboarding,
Diretta resta la sorgente operativa di fixture/risultati.

Questo modulo NON scrive registry o storici.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackfillSource:
    name: str
    structured: bool
    free: bool
    coverage: str
    enabled: bool = True


SOURCES = (
    BackfillSource(
        name="football-data.co.uk",
        structured=True,
        free=True,
        coverage="major_europe_plus_selected_world",
    ),
    BackfillSource(
        name="openfootball",
        structured=True,
        free=True,
        coverage="selected_leagues",
    ),
)


def source_order() -> tuple[BackfillSource, ...]:
    """Ordine dei provider automatici ammessi per il backfill."""
    return tuple(source for source in SOURCES if source.enabled)


def unresolved_status() -> str:
    """Stato esplicito: nessun provider automatico ha copertura verificata."""
    return "BACKFILL_REQUIRED"
