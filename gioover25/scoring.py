import random
from .config import WEIGHTS, NORMALIZATION
from .models import MatchInput, TeamStats


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(max_value, value))


def identify_strong_weak(match: MatchInput) -> tuple[TeamStats, TeamStats]:
    """La squadra più alta in classifica è quella con posizione numerica più bassa."""
    if match.home.position <= match.away.position:
        return match.home, match.away
    return match.away, match.home


def ranking_gap_score(strong: TeamStats, weak: TeamStats) -> float:
    """
    Valuta il tipo di distanza in classifica.

    Regole iniziali:
    - Grande distanza tipo 1 vs ultima: molto positiva.
    - Scontri diretti altissimi, es. 1 vs 2: cautela.
    - Scontri diretti bassissimi, es. 19 vs 20: cautela.
    - Squadre vicine a metà classifica: non vengono penalizzate troppo.
    """
    gap = abs(strong.position - weak.position)
    base = clamp(gap / NORMALIZATION["max_ranking_gap"])

    # Penalità per scontri troppo bloccati in alto o in basso.
    both_top = strong.position <= 3 and weak.position <= 5 and gap <= 3
    both_bottom = strong.position >= 16 and weak.position >= 16 and gap <= 3

    if both_top:
        base *= 0.45
    elif both_bottom:
        base *= 0.35
    elif gap <= 2 and 6 <= strong.position <= 12 and 6 <= weak.position <= 14:
        # Squadre vicine ma di metà classifica: partita potenzialmente meno bloccata.
        base = max(base, 0.45)

    return clamp(base)


def last10_team_profile(team: TeamStats) -> float:
    """
    Profilo ultime 10: premia gli Over, ma soprattutto la partecipazione offensiva.

    Caso importante:
    - 10 Over su 10 ma 0 gol fatti: non deve essere premiato troppo.
    - 10 Over su 10 con gol fatti e gol subiti: profilo molto interessante.
    """
    over_component = team.last10_over_rate
    attack_component = clamp(team.last10_gf_per_match / 1.6)
    defensive_openness = clamp(team.last10_ga_per_match / 2.0)

    # Partecipazione offensiva più importante del semplice Over grezzo.
    return clamp((over_component * 0.35) + (attack_component * 0.45) + (defensive_openness * 0.20))


def last10_match_profile(home: TeamStats, away: TeamStats) -> float:
    home_profile = last10_team_profile(home)
    away_profile = last10_team_profile(away)

    # Penalità se entrambe segnano pochissimo anche se subiscono tanto.
    both_low_attack = home.last10_gf_per_match < 0.6 and away.last10_gf_per_match < 0.6
    combined = (home_profile + away_profile) / 2

    if both_low_attack:
        combined *= 0.55

    return clamp(combined)


def calculate_score(match: MatchInput, random_seed: int | None = None) -> dict:
    if random_seed is not None:
        random.seed(random_seed)

    strong, weak = identify_strong_weak(match)

    ranking_score = ranking_gap_score(strong, weak)
    strong_gf_score = clamp(strong.gf_per_match / NORMALIZATION["excellent_gf_per_match"])
    weak_ga_score = clamp(weak.ga_per_match / NORMALIZATION["bad_ga_per_match"])
    strong_ga_score = clamp(strong.ga_per_match / NORMALIZATION["useful_ga_per_match_strong"])
    weak_gf_score = clamp(weak.gf_per_match / NORMALIZATION["useful_gf_per_match_weak"])
    last10_score = last10_match_profile(match.home, match.away)

    random_score = random.random()

    total = (
        ranking_score * WEIGHTS["ranking_gap"]
        + strong_gf_score * WEIGHTS["strong_team_goals_for"]
        + weak_ga_score * WEIGHTS["weak_team_goals_against"]
        + strong_ga_score * WEIGHTS["strong_team_goals_against"]
        + weak_gf_score * WEIGHTS["weak_team_goals_for"]
        + last10_score * WEIGHTS["last10_over_profile"]
        + random_score * WEIGHTS["random_component"]
    )

    if total >= 75:
        band = "ALTA"
    elif total >= 60:
        band = "MEDIA-ALTA"
    elif total >= 45:
        band = "MEDIA"
    else:
        band = "BASSA"

    reasons = []
    reasons.append(f"Squadra alta: {strong.name} ({strong.position}ª), squadra bassa: {weak.name} ({weak.position}ª)")
    reasons.append(f"GF alta: {strong.gf_per_match:.2f}/gara")
    reasons.append(f"GS bassa: {weak.ga_per_match:.2f}/gara")
    reasons.append(f"Profilo ultime 10: {last10_score:.2f}")

    return {
        "home": match.home.name,
        "away": match.away.name,
        "match": f"{match.home.name} - {match.away.name}",
        "score": round(total, 2),
        "band": band,
        "ranking_component": round(ranking_score * WEIGHTS["ranking_gap"], 2),
        "strong_gf_component": round(strong_gf_score * WEIGHTS["strong_team_goals_for"], 2),
        "weak_ga_component": round(weak_ga_score * WEIGHTS["weak_team_goals_against"], 2),
        "strong_ga_component": round(strong_ga_score * WEIGHTS["strong_team_goals_against"], 2),
        "weak_gf_component": round(weak_gf_score * WEIGHTS["weak_team_goals_for"], 2),
        "last10_component": round(last10_score * WEIGHTS["last10_over_profile"], 2),
        "random_component": round(random_score * WEIGHTS["random_component"], 2),
        "reason": " | ".join(reasons),
    }
