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


@dataclass(frozen=True)
class TeamNameDictionary:
    exact: dict[str, dict[str, TeamNameEntry]]
    normalized: dict[str, dict[str, TeamNameEntry]]


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
def _load_team_name_dictionary() -> TeamNameDictionary:
    """Carica gli alias esatti e quelli normalizzati per ciascun LeagueId.

    Il lookup esatto serve per i rari nomi distinti solo dalle maiuscole, come
    ``SAPA`` e ``SaPa`` nello stesso girone di Kolmonen. Se una chiave
    normalizzata e case-insensitive e' ambigua, non viene usata come fallback.
    """
    exact_entries: dict[str, dict[str, TeamNameEntry]] = {}
    normalized_entries: dict[str, dict[str, TeamNameEntry]] = {}
    ambiguous_normalized: dict[str, set[str]] = {}

    if not TEAM_NAME_DICTIONARY.exists():
        return TeamNameDictionary(exact={}, normalized={})

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
            league_exact = exact_entries.setdefault(league_id, {})
            league_normalized = normalized_entries.setdefault(league_id, {})
            league_ambiguous = ambiguous_normalized.setdefault(league_id, set())
            names = [canonical_name, real_name]
            names.extend(str(row.get("Aliases", "")).split("|"))

            for name in names:
                exact_key = _global_canonicalize(name)
                if not exact_key:
                    continue

                previous = league_exact.get(exact_key)
                if previous is not None and previous != entry:
                    raise ValueError(
                        "Alias squadra esatto ambiguo in team_name_dictionary.csv "
                        f"alla riga {line_number}: {name!r}"
                    )
                league_exact[exact_key] = entry

                normalized_key = _basic_normalize(exact_key)
                if normalized_key in league_ambiguous:
                    continue

                previous = league_normalized.get(normalized_key)
                if previous is not None and previous != entry:
                    # Non possiamo distinguere in modo case-insensitive, ma il
                    # lookup esatto resta sicuro e separa correttamente i club.
                    league_normalized.pop(normalized_key, None)
                    league_ambiguous.add(normalized_key)
                    continue

                league_normalized[normalized_key] = entry

    return TeamNameDictionary(
        exact=exact_entries,
        normalized=normalized_entries,
    )


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

    dictionary = _load_team_name_dictionary()
    league_key = str(league_id).strip()
    entry = dictionary.exact.get(league_key, {}).get(text)
    if entry is None:
        entry = dictionary.normalized.get(league_key, {}).get(
            _basic_normalize(text)
        )
    return entry.canonical_name if entry is not None else text


def get_real_team_name(league_id: str, team_name: object) -> str:
    """Restituisce il nome reale/esteso registrato nel dizionario."""
    text = _global_canonicalize(team_name)
    dictionary = _load_team_name_dictionary()
    league_key = str(league_id).strip()
    entry = dictionary.exact.get(league_key, {}).get(text)
    if entry is None:
        entry = dictionary.normalized.get(league_key, {}).get(
            _basic_normalize(text)
        )
    return entry.real_name if entry is not None else text


def normalize_team_name(league_id: str, team_name: object) -> str:
    """Restituisce il token interno di confronto della squadra."""
    canonical_name = canonicalize_team_display_name(team_name, league_id)
    return _basic_normalize(canonical_name)
