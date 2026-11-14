# Serie D italiana - onboarding 2026/27

Nove campionati separati nel registro: `Italy_SerieD_GironeA` ... `Italy_SerieD_GironeI`.
La colonna `CompetitionGroup` vale `Italy_SerieD` per raggruppamento amministrativo,
ma **non** deve fondere classifiche o statistiche fra gironi.

| LeagueId | Fonte risultati e calendario |
|---|---|
| Italy_SerieD_GironeA | https://www.diretta.it/calcio/italia/serie-d-girone-a/ |
| Italy_SerieD_GironeB | https://www.diretta.it/calcio/italia/serie-d-girone-b/ |
| Italy_SerieD_GironeC | https://www.diretta.it/calcio/italia/serie-d-girone-c/ |
| Italy_SerieD_GironeD | https://www.diretta.it/calcio/italia/serie-d-girone-d/ |
| Italy_SerieD_GironeE | https://www.diretta.it/calcio/italia/serie-d-girone-e/ |
| Italy_SerieD_GironeF | https://www.diretta.it/calcio/italia/serie-d-girone-f/ |
| Italy_SerieD_GironeG | https://www.diretta.it/calcio/italia/serie-d-girone-g/ |
| Italy_SerieD_GironeH | https://www.diretta.it/calcio/italia/serie-d-girone-h/ |
| Italy_SerieD_GironeI | https://www.diretta.it/calcio/italia/serie-d-girone-i/ |

## Stato
- Registro: aggiunte nove leghe; `Teams=0` e `ExpectedRounds=0` fino a validazione del formato di ogni girone.
- URL: percorsi Diretta identificati; non sono identificativi Flashscore/endpoint API verificati.
- Non ancora completati: mappatura ID sorgente, squadre per girone, normalizzazione nomi,
  importazione dei risultati da settembre 2026, verifica getmatches/getresults/prepare_input,
  controllo ranking e append_results.
- Non attribuire partite alla Serie D senza identificazione certa del girone.
- Non modificare gli engine né retrodatare pronostici: gli storici dei risultati
  possono essere importati retroattivamente, ma i pronostici vanno calcolati
  con le informazioni disponibili alla rispettiva MatchDate.
