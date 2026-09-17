# GioOver2.5 - Data Quality Report

Report diagnostico READ-ONLY. Le anomalie euristiche non implicano automaticamente dati errati.

## Riepilogo

- Modalità: **quick**
- Classifiche analizzate: **211** (3542 squadre/righe)
- Risultati storici: non analizzati in quick mode
- Laboratory: non analizzato in quick mode
- CRITICAL: **53**
- WARNING: **7**
- INFO: **47**

## Priorità per analisi IA

Analizzare prima i CRITICAL. Prima di bonificare verificare sempre il formato reale della competizione e lo storico sorgente. WARNING/INFO possono essere legittimi (rinvii, campionati dispari, formati speciali).

## CRITICAL (53)

### CRITICAL-001 · ST_PLAYED_SPREAD · Austria_Regionalliga_West
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: Marchfeld, Wiener Viktoria, Traiskirchen, Wienerberger, Mattersburg SV 2020, SV Donau; max: Hohenems, Dornbirn, SC Imst, Schwaz, Kitzbuhel, SK St. Johann, Tirol (Am), Fugen, Reichenau, Rothis, Kufstein, Lochau, Altach U21, Wolfurt, Lauterach, FC Lustenau.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Regionalliga_West.csv`

### CRITICAL-002 · ST_PLAYED_SPREAD · Belarus_PershayaLiga
- Area: `standings`
- Dettaglio: Played min=1, max=24, delta=23; min: Arsenal Dzerzhinsk, FC Baranovichi, Gomel, Slavia Mozyr; max: Niva Dolbizno, Slutsk, Lida, SKA-1938, Molodechno, FC Slonim, BumProm Gomel, Volna Pinsk, Soligorsk, Ostrovets, Din. Minsk 2, Minsk 2, Smorgon, Orsha, Uni X Labs, Gomel 2, BATE 2, Osipovichi.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Belarus_PershayaLiga.csv`

### CRITICAL-003 · ST_PLAYED_SPREAD · Belarus_VysshayaLiga
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Torpedo Zhodino, BATE Borisov, Neman Grodno, FC Baranovichi, Belshina Bobruisk; max: Gomel, FC Minsk, Arsenal Dzerzhinsk.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Belarus_VysshayaLiga.csv`

### CRITICAL-004 · ST_PLAYED_SPREAD · Bulgaria_ParvaLiga
- Area: `standings`
- Dettaglio: Played min=1, max=10, delta=9; min: Levski Sofia, Arda Kardzhali, PFC Lokomotiv Sofia 1929, Ludogorets Razgrad, Lokomotiv Plovdiv; max: CSKA 1948 Sofia, Botev Plovdiv, Spartak Varna, Botev Vratsa, Dunav Ruse.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ParvaLiga.csv`

### CRITICAL-005 · ST_PLAYED_SPREAD · Estonia_Esiliiga
- Area: `standings`
- Dettaglio: Played min=1, max=29, delta=28; min: Flora Tallinn U21, Nomme United U21; max: Tartu Welco, Flora U21, FC Tallinn.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_Esiliiga.csv`

### CRITICAL-006 · ST_PLAYED_SPREAD · Estonia_Meistriliiga
- Area: `standings`
- Dettaglio: Played min=2, max=29, delta=27; min: FC Kuressaare; max: Parnu JK Vaprus.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_Meistriliiga.csv`

### CRITICAL-007 · ST_PLAYED_SPREAD · Finland_Kolmonen_Eastern_Group2
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: SC Zulimanit; max: Kings, Jippo-J/Punamusta, Ylämyllyn Yllätys, KuPS/Akatemia 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Eastern_Group2.csv`

### CRITICAL-008 · ST_PLAYED_SPREAD · Finland_Kolmonen_Eastern_Group3
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Mikkelin Pallo-Kissat, Kotajärven Pallo; max: LAUTP.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Eastern_Group3.csv`

### CRITICAL-009 · ST_PLAYED_SPREAD · Finland_Kolmonen_Southern_Group1
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Malmin Palloseura, Lohjan Pallo; max: PPJ/Ruoholahti, EPS Reservi, HooGee.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Southern_Group1.csv`

### CRITICAL-010 · ST_PLAYED_SPREAD · Finland_Kolmonen_Southern_Group2
- Area: `standings`
- Dettaglio: Played min=1, max=19, delta=18; min: MPS/Atletico Malmi; max: TiPS, PPJ/Lauttasaari, Valtti, Töölön Taisto, HPS/2, Kontu, PPS.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Southern_Group2.csv`

### CRITICAL-011 · ST_DUP_TEAM · Finland_Ykkosliiga
- Area: `standings`
- Dettaglio: Squadre duplicate: jippo
- Verifica suggerita: Verificare alias/normalizzazione nomi squadra.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Ykkosliiga.csv`

### CRITICAL-012 · ST_PLAYED_SPREAD · Finland_Ykkosliiga
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: JIPPO, PK-35 Helsinki, Mikkelin Palloilijat, EIF; max: KTP, Jippo, Ekenas, Klubi 04, KaPa.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Ykkosliiga.csv`

### CRITICAL-013 · ST_PLAYED_SPREAD · Germany_3Liga
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: Viktoria Colonia; max: Meppen.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Germany_3Liga.csv`

### CRITICAL-014 · ST_PLAYED_SPREAD · Germany_Oberliga_BadenWurttemberg
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: 1\. FC Muhlhausen; max: Oberachern, Reutlingen, Backnang, Villingen, FC Holzhausen, Bahlinger, Ravensburg, Neckarsulm, Balingen, Singen, Karlsruher 2, Teningen, Essingen, Nottingen, Normannia Gmund.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_BadenWurttemberg.csv`

### CRITICAL-015 · ST_PLAYED_SPREAD · Germany_Oberliga_Bremen
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: Bremen I2; max: Schwachhausen.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_Bremen.csv`

### CRITICAL-016 · ST_PLAYED_SPREAD · Hungary_NBI
- Area: `standings`
- Dettaglio: Played min=1, max=8, delta=7; min: Budapest Honved, Vasas Budapest; max: Ujpest, Zalaegerszeg.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Hungary_NBI.csv`

### CRITICAL-017 · ST_PLAYED_SPREAD · Iceland_1DeildWomen
- Area: `standings`
- Dettaglio: Played min=3, max=19, delta=16; min: Keflavik Women; max: Haukar, HK Kopavogur, ÍA Akranes.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_1DeildWomen.csv`

### CRITICAL-018 · ST_PLAYED_SPREAD · Iceland_BestaDeildKvenna
- Area: `standings`
- Dettaglio: Played min=1, max=18, delta=17; min: Vikingur Reykjavik, FH Hafnarfjörður Women, Þór/KA Akureyri, Breidablik, Grindavik/Njarovik, Throttur, Valur Reykjavík, Stjarnan; max: Breidablik D, Hafnarfjordur D, IBV Vestmannaeyjar D, Stjarnan D, Throttur D, Grindavik/Njardvik D, Fram D, Valur D, Vikingur Reykjavik D, Thor/KA D.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_BestaDeildKvenna.csv`

### CRITICAL-019 · ST_PLAYED_SPREAD · Iceland_Division_1
- Area: `standings`
- Dettaglio: Played min=1, max=26, delta=25; min: HK Kopavogur, Hviti, Haukar; max: Fylkir.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_Division_1.csv`

### CRITICAL-020 · ST_PLAYED_SPREAD · Iceland_Division_2
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Fjoelnir; max: Haukar, Selfoss, Fjolnir.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_Division_2.csv`

### CRITICAL-021 · ST_DUP_TEAM · Islanda_Division_2_2026
- Area: `standings`
- Dettaglio: Squadre duplicate: kari, fjolnir, kfa, throttur vogar, dalvik/reynir, hviti, olafsvik, haukar, kormakur/hvot, selfoss
- Verifica suggerita: Verificare alias/normalizzazione nomi squadra.
- Sorgente: `data\storico\classifiche_calcolate\Islanda_Division_2_2026.csv`

### CRITICAL-022 · ST_PLAYED_SPREAD · Islanda_Division_2_2026
- Area: `standings`
- Dettaglio: Played min=1, max=9, delta=8; min: Kari, Fjolnir, KFA, Throttur Vogar, Dalvik/Reynir, Hviti, Olafsvik, Haukar, Kormakur/Hvot, Selfoss, Magni, KFG Gardabaer; max: Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Kormakur/Hvot, KFG Gardabaer, Olafsvik, KFA, Throttur Vogar, Magni, Haukar, Kari, Dalvik/Reynir, Selfoss, Fjolnir, Kormakur/Hvot, KFG Gardabaer, Hviti, Olafsvik, KFA, Throttur Vogar, Magni.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Islanda_Division_2_2026.csv`

### CRITICAL-023 · ST_PLAYED_SPREAD · Kazakhstan_PremierLeague
- Area: `standings`
- Dettaglio: Played min=1, max=26, delta=25; min: Altai Semey, Zhetysu Taldykorgan; max: Zhenis, Ulytau.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Kazakhstan_PremierLeague.csv`

### CRITICAL-024 · ST_PLAYED_SPREAD · Latvia_Virsliga
- Area: `standings`
- Dettaglio: Played min=1, max=28, delta=27; min: SK Super Nova, Liepaja; max: Riga FC, FK Liepaja, Jelgava.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Latvia_Virsliga.csv`

### CRITICAL-025 · ST_PLAYED_SPREAD · Lebanon_PremierLeague
- Area: `standings`
- Dettaglio: Played min=11, max=23, delta=12; min: Bourj FC; max: Al Riyadi Abbasiyah, Tadamon, Racing.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Lebanon_PremierLeague.csv`

### CRITICAL-026 · ST_PLAYED_SPREAD · Lithuania_Toplyga
- Area: `standings`
- Dettaglio: Played min=17, max=29, delta=12; min: Riteriai; max: Transinvest, FK Panevezys.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Lithuania_Toplyga.csv`

### CRITICAL-027 · ST_PLAYED_SPREAD · Moldova_Liga1_GroupA
- Area: `standings`
- Dettaglio: Played min=1, max=7, delta=6; min: Victoria, Falesti; max: Vulturii Cutezatori, Iskra Ribnita, FCM Ungheni, Univer Comrat, Zimbru 2, Sparta Selemet.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Moldova_Liga1_GroupA.csv`

### CRITICAL-028 · ST_PLAYED_SPREAD · Norway_2ndDivision_Group1
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Pors Football; max: Jerv, Bjarg, Mjoendalen.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_2ndDivision_Group1.csv`

### CRITICAL-029 · ST_PLAYED_SPREAD · Norway_2ndDivision_Group2
- Area: `standings`
- Dettaglio: Played min=2, max=20, delta=18; min: Eidsvold TF; max: Kjelsaas, Tromsdalen, Skeid, Trygg/Lade.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_2ndDivision_Group2.csv`

### CRITICAL-030 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group1
- Area: `standings`
- Dettaglio: Played min=1, max=21, delta=20; min: Brattvag, Arendal, , Mjondalen, Halden, IF Ready Football, Lokomotiv Oslo FK, Eik-Tonsberg, Lysekloster, Vidar, Notodden; max: Vaalerenga IF 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group1.csv`

### CRITICAL-031 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group2
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Eidsvold, Lørenskog; max: Strindheim, Melhus.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group2.csv`

### CRITICAL-032 · ST_DUP_TEAM · Norway_3rdDivision_Group3
- Area: `standings`
- Dettaglio: Squadre duplicate: os
- Verifica suggerita: Verificare alias/normalizzazione nomi squadra.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group3.csv`

### CRITICAL-033 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group3
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Askøy, Foerde, Os, Vard Haugesund, FK Fyllingsdalen; max: Austevoll, Stord, Gneist.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group3.csv`

### CRITICAL-034 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group4
- Area: `standings`
- Dettaglio: Played min=1, max=19, delta=18; min: Flekkeroey, Aakra; max: Madla IL, Vindbjart, Mandalskameratene, Varhaug, Flekkeroy, Viking 2, Brodd, Stabaek 2, Vag, Staal Jorpeland, Odd 2, Haugesund 2, Hinna, Akra.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group4.csv`

### CRITICAL-035 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group5
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Skjervoey; max: Harstad, Floeya.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group5.csv`

### CRITICAL-036 · ST_PLAYED_SPREAD · Norway_3rdDivision_Group6
- Area: `standings`
- Dettaglio: Played min=1, max=20, delta=19; min: Rælingen, Lillehammer FK; max: Elverum, Oppsal.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group6.csv`

### CRITICAL-037 · ST_PLAYED_SPREAD · Sweden_Division1_Norra
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Vasalunds, Sollentuna FK; max: AFC Eskilstuna, Assyriska FF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division1_Norra.csv`

### CRITICAL-038 · ST_PLAYED_SPREAD · Sweden_Division1_Sodra
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Haessleholms IF, Kristianstad FC, Trelleborgs FF; max: Hassleholms IF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division1_Sodra.csv`

### CRITICAL-039 · ST_PLAYED_SPREAD · Sweden_Division2_NorraGotaland
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Skara FC, Lidkoepings FK, Vaenersborgs IF, IFK Skoevde FK, IFK Kumla; max: IFK Skovde, Ahlafors IF, Herrestads AIF, Lidkoping, Vanersborgs IF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_NorraGotaland.csv`

### CRITICAL-040 · ST_PLAYED_SPREAD · Sweden_Division2_NorraSvealand
- Area: `standings`
- Dettaglio: Played min=1, max=24, delta=23; min: Kungsaengens IF, Kungsangens IF, Helges IF; max: Sunnersta AIF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_NorraSvealand.csv`

### CRITICAL-041 · ST_PLAYED_SPREAD · Sweden_Division2_Norrland
- Area: `standings`
- Dettaglio: Played min=1, max=21, delta=20; min: Team TG FF, Viggbyholms, Falu, Bollstanas, Angby, Kungsangen, Gute, IK Franke, Lidingo IFK; max: Skelleftea, IFK Lulea, IFK Ostersund, Boden, Gottne, Lucksta.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_Norrland.csv`

### CRITICAL-042 · ST_PLAYED_SPREAD · Sweden_Division2_SodraGotaland
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Stenungsunds, Karlslund, Dalstorps IF, Jonsereds, Smedby, Herrestads AIF, IFK Skovde, Motala, Tord, Onsala, Torslanda, Eker Orebro, Nosaby IF, Vaexjoe Norra IF, Vaxjo Norra IF, Haninge, Kumla; max: IFK Berga.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_SodraGotaland.csv`

### CRITICAL-043 · ST_PLAYED_SPREAD · Sweden_Division2_SodraSvealand
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Nykoepings BIS, FC Nacka Iliria; max: Nykopings, Nacka FC.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_SodraSvealand.csv`

### CRITICAL-044 · ST_PLAYED_SPREAD · Sweden_Division2_VastraGotaland
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Landvetter IS, Lindome GIF, Galtabaecks BK, IF Boelan; max: Dalstorps IF.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_VastraGotaland.csv`

### CRITICAL-045 · ST_PLAYED_SPREAD · Sweden_Superettan
- Area: `standings`
- Dettaglio: Played min=1, max=24, delta=23; min: Falkenbergs FF, Orgryte, Hacken, IK Brage; max: Norrkoping, Falkenberg, Östersund, Varberg, Landskrona, Oddevold, Nordic United, Sandviken, Ljungskile, Värnamo, Örebro, Norrby, Brage, Sundsvall.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Superettan.csv`

### CRITICAL-046 · ST_PLAYED_SPREAD · Switzerland_PromotionLeague
- Area: `standings`
- Dettaglio: Played min=1, max=8, delta=7; min: FC Kreuzlingen; max: Breitenrain.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Switzerland_PromotionLeague.csv`

### CRITICAL-047 · ST_PLAYED_SPREAD · Switzerland_SuperLeague
- Area: `standings`
- Dettaglio: Played min=1, max=8, delta=7; min: FC Haka j., Fish United; max: Sion, Young Boys, Basilea, Zurigo, Luzern, Grasshoppers, Vaduz, Lausanne.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Switzerland_SuperLeague.csv`

### CRITICAL-048 · ST_PLAYED_SPREAD · USA_MLS
- Area: `standings`
- Dettaglio: Played min=1, max=26, delta=25; min: Inter Miami CF, Seattle Sounders FC, New York City FC, Atlanta United, CF Montréal; max: Charlotte, Toronto FC.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLS.csv`

### CRITICAL-049 · ST_PLAYED_SPREAD · USA_MLSNextPro_EasternConference_NortheastDivision
- Area: `standings`
- Dettaglio: Played min=1, max=23, delta=22; min: Portland Timbers 2, Vancouver 2; max: New England Revolution 2, Philadelphia 2, Cincinnati 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_EasternConference_NortheastDivision.csv`

### CRITICAL-050 · ST_PLAYED_SPREAD · USA_MLSNextPro_EasternConference_SoutheastDivision
- Area: `standings`
- Dettaglio: Played min=3, max=24, delta=21; min: Connecticut FC, New York City 2, Toronto FC 2, Philadelphia 2, Cincinnati 2, New England Revolution 2, Columbus Crew 2; max: Crown Legacy.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_EasternConference_SoutheastDivision.csv`

### CRITICAL-051 · ST_PLAYED_SPREAD · USA_MLSNextPro_WesternConference_CentralDivision
- Area: `standings`
- Dettaglio: Played min=1, max=22, delta=21; min: Chicago Fire 2, Inter Miami 2; max: St. Louis City 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_WesternConference_CentralDivision.csv`

### CRITICAL-052 · ST_PLAYED_SPREAD · USA_MLSNextPro_WesternConference_PacificDivision
- Area: `standings`
- Dettaglio: Played min=4, max=23, delta=19; min: St. Louis City 2, Minnesota 2; max: Los Angeles FC 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_WesternConference_PacificDivision.csv`

### CRITICAL-053 · ST_PLAYED_SPREAD · USA_USLLeagueOne
- Area: `standings`
- Dettaglio: Played min=1, max=27, delta=26; min: Fort Wayne FC, Forward Madison FC, Chattanooga Red Wolves SC; max: AV Alta, Portland Hearts of Pine.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLLeagueOne.csv`

## WARNING (7)

### WARNING-001 · ST_PLAYED_SPREAD · FaroeIslands_1Deild
- Area: `standings`
- Dettaglio: Played min=18, max=23, delta=5; min: Fuglafjordur, Streymur 2; max: Vikingur 2, TB Tvoroyri.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\FaroeIslands_1Deild.csv`

### WARNING-002 · ST_POSITIONS · Islanda_Division_2_2026
- Area: `standings`
- Dettaglio: Posizioni non consecutive/univoche: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].
- Sorgente: `data\storico\classifiche_calcolate\Islanda_Division_2_2026.csv`

### WARNING-003 · ST_PLAYED_SPREAD · Peru_Liga2_GroupA
- Area: `standings`
- Dettaglio: Played min=5, max=10, delta=5; min: San Marcos; max: Union Comercio, Llacuabamba, AD Cantolao.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2_GroupA.csv`

### WARNING-004 · ST_PLAYED_SPREAD · Portugal_Liga3_SerieA
- Area: `standings`
- Dettaglio: Played min=1, max=5, delta=4; min: Caldas; max: Paredes, AD Marco 09, Varzim, Fafe, SC Vianense, Leca, Guimaraes B, Trofense, S. Joao Ver, Ferreira.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Portugal_Liga3_SerieA.csv`

### WARNING-005 · ST_PLAYED_SPREAD · Somalia_NationalLeague
- Area: `standings`
- Dettaglio: Played min=19, max=23, delta=4; min: Gantaalaha Afgooye; max: Dekedaha.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Somalia_NationalLeague.csv`

### WARNING-006 · ST_PLAYED_SPREAD · Spain_LaLiga
- Area: `standings`
- Dettaglio: Played min=1, max=6, delta=5; min: Rayo Vallecano; max: Alaves, Elche.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Spain_LaLiga.csv`

### WARNING-007 · ST_PLAYED_SPREAD · Wales_CymruSouth
- Area: `standings`
- Dettaglio: Played min=3, max=7, delta=4; min: Llantwit Major; max: Baglan Dragons, Afan Lido, Llanelli.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Wales_CymruSouth.csv`

## INFO (47)

### INFO-001 · ST_ODD_TEAMS · Austria_Regionalliga_North
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Regionalliga_North.csv`

### INFO-002 · ST_ODD_TEAMS · Austria_Steiermark
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Steiermark.csv`

### INFO-003 · ST_PLAYED_SPREAD · Austria_Steiermark
- Area: `standings`
- Dettaglio: Played min=1, max=4, delta=3; min: SV Schermann Rorhrbach; max: Grossklein, Lebring.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Steiermark.csv`

### INFO-004 · ST_PLAYED_SPREAD · Austria_Wien
- Area: `standings`
- Dettaglio: Played min=1, max=4, delta=3; min: Stammersdorf; max: Floridsdorfer AC (Am), Kagran.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Wien.csv`

### INFO-005 · ST_ODD_TEAMS · Azerbaijan_FirstLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Azerbaijan_FirstLeague.csv`

### INFO-006 · ST_ODD_TEAMS · Belarus_VysshayaLiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 21.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Belarus_VysshayaLiga.csv`

### INFO-007 · ST_ODD_TEAMS · Belgium_ChallengerProLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Belgium_ChallengerProLeague.csv`

### INFO-008 · ST_ODD_TEAMS · Bulgaria_ParvaLiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ParvaLiga.csv`

### INFO-009 · ST_ODD_TEAMS · CzechRepublic_4Liga_GroupA
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\CzechRepublic_4Liga_GroupA.csv`

### INFO-010 · ST_PLAYED_SPREAD · Estonia_EsiliigaB
- Area: `standings`
- Dettaglio: Played min=26, max=29, delta=3; min: Legion; max: Tartu Kalev.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_EsiliigaB.csv`

### INFO-011 · ST_ODD_TEAMS · Estonia_Meistriliiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_Meistriliiga.csv`

### INFO-012 · ST_PLAYED_SPREAD · Finland_Kakkonen_GroupC
- Area: `standings`
- Dettaglio: Played min=18, max=21, delta=3; min: TP-47, Vaajakoski, Hercules, SJK Akatemia 2; max: Huima / Urho, VPS 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kakkonen_GroupC.csv`

### INFO-013 · ST_PLAYED_SPREAD · Finland_Kolmonen_Eastern_Group1
- Area: `standings`
- Dettaglio: Played min=17, max=20, delta=3; min: KeuPa, JJK/2, Savon Pallo, Komeetat; max: SAPA.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Eastern_Group1.csv`

### INFO-014 · ST_ODD_TEAMS · Finland_Kolmonen_Eastern_Group2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Eastern_Group2.csv`

### INFO-015 · ST_ODD_TEAMS · Finland_Kolmonen_Southern_Group2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Southern_Group2.csv`

### INFO-016 · ST_ODD_TEAMS · Finland_Kolmonen_Southern_Group3
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Southern_Group3.csv`

### INFO-017 · ST_PLAYED_SPREAD · Finland_Kolmonen_Western_Group1
- Area: `standings`
- Dettaglio: Played min=18, max=21, delta=3; min: VG-62; max: SalPa 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Western_Group1.csv`

### INFO-018 · ST_ODD_TEAMS · Finland_Kolmonen_Western_Group3
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Kolmonen_Western_Group3.csv`

### INFO-019 · ST_ODD_TEAMS · Germany_3Liga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 21.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_3Liga.csv`

### INFO-020 · ST_ODD_TEAMS · Germany_Oberliga_BadenWurttemberg
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_BadenWurttemberg.csv`

### INFO-021 · ST_ODD_TEAMS · Germany_Oberliga_Bremen
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_Bremen.csv`

### INFO-022 · ST_ODD_TEAMS · Germany_Regionalliga_Bayern
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Regionalliga_Bayern.csv`

### INFO-023 · ST_ODD_TEAMS · Iceland_1DeildWomen
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_1DeildWomen.csv`

### INFO-024 · ST_ODD_TEAMS · Iceland_Division_1
- Area: `standings`
- Dettaglio: Numero squadre dispari: 27.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_Division_1.csv`

### INFO-025 · ST_ODD_TEAMS · Latvia_Virsliga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Latvia_Virsliga.csv`

### INFO-026 · ST_ODD_TEAMS · Moldova_Liga1_GroupB
- Area: `standings`
- Dettaglio: Numero squadre dispari: 5.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Moldova_Liga1_GroupB.csv`

### INFO-027 · ST_ODD_TEAMS · Norway_2ndDivision_Group1
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_2ndDivision_Group1.csv`

### INFO-028 · ST_ODD_TEAMS · Norway_2ndDivision_Group2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_2ndDivision_Group2.csv`

### INFO-029 · ST_ODD_TEAMS · Norway_3rdDivision_Group1
- Area: `standings`
- Dettaglio: Numero squadre dispari: 25.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group1.csv`

### INFO-030 · ST_ODD_TEAMS · Norway_3rdDivision_Group3
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group3.csv`

### INFO-031 · ST_ODD_TEAMS · Norway_3rdDivision_Group5
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Norway_3rdDivision_Group5.csv`

### INFO-032 · ST_ODD_TEAMS · Peru_Liga2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2.csv`

### INFO-033 · ST_PLAYED_SPREAD · Peru_Liga2
- Area: `standings`
- Dettaglio: Played min=3, max=6, delta=3; min: Binacional; max: Sport Huancayo 2, Tacna Heroica, Cesar Vallejo, Santos, Comerciantes, Llacuabamba, Estudiantil CNI.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2.csv`

### INFO-034 · ST_ODD_TEAMS · Peru_Liga2_GroupA
- Area: `standings`
- Dettaglio: Numero squadre dispari: 9.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2_GroupA.csv`

### INFO-035 · ST_ODD_TEAMS · Peru_Liga2_GroupB
- Area: `standings`
- Dettaglio: Numero squadre dispari: 9.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2_GroupB.csv`

### INFO-036 · ST_PLAYED_SPREAD · Peru_Liga2_GroupB
- Area: `standings`
- Dettaglio: Played min=8, max=11, delta=3; min: Estudiantil CNI; max: Minas, Sport Huancayo 2.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Peru_Liga2_GroupB.csv`

### INFO-037 · ST_PLAYED_SPREAD · Portugal_Liga3_SerieB
- Area: `standings`
- Dettaglio: Played min=1, max=4, delta=3; min: Lusitano GC; max: Caldas.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Portugal_Liga3_SerieB.csv`

### INFO-038 · ST_PLAYED_SPREAD · Slovenia_PrvaLiga
- Area: `standings`
- Dettaglio: Played min=8, max=11, delta=3; min: Radomlje; max: Aluminij.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\Slovenia_PrvaLiga.csv`

### INFO-039 · ST_ODD_TEAMS · SouthKorea_KLeague2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\SouthKorea_KLeague2.csv`

### INFO-040 · ST_ODD_TEAMS · Spain_LaLiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 21.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Spain_LaLiga.csv`

### INFO-041 · ST_ODD_TEAMS · Sweden_Division2_Norrland
- Area: `standings`
- Dettaglio: Numero squadre dispari: 23.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_Norrland.csv`

### INFO-042 · ST_ODD_TEAMS · Sweden_Division2_SodraGotaland
- Area: `standings`
- Dettaglio: Numero squadre dispari: 31.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_SodraGotaland.csv`

### INFO-043 · ST_ODD_TEAMS · Sweden_Division2_VastraGotaland
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_VastraGotaland.csv`

### INFO-044 · ST_ODD_TEAMS · Switzerland_PromotionLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Switzerland_PromotionLeague.csv`

### INFO-045 · ST_ODD_TEAMS · USA_MLS
- Area: `standings`
- Dettaglio: Numero squadre dispari: 35.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLS.csv`

### INFO-046 · ST_ODD_TEAMS · USA_USLChampionship
- Area: `standings`
- Dettaglio: Numero squadre dispari: 25.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLChampionship.csv`

### INFO-047 · ST_PLAYED_SPREAD · USA_USLChampionship
- Area: `standings`
- Dettaglio: Played min=22, max=25, delta=3; min: New Mexico, Rhode Island, Indy Eleven, Birmingham Legion, Brooklyn; max: Pittsburgh.
- Verifica suggerita: Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLChampionship.csv`
