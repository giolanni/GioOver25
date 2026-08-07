"""
===============================================================================
GioOver2.5 - engines/factory.py
===============================================================================

Registro centralizzato degli engine disponibili.

Registro degli engine disponibili, incluso il nuovo `v26`.
===============================================================================
"""

from . import v13, v20, v21, v21dev, v22, v23, v24, v25, v251, v26


ENGINES = {
    "v13": v13,
    "v20": v20,
    "v21": v21,
    "v21dev": v21dev,
    "v22": v22,
    "v23": v23,
    "v24": v24,
    "v25": v25,
    "v251": v251,
    "v26": v26,
}



def get_engine(name: str):
    """Restituisce il modulo dell'engine richiesto oppure solleva un errore."""

    key = name.strip().lower()

    if key not in ENGINES:
        raise ValueError(
            f"Motore non supportato: {name}. "
            f"Motori disponibili: {', '.join(sorted(ENGINES.keys()))}"
        )

    return ENGINES[key]



def get_available_engines() -> list[str]:
    """Restituisce l'elenco alfabetico degli engine registrati."""

    return sorted(ENGINES.keys())
