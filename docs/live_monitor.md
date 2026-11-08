# Monitor LIVE: associazione esplicita degli ID Flashscore

Il modulo `python -m tools.live_flashscore` legge
`data/live/flashscore_match_ids.csv` con intestazione:

```csv
MatchDate;LeagueId;Home;Away;MatchId
```

Ogni riga deve contenere i nomi **esatti** usati nel ranking e l'ID
Flashscore verificato per quella partita. Non vengono effettuate
associazioni fuzzy per evitare falsi OK/KO.

Aprendo **Monitor LIVE** nella GUI viene lanciata una lettura in
background; il tentativo si ripete ogni 60 secondi finché la sezione
è aperta. La finestra mostra eventuali errori nel log.

ATTENZIONE: la struttura dei feed Flashscore non è documentata e
può cambiare. Il parser accetta soltanto punteggi e stati riconosciuti;
se non riesce a verificarli, non modifica il CSV precedente.
Non è ancora disponibile la scoperta automatica degli ID delle partite.
I feed devono essere verificati su un evento reale prima di considerare
operativa l'acquisizione.

Per diagnosticare un ID:

```powershell
python -m tools.probe_flashscore_match --match-id ID
python -m tools.live_flashscore
```

Gli storici ranking e risultati ufficiali non vengono modificati.
