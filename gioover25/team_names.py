from __future__ import annotations

import re
import unicodedata

# Alias espliciti, limitati al LeagueId per evitare collisioni tra campionati.
# Sia le chiavi sia i valori devono essere scritti nella forma già normalizzata
# da _basic_normalize().
TEAM_ALIASES: dict[str, dict[str, str]] = {
    "Finland_Kolmonen_Southern_Group1": {
        "sexypoxyt": "poxyt",
    },
    "Finland_Kolmonen_Southern_Group2": {
        "tips vantaa": "tips",
        "puotinkylan valtti": "valtti",
        "fc kontu": "kontu",
        "lps helsinki": "laajasalon palloseura",
        "vjs vantaa b": "vjs 2",
    },
    "Finland_Kolmonen_Southern_Group3": {
        "riihimaen palloseura": "rips",
        "fc futura": "futura",
        "atlantis fc akatemia": "atlantis 2",
        "atlantis ii": "atlantis 2",
        "tips u21": "tips 2 u21",
        "tuusulan palloseura": "tups",
        "fc lahti 69": "lahti 69",
    },
    "Finland_Kolmonen_Eastern_Group1": {
        "jyvaskylan seudun palloseura": "sapa",
        "fc blackbird": "fc jyvaskyla blackbird",
    },
    "Finland_Kolmonen_Eastern_Group3": {
        "kouvolan jalkapallo": "kjp",
    },
    "Finland_Kolmonen_Western_Group1": {
        "piikkion palloseura": "pips",
        "ifk mariehamn 2": "ifk 2",
        "maskun palloseura": "maps",
        "jyrkkalan tykit": "jyty",
        "littoisten tyovaen urheilijat u20": "ltu u20",
        "pargas if": "pif",
        "kaarinan pojat": "kaapo",
        "abo cf": "acf",
    },
    "Finland_Kolmonen_Western_Group2": {
        "nokian palloseura": "nops",
        "tampere united 2": "tampere utd 2",
        "ylojarvi united fc": "ylojarvi utd",
        "tampereen peli toverit": "tp t",
        "leki futis": "fc leki",
        "saaksjarven loiske": "saaksjarven loiske",
        "fc haka juniors": "fc haka j",
        "lasten": "fc lasten",
    },
    "Finland_Kolmonen_Western_Group3": {
        "lapuan virkia": "virkia",
        "fc kiisto": "kiisto",
        "kiisto vaasa": "kiisto",
        "vaasa ifk": "vifk",
        "vaasan pallo veikot": "vpv",
        "vpv pallo veikot": "vpv",
        "sif": "sundom if",
        "sporting kristina": "sp kristina",
        "ypa ylivieska": "fc ylivieska",
        "sjk j apollo": "sjk j",
    },
    "Finland_Kolmonen_Eastern_Group2": {
        "kings sc": "kings",
    },
    "Finland_Kolmonen_North": {
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

    return re.sub(r"(?i)\s+(?:II|Ⅱ)$", " 2", text)


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
