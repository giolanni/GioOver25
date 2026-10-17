# Audit classifiche Diretta/Flashscore

`analysis.audit_diretta_standings` confronta in sola lettura tutte le
classifiche presenti in `data/storico/classifiche_calcolate` con le
classifiche correnti pubblicate da Diretta/Flashscore.

```powershell
python -m analysis.audit_diretta_standings
```

Per una singola lega:

```powershell
python -m analysis.audit_diretta_standings --league-id Italy_SerieA
```

Il comando produce:

- `analysis/data_quality_report/diretta_standings_audit.md`, sintesi per lega;
- `analysis/data_quality_report/diretta_standings_audit_details.csv`, dettaglio
  squadra per squadra e valori locali/remoti.

Il mapping riusa `league_registry.csv`, gli alias Diretta in
`league_aliases.csv` e `team_name_dictionary.csv`. Se una competizione ha più
stage, viene scelta la classifica con la maggiore sovrapposizione delle
squadre locali. Le somiglianze non presenti nel dizionario sono segnalate come
`ALIAS_SUSPECTED`, senza aggiornare automaticamente alcun dato.

Opzioni utili:

```powershell
python -m analysis.audit_diretta_standings --workers 2 --timeout 40
python -m analysis.audit_diretta_standings --fail-on-difference
python -m analysis.audit_diretta_standings --output-dir C:\temp\gioover-audit
```

`--fail-on-difference` è pensato per CI: l'esecuzione normale termina con zero
anche quando il report contiene differenze. Errori di mapping o disponibilità
di una singola lega vengono registrati nel report e non interrompono le altre.

## Limiti

- Diretta/Flashscore non offre un'API pubblica stabile: feed, firma o schema
  possono cambiare.
- Leghe non presenti, fuori stagione, senza classifica generale o con nomi
  troppo diversi vengono riportate come non mappabili/non disponibili.
- Penalizzazioni, spareggi e criteri ufficiali di tie-break possono produrre
  differenze legittime di punti o posizione rispetto al calcolo locale.
- Il confronto fotografa il momento dell'esecuzione: partite appena concluse
  possono essere già presenti su una sorgente e non ancora sull'altra.
- L'audit legge soltanto gli storici e le classifiche; sovrascrive unicamente
  i due file di report nella directory di output.
