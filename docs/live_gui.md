# Monitor LIVE della GUI

## Scopo e separazione dei dati

La schermata **LIVE** di `gioover25_gui.py` segue durante la giornata le
partite gia' presenti nei ranking degli engine. L'acquisizione usa lo stesso
feed Diretta/Flashscore gia' impiegato da `tools/diretta_mobile.py` e lo stesso
mapping di `data/league_registry.csv`.

Il dato operativo viene scritto esclusivamente in:

```text
data/live/partite_live.csv
```

Il monitor non modifica gli engine, non scrive negli storici di ranking o dei
risultati e non esegue `append_results`. Un risultato LIVE non viene quindi
mai importato automaticamente come risultato ufficiale.

## Avvio

Dalla cartella principale del repository:

```powershell
python gioover25_gui.py
```

Aprire **LIVE** nella barra laterale. L'aggiornamento automatico e' attivo per
impostazione predefinita ogni 60 secondi. L'intervallo e' modificabile nella
barra superiore (minimo 15 secondi); il pulsante **Aggiorna LIVE** forza un
singolo aggiornamento senza bloccare Tkinter.

Per acquisire il CSV senza GUI:

```powershell
python -m gioover25.live
```

Per un monitor da terminale:

```powershell
python -m gioover25.live --watch --interval 60
```

## Formato CSV

Il file usa il separatore `;` coerente con gli altri CSV del progetto:

```text
MatchDate;LeagueId;Home;Away;MatchId;Minute;HG;AG;Status;LastUpdate
```

La scrittura e' atomica. Se tutti i feed falliscono, il CSV precedente viene
conservato e l'errore viene registrato in `data/live/live.log`.

## Matching e deduplica

- I tre feed relativi (giornata richiesta e adiacenti) vengono filtrati usando
  la data reale dell'evento.
- La deduplica usa prima `MatchId` e poi la chiave canonica
  `MatchDate + LeagueId + Home + Away`.
- Il collegamento ai ranking usa i nomi squadra canonici del progetto; il
  fallback fuzzy e' limitato alla stessa data e allo stesso `LeagueId` e viene
  rifiutato se ambiguo.
- Le righe duplicate dello stesso engine vengono ridotte alla previsione piu'
  recente.

## Colori ed esiti

La GUI mostra una riga distinta per **Over 2.5** e **BTTS**:

- verde: obiettivo gia' raggiunto, anche a partita in corso;
- rosso: `KO` soltanto quando lo stato e' `FINAL`;
- giallo: partita disponibile ma obiettivo ancora in attesa;
- grigio: feed o matching non disponibile, partita rinviata o punteggio finale
  non utilizzabile.

Le percentuali nel riepilogo dell'engine usano esclusivamente partite `FINAL`
con punteggio valutabile. Il riquadro **Dato LIVE** segnala `FRESH`, `STALE` o
`UNAVAILABLE`; la soglia stale e' il massimo tra 180 secondi e tre intervalli
di aggiornamento.

## Collaudo

```powershell
python -m unittest tests.test_live -v
python -m unittest discover -s tests -v
```

I test coprono parsing degli stati/minuto, filtro data, deduplica, matching
normalizzato e fuzzy non ambiguo, CSV, stale, Over 2.5, BTTS e riepiloghi
calcolati solo sui finali.
