"""
Esegue l'intero laboratorio.

Uso:
    python -m analysis.laboratory.run_all
"""

from .build_laboratory import main as build_laboratory
from .distributions import main as build_distributions
from .candidate_rules import main as build_candidate_rules


def main() -> int:
    print("=== BUILD LABORATORY ===")
    build_laboratory()

    print("\n=== DISTRIBUTIONS ===")
    build_distributions()

    print("\n=== CANDIDATE RULES ===")
    build_candidate_rules()

    print("\nLaboratorio aggiornato.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())