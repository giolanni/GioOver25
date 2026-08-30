"""Provider xG esterni.

Understat è la fonte primaria gratuita per i principali campionati europei.
Big Balls Sports Data è un provider REST opzionale che richiede BBS_API_KEY.
"""

from .understat import UnderstatProvider
from .bigballs import BigBallsProvider

__all__ = ["UnderstatProvider", "BigBallsProvider"]
