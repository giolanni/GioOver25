# Riconciliazione dopo append_results

Il normale comando append_results riconcilia anche gli storici degli engine non attivi.
La chiave è LeagueId + MatchDate + nomi squadra normalizzati; PredictionDate non seleziona la giornata.

1. Cerca risultati già acquisiti nei CSV risultati e nelle altre occorrenze ranking. Propaga soltanto risultati univoci, senza alterare score, band o metriche. Risultati discordanti sono segnalati.
2. Legge output ranking correnti e old_ranking per le date passate presenti nel CSV importato. Una previsione assente dall'input e senza un risultato già acquisito o un rinvio registrato diventa NOT_FOUND nel registro partite_posticipate. È un rinvio PRESUNTO, non una conferma del provider.
3. Negli storici ranking usa POSTPONED per compatibilità con il successivo recupero del risultato e con le analisi. Un NOT_FOUND si sincronizza solo sulla sua MatchDate, senza coinvolgere una futura gara delle stesse squadre. La chiave del registro rinvii rimane invariata.
4. Stampa tutte le partite uniche dei giorni precedenti ancora SCHEDULED senza punteggio e gli engine interessati nel report data/debug/risultati_non_riconciliati.csv. Il report fotografa l'esecuzione corrente; il motivo NOT_FOUND resta nel registro rinvii.

Oggi e futuro sono esclusi dalla nuova riconciliazione. Con input vuoto non è possibile stabilire la giornata richiesta: nessun NOT_FOUND automatico, ma recupero dei risultati già noti e controllo dei vecchi SCHEDULED comunque eseguiti.

Nessuna modifica a getresults o alla CLI. NOT_FOUND è accettato anche come Status nell'input risultati, con HG/AG vuoti.
