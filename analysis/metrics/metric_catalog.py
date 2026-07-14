"""
===============================================================================
GioOver2.5 - Catalogo metriche sui driver reali v25
===============================================================================

SCOPO
-----
Generare metriche basate sui driver ex ante realmente presenti nei ranking.

FILE LETTI / SCRITTI
--------------------
Nessuno direttamente.

LOGICA
------
Vengono create soglie sui driver singoli e sulle feature di coppia
(minimo, massimo, somma, squilibrio), oltre a flag derivati da Reason.

LIMITAZIONI
-----------
Le metriche descrivono ricorrenze storiche e non sono regole automatiche.
===============================================================================
"""

from typing import Any, List
from .config import AnalysisConfig
from .models import MetricDefinition


def _num(value: Any) -> bool:
    return isinstance(value, (int, float))


def _le(field, threshold):
    return lambda r: _num(r.get(field)) and r[field] <= threshold


def _ge(field, threshold):
    return lambda r: _num(r.get(field)) and r[field] >= threshold


def build_metric_catalog(config: AnalysisConfig) -> List[MetricDefinition]:
    metrics = []

    def add(name, family, description, predicate):
        metrics.append(MetricDefinition(name, family, description, predicate))

    for t in config.score_thresholds:
        add(f"score_ge_{t:g}", "score", f"Score >= {t:g}", _ge("Score", t))
        add(f"score_le_{t:g}", "score", f"Score <= {t:g}", _le("Score", t))

    for t in config.ranking_gap_thresholds:
        add(f"ranking_gap_score_ge_{t:g}", "ranking_gap",
            f"RankingGapScore >= {t:g}", _ge("RankingGapScore", t))
        add(f"ranking_gap_score_le_{t:g}", "ranking_gap",
            f"RankingGapScore <= {t:g}", _le("RankingGapScore", t))

    for field, label in (
        ("HomeAttackScore", "home_attack"),
        ("AwayAttackScore", "away_attack"),
        ("AttackMin", "attack_min"),
        ("AttackMax", "attack_max"),
        ("AttackSum", "attack_sum"),
        ("AttackGap", "attack_gap"),
    ):
        for t in config.attack_thresholds:
            add(f"{label}_ge_{t:g}", "attacco", f"{label} >= {t:g}", _ge(field, t))
            add(f"{label}_le_{t:g}", "attacco", f"{label} <= {t:g}", _le(field, t))

    for field, label in (
        ("HomeDefenseWeaknessScore", "home_defense_weakness"),
        ("AwayDefenseWeaknessScore", "away_defense_weakness"),
        ("DefenseMin", "defense_min"),
        ("DefenseMax", "defense_max"),
        ("DefenseSum", "defense_sum"),
        ("DefenseGap", "defense_gap"),
    ):
        for t in config.defense_thresholds:
            add(f"{label}_ge_{t:g}", "difesa", f"{label} >= {t:g}", _ge(field, t))
            add(f"{label}_le_{t:g}", "difesa", f"{label} <= {t:g}", _le(field, t))

    for field, label in (
        ("HomeLast10OverScore", "home_last10"),
        ("AwayLast10OverScore", "away_last10"),
        ("Last10Min", "last10_min"),
        ("Last10Max", "last10_max"),
        ("Last10Sum", "last10_sum"),
        ("Last10Gap", "last10_gap"),
    ):
        for t in config.last10_thresholds:
            add(f"{label}_ge_{t:g}", "forma_recente", f"{label} >= {t:g}", _ge(field, t))
            add(f"{label}_le_{t:g}", "forma_recente", f"{label} <= {t:g}", _le(field, t))

    for field, label in (
        ("HomeVenueOverScore", "home_venue"),
        ("AwayVenueOverScore", "away_venue"),
        ("VenueMin", "venue_min"),
        ("VenueMax", "venue_max"),
        ("VenueSum", "venue_sum"),
        ("VenueGap", "venue_gap"),
    ):
        for t in config.venue_thresholds:
            add(f"{label}_ge_{t:g}", "venue", f"{label} >= {t:g}", _ge(field, t))
            add(f"{label}_le_{t:g}", "venue", f"{label} <= {t:g}", _le(field, t))

    for t in config.btts_thresholds:
        add(f"btts_ge_{t:g}", "btts", f"BTTSProfileScore >= {t:g}",
            _ge("BTTSProfileScore", t))
        add(f"btts_le_{t:g}", "btts", f"BTTSProfileScore <= {t:g}",
            _le("BTTSProfileScore", t))

    for field, name, desc in (
        ("ReasonWeakAwayAttack", "reason_weak_away_attack", "Reason: ospite poco prolifico"),
        ("ReasonHomeAttackNotDominant", "reason_home_attack_not_dominant", "Reason: attacco casa non dominante"),
        ("ReasonLowBTTS", "reason_low_btts", "Reason: BTTS basso"),
        ("ReasonWeakHomeVenue", "reason_weak_home_venue", "Reason: profilo over interno debole"),
        ("ReasonWeakAwayVenue", "reason_weak_away_venue", "Reason: profilo over esterno debole"),
        ("ReasonWeakHomeTrend", "reason_weak_home_trend", "Reason: trend over casa non forte"),
        ("ReasonWeakAwayTrend", "reason_weak_away_trend", "Reason: trend over trasferta non forte"),
        ("ReasonWeakGAWarning", "reason_weak_ga_warning", "Reason: sopravvalutazione weak_ga"),
        ("ReasonV25Penalty", "reason_v25_penalty", "Reason: penalità v25"),
    ):
        add(name, "reason", desc, lambda r, f=field: bool(r.get(f)))

    add(
        "both_attack_scores_ge_10",
        "combinata_base",
        "Entrambi gli AttackScore >= 10",
        lambda r: _num(r.get("AttackMin")) and r["AttackMin"] >= 10,
    )
    add(
        "both_defense_weakness_ge_6",
        "combinata_base",
        "Entrambi i DefenseWeaknessScore >= 6",
        lambda r: _num(r.get("DefenseMin")) and r["DefenseMin"] >= 6,
    )
    add(
        "both_last10_ge_7_2",
        "combinata_base",
        "Entrambi i Last10OverScore >= 7.2",
        lambda r: _num(r.get("Last10Min")) and r["Last10Min"] >= 7.2,
    )
    add(
        "both_venue_ge_7",
        "combinata_base",
        "Entrambi i VenueOverScore >= 7",
        lambda r: _num(r.get("VenueMin")) and r["VenueMin"] >= 7,
    )
    add(
        "balanced_high_attack",
        "combinata_base",
        "AttackMin >= 9 e AttackGap <= 3",
        lambda r: _num(r.get("AttackMin")) and _num(r.get("AttackGap"))
                  and r["AttackMin"] >= 9 and r["AttackGap"] <= 3,
    )
    add(
        "one_sided_attack_risk",
        "combinata_base",
        "AttackMax >= 11 e AttackMin <= 6",
        lambda r: _num(r.get("AttackMax")) and _num(r.get("AttackMin"))
                  and r["AttackMax"] >= 11 and r["AttackMin"] <= 6,
    )
    return metrics
