# TODO GioOver2.5 — sviluppo metriche

- Aggiungere `MatchDate` a tutti i nuovi file ranking prodotti da `rank_matches_v2`.
- Usare `MatchDate` come data primaria; mantenere `PredictionDate` solo come
  informazione storica e fallback legacy.
- Risolvere il bug per cui negli storici ranking non vengono conservate tutte
  le statistiche ex ante disponibili al momento della prediction.
- Quando il bug sarà corretto, estendere il framework alle statistiche grezze:
  punti, PPG, GF/partita, GA/partita, forma recente e dati venue.
- Rimuovere il fallback su `PredictionDate` dopo la bonifica completa.
