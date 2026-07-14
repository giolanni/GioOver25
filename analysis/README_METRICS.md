# GioOver2.5 — Framework metriche v3

## Cosa analizza

Il framework usa i driver ex ante realmente presenti nei ranking v25:

```text
Score
RankingGapScore
HomeAttackScore
AwayAttackScore
HomeDefenseWeaknessScore
AwayDefenseWeaknessScore
HomeLast10OverScore
AwayLast10OverScore
HomeVenueOverScore
AwayVenueOverScore
BTTSProfileScore
Reason
```

Lo storico fornisce `Band` e `Over25=OK/KO`.

## Matching

```text
se MatchDate presente:
    LeagueId + MatchDate + Home + Away
altrimenti:
    LeagueId + PredictionDate + Home + Away
```

La modalità usata viene salvata in `MatchMode`.

## Comando

```bash
python -m analysis.metrics.analyze_metrics
```

## Output principali

```text
population_summary.csv
metric_catalog.csv
top_alta_ko_patterns.csv
top_media_ok_patterns.csv
metric_occurrences.csv
metric_monthly_stability.csv
skipped_rows.csv
unmatched_history.csv
unmatched_rankings.csv
```

## Nota

Le metriche sono candidate descrittive. Non modificano v25 e non rappresentano
regole già validate.
