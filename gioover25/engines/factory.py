from . import v13, v20


ENGINES = {
    "v13": v13,
    "v20": v20,
}


def get_engine(name: str):
    key = name.strip().lower()

    if key not in ENGINES:
        raise ValueError(
            f"Motore non supportato: {name}. "
            f"Motori disponibili: {', '.join(sorted(ENGINES.keys()))}"
        )

    return ENGINES[key]