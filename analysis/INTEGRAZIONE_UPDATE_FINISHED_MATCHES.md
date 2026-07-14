# Integrazione automatica con update_finished_matches

Al termine dell'aggiornamento dello storico ranking si può richiamare il modulo
metriche in modo separato, così un errore dell'analisi non annulla il lavoro
principale.

```python
import subprocess
import sys

try:
    subprocess.run(
        [sys.executable, "-m", "analysis.metrics.analyze_metrics"],
        check=True,
    )
except Exception as exc:
    print(f"[WARN] Analisi metriche non completata: {exc}")
```

La posizione esatta della chiamata dipende dalla struttura attuale di
`update_finished_matches.py`. Sarebbe preferibile inserirla solo dopo che il
file storico è stato salvato correttamente.
