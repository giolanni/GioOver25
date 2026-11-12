# Audit prepare_input — mapping gironi (12 novembre 2026)

## Esito

Esaminato `tools/prepare_input.py` sul branch `v2-dev`. Il programma **usa già** sette mappe da `docs`, definite staticamente in `TEAM_MAPPING_FILES` (righe 9–17):

- Moldova Liga 1 (2026)
- Portugal Liga 3 (2026-27)
- Indonesia Championship (2026-27)
- Finland Kolmonen (2026)
- Perù Liga 2 (2026)
- USA MLS Next Pro (2026)
- USA USL League Two (2026)

Il caricatore `load_team_mappings()` (righe 57–74) riconosce CSV con `Team` e `LeagueId` o TXT `Team=LeagueId`. `resolve_match()` (righe 140–150) applica il mapping prima della risoluzione per nome della lega; quando uno dei due nomi è mappato a un LeagueId del paese ma non c'è un girone comune, restituisce `None` per evitare una classificazione arbitraria.

## Criticità concrete

1. **Nuove mappe non operative**: `docs/Tunisia_Ligue2_2026-27_team_mapping.csv` e `docs/SaudiArabia_Division2_2026-27_team_mapping.csv` non sono nell'elenco statico e usano `Team;Group` anziché `Team;LeagueId`. Non basta aggiungerle all'elenco: servono LeagueId di girone effettivamente presenti nel catalogo operativo e alias squadra validati.
2. **Stagione ignorata**: il caricatore non filtra per stagione/MatchDate. Se una squadra cambia girone tra due stagioni, il set di destinazioni può diventare ambiguo. Un registro annuale documentale non è attualmente letto dal programma.
3. **Ambiguità cross-league**: `load_team_mappings` indicizza le squadre solo con `norm(team)`, non con la competizione d'origine. `resolve_team_mapping` filtra per paese, ma non per competizione: due competizioni dello stesso paese possono condividere un nome squadra.
4. **Mappe incomplete e alias**: `moldova_liga1_groups_2026.csv` contiene 11 righe, mentre il formato stagionale va confermato. `kolmonen_2026_team_league_map.csv` contiene nomi canonici e alias, ma il caricatore usa solo `SourceTeam` e non considera `CanonicalTeam` nella stessa riga. Alias presenti in gruppi diversi richiedono un controllo esplicito.
5. **Nessuna validazione della stagione nel registry**: `data/league_registry.csv` contiene i LeagueId operativi; `docs/league_group_registry.csv` non è ancora collegato a `prepare_input`.

## Raccomandazione

Mantenere `data/league_registry.csv` come elenco di LeagueId operativi, con un LeagueId per girone quando il formato lo richiede. Non creare automaticamente nuove righe da `docs/league_group_registry.csv`.

Prima di modificare il caricatore:
1. Introdurre un formato unificato di mapping: `Season;ParentLeagueId;Team;GroupLeagueId;AliasStatus`.
2. Validare che ogni `GroupLeagueId` esista nel registry e sia figlio della competizione corretta.
3. Risolvere per `Season + ParentLeagueId + Team`, usando MatchDate.
4. Se la coppia squadra-girone è ambigua o il mapping incompleto, segnalare il caso come non risolto; non assegnare la lega madre per fallback.
5. Aggiungere test su Portugal, Indonesia, Moldova, Peru, Kolmonen, MLS Next Pro, USL League Two e sul cambio di stagione.
6. Solo dopo attivare Tunisia e Arabia Saudita; per Arabia Saudita completare prima il gruppo B.

**Nessuna modifica a engine, risultati, classifiche o `data/league_registry.csv` durante questo audit.**
