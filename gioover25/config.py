# Pesi iniziali del modello. Somma teorica: 100.
# Sono volutamente facili da modificare dopo i primi test reali.
WEIGHTS = {
    "ranking_gap": 22,
    "strong_team_goals_for": 20,
    "weak_team_goals_against": 20,
    "strong_team_goals_against": 7,
    "weak_team_goals_for": 7,
    "last10_over_profile": 10,
    "real_over_index": 10,
    "random_component": 0,
}

# Limiti usati per normalizzare i valori su scala 0-1.
NORMALIZATION = {
    "max_ranking_gap": 19,
    "excellent_gf_per_match": 2.4,
    "bad_ga_per_match": 2.2,
    "useful_ga_per_match_strong": 1.3,
    "useful_gf_per_match_weak": 1.2,
}

MODEL_VERSION = "1.3"
