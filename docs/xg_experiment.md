# GioOver2.5 — laboratorio xG

Branch: `experiment-xg-engine`

## Obiettivo

Acquisire expected goals da fonti gratuite, normalizzarli sui LeagueId canonici di GioOver2.5 e produrre feature utilizzabili in experiment/backtest senza leakage temporale.

## Fonti implementate

### Understat — primaria

Non richiede API key. Il provider legge i JSON pubblici incorporati nelle pagine Understat.

LeagueId configurati:
- `England_PremierLeague`
- `France_Ligue1`
- `Germany_Bundesliga`
- `Italy_SerieA`
- `Russia_PremierLeague`
- `Spain_LaLiga`

Dati: xG di squadra per match, risultato, ID partita; opzionalmente shot-level xG per singolo match.

### Big Balls Sports Data — secondaria / confronto

REST API con piano gratuito. Richiede `BBS_API_KEY` nell'ambiente.

LeagueId configurati:
- `England_PremierLeague`
- `France_Ligue1`
- `Germany_Bundesliga`
- `Italy_SerieA`
- `Spain_LaLiga`
- `USA_MLS`

La copertura xG può essere parziale: un match senza xG viene saltato, mai interpretato come xG=0.

## Registry

`data/league_registry_xg.csv` contiene volutamente **una sola colonna: `LeagueId`**. Sono ammessi soltanto valori già presenti nel registry canonico principale.

## Comandi

Scaricare Serie A 2026/27 da Understat:

```powershell
python -m gioover25.xg.download_xg --league-id Italy_SerieA --provider understat --season 2026
```

Scaricare MLS da Big Balls:

```powershell
$env:BBS_API_KEY="LA_TUA_CHIAVE"
python -m gioover25.xg.download_xg --league-id USA_MLS --provider bigballs
```

Sintesi corrente per squadra:

```powershell
python -m gioover25.xg.summarize_xg --league-id Italy_SerieA
```

Feature point-in-time per backtest:

```powershell
python -m gioover25.xg.build_features --league-id Italy_SerieA
```

Shot-level Understat:

```powershell
python -m gioover25.xg.download_shots MATCH_ID
```

## Output

- `data/xg/raw/<provider>/...csv`: xG normalizzati partita per partita.
- `data/xg/summary/...csv`: sintesi per squadra (stagione + recent form).
- `data/xg/features/...csv`: feature pre-match point-in-time.
- `data/xg/shots/understat/...json`: shot-level xG opzionale.

## Feature già disponibili

Per ogni squadra vengono calcolati:
- partite xG disponibili;
- xGF totale e medio;
- xGA totale e medio;
- differenziale xG medio;
- xGF/xGA recenti;
- finestre Last3, Last5 e Last10 nel dataset point-in-time;
- `ProjectedHomeXG`, `ProjectedAwayXG`, `ProjectedTotalXG` come stima neutra iniziale.

`Projected*` è volutamente una feature di laboratorio, non è ancora una regola dell'engine.

## Anti-leakage

`build_features.py` usa soltanto dati precedenti alla partita analizzata. Le partite della stessa data vengono trattate come un blocco: nessuna vede gli xG di un'altra gara dello stesso giorno.

Questo è il dataset da usare quando inizieremo a valutare se e quanto gli xG migliorano v20/v20def o un nuovo engine dedicato.
