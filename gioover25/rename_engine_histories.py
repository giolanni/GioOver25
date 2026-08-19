"""
GioOver2.5 - migrazione nomenclatura engine sperimentali.

SCOPO
-----
Rinomina cartelle e file già prodotti usando la vecchia nomenclatura:

    v20dev   -> v20plus
    v201dev  -> v20select
    v202dev  -> v20def
    v22dev   -> v22def
    v25dev   -> v25def
    v26dev   -> v26def

La migrazione riguarda ESPLICITAMENTE:

    data/output_ranking/
    data/storico/ranking/

Vengono rinominati:
- le cartelle engine;
- tutti i file contenuti, anche negli archivi old_ranking;
- qualsiasi nome file che contenga il vecchio identificatore engine.

Esempi:

    data/output_ranking/v20dev/
        -> data/output_ranking/v20plus/

    ranking_2026_08_19_v20dev.csv
        -> ranking_2026_08_19_v20plus.csv

    data/storico/ranking/v201dev/storico_ranking_v201dev.csv
        -> data/storico/ranking/v20select/storico_ranking_v20select.csv

IMPORTANTE
----------
I due nuovi engine v20defselect e v20defplus non hanno uno storico precedente,
quindi le rispettive cartelle nasceranno alla prima esecuzione.

USO
---
Dry-run:
    python -m gioover25.rename_engine_histories

Applicazione:
    python -m gioover25.rename_engine_histories --apply

Il dry-run non modifica nulla e stampa tutte le operazioni previste.
In presenza di una collisione (destinazione già esistente), lo script NON
sovrascrive: segnala il conflitto e richiede una verifica manuale.
"""

from __future__ import annotations

import argparse
from pathlib import Path


RENAME_MAP = {
    "v20dev": "v20plus",
    "v201dev": "v20select",
    "v202dev": "v20def",
    "v22dev": "v22def",
    "v25dev": "v25def",
    "v26dev": "v26def",
}

ROOTS = (
    Path("data/output_ranking"),
    Path("data/storico/ranking"),
)


def _replace_tokens(name: str) -> str:
    result = name

    # Ordine per lunghezza: evita che identificatori simili possano
    # interferire tra loro durante la sostituzione.
    for old, new in sorted(
        RENAME_MAP.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        result = result.replace(old, new)

    return result


def _collect_operations() -> list[tuple[Path, Path]]:
    operations = []

    for root in ROOTS:
        if not root.exists():
            continue

        # Prima i file e le sottocartelle più profonde. In questo modo il
        # rename di una directory padre avviene soltanto dopo i suoi contenuti.
        paths = sorted(
            root.rglob("*"),
            key=lambda path: len(path.parts),
            reverse=True,
        )

        for source in paths:
            new_name = _replace_tokens(
                source.name
            )

            if new_name == source.name:
                continue

            destination = source.with_name(
                new_name
            )

            operations.append(
                (source, destination)
            )

        # rglob non include la root stessa: gestiamo quindi esplicitamente
        # le directory engine direttamente sotto ciascuna root.
        for old, new in RENAME_MAP.items():
            source = root / old
            destination = root / new

            if source.exists() and (
                source,
                destination,
            ) not in operations:
                operations.append(
                    (source, destination)
                )

    return operations


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Rinomina output ranking e storici ranking secondo la nuova "
            "nomenclatura funzionale degli engine."
        )
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Applica realmente i rename. Senza flag esegue solo dry-run.",
    )

    args = parser.parse_args()
    operations = _collect_operations()

    if not operations:
        print(
            "Nessun file/cartella con la vecchia nomenclatura trovato."
        )
        return

    conflicts = []

    for source, destination in operations:
        # Una destination può risultare già presente perché è ancora una
        # source che verrà rinominata più avanti. Quello non è un conflitto.
        future_sources = {
            item[0]
            for item in operations
        }

        if destination.exists() and destination not in future_sources:
            conflicts.append(
                (source, destination)
            )

    print(
        f"Modalità: {'APPLY' if args.apply else 'DRY-RUN'}"
    )
    print(
        f"Operazioni previste: {len(operations)}"
    )
    print()

    for source, destination in operations:
        print(
            f"{source} -> {destination}"
        )

    if conflicts:
        print()
        print(
            "[ERRORE] Collisioni rilevate. Nessuna modifica applicata:"
        )

        for source, destination in conflicts:
            print(
                f"  {source} -> {destination} (DESTINAZIONE ESISTENTE)"
            )

        raise SystemExit(2)

    if not args.apply:
        print()
        print(
            "Dry-run completato. Se l'elenco è corretto, rilancia con --apply."
        )
        return

    renamed = 0

    for source, destination in operations:
        if not source.exists():
            # Può accadere quando una directory padre è stata già rinominata
            # come effetto di un'operazione precedente. In tal caso la sua
            # operazione esplicita non è più necessaria.
            continue

        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        source.rename(
            destination
        )
        renamed += 1

    print()
    print(
        f"Migrazione completata. Rename eseguiti: {renamed}"
    )
    print()
    print(
        "Nuova nomenclatura attiva:"
    )

    for old, new in RENAME_MAP.items():
        print(
            f"  {old} -> {new}"
        )


if __name__ == "__main__":
    main()
