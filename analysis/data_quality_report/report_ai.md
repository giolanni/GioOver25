# GioOver2.5 - Data Quality Report

Report diagnostico READ-ONLY. Le anomalie euristiche non implicano automaticamente dati errati.

## Riepilogo

- Modalità: **full**
- Classifiche analizzate: **211** (3535 squadre/righe)
- File risultati analizzati: **210** (16441 partite)
- Righe Laboratory analizzate: **9996**
- CRITICAL: **58**
- WARNING: **1661**
- INFO: **50**

## Priorità per analisi IA

Analizzare prima i CRITICAL. Prima di bonificare verificare sempre il formato reale della competizione e lo storico sorgente. WARNING/INFO possono essere legittimi (rinvii, campionati dispari, formati speciali).

## CRITICAL (58)

### CRITICAL-001 · LAB_SELF_MATCH · Finland_Kolmonen_Eastern_Group1 | 2026-08-21 | SAPA - SAPA
- Area: `laboratory`
- Dettaglio: Home e Away coincidono.
- Sorgente: `analysis\laboratory\data\01_matches.csv:4360`

### CRITICAL-002 · LAB_SELF_MATCH · Finland_Kolmonen_Eastern_Group1 | 2026-08-21 | SAPA - SAPA
- Area: `laboratory`
- Dettaglio: Home e Away coincidono.
- Sorgente: `analysis\laboratory\data\01_matches.csv:4589`

### CRITICAL-003 · ST_PLAYED_SPREAD · Austria_Regionalliga_West
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: Marchfeld, Wiener Viktoria, Traiskirchen, Wienerberger, Mattersburg SV 2020, SV Donau; max: Hohenems, Dornbirn, SC Imst, Schwaz, Kitzbuhel, SK St. Johann, Tirol (Am), Fugen, Reichenau, Rothis, Kufstein, Lochau, Altach U21, Wolfurt, Lauterach, FC Lustenau.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Regionalliga_West.csv`

### CRITICAL-004 · ST_PLAYED_SPREAD · Belarus_PershayaLiga
- Area: `standings`
- Dettaglio: Played min=1, max=24, delta=23; min: Arsenal Dzerzhinsk, FC Baranovichi, Gomel, Slavia Mozyr; max: Niva Dolbizno, Slutsk, Lida, SKA-1938, Molodechno, FC Slonim, BumProm Gomel, Volna Pinsk, Soligorsk, Ostrovets, Din. Minsk 2, Minsk 2, Smorgon, Orsha, Uni X Labs, Gomel 2, BATE 2, Osipovichi.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Belarus_PershayaLiga.csv`

### CRITICAL-005 · ST_PLAYED_SPREAD · Belarus_VysshayaLiga
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Torpedo Zhodino, BATE Borisov, Neman Grodno, FC Baranovichi, Belshina Bobruisk; max: Gomel, FC Minsk, Arsenal Dzerzhinsk.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Belarus_VysshayaLiga.csv`

### CRITICAL-006 · ST_PLAYED_SPREAD · Bulgaria_ParvaLiga
- Area: `standings`
- Dettaglio: Played min=1, max=10, delta=9; min: Levski Sofia, Arda Kardzhali, PFC Lokomotiv Sofia 1929, Ludogorets Razgrad, Lokomotiv Plovdiv; max: CSKA 1948 Sofia, Botev Plovdiv, Spartak Varna, Botev Vratsa, Dunav Ruse.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ParvaLiga.csv`

### CRITICAL-007 · ST_ALIAS_SUSPECTED · Estonia_Esiliiga
- Area: `standings`
- Dettaglio: Più nomi risolvono alla stessa identità canonica: Flora Tallinn U21 / Flora U21.
- Verifica suggerita: Consolidare tramite team_name_dictionary.csv e rigenerare classifica/Laboratory.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_Esiliiga.csv`

### CRITICAL-008 · ST_PLAYED_SPREAD · Estonia_Esiliiga
- Area: `standings`
- Dettaglio: Played min=1, max=29, delta=28; min: Flora Tallinn U21, Nomme United U21; max: Tartu Welco, Flora U21, FC Tallinn.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_Esiliiga.csv`

### CRITICAL-009 · ST_PLAYED_SPREAD · Estonia_Meistriliiga
- Area: `standings`
- Dettaglio: Played min=2, max=29, delta=27; min: FC Kuressaare; max: Parnu JK Vaprus.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_Meistriliiga.csv`

### CRITICAL-010 · ST_PLAYED_SPREAD · Finland_Kolmonen_Eastern_Group2
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: SC Zulimanit; max: Kings, Jippo-J/Punamusta, Ylämyllyn Yllätys, KuPS/Akatemia 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Eastern_Group2.csv`

### CRITICAL-011 · ST_PLAYED_SPREAD · Finland_Kolmonen_Eastern_Group3
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Mikkelin Pallo-Kissat, Kotajärven Pallo; max: LAUTP.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Eastern_Group3.csv`

### CRITICAL-012 · ST_PLAYED_SPREAD · Finland_Kolmonen_Southern_Group1
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Malmin Palloseura, Lohjan Pallo; max: PPJ/Ruoholahti, EPS Reservi, HooGee.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Southern_Group1.csv`

### CRITICAL-013 · ST_PLAYED_SPREAD · Finland_Kolmonen_Southern_Group2
- Area: `standings`
- Dettaglio: Played min=1, max=19, delta=18; min: MPS/Atletico Malmi; max: TiPS, PPJ/Lauttasaari, Valtti, Töölön Taisto, HPS/2, Kontu, PPS.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Southern_Group2.csv`

### CRITICAL-014 · ST_ALIAS_SUSPECTED · Finland_Ykkosliiga
- Area: `standings`
- Dettaglio: Più nomi risolvono alla stessa identità canonica: JIPPO / Jippo.
- Verifica suggerita: Consolidare tramite team_name_dictionary.csv e rigenerare classifica/Laboratory.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Ykkosliiga.csv`

### CRITICAL-015 · ST_DUP_TEAM · Finland_Ykkosliiga
- Area: `standings`
- Dettaglio: Squadre duplicate: jippo
- Verifica suggerita: Verificare alias/normalizzazione nomi squadra.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Ykkosliiga.csv`

### CRITICAL-016 · ST_PLAYED_SPREAD · Finland_Ykkosliiga
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: JIPPO, PK-35 Helsinki, Mikkelin Palloilijat, EIF; max: KTP, Jippo, Ekenas, Klubi 04, KaPa.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Ykkosliiga.csv`

### CRITICAL-017 · ST_PLAYED_SPREAD · Germany_3Liga
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: Viktoria Colonia; max: Meppen.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Germany_3Liga.csv`

### CRITICAL-018 · ST_ALIAS_SUSPECTED · Germany_Oberliga_BadenWurttemberg
- Area: `standings`
- Dettaglio: Più nomi risolvono alla stessa identità canonica: 1. FC Muhlhausen / 1\. FC Muhlhausen.
- Verifica suggerita: Consolidare tramite team_name_dictionary.csv e rigenerare classifica/Laboratory.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_BadenWurttemberg.csv`

### CRITICAL-019 · ST_PLAYED_SPREAD · Germany_Oberliga_BadenWurttemberg
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: 1\. FC Muhlhausen; max: Oberachern, Reutlingen, Backnang, Villingen, FC Holzhausen, Bahlinger, Ravensburg, Neckarsulm, Balingen, Singen, Karlsruher 2, Teningen, Essingen, Nottingen, Normannia Gmund.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_BadenWurttemberg.csv`

### CRITICAL-020 · ST_PLAYED_SPREAD · Germany_Oberliga_Bremen
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: Bremen I2; max: Schwachhausen.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_Bremen.csv`

### CRITICAL-021 · ST_PLAYED_SPREAD · Hungary_NBI
- Area: `standings`
- Dettaglio: Played min=1, max=8, delta=7; min: Budapest Honved, Vasas Budapest; max: Ujpest, Zalaegerszeg.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Hungary_NBI.csv`

### CRITICAL-022 · ST_PLAYED_SPREAD · Iceland_1DeildWomen
- Area: `standings`
- Dettaglio: Played min=3, max=19, delta=16; min: Keflavik Women; max: Haukar, HK Kopavogur, ÍA Akranes.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_1DeildWomen.csv`

### CRITICAL-023 · ST_PLAYED_SPREAD · Iceland_BestaDeildKvenna
- Area: `standings`
- Dettaglio: Played min=1, max=18, delta=17; min: Vikingur Reykjavik, FH Hafnarfjörður Women, Þór/KA Akureyri, Breidablik, Grindavik/Njarovik, Throttur, Valur Reykjavík, Stjarnan; max: Breidablik D, Hafnarfjordur D, IBV Vestmannaeyjar D, Stjarnan D, Throttur D, Grindavik/Njardvik D, Fram D, Valur D, Vikingur Reykjavik D, Thor/KA D.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_BestaDeildKvenna.csv`

### CRITICAL-024 · ST_PLAYED_SPREAD · Iceland_Division_1
- Area: `standings`
- Dettaglio: Played min=1, max=26, delta=25; min: HK Kopavogur, Hviti, Haukar; max: Fylkir.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_Division_1.csv`

### CRITICAL-025 · ST_PLAYED_SPREAD · Iceland_Division_2
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Throttur Vogum; max: Fjolnir.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_Division_2.csv`

### CRITICAL-026 · ST_DUP_TEAM · Islanda_Division_2_2026
- Area: `standings`
- Dettaglio: Squadre duplicate: kari, fjolnir, kfa, throttur vogar, dalvik/reynir, hviti, olafsvik, haukar, kormakur/hvot, selfoss
- Verifica suggerita: Verificare alias/normalizzazione nomi squadra.
- Sorgente: `data\storico\classifiche_calcolate\Islanda_Division_2_2026.csv`

### CRITICAL-027 · ST_PLAYED_SPREAD · Islanda_Division_2_2026
- Area: `standings`
- Dettaglio: Played min=1, max=9, delta=8; min: Kari, Fjolnir, KFA, Throttur Vogar, Dalvik/Reynir, Hviti, Olafsvik, Haukar, Kormakur/Hvot, Selfoss, Magni, KFG Gardabaer; max: Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Fjolnir, Kormakur/Hvot, KFG Gardabaer, Hviti, Olafsvik, KFA, Throttur Vogar, Magni.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Islanda_Division_2_2026.csv`

### CRITICAL-028 · ST_PLAYED_SPREAD · Kazakhstan_PremierLeague
- Area: `standings`
- Dettaglio: Played min=1, max=26, delta=25; min: Altai Semey, Zhetysu Taldykorgan; max: Zhenis, Ulytau.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Kazakhstan_PremierLeague.csv`

### CRITICAL-029 · ST_PLAYED_SPREAD · Latvia_Virsliga
- Area: `standings`
- Dettaglio: Played min=1, max=28, delta=27; min: SK Super Nova; max: Riga FC, FK Liepaja, Jelgava.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Latvia_Virsliga.csv`

### CRITICAL-030 · ST_PLAYED_SPREAD · Lebanon_PremierLeague
- Area: `standings`
- Dettaglio: Played min=11, max=23, delta=12; min: Bourj FC; max: Al Riyadi Abbasiyah, Tadamon, Racing.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Lebanon_PremierLeague.csv`

### CRITICAL-031 · ST_PLAYED_SPREAD · Lithuania_Toplyga
- Area: `standings`
- Dettaglio: Played min=17, max=29, delta=12; min: Riteriai; max: Transinvest, FK Panevezys.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Lithuania_Toplyga.csv`

### CRITICAL-032 · ST_PLAYED_SPREAD · Moldova_Liga1_GroupA
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: Victoria, Falesti; max: Vulturii Cutezatori, Iskra Ribnita, FCM Ungheni, Univer Comrat, Zimbru 2, Sparta Selemet.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Moldova_Liga1_GroupA.csv`

### CRITICAL-033 · ST_PLAYED_SPREAD · Norway_2ndDivision_Group1
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Pors Football; max: Jerv, Bjarg, Mjoendalen.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_2ndDivision_Group1.csv`

### CRITICAL-034 · ST_PLAYED_SPREAD · Norway_2ndDivision_Group2
- Area: `standings`
- Dettaglio: Played min=2, max=20, delta=18; min: Eidsvold TF; max: Kjelsaas, Tromsdalen, Skeid, Trygg/Lade.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_2ndDivision_Group2.csv`

### CRITICAL-035 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group1
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Brattvag, Arendal, , Mjondalen, Halden, IF Ready Football, Lokomotiv Oslo FK, Eik-Tonsberg, Lysekloster, Vidar, Notodden; max: Gamle Oslo, Heming, Baerum, Vaalerenga IF 2, Nordstrand, Ullern, Konnerud, Grei.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group1.csv`

### CRITICAL-036 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group2
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Eidsvold, Lørenskog; max: Strindheim, Melhus.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group2.csv`

### CRITICAL-037 · ST_ALIAS_SUSPECTED · Norway_3rdDivision_Group3
- Area: `standings`
- Dettaglio: Più nomi risolvono alla stessa identità canonica: OS / Os.
- Verifica suggerita: Consolidare tramite team_name_dictionary.csv e rigenerare classifica/Laboratory.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group3.csv`

### CRITICAL-038 · ST_DUP_TEAM · Norway_3rdDivision_Group3
- Area: `standings`
- Dettaglio: Squadre duplicate: os
- Verifica suggerita: Verificare alias/normalizzazione nomi squadra.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group3.csv`

### CRITICAL-039 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group3
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Askøy, Foerde, Os, Vard Haugesund, FK Fyllingsdalen; max: Austevoll, Stord, Gneist.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group3.csv`

### CRITICAL-040 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group5
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Skjervoey; max: Harstad, Floeya.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group5.csv`

### CRITICAL-041 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group6
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Rælingen, Lillehammer FK; max: Elverum, Oppsal.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group6.csv`

### CRITICAL-042 · ST_PLAYED_SPREAD · Sweden_Division1_Norra
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Vasalunds, Sollentuna FK; max: AFC Eskilstuna, Assyriska FF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division1_Norra.csv`

### CRITICAL-043 · ST_PLAYED_SPREAD · Sweden_Division1_Sodra
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Kristianstad FC, Trelleborgs FF, Tvaakers IF; max: Hassleholms IF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division1_Sodra.csv`

### CRITICAL-044 · ST_PLAYED_SPREAD · Sweden_Division2_NorraGotaland
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Skara FC, Lidkoepings FK, Vaenersborgs IF, IFK Skoevde FK, IFK Kumla; max: Ahlafors IF, Herrestads AIF, Vanersborgs IF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_NorraGotaland.csv`

### CRITICAL-045 · ST_PLAYED_SPREAD · Sweden_Division2_NorraSvealand
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Kungsaengens IF, Kungsangens IF, Helges IF; max: Sunnersta AIF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_NorraSvealand.csv`

### CRITICAL-046 · ST_PLAYED_SPREAD · Sweden_Division2_Norrland
- Area: `standings`
- Dettaglio: Played min=1, max=21, delta=20; min: Team TG FF, Viggbyholms, Falu, Bollstanas, Angby, Kungsangen, Gute, IK Franke, Lidingo IFK; max: Skelleftea, IFK Lulea, IFK Ostersund, Boden, Gottne, Lucksta.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_Norrland.csv`

### CRITICAL-047 · ST_PLAYED_SPREAD · Sweden_Division2_SodraGotaland
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Stenungsunds, Karlslund, Dalstorps IF, Jonsereds, Smedby, Herrestads AIF, IFK Skovde, Motala, Tord, Onsala, Torslanda, Eker Orebro, Nosaby IF, Vaexjoe Norra IF, Vaxjo Norra IF, Haninge, Kumla; max: IFK Berga.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_SodraGotaland.csv`

### CRITICAL-048 · ST_PLAYED_SPREAD · Sweden_Division2_VastraGotaland
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Landvetter IS, Lindome GIF, Galtabaecks BK, IF Boelan; max: Dalstorps IF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_VastraGotaland.csv`

### CRITICAL-049 · ST_PLAYED_SPREAD · Sweden_Superettan
- Area: `standings`
- Dettaglio: Played min=1, max=24, delta=23; min: Falkenbergs FF, Orgryte, Hacken, IK Brage; max: Norrkoping, Falkenberg, Östersund, Varberg, Landskrona, Oddevold, Nordic United, Sandviken, Ljungskile, Värnamo, Örebro, Norrby, Brage, Sundsvall.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Superettan.csv`

### CRITICAL-050 · ST_PLAYED_SPREAD · Switzerland_PromotionLeague
- Area: `standings`
- Dettaglio: Played min=1, max=8, delta=7; min: FC Kreuzlingen; max: Breitenrain.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Switzerland_PromotionLeague.csv`

### CRITICAL-051 · ST_PLAYED_SPREAD · Switzerland_SuperLeague
- Area: `standings`
- Dettaglio: Played min=1, max=8, delta=7; min: FC Haka j., Fish United; max: Sion, Young Boys, Basilea, Zurigo, Luzern, Grasshoppers, Vaduz, Lausanne.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Switzerland_SuperLeague.csv`

### CRITICAL-052 · ST_ALIAS_SUSPECTED · USA_MLS
- Area: `standings`
- Dettaglio: Più nomi risolvono alla stessa identità canonica: CF Montreal / CF Montréal.
- Verifica suggerita: Consolidare tramite team_name_dictionary.csv e rigenerare classifica/Laboratory.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLS.csv`

### CRITICAL-053 · ST_PLAYED_SPREAD · USA_MLS
- Area: `standings`
- Dettaglio: Played min=1, max=26, delta=25; min: Inter Miami CF, Seattle Sounders FC, New York City FC, Atlanta United, CF Montréal; max: Charlotte, Toronto FC.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLS.csv`

### CRITICAL-054 · ST_PLAYED_SPREAD · USA_MLSNextPro_EasternConference_NortheastDivision
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Portland Timbers 2, Vancouver 2; max: New England Revolution 2, Philadelphia 2, Cincinnati 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_EasternConference_NortheastDivision.csv`

### CRITICAL-055 · ST_PLAYED_SPREAD · USA_MLSNextPro_EasternConference_SoutheastDivision
- Area: `standings`
- Dettaglio: Played min=3, max=24, delta=21; min: Connecticut FC, New York City 2, Toronto FC 2, Philadelphia 2, Cincinnati 2, New England Revolution 2, Columbus Crew 2; max: Crown Legacy.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_EasternConference_SoutheastDivision.csv`

### CRITICAL-056 · ST_PLAYED_SPREAD · USA_MLSNextPro_WesternConference_CentralDivision
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Chicago Fire 2, Inter Miami 2; max: St. Louis City 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_WesternConference_CentralDivision.csv`

### CRITICAL-057 · ST_PLAYED_SPREAD · USA_MLSNextPro_WesternConference_PacificDivision
- Area: `standings`
- Dettaglio: Played min=4, max=23, delta=19; min: St. Louis City 2, Minnesota 2; max: Los Angeles FC 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_WesternConference_PacificDivision.csv`

### CRITICAL-058 · ST_PLAYED_SPREAD · USA_USLLeagueOne
- Area: `standings`
- Dettaglio: Played min=1, max=27, delta=26; min: Fort Wayne FC, Forward Madison FC, Chattanooga Red Wolves SC; max: AV Alta, Portland Hearts of Pine.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLLeagueOne.csv`

## WARNING (1661)

### WARNING-001 · LAB_DUP_MATCH · Albania_AbissnetSuperiore | 2026-09-11 | Skenderbeu - Tirana
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8116`

### WARNING-002 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-01 | Noah 2 - Andranik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6423`

### WARNING-003 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-01 | BKMA 2 - Bentonit
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6425`

### WARNING-004 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-01 | Olympia Yerevan - Araks Ararat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6451`

### WARNING-005 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-01 | Ararat-Armenia 2 - Mika
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6457`

### WARNING-006 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-15 | Mika - Urartu 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9410`

### WARNING-007 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-15 | Olympia Yerevan - Shirak 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9448`

### WARNING-008 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-15 | Pyunik 2 - Araks Ararat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9454`

### WARNING-009 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-15 | Lernayin Artsakh - Sardarapat 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9472`

### WARNING-010 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-14 | BKMA 2 - Andranik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9549`

### WARNING-011 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-14 | Noah 2 - Ararat 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9551`

### WARNING-012 · LAB_DUP_MATCH · Armenia_FirstLeague | 2026-09-14 | Ararat-Armenia 2 - Bentonit
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '5', 'OK'), attuali=('3', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9555`

### WARNING-013 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-08-14 | FC Gandzasar - Shirak
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2509`

### WARNING-014 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-08-15 | Ararat-Armenia - Van
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3052`

### WARNING-015 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-08-15 | BKMA - Ararat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3376`

### WARNING-016 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-08-16 | Pyunik - Sardarapat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3679`

### WARNING-017 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-08-21 | Ararat - Pyunik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4386`

### WARNING-018 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-08-21 | Alashkert - FC Gandzasar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4467`

### WARNING-019 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-08-30 | Noah - Ararat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6254`

### WARNING-020 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-08-30 | FC Gandzasar - BKMA
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6256`

### WARNING-021 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-09-11 | Ararat-Armenia - Syunik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8111`

### WARNING-022 · LAB_DUP_MATCH · Armenia_PremierLeague | 2026-09-11 | Van - BKMA
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8134`

### WARNING-023 · LAB_DUP_MATCH · Australia_NPLACT | 2026-08-15 | Monaro Panthers - Canberra Croatia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3126`

### WARNING-024 · LAB_DUP_MATCH · Australia_NPLACT | 2026-08-15 | O'Connor Knights - Canberra White Eagles
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3232`

### WARNING-025 · LAB_DUP_MATCH · Australia_NPLACT | 2026-08-15 | Brindabella - Tigers FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3308`

### WARNING-026 · LAB_DUP_MATCH · Australia_NPLACT | 2026-08-16 | Canberra Juventus - Queanbeyan City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3701`

### WARNING-027 · LAB_DUP_MATCH · Australia_NPLACT | 2026-08-16 | Belconnen Utd. - Canberra Olympic
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3728`

### WARNING-028 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-09 | Wollongong Wolves - Sydney Utd
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2171`

### WARNING-029 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-14 | Sydney FC U23 - St. George City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2606`

### WARNING-030 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-15 | APIA Leichhardt - SD Raiders
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3200`

### WARNING-031 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-15 | WS Wanderers U21 - St George Saints
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3268`

### WARNING-032 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-15 | Sydney Olympic - Sydney Utd
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3320`

### WARNING-033 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-15 | Manly Utd - NWS Spirit
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3384`

### WARNING-034 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-16 | Blacktown City - UNSW
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3791`

### WARNING-035 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-16 | Rockdale Ilinden - Wollongong Wolves
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3829`

### WARNING-036 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-16 | Marconi - Sutherland
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3836`

### WARNING-037 · LAB_DUP_MATCH · Australia_NPLNSW | 2026-08-21 | Sydney FC U23 - Rockdale Ilinden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4534`

### WARNING-038 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-07-31 | Cooks Hill United - Broadmeadow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1366`

### WARNING-039 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-08-09 | Broadmeadow - Kahibah
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2128`

### WARNING-040 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-08-09 | Charlestown Azzurri - Maitland
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2141`

### WARNING-041 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-08-16 | Belmont Swansea Utd. - Adamstown Rosebud
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3700`

### WARNING-042 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-08-16 | Kahibah - Cooks Hill United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3708`

### WARNING-043 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-08-16 | Broadmeadow - Charlestown Azzurri
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3714`

### WARNING-044 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-08-16 | Valentine - Weston Bears
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3752`

### WARNING-045 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-08-16 | Maitland - Edgeworth E.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3770`

### WARNING-046 · LAB_DUP_MATCH · Australia_NPLNorthernNSW | 2026-08-16 | Lambton J. - Newcastle Olympic
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3774`

### WARNING-047 · LAB_DUP_MATCH · Australia_NPLQueensland | 2026-07-31 | Wynnum Wolves - Brisbane City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1357`

### WARNING-048 · LAB_DUP_MATCH · Australia_NPLQueensland | 2026-07-31 | Rochedale - Eastern Suburbs
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1358`

### WARNING-049 · LAB_DUP_MATCH · Australia_NPLQueensland | 2026-08-14 | Brisbane Roar U23 - Gold Coast Knights
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2485`

### WARNING-050 · LAB_DUP_MATCH · Australia_NPLQueensland | 2026-08-14 | Wynnum Wolves - Magic United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2488`

### WARNING-051 · LAB_DUP_MATCH · Australia_NPLQueensland | 2026-08-14 | Olympic FC - Rochedale
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2489`

### WARNING-052 · LAB_DUP_MATCH · Australia_NPLQueensland | 2026-08-14 | Moreton City Excelsior - Queensland Lions
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2495`

### WARNING-053 · LAB_DUP_MATCH · Australia_NPLQueensland | 2026-08-14 | Peninsula - Brisbane City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2504`

### WARNING-054 · LAB_DUP_MATCH · Australia_NPLQueensland | 2026-08-14 | Gold Coast - Eastern Suburbs
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2543`

### WARNING-055 · LAB_DUP_MATCH · Australia_NPLQueenslandU23 | 2026-08-16 | QLD State Team U17 - Gold Coast Knights U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3682`

### WARNING-056 · LAB_DUP_MATCH · Australia_NPLQueenslandU23 | 2026-08-16 | Olympic FC U23 - Rochedale U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3686`

### WARNING-057 · LAB_DUP_MATCH · Australia_NPLQueenslandU23 | 2026-08-16 | Peninsula U23 - Brisbane City U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3705`

### WARNING-058 · LAB_DUP_MATCH · Australia_NPLQueenslandU23 | 2026-08-16 | Moreton City Excelsior U23 - Queensland Lions U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3726`

### WARNING-059 · LAB_DUP_MATCH · Australia_NPLQueenslandU23 | 2026-08-16 | Gold Coast Blaze U23 - Eastern Suburbs U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3735`

### WARNING-060 · LAB_DUP_MATCH · Australia_NPLQueenslandU23 | 2026-08-16 | Wynnum Wolves U23 - Magic United U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3738`

### WARNING-061 · LAB_DUP_MATCH · Australia_NPLSouthAustralia | 2026-07-31 | Campbelltown City - Adelaide City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1396`

### WARNING-062 · LAB_DUP_MATCH · Australia_NPLSouthAustralia | 2026-08-15 | NE Metrostars - Croydon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3143`

### WARNING-063 · LAB_DUP_MATCH · Australia_NPLSouthAustralia | 2026-08-15 | West Adelaide - Playford Patriots
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3196`

### WARNING-064 · LAB_DUP_MATCH · Australia_NPLSouthAustralia | 2026-08-15 | West Torrens - Adelaide United U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3264`

### WARNING-065 · LAB_DUP_MATCH · Australia_NPLSouthAustralia | 2026-08-15 | Para - Adelaide Comets
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3302`

### WARNING-066 · LAB_DUP_MATCH · Australia_NPLSouthAustralia | 2026-08-15 | Sturt Lions - Campbelltown City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3312`

### WARNING-067 · LAB_DUP_MATCH · Australia_NPLSouthAustralia | 2026-08-15 | FK Beograd - Adelaide City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3353`

### WARNING-068 · LAB_DUP_MATCH · Australia_NPLTasmania | 2026-08-15 | Launceston - Clarence Zebras
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3116`

### WARNING-069 · LAB_DUP_MATCH · Australia_NPLTasmania | 2026-08-15 | Devonport - Kingborough Lions
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3187`

### WARNING-070 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-07-31 | Bentleigh - Oakleigh
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1397`

### WARNING-071 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-07-31 | Preston Lions - Green Gully
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1402`

### WARNING-072 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-08-14 | Oakleigh - Green Gully
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2556`

### WARNING-073 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-08-14 | Dandenong City - Altona Magic
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2580`

### WARNING-074 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-08-14 | St Albans - Bentleigh
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2592`

### WARNING-075 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-08-15 | Heidelberg - Hume City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3285`

### WARNING-076 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-08-15 | George Cross - Avondale FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3305`

### WARNING-077 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-08-15 | Melbourne City U21 - South Melbourne
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3331`

### WARNING-078 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-08-16 | Preston Lions - Dandenong Thunder
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3828`

### WARNING-079 · LAB_DUP_MATCH · Australia_NPLVictoria | 2026-08-21 | Green Gully - St Albans
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4513`

### WARNING-080 · LAB_DUP_MATCH · Australia_NPLWesternAustralia | 2026-08-14 | Bayswater City - Stirling Macedonia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2517`

### WARNING-081 · LAB_DUP_MATCH · Australia_NPLWesternAustralia | 2026-08-15 | Armadale - Dianella White Eagle
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3073`

### WARNING-082 · LAB_DUP_MATCH · Australia_NPLWesternAustralia | 2026-08-15 | Perth Glory U23 - Fremantle City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3101`

### WARNING-083 · LAB_DUP_MATCH · Australia_NPLWesternAustralia | 2026-08-15 | Western Knights - Balcatta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3118`

### WARNING-084 · LAB_DUP_MATCH · Australia_NPLWesternAustralia | 2026-08-15 | Olympic Kingsway - Sorrento
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3184`

### WARNING-085 · LAB_DUP_MATCH · Australia_NPLWesternAustralia | 2026-08-15 | Perth Azzurri - Perth RedStar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3188`

### WARNING-086 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-09 | Wollongong Wolves U20 - Sydney Utd U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2142`

### WARNING-087 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-14 | Sydney FC U20 - St. George City U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2478`

### WARNING-088 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-15 | Sydney Olympic U20 - Sydney Utd U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3100`

### WARNING-089 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-15 | Manly Utd U20 - NWS Spirit U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3123`

### WARNING-090 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-15 | WS Wanderers U20 - St George Saints U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3139`

### WARNING-091 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-15 | APIA Leichhardt U20 - SD Raiders U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3157`

### WARNING-092 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-16 | Blacktown City U20 - UNSW U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3702`

### WARNING-093 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-16 | Marconi S. U20 - Sutherland U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3731`

### WARNING-094 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-16 | Rockdale Ilinden U20 - Wollongong Wolves U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3740`

### WARNING-095 · LAB_DUP_MATCH · Australia_NPL_NSW_U20 | 2026-08-21 | Sydney FC U20 - Rockdale Ilinden U20
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4391`

### WARNING-096 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-07-31 | Prospect United - Blacktown Spartans
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1375`

### WARNING-097 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-15 | Canterbury Bankstown - Hakoah Sydney
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3115`

### WARNING-098 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-15 | Inter Lions - Bankstown City Lions
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3163`

### WARNING-099 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-15 | Newcastle Jets U23 - Dulwich Hill
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3166`

### WARNING-100 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-15 | Western City Rangers - Hills United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3168`

### WARNING-101 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-15 | Bulls Academy - Northern Tigers
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3189`

### WARNING-102 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-15 | Macarthur Rams - Blacktown Spartans
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3253`

### WARNING-103 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-15 | Rydalmere Lions - Prospect United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3311`

### WARNING-104 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-16 | Central Coast Mariners U23 - Hurstville Zagreb
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3736`

### WARNING-105 · LAB_DUP_MATCH · Australia_NSWLeagueOne | 2026-08-21 | Blacktown Spartans - Hurstville Zagreb
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4412`

### WARNING-106 · LAB_DUP_MATCH · Australia_NorthernNSWStateLeague | 2026-08-09 | Wallsend Red Devils - West Wallsend
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2127`

### WARNING-107 · LAB_DUP_MATCH · Australia_NorthernNSWStateLeague | 2026-08-09 | Lake Macquarie - South Cardiff
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2146`

### WARNING-108 · LAB_DUP_MATCH · Australia_NorthernNSWStateLeague | 2026-08-15 | Newcastle Croatia - Wallsend Red Devils
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3057`

### WARNING-109 · LAB_DUP_MATCH · Australia_NorthernNSWStateLeague | 2026-08-15 | Toronto Awaba Stags - Lake Macquarie
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3104`

### WARNING-110 · LAB_DUP_MATCH · Australia_NorthernNSWStateLeague | 2026-08-15 | New Lambton - Cessnock City Hornets
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3158`

### WARNING-111 · LAB_DUP_MATCH · Australia_NorthernNSWStateLeague | 2026-08-15 | West Wallsend - South Cardiff
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3300`

### WARNING-112 · LAB_DUP_MATCH · Australia_NorthernNSWStateLeague | 2026-08-15 | Singleton Strikers - Dudley Redhead United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3315`

### WARNING-113 · LAB_DUP_MATCH · Australia_SAStateLeague | 2026-08-15 | South Adelaide - Adelaide Atletico
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3182`

### WARNING-114 · LAB_DUP_MATCH · Australia_SAStateLeague | 2026-08-15 | Adelaide Olympic - Adelaide Croatia Raiders
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3223`

### WARNING-115 · LAB_DUP_MATCH · Australia_SAStateLeague | 2026-08-15 | Cumberland Utd. - Modbury
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3275`

### WARNING-116 · LAB_DUP_MATCH · Australia_SAStateLeague | 2026-08-15 | Adelaide Cobras - Salisbury Utd.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3287`

### WARNING-117 · LAB_DUP_MATCH · Australia_SAStateLeague | 2026-08-15 | Blue Eagles - Eastern United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3291`

### WARNING-118 · LAB_DUP_MATCH · Australia_SAStateLeague | 2026-08-15 | Cove FC - Fulham Utd.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3301`

### WARNING-119 · LAB_DUP_MATCH · Australia_TasmaniaNorthernChampionship | 2026-07-31 | Ulverstone U21 - Launceston United U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1355`

### WARNING-120 · LAB_DUP_MATCH · Australia_TasmaniaNorthernChampionship | 2026-08-15 | Burnie Utd. - Ulverstone U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3062`

### WARNING-121 · LAB_DUP_MATCH · Australia_TasmaniaNorthernChampionship | 2026-08-15 | Somerset - Northern Rangers
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3071`

### WARNING-122 · LAB_DUP_MATCH · Australia_TasmaniaNorthernChampionship | 2026-08-15 | Devonport U21 - Riverside Olympic U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3127`

### WARNING-123 · LAB_DUP_MATCH · Australia_TasmaniaNorthernChampionship | 2026-08-15 | Launceston U21 - Launceston United U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3198`

### WARNING-124 · LAB_DUP_MATCH · Australia_TasmaniaSouthernChampionship | 2026-07-31 | Glenorchy Knights U21 - University of Tasmania
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1349`

### WARNING-125 · LAB_DUP_MATCH · Australia_TasmaniaSouthernChampionship | 2026-07-31 | Olympia Warriors - Hobart Utd.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1351`

### WARNING-126 · LAB_DUP_MATCH · Australia_TasmaniaSouthernChampionship | 2026-07-31 | South Hobart U21 - Taroona
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1352`

### WARNING-127 · LAB_DUP_MATCH · Australia_TasmaniaSouthernChampionship | 2026-08-15 | Olympia Warriors - Hobart City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3048`

### WARNING-128 · LAB_DUP_MATCH · Australia_TasmaniaSouthernChampionship | 2026-08-15 | Taroona - Glenorchy Knights U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3053`

### WARNING-129 · LAB_DUP_MATCH · Australia_TasmaniaSouthernChampionship | 2026-08-15 | New Town - University of Tasmania
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3086`

### WARNING-130 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague | 2026-07-31 | Melbourne Knights - Western Utd. U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1359`

### WARNING-131 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague | 2026-07-31 | Northcote City - Eltham Redbacks
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1369`

### WARNING-132 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague | 2026-08-14 | Eltham Redbacks - Manningham United Blues
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2484`

### WARNING-133 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague | 2026-08-15 | Brunswick City - North Geelong
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3134`

### WARNING-134 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague | 2026-08-15 | Port Melbourne Sharks - Melbourne Knights
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3324`

### WARNING-135 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague | 2026-08-15 | Brunswick Juventus - Melbourne Srbija
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3337`

### WARNING-136 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague | 2026-08-16 | Western Utd. U21 - Langwarrin
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3697`

### WARNING-137 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague | 2026-08-21 | Northcote City - Brunswick Juventus
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4498`

### WARNING-138 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-07-31 | Essendon Royals SC - Altona City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1381`

### WARNING-139 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-07-31 | Kingston City - Springvale
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1390`

### WARNING-140 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-07-31 | Box Hill - Keilor Park
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1399`

### WARNING-141 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-07-31 | Whittlesea United - Eastern Lions
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1401`

### WARNING-142 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-14 | Springvale - Malvern
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2541`

### WARNING-143 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-14 | Eastern Lions - Essendon Royals SC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2545`

### WARNING-144 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-14 | Nunawading City - Bayside Argonauts
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2590`

### WARNING-145 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-14 | Keilor Park - Whittlesea United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2612`

### WARNING-146 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-15 | Goulburn Valley Suns - Werribee City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3178`

### WARNING-147 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-15 | Moreland City - Box Hill
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3257`

### WARNING-148 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-15 | Altona City - Kingston City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3357`

### WARNING-149 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-21 | Essendon Royals SC - Keilor Park
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4441`

### WARNING-150 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-21 | Whittlesea United - Moreland City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4474`

### WARNING-151 · LAB_DUP_MATCH · Australia_VictoriaPremierLeague2 | 2026-08-21 | Box Hill - Nunawading City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4519`

### WARNING-152 · LAB_DUP_MATCH · Australia_WAStateLeague | 2026-08-15 | Floreat Athena - Mandurah City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3080`

### WARNING-153 · LAB_DUP_MATCH · Australia_WAStateLeague | 2026-08-15 | Nedlands - Subiaco
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3084`

### WARNING-154 · LAB_DUP_MATCH · Australia_WAStateLeague | 2026-08-15 | Kingsley Westside - Murdoch Melville
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3161`

### WARNING-155 · LAB_DUP_MATCH · Australia_WAStateLeague | 2026-08-15 | Quinns - Gwelup Croatia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3180`

### WARNING-156 · LAB_DUP_MATCH · Australia_WAStateLeague | 2026-08-15 | Joondalup - Curtin Univ
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3214`

### WARNING-157 · LAB_DUP_MATCH · Australia_WAStateLeague | 2026-08-15 | Cockburn City - Inglewood
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3318`

### WARNING-158 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-14 | Hertha Wels - SK Rapid 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2623`

### WARNING-159 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-14 | St. Polten - BW Linz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2629`

### WARNING-160 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-15 | Kapfenberg - Innsbruck
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3076`

### WARNING-161 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-15 | Voitsberg - Bregenz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3165`

### WARNING-162 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-15 | Sturm Graz 2 - Admira
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3173`

### WARNING-163 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-15 | Austria (Am) - A. Salzburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3367`

### WARNING-164 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-15 | Floridsdorfer AC - Amstetten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3369`

### WARNING-165 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-16 | First Vienna - Liefering
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3673`

### WARNING-166 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-21 | Amstetten - Hertha Wels
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4397`

### WARNING-167 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-21 | A. Salzburg - Kapfenberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4400`

### WARNING-168 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-21 | Liefering - Austria (Am)
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4449`

### WARNING-169 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-21 | Admira - First Vienna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4484`

### WARNING-170 · LAB_DUP_MATCH · Austria_2Liga | 2026-08-21 | Innsbruck - St. Polten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4565`

### WARNING-171 · LAB_DUP_MATCH · Austria_2Liga | 2026-09-11 | SK Rapid 2 - First Vienna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8106`

### WARNING-172 · LAB_DUP_MATCH · Austria_2Liga | 2026-09-11 | Innsbruck - Voitsberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8118`

### WARNING-173 · LAB_DUP_MATCH · Austria_2Liga | 2026-09-11 | Admira - Kapfenberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8146`

### WARNING-174 · LAB_DUP_MATCH · Austria_2Liga | 2026-09-11 | Amstetten - Austria (Am)
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8159`

### WARNING-175 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-14 | LASK - Ried
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2582`

### WARNING-176 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-15 | A. Lustenau - Wolfsberger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3378`

### WARNING-177 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-15 | Sturm Graz - Altach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3409`

### WARNING-178 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-16 | SK Rapid - Grazer
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('8', '0', 'OK'), attuali=('8', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3816`

### WARNING-179 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-16 | Tirol - Salzburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3899`

### WARNING-180 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-16 | Hartberg - Austria Vienna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3904`

### WARNING-181 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-21 | Ried - Grazer
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4415`

### WARNING-182 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-30 | Hartberg - Ried
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6269`

### WARNING-183 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-08-30 | Salzburg - Austria Vienna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6271`

### WARNING-184 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-09-01 | Wolfsberger - LASK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6462`

### WARNING-185 · LAB_DUP_MATCH · Austria_Bundesliga | 2026-09-11 | Ried - Salzburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8090`

### WARNING-186 · LAB_DUP_MATCH · Austria_Burgenland | 2026-08-21 | Leithaprodersdorf - Halbturn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4378`

### WARNING-187 · LAB_DUP_MATCH · Austria_Burgenland | 2026-08-21 | Deutschkreutz - Neusiedl
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4521`

### WARNING-188 · LAB_DUP_MATCH · Austria_Burgenland | 2026-08-21 | Lackenbach - Klingenbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4547`

### WARNING-189 · LAB_DUP_MATCH · Austria_Burgenland | 2026-08-21 | Pinkafeld - Oberpullendorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4563`

### WARNING-190 · LAB_DUP_MATCH · Austria_Burgenland | 2026-08-21 | SV Eberau - Bad Sauerbrunn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4572`

### WARNING-191 · LAB_DUP_MATCH · Austria_Burgenland | 2026-08-21 | Neudorf/Parndorf - Kohfidisch
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4575`

### WARNING-192 · LAB_DUP_MATCH · Austria_Burgenland | 2026-09-11 | Bad Sauerbrunn - Pama
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8009`

### WARNING-193 · LAB_DUP_MATCH · Austria_Burgenland | 2026-09-11 | Oberpullendorf - Kohfidisch
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8060`

### WARNING-194 · LAB_DUP_MATCH · Austria_Burgenland | 2026-09-11 | Klingenbach - Deutschkreutz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8109`

### WARNING-195 · LAB_DUP_MATCH · Austria_Burgenland | 2026-09-11 | Leithaprodersdorf - Lackenbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8127`

### WARNING-196 · LAB_DUP_MATCH · Austria_Karnten | 2026-08-14 | SC St. Veit - Saint Michael Lavanttal
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2463`

### WARNING-197 · LAB_DUP_MATCH · Austria_Karnten | 2026-08-14 | SV Spittal - TSV Grafenstein
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2631`

### WARNING-198 · LAB_DUP_MATCH · Austria_Karnten | 2026-08-15 | KAC 1909 - Nussdorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3069`

### WARNING-199 · LAB_DUP_MATCH · Austria_Karnten | 2026-08-15 | Lendorf - SAK Klagenfurt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3145`

### WARNING-200 · LAB_DUP_MATCH · Austria_Karnten | 2026-08-15 | SC Landskron - Atus Ferlach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3408`

### WARNING-201 · LAB_DUP_MATCH · Austria_Karnten | 2026-08-15 | Matrei - SGA Sirnitz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3415`

### WARNING-202 · LAB_DUP_MATCH · Austria_Karnten | 2026-08-21 | SV Spittal - Matrei
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4571`

### WARNING-203 · LAB_DUP_MATCH · Austria_Karnten | 2026-09-11 | SC St. Veit - SGA Sirnitz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7979`

### WARNING-204 · LAB_DUP_MATCH · Austria_Karnten | 2026-09-11 | Nussdorf - Saint Michael Lavanttal
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8039`

### WARNING-205 · LAB_DUP_MATCH · Austria_Karnten | 2026-09-11 | Lendorf - Kottmannsdorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('7', '2', 'OK'), attuali=('7', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8075`

### WARNING-206 · LAB_DUP_MATCH · Austria_Karnten | 2026-09-11 | SAK Klagenfurt - Dellach/Gail
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8081`

### WARNING-207 · LAB_DUP_MATCH · Austria_Karnten | 2026-09-11 | KAC 1909 - Atus Ferlach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8147`

### WARNING-208 · LAB_DUP_MATCH · Austria_Niederosterreich | 2026-08-21 | Zwettl - Amstetten (Am)
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4364`

### WARNING-209 · LAB_DUP_MATCH · Austria_Niederosterreich | 2026-08-21 | Langenrohr - St. Peter in der Au
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4396`

### WARNING-210 · LAB_DUP_MATCH · Austria_Niederosterreich | 2026-08-21 | Ardagger - Retz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4533`

### WARNING-211 · LAB_DUP_MATCH · Austria_Niederosterreich | 2026-08-21 | Ebreichsdorf - Ortmann
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4553`

### WARNING-212 · LAB_DUP_MATCH · Austria_Niederosterreich | 2026-09-11 | SCU Kilb - Hohenau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7988`

### WARNING-213 · LAB_DUP_MATCH · Austria_Niederosterreich | 2026-09-11 | Zwettl - Ardagger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8072`

### WARNING-214 · LAB_DUP_MATCH · Austria_Niederosterreich | 2026-09-11 | Wieselburg - Langenrohr
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8113`

### WARNING-215 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-14 | ASK St.Valentin - Bad Ischl
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2530`

### WARNING-216 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-14 | Friedburg - Edelweiss
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2622`

### WARNING-217 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-15 | St. Martin im Muhlreis - Weisskirchen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3098`

### WARNING-218 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-15 | Perg - Garsten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3154`

### WARNING-219 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-15 | Andorf - Pregarten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3360`

### WARNING-220 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-21 | Weisskirchen - Friedburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4390`

### WARNING-221 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-21 | Pregarten - St. Martin im Muhlreis
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4452`

### WARNING-222 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-21 | Union Unis Gschwandt - ASK St.Valentin
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4482`

### WARNING-223 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-21 | Edelweiss - Perg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4497`

### WARNING-224 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-21 | Vocklamarkt - Mondsee
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4550`

### WARNING-225 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-21 | Gmunden - Micheldorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4558`

### WARNING-226 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-08-21 | Garsten - Ostermiething
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4569`

### WARNING-227 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-09-01 | Weisskirchen - Friedburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6458`

### WARNING-228 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-09-11 | Ostermiething - Pregarten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8070`

### WARNING-229 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-09-11 | Friedburg - Andorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8087`

### WARNING-230 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-09-11 | Vocklamarkt - Gmunden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8100`

### WARNING-231 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-09-11 | Micheldorf - Weisskirchen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8104`

### WARNING-232 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-09-11 | Perg - Bad Ischl
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8112`

### WARNING-233 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-09-11 | ASK St.Valentin - St. Martin im Muhlreis
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8128`

### WARNING-234 · LAB_DUP_MATCH · Austria_Oberosterreich | 2026-09-15 | Vocklamarkt - Ostermiething
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9419`

### WARNING-235 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-14 | Donaufeld Wien - SV Oberwart
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2512`

### WARNING-236 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-14 | Kremser - Parndorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2583`

### WARNING-237 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-14 | Warth - Favoritner
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2585`

### WARNING-238 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-14 | Leobendorf - Horn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2602`

### WARNING-239 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-14 | Wiener - Gloggnitz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2647`

### WARNING-240 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-15 | Wienerberger - Traiskirchen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3246`

### WARNING-241 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-15 | SV Donau - Marchfeld
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3321`

### WARNING-242 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-15 | Wiener Viktoria - Mattersburg SV 2020
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3412`

### WARNING-243 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-21 | SV Oberwart - Wienerberger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '2', 'OK'), attuali=('5', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4372`

### WARNING-244 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-21 | Horn - SV Donau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4437`

### WARNING-245 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-21 | Marchfeld - Kremser
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4516`

### WARNING-246 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-21 | Wiener - Wiener Viktoria
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4528`

### WARNING-247 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-21 | Traiskirchen - Leobendorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '4', 'OK'), attuali=('5', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4567`

### WARNING-248 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-08-21 | Favoritner - Donaufeld Wien
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4576`

### WARNING-249 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-09-01 | Horn - Parndorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6463`

### WARNING-250 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-09-11 | Parndorf - Traiskirchen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8013`

### WARNING-251 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-09-11 | Kremser - SV Oberwart
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8119`

### WARNING-252 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-09-11 | Marchfeld - Horn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8150`

### WARNING-253 · LAB_DUP_MATCH · Austria_Regionalliga_East | 2026-09-11 | SV Donau - Favoritner
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8187`

### WARNING-254 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-14 | Wallern/St Marienkirchen - Dietach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2472`

### WARNING-255 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-14 | UFC Hallein - Schallerbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2514`

### WARNING-256 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-14 | TSV St. Johann - Saalfelden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2564`

### WARNING-257 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-14 | Union Gurten - Vorwarts Steyr
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2577`

### WARNING-258 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-14 | Seekirchen - Kuchl
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2616`

### WARNING-259 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-15 | Wals-Grunau - LASK (Am)
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3217`

### WARNING-260 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-15 | Ried (Am) - Grodig
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3374`

### WARNING-261 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-21 | Schallerbach - Dietach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4381`

### WARNING-262 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-21 | Kuchl - Wals-Grunau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4398`

### WARNING-263 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-21 | Wallern/St Marienkirchen - TSV St. Johann
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4416`

### WARNING-264 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-21 | Leonfelden - UFC Hallein
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4438`

### WARNING-265 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-08-21 | Saalfelden - Seekirchen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4443`

### WARNING-266 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-09-11 | Union Gurten - Saalfelden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8014`

### WARNING-267 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-09-11 | Schallerbach - Grodig
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8032`

### WARNING-268 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-09-11 | Seekirchen - Dietach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8035`

### WARNING-269 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-09-11 | Leonfelden - Vorwarts Steyr
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8093`

### WARNING-270 · LAB_DUP_MATCH · Austria_Regionalliga_North | 2026-09-15 | Vorwarts Steyr - Schallerbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9474`

### WARNING-271 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-14 | A. Klagenfurt - Wolfsberger (Am)
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2573`

### WARNING-272 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-14 | ATSV Wolfsberger - Volkermarkt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2579`

### WARNING-273 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-14 | Treibach - Atus Velden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2605`

### WARNING-274 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-15 | Donau Klagenfurt - Bleiburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3399`

### WARNING-275 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-21 | Allerheiligen - Weiz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4426`

### WARNING-276 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-21 | Wolfsberger (Am) - Treibach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4428`

### WARNING-277 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-21 | Volkermarkt - Donau Klagenfurt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '3', 'OK'), attuali=('5', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4525`

### WARNING-278 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-21 | Atus Velden - ATSV Wolfsberger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4552`

### WARNING-279 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-21 | Gleisdorf - Kalsdorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4555`

### WARNING-280 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-08-21 | Deutschlandsberger - Hartberg (Am)
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4564`

### WARNING-281 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-09-01 | Lafnitz - Kalsdorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6430`

### WARNING-282 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-09-01 | Deutschlandsberger - Gleisdorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6437`

### WARNING-283 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-09-11 | Lafnitz - Deutschlandsberger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7981`

### WARNING-284 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-09-11 | Gleisdorf - Allerheiligen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8010`

### WARNING-285 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-09-11 | Kalsdorf - Hartberg (Am)
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8037`

### WARNING-286 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-09-11 | A. Klagenfurt - ATSV Wolfsberger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8043`

### WARNING-287 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-09-11 | Treibach - Donau Klagenfurt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8046`

### WARNING-288 · LAB_DUP_MATCH · Austria_Regionalliga_South | 2026-09-11 | Tillmitsch - Weiz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8053`

### WARNING-289 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-14 | Wolfurt - Reichenau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2533`

### WARNING-290 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-14 | Kitzbuhel - Rothis
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2578`

### WARNING-291 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-15 | Fugen - Hohenems
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3105`

### WARNING-292 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-15 | Lauterach - Schwaz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3172`

### WARNING-293 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-15 | Lochau - Altach U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3190`

### WARNING-294 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-15 | SK St. Johann - Dornbirn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3297`

### WARNING-295 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-15 | FC Lustenau - Kufstein
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3345`

### WARNING-296 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-15 | SC Imst - Tirol (Am)
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3400`

### WARNING-297 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-21 | Dornbirn - Lochau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('7', '0', 'OK'), attuali=('7', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4489`

### WARNING-298 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-08-21 | SK St. Johann - Reichenau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4538`

### WARNING-299 · LAB_DUP_MATCH · Austria_Regionalliga_West | 2026-09-11 | Fugen - Reichenau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8063`

### WARNING-300 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-14 | Strasswalchen - SAK 1914
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2508`

### WARNING-301 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-15 | USV 1960 Berndorf - Eugendorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3037`

### WARNING-302 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-15 | Burmoos - Neumarkt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3040`

### WARNING-303 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-15 | Schwarzach - Golling
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3090`

### WARNING-304 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-15 | Puch - TSU Bramberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3117`

### WARNING-305 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-15 | Seekirchen U21 - Union Henndorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3135`

### WARNING-306 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-15 | UFC Siezenheim - Thalgau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3221`

### WARNING-307 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-16 | USK Anif - ATSV Salzburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3747`

### WARNING-308 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-21 | Union Henndorf - USV 1960 Berndorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4366`

### WARNING-309 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-21 | TSU Bramberg - Seekirchen U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4393`

### WARNING-310 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-21 | Eugendorf - UFC Siezenheim
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4406`

### WARNING-311 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-21 | Schwarzach - Puch
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4420`

### WARNING-312 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-21 | Golling - ATSV Salzburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4431`

### WARNING-313 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-21 | Thalgau - Strasswalchen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4456`

### WARNING-314 · LAB_DUP_MATCH · Austria_Salzburg | 2026-08-21 | SAK 1914 - Burmoos
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4536`

### WARNING-315 · LAB_DUP_MATCH · Austria_Salzburg | 2026-09-11 | USV 1960 Berndorf - Puch
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '5', 'OK'), attuali=('1', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7983`

### WARNING-316 · LAB_DUP_MATCH · Austria_Steiermark | 2026-09-15 | Kindberg Murzhofen - TUS Bad Waltersdorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9404`

### WARNING-317 · LAB_DUP_MATCH · Austria_Steiermark | 2026-09-15 | SV Wildon - SV Schermann Rorhrach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9405`

### WARNING-318 · LAB_DUP_MATCH · Austria_Steiermark | 2026-09-15 | Leoben - SV Union Gnas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9440`

### WARNING-319 · LAB_DUP_MATCH · Austria_Steiermark | 2026-09-15 | UFC Fehring - Grossklein
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9485`

### WARNING-320 · LAB_DUP_MATCH · Austria_Steiermark | 2026-09-15 | Hohenhaus Schladming - Koflach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9494`

### WARNING-321 · LAB_DUP_MATCH · Austria_Steiermark | 2026-09-15 | Weindorf St. Anna - Stadtwerke Bruck/Mur
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9496`

### WARNING-322 · LAB_DUP_MATCH · Austria_Steiermark | 2026-09-15 | Furstenfeld - Lebring
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9501`

### WARNING-323 · LAB_DUP_MATCH · Austria_Steiermark | 2026-09-15 | Ilzer SV - Pachern
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9515`

### WARNING-324 · LAB_DUP_MATCH · Austria_Tirol | 2026-08-14 | Absam - SC Kundl
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2480`

### WARNING-325 · LAB_DUP_MATCH · Austria_Tirol | 2026-08-14 | FC Natters - Innsbrucker AC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2500`

### WARNING-326 · LAB_DUP_MATCH · Austria_Tirol | 2026-08-14 | Vols - SV Worgl
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2574`

### WARNING-327 · LAB_DUP_MATCH · Austria_Tirol | 2026-08-15 | FC Volders - SC Mils 05
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3169`

### WARNING-328 · LAB_DUP_MATCH · Austria_Tirol | 2026-08-15 | Stubai - Munster
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3222`

### WARNING-329 · LAB_DUP_MATCH · Austria_Tirol | 2026-08-15 | SV Oberperfuss - Kolsass Weer
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3352`

### WARNING-330 · LAB_DUP_MATCH · Austria_Tirol | 2026-08-21 | Kematen - FC Natters
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '5', 'OK'), attuali=('5', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4392`

### WARNING-331 · LAB_DUP_MATCH · Austria_Tirol | 2026-08-21 | SV Worgl - FC Volders
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4485`

### WARNING-332 · LAB_DUP_MATCH · Austria_Tirol | 2026-09-11 | SV Oberperfuss - Innsbrucker AC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8094`

### WARNING-333 · LAB_DUP_MATCH · Austria_Wien | 2026-09-11 | A XIII-Auhof Center - Kagran
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8165`

### WARNING-334 · LAB_DUP_MATCH · Azerbaijan_PremierLeague | 2026-09-11 | Imisli FK - Neftci Baku
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8172`

### WARNING-335 · LAB_DUP_MATCH · Azerbaijan_PremierLeague | 2026-09-14 | Safa Baku - Sabah Baku
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9585`

### WARNING-336 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-07-31 | Din. Minsk 2 - Niva Dolbizno
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1372`

### WARNING-337 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-07-31 | Orsha - Soligorsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1374`

### WARNING-338 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-07-31 | Slutsk - SKA-1938
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1387`

### WARNING-339 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-15 | Soligorsk - Niva Dolbizno
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '6', 'OK'), attuali=('2', '6', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3151`

### WARNING-340 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-15 | Slutsk - Osipovichi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3171`

### WARNING-341 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-15 | SKA-1938 - Lida
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3185`

### WARNING-342 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-15 | Molodechno - Gomel 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3242`

### WARNING-343 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-15 | Uni X Labs - Orsha
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3348`

### WARNING-344 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-16 | BATE 2 - Volna Pinsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '3', 'OK'), attuali=('5', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3709`

### WARNING-345 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-16 | Din. Minsk 2 - Minsk 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3757`

### WARNING-346 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-16 | FC Slonim - Smorgon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3802`

### WARNING-347 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-16 | Ostrovets - BumProm Gomel
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3833`

### WARNING-348 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-21 | Molodechno - Soligorsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4421`

### WARNING-349 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-08-21 | Orsha - BATE 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4455`

### WARNING-350 · LAB_DUP_MATCH · Belarus_PershayaLiga | 2026-09-11 | Din. Minsk 2 - Orsha
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8019`

### WARNING-351 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-07-31 | Dnepr Mogilev - Naftan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1404`

### WARNING-352 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-09 | Gomel - FC Minsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2170`

### WARNING-353 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-14 | Dnepr Mogilev - Belshina
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2597`

### WARNING-354 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-14 | Arsenal Dzerzhinsk - Slavia Mozyr
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2603`

### WARNING-355 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-15 | Gomel - Naftan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3319`

### WARNING-356 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-15 | Neman - FC Minsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3356`

### WARNING-357 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-15 | BATE - Vitebsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3386`

### WARNING-358 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-16 | Dynamo Brest - Isloch
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3844`

### WARNING-359 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-21 | FC Minsk - Vitebsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4545`

### WARNING-360 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-08-30 | BATE - FC Minsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6266`

### WARNING-361 · LAB_DUP_MATCH · Belarus_VysshayaLiga | 2026-09-11 | FC Minsk - Slavia Mozyr
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8167`

### WARNING-362 · LAB_DUP_MATCH · Belgium_ChallengerProLeague | 2026-09-11 | Gent U23 - Dender
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8105`

### WARNING-363 · LAB_DUP_MATCH · Belgium_ChallengerProLeague | 2026-09-11 | Beerschot VA - K. Lierse S.K.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8143`

### WARNING-364 · LAB_DUP_MATCH · Belgium_JupilerProLeague | 2026-08-21 | St. Liege - RAAL La Louviere
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4367`

### WARNING-365 · LAB_DUP_MATCH · Belgium_JupilerProLeague | 2026-08-30 | Anversa - St. Truiden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6244`

### WARNING-366 · LAB_DUP_MATCH · Belgium_JupilerProLeague | 2026-08-30 | Westerlo - Waregem
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6253`

### WARNING-367 · LAB_DUP_MATCH · Belgium_JupilerProLeague | 2026-08-30 | Gent - Club Brugge
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6262`

### WARNING-368 · LAB_DUP_MATCH · Belgium_JupilerProLeague | 2026-08-30 | Royale Union SG - Anderlecht
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6270`

### WARNING-369 · LAB_DUP_MATCH · Belgium_JupilerProLeague | 2026-09-11 | KV Mechelen - Anderlecht
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8164`

### WARNING-370 · LAB_DUP_MATCH · Bhutan_PremierLeague | 2026-07-31 | Drukpa - BFF Academy U19
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1377`

### WARNING-371 · LAB_DUP_MATCH · Bhutan_PremierLeague | 2026-08-15 | Thimphu FC - Transport United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3379`

### WARNING-372 · LAB_DUP_MATCH · Bhutan_PremierLeague | 2026-08-16 | Ugyen Academy - Tensung
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3872`

### WARNING-373 · LAB_DUP_MATCH · Bhutan_PremierLeague | 2026-09-11 | Thimphu FC - Drukpa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8099`

### WARNING-374 · LAB_DUP_MATCH · Bhutan_PremierLeague | 2026-09-15 | Tensung - BFF Academy U19
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9457`

### WARNING-375 · LAB_DUP_MATCH · Bhutan_PremierLeague | 2026-09-14 | Drukpa - RTC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9568`

### WARNING-376 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-07-31 | Universitario de Vinto - Guabira
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1353`

### WARNING-377 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-07-31 | The Strongest - Aurora
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1406`

### WARNING-378 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-08-14 | Universitario de Vinto - Tomayapo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2550`

### WARNING-379 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-08-15 | Real Oruro - Oriente Petrolero
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3096`

### WARNING-380 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-08-15 | Bolivar - SA Bulo Bulo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3201`

### WARNING-381 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-08-15 | Guabira - The Strongest
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3235`

### WARNING-382 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-08-16 | Nacional Potosi - Academia del Balompie
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3730`

### WARNING-383 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-08-16 | Always Ready - Real Potosi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3845`

### WARNING-384 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-08-16 | Blooming - Aurora
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3879`

### WARNING-385 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-09-15 | Academia del Balompie - The Strongest
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9432`

### WARNING-386 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-09-15 | Real Oruro - Real Potosi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9469`

### WARNING-387 · LAB_DUP_MATCH · Bolivia_DivisionProfesional | 2026-09-14 | Tomayapo - Bolivar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9559`

### WARNING-388 · LAB_DUP_MATCH · Bosnia_PrvaLiga_RS | 2026-09-11 | Romanija Pale - Zvijezda 09
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8001`

### WARNING-389 · LAB_DUP_MATCH · Bosnia_WWINLigaBiH | 2026-09-01 | Zrinjski - BSK Banja Luka
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6472`

### WARNING-390 · LAB_DUP_MATCH · Bosnia_WWINLigaBiH | 2026-09-11 | Celik Zenica - Radnik Bijeljina
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8126`

### WARNING-391 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-08-14 | CSKA 1948 Sofia - Cherno More
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2534`

### WARNING-392 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-08-15 | Ludogorets - Botev Plovdiv
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3255`

### WARNING-393 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-08-16 | CSKA Sofia - Botev Vratsa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3721`

### WARNING-394 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-08-16 | Lok. Plovdiv - Dunav Ruse
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3861`

### WARNING-395 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-08-21 | Cherno More - Dunav Ruse
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4457`

### WARNING-396 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-08-30 | CSKA Sofia - Cherno More
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6250`

### WARNING-397 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-08-30 | Botev Plovdiv - Levski
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6257`

### WARNING-398 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-08-30 | Spartak Varna - Ludogorets
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6259`

### WARNING-399 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-09-11 | Cherno More - Lok. Sofia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8056`

### WARNING-400 · LAB_DUP_MATCH · Bulgaria_ParvaLiga | 2026-09-14 | Ludogorets - Septemvri Sofia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9575`

### WARNING-401 · LAB_DUP_MATCH · Bulgaria_VtoraLiga | 2026-08-21 | Lok. Gorna - Etar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4585`

### WARNING-402 · LAB_DUP_MATCH · Bulgaria_VtoraLiga | 2026-09-01 | Hebar - Fratria
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6461`

### WARNING-403 · LAB_DUP_MATCH · Bulgaria_VtoraLiga | 2026-09-15 | Lok. Gorna - Nesebar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9508`

### WARNING-404 · LAB_DUP_MATCH · Bulgaria_VtoraLiga | 2026-09-15 | Ludogorets 2 - Fratria
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9509`

### WARNING-405 · LAB_DUP_MATCH · Bulgaria_VtoraLiga | 2026-09-14 | Hebar - Etar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9553`

### WARNING-406 · LAB_DUP_MATCH · Croatia_HNL | 2026-09-14 | Gorica - Varazdin
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9590`

### WARNING-407 · LAB_DUP_MATCH · Croatia_PrvaNL | 2026-09-11 | Din. Zagabria 2 - Sesvete
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8184`

### WARNING-408 · LAB_DUP_MATCH · Croatia_PrvaNL | 2026-09-11 | Opatija - Bijelo Brdo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8190`

### WARNING-409 · LAB_DUP_MATCH · CzechRepublic_1Liga | 2026-08-15 | Sparta Praga - Teplice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3186`

### WARNING-410 · LAB_DUP_MATCH · CzechRepublic_1Liga | 2026-08-15 | Pardubice - Mlada Boleslav
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3243`

### WARNING-411 · LAB_DUP_MATCH · CzechRepublic_1Liga | 2026-08-15 | Plzen - Zlin
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3252`

### WARNING-412 · LAB_DUP_MATCH · CzechRepublic_1Liga | 2026-08-15 | Slovacko - Sigma Olomouc
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3259`

### WARNING-413 · LAB_DUP_MATCH · CzechRepublic_1Liga | 2026-08-16 | Ostrava - Artis Brno
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3809`

### WARNING-414 · LAB_DUP_MATCH · CzechRepublic_1Liga | 2026-08-16 | Liberec - Slavia Praga
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3827`

### WARNING-415 · LAB_DUP_MATCH · CzechRepublic_3CFL_GroupA | 2026-08-21 | Motorlet Prague - Dukla Praga B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4537`

### WARNING-416 · LAB_DUP_MATCH · CzechRepublic_3CFL_GroupA | 2026-09-11 | Pisek - Ceske Budejovice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8069`

### WARNING-417 · LAB_DUP_MATCH · CzechRepublic_3CFL_GroupB | 2026-09-11 | Liberec B - Pardubice B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8078`

### WARNING-418 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-15 | Hlubina - Sigma Olomouc B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3056`

### WARNING-419 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-15 | Hodonin - Artis Brno B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3236`

### WARNING-420 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-15 | Nove Mesto na Morave - Zlin B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3304`

### WARNING-421 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-15 | FK Frydek-Mistek - Vsetin
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3341`

### WARNING-422 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-15 | Uhersky Brod - SK Hranice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3396`

### WARNING-423 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-16 | Unicov - Brno B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3678`

### WARNING-424 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-16 | Slovacko B - Blansko
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3683`

### WARNING-425 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-16 | Polanka nad Odrou - Vitkovice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3852`

### WARNING-426 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-16 | Havirov - Karvina B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3876`

### WARNING-427 · LAB_DUP_MATCH · CzechRepublic_3MSFL | 2026-08-21 | SK Hranice - Havirov
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4582`

### WARNING-428 · LAB_DUP_MATCH · CzechRepublic_4Liga_GroupA | 2026-09-11 | Krimice - Horovice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7996`

### WARNING-429 · LAB_DUP_MATCH · CzechRepublic_4Liga_GroupB | 2026-08-21 | Hvezda Cheb - Velvary
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4380`

### WARNING-430 · LAB_DUP_MATCH · CzechRepublic_4Liga_GroupB | 2026-08-21 | Chomutov - Usti n. L. B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4460`

### WARNING-431 · LAB_DUP_MATCH · CzechRepublic_4Liga_GroupD | 2026-08-21 | Velke Mezirici - Tasovice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4401`

### WARNING-432 · LAB_DUP_MATCH · CzechRepublic_4Liga_GroupE | 2026-08-21 | Hluk - Kromeriz B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4505`

### WARNING-433 · LAB_DUP_MATCH · CzechRepublic_4Liga_GroupE | 2026-09-11 | Batov - FK Kozlovice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8096`

### WARNING-434 · LAB_DUP_MATCH · CzechRepublic_4Liga_GroupF | 2026-08-21 | Hlucin - Bridlicna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4493`

### WARNING-435 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-14 | Dukla Praga - Slavia Praga B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2595`

### WARNING-436 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-14 | Kladno - Vlasim
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2600`

### WARNING-437 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-15 | Pribram - Prostejov
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3380`

### WARNING-438 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-15 | Ceska Lipa - Karvina
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '5', 'OK'), attuali=('2', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3381`

### WARNING-439 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-15 | Taborsko - Opava
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3391`

### WARNING-440 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-15 | Kromeriz - Jihlava
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3420`

### WARNING-441 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-16 | Zizkov - Ostrava B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3894`

### WARNING-442 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-21 | Vlasim - Pribram
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4417`

### WARNING-443 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-21 | Usti n. L. - Dukla Praga
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4454`

### WARNING-444 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-21 | Karvina - Zizkov
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4511`

### WARNING-445 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-21 | Jihlava - Taborsko
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4523`

### WARNING-446 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-21 | Prostejov - Kladno
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4542`

### WARNING-447 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-08-21 | Opava - Trinec
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4578`

### WARNING-448 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-09-11 | Dukla Praga - Vlasim
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8062`

### WARNING-449 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-09-11 | Pribram - Ostrava B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8068`

### WARNING-450 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-09-11 | Trinec - Karvina
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8097`

### WARNING-451 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-09-11 | Usti n. L. - Jihlava
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8152`

### WARNING-452 · LAB_DUP_MATCH · CzechRepublic_ChNL | 2026-09-11 | Taborsko - Kladno
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8168`

### WARNING-453 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-14 | Kolding - Vejle
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2610`

### WARNING-454 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-14 | Aalborg - Fredericia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2635`

### WARNING-455 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-15 | Hillerod - Aarhus Fremad
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3046`

### WARNING-456 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-15 | Esbjerg - Hobro
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3276`

### WARNING-457 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-15 | Koge - Hvidovre IF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3373`

### WARNING-458 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-16 | Vendsyssel - AB Copenhagen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3810`

### WARNING-459 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-21 | Vejle - Esbjerg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4375`

### WARNING-460 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-21 | Hobro - Aalborg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4491`

### WARNING-461 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-08-21 | Fredericia - Aarhus Fremad
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4527`

### WARNING-462 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-09-11 | Hobro - Vejle
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8029`

### WARNING-463 · LAB_DUP_MATCH · Denmark_1stDivision | 2026-09-11 | Vendsyssel - Aarhus Fremad
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8148`

### WARNING-464 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-14 | Nykobing - B.93
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2460`

### WARNING-465 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-14 | Skive - F. Amager
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2464`

### WARNING-466 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-14 | Brabrand - Naestved
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2510`

### WARNING-467 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-14 | Hellerup - FA 2000
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2643`

### WARNING-468 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-15 | Roskilde - Middelfart
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3141`

### WARNING-469 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-15 | VSK Aarhus - Thisted
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3270`

### WARNING-470 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-21 | Thisted - Skive
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4469`

### WARNING-471 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-21 | F. Amager - Roskilde
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4480`

### WARNING-472 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-08-21 | B.93 - Hellerup
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4486`

### WARNING-473 · LAB_DUP_MATCH · Denmark_2ndDivision | 2026-09-11 | F. Amager - Hellerup
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8141`

### WARNING-474 · LAB_DUP_MATCH · Denmark_3rdDivision | 2026-08-14 | Helsingor - BK Frem
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2477`

### WARNING-475 · LAB_DUP_MATCH · Denmark_3rdDivision | 2026-08-15 | Holbaek - Sundby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3045`

### WARNING-476 · LAB_DUP_MATCH · Denmark_3rdDivision | 2026-08-15 | Ringsted - Holstebro
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3049`

### WARNING-477 · LAB_DUP_MATCH · Denmark_3rdDivision | 2026-08-15 | Næsby - Bronshoj
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3314`

### WARNING-478 · LAB_DUP_MATCH · Denmark_3rdDivision | 2026-08-15 | ASA Aarhus - Vanløse
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3355`

### WARNING-479 · LAB_DUP_MATCH · Denmark_3rdDivision | 2026-08-15 | Horsholm-Usserod - Ishoj
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3401`

### WARNING-480 · LAB_DUP_MATCH · Denmark_3rdDivision | 2026-08-21 | Bronshoj - Holbaek
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4479`

### WARNING-481 · LAB_DUP_MATCH · Denmark_Superliga | 2026-08-14 | Viborg - Aarhus
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2632`

### WARNING-482 · LAB_DUP_MATCH · Denmark_Superliga | 2026-08-16 | Lyngby - Midtjylland
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3674`

### WARNING-483 · LAB_DUP_MATCH · Denmark_Superliga | 2026-08-16 | Randers - FC Copenhagen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3834`

### WARNING-484 · LAB_DUP_MATCH · Denmark_Superliga | 2026-08-16 | Odense - Horsens
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3901`

### WARNING-485 · LAB_DUP_MATCH · Denmark_Superliga | 2026-08-16 | Nordsjaelland - Silkeborg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3905`

### WARNING-486 · LAB_DUP_MATCH · Denmark_Superliga | 2026-09-11 | FC Copenhagen - Horsens
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7998`

### WARNING-487 · LAB_DUP_MATCH · Denmark_Superliga | 2026-09-14 | Midtjylland - Brondby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9562`

### WARNING-488 · LAB_DUP_MATCH · England_Championship | 2026-09-01 | Stoke - Norwich
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6429`

### WARNING-489 · LAB_DUP_MATCH · England_Championship | 2026-09-01 | Portsmouth - Derby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6431`

### WARNING-490 · LAB_DUP_MATCH · England_Championship | 2026-09-01 | West Ham - Wolves
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6444`

### WARNING-491 · LAB_DUP_MATCH · England_Championship | 2026-09-01 | Lincoln - Blackburn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6447`

### WARNING-492 · LAB_DUP_MATCH · England_Championship | 2026-09-01 | Birmingham - Southampton
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6450`

### WARNING-493 · LAB_DUP_MATCH · England_Championship | 2026-09-01 | Swansea - Watford
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6460`

### WARNING-494 · LAB_DUP_MATCH · England_Championship | 2026-09-01 | Preston - Bristol City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6469`

### WARNING-495 · LAB_DUP_MATCH · England_Championship | 2026-09-01 | Sheffield Utd - Bolton
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6470`

### WARNING-496 · LAB_DUP_MATCH · England_Championship | 2026-09-11 | West Ham - Wrexham
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8080`

### WARNING-497 · LAB_DUP_MATCH · England_Championship | 2026-09-15 | Middlesbrough - Millwall
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9422`

### WARNING-498 · LAB_DUP_MATCH · England_Championship | 2026-09-15 | Bristol City - Lincoln
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9488`

### WARNING-499 · LAB_DUP_MATCH · England_LeagueOne | 2026-09-01 | Wycombe - Sheffield Wed
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6439`

### WARNING-500 · LAB_DUP_MATCH · England_LeagueOne | 2026-09-01 | Doncaster - Notts County
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6454`

### WARNING-501 · LAB_DUP_MATCH · England_LeagueOne | 2026-09-01 | Bromley - Leyton Orient
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6455`

### WARNING-502 · LAB_DUP_MATCH · England_LeagueOne | 2026-09-01 | Bradford City - Cambridge Utd
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6466`

### WARNING-503 · LAB_DUP_MATCH · England_LeagueOne | 2026-09-01 | Peterborough - Stevenage
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6467`

### WARNING-504 · LAB_DUP_MATCH · England_LeagueOne | 2026-09-01 | Leicester - Plymouth
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6471`

### WARNING-505 · LAB_DUP_MATCH · England_PremierLeague | 2026-09-14 | Leeds - Newcastle
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9558`

### WARNING-506 · LAB_DUP_MATCH · Estonia_Esiliiga | 2026-08-15 | Tartu Welco - Flora U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3085`

### WARNING-507 · LAB_DUP_MATCH · Estonia_Esiliiga | 2026-08-15 | Tallinna Kalev - Elva
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3088`

### WARNING-508 · LAB_DUP_MATCH · Estonia_Esiliiga | 2026-08-15 | Viimsi JK - Levadia U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3160`

### WARNING-509 · LAB_DUP_MATCH · Estonia_Esiliiga | 2026-08-15 | Maardu - FC Tallinn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3192`

### WARNING-510 · LAB_DUP_MATCH · Estonia_Esiliiga | 2026-08-21 | Flora U21 - Viimsi JK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4414`

### WARNING-511 · LAB_DUP_MATCH · Estonia_Esiliiga | 2026-09-14 | Tartu Welco - Nomme Kalju U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9534`

### WARNING-512 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-09 | Tallinna Kalev U21 - Johvi Phoenix
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2126`

### WARNING-513 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-09 | Levadia U19 - Tabasalu
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2134`

### WARNING-514 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-09 | Legion - Narva U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2136`

### WARNING-515 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-15 | Tartu Kalev - Parnu JK Vaprus U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3042`

### WARNING-516 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-15 | Narva U21 - Johvi Phoenix
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3074`

### WARNING-517 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-15 | Legion - Tammeka U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3097`

### WARNING-518 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-16 | Tabasalu - Tallinna Kalev U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3681`

### WARNING-519 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-16 | Tulevik - Levadia U19
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3696`

### WARNING-520 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-08-21 | Tallinna Kalev U21 - Legion
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4394`

### WARNING-521 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-09-11 | Tallinna Kalev U21 - Tabasalu
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7997`

### WARNING-522 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-09-11 | Narva U21 - Levadia U19
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8006`

### WARNING-523 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-09-15 | Narva U21 - Tammeka U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9411`

### WARNING-524 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-09-15 | Levadia U19 - Tulevik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '5', 'OK'), attuali=('3', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9415`

### WARNING-525 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-09-14 | Johvi Phoenix - Tallinna Kalev U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9526`

### WARNING-526 · LAB_DUP_MATCH · Estonia_EsiliigaB | 2026-09-14 | Tabasalu - Legion
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9556`

### WARNING-527 · LAB_DUP_MATCH · Estonia_Meistriliiga | 2026-07-31 | Nomme Utd - Narva
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1362`

### WARNING-528 · LAB_DUP_MATCH · Estonia_Meistriliiga | 2026-08-14 | Nomme Utd - Tammeka
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2507`

### WARNING-529 · LAB_DUP_MATCH · Estonia_Meistriliiga | 2026-08-16 | Harju JK Laagri - Levadia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3745`

### WARNING-530 · LAB_DUP_MATCH · Estonia_Meistriliiga | 2026-08-16 | Narva - Paide
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3788`

### WARNING-531 · LAB_DUP_MATCH · Estonia_Meistriliiga | 2026-08-16 | Flora - Kuressaare
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3803`

### WARNING-532 · LAB_DUP_MATCH · Estonia_Meistriliiga | 2026-08-16 | Kalju - Parnu JK Vaprus
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3822`

### WARNING-533 · LAB_DUP_MATCH · Estonia_Meistriliiga | 2026-08-21 | Levadia - Narva
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4439`

### WARNING-534 · LAB_DUP_MATCH · FaroeIslands_1Deild | 2026-08-15 | FC Suduroy - Streymur 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '1', 'OK'), attuali=('6', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3060`

### WARNING-535 · LAB_DUP_MATCH · FaroeIslands_1Deild | 2026-08-15 | Vikingur 2 - Fuglafjordur
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3083`

### WARNING-536 · LAB_DUP_MATCH · FaroeIslands_1Deild | 2026-08-15 | B36 Torshavn 2 - TB Tvoroyri
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3087`

### WARNING-537 · LAB_DUP_MATCH · FaroeIslands_1Deild | 2026-08-15 | Hoyvik - Sandur
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3106`

### WARNING-538 · LAB_DUP_MATCH · FaroeIslands_1Deild | 2026-08-15 | Runavik 2 - HB Torshavn 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3286`

### WARNING-539 · LAB_DUP_MATCH · FaroeIslands_PremierLeague | 2026-08-16 | Runavik - Streymur
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3780`

### WARNING-540 · LAB_DUP_MATCH · FaroeIslands_PremierLeague | 2026-08-16 | HB Torshavn - Toftir
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3793`

### WARNING-541 · LAB_DUP_MATCH · FaroeIslands_PremierLeague | 2026-08-16 | Skala Itrottarfelag - Vikingur
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3811`

### WARNING-542 · LAB_DUP_MATCH · FaroeIslands_PremierLeague | 2026-08-16 | 07 Vestur Sorvagur - B36 Torshavn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3835`

### WARNING-543 · LAB_DUP_MATCH · FaroeIslands_PremierLeague | 2026-08-21 | Vikingur - B36 Torshavn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4475`

### WARNING-544 · LAB_DUP_MATCH · FaroeIslands_PremierLeague | 2026-09-11 | Argir - Toftir
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8136`

### WARNING-545 · LAB_DUP_MATCH · Finland_Kakkonen_GroupA | 2026-07-31 | Union Plaani - PEPO
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1384`

### WARNING-546 · LAB_DUP_MATCH · Finland_Kakkonen_GroupA | 2026-08-15 | HIFK - Atlantis
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '5', 'OK'), attuali=('3', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3066`

### WARNING-547 · LAB_DUP_MATCH · Finland_Kakkonen_GroupA | 2026-08-15 | PuiU - Kiffen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3193`

### WARNING-548 · LAB_DUP_MATCH · Finland_Kakkonen_GroupA | 2026-08-15 | HPS - Union Plaani
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3216`

### WARNING-549 · LAB_DUP_MATCH · Finland_Kakkonen_GroupA | 2026-08-16 | Lahden Reipas - PEPO
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3733`

### WARNING-550 · LAB_DUP_MATCH · Finland_Kakkonen_GroupB | 2026-07-31 | Abo - HJS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1383`

### WARNING-551 · LAB_DUP_MATCH · Finland_Kakkonen_GroupB | 2026-07-31 | GrIFK - EBK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1386`

### WARNING-552 · LAB_DUP_MATCH · Finland_Kakkonen_GroupB | 2026-08-15 | Ilves 2 - NJS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3152`

### WARNING-553 · LAB_DUP_MATCH · Finland_Kakkonen_GroupB | 2026-08-15 | Abo - EPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3177`

### WARNING-554 · LAB_DUP_MATCH · Finland_Kakkonen_GroupB | 2026-08-15 | MuSa - EBK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3195`

### WARNING-555 · LAB_DUP_MATCH · Finland_Kakkonen_GroupB | 2026-08-15 | HJS - GrIFK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3240`

### WARNING-556 · LAB_DUP_MATCH · Finland_Kakkonen_GroupB | 2026-08-15 | Honka - P-Iirot Rauma
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3288`

### WARNING-557 · LAB_DUP_MATCH · Finland_Kakkonen_GroupC | 2026-08-15 | VPS 2 - Hercules
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3059`

### WARNING-558 · LAB_DUP_MATCH · Finland_Kakkonen_GroupC | 2026-08-15 | Vaajakoski - GBK Kokkola
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3063`

### WARNING-559 · LAB_DUP_MATCH · Finland_Kakkonen_GroupC | 2026-08-15 | Jaro 2 - Huima / Urho
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '6', 'OK'), attuali=('2', '6', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3122`

### WARNING-560 · LAB_DUP_MATCH · Finland_Kakkonen_GroupC | 2026-08-16 | Narpes Kraft - SJK Akatemia 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3672`

### WARNING-561 · LAB_DUP_MATCH · Finland_Kakkonen_GroupC | 2026-08-16 | JBK - TP-47
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3756`

### WARNING-562 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group1 | 2026-08-14 | FC Vaajakoski/2 - SAPA
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2486`

### WARNING-563 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group1 | 2026-08-14 | FC Metso - Komeetat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2516`

### WARNING-564 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group1 | 2026-08-14 | KeuPa - Blackbird
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2636`

### WARNING-565 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group1 | 2026-08-21 | SAPA - SAPA
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4589`

### WARNING-566 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group1 | 2026-09-09 | FC Vaajakoski/2 - KeuPa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '5', 'OK'), attuali=('4', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7719`

### WARNING-567 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group1 | 2026-09-11 | Komeetat - Blackbird
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8211`

### WARNING-568 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group2 | 2026-08-14 | ToU - Ylämyllyn Yllätys
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2499`

### WARNING-569 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group2 | 2026-08-14 | Zulimanit - KuPS/Akatemia 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2531`

### WARNING-570 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group2 | 2026-09-09 | KuPS/Akatemia 2 - PK-37
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7722`

### WARNING-571 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group3 | 2026-08-14 | Mikkelin Palloilijat 2 - KoPa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2481`

### WARNING-572 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group3 | 2026-08-21 | KoPa - KJP
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4476`

### WARNING-573 · LAB_DUP_MATCH · Finland_Kolmonen_Eastern_Group3 | 2026-09-09 | LAUTP - Kultsu
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7718`

### WARNING-574 · LAB_DUP_MATCH · Finland_Kolmonen_North | 2026-08-21 | Ajax Sarkkiranta - Santa Claus
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4448`

### WARNING-575 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group1 | 2026-08-14 | NuPS - EIF/Akademi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2502`

### WARNING-576 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group1 | 2026-08-16 | EPS Reservi - Pöxyt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3689`

### WARNING-577 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group1 | 2026-08-16 | GrIFK/Akatemia U23 - PPJ/Ruoholahti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3698`

### WARNING-578 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group1 | 2026-08-21 | Pöxyt - GrIFK/Akatemia U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4373`

### WARNING-579 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group1 | 2026-08-21 | NuPS - LePa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4442`

### WARNING-580 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group1 | 2026-08-21 | MPS - Etelä-Espoon Pallo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4504`

### WARNING-581 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group1 | 2026-08-30 | GrIFK/Akatemia U23 - HooGee
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6246`

### WARNING-582 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group1 | 2026-09-09 | LePa - GrIFK/Akatemia U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7721`

### WARNING-583 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-08-09 | VJS 2 - TiPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2211`

### WARNING-584 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-08-14 | Laajasalon Palloseura - Töölön Taisto
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2468`

### WARNING-585 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-08-14 | Valtti - Atlantis FC/2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2469`

### WARNING-586 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-08-14 | PPJ/Lauttasaari - Kontu
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2483`

### WARNING-587 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-08-14 | TiPS - ToTe
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2487`

### WARNING-588 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-08-21 | TiPS - PPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4384`

### WARNING-589 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-08-21 | Kontu - Valtti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4387`

### WARNING-590 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-09-07 | VJS 2 - ToTe
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7601`

### WARNING-591 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group2 | 2026-09-11 | PPS - Töölön Taisto
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8212`

### WARNING-592 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group3 | 2026-08-14 | RiPS - TuPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2498`

### WARNING-593 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group3 | 2026-08-14 | Futura - TiPS/2 U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2501`

### WARNING-594 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group3 | 2026-08-14 | Ponnistus - Lahti/69
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2551`

### WARNING-595 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group3 | 2026-08-16 | JäPS/47 - ToTe/Tapio
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3684`

### WARNING-596 · LAB_DUP_MATCH · Finland_Kolmonen_Southern_Group3 | 2026-08-21 | Lahti/69 - RiPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4405`

### WARNING-597 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group1 | 2026-08-14 | KaaPo - Peimari United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2520`

### WARNING-598 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group1 | 2026-08-14 | ÅCF - PiPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2568`

### WARNING-599 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group1 | 2026-08-21 | VG-62 - KaaPo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4436`

### WARNING-600 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group1 | 2026-08-21 | ÅCF - EuPa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4453`

### WARNING-601 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group1 | 2026-08-21 | LTU U20 - MaPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4478`

### WARNING-602 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group1 | 2026-09-01 | SalPa 2 - EuPa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6449`

### WARNING-603 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group2 | 2026-08-14 | ACE - NoPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2476`

### WARNING-604 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group2 | 2026-08-14 | Sääksjärven Loiske - TPV/2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2505`

### WARNING-605 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group2 | 2026-09-01 | FC Haka j. - Ylöjärvi Utd.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '4', 'OK'), attuali=('5', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6424`

### WARNING-606 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group3 | 2026-08-09 | Sp. Kristina - VPV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2220`

### WARNING-607 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group3 | 2026-08-11 | VPV - Kiisto
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2225`

### WARNING-608 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group3 | 2026-08-21 | VIFK - VPV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4450`

### WARNING-609 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group3 | 2026-09-01 | KPV/Akatemia - Sp. Kristina
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6433`

### WARNING-610 · LAB_DUP_MATCH · Finland_Kolmonen_Western_Group3 | 2026-09-09 | KPV/Akatemia - NIK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7720`

### WARNING-611 · LAB_DUP_MATCH · Finland_Veikkausliiga | 2026-08-14 | VPS - TPS Turku
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2591`

### WARNING-612 · LAB_DUP_MATCH · Finland_Veikkausliiga | 2026-08-15 | Mariehamn - SJK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3349`

### WARNING-613 · LAB_DUP_MATCH · Finland_Veikkausliiga | 2026-08-16 | HJK - Jaro
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3797`

### WARNING-614 · LAB_DUP_MATCH · Finland_Veikkausliiga | 2026-08-16 | Lahti - KuPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3881`

### WARNING-615 · LAB_DUP_MATCH · Finland_Veikkausliiga | 2026-08-16 | Oulu - Inter Turku
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3889`

### WARNING-616 · LAB_DUP_MATCH · Finland_Veikkausliiga | 2026-08-21 | SJK - Lahti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4556`

### WARNING-617 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-07-31 | Inter Turku 2 - VJS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1367`

### WARNING-618 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-07-31 | Keski-Uusimaa - Tampere Utd
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '4', 'OK'), attuali=('4', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1393`

### WARNING-619 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-08-15 | Tampere Utd - TPV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3202`

### WARNING-620 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-08-15 | OLS Oulu - RoPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3225`

### WARNING-621 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-08-15 | SalPa - Jazz Pori
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3254`

### WARNING-622 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-08-16 | KuPS Akatemia - Keski-Uusimaa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3716`

### WARNING-623 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-08-16 | VJS - JJK Jyvaskyla
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '4', 'OK'), attuali=('4', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3748`

### WARNING-624 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-08-16 | Inter Turku 2 - KPV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3782`

### WARNING-625 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-08-21 | KPV - KuPS Akatemia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4402`

### WARNING-626 · LAB_DUP_MATCH · Finland_Ykkonen | 2026-08-21 | Keski-Uusimaa - JJK Jyvaskyla
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4410`

### WARNING-627 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-07-31 | KTP - SJK Akatemia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1405`

### WARNING-628 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-07-31 | Ekenas - Klubi 04
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1407`

### WARNING-629 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-07-31 | PK-35 - Haka
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1408`

### WARNING-630 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-08-14 | JaPS - Haka
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2609`

### WARNING-631 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-08-15 | KTP - KaPa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3245`

### WARNING-632 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-08-15 | PK-35 - Klubi 04
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3392`

### WARNING-633 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-08-15 | Jippo - SJK Akatemia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3395`

### WARNING-634 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-08-16 | Mikkeli - Ekenas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3868`

### WARNING-635 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-08-21 | Haka - SJK Akatemia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4501`

### WARNING-636 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-08-21 | PK-35 - JaPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4560`

### WARNING-637 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-08-30 | SJK Akatemia - Klubi 04
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '6', 'OK'), attuali=('2', '6', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6273`

### WARNING-638 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-09-11 | KaPa - PK-35
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8139`

### WARNING-639 · LAB_DUP_MATCH · Finland_Ykkosliiga | 2026-09-11 | KTP - JaPS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8154`

### WARNING-640 · LAB_DUP_MATCH · France_Ligue1 | 2026-09-11 | Rennes - Marsiglia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8020`

### WARNING-641 · LAB_DUP_MATCH · France_Ligue2 | 2026-08-21 | Dunkerque - Montpellier
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4496`

### WARNING-642 · LAB_DUP_MATCH · France_Ligue2 | 2026-08-21 | Sochaux - Guingamp
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4535`

### WARNING-643 · LAB_DUP_MATCH · France_Ligue2 | 2026-08-21 | Clermont - Dijon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4581`

### WARNING-644 · LAB_DUP_MATCH · France_Ligue2 | 2026-08-21 | Pau FC - Nancy
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4587`

### WARNING-645 · LAB_DUP_MATCH · France_Ligue2 | 2026-08-21 | Boulogne - Red Star
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4588`

### WARNING-646 · LAB_DUP_MATCH · France_Ligue2 | 2026-09-11 | Rodez - Grenoble
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8008`

### WARNING-647 · LAB_DUP_MATCH · France_Ligue2 | 2026-09-11 | Dijon - Laval
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8095`

### WARNING-648 · LAB_DUP_MATCH · France_Ligue2 | 2026-09-11 | Nancy - Reims
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8181`

### WARNING-649 · LAB_DUP_MATCH · France_Ligue2 | 2026-09-11 | Montpellier - Pau FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8192`

### WARNING-650 · LAB_DUP_MATCH · France_Ligue2 | 2026-09-11 | Clermont - Boulogne
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8195`

### WARNING-651 · LAB_DUP_MATCH · France_Ligue2 | 2026-09-14 | Red Star - Metz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9593`

### WARNING-652 · LAB_DUP_MATCH · Georgia_ErovnuliLiga | 2026-08-21 | Meshakhte Tkibuli - Dinamo Batumi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4377`

### WARNING-653 · LAB_DUP_MATCH · Georgia_ErovnuliLiga | 2026-09-14 | Torpedo Kutaisi - Samgurali
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9550`

### WARNING-654 · LAB_DUP_MATCH · Georgia_ErovnuliLiga | 2026-09-14 | Din. Tbilisi - Gagra
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9569`

### WARNING-655 · LAB_DUP_MATCH · Georgia_ErovnuliLiga | 2026-09-14 | Meshakhte Tkibuli - Rustavi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9591`

### WARNING-656 · LAB_DUP_MATCH · Germany_2Bundesliga | 2026-09-11 | Norimberga - Hannover
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8036`

### WARNING-657 · LAB_DUP_MATCH · Germany_2Bundesliga | 2026-09-11 | Darmstadt - Bielefeld
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8067`

### WARNING-658 · LAB_DUP_MATCH · Germany_3Liga | 2026-09-11 | Viktoria Koln - Rostock
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7984`

### WARNING-659 · LAB_DUP_MATCH · Germany_3Liga | 2026-09-15 | Duisburg - Havelse
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9413`

### WARNING-660 · LAB_DUP_MATCH · Germany_3Liga | 2026-09-15 | Wurzburger Kickers - Aachen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9417`

### WARNING-661 · LAB_DUP_MATCH · Germany_3Liga | 2026-09-15 | Meppen - Viktoria Koln
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9427`

### WARNING-662 · LAB_DUP_MATCH · Germany_3Liga | 2026-09-15 | Regensburg - Dusseldorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9473`

### WARNING-663 · LAB_DUP_MATCH · Germany_3Liga | 2026-09-15 | Grossaspach - Verl
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9489`

### WARNING-664 · LAB_DUP_MATCH · Germany_Bundesliga | 2026-09-11 | Union Berlino - Schalke
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8102`

### WARNING-665 · LAB_DUP_MATCH · Germany_Oberliga_BadenWurttemberg | 2026-08-21 | Oberachern - Teningen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4365`

### WARNING-666 · LAB_DUP_MATCH · Germany_Oberliga_BadenWurttemberg | 2026-08-21 | Balingen - Reutlingen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4368`

### WARNING-667 · LAB_DUP_MATCH · Germany_Oberliga_BadenWurttemberg | 2026-08-21 | Backnang - Nottingen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4408`

### WARNING-668 · LAB_DUP_MATCH · Germany_Oberliga_BadenWurttemberg | 2026-08-21 | Young Boys Reutlingen - Ravensburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4573`

### WARNING-669 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-14 | DJK Bamberg - Stadeln
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2492`

### WARNING-670 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-14 | Ammerthal - Fortuna Regensburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2567`

### WARNING-671 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-14 | Cham - Gebenbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2584`

### WARNING-672 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-14 | Neudrossenfeld - Aschaffenburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2614`

### WARNING-673 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-14 | Kornburg - Bayern Hof
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2642`

### WARNING-674 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-15 | Ingolstadt 2 - Wurzburger FV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3181`

### WARNING-675 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-15 | Bamberg - Regensburg 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3238`

### WARNING-676 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-15 | Neumarkt - Weiden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3387`

### WARNING-677 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-15 | Grossbardorf - Nordlingen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3413`

### WARNING-678 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-21 | DJK Bamberg - Regensburg 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4424`

### WARNING-679 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-21 | Bamberg - Wurzburger FV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4433`

### WARNING-680 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-21 | Kornburg - Fortuna Regensburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4494`

### WARNING-681 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-08-21 | Cham - Aschaffenburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4495`

### WARNING-682 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-09-11 | Gebenbach - Bayern Hof
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8040`

### WARNING-683 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-09-11 | Neudrossenfeld - Bamberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8137`

### WARNING-684 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Nord | 2026-09-15 | Aschaffenburg - Wurzburger FV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9449`

### WARNING-685 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-14 | FC Schwaig - Kirchanschoring
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2473`

### WARNING-686 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-14 | Heimstetten - Schalding
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2497`

### WARNING-687 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-14 | Monaco 1860 2 - Hankofen-Hailing
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2503`

### WARNING-688 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-14 | Pipinsried - Pfaffenhofen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2521`

### WARNING-689 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-14 | Kottern-St. Mang - Landshut
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2538`

### WARNING-690 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-14 | Ismaning - TSV 1880 Wasserburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2549`

### WARNING-691 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-14 | Rosenheim - Deisenhofen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2598`

### WARNING-692 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-14 | Erlbach - Gundelfingen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2617`

### WARNING-693 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-15 | Geretsried - Schwabmunchen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3208`

### WARNING-694 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-21 | Kottern-St. Mang - TSV 1880 Wasserburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4444`

### WARNING-695 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-21 | Heimstetten - Hankofen-Hailing
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4483`

### WARNING-696 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-21 | Monaco 1860 2 - Deisenhofen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4500`

### WARNING-697 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-08-21 | FC Schwaig - Erlbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4540`

### WARNING-698 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-09-11 | TSV 1880 Wasserburg - Heimstetten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8007`

### WARNING-699 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-09-11 | Hankofen-Hailing - Schalding
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8041`

### WARNING-700 · LAB_DUP_MATCH · Germany_Oberliga_Bayern_Sud | 2026-09-11 | Erlbach - Kottern-St. Mang
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8188`

### WARNING-701 · LAB_DUP_MATCH · Germany_Oberliga_Bremen | 2026-08-21 | Grohn - OSC Bremerhaven
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '7', 'OK'), attuali=('0', '7', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4502`

### WARNING-702 · LAB_DUP_MATCH · Germany_Oberliga_Bremen | 2026-08-21 | Brinkumer - Eiche Horn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4532`

### WARNING-703 · LAB_DUP_MATCH · Germany_Oberliga_Bremen | 2026-08-21 | Leher - Aumund-Vegesack
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4570`

### WARNING-704 · LAB_DUP_MATCH · Germany_Oberliga_Bremen | 2026-09-11 | OSC Bremerhaven - Oberneuland
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('12', '0', 'OK'), attuali=('12', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7995`

### WARNING-705 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-14 | Victoria Hamburg - Paloma
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '5', 'OK'), attuali=('1', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2471`

### WARNING-706 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-14 | Vorwarts-Wacker - Niendorfer TSV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2474`

### WARNING-707 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-14 | Suderelbe - Norderstedt 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2479`

### WARNING-708 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-14 | Dassendorf - Altona
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2581`

### WARNING-709 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-14 | Wandsbeker Concordia - ETSV Hamburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2638`

### WARNING-710 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-16 | Pinneberg - Tesla Hamburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3687`

### WARNING-711 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-16 | HEBC Hamburg - HT 16
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3727`

### WARNING-712 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-16 | Sasel - Harksheide
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3795`

### WARNING-713 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-21 | Norderstedt 2 - Sasel
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4411`

### WARNING-714 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-21 | Harksheide - Dassendorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4468`

### WARNING-715 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-08-21 | ETSV Hamburg - HEBC Hamburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4517`

### WARNING-716 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-09-11 | ETSV Hamburg - Harksheide
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8005`

### WARNING-717 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-09-11 | Suderelbe - HT 16
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8028`

### WARNING-718 · LAB_DUP_MATCH · Germany_Oberliga_Hamburg | 2026-09-11 | Wandsbeker Concordia - Norderstedt 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8033`

### WARNING-719 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-15 | Hummetroth - Stadtallendorf
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3212`

### WARNING-720 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-15 | Hadamar - Unter-Flockenbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3220`

### WARNING-721 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-15 | VfB Marburg - Kassel 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3382`

### WARNING-722 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-15 | Fernwald - Hunfelder
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3397`

### WARNING-723 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-15 | Giessen - Hanauer SC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3406`

### WARNING-724 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-16 | CSC 03 Kassel - Friedberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3739`

### WARNING-725 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-16 | RW Walldorf - Pohlheim
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3741`

### WARNING-726 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-16 | Eddersheim - Alzenau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3750`

### WARNING-727 · LAB_DUP_MATCH · Germany_Oberliga_Hessen | 2026-08-16 | Baunatal - Darmstadt U21
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3784`

### WARNING-728 · LAB_DUP_MATCH · Germany_Oberliga_NOFV_Sud | 2026-09-11 | Sandersdorf - Meuselwitz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8149`

### WARNING-729 · LAB_DUP_MATCH · Germany_Oberliga_Niederrhein | 2026-09-11 | Holzheim - Germania Ratingen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8092`

### WARNING-730 · LAB_DUP_MATCH · Germany_Oberliga_Niederrhein | 2026-09-11 | Scherpenberg - Solingen-Wald
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8156`

### WARNING-731 · LAB_DUP_MATCH · Germany_Oberliga_Niederrhein | 2026-09-15 | Dusseldorf 2 - Wuppertaler
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9506`

### WARNING-732 · LAB_DUP_MATCH · Germany_Oberliga_Niedersachsen | 2026-09-11 | BSV Rehden - Verden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8018`

### WARNING-733 · LAB_DUP_MATCH · Germany_Oberliga_Niedersachsen | 2026-09-11 | Hildesheim - Hemmingen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8044`

### WARNING-734 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-14 | Auersmacher - Hertha Wiesbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2506`

### WARNING-735 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-14 | Ahrweiler - Emmelshausen-Karbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2513`

### WARNING-736 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-14 | Elversberg 2 - Worms
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2596`

### WARNING-737 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-15 | RW Koblenz - Diefflen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3031`

### WARNING-738 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-15 | Pirmasens - Mechtersheim
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3036`

### WARNING-739 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-15 | Engers - Schott Mainz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3068`

### WARNING-740 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-15 | Cosmos Koblenz - Eisbachtal
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3092`

### WARNING-741 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-15 | RW Wittlich - TSV 1881 Gau-Odernheim
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3346`

### WARNING-742 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-15 | Gonsenheim - Koblenz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3363`

### WARNING-743 · LAB_DUP_MATCH · Germany_Oberliga_RheinlandPfalzSaar | 2026-08-21 | Diefflen - Pirmasens
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4370`

### WARNING-744 · LAB_DUP_MATCH · Germany_Oberliga_SchleswigHolstein | 2026-08-14 | Eckernforder SV - Kiel 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2475`

### WARNING-745 · LAB_DUP_MATCH · Germany_Oberliga_SchleswigHolstein | 2026-08-14 | Hohenwestedt - Eichede
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2599`

### WARNING-746 · LAB_DUP_MATCH · Germany_Oberliga_SchleswigHolstein | 2026-08-15 | Nordmark Satrup - Oldenburger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3033`

### WARNING-747 · LAB_DUP_MATCH · Germany_Oberliga_SchleswigHolstein | 2026-08-15 | Rapid Lubeck - Lubeck 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3038`

### WARNING-748 · LAB_DUP_MATCH · Germany_Oberliga_SchleswigHolstein | 2026-08-15 | Kaltenkirchen - Phonix Lubeck B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3075`

### WARNING-749 · LAB_DUP_MATCH · Germany_Oberliga_SchleswigHolstein | 2026-08-15 | Rotenhof - PSV Neumunster
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3133`

### WARNING-750 · LAB_DUP_MATCH · Germany_Oberliga_SchleswigHolstein | 2026-08-16 | Flensburg - Kilia Kiel
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3680`

### WARNING-751 · LAB_DUP_MATCH · Germany_Oberliga_SchleswigHolstein | 2026-08-16 | VfR Neumunster - Heider SV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '1', 'OK'), attuali=('6', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3713`

### WARNING-752 · LAB_DUP_MATCH · Germany_Oberliga_Westfalen | 2026-08-21 | Schermbeck 2020 - Bielefeld 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4385`

### WARNING-753 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Memmingen - Monaco 1860
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2470`

### WARNING-754 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Buchbach - Aubstadt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2525`

### WARNING-755 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Eichstatt - Ansbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2526`

### WARNING-756 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Schweinfurt - Bayreuth
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2542`

### WARNING-757 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Augsburg 2 - Vilzing
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2562`

### WARNING-758 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Illertissen - Unterhaching
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2615`

### WARNING-759 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Furth 2 - Landsberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2628`

### WARNING-760 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Eltersdorf - Norinberga 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2633`

### WARNING-761 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-14 | Burghausen - Schwaben Augsburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2634`

### WARNING-762 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-21 | Bayreuth - Illertissen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4422`

### WARNING-763 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-21 | Norinberga 2 - Burghausen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4446`

### WARNING-764 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-21 | Schwaben Augsburg - Augsburg 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4463`

### WARNING-765 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-21 | Ansbach - Buchbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4509`

### WARNING-766 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-21 | Landsberg - Eichstatt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4515`

### WARNING-767 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-08-21 | Eltersdorf - Furth 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4586`

### WARNING-768 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-11 | Burghausen - Landsberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8071`

### WARNING-769 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-11 | Illertissen - Norinberga 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8076`

### WARNING-770 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-11 | Monaco 1860 - Schwaben Augsburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8089`

### WARNING-771 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-11 | Aubstadt - Unterhaching
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8129`

### WARNING-772 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-11 | Buchbach - Bayern 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8151`

### WARNING-773 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-15 | Schweinfurt - Illertissen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9424`

### WARNING-774 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-15 | Bayreuth - Aubstadt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9425`

### WARNING-775 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-15 | Memmingen - Burghausen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9429`

### WARNING-776 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-15 | Furth 2 - Monaco 1860
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9452`

### WARNING-777 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-15 | Norinberga 2 - Schwaben Augsburg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9453`

### WARNING-778 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-15 | Bayern 2 - Augsburg 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9455`

### WARNING-779 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-15 | Vilzing - Ansbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9479`

### WARNING-780 · LAB_DUP_MATCH · Germany_Regionalliga_Bayern | 2026-09-15 | Eltersdorf - Eichstatt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9490`

### WARNING-781 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-15 | Emden - Eimsbutteler
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3035`

### WARNING-782 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-15 | VfB Oldenburg - Norderstedt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3197`

### WARNING-783 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-15 | SC Weiche-08 - Jeddeloh
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '2', 'OK'), attuali=('5', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3366`

### WARNING-784 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-15 | Phonix Lubeck - VfB Lubeck
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3417`

### WARNING-785 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-16 | Amburgo 2 - Drochtersen/Assel
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3668`

### WARNING-786 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-16 | Schoningen - Todesfelde
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3760`

### WARNING-787 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-16 | St. Pauli 2 - Brema 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3790`

### WARNING-788 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-16 | Hannover 2 - Delmenhorst
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3819`

### WARNING-789 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-16 | Bremer - Hannoverscher SC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3883`

### WARNING-790 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-08-21 | Amburgo 2 - Eimsbutteler
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4363`

### WARNING-791 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-09-11 | SC Weiche-08 - Amburgo 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7991`

### WARNING-792 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-09-11 | Delmenhorst - Drochtersen/Assel
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8012`

### WARNING-793 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-09-11 | VfB Oldenburg - Hannover 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8042`

### WARNING-794 · LAB_DUP_MATCH · Germany_Regionalliga_Nord | 2026-09-15 | Drochtersen/Assel - Emden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('8', '2', 'OK'), attuali=('8', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9407`

### WARNING-795 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-14 | Hertha 2 - BFC Dynamo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2511`

### WARNING-796 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-14 | Zwickau - Luckenwalde
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2565`

### WARNING-797 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-14 | Babelsberg - RSV Eintracht
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2594`

### WARNING-798 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-14 | Chemie Leipzig - Jena
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2637`

### WARNING-799 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-15 | Erfurt - Magdeburg 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3081`

### WARNING-800 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-15 | BFC Preussen - Greifswald
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3112`

### WARNING-801 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-15 | Chemnitzer - Aue
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3323`

### WARNING-802 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-16 | Tasmania Berlin - Lokomotive Leipzig
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3722`

### WARNING-803 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-08-16 | Altglienicke - Hallescher
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3772`

### WARNING-804 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-09-11 | Erfurt - RSV Eintracht
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8015`

### WARNING-805 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-09-11 | Altglienicke - Chemnitzer
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8074`

### WARNING-806 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-09-15 | Zwickau - Altglienicke
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9445`

### WARNING-807 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-09-15 | Hertha 2 - Erfurt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9458`

### WARNING-808 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-09-15 | Luckenwalde - BFC Preussen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9470`

### WARNING-809 · LAB_DUP_MATCH · Germany_Regionalliga_Nordost | 2026-09-15 | Hallescher - Jena
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9504`

### WARNING-810 · LAB_DUP_MATCH · Germany_Regionalliga_Sudwest | 2026-09-01 | Kassel - Trier
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6435`

### WARNING-811 · LAB_DUP_MATCH · Germany_Regionalliga_Sudwest | 2026-09-11 | Freiburg 2 - Sandhausen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8038`

### WARNING-812 · LAB_DUP_MATCH · Germany_Regionalliga_Sudwest | 2026-09-11 | Kassel - Offenbach
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8083`

### WARNING-813 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-14 | Westfalia Rhynern - Wiedenbruck
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2461`

### WARNING-814 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-14 | Schalke 2 - Siegen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2467`

### WARNING-815 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-14 | Bergisch Gladbach - Dortmund 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2625`

### WARNING-816 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-14 | Bonner - Lotte
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2630`

### WARNING-817 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-15 | Rodinghausen - Paderborn 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3109`

### WARNING-818 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-15 | Monchengladbach 2 - Bocholt
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3333`

### WARNING-819 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-15 | Bochum 2 - Oberhausen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3365`

### WARNING-820 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-15 | Hilden - Wattenscheid
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3414`

### WARNING-821 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-16 | Colonia 2 - FC Gutersloh
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3854`

### WARNING-822 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-21 | Wattenscheid - Schalke 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4409`

### WARNING-823 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-08-21 | Siegen - Monchengladbach 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4466`

### WARNING-824 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-09-01 | Bocholt - Bonner
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6426`

### WARNING-825 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-09-01 | Oberhausen - Westfalia Rhynern
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6432`

### WARNING-826 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-09-01 | Bochum 2 - Colonia 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6445`

### WARNING-827 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-09-01 | Dortmund 2 - Schalke 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6446`

### WARNING-828 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-09-01 | FC Gutersloh - Hilden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6465`

### WARNING-829 · LAB_DUP_MATCH · Germany_Regionalliga_West | 2026-09-11 | Oberhausen - Schalke 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7987`

### WARNING-830 · LAB_DUP_MATCH · Hungary_NBI | 2026-08-14 | Honved - Vasas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2532`

### WARNING-831 · LAB_DUP_MATCH · Hungary_NBI | 2026-08-15 | Ujpest - MTK Budapest
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3034`

### WARNING-832 · LAB_DUP_MATCH · Hungary_NBI | 2026-08-15 | Nyiregyhaza - Kisvarda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3326`

### WARNING-833 · LAB_DUP_MATCH · Hungary_NBI | 2026-08-16 | Puskas Academy - Paks
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3742`

### WARNING-834 · LAB_DUP_MATCH · Hungary_NBI | 2026-08-16 | Debrecen - Győr
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3806`

### WARNING-835 · LAB_DUP_MATCH · Hungary_NBI | 2026-08-21 | Paks - Ujpest
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4362`

### WARNING-836 · LAB_DUP_MATCH · Hungary_NBI | 2026-08-30 | Puskas Academy - Ferencvaros
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6264`

### WARNING-837 · LAB_DUP_MATCH · Hungary_NBII | 2026-08-15 | Nagykanizsa - Soroksar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3155`

### WARNING-838 · LAB_DUP_MATCH · Hungary_NBII | 2026-08-15 | Kazincbarcika - Kozarmisleny
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3219`

### WARNING-839 · LAB_DUP_MATCH · Hungary_NBII | 2026-08-15 | Kecskemeti - Videoton
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3289`

### WARNING-840 · LAB_DUP_MATCH · Hungary_NBII | 2026-08-15 | DVTK - Ajka
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3299`

### WARNING-841 · LAB_DUP_MATCH · Hungary_NBII | 2026-08-15 | Szeged - Gyirmot
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3334`

### WARNING-842 · LAB_DUP_MATCH · Hungary_NBII | 2026-08-15 | Mezokovesd - BVSC-Zuglo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3423`

### WARNING-843 · LAB_DUP_MATCH · Hungary_NBII | 2026-08-16 | Karcagi - Tiszakecske
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3896`

### WARNING-844 · LAB_DUP_MATCH · Hungary_NBII | 2026-08-16 | Szentlorinc - Csakvari
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3898`

### WARNING-845 · LAB_DUP_MATCH · Iceland_BestaDeildKarla | 2026-08-15 | Thor Akureyri - Keflavik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3199`

### WARNING-846 · LAB_DUP_MATCH · Iceland_BestaDeildKarla | 2026-08-16 | KR Reykjavik - Breidablik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3693`

### WARNING-847 · LAB_DUP_MATCH · Iceland_BestaDeildKarla | 2026-08-16 | Vestmannaeyjar - Akranes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3723`

### WARNING-848 · LAB_DUP_MATCH · Iceland_BestaDeildKarla | 2026-08-16 | Hafnarfjordur - Vikingur Reykjavik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3786`

### WARNING-849 · LAB_DUP_MATCH · Iceland_BestaDeildKarla | 2026-09-01 | KR Reykjavik - Vikingur Reykjavik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6428`

### WARNING-850 · LAB_DUP_MATCH · Iceland_BestaDeildKarla | 2026-09-14 | Vikingur Reykjavik - Keflavik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9539`

### WARNING-851 · LAB_DUP_MATCH · Iceland_Division_1 | 2026-08-21 | Grotta - IR Reykjavik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4399`

### WARNING-852 · LAB_DUP_MATCH · Iceland_Division_1 | 2026-08-21 | Aegir - Afturelding
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '7', 'OK'), attuali=('0', '7', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4404`

### WARNING-853 · LAB_DUP_MATCH · Iceland_Division_2 | 2026-08-09 | Kormakur/Hvot - Throttur Vogar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2132`

### WARNING-854 · LAB_DUP_MATCH · Iceland_Division_2 | 2026-08-14 | Haukar - Hviti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2496`

### WARNING-855 · LAB_DUP_MATCH · Iceland_Division_2 | 2026-08-15 | Selfoss - Fjolnir
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '2', 'OK'), attuali=('6', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3043`

### WARNING-856 · LAB_DUP_MATCH · Iceland_Division_2 | 2026-08-15 | KFG Gardabaer - KFA
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3108`

### WARNING-857 · LAB_DUP_MATCH · Iceland_Division_2 | 2026-08-15 | Throttur Vogar - Dalvik/Reynir
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3144`

### WARNING-858 · LAB_DUP_MATCH · Iceland_Division_2 | 2026-08-15 | Magni - Kormakur/Hvot
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3215`

### WARNING-859 · LAB_DUP_MATCH · Iceland_Division_2 | 2026-08-15 | Kari - Olafsvik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3260`

### WARNING-860 · LAB_DUP_MATCH · Italy_SerieA | 2026-09-11 | Venezia - Fiorentina
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8163`

### WARNING-861 · LAB_DUP_MATCH · Italy_SerieA | 2026-09-14 | Inter - Udinese
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '3', 'OK'), attuali=('5', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9525`

### WARNING-862 · LAB_DUP_MATCH · Italy_SerieA | 2026-09-14 | Como - Parma
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9546`

### WARNING-863 · LAB_DUP_MATCH · Italy_SerieA | 2026-09-14 | Torino - Roma
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9565`

### WARNING-864 · LAB_DUP_MATCH · Italy_SerieB | 2026-09-11 | Pisa - Entella
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8091`

### WARNING-865 · LAB_DUP_MATCH · Italy_SerieB | 2026-09-11 | Empoli - Arezzo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8114`

### WARNING-866 · LAB_DUP_MATCH · Italy_SerieB | 2026-09-11 | Benevento - Verona
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8185`

### WARNING-867 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-11 | Casarano - Barletta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7994`

### WARNING-868 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-11 | Audace Cerignola - Giugliano
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8121`

### WARNING-869 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-11 | Salernitana - Potenza
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8135`

### WARNING-870 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-11 | Altamura - Bari
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8191`

### WARNING-871 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Casarano - Audace Cerignola
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9433`

### WARNING-872 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Barletta - Salernitana
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9436`

### WARNING-873 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Picerno - Catania
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9451`

### WARNING-874 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Casertana - Altamura
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9463`

### WARNING-875 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Crotone - Inter U23
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9464`

### WARNING-876 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Bari - Potenza
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9480`

### WARNING-877 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Giugliano - Cosenza
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '2', 'OK'), attuali=('5', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9484`

### WARNING-878 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Cavese - Sorrento
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9493`

### WARNING-879 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Foggia - Savoia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9510`

### WARNING-880 · LAB_DUP_MATCH · Italy_SerieC_GironeC | 2026-09-15 | Scafatese - Monopoli
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9512`

### WARNING-881 · LAB_DUP_MATCH · Japan_J1League | 2026-08-21 | Tokyo - Chiba
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4407`

### WARNING-882 · LAB_DUP_MATCH · Japan_J1League | 2026-08-21 | Kashiwa - V-Varen Nagasaki
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4473`

### WARNING-883 · LAB_DUP_MATCH · Japan_J1League | 2026-09-11 | Kyoto - Kashiwa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8079`

### WARNING-884 · LAB_DUP_MATCH · Japan_J1League | 2026-09-11 | Kobe - Kashima
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8160`

### WARNING-885 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-07-31 | FC Astana 2 - Arys
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1363`

### WARNING-886 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-07-31 | Tobol 2 - Shakhter K.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1373`

### WARNING-887 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-07-31 | Kairat Almaty 2 - Jaiyq
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1403`

### WARNING-888 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-08-14 | Khan Tengri - Arys
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2558`

### WARNING-889 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-08-14 | Taraz - Turan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2559`

### WARNING-890 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-08-14 | Kaspij Aktau 2 - Yelimay Semey 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2589`

### WARNING-891 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-08-14 | FC Batyr - Jaiyq
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2607`

### WARNING-892 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-08-21 | Turan - Kairat Almaty 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4465`

### WARNING-893 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-08-21 | Shakhter K. - FC Astana 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4470`

### WARNING-894 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-08-21 | Jaiyq - Kaspij Aktau 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4520`

### WARNING-895 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-09-11 | FC Batyr - Tobol 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '5', 'OK'), attuali=('1', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8024`

### WARNING-896 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-09-11 | Kaspij Aktau 2 - Arys
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8120`

### WARNING-897 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-09-11 | Taraz - Khan Tengri
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8130`

### WARNING-898 · LAB_DUP_MATCH · Kazakhstan_FirstLeague | 2026-09-11 | Jaiyq - Shakhter K.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8178`

### WARNING-899 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-09 | FC Astana - Okzhetpes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2161`

### WARNING-900 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-09 | Yelimay Semey - Ertis Pavlodar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2169`

### WARNING-901 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-09 | Atyrau - Aktobe
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2174`

### WARNING-902 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-09 | Tobol - Kaisar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2176`

### WARNING-903 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-15 | Ordabasy - Altai
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3309`

### WARNING-904 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-15 | Kairat Almaty - Ulytau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3370`

### WARNING-905 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-15 | Zhenis - Zhetysu
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3371`

### WARNING-906 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-15 | Kaisar - Aktobe
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3375`

### WARNING-907 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-16 | Kyzylzhar - FC Astana
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3831`

### WARNING-908 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-16 | Kaspij Aktau - Yelimay Semey
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3837`

### WARNING-909 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-16 | Atyrau - Okzhetpes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3857`

### WARNING-910 · LAB_DUP_MATCH · Kazakhstan_PremierLeague | 2026-08-16 | Ertis Pavlodar - Tobol
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3875`

### WARNING-911 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-08-14 | Ozgon - Aldier
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2552`

### WARNING-912 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-08-14 | Neftchi Kochkor-Ata - Abdysh-Ata
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2593`

### WARNING-913 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-08-15 | Kyrgyzaltyn - Bars
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3089`

### WARNING-914 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-08-15 | Ilbirs - Dordoi Bishkek
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3325`

### WARNING-915 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-08-16 | Asia Talas - Bishkek City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3776`

### WARNING-916 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-08-16 | Alay Osh - Talant
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3878`

### WARNING-917 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-08-21 | Talant - Ozgon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4508`

### WARNING-918 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-09-01 | Aldier - Muras United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6441`

### WARNING-919 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-09-01 | Neftchi Kochkor-Ata - Alga
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6448`

### WARNING-920 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-09-11 | Neftchi Kochkor-Ata - Asiagoal Bishkek
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8144`

### WARNING-921 · LAB_DUP_MATCH · Kyrgyzstan_PremierLiga | 2026-09-11 | Ilbirs - Bishkek City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8170`

### WARNING-922 · LAB_DUP_MATCH · Latvia_NakotnesLiga | 2026-07-31 | Super Nova 2 - Riga Mariners
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1391`

### WARNING-923 · LAB_DUP_MATCH · Latvia_NakotnesLiga | 2026-08-09 | Riga Mariners - Tukums 2000 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2150`

### WARNING-924 · LAB_DUP_MATCH · Latvia_NakotnesLiga | 2026-08-15 | Marupe - Super Nova 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3292`

### WARNING-925 · LAB_DUP_MATCH · Latvia_NakotnesLiga | 2026-09-11 | Rezekne - Super Nova 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8110`

### WARNING-926 · LAB_DUP_MATCH · Latvia_NakotnesLiga | 2026-09-14 | RFS 2 - Skanste
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9532`

### WARNING-927 · LAB_DUP_MATCH · Latvia_Virsliga | 2026-08-09 | Riga FC - Ogre United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2135`

### WARNING-928 · LAB_DUP_MATCH · Latvia_Virsliga | 2026-08-09 | Super Nova - FK Liepaja
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2163`

### WARNING-929 · LAB_DUP_MATCH · Latvia_Virsliga | 2026-08-09 | Jelgava - Auda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2173`

### WARNING-930 · LAB_DUP_MATCH · Latvia_Virsliga | 2026-08-21 | Auda - Tukums 2000
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4458`

### WARNING-931 · LAB_DUP_MATCH · Latvia_Virsliga | 2026-08-21 | FK Liepaja - Grobina
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4492`

### WARNING-932 · LAB_DUP_MATCH · Latvia_Virsliga | 2026-09-11 | Ogre United - FK Liepaja
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8052`

### WARNING-933 · LAB_DUP_MATCH · Latvia_Virsliga | 2026-09-11 | Riga FC - Auda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8138`

### WARNING-934 · LAB_DUP_MATCH · Latvia_Virsliga | 2026-09-15 | Super Nova - Riga FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9461`

### WARNING-935 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-07-31 | Hegelmann Litauen 2 - FK Minija
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1389`

### WARNING-936 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-07-31 | BE1 NFA - Jonava
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1398`

### WARNING-937 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-14 | Ekranas - FK Minija
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2546`

### WARNING-938 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-14 | BE1 NFA - Hegelmann Litauen 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2554`

### WARNING-939 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-14 | Siauliai 2 - Zalgiris 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2570`

### WARNING-940 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-14 | Transinvest 2 - Atmosfera
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2572`

### WARNING-941 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-14 | Kauno Zalgiris 2 - Jonava
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2604`

### WARNING-942 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-15 | Dainava Alytus - BFA Vilnius
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3277`

### WARNING-943 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-15 | Garliava - Tauras
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3327`

### WARNING-944 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-15 | Neptunas - Babrungas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3383`

### WARNING-945 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-21 | Hegelmann Litauen 2 - Ekranas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4459`

### WARNING-946 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-21 | Jonava - Siauliai 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4503`

### WARNING-947 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-21 | BE1 NFA - Garliava
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4524`

### WARNING-948 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-08-21 | Babrungas - Tauras
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4548`

### WARNING-949 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-09-11 | Transinvest 2 - Hegelmann Litauen 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8073`

### WARNING-950 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-09-11 | Neptunas - Jonava
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8132`

### WARNING-951 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-09-11 | Babrungas - Atmosfera
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8133`

### WARNING-952 · LAB_DUP_MATCH · Lithuania_ILyga | 2026-09-14 | Siauliai 2 - BE1 NFA
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9567`

### WARNING-953 · LAB_DUP_MATCH · Lithuania_Toplyga | 2026-08-09 | FA Siauliai - Dziugas Telsiai
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2168`

### WARNING-954 · LAB_DUP_MATCH · Lithuania_Toplyga | 2026-08-09 | Banga - Suduva
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2175`

### WARNING-955 · LAB_DUP_MATCH · Lithuania_Toplyga | 2026-08-16 | Kauno Zalgiris - Transinvest
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3801`

### WARNING-956 · LAB_DUP_MATCH · Lithuania_Toplyga | 2026-08-16 | Zalgiris - Banga
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3871`

### WARNING-957 · LAB_DUP_MATCH · Lithuania_Toplyga | 2026-09-15 | Banga - Transinvest
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9476`

### WARNING-958 · LAB_DUP_MATCH · Lithuania_Toplyga | 2026-09-14 | Banga - Transinvest
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9570`

### WARNING-959 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-14 | Alebrijes Oaxaca - Tepatitlan de Morelos
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2620`

### WARNING-960 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-15 | Zacatecas Mineros - Venados
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3120`

### WARNING-961 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-15 | Correcaminos - Tapatio
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3140`

### WARNING-962 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-15 | Atletico La Paz - Piratas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3377`

### WARNING-963 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-15 | Cruz Azul Hidalgo - Atl. Morelia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3385`

### WARNING-964 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-16 | Dorados - Tlaxcala
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3734`

### WARNING-965 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-16 | Leones Negros - Jaiba Brava
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3870`

### WARNING-966 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-16 | Cancun - Alacranes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3902`

### WARNING-967 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-21 | Atl. Morelia - Correcaminos
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4371`

### WARNING-968 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-21 | Venados - Dorados
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4427`

### WARNING-969 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-08-21 | Tepatitlan de Morelos - Tlaxcala
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4490`

### WARNING-970 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-09-11 | Cruz Azul Hidalgo - Piratas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8166`

### WARNING-971 · LAB_DUP_MATCH · Mexico_LigaExpansionMX_Apertura | 2026-09-11 | Alebrijes Oaxaca - Alacranes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8193`

### WARNING-972 · LAB_DUP_MATCH · Mexico_LigaMX_Apertura | 2026-08-16 | U.N.A.M. - Queretaro
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3695`

### WARNING-973 · LAB_DUP_MATCH · Mexico_LigaMX_Apertura | 2026-08-16 | Atlas - Tigres
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3773`

### WARNING-974 · LAB_DUP_MATCH · Mexico_LigaMX_Apertura | 2026-08-16 | Monterrey - Juarez
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '1', 'OK'), attuali=('6', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3824`

### WARNING-975 · LAB_DUP_MATCH · Mexico_LigaMX_Apertura | 2026-08-16 | Atlante - Toluca
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3826`

### WARNING-976 · LAB_DUP_MATCH · Mexico_LigaMX_Apertura | 2026-09-11 | U.N.A.M. - Leon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8173`

### WARNING-977 · LAB_DUP_MATCH · Mexico_LigaMX_Apertura | 2026-09-15 | Leon - Atl. San Luis
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9471`

### WARNING-978 · LAB_DUP_MATCH · Mexico_LigaMX_Apertura | 2026-09-14 | Guadalajara - U.N.A.M.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9571`

### WARNING-979 · LAB_DUP_MATCH · Mexico_LigaMX_Apertura | 2026-09-14 | Santos Laguna - Juarez
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9583`

### WARNING-980 · LAB_DUP_MATCH · Moldova_Liga1_GroupA | 2026-08-14 | Zimbru 2 - Iskra Ribnita
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2523`

### WARNING-981 · LAB_DUP_MATCH · Moldova_Liga1_GroupA | 2026-08-14 | Vulturii Cutezatori - Sparta Selemet
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '2', 'OK'), attuali=('6', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2528`

### WARNING-982 · LAB_DUP_MATCH · Moldova_Liga1_GroupA | 2026-08-15 | FCM Ungheni - Univer Comrat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '2', 'OK'), attuali=('6', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3251`

### WARNING-983 · LAB_DUP_MATCH · Moldova_Liga1_GroupA | 2026-08-21 | Univer Comrat - Vulturii Cutezatori
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4376`

### WARNING-984 · LAB_DUP_MATCH · Moldova_Liga1_GroupA | 2026-08-21 | Zimbru 2 - FCM Ungheni
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4383`

### WARNING-985 · LAB_DUP_MATCH · Moldova_Liga1_GroupA | 2026-08-21 | Iskra Ribnita - Sparta Selemet
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('10', '0', 'OK'), attuali=('10', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4395`

### WARNING-986 · LAB_DUP_MATCH · Moldova_Liga1_GroupA | 2026-09-11 | Zimbru 2 - Univer Comrat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7982`

### WARNING-987 · LAB_DUP_MATCH · Moldova_Liga1_GroupA | 2026-09-11 | Vulturii Cutezatori - Iskra Ribnita
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7989`

### WARNING-988 · LAB_DUP_MATCH · Moldova_Liga1_GroupB | 2026-09-11 | Oguzsport - National Ialoveni
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8194`

### WARNING-989 · LAB_DUP_MATCH · Moldova_SuperLiga | 2026-08-15 | Dacia Buiucani - Petrocub
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3211`

### WARNING-990 · LAB_DUP_MATCH · Moldova_SuperLiga | 2026-08-15 | Politehnica UTM - Balti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3307`

### WARNING-991 · LAB_DUP_MATCH · Moldova_SuperLiga | 2026-08-16 | Real Sireti - S. Tiraspol
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3815`

### WARNING-992 · LAB_DUP_MATCH · Moldova_SuperLiga | 2026-08-16 | Zimbru - Milsami
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3867`

### WARNING-993 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-08-15 | Sutjeska - Otrant
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3416`

### WARNING-994 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-08-16 | Mladost DG - Mornar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3906`

### WARNING-995 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-08-16 | Arsenal Tivat - Buducnost
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3908`

### WARNING-996 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-08-16 | Petrovac - Jezero
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3909`

### WARNING-997 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-08-21 | Mornar - Buducnost
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4583`

### WARNING-998 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-08-30 | Buducnost - Bokelj
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6275`

### WARNING-999 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-09-15 | Jezero - Bokelj
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9514`

### WARNING-1000 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-09-14 | Mornar - Otrant
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9588`

### WARNING-1001 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-09-14 | Mladost DG - Buducnost
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9596`

### WARNING-1002 · LAB_DUP_MATCH · Montenegro_PrvaCrnogorskaLiga | 2026-09-14 | Petrovac - Arsenal Tivat
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9597`

### WARNING-1003 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-08-21 | Maastricht - FC Volendam
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4369`

### WARNING-1004 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-08-21 | FC Emmen - Jong AZ
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4451`

### WARNING-1005 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-08-21 | Dordrecht - Roda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4472`

### WARNING-1006 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-08-21 | Vitesse - Almere City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4522`

### WARNING-1007 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-08-21 | Den Bosch - Eindhoven
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '2', 'OK'), attuali=('5', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4531`

### WARNING-1008 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-08-21 | Helmond - Waalwijk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4543`

### WARNING-1009 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-08-30 | Eindhoven - Heracles
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6243`

### WARNING-1010 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-08-30 | Venlo - FC Emmen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6245`

### WARNING-1011 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-11 | Heracles - Jong AZ
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7980`

### WARNING-1012 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-11 | FC Emmen - De Graafschap
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7993`

### WARNING-1013 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-11 | Breda - Jong Utrecht
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8003`

### WARNING-1014 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-11 | Eindhoven - Dordrecht
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8004`

### WARNING-1015 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-11 | Venlo - Oss
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8011`

### WARNING-1016 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-11 | Helmond - Jong PSV
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8017`

### WARNING-1017 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-11 | Jong Ajax - Waalwijk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8030`

### WARNING-1018 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-11 | Maastricht - Almere City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8108`

### WARNING-1019 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-15 | Jong PSV - Jong AZ
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9418`

### WARNING-1020 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-15 | Jong Utrecht - Jong Ajax
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9428`

### WARNING-1021 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-14 | Jong Utrecht - Jong Ajax
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '1', 'OK'), attuali=('6', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9538`

### WARNING-1022 · LAB_DUP_MATCH · Netherlands_EersteDivisie | 2026-09-14 | Jong PSV - Jong AZ
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9541`

### WARNING-1023 · LAB_DUP_MATCH · Netherlands_Eredivisie | 2026-09-11 | Alkmaar - Willem 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8002`

### WARNING-1024 · LAB_DUP_MATCH · Netherlands_Eredivisie | 2026-09-15 | Ajax - Willem 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9423`

### WARNING-1025 · LAB_DUP_MATCH · NorthMacedonia_1MFL | 2026-08-21 | Bregalnica - Bashkimi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4487`

### WARNING-1026 · LAB_DUP_MATCH · NorthMacedonia_1MFL | 2026-08-21 | FK Skopje - Tikves
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4541`

### WARNING-1027 · LAB_DUP_MATCH · NorthMacedonia_1MFL | 2026-08-30 | Bashkimi - Shkendija Haracine
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6272`

### WARNING-1028 · LAB_DUP_MATCH · NorthMacedonia_1MFL | 2026-09-11 | Tikves - Struga
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8175`

### WARNING-1029 · LAB_DUP_MATCH · NorthMacedonia_1MFL | 2026-09-11 | Arsimi - Shkendija
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8186`

### WARNING-1030 · LAB_DUP_MATCH · NorthMacedonia_1MFL | 2026-09-15 | Shkendija Haracine - FK Skopje
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9507`

### WARNING-1031 · LAB_DUP_MATCH · NorthMacedonia_1MFL | 2026-09-14 | Shkendija Haracine - FK Skopje
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9598`

### WARNING-1032 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-15 | Dundela - Annagh
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3032`

### WARNING-1033 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-15 | Glenavon - Strabane Athletic
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3103`

### WARNING-1034 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-15 | Institute - Loughgall
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3129`

### WARNING-1035 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-15 | Moyola - Ballinamallard
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3149`

### WARNING-1036 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-15 | Newington - Queens Univ.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3194`

### WARNING-1037 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-15 | Rathfriland - Newry City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3226`

### WARNING-1038 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-15 | Warrenpoint - Ards
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3250`

### WARNING-1039 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-15 | H&W Welders - Armagh
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3342`

### WARNING-1040 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-08-21 | Newry City - Warrenpoint
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4423`

### WARNING-1041 · LAB_DUP_MATCH · NorthernIreland_NIFLChampionship | 2026-09-11 | Strabane Athletic - Newry City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8026`

### WARNING-1042 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-08-21 | Linfield - Cliftonville
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4389`

### WARNING-1043 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-08-21 | Ballymena - Glentoran
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4488`

### WARNING-1044 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-09-11 | Coleraine - Ballymena
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8059`

### WARNING-1045 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-09-15 | Ballymena - C. Rangers
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9459`

### WARNING-1046 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-09-15 | Glentoran - Coleraine
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9468`

### WARNING-1047 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-09-15 | Crusaders - Dungannon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9477`

### WARNING-1048 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-09-15 | Larne - Cliftonville
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9491`

### WARNING-1049 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-09-15 | Portadown - Linfield
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9500`

### WARNING-1050 · LAB_DUP_MATCH · NorthernIreland_NIFLPremiership | 2026-09-15 | Limavady - Bangor FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9503`

### WARNING-1051 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-09 | Eik-Tonsberg - Traeff
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2145`

### WARNING-1052 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-09 | Brattvag - Lysekloster
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2152`

### WARNING-1053 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-15 | Mjoendalen - Eik-Tonsberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3241`

### WARNING-1054 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-15 | Lysekloster - Halden
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3247`

### WARNING-1055 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-15 | Vidar - Arendal
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3283`

### WARNING-1056 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-15 | Notodden - Brattvag
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3390`

### WARNING-1057 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-16 | Sandviken - Jerv
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3706`

### WARNING-1058 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-16 | Sotra - Traeff
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3758`

### WARNING-1059 · LAB_DUP_MATCH · Norway_2ndDivision_Group1 | 2026-08-16 | Pors - Bjarg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3830`

### WARNING-1060 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-09 | Rana FK - Skeid
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2144`

### WARNING-1061 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-09 | Tromsdalen - Lørenskog
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2154`

### WARNING-1062 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-15 | Lørenskog - Eidsvold
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '7', 'OK'), attuali=('1', '7', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3234`

### WARNING-1063 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-16 | Ull/Kisa - Trygg/Lade
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3694`

### WARNING-1064 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-16 | Stjordals Blink - Honefoss
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3703`

### WARNING-1065 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-16 | Kjelsaas - Junkeren
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3715`

### WARNING-1066 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-16 | Follo - Rana FK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3737`

### WARNING-1067 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-16 | Skeid - Levanger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3751`

### WARNING-1068 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-08-16 | Grorud - Tromsdalen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3781`

### WARNING-1069 · LAB_DUP_MATCH · Norway_2ndDivision_Group2 | 2026-09-11 | Eidsvold - Ull/Kisa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7992`

### WARNING-1070 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-07-31 | Gamle Oslo - Union Carl Berner
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1354`

### WARNING-1071 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-08-15 | Gamle Oslo - Konnerud
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('7', '1', 'OK'), attuali=('7', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3047`

### WARNING-1072 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-08-15 | Grei - Baerum
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '7', 'OK'), attuali=('1', '7', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3050`

### WARNING-1073 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-08-15 | Frigg - Lokomotiv Oslo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3058`

### WARNING-1074 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-08-15 | Ullern - Union Carl Berner
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3094`

### WARNING-1075 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-08-15 | Heming - Asker
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '5', 'OK'), attuali=('2', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3150`

### WARNING-1076 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-08-16 | Vaalerenga IF 2 - Ready
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3690`

### WARNING-1077 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-09-01 | Nordstrand - Grei
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '5', 'OK'), attuali=('3', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6427`

### WARNING-1078 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-09-15 | Asker - K. Oslo 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9406`

### WARNING-1079 · LAB_DUP_MATCH · Norway_3rdDivision_Group1 | 2026-09-14 | Asker - K. Oslo 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('7', '2', 'OK'), attuali=('7', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9527`

### WARNING-1080 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-07-31 | Herd - Volda TI
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1364`

### WARNING-1081 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-08-09 | Molde 2 - FK Kvik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '3', 'OK'), attuali=('6', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2133`

### WARNING-1082 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-08-15 | Orkla - Spjelkavik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '5', 'OK'), attuali=('2', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3077`

### WARNING-1083 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-08-15 | Herd - Ranheim 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('9', '0', 'OK'), attuali=('9', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3079`

### WARNING-1084 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-08-15 | Strindheim - Ntnui
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3099`

### WARNING-1085 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-08-15 | Nardo - Melhus
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3137`

### WARNING-1086 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-08-15 | Byåsen - Volda TI
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3146`

### WARNING-1087 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-09-15 | Aalesund 2 - Spjelkavik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9408`

### WARNING-1088 · LAB_DUP_MATCH · Norway_3rdDivision_Group2 | 2026-09-14 | Aalesund 2 - Spjelkavik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9528`

### WARNING-1089 · LAB_DUP_MATCH · Norway_3rdDivision_Group3 | 2026-08-15 | Gneist - Forde
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3072`

### WARNING-1090 · LAB_DUP_MATCH · Norway_3rdDivision_Group3 | 2026-08-15 | Sogndal 2 - Fana
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3078`

### WARNING-1091 · LAB_DUP_MATCH · Norway_3rdDivision_Group3 | 2026-08-15 | Austevoll - V. Haugesund
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3113`

### WARNING-1092 · LAB_DUP_MATCH · Norway_3rdDivision_Group3 | 2026-08-15 | Djerv 1919 - Fyllingsdalen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3183`

### WARNING-1093 · LAB_DUP_MATCH · Norway_3rdDivision_Group3 | 2026-08-15 | Varegg - Askoy
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3281`

### WARNING-1094 · LAB_DUP_MATCH · Norway_3rdDivision_Group3 | 2026-09-15 | Åsane 2 - Brann 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9409`

### WARNING-1095 · LAB_DUP_MATCH · Norway_3rdDivision_Group3 | 2026-09-14 | Åsane 2 - Brann 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9529`

### WARNING-1096 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-07-31 | Varhaug - Hinna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '5', 'OK'), attuali=('3', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1370`

### WARNING-1097 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-08-15 | Flekkeroy - Brodd
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3041`

### WARNING-1098 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-08-15 | Vindbjart - Akra
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3102`

### WARNING-1099 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-08-15 | Vag - Mandalskameratene
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3124`

### WARNING-1100 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-08-16 | Odd 2 - Hinna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3685`

### WARNING-1101 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-09-15 | Akra - Odd 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9412`

### WARNING-1102 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-09-15 | Viking 2 - Varhaug
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9426`

### WARNING-1103 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-09-14 | Akra - Odd 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9531`

### WARNING-1104 · LAB_DUP_MATCH · Norway_3rdDivision_Group4 | 2026-09-14 | Viking 2 - Varhaug
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9543`

### WARNING-1105 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-08-15 | Skjervoy - Floeya
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3054`

### WARNING-1106 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-08-15 | Ulfstind - Skjetten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3065`

### WARNING-1107 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-08-16 | Lillestrom 2 - Harstad
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3669`

### WARNING-1108 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-08-16 | Fauske Sprint - Finnsnes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3676`

### WARNING-1109 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-08-16 | Alta - Kongsvinger 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3677`

### WARNING-1110 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-08-16 | Strømsgodset 2 - Skedsmo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3688`

### WARNING-1111 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-09-15 | Fauske Sprint - Strømsgodset 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9403`

### WARNING-1112 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-09-15 | Skjetten - Tromsø 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9414`

### WARNING-1113 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-09-15 | Skedsmo - Lillestrom 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9421`

### WARNING-1114 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-09-14 | Fauske Sprint - Strømsgodset 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '3', 'OK'), attuali=('5', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9524`

### WARNING-1115 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-09-14 | Skjetten - Tromsø 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9530`

### WARNING-1116 · LAB_DUP_MATCH · Norway_3rdDivision_Group5 | 2026-09-14 | Skedsmo - Lillestrom 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9533`

### WARNING-1117 · LAB_DUP_MATCH · Norway_3rdDivision_Group6 | 2026-08-09 | Raelingen - Rade
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2124`

### WARNING-1118 · LAB_DUP_MATCH · Norway_3rdDivision_Group6 | 2026-08-09 | Sarpsborg 08 2 - Brumunddal
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('11', '0', 'OK'), attuali=('11', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2139`

### WARNING-1119 · LAB_DUP_MATCH · Norway_3rdDivision_Group6 | 2026-08-15 | Brumunddal - Raelingen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3067`

### WARNING-1120 · LAB_DUP_MATCH · Norway_3rdDivision_Group6 | 2026-08-15 | Sandefjord 2 - Bjorkelangen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3091`

### WARNING-1121 · LAB_DUP_MATCH · Norway_3rdDivision_Group6 | 2026-08-15 | Rade - Drobak-Frogn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3162`

### WARNING-1122 · LAB_DUP_MATCH · Norway_3rdDivision_Group6 | 2026-08-15 | Oppsal - Elverum
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3179`

### WARNING-1123 · LAB_DUP_MATCH · Norway_3rdDivision_Group6 | 2026-08-15 | Orn - SK Gjovik-Lyn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3328`

### WARNING-1124 · LAB_DUP_MATCH · Norway_3rdDivision_Group6 | 2026-09-01 | SK Gjovik-Lyn - Brumunddal
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6443`

### WARNING-1125 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-07-31 | Vålerenga - HamKam
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1380`

### WARNING-1126 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-07-31 | Bodo/Glimt - Lilleström
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1400`

### WARNING-1127 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-08-09 | Lilleström - Rosenborg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2160`

### WARNING-1128 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-08-14 | Rosenborg - Viking
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2544`

### WARNING-1129 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-08-15 | KFUM Oslo - Lilleström
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3361`

### WARNING-1130 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-08-16 | Brann - HamKam
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3707`

### WARNING-1131 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-08-16 | Aalesund - Vålerenga
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '5', 'OK'), attuali=('5', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3755`

### WARNING-1132 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-08-16 | Molde - Tromsø
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3783`

### WARNING-1133 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-08-16 | Fredrikstad - Kristiansund
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3841`

### WARNING-1134 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-08-16 | Sarpsborg 08 - Sandefjord
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3866`

### WARNING-1135 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-09-15 | Bodo/Glimt - Sandefjord
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9460`

### WARNING-1136 · LAB_DUP_MATCH · Norway_Eliteserien | 2026-09-14 | Bodo/Glimt - Sandefjord
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9557`

### WARNING-1137 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-09 | Haugesund - Raufoss
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('7', '2', 'OK'), attuali=('7', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2129`

### WARNING-1138 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-09 | Åsane - Kongsvinger
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2130`

### WARNING-1139 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-09 | Strømmen - Ranheim
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2131`

### WARNING-1140 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-09 | Strömsgodset - Egersund
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2137`

### WARNING-1141 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-09 | Sogndal - Bryne
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2148`

### WARNING-1142 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-09 | Sandnes - Hodd
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2156`

### WARNING-1143 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-15 | Ranheim - Strömsgodset
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3082`

### WARNING-1144 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-15 | Lyn - Odd
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3138`

### WARNING-1145 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-15 | Bryne - Moss
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3218`

### WARNING-1146 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-16 | Kongsvinger - Haugesund
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3670`

### WARNING-1147 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-16 | Hodd - Strømmen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3743`

### WARNING-1148 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-16 | Sogndal - Sandnes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3762`

### WARNING-1149 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-16 | Raufoss - Åsane
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3764`

### WARNING-1150 · LAB_DUP_MATCH · Norway_OBOSLigaen | 2026-08-16 | Egersund - Stabaek
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3765`

### WARNING-1151 · LAB_DUP_MATCH · Paraguay_DivisionIntermedia | 2026-08-21 | Dep. Capiata - Guairena
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4551`

### WARNING-1152 · LAB_DUP_MATCH · Paraguay_DivisionIntermedia | 2026-08-21 | Sol De America - Resistencia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4568`

### WARNING-1153 · LAB_DUP_MATCH · Paraguay_DivisionIntermedia | 2026-09-11 | 12 de Junio - Atl. Tembetary
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8045`

### WARNING-1154 · LAB_DUP_MATCH · Paraguay_DivisionIntermedia | 2026-09-15 | Atl. Tembetary - Sp. Carapegua
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9483`

### WARNING-1155 · LAB_DUP_MATCH · Paraguay_DivisionIntermedia | 2026-09-15 | Independiente F.B.C. - Encarnacion FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9497`

### WARNING-1156 · LAB_DUP_MATCH · Paraguay_DivisionIntermedia | 2026-09-14 | Benjamin Aceval - Paraguari AC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9544`

### WARNING-1157 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-14 | Grau - Comerciantes Unidos
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2539`

### WARNING-1158 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-15 | Cusco - Juan Pablo 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3206`

### WARNING-1159 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-15 | Los Chankas - Melgar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3294`

### WARNING-1160 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-15 | AD Tarma - Alianza Atl.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3313`

### WARNING-1161 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-16 | A. Lima - Cajamarca
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3692`

### WARNING-1162 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-16 | FC Cajamarca - U. de Deportes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3821`

### WARNING-1163 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-16 | Sporting Cristal - Huancayo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3900`

### WARNING-1164 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-16 | Moquegua - Sport Boys
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3907`

### WARNING-1165 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-21 | FC Cajamarca - Grau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4530`

### WARNING-1166 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-08-21 | Alianza Atl. - Sporting Cristal
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4554`

### WARNING-1167 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-09-01 | Grau - Melgar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6464`

### WARNING-1168 · LAB_DUP_MATCH · Peru_Liga1_Clausura | 2026-09-11 | Cajamarca - Juan Pablo 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8077`

### WARNING-1169 · LAB_DUP_MATCH · Peru_Liga2 | 2026-08-21 | Sport Huancayo 2 - Estudiantil CNI
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4579`

### WARNING-1170 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-14 | Grodzisk M. - S. Rzeszow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2608`

### WARNING-1171 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-14 | Ruch - Lechia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2618`

### WARNING-1172 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-15 | Chrobry Glogow - Podbeskidzie
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3213`

### WARNING-1173 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-15 | Odra Opole - Warta Poznan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3280`

### WARNING-1174 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-15 | Pogon Siedlce - Polonia W.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3336`

### WARNING-1175 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-16 | Stal Mielec - Polonia B.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '2', 'OK'), attuali=('5', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3675`

### WARNING-1176 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-16 | LKS Lodz - Termalica B-B.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3724`

### WARNING-1177 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-16 | Skierniewice - Legnica
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3891`

### WARNING-1178 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-21 | Chrobry Glogow - Warta Poznan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4418`

### WARNING-1179 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-21 | Lechia - Pogon Siedlce
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4461`

### WARNING-1180 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-30 | Arka - Polonia B.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6247`

### WARNING-1181 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-30 | Legnica - Warta Poznan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6261`

### WARNING-1182 · LAB_DUP_MATCH · Poland_Division1 | 2026-08-30 | Chrobry Glogow - Ruch
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6274`

### WARNING-1183 · LAB_DUP_MATCH · Poland_Division1 | 2026-09-11 | Polonia W. - Polonia B.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8031`

### WARNING-1184 · LAB_DUP_MATCH · Poland_Division1 | 2026-09-11 | Puszcza - LKS Lodz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8179`

### WARNING-1185 · LAB_DUP_MATCH · Poland_Division1 | 2026-09-14 | Stal Mielec - Termalica B-B.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9536`

### WARNING-1186 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-14 | Leczna - Podhale Nowy Targ
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '2', 'OK'), attuali=('5', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2611`

### WARNING-1187 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-15 | Swit Szczecin - Sandecja
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3258`

### WARNING-1188 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-15 | Slask 2 - Chojniczanka
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3273`

### WARNING-1189 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-15 | R. Rzeszow - Tychy
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3362`

### WARNING-1190 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-15 | Kleczew - Bielsko-Biala
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3372`

### WARNING-1191 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-16 | Hutnik Krakow - Legia 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3720`

### WARNING-1192 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-16 | Pruszkow - Ol. Grudziadz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3725`

### WARNING-1193 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-16 | S. Wola - Avia Swidnik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3794`

### WARNING-1194 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-16 | Zawisza - Z. Gora
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3877`

### WARNING-1195 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-21 | Chojniczanka - S. Wola
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4471`

### WARNING-1196 · LAB_DUP_MATCH · Poland_Division2 | 2026-08-21 | Sandecja - Leczna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4529`

### WARNING-1197 · LAB_DUP_MATCH · Poland_Division2 | 2026-09-11 | R. Rzeszow - Z. Gora
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7999`

### WARNING-1198 · LAB_DUP_MATCH · Poland_Division2 | 2026-09-11 | Kleczew - Ol. Grudziadz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8125`

### WARNING-1199 · LAB_DUP_MATCH · Poland_Division2 | 2026-09-11 | Pruszkow - Tychy
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8145`

### WARNING-1200 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-14 | Legia - Radomiak Radom
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2491`

### WARNING-1201 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-15 | Piast - Wieczysta Krakow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3107`

### WARNING-1202 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-15 | Zaglebie - Slask
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3347`

### WARNING-1203 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-15 | Widzew Lodz - Korona
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3405`

### WARNING-1204 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-16 | Gornik Zabrze - Wisla
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3667`

### WARNING-1205 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-16 | Motor Lublin - Katowice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3671`

### WARNING-1206 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-16 | Cracovia - Rakow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3885`

### WARNING-1207 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-21 | Cracovia - Wieczysta Krakow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4464`

### WARNING-1208 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-30 | Gornik Zabrze - Katowice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6248`

### WARNING-1209 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-08-30 | Rakow - Jagiellonia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '5', 'OK'), attuali=('2', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6252`

### WARNING-1210 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-09-11 | Wisla - Jagiellonia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8023`

### WARNING-1211 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-09-11 | Rakow - Motor Lublin
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8047`

### WARNING-1212 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-09-15 | Rakow - Zaglebie
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9462`

### WARNING-1213 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-09-15 | Korona - Gornik Zabrze
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9481`

### WARNING-1214 · LAB_DUP_MATCH · Poland_Ekstraklasa | 2026-09-14 | Radomiak Radom - Piast
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9574`

### WARNING-1215 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-14 | Mazovia Minsk Mazowiecki - Zabki
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2494`

### WARNING-1216 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-14 | T. Mazowiecki - LKS Lomza
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '2', 'OK'), attuali=('5', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2557`

### WARNING-1217 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-14 | Suwalki - Troszyn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2566`

### WARNING-1218 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-14 | Weszlo - Mlawa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2569`

### WARNING-1219 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-15 | Lidzbark Warminski - Plock 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3039`

### WARNING-1220 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-15 | Zambrow - Elblag
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3093`

### WARNING-1221 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-15 | Widzew Lodz 2 - Swit
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3130`

### WARNING-1222 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-15 | Warta Sieradz - Jagiellonia 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3205`

### WARNING-1223 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-08-15 | Pelikan - LKS Lodz 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3388`

### WARNING-1224 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-09-11 | Widzew Lodz 2 - Mazovia Minsk Mazowiecki
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8016`

### WARNING-1225 · LAB_DUP_MATCH · Poland_IIILiga_Group1 | 2026-09-11 | Zabki - T. Mazowiecki
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8058`

### WARNING-1226 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-14 | Wrzesnia - Luzino
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2490`

### WARNING-1227 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-14 | Chemik Bydgoszcz - Sroda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2524`

### WARNING-1228 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-14 | Unia Swarzedz - Notec Czarnkow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2563`

### WARNING-1229 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-15 | Lipno Steszew - Kluczevia Stargard
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3142`

### WARNING-1230 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-15 | Gedania Gdansk - Wda Swiecie
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3164`

### WARNING-1231 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-15 | Blekitni Stargard - Lech 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3239`

### WARNING-1232 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-15 | Grom Nowy Staw - Elana Torun
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3272`

### WARNING-1233 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-15 | Kotwica Kornik - KKS Kalisz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3393`

### WARNING-1234 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-08-15 | Koszalin - Swinoujscie
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3404`

### WARNING-1235 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-09-11 | Luzino - Grom Nowy Staw
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7986`

### WARNING-1236 · LAB_DUP_MATCH · Poland_IIILiga_Group2 | 2026-09-11 | Sroda - Unia Swarzedz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8054`

### WARNING-1237 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-14 | Polkowice - Legnica 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2462`

### WARNING-1238 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-14 | Brzeg - BKS Sparta Katowice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2587`

### WARNING-1239 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-14 | Carina Gubin - Jelenia Gora
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2624`

### WARNING-1240 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-15 | Stilon Gorzow - Nysa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3055`

### WARNING-1241 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-15 | Sulow - Warta Gorzow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3175`

### WARNING-1242 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-15 | Goczalkowice Zdroj - Sleza Wroclaw
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3343`

### WARNING-1243 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-15 | Bytom Odrzanski - Kluczbork
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3358`

### WARNING-1244 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-16 | Zaglebie 2 - Rakow 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3785`

### WARNING-1245 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-08-16 | ROW Rybnik - Sosnowiec
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3890`

### WARNING-1246 · LAB_DUP_MATCH · Poland_IIILiga_Group3 | 2026-09-11 | Carina Gubin - Bytom Odrzanski
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8174`

### WARNING-1247 · LAB_DUP_MATCH · Poland_IIILiga_Group4 | 2026-09-11 | Biala Podlaska - Wieczysta Krakow 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8182`

### WARNING-1248 · LAB_DUP_MATCH · Portugal_Liga3_SerieA | 2026-08-21 | Fafe - Guimaraes B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4510`

### WARNING-1249 · LAB_DUP_MATCH · Portugal_LigaPortugal | 2026-09-15 | Moreirense - Maritimo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9430`

### WARNING-1250 · LAB_DUP_MATCH · Portugal_LigaPortugal | 2026-09-15 | Rio Ave - Estrela
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9438`

### WARNING-1251 · LAB_DUP_MATCH · Portugal_LigaPortugal | 2026-09-15 | Braga - Estoril
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9498`

### WARNING-1252 · LAB_DUP_MATCH · Portugal_LigaPortugal | 2026-09-14 | Rio Ave - Estrela
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9537`

### WARNING-1253 · LAB_DUP_MATCH · Portugal_LigaPortugal | 2026-09-14 | Moreirense - Maritimo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9542`

### WARNING-1254 · LAB_DUP_MATCH · Portugal_LigaPortugal | 2026-09-14 | Braga - Estoril
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9592`

### WARNING-1255 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-08-21 | Tondela - Academica
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4481`

### WARNING-1256 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-08-21 | Benfica B - Portimonense
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4584`

### WARNING-1257 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-08-30 | FC Porto B - Penafiel
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6263`

### WARNING-1258 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-08-30 | Sporting B - Farense
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6267`

### WARNING-1259 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-08-30 | Amarante - Benfica B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6268`

### WARNING-1260 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-09-11 | Torreense - Leixoes
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8124`

### WARNING-1261 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-09-11 | Academica - Benfica B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8189`

### WARNING-1262 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-09-15 | FC Porto B - Vizela
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9499`

### WARNING-1263 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-09-15 | Sporting B - Lusitania FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9511`

### WARNING-1264 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-09-14 | FC Porto B - Vizela
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9576`

### WARNING-1265 · LAB_DUP_MATCH · Portugal_LigaPortugal2 | 2026-09-14 | Sporting B - Lusitania FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9580`

### WARNING-1266 · LAB_DUP_MATCH · Romania_Liga2 | 2026-08-21 | Chindia Targoviste - CS Din. Bucuresti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4440`

### WARNING-1267 · LAB_DUP_MATCH · Romania_Liga2 | 2026-09-15 | CSM Resita - FC Bacau
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9434`

### WARNING-1268 · LAB_DUP_MATCH · Romania_Superliga | 2026-08-14 | FC Arges - Farul Constanta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2613`

### WARNING-1269 · LAB_DUP_MATCH · Romania_Superliga | 2026-08-14 | FC Voluntari - Petrolul
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2626`

### WARNING-1270 · LAB_DUP_MATCH · Romania_Superliga | 2026-08-15 | Rapid Bucarest - Din. Bucuresti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3411`

### WARNING-1271 · LAB_DUP_MATCH · Romania_Superliga | 2026-08-15 | Csikszereda M. Ciuc - Sepsi Sf. Gheorghe
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3418`

### WARNING-1272 · LAB_DUP_MATCH · Romania_Superliga | 2026-08-16 | Corvinul - CFR Cluj
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3808`

### WARNING-1273 · LAB_DUP_MATCH · Romania_Superliga | 2026-08-16 | Otelul - Univ. Craiova
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3840`

### WARNING-1274 · LAB_DUP_MATCH · Romania_Superliga | 2026-08-21 | Petrolul - Rapid Bucarest
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4580`

### WARNING-1275 · LAB_DUP_MATCH · Romania_Superliga | 2026-08-30 | Farul Constanta - Botosani
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6255`

### WARNING-1276 · LAB_DUP_MATCH · Romania_Superliga | 2026-09-11 | Farul Constanta - UTA Arad
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8155`

### WARNING-1277 · LAB_DUP_MATCH · Romania_Superliga | 2026-09-11 | Csikszereda M. Ciuc - Din. Bucuresti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8162`

### WARNING-1278 · LAB_DUP_MATCH · Romania_Superliga | 2026-09-14 | U. Cluj - Otelul
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9561`

### WARNING-1279 · LAB_DUP_MATCH · Romania_Superliga | 2026-09-14 | FCSB - Petrolul
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9573`

### WARNING-1280 · LAB_DUP_MATCH · Russia_FNL | 2026-08-14 | R. Volgograd - Ural
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2619`

### WARNING-1281 · LAB_DUP_MATCH · Russia_FNL | 2026-08-14 | Neftekhimik - Yaroslavl
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2627`

### WARNING-1282 · LAB_DUP_MATCH · Russia_FNL | 2026-08-15 | Sochi - Ulyanovsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3204`

### WARNING-1283 · LAB_DUP_MATCH · Russia_FNL | 2026-08-15 | Tekstilshtik - Pari NN
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3244`

### WARNING-1284 · LAB_DUP_MATCH · Russia_FNL | 2026-08-15 | Yenisey - Kamaz
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3262`

### WARNING-1285 · LAB_DUP_MATCH · Russia_FNL | 2026-08-15 | SKA Khabarovsk - Veles Moscow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3279`

### WARNING-1286 · LAB_DUP_MATCH · Russia_FNL | 2026-08-15 | Leningradets - Arsenal Tula
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3322`

### WARNING-1287 · LAB_DUP_MATCH · Russia_FNL | 2026-08-15 | Chelyabinsk - Torpedo Moscow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3354`

### WARNING-1288 · LAB_DUP_MATCH · Russia_FNL | 2026-08-16 | Sochi - Ulyanovsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3766`

### WARNING-1289 · LAB_DUP_MATCH · Russia_FNL | 2026-08-21 | Torpedo Moscow - S. Kostroma
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4518`

### WARNING-1290 · LAB_DUP_MATCH · Russia_FNL | 2026-08-30 | SKA Khabarovsk - Torpedo Moscow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6258`

### WARNING-1291 · LAB_DUP_MATCH · Russia_FNL | 2026-09-14 | Veles Moscow - Sochi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9563`

### WARNING-1292 · LAB_DUP_MATCH · Russia_FNL | 2026-09-14 | Kamaz - Chelyabinsk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9581`

### WARNING-1293 · LAB_DUP_MATCH · Russia_FNL | 2026-09-14 | Yaroslavl - Ural
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9582`

### WARNING-1294 · LAB_DUP_MATCH · Russia_FNL | 2026-09-14 | S. Kostroma - Neftekhimik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9595`

### WARNING-1295 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-08-14 | Orenburg - Lok. Mosca
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2571`

### WARNING-1296 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-08-15 | FK Rostov - Kazan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3265`

### WARNING-1297 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-08-15 | Krasnodar - Akhmat Grozny
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3267`

### WARNING-1298 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-08-15 | Rodina Moscow - Akron Togliatti
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3271`

### WARNING-1299 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-08-15 | CSKA Mosca - F. Voronezh
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3330`

### WARNING-1300 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-08-16 | Baltika - Sp. Mosca
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3711`

### WARNING-1301 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-08-16 | Zenit - Din. Mosca
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3717`

### WARNING-1302 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-08-16 | Samara - Dynamo Makhachkala
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3853`

### WARNING-1303 · LAB_DUP_MATCH · Russia_PremierLeague | 2026-09-11 | Samara - Rodina Moscow
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8064`

### WARNING-1304 · LAB_DUP_MATCH · SaudiArabia_ProfessionalLeague | 2026-09-01 | Al-Hilal - Al Ahli SC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6440`

### WARNING-1305 · LAB_DUP_MATCH · SaudiArabia_ProfessionalLeague | 2026-09-11 | Al Ahli SC - Al Hazem
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8088`

### WARNING-1306 · LAB_DUP_MATCH · SaudiArabia_ProfessionalLeague | 2026-09-11 | Al Qadsiah - Al-Ettifaq
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8107`

### WARNING-1307 · LAB_DUP_MATCH · SaudiArabia_ProfessionalLeague | 2026-09-11 | Al-Faysaly - Al-Ittihad FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8176`

### WARNING-1308 · LAB_DUP_MATCH · Scotland_Premiership | 2026-09-15 | Hibernian - Kilmarnock
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9431`

### WARNING-1309 · LAB_DUP_MATCH · Scotland_Premiership | 2026-09-15 | Falkirk - Hearts
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9444`

### WARNING-1310 · LAB_DUP_MATCH · Scotland_Premiership | 2026-09-15 | Motherwell - Aberdeen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9495`

### WARNING-1311 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-08-14 | Sp. Subotica - Teleoptik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2493`

### WARNING-1312 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-08-14 | Loznica - Borac 1926
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2639`

### WARNING-1313 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-08-14 | Napredak - Metalac
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2641`

### WARNING-1314 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-08-14 | Vozdovac - Graficar Beograd
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2648`

### WARNING-1315 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-08-15 | Smederevo - Bor 1919
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3148`

### WARNING-1316 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-08-15 | Javor - Vrsac
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3389`

### WARNING-1317 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-08-15 | Jedinstvo U. - TSC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3421`

### WARNING-1318 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-08-15 | Proleter 023 - Dubocica
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3422`

### WARNING-1319 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-09-01 | Teleoptik - Vozdovac
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6468`

### WARNING-1320 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-09-11 | Sp. Subotica - Napredak
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8101`

### WARNING-1321 · LAB_DUP_MATCH · Serbia_PrvaLiga | 2026-09-11 | Metalac - Dubocica
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8140`

### WARNING-1322 · LAB_DUP_MATCH · Serbia_SuperLiga | 2026-08-15 | Cukaricki - OFK Belgrado
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3278`

### WARNING-1323 · LAB_DUP_MATCH · Serbia_SuperLiga | 2026-08-15 | Radnik - Macva
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3402`

### WARNING-1324 · LAB_DUP_MATCH · Serbia_SuperLiga | 2026-08-16 | Partizan - Radnicki 1923
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3754`

### WARNING-1325 · LAB_DUP_MATCH · Serbia_SuperLiga | 2026-08-16 | IMT Novi Beograd - Radnicki Nis
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3869`

### WARNING-1326 · LAB_DUP_MATCH · Serbia_SuperLiga | 2026-08-16 | Zemun - Mladost
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3895`

### WARNING-1327 · LAB_DUP_MATCH · Serbia_SuperLiga | 2026-09-11 | Zeleznicar Pancevo - Macva
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8169`

### WARNING-1328 · LAB_DUP_MATCH · Serbia_SuperLiga | 2026-09-14 | Zemun - Radnik
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9586`

### WARNING-1329 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-08-14 | Pohronie - MFK Bytca
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2482`

### WARNING-1330 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-08-14 | L. Mikulas - Zvolen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2644`

### WARNING-1331 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-08-15 | Samorin - Lehota p. V.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3110`

### WARNING-1332 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-08-15 | Z. Moravce-Vrable - Zilina B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3368`

### WARNING-1333 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-08-15 | Inter Bratislava - Galanta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3403`

### WARNING-1334 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-08-16 | Malzenice - Povazska Bystrica
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3704`

### WARNING-1335 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-08-16 | Petrzalka - Presov
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3848`

### WARNING-1336 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-09-11 | Pohronie - L. Mikulas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8049`

### WARNING-1337 · LAB_DUP_MATCH · Slovakia_2Liga | 2026-09-14 | Z. Moravce-Vrable - Zvolen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9587`

### WARNING-1338 · LAB_DUP_MATCH · Slovakia_3Liga_West | 2026-08-21 | MSK Senec - Dun. Streda B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4361`

### WARNING-1339 · LAB_DUP_MATCH · Slovakia_3Liga_West | 2026-09-11 | Myjava - Trencin B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8034`

### WARNING-1340 · LAB_DUP_MATCH · Slovakia_NikeLiga | 2026-08-15 | Skalica - Kosice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3044`

### WARNING-1341 · LAB_DUP_MATCH · Slovakia_NikeLiga | 2026-08-15 | Slovan Bratislava - Ruzomberok
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3125`

### WARNING-1342 · LAB_DUP_MATCH · Slovakia_NikeLiga | 2026-08-15 | Podbrezova - Trencin
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3207`

### WARNING-1343 · LAB_DUP_MATCH · Slovakia_NikeLiga | 2026-08-15 | Banska Bystrica - Zilina
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3298`

### WARNING-1344 · LAB_DUP_MATCH · Slovakia_NikeLiga | 2026-08-16 | Komarno - Dun. Streda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3887`

### WARNING-1345 · LAB_DUP_MATCH · Slovakia_NikeLiga | 2026-08-16 | Trnava - Michalovce
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3888`

### WARNING-1346 · LAB_DUP_MATCH · Slovenia_2SNL | 2026-08-21 | NK Krka - Slovan Ljubljana
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4526`

### WARNING-1347 · LAB_DUP_MATCH · Slovenia_2SNL | 2026-08-21 | Jadran Dekani - NK Jesenice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4546`

### WARNING-1348 · LAB_DUP_MATCH · Slovenia_2SNL | 2026-08-21 | Triglav - Brezice
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4549`

### WARNING-1349 · LAB_DUP_MATCH · Slovenia_2SNL | 2026-09-11 | Primorje - Bilje
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8021`

### WARNING-1350 · LAB_DUP_MATCH · Slovenia_2SNL | 2026-09-11 | Tabor Sezana - Dravinja
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8180`

### WARNING-1351 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-15 | Nafta - Celje
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3351`

### WARNING-1352 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-15 | O. Ljubljana - Maribor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3419`

### WARNING-1353 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-16 | Grosuplje - Mura
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3825`

### WARNING-1354 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-16 | Koper - Bravo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3855`

### WARNING-1355 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-16 | Radomlje - Aluminij
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3884`

### WARNING-1356 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-21 | O. Ljubljana - Nafta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4561`

### WARNING-1357 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-21 | Aluminij - Grosuplje
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4562`

### WARNING-1358 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-30 | Grosuplje - Celje
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6251`

### WARNING-1359 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-08-30 | Nafta - Maribor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6265`

### WARNING-1360 · LAB_DUP_MATCH · Slovenia_PrvaLiga | 2026-09-11 | Grosuplje - Nafta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8084`

### WARNING-1361 · LAB_DUP_MATCH · Somalia_NationalLeague | 2026-07-12 | Raadsan - Heegan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:334`

### WARNING-1362 · LAB_DUP_MATCH · Somalia_NationalLeague | 2026-08-09 | Gaadiidka - Mogadishu City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2166`

### WARNING-1363 · LAB_DUP_MATCH · Somalia_NationalLeague | 2026-08-12 | Jubba - Gantaalaha Afgooye
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '5', 'OK'), attuali=('1', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2241`

### WARNING-1364 · LAB_DUP_MATCH · Somalia_NationalLeague | 2026-08-12 | Jeenyo - Jazeera
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2243`

### WARNING-1365 · LAB_DUP_MATCH · Somalia_NationalLeague | 2026-08-14 | Gaadiidka - Dekedaha
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2537`

### WARNING-1366 · LAB_DUP_MATCH · SouthKorea_KLeague1 | 2026-08-15 | Jeju SK - Anyang
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3329`

### WARNING-1367 · LAB_DUP_MATCH · SouthKorea_KLeague1 | 2026-08-15 | Seoul - Daejeon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3350`

### WARNING-1368 · LAB_DUP_MATCH · SouthKorea_KLeague1 | 2026-08-15 | Gwangju - Pohang
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3394`

### WARNING-1369 · LAB_DUP_MATCH · SouthKorea_KLeague1 | 2026-08-16 | Ulsan HD - Gangwon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3860`

### WARNING-1370 · LAB_DUP_MATCH · SouthKorea_KLeague1 | 2026-08-16 | Incheon - Gimcheon Sangmu
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3880`

### WARNING-1371 · LAB_DUP_MATCH · SouthKorea_KLeague1 | 2026-08-16 | Bucheon - Jeonbuk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3893`

### WARNING-1372 · LAB_DUP_MATCH · SouthKorea_KLeague2 | 2026-08-15 | Busan - Hwaseong
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3266`

### WARNING-1373 · LAB_DUP_MATCH · SouthKorea_KLeague2 | 2026-08-15 | Cheongju Jikji - Jeonnam
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3317`

### WARNING-1374 · LAB_DUP_MATCH · SouthKorea_KLeague2 | 2026-08-15 | Suwon Bluewings - Suwon FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3332`

### WARNING-1375 · LAB_DUP_MATCH · SouthKorea_KLeague2 | 2026-08-15 | Gimhae - Gyeongnam
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3344`

### WARNING-1376 · LAB_DUP_MATCH · SouthKorea_KLeague2 | 2026-08-16 | Seoul E-Land - Ansan Greeners
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3749`

### WARNING-1377 · LAB_DUP_MATCH · SouthKorea_KLeague2 | 2026-08-16 | Daegu - Asan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3812`

### WARNING-1378 · LAB_DUP_MATCH · SouthKorea_KLeague2 | 2026-08-16 | Gimpo FC - Cheonan City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3843`

### WARNING-1379 · LAB_DUP_MATCH · SouthKorea_KLeague2 | 2026-08-16 | Paju Frontier - Seongnam
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3892`

### WARNING-1380 · LAB_DUP_MATCH · Spain_LaLiga | 2026-09-11 | Siviglia - Valencia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8051`

### WARNING-1381 · LAB_DUP_MATCH · Spain_LaLiga | 2026-09-15 | Elche - Real Madrid
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9443`

### WARNING-1382 · LAB_DUP_MATCH · Spain_LaLiga | 2026-09-15 | Vallecano - Espanyol
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9450`

### WARNING-1383 · LAB_DUP_MATCH · Spain_LaLiga | 2026-09-15 | Alaves - Valencia
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9465`

### WARNING-1384 · LAB_DUP_MATCH · Spain_LaLiga | 2026-09-14 | Villarreal - Betis
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9545`

### WARNING-1385 · LAB_DUP_MATCH · Spain_LaLiga2 | 2026-09-11 | Burgos CF - Ceuta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8098`

### WARNING-1386 · LAB_DUP_MATCH · Spain_LaLiga2 | 2026-09-14 | Celta Vigo B - Eibar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9566`

### WARNING-1387 · LAB_DUP_MATCH · SriLanka_SuperLeague | 2026-08-14 | Blue Eagles - Colombo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2646`

### WARNING-1388 · LAB_DUP_MATCH · SriLanka_SuperLeague | 2026-08-15 | Renown - Red Star
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3293`

### WARNING-1389 · LAB_DUP_MATCH · SriLanka_SuperLeague | 2026-08-16 | Ratnam - UP Country Lions
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '5', 'OK'), attuali=('1', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3859`

### WARNING-1390 · LAB_DUP_MATCH · SriLanka_SuperLeague | 2026-08-21 | Defenders FC - Ratnam
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4559`

### WARNING-1391 · LAB_DUP_MATCH · SriLanka_SuperLeague | 2026-09-01 | New Young's SC - Ratnam
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6453`

### WARNING-1392 · LAB_DUP_MATCH · SriLanka_SuperLeague | 2026-09-11 | Defenders FC - New Young's SC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8086`

### WARNING-1393 · LAB_DUP_MATCH · SriLanka_SuperLeague | 2026-09-15 | Blue Eagles - Sea Hawks
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9513`

### WARNING-1394 · LAB_DUP_MATCH · SriLanka_SuperLeague | 2026-09-14 | Ratnam - Blue Star
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9547`

### WARNING-1395 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-09 | Malmo FF - Degerfors
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2149`

### WARNING-1396 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-09 | Hammarby - Hacken
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2155`

### WARNING-1397 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-09 | Göteborg - Kalmar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2164`

### WARNING-1398 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-09 | Halmstad - GAIS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2172`

### WARNING-1399 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-14 | Elfsborg - Västerås SK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2586`

### WARNING-1400 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-15 | Mjallby - Sirius
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3233`

### WARNING-1401 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-16 | Djurgarden - AIK Stockholm
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3768`

### WARNING-1402 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-16 | Brommapojkarna - Orgryte
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3792`

### WARNING-1403 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-16 | Kalmar - Hammarby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3800`

### WARNING-1404 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-16 | Degerfors - Göteborg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3813`

### WARNING-1405 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-16 | GAIS - Malmo FF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3839`

### WARNING-1406 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-08-21 | Sirius - Hacken
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4447`

### WARNING-1407 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-09-11 | Hacken - Mjallby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8085`

### WARNING-1408 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-09-14 | Sirius - Degerfors
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9572`

### WARNING-1409 · LAB_DUP_MATCH · Sweden_Allsvenskan | 2026-09-14 | Djurgarden - GAIS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9584`

### WARNING-1410 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-09 | Arlanda - Pitea
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2162`

### WARNING-1411 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-14 | AFC Eskilstuna - Hammarby TFF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2555`

### WARNING-1412 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-15 | Karlbergs - Stocksund
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3167`

### WARNING-1413 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-15 | Gefle - Umeå
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3295`

### WARNING-1414 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-15 | Sollentuna - Jarfalla
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3303`

### WARNING-1415 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-15 | Karlstad - Assyriska FF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3310`

### WARNING-1416 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-16 | Pitea - Vasalund
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3759`

### WARNING-1417 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-16 | FBK Karlstad - Enkoping SK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3818`

### WARNING-1418 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-16 | Stockholm Internazionale - Arlanda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3849`

### WARNING-1419 · LAB_DUP_MATCH · Sweden_Division1_Norra | 2026-08-21 | Stockholm Internazionale - Jarfalla
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4413`

### WARNING-1420 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-09 | Jonkoping - Olympic
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2153`

### WARNING-1421 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-14 | Lunds - Hassleholms IF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2527`

### WARNING-1422 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-15 | Olympic - AFC Malmo
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3174`

### WARNING-1423 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-15 | Laholms - Jonkoping
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3282`

### WARNING-1424 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-15 | Angelholm - Trollhättan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3316`

### WARNING-1425 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-15 | Kristianstad - Tvaaker
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3339`

### WARNING-1426 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-16 | Rosengard - Utsikten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3719`

### WARNING-1427 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-16 | Trelleborg - Eskilsminne
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3729`

### WARNING-1428 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-08-16 | Atvidaberg - Skövde
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3746`

### WARNING-1429 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-09-11 | Lunds - Rosengard
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8082`

### WARNING-1430 · LAB_DUP_MATCH · Sweden_Division1_Sodra | 2026-09-11 | Trollhättan - Utsikten
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8115`

### WARNING-1431 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-07-31 | IFK Skovde - Ahlafors IF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1365`

### WARNING-1432 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-07-31 | Vanersborgs FK - Herrestads AIF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1376`

### WARNING-1433 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-07-31 | Karlstad 2 - Grebbestad
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1378`

### WARNING-1434 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-07-31 | Stenungsunds - Skara
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1388`

### WARNING-1435 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-07-31 | Tord - Kumla
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1394`

### WARNING-1436 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-09 | Motala - Husqvarna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2157`

### WARNING-1437 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-09 | Herrestads AIF - Tord
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2159`

### WARNING-1438 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-14 | Ahlafors IF - Grebbestad
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2535`

### WARNING-1439 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-14 | Husqvarna - Skara
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2548`

### WARNING-1440 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-15 | IFK Skovde - Herrestads AIF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3249`

### WARNING-1441 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-15 | Tord - Motala
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3335`

### WARNING-1442 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-15 | Stenungsunds - Kumla
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3340`

### WARNING-1443 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-16 | Karlstad 2 - Lidkoping
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3799`

### WARNING-1444 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-21 | Vanersborgs FK - IFK Skovde
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4425`

### WARNING-1445 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-21 | Herrestads AIF - Vanersborgs IF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4432`

### WARNING-1446 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-21 | Lidkoping - Ahlafors IF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4445`

### WARNING-1447 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-08-21 | Kumla - Husqvarna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '6', 'OK'), attuali=('2', '6', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4507`

### WARNING-1448 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-09-11 | Vanersborgs IF - Grebbestad
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8061`

### WARNING-1449 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-09-11 | Stenungsunds - Vanersborgs FK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8122`

### WARNING-1450 · LAB_DUP_MATCH · Sweden_Division2_NorraGotaland | 2026-09-11 | Kumla - Motala
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8153`

### WARNING-1451 · LAB_DUP_MATCH · Sweden_Division2_NorraSvealand | 2026-08-15 | Gute - Bollstanas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3256`

### WARNING-1452 · LAB_DUP_MATCH · Sweden_Division2_NorraSvealand | 2026-08-15 | Falu - IK Franke
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3274`

### WARNING-1453 · LAB_DUP_MATCH · Sweden_Division2_NorraSvealand | 2026-08-15 | Angby - Kungsangen
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3296`

### WARNING-1454 · LAB_DUP_MATCH · Sweden_Division2_NorraSvealand | 2026-08-15 | Lidingo IFK - Viggbyholms
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3359`

### WARNING-1455 · LAB_DUP_MATCH · Sweden_Division2_NorraSvealand | 2026-08-16 | Skiljebo - Helges
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3712`

### WARNING-1456 · LAB_DUP_MATCH · Sweden_Division2_NorraSvealand | 2026-08-16 | Sunnersta AIF - Taby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3771`

### WARNING-1457 · LAB_DUP_MATCH · Sweden_Division2_NorraSvealand | 2026-08-16 | Enskede - Korsnas
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3778`

### WARNING-1458 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-09 | IFK Umea - Fransta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2138`

### WARNING-1459 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-15 | Umea FF - Umea FC Akademi
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3111`

### WARNING-1460 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-15 | Kubikenborgs IF - Taftea IK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3147`

### WARNING-1461 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-15 | IFK Umea - Storfors
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3159`

### WARNING-1462 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-15 | Fransta - Friska Viljor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3170`

### WARNING-1463 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-15 | Skelleftea - IFK Lulea
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3230`

### WARNING-1464 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-15 | Boden - Gottne
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3231`

### WARNING-1465 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-16 | IFK Ostersund - Lucksta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3699`

### WARNING-1466 · LAB_DUP_MATCH · Sweden_Division2_Norrland | 2026-08-21 | Umea FF - IFK Umea
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4403`

### WARNING-1467 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-07-31 | IFK Karlshamn - Rappe GOIF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1395`

### WARNING-1468 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-09 | IFK Trelleborg - Vaxjo Norra
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2165`

### WARNING-1469 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-14 | Solvesborgs - Nosaby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2519`

### WARNING-1470 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-15 | Torns - IFK Berga
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '4', 'OK'), attuali=('3', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3114`

### WARNING-1471 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-15 | Lilla Torg - Karlskrona
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3237`

### WARNING-1472 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-15 | IFK Karlshamn - IFK Trelleborg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '5', 'OK'), attuali=('1', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3290`

### WARNING-1473 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-16 | Linero IF - Rappe GOIF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '1', 'OK'), attuali=('5', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3761`

### WARNING-1474 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-16 | Osterlen - Oskarshamn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3763`

### WARNING-1475 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-16 | Vaxjo Norra - Staffanstorp United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3796`

### WARNING-1476 · LAB_DUP_MATCH · Sweden_Division2_SodraGotaland | 2026-08-21 | Solvesborgs - IFK Karlshamn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4434`

### WARNING-1477 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-07-31 | Farsta - Ragsved
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1361`

### WARNING-1478 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-09 | Eker Orebro - Nacka FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2143`

### WARNING-1479 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-09 | Nykopings - Sleipner
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2147`

### WARNING-1480 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-09 | Lindo FF - Fittja
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2151`

### WARNING-1481 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-14 | Farsta - Nykopings
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2576`

### WARNING-1482 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-15 | Karlslund - Haninge
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3176`

### WARNING-1483 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-15 | Smedby - Eker Orebro
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3248`

### WARNING-1484 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-16 | Forward - Syrianska
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3710`

### WARNING-1485 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-16 | Fittja - Ragsved
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3718`

### WARNING-1486 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-08-16 | Nacka FC - Orebro Syr.
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3856`

### WARNING-1487 · LAB_DUP_MATCH · Sweden_Division2_SodraSvealand | 2026-09-14 | Haninge - Syrianska
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9535`

### WARNING-1488 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-07-31 | Lindome - Jonsereds
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1379`

### WARNING-1489 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-07-31 | Boljan - Frölunda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1382`

### WARNING-1490 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-07-31 | Kongahalla - Onsala
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1385`

### WARNING-1491 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-09 | Astrio - Torslanda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '6', 'OK'), attuali=('0', '6', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2158`

### WARNING-1492 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-09 | Jonsereds - Landvetter
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2167`

### WARNING-1493 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-14 | Hestrafors - Qviding
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2466`

### WARNING-1494 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-14 | Lindome - Astrio
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2518`

### WARNING-1495 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-14 | Kongahalla - Frölunda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2529`

### WARNING-1496 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-14 | Boljan - Astorps
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2540`

### WARNING-1497 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-14 | Landvetter - Galtabacks BK
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2561`

### WARNING-1498 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-15 | Jonsereds - Onsala
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3210`

### WARNING-1499 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-08-15 | Torslanda - Dalstorps IF
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3227`

### WARNING-1500 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-09-11 | Boljan - Hestrafors
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8025`

### WARNING-1501 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-09-11 | Dalstorps IF - Frölunda
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8027`

### WARNING-1502 · LAB_DUP_MATCH · Sweden_Division2_VastraGotaland | 2026-09-11 | Lindome - Landvetter
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8123`

### WARNING-1503 · LAB_DUP_MATCH · Sweden_Superettan | 2026-07-31 | Oddevold - Norrby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:1392`

### WARNING-1504 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-09 | Varberg - Sandviken
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2140`

### WARNING-1505 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-14 | Brage - Örebro
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '3', 'OK'), attuali=('3', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2547`

### WARNING-1506 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-14 | Landskrona - Oddevold
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2588`

### WARNING-1507 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-15 | Sundsvall - Helsingborg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3228`

### WARNING-1508 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-15 | Falkenberg - Norrby
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3263`

### WARNING-1509 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-15 | Nordic United - Varberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3269`

### WARNING-1510 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-15 | Ljungskile - Öster
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3284`

### WARNING-1511 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-15 | Sandviken - Norrkoping
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '4', 'OK'), attuali=('1', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3338`

### WARNING-1512 · LAB_DUP_MATCH · Sweden_Superettan | 2026-08-16 | Värnamo - Östersund
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3838`

### WARNING-1513 · LAB_DUP_MATCH · Sweden_Superettan | 2026-09-01 | Helsingborg - Örebro
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6452`

### WARNING-1514 · LAB_DUP_MATCH · Sweden_Superettan | 2026-09-15 | Brage - Sandviken
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9447`

### WARNING-1515 · LAB_DUP_MATCH · Sweden_Superettan | 2026-09-15 | Värnamo - Öster
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9478`

### WARNING-1516 · LAB_DUP_MATCH · Sweden_Superettan | 2026-09-15 | Landskrona - Sundsvall
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9492`

### WARNING-1517 · LAB_DUP_MATCH · Sweden_Superettan | 2026-09-14 | Norrby - Varberg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9560`

### WARNING-1518 · LAB_DUP_MATCH · Sweden_Superettan | 2026-09-14 | Örebro - Nordic United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9577`

### WARNING-1519 · LAB_DUP_MATCH · Sweden_Superettan | 2026-09-14 | Östersund - Helsingborg
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9579`

### WARNING-1520 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-08-21 | Rapperswil-Jona - Winterthur
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4430`

### WARNING-1521 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-08-21 | Nyonnais - Etoile-Carouge
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4539`

### WARNING-1522 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-08-21 | Xamax - Lausanne Ouchy
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4544`

### WARNING-1523 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-09-01 | Rapperswil-Jona - Kriens
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6436`

### WARNING-1524 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-09-01 | Xamax - Yverdon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6442`

### WARNING-1525 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-09-01 | Nyonnais - Winterthur
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6456`

### WARNING-1526 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-09-01 | Lausanne Ouchy - Etoile-Carouge
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6474`

### WARNING-1527 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-09-11 | Nyonnais - Xamax
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8065`

### WARNING-1528 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-09-11 | Rapperswil-Jona - Yverdon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8066`

### WARNING-1529 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-09-11 | Lausanne Ouchy - Wil
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8131`

### WARNING-1530 · LAB_DUP_MATCH · Switzerland_ChallengeLeague | 2026-09-11 | Etoile-Carouge - Winterthur
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8161`

### WARNING-1531 · LAB_DUP_MATCH · Switzerland_PromotionLeague | 2026-08-15 | Paradiso - Breitenrain
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3121`

### WARNING-1532 · LAB_DUP_MATCH · Switzerland_PromotionLeague | 2026-08-15 | Lugano 2 - Luzerna 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '3', 'OK'), attuali=('4', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3156`

### WARNING-1533 · LAB_DUP_MATCH · Switzerland_SuperLeague | 2026-09-01 | Zurigo - Young Boys
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '4', 'OK'), attuali=('2', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6422`

### WARNING-1534 · LAB_DUP_MATCH · Switzerland_SuperLeague | 2026-09-15 | Grasshoppers - Sion
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '5', 'OK'), attuali=('2', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9420`

### WARNING-1535 · LAB_DUP_MATCH · Turkey_1Lig | 2026-08-21 | Karagumruk - Bursaspor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4566`

### WARNING-1536 · LAB_DUP_MATCH · Turkey_1Lig | 2026-09-01 | Sariyer - Pendikspor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6434`

### WARNING-1537 · LAB_DUP_MATCH · Turkey_1Lig | 2026-09-01 | Boluspor - Keciorengucu
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6438`

### WARNING-1538 · LAB_DUP_MATCH · Turkey_1Lig | 2026-09-01 | Bandirmaspor - Antalyaspor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6459`

### WARNING-1539 · LAB_DUP_MATCH · Turkey_1Lig | 2026-09-01 | Umraniyespor - Muglaspor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6473`

### WARNING-1540 · LAB_DUP_MATCH · Turkey_1Lig | 2026-09-11 | Sariyer - Bandirmaspor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8183`

### WARNING-1541 · LAB_DUP_MATCH · Turkey_1Lig | 2026-09-15 | Kayserispor - Istanbulspor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9456`

### WARNING-1542 · LAB_DUP_MATCH · Turkey_1Lig | 2026-09-14 | Kayserispor - Istanbulspor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9554`

### WARNING-1543 · LAB_DUP_MATCH · Turkey_SuperLig | 2026-09-11 | Besiktas - Erzurumspor
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8158`

### WARNING-1544 · LAB_DUP_MATCH · Turkey_SuperLig | 2026-09-15 | Gaziantep - Fenerbahce
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9467`

### WARNING-1545 · LAB_DUP_MATCH · Turkey_SuperLig | 2026-09-14 | Gaziantep - Fenerbahce
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9589`

### WARNING-1546 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Orlando City - Cincinnati
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3691`

### WARNING-1547 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Atlanta Utd - New York Red Bulls
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3732`

### WARNING-1548 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Nashville SC - Inter Miami
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3744`

### WARNING-1549 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Charlotte - Columbus Crew
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3753`

### WARNING-1550 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Colorado Rapids - Sporting Kansas City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3779`

### WARNING-1551 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Toronto FC - New England Revolution
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3787`

### WARNING-1552 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Real Salt Lake - Minnesota
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3789`

### WARNING-1553 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Los Angeles FC - San Diego FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3798`

### WARNING-1554 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | San Jose Earthquakes - St. Louis City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3817`

### WARNING-1555 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | CF Montreal - DC United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3832`

### WARNING-1556 · LAB_DUP_MATCH · USA_MLS | 2026-08-16 | Houston Dynamo - Los Angeles Galaxy
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3842`

### WARNING-1557 · LAB_DUP_MATCH · USA_MLS | 2026-09-15 | San Diego FC - Philadelphia Union
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9442`

### WARNING-1558 · LAB_DUP_MATCH · USA_MLS | 2026-09-14 | Vancouver Whitecaps - Austin FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9548`

### WARNING-1559 · LAB_DUP_MATCH · USA_MLS | 2026-09-14 | San Diego FC - Philadelphia Union
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9552`

### WARNING-1560 · LAB_DUP_MATCH · USA_MLSNextPro_EasternConference_NortheastDivision | 2026-08-15 | Toronto FC 2 - Chattanooga
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3131`

### WARNING-1561 · LAB_DUP_MATCH · USA_MLSNextPro_EasternConference_NortheastDivision | 2026-08-16 | Columbus Crew 2 - New York City 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '2', 'OK'), attuali=('4', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3769`

### WARNING-1562 · LAB_DUP_MATCH · USA_MLSNextPro_EasternConference_SoutheastDivision | 2026-08-14 | Atlanta United 2 - New York Red Bulls 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2536`

### WARNING-1563 · LAB_DUP_MATCH · USA_MLSNextPro_EasternConference_SoutheastDivision | 2026-08-15 | Chicago Fire 2 - Orlando City B
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3070`

### WARNING-1564 · LAB_DUP_MATCH · USA_MLSNextPro_WesternConference_CentralDivision | 2026-08-15 | Houston Dynamo 2 - Ventura County
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3153`

### WARNING-1565 · LAB_DUP_MATCH · USA_MLSNextPro_WesternConference_CentralDivision | 2026-08-16 | Sporting Kansas City 2 - Colorado Rapids 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3820`

### WARNING-1566 · LAB_DUP_MATCH · USA_MLSNextPro_WesternConference_PacificDivision | 2026-08-14 | Real Monarchs - Minnesota 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2553`

### WARNING-1567 · LAB_DUP_MATCH · USA_MLSNextPro_WesternConference_PacificDivision | 2026-08-16 | Austin FC 2 - Vancouver 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3851`

### WARNING-1568 · LAB_DUP_MATCH · USA_MLSNextPro_WesternConference_PacificDivision | 2026-08-16 | North Texas - Portland Timbers 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3873`

### WARNING-1569 · LAB_DUP_MATCH · USA_MLSNextPro_WesternConference_PacificDivision | 2026-08-21 | Los Angeles FC 2 - Sporting Kansas City 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4419`

### WARNING-1570 · LAB_DUP_MATCH · USA_MLSNextPro_WesternConference_PacificDivision | 2026-08-30 | Real Monarchs - Tacoma Defiance
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6249`

### WARNING-1571 · LAB_DUP_MATCH · USA_MLSNextPro_WesternConference_PacificDivision | 2026-08-30 | Portland Timbers 2 - Austin FC 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:6260`

### WARNING-1572 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Sporting Jax - Indy Eleven
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3804`

### WARNING-1573 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Orange County SC - Louisville City
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3805`

### WARNING-1574 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Tampa Bay - Rhode Island
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3807`

### WARNING-1575 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Las Vegas Lights - Brooklyn
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3823`

### WARNING-1576 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Colorado Springs - Birmingham Legion
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3850`

### WARNING-1577 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | San Antonio - El Paso
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3858`

### WARNING-1578 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Oakland Roots - Monterey Bay
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3862`

### WARNING-1579 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Sacramento Republic - Lexington
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3863`

### WARNING-1580 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Detroit - Loudoun
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3864`

### WARNING-1581 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Pittsburgh - Charleston
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3874`

### WARNING-1582 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | New Mexico - FC Tulsa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3886`

### WARNING-1583 · LAB_DUP_MATCH · USA_USLChampionship | 2026-08-16 | Hartford Athletic - Miami FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3897`

### WARNING-1584 · LAB_DUP_MATCH · USA_USLLeagueOne | 2026-08-16 | Greenville - One Knoxville
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3767`

### WARNING-1585 · LAB_DUP_MATCH · USA_USLLeagueOne | 2026-08-16 | Charlotte Independ. - Sarasota Paradise
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3775`

### WARNING-1586 · LAB_DUP_MATCH · USA_USLLeagueOne | 2026-08-16 | New York Cosmos - AV Alta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3777`

### WARNING-1587 · LAB_DUP_MATCH · USA_USLLeagueOne | 2026-08-16 | Fort Wayne - Chattanooga Red Wolves
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3814`

### WARNING-1588 · LAB_DUP_MATCH · USA_USLLeagueOne | 2026-08-16 | Spokane Velocity - Corpus Christi FC
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3846`

### WARNING-1589 · LAB_DUP_MATCH · USA_USLLeagueOne | 2026-08-16 | Westchester SC - FC Naples
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3847`

### WARNING-1590 · LAB_DUP_MATCH · USA_USLLeagueOne | 2026-09-15 | Portland Hearts of Pine - AV Alta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9446`

### WARNING-1591 · LAB_DUP_MATCH · USA_USLLeagueOne | 2026-09-14 | Portland Hearts of Pine - AV Alta
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9564`

### WARNING-1592 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-08-14 | Prykarpattya - Probiy Horodenka
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2515`

### WARNING-1593 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-08-14 | Ahrobiznes Volochysk - Lokomotyv Kyiv
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2575`

### WARNING-1594 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-08-15 | Metalist Kharkiv - Oleksandriya
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3128`

### WARNING-1595 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-08-15 | SC Poltava - UCSA
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3229`

### WARNING-1596 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-08-15 | FC Chernihiv - Zhytomyr 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3364`

### WARNING-1597 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-08-15 | Viktoria - Kulikiv
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3410`

### WARNING-1598 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-08-16 | Inhulets - Nyva Ternopil
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '2', 'OK'), attuali=('1', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3865`

### WARNING-1599 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-08-16 | Fenix Mariupol - Kolos Kovalivka 2
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3903`

### WARNING-1600 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-09-11 | UCSA - FC Chernihiv
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8171`

### WARNING-1601 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-09-15 | Zhytomyr 2 - Ahrobiznes Volochysk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9435`

### WARNING-1602 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-09-15 | Oleksandriya - Viktoria
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9502`

### WARNING-1603 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-09-14 | Zhytomyr 2 - Ahrobiznes Volochysk
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9540`

### WARNING-1604 · LAB_DUP_MATCH · Ukraine_PershaLiga | 2026-09-14 | Oleksandriya - Viktoria
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9599`

### WARNING-1605 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-08-14 | Epitsentr - Veres-Rivne
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2621`

### WARNING-1606 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-08-15 | Karpaty Lviv - Bukovyna
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3398`

### WARNING-1607 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-08-15 | Kudrivka - Obolon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '0', 'KO'), attuali=('0', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3407`

### WARNING-1608 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-08-16 | FC Kharkiv - Shakhtar
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3882`

### WARNING-1609 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-09-11 | Kolos Kovalivka - Karpaty Lviv
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8142`

### WARNING-1610 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-09-15 | Dyn. Kyiv - Epitsentr
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9486`

### WARNING-1611 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-09-15 | Shakhtar - Ch. Odesa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9505`

### WARNING-1612 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-09-14 | Dyn. Kyiv - Epitsentr
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9578`

### WARNING-1613 · LAB_DUP_MATCH · Ukraine_PremierLeague | 2026-09-14 | Shakhtar - Ch. Odesa
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9594`

### WARNING-1614 · LAB_DUP_MATCH · Wales_CymruNorth | 2026-08-21 | Holyhead - Bangor 1876
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4429`

### WARNING-1615 · LAB_DUP_MATCH · Wales_CymruNorth | 2026-08-21 | Mold Alexandra - Buckley
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4499`

### WARNING-1616 · LAB_DUP_MATCH · Wales_CymruNorth | 2026-08-21 | Denbigh - Porthmadog
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '3', 'OK'), attuali=('2', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4512`

### WARNING-1617 · LAB_DUP_MATCH · Wales_CymruNorth | 2026-09-11 | Denbigh - Bala Town
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '2', 'OK'), attuali=('5', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7990`

### WARNING-1618 · LAB_DUP_MATCH · Wales_CymruNorth | 2026-09-15 | Penrhyncoch - Bala Town
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9416`

### WARNING-1619 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-14 | Llandudno - Holywell
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2465`

### WARNING-1620 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-14 | Cambrian United - Flint
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2522`

### WARNING-1621 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-14 | Connah's Q. - Trefelin
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('6', '0', 'OK'), attuali=('6', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2560`

### WARNING-1622 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-14 | Airbus - Ammanford
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '0', 'KO'), attuali=('2', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2601`

### WARNING-1623 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-14 | Haverfordwest - Penybont
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2640`

### WARNING-1624 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-14 | TNS - Briton Ferry
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:2645`

### WARNING-1625 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-15 | Caernarfon - Colwyn Bay
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3119`

### WARNING-1626 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-15 | Barry - Cardiff Metropolitan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:3306`

### WARNING-1627 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-21 | Holywell - Barry
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '3', 'OK'), attuali=('1', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4379`

### WARNING-1628 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-21 | Trefelin - Caernarfon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4435`

### WARNING-1629 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-21 | Penybont - Llandudno
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4477`

### WARNING-1630 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-21 | Flint - Briton Ferry
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4514`

### WARNING-1631 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-21 | Haverfordwest - Cambrian United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '3', 'OK'), attuali=('0', '3', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4557`

### WARNING-1632 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-21 | Cardiff Metropolitan - TNS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4574`

### WARNING-1633 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-08-21 | Colwyn Bay - Airbus
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4577`

### WARNING-1634 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-11 | Cambrian United - Holywell
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8022`

### WARNING-1635 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-11 | Ammanford - Caernarfon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8055`

### WARNING-1636 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-11 | Barry - Llandudno
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '1', 'OK'), attuali=('4', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8057`

### WARNING-1637 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-11 | Flint - Cardiff Metropolitan
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8103`

### WARNING-1638 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-11 | Trefelin - Penybont
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8117`

### WARNING-1639 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-11 | Airbus - TNS
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '2', 'KO'), attuali=('0', '2', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8157`

### WARNING-1640 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-11 | Haverfordwest - Briton Ferry
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '1', 'OK'), attuali=('3', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8177`

### WARNING-1641 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-15 | Holywell - Colwyn Bay
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '5', 'OK'), attuali=('0', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9437`

### WARNING-1642 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-15 | Llandudno - Caernarfon
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '1', 'KO'), attuali=('1', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9439`

### WARNING-1643 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-15 | Barry - Ammanford
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '2', 'OK'), attuali=('2', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9441`

### WARNING-1644 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-15 | Trefelin - Cambrian United
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '4', 'OK'), attuali=('0', '4', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9466`

### WARNING-1645 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-15 | Connah's Q. - Airbus
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9475`

### WARNING-1646 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-15 | TNS - Flint
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('5', '0', 'OK'), attuali=('5', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9482`

### WARNING-1647 · LAB_DUP_MATCH · Wales_CymruPremier | 2026-09-15 | Penybont - Briton Ferry
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '2', 'OK'), attuali=('3', '2', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:9487`

### WARNING-1648 · LAB_DUP_MATCH · Wales_CymruSouth | 2026-08-21 | Afan Lido - Pontardawe
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '0', 'KO'), attuali=('1', '0', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4374`

### WARNING-1649 · LAB_DUP_MATCH · Wales_CymruSouth | 2026-08-21 | Pontypridd - Trethomas Bluebirds
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('2', '1', 'OK'), attuali=('2', '1', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4388`

### WARNING-1650 · LAB_DUP_MATCH · Wales_CymruSouth | 2026-08-21 | Caerau Ely - Pure Swansea
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('1', '5', 'OK'), attuali=('1', '5', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4462`

### WARNING-1651 · LAB_DUP_MATCH · Wales_CymruSouth | 2026-08-21 | Newport City - Baglan Dragons
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:4506`

### WARNING-1652 · LAB_DUP_MATCH · Wales_CymruSouth | 2026-09-11 | Pontypridd - Afan Lido
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('0', '1', 'KO'), attuali=('0', '1', 'KO').
- Sorgente: `analysis\laboratory\data\01_matches.csv:7985`

### WARNING-1653 · LAB_DUP_MATCH · Wales_CymruSouth | 2026-09-11 | Caerau Ely - Llanelli
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('3', '0', 'OK'), attuali=('3', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8000`

### WARNING-1654 · LAB_DUP_MATCH · Wales_CymruSouth | 2026-09-11 | Newport City - Trethomas Bluebirds
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('', '', ''), attuali=('', '', '').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8048`

### WARNING-1655 · LAB_DUP_MATCH · Wales_CymruSouth | 2026-09-11 | Pure Swansea - Pontardawe
- Area: `laboratory`
- Dettaglio: Duplicato per engine 2.5.0; valori precedenti=('4', '0', 'OK'), attuali=('4', '0', 'OK').
- Sorgente: `analysis\laboratory\data\01_matches.csv:8050`

### WARNING-1656 · ST_PLAYED_SPREAD · FaroeIslands_1Deild
- Area: `standings`
- Dettaglio: Played min=18, max=23, delta=5; min: Fuglafjordur, Streymur 2; max: Vikingur 2, TB Tvoroyri.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\FaroeIslands_1Deild.csv`

### WARNING-1657 · ST_POSITIONS · Islanda_Division_2_2026
- Area: `standings`
- Dettaglio: Posizioni non consecutive/univoche: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].
- Sorgente: `data\storico\classifiche_calcolate\Islanda_Division_2_2026.csv`

### WARNING-1658 · ST_PLAYED_SPREAD · Peru_Liga2_GroupA
- Area: `standings`
- Dettaglio: Played min=5, max=10, delta=5; min: San Marcos; max: Union Comercio, Llacuabamba, AD Cantolao.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2_GroupA.csv`

### WARNING-1659 · ST_PLAYED_SPREAD · Portugal_Liga3_SerieA
- Area: `standings`
- Dettaglio: Played min=1, max=5, delta=4; min: Caldas; max: Paredes, AD Marco 09, Varzim, Fafe, SC Vianense, Leca, Guimaraes B, Trofense, S. Joao Ver, Ferreira.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Portugal_Liga3_SerieA.csv`

### WARNING-1660 · ST_PLAYED_SPREAD · Spain_LaLiga
- Area: `standings`
- Dettaglio: Played min=1, max=6, delta=5; min: Rayo Vallecano; max: Alaves, Elche.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Spain_LaLiga.csv`

### WARNING-1661 · ST_PLAYED_SPREAD · Wales_CymruSouth
- Area: `standings`
- Dettaglio: Played min=3, max=7, delta=4; min: Llantwit Major; max: Baglan Dragons, Afan Lido, Llanelli.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Wales_CymruSouth.csv`

## INFO (50)

### INFO-001 · LAB_UNMATCHED
- Area: `laboratory`
- Dettaglio: 06_unmatched_matches.csv contiene 2270 righe da esaminare.
- Verifica suggerita: Analizzare soprattutto LeagueId/team ricorrenti: possono indicare alias o ranking non agganciati.
- Sorgente: `analysis\laboratory\data\06_unmatched_matches.csv`

### INFO-002 · ST_ODD_TEAMS · Austria_Regionalliga_North
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Regionalliga_North.csv`

### INFO-003 · ST_ODD_TEAMS · Austria_Steiermark
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Steiermark.csv`

### INFO-004 · ST_PLAYED_SPREAD · Austria_Steiermark
- Area: `standings`
- Dettaglio: Played min=1, max=4, delta=3; min: SV Schermann Rorhrbach; max: Grossklein, Lebring.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Steiermark.csv`

### INFO-005 · ST_PLAYED_SPREAD · Austria_Wien
- Area: `standings`
- Dettaglio: Played min=1, max=4, delta=3; min: Stammersdorf; max: Floridsdorfer AC (Am), Kagran.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Wien.csv`

### INFO-006 · ST_ODD_TEAMS · Azerbaijan_FirstLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Azerbaijan_FirstLeague.csv`

### INFO-007 · ST_ODD_TEAMS · Belarus_VysshayaLiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 21.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Belarus_VysshayaLiga.csv`

### INFO-008 · ST_ODD_TEAMS · Belgium_ChallengerProLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Belgium_ChallengerProLeague.csv`

### INFO-009 · ST_ODD_TEAMS · Bulgaria_ParvaLiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ParvaLiga.csv`

### INFO-010 · ST_ODD_TEAMS · CzechRepublic_4Liga_GroupA
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\CzechRepublic_4Liga_GroupA.csv`

### INFO-011 · ST_PLAYED_SPREAD · Estonia_EsiliigaB
- Area: `standings`
- Dettaglio: Played min=26, max=29, delta=3; min: Legion; max: Tartu Kalev.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_EsiliigaB.csv`

### INFO-012 · ST_ODD_TEAMS · Estonia_Meistriliiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_Meistriliiga.csv`

### INFO-013 · ST_PLAYED_SPREAD · Finland_Kakkonen_GroupC
- Area: `standings`
- Dettaglio: Played min=18, max=21, delta=3; min: TP-47, Vaajakoski, Hercules, SJK Akatemia 2; max: Huima / Urho, VPS 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kakkonen_GroupC.csv`

### INFO-014 · ST_PLAYED_SPREAD · Finland_Kolmonen_Eastern_Group1
- Area: `standings`
- Dettaglio: Played min=17, max=20, delta=3; min: KeuPa, JJK/2, Savon Pallo, Komeetat; max: SAPA.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Eastern_Group1.csv`

### INFO-015 · ST_ODD_TEAMS · Finland_Kolmonen_Eastern_Group2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Eastern_Group2.csv`

### INFO-016 · ST_ODD_TEAMS · Finland_Kolmonen_Southern_Group2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Southern_Group2.csv`

### INFO-017 · ST_ODD_TEAMS · Finland_Kolmonen_Southern_Group3
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Southern_Group3.csv`

### INFO-018 · ST_PLAYED_SPREAD · Finland_Kolmonen_Western_Group1
- Area: `standings`
- Dettaglio: Played min=18, max=21, delta=3; min: VG-62; max: SalPa 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Western_Group1.csv`

### INFO-019 · ST_ODD_TEAMS · Finland_Kolmonen_Western_Group3
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Western_Group3.csv`

### INFO-020 · ST_ODD_TEAMS · Germany_3Liga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 21.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_3Liga.csv`

### INFO-021 · ST_ODD_TEAMS · Germany_Oberliga_BadenWurttemberg
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_BadenWurttemberg.csv`

### INFO-022 · ST_ODD_TEAMS · Germany_Oberliga_Bremen
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_Bremen.csv`

### INFO-023 · ST_ODD_TEAMS · Germany_Regionalliga_Bayern
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Regionalliga_Bayern.csv`

### INFO-024 · ST_ODD_TEAMS · Iceland_1DeildWomen
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_1DeildWomen.csv`

### INFO-025 · ST_ODD_TEAMS · Iceland_Division_1
- Area: `standings`
- Dettaglio: Numero squadre dispari: 27.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_Division_1.csv`

### INFO-026 · ST_ODD_TEAMS · Iceland_Division_2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_Division_2.csv`

### INFO-027 · ST_ODD_TEAMS · Moldova_Liga1_GroupB
- Area: `standings`
- Dettaglio: Numero squadre dispari: 5.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Moldova_Liga1_GroupB.csv`

### INFO-028 · ST_ODD_TEAMS · Norway_2ndDivision_Group1
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_2ndDivision_Group1.csv`

### INFO-029 · ST_ODD_TEAMS · Norway_2ndDivision_Group2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_2ndDivision_Group2.csv`

### INFO-030 · ST_ODD_TEAMS · Norway_3rdDivision_Group1
- Area: `standings`
- Dettaglio: Numero squadre dispari: 25.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group1.csv`

### INFO-031 · ST_ODD_TEAMS · Norway_3rdDivision_Group3
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group3.csv`

### INFO-032 · ST_ODD_TEAMS · Norway_3rdDivision_Group5
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group5.csv`

### INFO-033 · ST_ODD_TEAMS · Peru_Liga2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2.csv`

### INFO-034 · ST_PLAYED_SPREAD · Peru_Liga2
- Area: `standings`
- Dettaglio: Played min=3, max=6, delta=3; min: Binacional; max: Sport Huancayo 2, Tacna Heroica, Cesar Vallejo, Santos, Comerciantes, Llacuabamba, Estudiantil CNI.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2.csv`

### INFO-035 · ST_ODD_TEAMS · Peru_Liga2_GroupA
- Area: `standings`
- Dettaglio: Numero squadre dispari: 9.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2_GroupA.csv`

### INFO-036 · ST_ODD_TEAMS · Peru_Liga2_GroupB
- Area: `standings`
- Dettaglio: Numero squadre dispari: 9.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2_GroupB.csv`

### INFO-037 · ST_PLAYED_SPREAD · Peru_Liga2_GroupB
- Area: `standings`
- Dettaglio: Played min=8, max=11, delta=3; min: Estudiantil CNI; max: Minas, Sport Huancayo 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2_GroupB.csv`

### INFO-038 · ST_PLAYED_SPREAD · Portugal_Liga3_SerieB
- Area: `standings`
- Dettaglio: Played min=1, max=4, delta=3; min: Lusitano GC; max: Caldas.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Portugal_Liga3_SerieB.csv`

### INFO-039 · ST_PLAYED_SPREAD · Slovenia_PrvaLiga
- Area: `standings`
- Dettaglio: Played min=8, max=11, delta=3; min: Radomlje; max: Aluminij.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Slovenia_PrvaLiga.csv`

### INFO-040 · ST_PLAYED_SPREAD · Somalia_NationalLeague
- Area: `standings`
- Dettaglio: Played min=19, max=22, delta=3; min: Gantaalaha Afgooye; max: Heegan, Dekedaha, Horseed, Elman, Jeenyo, Jubba.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Somalia_NationalLeague.csv`

### INFO-041 · ST_ODD_TEAMS · SouthKorea_KLeague2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\SouthKorea_KLeague2.csv`

### INFO-042 · ST_ODD_TEAMS · Spain_LaLiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 21.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Spain_LaLiga.csv`

### INFO-043 · ST_ODD_TEAMS · Sweden_Division1_Sodra
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division1_Sodra.csv`

### INFO-044 · ST_ODD_TEAMS · Sweden_Division2_Norrland
- Area: `standings`
- Dettaglio: Numero squadre dispari: 23.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_Norrland.csv`

### INFO-045 · ST_ODD_TEAMS · Sweden_Division2_SodraGotaland
- Area: `standings`
- Dettaglio: Numero squadre dispari: 31.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_SodraGotaland.csv`

### INFO-046 · ST_ODD_TEAMS · Sweden_Division2_VastraGotaland
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_VastraGotaland.csv`

### INFO-047 · ST_ODD_TEAMS · Switzerland_PromotionLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Switzerland_PromotionLeague.csv`

### INFO-048 · ST_ODD_TEAMS · USA_MLS
- Area: `standings`
- Dettaglio: Numero squadre dispari: 35.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLS.csv`

### INFO-049 · ST_ODD_TEAMS · USA_USLChampionship
- Area: `standings`
- Dettaglio: Numero squadre dispari: 25.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLChampionship.csv`

### INFO-050 · ST_PLAYED_SPREAD · USA_USLChampionship
- Area: `standings`
- Dettaglio: Played min=22, max=25, delta=3; min: New Mexico, Rhode Island, Indy Eleven, Birmingham Legion, Brooklyn; max: Pittsburgh.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLChampionship.csv`
