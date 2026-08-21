"""
GioOver2.5 - engines/factory.py

NAMING DEGLI ENGINE SPERIMENTALI
--------------------------------
La nomenclatura funzionale sostituisce la vecchia sequenza v20dev/v201dev/
v202dev, che non descriveva più correttamente il ruolo degli engine.

Suffissi:
    plus    = engine base + selezioni promosse
    select  = solo sottoinsieme selezionato
    def     = variante con penalità strong-defense

Famiglia v20 originale:
    v20
    v20select
    v20plus

Famiglia v20 strong-defense:
    v20def
    v20defselect
    v20defplus
    v20defplus_v2
    v20defplus_v3

Altre varianti strong-defense:
    v22def
    v25def
    v26def
"""

from . import (
    v13,
    v20,
    v20plus,
    v20select,
    v20def,
    v20defselect,
    v20defplus,
    v20defplus_v2,
    v20defplus_v3,
    v21,
    v21dev,
    v22,
    v22def,
    v23,
    v24,
    v25,
    v25def,
    v251,
    v26,
    v26def,
)

OFFICIAL_ENGINES = {
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

EXPERIMENTAL_ENGINES = {
    "v20plus": v20plus,
    "v20select": v20select,
    "v20def": v20def,
    "v20defselect": v20defselect,
    "v20defplus": v20defplus,
    "v20defplus_v2": v20defplus_v2,
    "v20defplus_v3": v20defplus_v3,
    "v22def": v22def,
    "v25def": v25def,
    "v26def": v26def,
}

ENGINES = {
    **OFFICIAL_ENGINES,
    **EXPERIMENTAL_ENGINES,
}


def get_engine(name: str):
    key = name.strip().lower()

    if key not in ENGINES:
        raise ValueError(
            f"Motore non supportato: {name}. "
            f"Motori disponibili: {', '.join(sorted(ENGINES.keys()))}"
        )

    return ENGINES[key]


def get_available_engines() -> list[str]:
    return sorted(ENGINES.keys())


def get_official_engines() -> list[str]:
    return sorted(OFFICIAL_ENGINES.keys())


def get_experimental_engines() -> list[str]:
    return sorted(EXPERIMENTAL_ENGINES.keys())
