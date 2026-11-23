"""Ranking giornaliero BTTS con il modello congelato del laboratorio."""
import json

from analysis import vg3_btts as lab

ENGINE_NAME = "vg3"
ENGINE_VERSION = "3.0.0"
MARKET = "GOAL"


def rank_day_inputs(rows, prediction_date):
    targets = {lab.key(row, row["LeagueId"]): row for row in rows}
    model = json.loads(lab.MODEL.read_text())
    finals, _, _ = lab.archive()
    rankings = []
    for key, features in lab.replay(finals, set(targets)):
        day, league, home, away = key
        probability = None
        if features is not None and not league.startswith("Australia_"):
            probability = lab.probability(features, model)
        band = "NESSUN-SEGNALE" if probability is None else (
            "ALTA" if probability >= model["alta"] else "BASSA"
        )
        rankings.append({
            "MatchDate": day.isoformat(), "LeagueId": league, "Home": home, "Away": away,
            "PredictionDate": prediction_date, "Round": targets[key].get("Round", ""),
            "HomeSourceLeagueId": league, "AwaySourceLeagueId": league,
            "AlgorithmVersion": ENGINE_VERSION,
            "Score": probability * 100 if probability is not None else "", "Band": band,
            "Reason": "VG3 BTTS" if probability is not None else
                      ("Lega australiana esclusa" if league.startswith("Australia_") else "Meno di 5 gare per squadra nei 180 giorni precedenti"),
        })
    return rankings
