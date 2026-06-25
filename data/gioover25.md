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

# Ruolo dell'assiste# GioOver2.5 - Specifiche Tecniche e Linee Guida (v2.0)

## 1. Scopo del progetto

GioOver2.5 nasce come motore statistico per stimare la probabilità che una partita termini con almeno **3 gol complessivi (Over 2.5)**.

L'obiettivo della versione 2.x è evolvere il progetto in una piattaforma completa per:

* raccolta dello storico dei campionati;
* ricostruzione automatica delle classifiche;
* estrazione dinamica delle statistiche;
* analisi delle prestazioni del modello;
* evoluzione futura verso un **Goal Probability Engine**.

---

# 2. Filosofia del progetto

Ogni modifica deve essere:

* misurabile;
* documentata;
* reversibile;
* verificabile statisticamente.

Il modello NON deve essere modificato sulla base di poche partite.

Ogni modifica dovrà essere giustificata dallo storico raccolto.

---

# 3. Architettura

```
GioOver25/

gioover25/

data/

    storico/

        risultati/

            Country_League_Season.csv

        classifiche_calcolate/

            Country_League_Season.csv

    input_partite/

    output_ranking/

    league_registry.csv

docs/

CHANGELOG.md
ROADMAP.md
instructions.md
```

La cartella **raw** è stata eliminata.

---

# 4. Convenzioni

## Nome file

Sempre

```
Country_League_Season.csv
```

Esempi

```
Iceland_Division1_2026.csv

Norway_3rdDivision_Group6_2026.csv

USA_USLLeagueTwo_Heartland_2026.csv
```

Mai spazi.

Sempre underscore.

---

# 5. league_registry.csv

Contiene le informazioni strutturali delle competizioni.

Campi previsti:

* Country
* League
* Season
* Teams
* Rounds
* Promotion
* Relegation
* Playoff
* Notes

Il file verrà utilizzato da tutto il software.

---

# 6. Storico risultati

Percorso

```
data/storico/risultati/
```

Ogni riga rappresenta una partita.

Formato

```
Date
Round
Home
Away
HomeGoals
AwayGoals
Result
```

Questo rappresenta la base dati ufficiale del progetto.

Non viene mai cancellato.

---

# 7. Classifiche calcolate

Percorso

```
data/storico/classifiche_calcolate/
```

Le classifiche NON vengono inserite manualmente.

Sono ricostruite automaticamente dallo storico risultati.

---

# 8. Input giornaliero

Percorso

```
data/input_partite/
```

Contiene esclusivamente le partite da analizzare.

Non rappresenta uno storico.

---

# 9. Output ranking

Percorso

```
data/output_ranking/
```

Ogni ranking contiene:

* score
* fascia
* componenti dello score
* motivazioni
* risultato (quando disponibile)
* esito

---

# 10. Principio fondamentale

Le statistiche ordinarie NON vengono salvate.

Saranno sempre calcolate leggendo lo storico.

Ad esempio:

* ultime 5
* ultime 10
* Over
* Under
* BTTS
* forma
* gol medi
* head-to-head

Questo elimina qualsiasi incoerenza.

---

# 11. Statistiche avanzate

Statistiche non ricostruibili (es. xG, tiri, corner, PPDA) potranno essere archiviate solo quando disponibili.

Non costituiscono un requisito obbligatorio.

---

# 12. Ranking Gap v1.3

Il Ranking Gap dovrà considerare contemporaneamente:

* posizione in classifica;
* numero di squadre del campionato;
* distanza reale in punti;
* punti per partita (PPG).

La distanza di posizione dovrà essere normalizzata sul numero di squadre.

La distanza in punti dovrà essere rapportata ai punti per partita per evitare che le prime giornate abbiano lo stesso peso delle ultime.

---

# 13. Workflow

1. Preparazione del CSV delle partite.
2. Generazione del ranking.
3. Aggiornamento dello storico.
4. Inserimento del risultato finale.
5. Aggiornamento automatico dell'esito.

---

# 14. Versionamento

Ogni modifica significativa incrementa:

```
MODEL_VERSION
```

Ogni modifica deve essere riportata nel CHANGELOG.

---

# 15. Benchmark

Il benchmark ufficiale del progetto viene costruito esclusivamente utilizzando lo storico raccolto.

Le metriche da monitorare comprendono:

* Accuracy Over 2.5
* Accuracy per fascia
* Accuracy per campionato
* Accuracy per nazione

---

# 16. Analytics (Roadmap)

Il software dovrà produrre automaticamente:

* accuracy_by_band
* accuracy_by_country
* accuracy_by_league
* score_distribution
* goal_distribution
* over15_analysis
* over25_analysis
* over35_analysis
* over45_analysis
* over55_analysis
* over65_analysis
* ko_alta

---

# 17. Goal Probability Engine

L'obiettivo finale è stimare la propensione complessiva ai gol.

Dal punteggio assegnato dal modello dovrà essere possibile stimare la probabilità di:

* Over 1.5
* Over 2.5
* Over 3.5
* Over 4.5
* Over 5.5
* Over 6.5

senza modificare il modello principale.

---

# 18. Regole di sviluppo

Ogni nuova feature deve:

* essere supportata dai dati;
* non aumentare inutilmente il lavoro manuale;
* mantenere la compatibilità con lo storico;
* essere facilmente reversibile.

Le modifiche al modello devono essere introdotte solo dopo un'analisi statistica su un numero significativo di partite concluse.

---

# 19. Ruolo dell'assistente

L'assistente deve comportarsi come un revisore tecnico.

Per ogni proposta deve valutare:

* vantaggi;
* svantaggi;
* impatto sull'architettura;
* rischio di overfitting;
* costo di manutenzione;
* beneficio statistico.

L'obiettivo è mantenere GioOver2.5 un progetto scientificamente rigoroso e facilmente evolvibile nel tempo.
nte

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