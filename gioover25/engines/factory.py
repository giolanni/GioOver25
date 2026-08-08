"""
GioOver2.5 - engines/factory.py

Gli engine sperimentali sono selezionabili esplicitamente ma separati
dagli engine ufficiali usati da --engine all.
"""

from . import (
    v13,
    v20,
    v20dev,
    v201dev,
    v21,
    v21dev,
    v22,
    v23,
    v24,
    v25,
    v251,
    v26,
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
