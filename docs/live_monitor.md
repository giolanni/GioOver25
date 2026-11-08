# Monitor LIVE Diretta

Il pulsante **Aggiorna LIVE** esegue `python -m tools.live_flashscore`
su richiesta (nessun polling automatico). Il modulo riutilizza
`tools.diretta_mobile.fetch_feed`, `parse_feed` e
`tools.prepare_input.resolve_match` / `canonical_team`.

Prende le partite con MatchDate odierna dagli storici ranking,
interroga il feed giornaliero Diretta e i due offset adiacenti,
associa soltanto le corrispondenze univoche per campionato, data,
squadra di casa e trasferta e scrive esclusivamente
`data/live/partite_live.csv`.

Non è più richiesto `flashscore_match_ids.csv`.
Se non trova corrispondenze conserva il CSV precedente.

Gli stati sono conservativi: codice feed AB=3 interpretato come FINAL,
AB=2 come LIVE, altri codici non sono trasformati in esiti finali.
**Da verificare sul feed reale** che i codici di stato siano corretti;
in particolare evitare falsi KO. Le partite prive di uno stato
riconosciuto non vengono mostrate come esiti verificati.

Diagnostica:
```powershell
python -m tools.live_flashscore
```

Nessuna modifica a engine, storici ufficiali o file risultati.
