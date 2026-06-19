# Pesi iniziali del modello. Somma teorica: 100.
# Sono volutamente facili da modificare dopo i primi test reali.

WEIGHTS = {
    "ranking_gap": 24,
    "strong_team_goals_for": 22,
    "weak_team_goals_against": 22,
    "strong_team_goals_against": 8,
    "weak_team_goals_for": 8,
    "last10_over_profile": 12,
    "random_component": 4,
}

# Limiti usati per normalizzare i valori su scala 0-1.
NORMALIZATION = {
    "max_ranking_gap": 19,
    "excellent_gf_per_match": 2.4,
    "bad_ga_per_match": 2.2,
    "useful_ga_per_match_strong": 1.3,
    "useful_gf_per_match_weak": 1.2,
}
