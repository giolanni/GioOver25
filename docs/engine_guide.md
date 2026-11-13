# GioOver2.5 — Guida evolutiva degli engine

> Aggiornata al 13 novembre 2026. Fonte: implementazioni `gioover25/engines/`, `gioover25/scoring_*.py` e `engines/factory.py`. La guida descrive **differenze di codice**, non afferma che una versione più recente sia statisticamente migliore. Le varianti non sono una sequenza lineare.

## Come leggere i driver

- **GF / GA**: gol fatti / subiti medi per partita; **L5 / L10**: ultime 5 / 10 gare precedenti; **FULL**: storico complessivo.
- **Over25**: quota di gare con almeno 3 gol; **BTTS**: entrambe le squadre a segno.
- **PPG**: punti per partita; **gap PPG**: differenza fra le due squadre.
- **Home/Away**, **venue**: rendimento in casa / trasferta.
- **Score**: indice calcolato dall'engine; **Band**: fascia assegnata. Una variante può modificare solo la fascia senza cambiare lo score.
- **Min**: minimo fra i valori delle due squadre. **Maturity**: numero minimo di partite disponibili fra le squadre.
- Gli engine possono usare driver diversi pur restituendo colonne di output con gli stessi nomi. Verificare sempre il file `scoring_*.py`.

## Evoluzione principale: V1 → V3.1

| Versione | Base | Novità rispetto alla precedente | Driver / effetto |
|---|---|---|---|
| **V1** (`v1`) | Origine | Primo modello composito Over 2.5 | Gap di classifica, GF squadra forte, GA squadra debole, profilo L10 (Over25/GF/GA), fattori di campo e componente pseudo-casuale deterministica; soglie ALTA ≥75, MEDIA-ALTA ≥60, MEDIA ≥45 |
| **V1.3** (`v13`) | V1 | Riformula il driver di squilibrio | Gap di posizione **35%** + gap PPG **65%** (normalizzato su 1,50), anziché la sola distanza in classifica con correttivi top/bottom. Mantiene l'approccio composito |
| **V2.0** (`v20`) | Nuovo scoring V2 | Passa a `scoring_v2.calculate_score_v2` | Componenti esplicite di ranking gap, attacco casa, attacco ospite, vulnerabilità difensiva casa/ospite e Over25 L10 di entrambe (15 punti ciascuna); V20 è una baseline indipendente e congelata |
| **V2.1** (`v21`) | Nuovo scoring V21 | Introduce una composizione più ricca e normalizzata | `_attack_score`, `_defense_weakness_score`, `_last10_over_score`, `_venue_over_score`, `_btts_score`; L10 Over25 pesa 12 punti per squadra; non è un semplice incremento aritmetico di V20 |
| **V2.2** (`v22`) | V21 | Rielabora il modello V21 | Mantiene driver attacco/difesa, Over25 L10, venue e BTTS, con logica di score/ragioni propria in `scoring_v22.py`. Non interpretare V22 come un bonus fisso a V21 |
| **V2.3** (`v23`) | V22 | Introduce **penalità contestuali** | Sottrae penalità di **3–5 punti** per combinazioni sfavorevoli di metriche di gol/Over e profili delle squadre; riduce le valutazioni di incontri a rischio |
| **V2.4** (`v24`) | **V22** (ramo parallelo a V23) | Aggiunge **bonus di apertura della partita** | +5 se BTTS FULL medio ≥0,60; +4 se GF FULL ospite ≥1,30; +4 se entrambe GA FULL ≥1,20; +4 se GF ospite ≥1,20 e BTTS medio ≥0,55; score massimo 100 |
| **V2.5** (`v25`) | **V22** (non V24) | Penalizza sfide equilibrate al vertice con difesa forte | Entrambe top 5, gap posizioni ≤2; gap punti ≤4 e PPG ≤0,30 se gare giocate simili, altrimenti gap PPG ≤0,25. Con GA FULL della migliore <1,00: −6; se <0,80: altri −3; se score base ≥85: altri −3 |
| **V2.5.1** (`v251`) | V25 | Variante sperimentale di calibrazione | Valuta difese forti con GA recente (soglie **1,00** e **0,80**) e PPG L5 basso per entrambe (≤ **0,60**); correzione negativa massima **4 punti** |
| **V2.6** (`v26`) | V25, **non V2.5.1** | Aggiunge la classificazione **PROX** | **Score identico a V25**; se entrambe hanno ≥10 gare e gap PPG ≤0,30, ALTA→PROX-ALTA e MEDIA→PROX-MEDIA. La novità è nella fascia, non nello score |
| **V2.7** (`v27`) | V26 | Selettore sperimentale Over25 | Seleziona quando **HomeAttackScore ≥12,428** e **Away GA L5 ≥2,20**; non dipende dalla fascia originaria. V26 serve a preservare driver e output |
| **V3.0** (`v30`) | Nuova famiglia | Selezione per **storico giovane** | Maturity fra **7 e 8**, minimo Over25 L5 ≥**0,70**, delta GF L5 ≥**0,20** (forte ≥0,30); score di ranking dedicato, soglie di selezione 80/90 |
| **V3.1** (`v31`) | V30 | Raffina la selezione con produzione offensiva storica | Maturity 7–8, minimo Over25 L5 ≥0,70, **GF FULL minimo ≥1,40**, delta GF L5 ≥0,20/0,30 per livelli di selezione; soglie score 80/85/90; ripesa il ranking (Over 40%, GF 30%, delta 15%, maturity 15%) |

### Interpretazione delle transizioni

**V1 → V1.3.** Il salto più riconoscibile è l'inserimento esplicito della distanza in **punti per partita** nel ranking gap. Il gap di posizione resta, ma perde la centralità della V1. Le due versioni non devono essere confrontate come se avessero lo stesso score.

**V1.3 → V2.0.** V20 sostituisce la logica V1 con una composizione più esplicita dei driver offensivi/difensivi e della frequenza Over25 nelle ultime dieci. **V20 originale non va modificato**: ogni esperimento è implementato in un engine distinto.

**V2.0 → V2.1 → V2.2.** Evolvono i driver di contesto: forma Over25 L10, venue, BTTS, attacco e vulnerabilità difensiva. La differenza va letta nel codice dei rispettivi scorer, non soltanto nei valori numerici finali.

**V2.2 → V2.3 / V2.4 / V2.5.** Attenzione alla genealogia: **V23, V24 e V25 ripartono tutti dallo scorer V22**, non applicano le modifiche in cascata. V23 sottrae penalità (GF FULL ospite <1,10: −4; BTTS FULL medio <0,50: −4; Over25 FULL medio <0,50: −3; ulteriori −4/−4 per score V22 ≥85 e −5 se score ≥90 con GF ospite <1,00 e BTTS <0,50). V24 applica bonus di apertura; V25 penalizza il rischio di sfide equilibrate al vertice. Sono tre esperimenti distinti sulla stessa base.

**V2.5 → V2.5.1 / V2.6.** Sono **due rami diversi**: V2.5.1 modifica lo score con controlli difensivi; V2.6 conserva esattamente lo score V2.5 e segnala la prossimità di PPG con PROX.

**V2.7 → V3.0 → V3.1.** V2.7 è un filtro basato su attacco casa e GA recente ospite; V3.0/V3.1 introducono una famiglia di selettori per campioni giovani, con maturity e frequenza Over L5. Non sono semplici aggiornamenti del filtro V2.7.

## Varianti parallele: famiglia V20

| Engine | Differenza dalla base | Regola / driver |
|---|---|---|
| `v20select` | Selezione pura da V20 | MEDIA-ALTA V20, score ≥71 e doppia conferma ALTA V22 + V25; il resto non è selezionato |
| `v20plus` | Estensione di V20 | Mantiene le ALTA V20 e aggiunge il segmento promosso da `v20select` |
| `v20def` | Penalizzazione difensiva | Se almeno una squadra ha **GA L5 ≤1,60**, sottrae **3** punti a V20 |
| `v20defselect` | Selezione pura da V20def | MEDIA-ALTA V20def, score ≥71 e conferma ALTA V22def + V25def |
| `v20defplus` | Estensione di V20def | ALTA V20def più il segmento selezionato da V20defselect |
| `v20defplus_v2` | Seconda variante della promozione | Esperimento distinto: consultare le condizioni congelate nel modulo omonimo |
| `v20defplus_v3` | Promozione a soglie numeriche | Mantiene ALTA V20def; promuove MEDIA-ALTA se **V20def ≥69**, **V22def ≥60**, **V25def ≥80** |

### Altre varianti difensive e sperimentali

- **V21dev**: scoring sperimentale separato in `scoring_v21dev.py`; non sovrascrive V21.
- **V22def**: V22 meno **13 punti** se la difesa ospite ha **GA L5 ≤1,60**.
- **V25def**: V25 meno **13 punti** con la stessa condizione sulla difesa ospite.
- **V26def**: V26 meno **14 punti** se almeno una difesa ha **GA L5 ≤1,20**; conserva la logica di fascia PROX di V26.
- Le varianti `def` hanno regole **differenti**, non una penalità comune: confrontare sempre soglia, squadra coinvolta e punti sottratti.

## Famiglia GOAL/BTTS — indipendente dagli Over25

Il mercato principale di **VG1** è **BTTS**, non Over 2.5. Il modello originale `scoring_vg1.py` utilizza fra l'altro BTTS FULL, GF L5, gap PPG FULL e Over25 FULL per i livelli di selezione. Parametri di riferimento nel codice: `MIN_BTTS_FULL=0.70`, `MIN_GF_L5=1.80`, `MAX_PPG_GAP_FULL=1.00`, `MIN_OVER_FULL_TOP=0.80`. **VG1 originale è congelato**.

| Variante | Cosa cambia rispetto a VG1 |
|---|---|
| **VG1.2** | Promuove esclusivamente score **65 ≤ score < 70**, escludendo le ALTA native |
| **VG1.3** | Promuove esclusivamente **68 ≤ score < 72**, escludendo le ALTA native |
| **VG1.4** | Promuove esclusivamente **65 ≤ score < 72**, escludendo le ALTA native |
| **VG2.2** | Seleziona solo ALTA native VG1 con **min(GF L5) > 2,2** |
| **VG2.6** | Seleziona solo ALTA native VG1 con **min(GF L5) > 2,6** |

**Attenzione:** nei moduli `vg22.py` e `vg26.py` l'operatore implementato è **strettamente >**, non ≥. Il nome dell'engine non implica una modifica dello scoring originale VG1.

## VEG90 — selettore indipendente

Regola congelata in `engines/veg90.py`: **ExpectedGoals ≥5,0**, **min(GA L5) ≥1,2**, **min(Over25 L5) ≥0,80**. Se selezionato, score 90, altrimenti 0. Il nome VEG90 indica l'obiettivo sperimentale, **non** una percentuale di successo garantita.

## Dove verificare i dettagli e come mantenere questa guida

1. **Registrazione e famiglie**: `gioover25/engines/factory.py`.
2. **Wrapper e soglie di selezione**: `gioover25/engines/<engine>.py`.
3. **Formule complete dei driver**: `gioover25/scoring_v2.py`, `scoring_v21.py`, …, `scoring_v31.py`, `scoring_vg1.py`.
4. **Significato delle fasce**: il relativo scorer e la pipeline `rank_matches_v2`.
5. **Risultati reali**: storici ranking, usando solo OK/KO, MatchDate e campione comune quando si confrontano engine.

Quando nasce una variante, documentare: **base esatta, driver aggiunti/rimossi, formula, soglie e inclusività, effetto su score/band, dipendenze, motivazione, stato sperimentale**. Non dedurre il miglioramento dalla numerazione.
