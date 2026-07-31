from __future__ import annotations

import re
import unicodedata

# Alias espliciti, limitati al LeagueId per evitare collisioni tra campionati.
# Sia le chiavi sia i valori devono essere scritti nella forma già normalizzata
# da _basic_normalize().
TEAM_ALIASES: dict[str, dict[str, str]] = {
    "Finland_Kolmonen_Southern_Group2": {
        "tips vantaa": "tips",
        "puotinkylan valtti": "valtti",
    },
    "Finland_Kolmonen_Eastern_Group1": {
        "jyvaskylan seudun palloseura": "sapa",
        "fc blackbird": "fc jyvaskyla blackbird",
    },
    "Finland_Kolmonen_Eastern_Group3": {
        "mikkelin palloilijat 2": "mikkelin palloilijat ii",
        "kouvolan jalkapallo": "kjp",
    },
    "Finland_Kolmonen_Western_Group3": {
        "lapuan virkia": "virkia",
    },
    "Finland_Kolmonen_Eastern_Group2": {
        "kings sc": "kings",
    },
}


def _basic_normalize(value: object) -> str:
    """Normalizza grafia, maiuscole, accenti e separatori."""
    text = str(value or "").casefold().strip()
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[._/\\'’`-]+", " ", text)
    return " ".join(text.split())


def normalize_team_name(league_id: str, team_name: object) -> str:
    """Restituisce il nome canonico della squadra per la lega indicata."""
    normalized = _basic_normalize(team_name)
    aliases = TEAM_ALIASES.get(str(league_id or "").strip(), {})
    return aliases.get(normalized, normalized)
