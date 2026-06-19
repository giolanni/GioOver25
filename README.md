# GioOver2.5

Applicativo Python per valutare le partite del giorno e produrre una classifica pesata delle gare più interessanti per Over 2.5.

## Obiettivo

Il programma prende in input un file CSV con dati ricavati manualmente da Diretta.it e calcola uno score Over 2.5 basato su:

1. Differenza e tipo di classifica tra le due squadre.
2. Gol fatti dalla squadra più alta in classifica.
3. Gol subiti dalla squadra più bassa in classifica.
4. Gol subiti dalla squadra più alta in classifica.
5. Gol fatti dalla squadra più bassa in classifica.
6. Andamento ultime 10 partite / H2H per ciascuna squadra.
7. Componente random controllata.

## Avvio rapido

```bash
python -m gioover25.main data/input/partite_esempio.csv
```

Output:

```text
data/output/classifica_over25.csv
```

## Formato CSV input

Vedi `data/input/partite_esempio.csv`.

