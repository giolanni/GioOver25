"""
Esegue costruzione laboratorio e distribuzioni.

Uso:
    python -m analysis.laboratory.run_all
"""

from .build_laboratory import main as build_laboratory
from .distributions import main as build_distributions


def main() -> int:
    build_laboratory()
    build_distributions()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
