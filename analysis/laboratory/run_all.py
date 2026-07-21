"""
===============================================================================
GioOver2.5 - analysis/laboratory/run_all.py
===============================================================================

SCOPO
-----
Esegue l'intera pipeline ufficiale del Laboratory.

La diagnostica delle FASCIA ALTA KO non è un'attività manuale o episodica:
viene rigenerata automaticamente dopo gli altri report ogni volta che viene
eseguito questo modulo.

USO
---
    python -m analysis.laboratory.run_all
===============================================================================
"""

# Costruisce i dataset 01_matches e 02_drivers.
from .build_laboratory import main as build_laboratory

# Costruisce le distribuzioni dei driver.
from .distributions import main as build_distributions

# Costruisce le regole candidate.
from .candidate_rules import main as build_candidate_rules

# Costruisce i report avanzati di potere, curve, coppie, triple e correlazioni.
from .driver_analysis import main as build_driver_analysis

# Costruisce automaticamente autopsia, pattern e andamento della FASCIA ALTA.
from .high_ko_autopsy import main as build_high_ko_autopsy


def main() -> int:
    """Esegue in ordine tutte le fasi del Laboratory."""

    print("=== BUILD LABORATORY ===")
    build_laboratory()

    print("\n=== DISTRIBUTIONS ===")
    build_distributions()

    print("\n=== CANDIDATE RULES ===")
    build_candidate_rules()

    print("\n=== DRIVER ANALYSIS ===")
    build_driver_analysis()

    print("\n=== HIGH KO AUTOPSY ===")
    build_high_ko_autopsy()

    print("\nLaboratorio aggiornato.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
