# GioOver2.5 — Manuale degli engine e della loro evoluzione

**Edizione 2 — 13 novembre 2026 · Guida tecnica e funzionale**

Questa guida serve a rispondere a quattro domande: **che cosa misura un engine? Perché è nato? Quali driver usa e con quali pesi? In che cosa è diverso da quello precedente?** È scritta per essere comprensibile anche senza conoscere il codice Python. Ogni regola numerica riportata è stata ricavata dalle implementazioni, non ricostruita dai nomi degli engine.

> **Principio fondamentale:** V3.1 non è necessariamente “migliore” di V3.0 e V2.5 non è una V2.4 con ulteriori modifiche. Le versioni sono una cronologia di esperimenti, **non una classifica di precisione**. Per scegliere il migliore occorrono risultati OK/KO verificati sullo stesso insieme di partite.

## Indice

1. [Come funziona una previsione](#1-come-funziona-una-previsione)
2. [Dizionario dei driver](#2-dizionario-dei-driver)
3. [Albero genealogico degli engine](#3-albero-genealogico-degli-engine)
4. [V1 e V1.3 — il modello originale](#4-v1-e-v13--il-modello-originale)
5. [V2.0 — la baseline V20](#5-v20--la-baseline-v20)
6. [V2.1 e V2.2 — il modello multidimensionale](#6-v21-e-v22--il-modello-multidimensionale)
7. [V2.3, V2.4 e V2.5 — tre esperimenti distinti](#7-v23-v24-e-v25--tre-esperimenti-distinti)
8. [V2.5.1 e V2.6 — prudenza e PROX](#8-v251-e-v26--prudenza-e-prox)
9. [V2.7 — selezione indipendente dalla fascia](#9-v27--selezione-indipendente-dalla-fascia)
10. [V3.0 e V3.1 — il modello a storico giovane](#10-v30-e-v31--il-modello-a-storico-giovane)
11. [Varianti V20, difensive e selettori](#11-varianti-v20-difensive-e-selettori)
12. [VG1 e derivati — il mercato BTTS](#12-vg1-e-derivati--il-mercato-btts)
13. [VEG90](#13-veg90)
14. [Esempi completi di confronto](#14-esempi-completi-di-confronto)
15. [Come verificare una previsione e aggiornare la guida](#15-come-verificare-una-previsione-e-aggiornare-la-guida)

---

## 1. Come funziona una previsione

Una partita, ad esempio **Squadra A – Squadra B**, viene associata a un campionato (`LeagueId`) e a una data effettiva di incontro (`MatchDate`). La pipeline legge le statistiche **precedenti** alla partita e le consegna agli engine. Ogni engine restituisce:

- **Score**: un numero calcolato da una formula o assegnato da una regola di selezione. **Non è una probabilità calibrata**: score 90 non significa automaticamente 90% di probabilità di Over 2.5.
- **Band**: la categoria di interesse, tipicamente `ALTA`, `MEDIA-ALTA`, `MEDIA`, `BASSA`, oppure una categoria contestuale (`PROX-ALTA`).
- **Reason**: il testo diagnostico che spiega i segnali attivati.
- **Driver**: contributi numerici delle singole statistiche, quando previsti dal modello.

### Un esempio elementare

Se una squadra ha realizzato 18 gol in 10 partite, **GF/gara = 1,80**. Se ha giocato 8 Over 2.5 nelle ultime 10, **Over25 L10 = 0,80**. Un engine può trasformare questi valori in punti usando pesi: `0,80 × 15 = 12`. Un altro engine può richiedere semplicemente `Over25 L5 ≥ 0,70` per accettare la partita.

**Due modi di ragionare diversi:**

1. **Scoring composito** (V1, V20, V21, V22): somma contributi di più driver. Un segnale forte può compensarne uno debole.
2. **Selettore a condizioni** (V27, V30, V31, VG1, VEG90): per ricevere una fascia elevata devono verificarsi condizioni precise. Un solo requisito mancante può escludere il segnale.

Alcuni selettori **mantengono lo score dell'engine base ma cambiano soltanto la fascia**. Questo è essenziale quando si leggono gli storici.

### Fasce: attenzione alle differenze

V1/V1.3/V20 usano quattro fasce: **ALTA ≥75**, **MEDIA-ALTA ≥60**, **MEDIA ≥45**, altrimenti BASSA. Gli scorer della famiglia V21/V22 usano `_band` con **ALTA ≥75**, **MEDIA ≥60**, altrimenti BASSA. Perciò **MEDIA-ALTA non significa sempre la stessa cosa in tutti gli engine**. Eventuali etichette di maturità (`IMM-`) o contestuali sono gestite anche dalla pipeline: non vanno confuse con lo scoring puro.

---

## 2. Dizionario dei driver

| Driver | Formula o significato | Perché può essere utile | Rischio interpretativo |
|---|---|---|---|
| **GF/gara** | Gol fatti / gare | Misura la produzione offensiva | Media alta su poche gare o contro avversari deboli |
| **GA/gara** | Gol subiti / gare | GA alto segnala difesa vulnerabile | Una difesa forte (GA basso) può ostacolare l'Over |
| **Over25 L5/L10** | Gare con almeno 3 gol / ultime 5 o 10 | Tendenza recente a risultati ricchi di gol | Campione ridotto, oscillazioni elevate |
| **Over25 FULL** | Over 2.5 / gare complessive | Tendenza stagionale più stabile | Può reagire lentamente a cambi di forma |
| **BTTS FULL/L5** | Gare in cui entrambe segnano / gare | Segnala partite aperte da entrambi i lati | Un 3–0 è Over ma non BTTS; un 1–1 è BTTS ma non Over |
| **PPG** | Punti / gare | Forza sportiva normalizzata per gare giocate | Non misura direttamente il numero di gol |
| **Gap PPG** | `abs(PPG casa − PPG ospite)` | Misura l'equilibrio delle squadre | Un match equilibrato può essere sia aperto sia tattico |
| **Position gap** | Differenza delle posizioni in classifica | Squilibrio di ranking | Posizioni poco confrontabili tra gironi |
| **Venue Over** | Over della squadra in casa / in trasferta | Distingue prestazioni nei due contesti | Campioni home/away più piccoli |
| **Min(X)** | `min(X casa, X ospite)` | Richiede che **entrambe** soddisfino un livello | Una squadra molto forte non compensa quella debole |
| **Maturity** | `min(gare casa, gare ospite)` | Controlla quanto è giovane lo storico | Non è un indicatore di qualità in sé |
| **Delta GF L5** | Media dei GF/gara L5 delle due squadre **meno** media GF/gara FULL | Misura l'accelerazione offensiva recente | Non indica direttamente i gol attesi |
| **ExpectedGoals** | Stima separata dei gol attesi per l'incontro | Usata come filtro sperimentale VEG90 | Non coincide necessariamente con gli xG ufficiali dei provider |

**FULL** indica il totale disponibile prima del match; **L5/L10** le ultime cinque/dieci partite precedenti. **GA L5 ≤1,20** significa una difesa che subisce mediamente al massimo 1,2 gol nelle ultime cinque. **GA L5 ≥2,20** significa invece una difesa che ne concede almeno 2,2.

### Che cosa significa normalizzare?

Le statistiche hanno unità diverse. Per combinarle in uno score si trasformano spesso in un numero fra 0 e 1: `clamp(valore / soglia, 0, 1)`. Per esempio, nella V20, **GF casa = 2,0** diventa `2,0 / 2,5 = 0,80`, quindi **20 punti** su un massimo di 25 per quel driver. Se GF fosse 3,0, il contributo resterebbe **25**, perché il valore viene limitato a 1.

---

## 3. Albero genealogico degli engine

Questa è la **dipendenza effettiva del codice**, distinta dall'ordine numerico:

```text
V1 ──(cambia formula del gap)──> V1.3

V2.0 / V20 (nuovo scorer autonomo)
  ├── V20def (penalità difesa recente)
  │     ├── V20defselect (solo promozioni selezionate)
  │     ├── V20defplus (ALTA originali + promozioni)
  │     ├── V20defplus_v2 (soglie 70/80/80)
  │     └── V20defplus_v3 (soglie 69/60/80)
  ├── V20select (MEDIA-ALTA confermate da V22 e V25)
  └── V20plus (ALTA originali + promozioni)

V2.1 (nuovo scorer multidimensionale)
  ├── V21dev (scorer sperimentale separato)
  └── V2.2 (scorer che riusa funzioni V21dev)
        ├── V2.3 (V22 - penalità per profilo chiuso)
        ├── V2.4 (V22 + bonus per profilo aperto)
        ├── V2.5 (V22 - penalità top di classifica)
        │     ├── V2.5.1 (micro-penalità su V25)
        │     ├── V2.5def (penalità difesa recente)
        │     └── V2.6 (score V25 + etichetta PROX)
        │           ├── V2.6def (penalità difesa recente)
        │           └── V2.7 (selettore attacco casa + GA L5 ospite)
        └── V2.2def (penalità difesa recente)

V3.0 (scorer autonomo: campione giovane)
V3.1 (scorer autonomo: nuova regola su campione giovane)
VG1  (scorer autonomo BTTS) ──> VG1.2 / VG1.3 / VG1.4 / VG2.2 / VG2.6
VEG90 (selettore autonomo ExpectedGoals + GA + Over L5)
```

**Nota:** V3.1 è una nuova implementazione che sviluppa l'idea di V3.0, ma non chiama la sua funzione. Analogamente, la cronologia V23→V24→V25 **non** equivale a `scoreV22 - penalitàV23 + bonusV24 - penalitàV25`: ogni scorer riparte da V22.

---

## 4. V1 e V1.3 — il modello originale

### V1: quale domanda si pone?

“Una squadra più forte incontra una squadra più debole: il divario e le caratteristiche offensive/difensive suggeriscono almeno tre gol?”

Il codice individua **squadra forte e squadra debole per posizione in classifica**, non necessariamente casa e trasferta. Quindi `strong_gf` è il GF della meglio classificata, non sempre il GF della squadra di casa.

**Composizione dello score V1** (pesi da `gioover25/config.py`):

| Componente | Peso massimo | Significato |
|---|---:|---|
| Gap classifica | 22 | Quanto sono lontane le posizioni |
| GF squadra forte | 20 | Quanto segna la meglio classificata |
| GA squadra debole | 20 | Quanto subisce la peggio classificata |
| GA squadra forte | 7 | Quanto è vulnerabile anche la forte |
| GF squadra debole | 7 | Quanto può contribuire la debole |
| Profilo L10 combinato | 10 | Over25 L10 35%, GF L10 45%, GA L10 20% per squadra |
| Real Over Index | 10 | Media Over25 L10 delle due squadre |
| Componente pseudo-casuale | **0** | Il valore è calcolato deterministicamente ma ha **peso nullo** |

La somma dei massimi attivi è **96**, non 100. Il codice contiene anche una riduzione del profilo L10 se **entrambe** segnano meno di 0,6 GF/gara nelle ultime dieci. Il gap classifica V1 ha correttivi per partite fra squadre di alta/bassa classifica.

### V1.3: che cosa cambia?

La novità **centrale** è il calcolo del gap. In V1 si parte dalla differenza di posizioni normalizzata; in V1.3 si combinano **35% gap posizioni + 65% gap PPG**.

```text
position_gap_ratio = abs(posizione_forte - posizione_debole) / (numero_squadre - 1)
ppg_gap_ratio      = clamp(abs(PPG_forte - PPG_debole) / 1,50)
ranking_gap_V13    = 0,35 × position_gap_ratio + 0,65 × ppg_gap_ratio
```

**Esempio illustrativo:** campionato a 20 squadre; posizioni 4ª e 9ª; PPG 1,80 e 1,50. Gap posizioni = `5/19 = 0,263`, gap PPG = `0,30/1,50 = 0,20`. V1.3 ottiene `0,35×0,263 + 0,65×0,20 = 0,222`, ossia **4,89 punti** del contributo ranking (peso 22).

**Perché serve:** due squadre vicine per posizione possono avere punti per gara molto diversi, e viceversa. V1.3 prova a rendere il gap meno dipendente dalla sola posizione.

**Cosa NON cambia:** pesi degli altri driver, soglie di fascia, profilo L10 e approccio forte/debole. **Limite:** V1.3 non è una stima di gol attesi.

**Sorgenti:** `engines/v1.py`, `engines/v13.py`, `config.py`.

---

## 5. V2.0 — la baseline V20

### L'idea nuova

V20 abbandona l'orientamento “squadra forte contro debole” come struttura dominante. Pone una domanda più mirata: **la squadra di casa segna abbastanza, la squadra ospite concede abbastanza e le due hanno una buona storia Over25 recente?**

La formula effettiva è:

```text
V20 =
    20 × RankingGapNormalizzato
  + 25 × clamp(GF_FULL_casa / 2,5)
  + 25 × clamp(GA_FULL_ospite / 2,5)
  + 15 × Over25_L10_casa
  + 15 × Over25_L10_ospite
```

Il ranking gap viene calcolato dal modulo `gioover25/ranking_gap.py`, quindi non va confuso automaticamente con `abs(position_gap)`.

| Driver | Massimo |
|---|---:|
| Ranking gap | 20 |
| Attacco casa | 25 |
| Difesa ospite vulnerabile | 25 |
| Over25 L10 casa | 15 |
| Over25 L10 ospite | 15 |
| **Totale** | **100** |

### Esempio di calcolo V20

Immaginiamo ranking gap normalizzato **0,50**, GF casa **2,00**, GA ospite **1,75**, Over25 L10 casa **0,80**, Over25 L10 ospite **0,70**.

| Driver | Calcolo | Punti |
|---|---|---:|
| Gap | 0,50 × 20 | 10,0 |
| GF casa | (2,00 / 2,5) × 25 | 20,0 |
| GA ospite | (1,75 / 2,5) × 25 | 17,5 |
| Over casa L10 | 0,80 × 15 | 12,0 |
| Over ospite L10 | 0,70 × 15 | 10,5 |
| **Score V20** | Somma | **70,0** |

Risultato: **MEDIA-ALTA** secondo le fasce V20. Per diventare ALTA occorrono almeno 75 punti.

### Cosa cambia rispetto a V1.3?

- **Casa/trasferta diventano strutturali**: non si riorganizzano le squadre in forte/debole.
- Si dà **metà del peso complessivo** alla coppia GF casa + GA ospite.
- L'Over25 L10 pesa **30 punti** complessivi, più dei 20 punti combinati dei due indicatori recenti in V1.3.
- Spariscono dalla formula diretta i driver GF squadra debole e GA squadra forte.

**Limite da conoscere:** una partita con attacco casa forte e difesa ospite debole può ottenere un punteggio alto anche se l'ospite segna poco. Questo spiega perché le versioni successive esplorano BTTS, attacco ospite e vulnerabilità difensiva di entrambe.

**Regola di progetto:** **V20 originale rimane invariato**. Le prove si fanno tramite engine distinti.

**Sorgente:** `scoring_v2.py`.

---

## 6. V2.1 e V2.2 — il modello multidimensionale

### V2.1: che cosa aggiunge a V20?

V21 passa da 5 a **10 contributi**. Non considera più soltanto l'attacco casa e la difesa ospite: valuta **entrambi gli attacchi, entrambe le difese, gli Over L10, gli Over nel contesto casa/trasferta e la frequenza BTTS**.

| Driver | V20 | V21 |
|---|---:|---:|
| Gap ranking | 20 | 8 |
| Attacco casa | 25 | 13 |
| Attacco ospite | — | 13 |
| Vulnerabilità difesa casa | — | 10 |
| Vulnerabilità difesa ospite | 25 | 14 |
| Over25 L10 casa | 15 | 12 |
| Over25 L10 ospite | 15 | 12 |
| Over25 casa **in casa** | — | 8 |
| Over25 ospite **in trasferta** | — | 8 |
| BTTS medio FULL | — | 12 |
| **Somma dei massimi** | **100** | **110** |

**Attenzione:** la somma dei pesi V21 è **110**; il codice non divide per 110 per riportare automaticamente a 100. Questo è un fatto importante per confrontare gli score tra versioni.

Per attacco e difesa V21 normalizza dividendo GF/GA per **2,2**. Il gap usa la differenza di posizioni divisa per `numero_squadre - 1`. I driver venue sono la frequenza Over25 nelle gare interne/esterne pertinenti.

**Perché cambia:** un Over 2.5 può arrivare da un 2–1, un 1–2 o un 3–0. Il modello cerca più combinazioni di gol, invece di privilegiare unicamente la coppia attacco casa/difesa ospite.

### V2.2: non solo una nuova etichetta

V22 utilizza le funzioni del modulo sperimentale `scoring_v21dev.py`, quindi **non è semplicemente V21 con due pesi cambiati**. Rispetto alla composizione V21 visibile sopra, i pesi diventano:

| Driver | V21 | V22 | Differenza |
|---|---:|---:|---:|
| Gap | 8 | 6 | −2 |
| Attacco casa | 13 | 13 | 0 |
| Attacco ospite | 13 | 13 | 0 |
| Difesa casa vulnerabile | 10 | 8 | −2 |
| Difesa ospite vulnerabile | 14 | 10 | −4 |
| Over L10 casa | 12 | 12 | 0 |
| Over L10 ospite | 12 | 12 | 0 |
| Venue casa | 8 | 10 | +2 |
| Venue ospite | 8 | 10 | +2 |
| BTTS | 12 | 12 | 0 |
| **Somma** | **110** | **104** | **−6** |

**La scelta funzionale:** ridurre il peso del gap e della difesa debole, aumentando quello delle abitudini Over nel proprio campo. V22 aggiunge inoltre una `Reason` esplicita in **PRO** e **CONTRO**: ad esempio attacco ospite poco prolifico, trend Over non forte, venue debole, BTTS basso.

**Importante:** i CONTRO descritti nella `Reason` **non sono automaticamente penalità numeriche**. In V22 lo score è ancora una somma pesata; le penalità esplicite arrivano con V23/V25.

**Sorgenti:** `scoring_v21.py`, `scoring_v21dev.py`, `scoring_v22.py`.

---

## 7. V2.3, V2.4 e V2.5 — tre esperimenti distinti

Tutte e tre chiamano `calculate_score_v22` e **ripartono dal risultato V22**. Questo è il punto più importante della loro genealogia.

### V2.3 — punire i profili potenzialmente chiusi

Domanda: “V22 sta sopravvalutando una gara in cui l'ospite segna poco o la storia BTTS/Over è debole?”

| Condizione | Penalità |
|---|---:|
| GF FULL ospite <1,10 | −4 |
| BTTS FULL medio delle due <0,50 | −4 |
| Over25 FULL medio delle due <0,50 | −3 |
| Score **V22 ≥85** e GF ospite <1,10 | −4 aggiuntivi |
| Score **V22 ≥85** e BTTS medio <0,50 | −4 aggiuntivi |
| Score **V22 ≥90**, GF ospite <1,00 e BTTS medio <0,50 | −5 aggiuntivi |

Le penalità **si sommano**. Esempio: V22 = 87, ospite GF 0,90, BTTS 0,40, Over25 FULL medio 0,45. Si applicano −4−4−3−4−4 = **−19**, quindi **V23 = 68**. L'ultima penalità da −5 non scatta perché V22 è inferiore a 90. Il risultato viene riclassificato nella fascia corrispondente.

**Razionale:** un 1–0 o 2–0 può sembrare plausibile con una squadra favorita, ma non è Over 2.5. V23 cerca di intercettare quel rischio.

### V2.4 — premiare i profili aperti

V24 **non eredita le penalità V23**. Riparte da V22 e aggiunge:

| Condizione | Bonus |
|---|---:|
| BTTS FULL medio ≥0,60 | +5 |
| GF FULL ospite ≥1,30 | +4 |
| GA FULL casa ≥1,20 **e** GA FULL ospite ≥1,20 | +4 |
| GF FULL ospite ≥1,20 **e** BTTS medio ≥0,55 | +4 |

**Esempio:** V22 = 69; BTTS medio 0,65; GF ospite 1,40; GA casa 1,30; GA ospite 1,50. Scattano tutti i bonus: **69 + 5 + 4 + 4 + 4 = 86**. Lo score è limitato a un massimo di 100.

**Razionale:** valorizzare partite in cui entrambe possono contribuire al punteggio, non soltanto quelle in cui una difesa è fragile.

### V2.5 — prudenza nelle sfide equilibrate di vertice

V25 riparte **ancora da V22**, senza sommare V23 o V24. Cerca una situazione specifica: **due squadre vicine nelle prime cinque posizioni**, con una difesa molto solida della squadra meglio classificata.

Per essere una `close_top_match` servono **tutte** queste condizioni:

1. Entrambe nelle **prime 5**.
2. Differenza posizioni **≤2**.
3. Se hanno disputato un numero simile di gare (differenza ≤1): gap punti **≤4** **e** gap PPG **≤0,30**.
4. Se hanno disputato un numero diverso di gare (differenza >1): gap PPG **≤0,25**.

Solo allora si guarda il GA FULL della squadra meglio classificata:

| Condizione ulteriore | Penalità |
|---|---:|
| GA FULL della migliore <1,00 | −6 |
| GA FULL della migliore <0,80 | altri −3 |
| Score V22 ≥85 e GA FULL della migliore <1,00 | altri −3 |

**Esempio:** V22 = 88, due squadre 2ª e 3ª con PPG quasi uguali, GA della migliore 0,75. Le penalità sono −6−3−3 = **−12**: V25 = **76**. La partita resta ALTA, ma con margine ridotto.

**Razionale:** evitare di trattare automaticamente una sfida al vertice come molto favorevole all'Over quando una delle due difese è particolarmente solida.

### Sintesi delle tre filosofie

- **V23:** “Attenzione all'ospite sterile e allo storico povero di gol.”
- **V24:** “Premiamo le gare in cui gli indizi di apertura si rafforzano.”
- **V25:** “Attenzione alle sfide equilibrate tra squadre di vertice con difese solide.”

Non esiste nel codice una V25 che sommi tutti e tre gli approcci.

**Sorgenti:** `scoring_v23.py`, `scoring_v24.py`, `scoring_v25.py`.

---

## 8. V2.5.1 e V2.6 — prudenza e PROX

### V2.5.1 — piccoli correttivi a V25

V251 prende **V25** e sottrae micro-penalità:

| Situazione | Correzione |
|---|---:|
| Almeno una difesa con GA FULL <1,00, con entrambe ≥5 gare | −1 |
| Almeno una difesa con GA FULL <0,80, con entrambe ≥5 gare | **−2 al posto di −1** |
| Entrambe con PPG L5 ≤0,60 e almeno 5 gare recenti per ciascuna | −1 |
| Una squadra marcata `restart_not_ready` | −1 |
| Entrambe marcate `restart_not_ready` | −2 |
| **Limite massimo della somma** | **−4** |

Esempio: V25 = 78; difesa molto forte −2, forma recente bassa −1, una squadra in ripresa −1: **V251 = 74**, che scende dalla fascia ALTA.

**Precisazione importante:** la difesa qui è misurata con **GA FULL**, non GA L5. L5 viene invece usato per il PPG recente. La `Reason` include un blocco `V251_DIAGNOSTICS` che permette di ricostruire ogni correzione.

### V2.6 — stesso score V25, fascia diversa

V26 **non modifica neppure di un punto** il calcolo V25. Introduce `PROX`, un'informazione contestuale sull'equilibrio della partita:

```text
Se gare casa >= 10
e gare ospite >= 10
e abs(PPG casa - PPG ospite) <= 0,30:

    ALTA  -> PROX-ALTA
    MEDIA -> PROX-MEDIA
    BASSA -> BASSA
```

Esempio: V25 = 79 ALTA; 15 gare a testa; PPG 1,73 contro 1,60. V26 resta **score 79**, ma fascia **PROX-ALTA**.

**Non interpretare PROX-ALTA come “più forte di ALTA”**: è un'etichetta di contesto che richiede una validazione separata sugli esiti.

**Sorgenti:** `scoring_v251.py`, `engines/v26.py`.

---

## 9. V2.7 — selezione indipendente dalla fascia

V27 nasce per isolare un profilo preciso, indipendentemente da quanto V26 consideri alta la partita.

**Regola di selezione (entrambe obbligatorie):**

```text
HomeAttackScore >= 12,428
AwayGA_L5       >= 2,20
```

- `HomeAttackScore` è il **contributo numerico** del driver attacco casa restituito dallo scorer V25/V26, **non** il GF/gara grezzo.
- `AwayGA_L5` è la media dei gol subiti dall'ospite nelle ultime cinque, fornita alla funzione come parametro.
- Se entrambe vere, la fascia diventa **ALTA**; altrimenti **BASSA**.
- Lo **score numerico originario V26 rimane invariato**.

**Esempio:** score V26 64, HomeAttackScore 13,0, AwayGA L5 2,4: **V27 ALTA con score 64**. Questo non è un errore: la fascia è decisa dal selettore, non dalla soglia numerica standard.

**Perché nasce:** per verificare in isolamento se attacco casa e difesa ospite recente siano driver più discriminanti di un grande score composito.

**Sorgente:** `engines/v27.py`.

---

## 10. V3.0 e V3.1 — il modello a storico giovane

Questi engine **non** sono un V27 migliorato. Nascono da un'altra ipotesi: selezionare partite quando entrambe le squadre hanno uno storico **ancora giovane ma sufficiente** e mostrano tendenze offensive recenti.

### V3.0: la ripresa offensiva recente

Definizioni:

```text
Maturity       = min(gare_totali_casa, gare_totali_ospite)
MinOverL5      = min(Over25_L5_casa, Over25_L5_ospite)
AvgGFL5        = (GF_L5_casa + GF_L5_ospite) / 2
AvgGFFull      = (GF_FULL_casa + GF_FULL_ospite) / 2
DeltaGFL5      = AvgGFL5 - AvgGFFull
```

| Livello | Condizioni | Score assegnato |
|---|---|---:|
| **CORE** | Maturity 7–8, MinOverL5 ≥0,70, DeltaGFL5 ≥0,20 | 80 |
| **STRONG** | Tutto CORE e DeltaGFL5 ≥0,30 | 90 |
| **NO-SIGNAL** | Non soddisfa CORE | Score continuo di ranking, fino a 74 |

Lo score continuo per NO-SIGNAL pesa **15% maturity**, **40% Over L5**, **25% GF L5** e **20% delta GF**, con fattore finale 74. Serve a ordinare i non selezionati, non a creare una ALTA.

**Esempio:** gare totali 7 e 8; Over L5 0,80 e 0,80; AvgGFL5 2,10; AvgGFFull 1,75; Delta +0,35. Tutte le condizioni STRONG sono vere: **score 90**.

### V3.1: aggiunge un requisito offensivo stagionale

V31 mantiene Maturity 7–8 e MinOverL5 ≥0,70, ma aggiunge **MinGFFull ≥1,40**: **entrambe** devono avere una produzione offensiva stagionale sufficiente. Il delta recente diventa un **rafforzativo**, non un requisito del segnale BASE.

| Livello | Condizioni | Score |
|---|---|---:|
| **BASE** | Maturity 7–8; MinOverL5 ≥0,70; MinGFFull ≥1,40 | 80 |
| **BOOST** | Tutto BASE e DeltaGFL5 ≥0,20 | 85 |
| **STRONG** | Tutto BASE e DeltaGFL5 ≥0,30 | 90 |
| **NO-SIGNAL** | BASE non soddisfatto | Score continuo fino a 74 |

Lo score continuo dei non selezionati pesa **15% maturity**, **40% Over L5**, **30% MinGFFull**, **15% delta GF**.

### Il confronto decisivo V30 vs V31

**Caso A:** Maturity 7, MinOverL5 0,80, DeltaGFL5 +0,35, ma una squadra segna soltanto 1,10 GF FULL. **V30 STRONG (90)**; **V31 NO-SIGNAL**, perché MinGFFull <1,40.

**Caso B:** Maturity 8, MinOverL5 0,80, MinGFFull 1,60, ma DeltaGFL5 +0,05. **V30 NO-SIGNAL**; **V31 BASE (80)**, perché il delta positivo non è obbligatorio per il BASE.

**Conclusione:** V31 **non è un sottoinsieme** di V30. Le due selezioni possono differire in entrambe le direzioni.

**Sorgenti:** `scoring_v30.py`, `scoring_v31.py`.

---

## 11. Varianti V20, difensive e selettori

### Perché esistono?

Per provare ipotesi senza alterare gli engine originali. Alcune varianti **sottraggono punti**, altre **promuovono una fascia** e altre **mostrano soltanto le selezioni sperimentali**.

### V20select e V20plus: stessa regola, due usi

Una partita è candidata se:

1. V20 la mette in **MEDIA-ALTA**;
2. score V20 **≥71**;
3. V22 la mette in **ALTA**;
4. V25 la mette in **ALTA**.

**V20select** mostra come ALTA **solo** le candidate, impostando score 0 e BASSA per tutte le altre. Serve a misurare il segmento promosso senza mescolarlo alle ALTA originali.

**V20plus** conserva tutte le ALTA originali V20 **e aggiunge** le candidate, promuovendone la fascia. Lo score numerico V20 non cambia per una promozione.

**Esempio:** V20 score 72 MEDIA-ALTA; V22 ALTA; V25 ALTA. V20select = **ALTA 72**; V20plus = **ALTA 72**; V20 originale = **MEDIA-ALTA 72**.

### Le penalità difensive

| Engine | Base | Difesa controllata | Soglia | Penalità |
|---|---|---|---:|---:|
| **V20def** | V20 | Almeno una delle due, GA L5 | ≤1,60 | −3 |
| **V22def** | V22 | Solo ospite, GA L5 | ≤1,60 | −13 |
| **V25def** | V25 | Solo ospite, GA L5 | ≤1,60 | −13 |
| **V26def** | V26 | Almeno una delle due, GA L5 | ≤1,20 | −14 |

**Perché soglie diverse?** Sono esperimenti separati. Non esiste un parametro universale `strong_defense` che renda intercambiabili queste varianti. Il driver GA L5 deve essere disponibile; se manca non si deve inventare un valore.

### V20defselect e V20defplus

Sono l'equivalente difensivo della coppia V20select/V20plus:

- Base **V20def**, non V20.
- Candidate: V20def **MEDIA-ALTA** con score **≥71**, e **V22def ALTA** e **V25def ALTA**.
- **V20defselect** isola soltanto le promozioni.
- **V20defplus** mantiene le ALTA V20def e aggiunge le promozioni.

### V20defplus_v2 e V20defplus_v3

Entrambe preservano le ALTA native V20def, ma cambiano il test numerico sulle MEDIA-ALTA:

| Variante | V20def | V22def | V25def |
|---|---:|---:|---:|
| **V20defplus_v2** | ≥70 | ≥80 | ≥80 |
| **V20defplus_v3** | ≥69 | ≥60 | ≥80 |

**Esempio:** V20def 69,5 MEDIA-ALTA; V22def 75; V25def 85. **V3 promuove**, **V2 non promuove**. Non significa che V3 sia migliore: è meno restrittiva su due soglie e va valutata sul tasso OK/KO e sulla numerosità.

### V21dev

V21dev è un'implementazione sperimentale separata (`scoring_v21dev.py`). Ha un ruolo tecnico importante perché **V22 riusa le sue funzioni ausiliarie e il suo tipo di risultato**. Non va trattato come una sostituzione automatica della V21 ufficiale.

**Sorgenti:** `engines/v20*.py`, `engines/v22def.py`, `engines/v25def.py`, `engines/v26def.py`, `scoring_v21dev.py`.

---

## 12. VG1 e derivati — il mercato BTTS

### Una differenza fondamentale: il mercato

**VG1 prevede GOAL/BTTS**: entrambe le squadre devono segnare almeno un gol. Un **1–1 è OK BTTS** ma **KO Over 2.5**. Un **3–0 è OK Over 2.5** ma **KO BTTS**. Perciò le statistiche di VG1 e degli engine Over non vanno sommate o confrontate senza distinguere il mercato.

### Come funziona VG1

```text
MinBTTSFull   = min(BTTS_FULL_casa, BTTS_FULL_ospite)
MinGFL5       = min(GF_L5_casa, GF_L5_ospite)
GapPPGFull    = abs(PPG_casa - PPG_ospite)
DeltaBTTSL5   = media(BTTS_L5) - media(BTTS_FULL)
MinOverFull   = min(Over25_FULL_casa, Over25_FULL_ospite)
```

| Livello | Requisiti cumulativi | Score |
|---|---|---:|
| **BASE** | MinBTTSFull ≥0,70; MinGFL5 ≥1,80 | 76 |
| **ALTA** | BASE + GapPPGFull ≤1,00 + DeltaBTTSL5 ≥0 | 85 |
| **TOP** | ALTA + MinOverFull ≥0,80 | 92 |
| **NO-SIGNAL** | Nessuna delle precedenti | Score continuo fino a 74 |

Lo score continuo per i non selezionati combina **40% BTTS FULL minimo, 35% GF L5 minimo, 10% gap PPG, 10% delta BTTS, 5% Over FULL minimo**. Questo serve all'ordinamento, non sostituisce le condizioni BASE/ALTA/TOP.

**Esempio:** MinBTTSFull 0,75; MinGFL5 2,00; GapPPG 0,60; DeltaBTTS +0,10; MinOverFull 0,65. È **ALTA score 85**, ma non TOP perché MinOverFull è inferiore a 0,80.

**VG1 originale è congelato: nessuna variante deve modificarne la formula.**

### Varianti BTTS: che cosa selezionano esattamente?

| Engine | Regola | Differenza rispetto a VG1 |
|---|---|---|
| **VG1.2** | `65 ≤ score VG1 < 70` e fascia originale non ALTA | Isola una fascia di score più basso |
| **VG1.3** | `68 ≤ score VG1 < 72` e fascia originale non ALTA | Finestra più alta e stretta |
| **VG1.4** | `65 ≤ score VG1 < 72` e fascia originale non ALTA | Unisce le due finestre parzialmente sovrapposte |
| **VG2.2** | VG1 originale ALTA e **MinGFL5 >2,2** | Sottoinsieme ad alta produzione offensiva recente |
| **VG2.6** | VG1 originale ALTA e **MinGFL5 >2,6** | Sottoinsieme ancora più selettivo |

Le varianti mantengono lo score numerico originale e riclassificano la fascia per identificare il segmento. In **VG2.2 e VG2.6** il confronto nel codice è **strettamente `>`**, non `≥`.

**Maturità del campione:** la pipeline può aggiungere etichette `IMM-` quando manca il requisito di cinque gare per squadra; questa classificazione operativa va documentata separatamente dal cuore immutato di VG1.

**Sorgenti:** `scoring_vg1.py`, `engines/vg1.py`, `engines/vg12.py`, `vg13.py`, `vg14.py`, `vg22.py`, `vg26.py`.

---

## 13. VEG90

VEG90 è un **selettore sperimentale Over 2.5**, non un aggiornamento di V30/V31 e non un engine BTTS.

Richiede **contemporaneamente**:

1. **ExpectedGoals ≥5,0**;
2. **MinGA L5 ≥1,2**: entrambe le squadre hanno subito almeno 1,2 gol/gara nelle ultime cinque;
3. **MinOver25 L5 ≥0,80**: entrambe hanno una frequenza Over25 L5 almeno pari a 0,80.

Se tutti i requisiti sono veri: **score 90, fascia ALTA**. Altrimenti: **score 0, fascia BASSA**.

**Esempio:** ExpectedGoals 5,2; GA L5 casa 1,4; GA L5 ospite 1,8; Over25 L5 casa 0,80 e ospite 1,00. Tutti i test passano: VEG90 seleziona.

**Attenzione:** il numero 90 nel nome **non garantisce il 90% di precisione**. Per valutare l'obiettivo occorrono esiti reali, numerosità sufficiente e test fuori campione.

**Sorgente:** `engines/veg90.py`.

---

## 14. Esempi completi di confronto

Gli esempi seguenti sono **didattici**, non partite reali; servono a mostrare come due engine possano classificare diversamente lo stesso incontro.

### Esempio A — V20 ALTA, V20def non ALTA

- V20 = **76** → ALTA.
- GA L5 casa = 1,40; GA L5 ospite = 2,10.
- V20def trova **almeno una difesa ≤1,60** e sottrae 3.
- **V20def = 73 → MEDIA-ALTA**.

**Lezione:** V20def non aggiunge partite: prova a scartare quelle in cui una difesa recente appare solida.

### Esempio B — V25 e V26 stesso score, fascia diversa

- V25 = **80** → ALTA.
- Gare giocate: 14 e 15; PPG 1,65 e 1,45.
- V26 = **80 → PROX-ALTA**.

**Lezione:** non bisogna confrontare soltanto lo score: la fascia è parte del risultato.

### Esempio C — V27 seleziona una MEDIA

- Score V26 = **63**, HomeAttackScore = **13,1**, AwayGA L5 = **2,5**.
- V27 = **ALTA con score 63**.

**Lezione:** V27 è un filtro indipendente dalla soglia score 75.

### Esempio D — V30 e V31 divergono

- Maturity = 7, MinOverL5 = 0,80, DeltaGFL5 = +0,32, MinGFFull = 1,20.
- **V30 STRONG (90)** perché supera i suoi requisiti.
- **V31 NO-SIGNAL** perché una squadra non raggiunge 1,40 GF FULL.

**Lezione:** “versione successiva” non significa che tutte le vecchie ALTA siano mantenute.

### Esempio E — stesso risultato, mercati differenti

| Finale | Over 2.5 | BTTS |
|---|---|---|
| 3–0 | OK | KO |
| 2–1 | OK | OK |
| 1–1 | KO | OK |
| 0–0 | KO | KO |

**Lezione:** VG1 va valutato sul mercato BTTS. Un eventuale Over 2.5 nelle ALTA VG1 è soltanto una statistica secondaria.

---

## 15. Come verificare una previsione e aggiornare la guida

### Lettura di una riga ranking

1. Identificare la partita con **`LeagueId + MatchDate + Home + Away`**; `PredictionDate` non sostituisce `MatchDate`.
2. Leggere **`AlgorithmVersion`** per sapere quale codice ha generato lo score.
3. Leggere **`Score`**, **`Band`** e **`Reason`**: alcune varianti cambiano solo la fascia.
4. Confrontare i driver esposti con **la formula specifica** dell'engine; un campo zero può essere semplicemente un campo legacy non usato da un selettore.
5. Controllare che le statistiche siano **precedenti** alla partita e che il campionato/girone sia quello giusto.
6. Per misurare l'efficacia usare solo esiti **OK/KO**, non SCHEDULED o risultati mancanti. Confrontare engine sul **set comune di partite** e, quando utile, separare leghe australiane e fasce.
7. Per VG1 valutare prima **BTTS**, per gli altri Over 2.5 salvo esplicite eccezioni.

### Dove leggere il codice

| Obiettivo | File |
|---|---|
| Elenco engine e caricamento | `gioover25/engines/factory.py` |
| Regola particolare di una variante | `gioover25/engines/<nome>.py` |
| Formula V1/V1.3 | `gioover25/engines/v1.py`, `v13.py`, `gioover25/config.py` |
| Formula V20 | `gioover25/scoring_v2.py`, `gioover25/ranking_gap.py` |
| Formule V21–V25 | `gioover25/scoring_v21.py` … `scoring_v25.py` |
| Formula V251 | `gioover25/scoring_v251.py` |
| Selettori V30/V31 | `gioover25/scoring_v30.py`, `scoring_v31.py` |
| Formula BTTS | `gioover25/scoring_vg1.py` |
| Struttura gironi e mappe | `docs/maps/` |
| Ranking e storico risultati | `data/output_ranking/`, `data/storico/ranking/` |

### Regola editoriale per ogni futuro engine

Documentare sempre **(a)** mercato, **(b)** base esatta, **(c)** driver nuovi/rimossi, **(d)** formula e pesi, **(e)** soglie con operatori `<`, `<=`, `>`, `>=`, **(f)** cosa cambia tra score e fascia, **(g)** esempio di una partita che viene promossa/scartata, **(h)** stato sperimentale e risultati misurati separatamente.

### Limiti della documentazione

Questa guida descrive il **codice attuale**, non pretende di ricostruire tutte le motivazioni storiche originali degli esperimenti. Quando una motivazione non è esplicitata nei commenti, viene presentata come **interpretazione funzionale** e non come prova di efficacia. Le soglie dei selettori sono condizioni operative, **non probabilità**. Per stabilire quale engine sia migliore servono backtest riproducibili e dati verificati.

---

**Stato:** manuale di riferimento per il branch `v2-dev`. Modificare questa guida quando cambia un engine; **non modificare V20 o VG1 originali per aggiornare la documentazione**.
