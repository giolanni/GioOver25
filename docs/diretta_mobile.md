# Diretta Mobile - generazione automatica degli input

## Scopo

Il tool `tools/diretta_mobile.py` permette di interrogare direttamente la versione mobile di Diretta e preparare gli input utilizzati da GioOver2.5.

La sorgente è `m.diretta.it`.

Il tool supporta attualmente tre giornate relative:

- ieri;
- oggi;
- domani.

L'uso di una data arbitraria non è ancora implementato.

## Comandi

### Risultati di ieri

```powershell
python -m tools.diretta_mobile --yesterday
```

Prepara `data/input_risultati/risultati.csv`, destinato ad `append_results`.

### Partite di oggi

```powershell
python -m tools.diretta_mobile --today
```

Prepara `data/input_partite/partite.csv`, destinato a `rank_matches`.

### Partite di domani

```powershell
python -m tools.diretta_mobile --tomorrow
```

Prepara `data/input_partite/partite.csv`, destinato a `rank_matches`.

`--today` e `--tomorrow` usano lo stesso file di destinazione: l'ultimo comando eseguito sostituisce il contenuto precedente.

## Dry run

È possibile controllare ciò che verrebbe prodotto senza modificare i CSV:

```powershell
python -m tools.diretta_mobile --yesterday --dry-run
python -m tools.diretta_mobile --today --dry-run
python -m tools.diretta_mobile --tomorrow --dry-run
```

È consigliabile usare il dry run durante la fase iniziale di verifica del servizio.

## League registry

`data/league_registry.csv` è la fonte canonica per i campionati gestiti da GioOver2.5.

Il servizio prova a risolvere ogni coppia paese/competizione di Diretta nel relativo `LeagueId`.

Le competizioni non riconosciute o non presenti nel registry:

- non vengono inserite nel CSV;
- vengono indicate nel riepilogo a video.

Il servizio riutilizza la logica di normalizzazione e risoluzione già presente in `tools/prepare_input.py`, evitando una seconda implementazione indipendente del mapping.

## Partite borderline

Le partite con orario `00:xx` vengono segnalate esplicitamente come borderline.

Per ciascuna viene mostrato:

- orario;
- paese;
- competizione;
- partita;
- `LeagueId`, se riconosciuto;
- `FUORI REGISTRY`, se non appartiene alle competizioni gestite.

Il servizio non sposta automaticamente queste partite da una data all'altra. La data resta quella della giornata Diretta interrogata.

Questa scelta serve a rendere visibili eventuali problemi di confine giornata senza introdurre correzioni automatiche non verificate.

## Risultati

In modalità `--yesterday` vengono considerate per il CSV solo le partite riconosciute dal registry per cui è disponibile un risultato numerico valido.

Partite rinviate, posticipate, sospese o senza risultato utilizzabile non vengono inserite.

Il formato prodotto è quello canonico di GioOver2.5:

```text
LeagueId;Round;MatchDate;Home;Away;HG;AG;Status;Notes
```

Attualmente `Round` e `Notes` restano vuoti quando l'informazione non è ricavata dalla pagina mobile.

## Partite da analizzare

In modalità `--today` o `--tomorrow` il formato prodotto è:

```text
LeagueId;MatchDate;Home;Away
```

ed è compatibile con l'input di `rank_matches`.

## Filosofia del servizio

Il downloader Diretta deve rimanere un componente di acquisizione dati.

Non esegue automaticamente:

- `rank_matches`;
- `append_results`.

La sequenza prevista nella prima fase è quindi:

```text
m.diretta.it
      |
diretta_mobile
      |
controllo riepilogo / borderline
      |
partite.csv oppure risultati.csv
      |
rank_matches oppure append_results
```

Dopo un periodo di verifica dell'affidabilità del parser si potrà valutare l'esecuzione automatica del passaggio successivo.

## Data arbitraria

Da implementare in una fase successiva.

L'obiettivo è arrivare a una sintassi simile a:

```powershell
python -m tools.diretta_mobile --date YYYY-MM-DD
```

Prima dell'implementazione va verificato il comportamento di `m.diretta.it` per date diverse da ieri/oggi/domani e, in particolare, la gestione delle partite a cavallo della mezzanotte.
