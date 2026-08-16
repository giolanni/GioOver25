"""
GioOver2.5 - engines/factory.py

Engine ufficiali e sperimentali.
I nuovi strong-defense DEV sono congelati dal 16/08/2026.
"""

from . import (
    v13,
    v20,
    v20dev,
    v201dev,
    v202dev,
    v21,
    v21dev,
    v22,
    v22dev,
    v23,
    v24,
    v25,
    v25dev,
    v251,
    v26,
    v26dev,
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
    "v20dev": v20dev,
    "v201dev": v201dev,
    "v202dev": v202dev,
    "v22dev": v22dev,
    "v25dev": v25dev,
    "v26dev": v26dev,
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
