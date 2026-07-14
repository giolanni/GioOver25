"""
===============================================================================
GioOver2.5 - Configurazione analisi metriche v3
===============================================================================

SCOPO
-----
Centralizzare le soglie usate per analizzare i driver ex ante realmente
presenti nei file ranking v25.

FILE LETTI / SCRITTI
--------------------
Nessuno.

LOGICA
------
Le soglie sono esplorative. Servono a cercare ricorrenze nei gruppi:
ALTA+OK, ALTA+KO, MEDIA+OK, MEDIA+KO.

LIMITAZIONI
-----------
Le soglie non rappresentano regole già validate.
===============================================================================
"""

from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class AnalysisConfig:
    high_band_labels: Tuple[str, ...] = ("ALTA", "HIGH")
    medium_band_labels: Tuple[str, ...] = ("MEDIA", "MEDIUM")
    ok_labels: Tuple[str, ...] = ("OK", "OVER", "OVER25", "OVER_25")
    ko_labels: Tuple[str, ...] = ("KO", "UNDER", "UNDER25", "UNDER_25")

    min_occurrences_simple: int = 20
    min_occurrences_pair: int = 30
    min_media_ok_precision: float = 0.80
    min_alta_ko_capture: float = 0.10
    max_pair_metrics: int = 35

    score_thresholds: Tuple[float, ...] = (60, 65, 70, 75, 80, 85, 90)
    ranking_gap_thresholds: Tuple[float, ...] = (0.5, 1, 2, 3, 4, 5, 6)
    attack_thresholds: Tuple[float, ...] = (4, 6, 8, 10, 11, 12, 13)
    defense_thresholds: Tuple[float, ...] = (2, 4, 6, 8, 9, 10)
    last10_thresholds: Tuple[float, ...] = (4, 6, 7.2, 8.4, 9.6, 10.8)
    venue_thresholds: Tuple[float, ...] = (4, 5, 6, 7, 8, 9, 10)
    btts_thresholds: Tuple[float, ...] = (5, 6, 7, 8, 9)
