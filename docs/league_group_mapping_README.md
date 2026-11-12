# Gironi e mapping squadre — gestione annuale

Registro principale: `docs/league_group_registry.csv`. Una riga per lega e stagione, con struttura, dimensioni, stato della verifica e fonte. Aggiornare ogni anno **prima** di utilizzare i mapping per calcolare classifiche o driver.

## Stati
- `CONFIRMED`: struttura verificata, non necessariamente tutti gli alias del provider.
- `KNOWN_FORMAT`: campionato con numero elevato di squadre legittimo.
- `SECONDARY_SOURCE`: attendere ulteriore conferma prima dell'uso automatico.
- `CONFLICTING_COUNTS`: numero di squadre discordante fra fonti; richiede controllo manuale.
- `REVIEW_REQUIRED`: struttura non verificata per la stagione.

## CSV di mapping
Le colonne `Team;Group;SourceNameStatus;SourceURL` riportano il nome pubblicato e il girone. **Non sono ancora un mapping eseguibile per il codice**, perché il nome del provider in `data/storico/risultati` e `data/storico/classifiche_calcolate` potrebbe essere diverso. Non usare corrispondenze approssimative automaticamente: confrontare gli elenchi con i nomi effettivi e creare alias espliciti verificati.

Per il 2026-27 sono state trascritte le assegnazioni pubblicate per Tunisia Ligue 2 e Saudi Arabia Division 2. Algeria, Congo, Libia, Argentina e Ghana necessitano ancora di assegnazioni verificabili/normalizzazione; **non inventare** le squadre mancanti.

## Procedura di rinnovo
1. Verificare formato e partecipanti da fonte ufficiale per la nuova stagione.
2. Aggiornare `Season`, `ExpectedTeams`, `Groups`, `GroupSizes`, `SourceURL` e `Verification`.
3. Creare il CSV `<LeagueId>_<Season>_team_mapping.csv` soltanto dopo aver reperito le assegnazioni.
4. Confrontare i nomi con i file locali e risolvere gli alias.
5. Solo dopo, integrare i mapping nel calcolo della classifica; non modificare automaticamente gli engine.
6. Ripetere `python -m analysis.data_quality --quick` e verificare eventuali discrepanze.

## Anomalia Congo DR
FECOFA comunica 25 club (13+12), ma footrdc.com/linafoot/clubs elenca 26 club (13+13). La classifica locale ne mostra 26. Non rimuovere nessuna squadra senza identificare causa e fase/season corretta.

## Avvertenza
Una lega con più di 22 squadre può essere regolare; il problema reale è l'eventuale calcolo di una **classifica unica per gironi distinti**. Questo registro è documentazione e non modifica la logica del ranking.
