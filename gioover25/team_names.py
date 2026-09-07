from __future__ import annotations

import csv
import re
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


TEAM_NAME_DICTIONARY = (
    Path(__file__).resolve().parents[1] / "data" / "team_name_dictionary.csv"
)


@dataclass(frozen=True)
class TeamNameEntry:
    canonical_name: str
    real_name: str


def _global_canonicalize(value: object) -> str:
    """Applica soltanto le convenzioni valide per tutte le leghe."""
    text = " ".join(str(value or "").strip().split())
    if not text:
        return text

    # Convenzione globale GioOver2.5: il suffisso finale II/Ⅱ diventa 2.
    return re.sub(r"(?i)\s+(?:II|Ⅱ)$", " 2", text)


def _basic_normalize(value: object) -> str:
    """Normalizza grafia, maiuscole, accenti e separatori per il confronto."""
    text = _global_canonicalize(value).casefold().strip()
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[._/\\'’`-]+", " ", text)
    return " ".join(text.split())


@lru_cache(maxsize=1)
def _load_team_name_dictionary() -> dict[str, dict[str, TeamNameEntry]]:
    """Carica il dizionario unico alias -> nome canonico per LeagueId."""
    entries: dict[str, dict[str, TeamNameEntry]] = {}

    if not TEAM_NAME_DICTIONARY.exists():
        return entries

    with TEAM_NAME_DICTIONARY.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        required = {"LeagueId", "CanonicalName", "RealName", "Aliases"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                "team_name_dictionary.csv non valido. Mancano le colonne: "
                + ", ".join(sorted(missing))
            )

        for line_number, row in enumerate(reader, start=2):
            league_id = str(row.get("LeagueId", "")).strip()
            canonical_name = _global_canonicalize(row.get("CanonicalName", ""))
            real_name = " ".join(str(row.get("RealName", "")).strip().split())

            if not league_id or not canonical_name:
                raise ValueError(
                    "team_name_dictionary.csv non valido alla riga "
                    f"{line_number}: LeagueId e CanonicalName sono obbligatori"
                )

            entry = TeamNameEntry(
                canonical_name=canonical_name,
                real_name=real_name or canonical_name,
            )
            league_entries = entries.setdefault(league_id, {})
            names = [canonical_name, real_name]
            names.extend(str(row.get("Aliases", "")).split("|"))

            for name in names:
                key = _basic_normalize(name)
                if not key:
                    continue

                previous = league_entries.get(key)
                if previous is not None and previous != entry:
                    raise ValueError(
                        "Alias squadra ambiguo in team_name_dictionary.csv "
                        f"alla riga {line_number}: {name!r}"
                    )
                league_entries[key] = entry

    return entries


def canonicalize_team_display_name(
    value: object,
    league_id: str | None = None,
) -> str:
    """Restituisce il nome canonico da mostrare e persistere.

    Il dizionario è specifico per lega, evitando collisioni tra squadre con
    nomi simili. Senza una voce nel dizionario restano attive soltanto le
    regole globali, come la conversione del suffisso ``II`` in ``2``.
    """
    text = _global_canonicalize(value)
    if not text or not league_id:
        return text

    entry = _load_team_name_dictionary().get(str(league_id).strip(), {}).get(
        _basic_normalize(text)
    )
    return entry.canonical_name if entry is not None else text


def get_real_team_name(league_id: str, team_name: object) -> str:
    """Restituisce il nome reale/esteso registrato nel dizionario."""
    text = _global_canonicalize(team_name)
    entry = _load_team_name_dictionary().get(str(league_id).strip(), {}).get(
        _basic_normalize(text)
    )
    return entry.real_name if entry is not None else text


def normalize_team_name(league_id: str, team_name: object) -> str:
    """Restituisce il token interno di confronto della squadra."""
    canonical_name = canonicalize_team_display_name(team_name, league_id)
    return _basic_normalize(canonical_name)
