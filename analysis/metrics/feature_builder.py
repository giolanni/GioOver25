"""
===============================================================================
GioOver2.5 - Feature derivate dai driver ex ante v25
===============================================================================

SCOPO
-----
Calcolare indicatori derivati esclusivamente dai driver presenti nei ranking
originali v25.

DRIVER UTILIZZATI
-----------------
Score, RankingGapScore, HomeAttackScore, AwayAttackScore,
HomeDefenseWeaknessScore, AwayDefenseWeaknessScore,
HomeLast10OverScore, AwayLast10OverScore,
HomeVenueOverScore, AwayVenueOverScore, BTTSProfileScore.

FILE LETTI / SCRITTI
--------------------
Nessuno direttamente.

LOGICA
------
Per ogni coppia home/away vengono calcolati minimo, massimo, somma e squilibrio.
Vengono inoltre estratti flag testuali dal campo Reason.

LIMITAZIONI
-----------
Le statistiche grezze non sono ricostruibili da questi score. Quando il bug
degli storici sarà corretto, il framework potrà essere esteso ai dati originali.
===============================================================================
"""

from typing import Dict, Any, Iterable, List, Optional
from datetime import datetime


def to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _norm(value: Any) -> str:
    return str(value or "").strip().upper()


def _year_month(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(text[:10], fmt).strftime("%Y-%m")
        except ValueError:
            pass
    return text[:7] if len(text) >= 7 else text


def _pair_features(a: Optional[float], b: Optional[float]):
    vals = [v for v in (a, b) if v is not None]
    if len(vals) != 2:
        return None, None, None, None
    return min(vals), max(vals), a + b, abs(a - b)


def enrich_record(row: Dict[str, Any]) -> Dict[str, Any]:
    r = dict(row)

    fields = (
        "Score", "RankingGapScore",
        "HomeAttackScore", "AwayAttackScore",
        "HomeDefenseWeaknessScore", "AwayDefenseWeaknessScore",
        "HomeLast10OverScore", "AwayLast10OverScore",
        "HomeVenueOverScore", "AwayVenueOverScore",
        "BTTSProfileScore",
    )
    for field in fields:
        r[field] = to_float(r.get(field))

    attack_min, attack_max, attack_sum, attack_gap = _pair_features(
        r.get("HomeAttackScore"), r.get("AwayAttackScore")
    )
    defense_min, defense_max, defense_sum, defense_gap = _pair_features(
        r.get("HomeDefenseWeaknessScore"), r.get("AwayDefenseWeaknessScore")
    )
    last10_min, last10_max, last10_sum, last10_gap = _pair_features(
        r.get("HomeLast10OverScore"), r.get("AwayLast10OverScore")
    )
    venue_min, venue_max, venue_sum, venue_gap = _pair_features(
        r.get("HomeVenueOverScore"), r.get("AwayVenueOverScore")
    )

    reason = str(r.get("Reason", "") or "")
    reason_norm = reason.lower()

    r.update({
        "BandNorm": _norm(r.get("Band")),
        "OutcomeNorm": _norm(r.get("Outcome")),
        "AnalysisMonth": _year_month(r.get("MatchDate") or r.get("PredictionDate")),
        "AttackMin": attack_min,
        "AttackMax": attack_max,
        "AttackSum": attack_sum,
        "AttackGap": attack_gap,
        "DefenseMin": defense_min,
        "DefenseMax": defense_max,
        "DefenseSum": defense_sum,
        "DefenseGap": defense_gap,
        "Last10Min": last10_min,
        "Last10Max": last10_max,
        "Last10Sum": last10_sum,
        "Last10Gap": last10_gap,
        "VenueMin": venue_min,
        "VenueMax": venue_max,
        "VenueSum": venue_sum,
        "VenueGap": venue_gap,
        "ReasonWeakAwayAttack": "ospite poco prolifico" in reason_norm,
        "ReasonHomeAttackNotDominant": "attacco casa non dominante" in reason_norm,
        "ReasonLowBTTS": "btts basso" in reason_norm,
        "ReasonWeakHomeVenue": "profilo over interno debole" in reason_norm,
        "ReasonWeakAwayVenue": "profilo over esterno debole" in reason_norm,
        "ReasonWeakHomeTrend": "trend over casa non forte" in reason_norm,
        "ReasonWeakAwayTrend": "trend over trasferta non forte" in reason_norm,
        "ReasonWeakGAWarning": "sopravvalutazione weak_ga" in reason_norm,
        "ReasonV25Penalty": "contro v25" in reason_norm or "v25:" in reason_norm,
    })
    return r


def enrich_records(rows: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [enrich_record(row) for row in rows]
