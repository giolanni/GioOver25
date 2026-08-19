from __future__ import annotations

import re
import unicodedata

# Alias espliciti, limitati al LeagueId per evitare collisioni tra campionati.
# Sia le chiavi sia i valori devono essere scritti nella forma già normalizzata
# da _basic_normalize().
TEAM_ALIASES: dict[str, dict[str, str]] = {
    "Finland_Kolmonen_Southern_Group1": {
        # SofaScore usa anche la denominazione societaria "SexyPöxyt".
        # Nel progetto la forma canonica di questa squadra è "Pöxyt".
        "sexypoxyt": "poxyt",
    },
    "Finland_Kolmonen_Southern_Group2": {
        "tips vantaa": "tips",
        "puotinkylan valtti": "valtti",
    },
    "Finland_Kolmonen_Eastern_Group1": {
        "jyvaskylan seudun palloseura": "sapa",
        "fc blackbird": "fc jyvaskyla blackbird",
    },
    "Finland_Kolmonen_Eastern_Group3": {
        "kouvolan jalkapallo": "kjp",
    },
    "Finland_Kolmonen_Western_Group3": {
        "lapuan virkia": "virkia",
    },
    "Finland_Kolmonen_Eastern_Group2": {
        "kings sc": "kings",
    },
    "Finland_Kolmonen_North": {
        # SofaScore usa in vari punti i nomi societari estesi, mentre nei
        # risultati/classifica del girone mostra le forme brevi sottostanti.
        # Senza questi alias la stessa squadra può essere conteggiata due volte.
        "kajaanin haka": "kajha",
        "kajaanin palloilijat": "kapa",
        "kemin palloseura": "keps",
        "rollon pojat": "ropo",
        "fc santa claus": "santa claus",
    },
}


def canonicalize_team_display_name(value: object) -> str:
    """Restituisce il nome squadra nella forma canonica persistibile.

    Regole globali GioOver2.5:
    - il suffisso finale ``II`` (o il carattere unicode ``Ⅱ``) viene sempre
      convertito in ``2``;
    - ``EPS/Reservi`` viene persistito come ``EPS Reservi``;
    - ``SexyPöxyt`` viene persistito come ``Pöxyt``;
    - le sostituzioni avvengono solo su nomi completi noti o sul token finale II.

    Esempi:
        New York Red Bulls II -> New York Red Bulls 2
        Sporting Kansas City Ⅱ -> Sporting Kansas City 2
        EPS/Reservi -> EPS Reservi
        SexyPöxyt -> Pöxyt
        Zimbru 2 -> Zimbru 2
    """

    text = " ".join(str(value or "").strip().split())

    if not text:
        return text

    exact_aliases = {
        "eps/reservi": "EPS Reservi",
        "sexypöxyt": "Pöxyt",
        "sexypoxyt": "Pöxyt",
    }

    exact = exact_aliases.get(text.casefold())

    if exact is not None:
        return exact

    return re.sub(
        r"(?i)\s+(?:II|Ⅱ)$",
        " 2",
        text,
    )


def _basic_normalize(value: object) -> str:
    """Normalizza grafia, maiuscole, accenti e separatori."""
    text = canonicalize_team_display_name(value).casefold().strip()
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[._/\\'’`-]+", " ", text)
    return " ".join(text.split())


def normalize_team_name(league_id: str, team_name: object) -> str:
    """Restituisce il nome canonico della squadra per la lega indicata."""
    normalized = _basic_normalize(team_name)
    aliases = TEAM_ALIASES.get(str(league_id or "").strip(), {})
    return aliases.get(normalized, normalized)
