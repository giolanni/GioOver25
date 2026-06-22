# GioOver2.5 - Instructions

## Scopo del progetto

GioOver2.5 è un motore statistico che classifica partite di calcio in base alla probabilità di terminare con almeno 3 gol complessivi (Over 2.5).

L'obiettivo NON è prevedere il risultato esatto, ma costruire un ranking delle partite più interessanti dal punto di vista statistico.

---

# Filosofia del progetto

Ogni modifica deve essere:

- misurabile;
- reversibile;
- documentata.

NON modificare mai pesi o formule sulla base di una o poche partite.

Ogni variazione deve essere supportata da uno storico sufficientemente ampio.

---

# Struttura del progetto

```
GioOver25/

gioover25/
    config.py
    models.py
    io_utils.py
    scoring.py
    main.py
    append_to_storico.py
    aggiorna_esiti.py

data/
    input/
    output/
    storico/

README.md
CHANGELOG.md
instructions.md
```

---

# Formato CSV Input

```
country;
league;
Home;
Away;
PosHome;
PosAway;
PtsHome;
PtsAway;
GFHome;
GSHome;
GFAway;
GSAway;
MatchHome;
WinHome;
GFH10;
GSH10;
MatchAway;
WinAway;
GFA10;
GSA10
```

## Significato colonne

### WinHome / WinAway

ATTENZIONE

NON rappresentano le vittorie.

Rappresentano il numero di Over 2.5 nelle ultime N partite considerate.

---

# Formato CSV Output

```
country
league
home
away
match
score
band

ranking_component
strong_gf_component
weak_ga_component
strong_ga_component
weak_gf_component
last10_component
real_over_index_component
random_component

risultato
ESITO

reason
```

---

# Formato Storico

```
data
model_version

country
league

home
away
match

score
band

ranking_component
strong_gf_component
weak_ga_component
strong_ga_component
weak_gf_component
last10_component
real_over_index_component
random_component

risultato
ESITO
```

Lo storico rappresenta il patrimonio principale del progetto.

NON deve mai essere cancellato.

---

# Workflow

## 1

Creazione CSV input

↓

## 2

Esecuzione

```
python -m gioover25.main
```

↓

## 3

Generazione classifica

↓

## 4

append_to_storico.py

↓

## 5

Inserimento manuale del solo risultato

Esempio

```
2-1
1-1
3-0
RINVIATA
```

↓

## 6

aggiorna_esiti.py

↓

Calcolo automatico

```
OK
KO
RINVIATA
```

---

# Regole di sviluppo

## NON modificare

- struttura TeamStats
- struttura MatchInput
- formato CSV storico

senza aggiornare tutta la pipeline.

---

# Gestione versioni

Ogni modifica significativa incrementa

```
MODEL_VERSION
```

esempio

```
1.0
1.1
1.2
```

e deve essere riportata nel CHANGELOG.

---

# Principi di sviluppo

Ogni modifica deve rispettare queste regole.

## 1

Preferire codice semplice e leggibile.

## 2

Preferire funzioni piccole.

## 3

Preferire dati espliciti rispetto a logiche nascoste.

## 4

Ogni statistica utilizzata deve poter essere salvata nello storico.

---

# Benchmark ufficiale

Australia Giugno 2026

Partite analizzate:

20

Rinviate:

2

Valide:

18

Corrette:

12

Errate:

6

Accuracy:

66.7%

Storicamente la fascia ALTA (>75) è risultata la più affidabile.

---

# Regola fondamentale

NON ottimizzare il modello sulla base di pochi risultati.

Prima di modificare:

- pesi
- normalizzazioni
- formule
- soglie

raccogliere almeno 100 nuove partite concluse.

---

# Obiettivo finale

Trasformare GioOver2.5 da semplice classificatore statistico a laboratorio di analisi.

Ogni partita deve diventare un esperimento registrato contenente:

- input
- output
- componenti dello score
- risultato reale
- esito

per consentire un miglioramento oggettivo del modello basato sui dati e non sulle impressioni.

---

# Ruolo dell'assistente

L'assistente deve comportarsi come un revisore tecnico critico.

NON deve confermare automaticamente le proposte.

Per ogni nuova idea deve valutare:

- vantaggi
- svantaggi
- impatto sullo storico
- rischio di overfitting
- complessità di manutenzione
- reale beneficio statistico

proponendo sempre la soluzione più robusta e mantenibile nel lungo periodo.