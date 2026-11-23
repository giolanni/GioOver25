# VG3 sperimentale per il mercato Gol

Il comando giornaliero usa il modello congelato incluso nel branch e la libreria standard di Python.

```powershell
python -m analysis.vg3_btts --rank data/input_partite/partite.csv
```

Il file `data/output_ranking/vg3/ranking_vg3.csv` contiene tutte le gare in input ordinate per MatchDate e score decrescente. La soglia ALTA è 66 su 100 sul valore prima dell'arrotondamento. Le gare con storia insufficiente e quelle australiane ricevono NESSUN-SEGNALE. Il comando è indipendente dalla GUI e da rank_matches_v2.

## Come si forma lo score

Una regressione logistica combina cinque misure: probabilità che entrambe segnino ricavata incrociando la frequenza con cui ciascuna segna e quella con cui l'avversaria subisce, la stessa misura distinta per sede, frequenza media BTTS delle due squadre, frequenza nelle ultime otto e frequenza della lega. I tassi sono regolarizzati con osservazioni iniziali per limitare l'effetto dei piccoli campioni. Il modello richiede almeno cinque partite per squadra nella stessa LeagueId nei 180 giorni precedenti. L'identità di squadra segue il nome registrato nella lega. Cambi di nome o di girone possono ridurre lo storico utilizzabile.

## Verifica riproducibile

```powershell
python -m pip install pandas scikit-learn
python -m analysis.vg3_btts --train
```

Il secondo comando ristima e scrive i coefficienti nel JSON accanto al modulo. Per riprodurre i numeri usare lo snapshot ce02df6 di v2-dev. Il laboratorio unisce risultati, finali dei ranking e GS1 con la chiave LeagueId, MatchDate, Home, Away. Esclude punteggi discordanti, vittorie a tavolino segnalate, leghe Australia_ e due date anomale del 2016. I file di classifiche, aggregati dei reset e selezioni di report non forniscono risultati individuali aggiuntivi. Le statistiche di ogni gara usano solo date precedenti e l'esito è HG > 0 e AG > 0. Si tratta di una ricostruzione dallo snapshot corrente, che può contenere correzioni successive al pronostico.

Addestramento fino al 23 settembre 2026 su 10.484 partite. Validazione dal 24 settembre al 23 ottobre su 6.956 partite. Fra le soglie intere da 60 a 85 con almeno 50 selezioni e otto giorni attivi, viene scelta quella con il limite inferiore di Wilson più alto. Test dal 24 ottobre al 22 novembre su 8.944 partite con storia sufficiente. Il set comune richiede anche un ranking VG1 archiviato con PredictionDate entro MatchDate. Il repository non documenta l'orario di emissione per le previsioni dello stesso giorno.

| ALTA su set comune | OK | KO | Totale | BTTS |
|---|---:|---:|---:|---:|
| VG3 validazione | 377 | 205 | 582 | 64,78% |
| VG1 validazione | 88 | 49 | 137 | 64,23% |
| VG3 test | 390 | 223 | 613 | 63,62% |
| VG1 test | 82 | 49 | 131 | 62,60% |

Il comando stampa anche i risultati sull'intero campione, la prima e le prime due ALTA giornaliere e il conteggio delle giornate con tutti gli esiti OK. TOP2 conta fino a due partite per giorno con ALTA. L'analisi misura il mercato BTTS senza quote e usa solo gare risolte nella valutazione retrospettiva.

## Engine operativi in rank_matches_v2

```powershell
python -m gioover25.rank_matches_v2 data/input_partite/partite.csv --engine vg3
python -m gioover25.rank_matches_v2 data/input_partite/partite.csv --engine vg3strict
```

Anche `--engine all` genera i due ranking e registra le previsioni nei rispettivi storici. VG3 include le gare senza segnale. VG3strict pubblica da zero a due gare per MatchDate. Usare l'intero programma giornaliero come input perché la posizione dipende dalle altre gare presenti.

VG3strict calcola V25 sulle stesse gare anche quando viene lanciato da solo. Sul set valutabile da entrambi, prende le due migliori ALTA di VG3. In parallelo applica la soglia 7,5 a entrambi i driver VenueOverScore di V25 e prende le due gare con il miglior punteggio del modello BTTS sui driver V25. Pubblica l'intersezione, con score VG3 e posizioni in Reason. A parità di punteggio ordina per LeagueId, Home, Away. Se manca l'accordo, il CSV giornaliero contiene solo l'intestazione.
