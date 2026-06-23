# Workflow GioOver2.5

## 1. Creazione file di input

Creare un file CSV nella cartella:

```
data/input/
```

Formato:

```csv
country;league;Home;Away;PosHome;PosAway;PtsHome;PtsAway;GFHome;GSHome;GFAway;GSAway;MatchHome;WinHome;GFH10;GSH10;MatchAway;WinAway;GFA10;GSA10
```

---

## 2. Generazione classifica

Eseguire:

```powershell
python -m gioover25.main data/input/partite<data>.csv --output data/output/classifica<data>.csv --seed 42
```

Esempio:

```powershell
python -m gioover25.main data/input/partite21giugno2026.csv --output data/output/classifica_21giu2026.csv --seed 42
```

Output:

```
data/output/classifica_21giu2026.csv
```

---

## 3. Aggiornamento storico

Eseguire:

```powershell
python -m gioover25.append_to_storico data/output/classifica_23giu2026_2.csv --data 2026-06-23

```

Output:

```
data/storico/storico_risultati.csv
```

Le partite vengono aggiunte automaticamente allo storico.

---

## 4. Inserimento risultati

Aprire:

```
data/storico/storico_risultati.csv
```

Compilare solamente la colonna:

```
risultato
```

Valori ammessi:

```
2-1
1-1
3-0
0-0
RINVIATA
```

NON compilare la colonna ESITO.

---

## 5. Aggiornamento automatico esiti

Eseguire:

```powershell
python -m gioover25.aggiorna_esiti --storico data/storico/storico_risultati.csv
```

Lo script aggiornerà automaticamente:

```
ESITO

OK
KO
RINVIATA
```

---

# Regole operative

NON modificare manualmente:

- score
- band
- componenti dello score
- ESITO

Compilare esclusivamente:

```
risultato
```

---

# Flusso completo

```
Creazione CSV Input
        │
        ▼
gioover25.main
        │
        ▼
Classifica CSV
        │
        ▼
append_to_storico.py
        │
        ▼
storico_risultati.csv
        │
        ▼
Inserimento colonna "risultato"
        │
        ▼
aggiorna_esiti.py
        │
        ▼
Storico aggiornato con ESITO automatico
```