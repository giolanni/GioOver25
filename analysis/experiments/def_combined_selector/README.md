# DEF combined selector backtest

Esegue una simulazione retroattiva della regola congiunta:

`v20def >= X AND v22def >= Y AND v25def >= Z`

Le tre soglie sono indipendenti. L'esperimento non modifica gli engine e usa gli score DEF ricostruiti point-in-time dal backtest retroattivo.

Esecuzione:

```powershell
python -m analysis.experiments.def_combined_selector_backtest
```

Output generati in `analysis/experiments/def_combined_selector/output/`.

Il confronto principale comprende la baseline `71/75/75`, l'ipotesi `70/80/80`, l'intera griglia delle combinazioni, stabilità mensile, risultati senza Australia e ranking tramite limite inferiore Wilson 95%.
