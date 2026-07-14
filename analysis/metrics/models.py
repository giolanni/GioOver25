"""
===============================================================================
GioOver2.5 - Modelli dati del framework di analisi
===============================================================================

SCOPO
-----
Definire strutture dati semplici e tipizzate per rappresentare:
- una metrica candidata;
- il risultato statistico della sua valutazione.

FILE LETTI / SCRITTI
--------------------
Nessuno.

LOGICA
------
MetricDefinition contiene una funzione booleana applicata a una riga arricchita
di feature. MetricEvaluation contiene conteggi e indicatori calcolati.

LIMITAZIONI
-----------
I modelli non stabiliscono se una metrica debba entrare in un engine. Forniscono
solo dati quantitativi utili alla successiva valutazione.
===============================================================================
"""

from dataclasses import dataclass
from typing import Callable, Dict, Any


Predicate = Callable[[Dict[str, Any]], bool]


@dataclass(frozen=True)
class MetricDefinition:
    name: str
    family: str
    description: str
    predicate: Predicate


@dataclass
class MetricEvaluation:
    metric_name: str
    family: str
    description: str
    occurrences: int
    alta_ok: int
    alta_ko: int
    media_ok: int
    media_ko: int
    other: int
    over_total: int
    under_total: int
    over_precision: float
    coverage: float
    alta_ko_capture: float
    alta_ok_capture: float
    media_ok_capture: float
    media_ko_capture: float
    alta_ko_lift: float
    media_ok_precision: float
    media_ok_lift: float
    exclusion_efficiency: float
    promotion_efficiency: float
