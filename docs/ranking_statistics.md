# Statistiche degli storici ranking

Il comando legge direttamente i file in `data/storico/ranking` e calcola:

- Over 2.5 per `ALTA`;
- Over 2.5 per `IMM-ALTA-*`, separatamente;
- Over 1.5 per `MEDIA`;
- Over 1.5 per `MEDIA-ALTA`;
- Over 1.5 per `MEDIA + MEDIA-ALTA`.

Vengono considerate soltanto le partite concluse con `Over25=OK/KO`. Le date
sono sempre `MatchDate`; soltanto per le righe legacy senza `MatchDate` viene
usata `PredictionDate`.

## Esempi

Intero storico di ogni engine e set comune a tutti gli engine:

```powershell
python -m analysis.ranking_statistics
```

Giorni specifici:

```powershell
python -m analysis.ranking_statistics --dates 2026-09-05 2026-09-06 2026-09-07
```

Il risultato precedente è cumulativo. Per ottenere nello stesso lancio sia il
cumulativo sia ogni giornata separata:

```powershell
python -m analysis.ranking_statistics --dates 2026-09-05 2026-09-06 2026-09-07 --daily
```

Sono accettate anche date italiane:

```powershell
python -m analysis.ranking_statistics --dates 05/09/2026 06/09/2026 07/09/2026
```

Ultimi 10 giorni di calendario, calcolati rispetto all'ultima `MatchDate`
conclusa disponibile:

```powershell
python -m analysis.ranking_statistics --last-days 10
```

Si può aggiungere `--daily` anche agli ultimi N giorni.

Solo set comune e anche confronto senza Australia:

```powershell
python -m analysis.ranking_statistics --scope common --league-view both
```

Solo alcuni engine:

```powershell
python -m analysis.ranking_statistics --engines v20 v22 v25 v26
```

Intervallo di date:

```powershell
python -m analysis.ranking_statistics --start-date 2026-09-01 --end-date 2026-09-07
```

Esportazione CSV:

```powershell
python -m analysis.ranking_statistics --last-days 10 --csv data/output_reports/ranking_statistics_ultimi10.csv
```

## Definizione del set comune

Una fixture è identificata da:

```text
LeagueId + MatchDate + Home + Away
```

Il set comune contiene soltanto le fixture concluse presenti in tutti gli
engine selezionati. Eventuali fixture con risultati discordanti tra gli engine
sono escluse e segnalate.

La classifica è ordinata prima per percentuale e poi per numerosità del campione.
La metrica di ordinamento predefinita è `alta_o25`; si può cambiare con
`--sort-by`.
