# Gironi e mapping squadre — gestione annuale

Registro principale: `docs/maps/league_group_registry.csv`. Una riga per lega e stagione, con struttura, dimensioni, stato della verifica e fonte. Aggiornare ogni anno **prima** di utilizzare i mapping per calcolare classifiche o driver.

## Stati
- `CONFIRMED`: struttura verificata, non necessariamente tutti gli alias del provider.
- `KNOWN_FORMAT`: campionato con numero elevato di squadre legittimo.
- `SECONDARY_SOURCE`: attendere ulteriore conferma prima dell'uso automatico.
- `CONFLICTING_COUNTS`: numero di squadre discordante fra fonti; richiede controllo manuale.
- `REVIEW_REQUIRED`: struttura non verificata per la stagione.
- `GROUP_ASSIGNMENTS_INCOMPLETE`: struttura confermata ma elenco delle squadre incompleto.

## CSV di mapping
Le colonne `Team;Group;SourceNameStatus;SourceURL` riportano il nome pubblicato e il girone. **Non sono ancora un mapping eseguibile per il codice**, perché il nome del provider in `data/storico/risultati` e `data/storico/classifiche_calcolate` potrebbe essere diverso. Non usare corrispondenze approssimative automaticamente: confrontare gli elenchi con i nomi effettivi e creare alias espliciti verificati.

Per il 2026-27 sono state trascritte le assegnazioni pubblicate per Tunisia Ligue 2 e Saudi Arabia Division 2. **Attenzione Arabia Saudita:** il comunicato indica 16 squadre per girone, ma il testo disponibile elenca solo 15 nomi per il gruppo B; il mapping è incompleto e non deve essere usato finché la sedicesima squadra non sarà verificata. Algeria, Congo, Libia, Argentina e Ghana necessitano ancora di assegnazioni verificabili/normalizzazione; **non inventare** le squadre mancanti.

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

## Mappe storiche già censite

Il registro comprende anche le mappe già presenti in `docs` per:
- Indonesia Championship (West/East, 2026-27)
- Portugal Liga 3 (Serie A/Serie B, 2026-27)
- Finland Kolmonen (10 gruppi regionali, 2026)
- Moldova Liga 1 (Group A/B; elenco in mappa incompleto da verificare, 2026)
- Perù Liga 2 (Group A/B; controllare la fase playoff, 2026)
- USA MLS Next Pro (4 divisioni, 2026)
- USA USL League Two (20 divisioni del mapping, 2026; PlayIn/PlayOff non sono gironi)

**Distinzione importante:** `data/league_registry.csv` è il catalogo operativo dei LeagueId usati dai processi e dalle classifiche. `docs/maps/league_group_registry.csv` è il registro storico/stagionale della struttura a gironi. Non copiare automaticamente le righe dal secondo al primo. Il primo va modificato solo per LeagueId mancanti o proprietà operative dimostratamente errate, dopo aver verificato la logica di ingestione e l'assegnazione ai singoli gironi. Al momento i genitori e i sottogironi di Indonesia, Portogallo, Moldova e Perù risultano già presenti nel catalogo operativo; sono presenti anche i gruppi regionali finlandesi e le divisioni MLS Next Pro e USL League Two. Le mappe non sono di per sé prova che l'applicativo le carichi.
