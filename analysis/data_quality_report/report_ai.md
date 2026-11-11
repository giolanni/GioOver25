# GioOver2.5 - Data Quality Report

Report diagnostico READ-ONLY. Le anomalie euristiche non implicano automaticamente dati errati.

## Riepilogo

- Modalità: **full**
- Classifiche analizzate: **326** (4967 squadre/righe)
- File risultati analizzati: **372** (36847 partite)
- Righe Laboratory analizzate: **21055**
- CRITICAL: **0**
- WARNING: **18**
- INFO: **48**

## Priorità per analisi IA

Analizzare prima i CRITICAL. Prima di bonificare verificare sempre il formato reale della competizione e lo storico sorgente. WARNING/INFO possono essere legittimi (rinvii, campionati dispari, formati speciali).

## CRITICAL (0)

Nessuna anomalia.

## WARNING (18)

### WARNING-001 · ST_PLAYED_SPREAD · Austria_Salzburg
- Area: `standings`
- Dettaglio: Played min=11, max=16, delta=5; min: Seekirchen U21; max: Strasswalchen, Thalgau.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Salzburg.csv`

### WARNING-002 · ST_PLAYED_SPREAD · Bulgaria_ThirdLeagueNorthWest
- Area: `standings`
- Dettaglio: Played min=4, max=11, delta=7; min: Juventus Malchika; max: Yantra Polski Trambesh, Partizan Cerven Brjag, Pavlikeni.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ThirdLeagueNorthWest.csv`

### WARNING-003 · ST_PLAYED_SPREAD · CongoDr_Ligue1
- Area: `standings`
- Dettaglio: Played min=1, max=5, delta=4; min: Mazembe; max: Celeste.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\CongoDr_Ligue1.csv`

### WARNING-004 · ST_PLAYED_SPREAD · England_IsthmianLeaguePremierDivision
- Area: `standings`
- Dettaglio: Played min=11, max=18, delta=7; min: Cray Wanderers; max: Maldon & Tiptree.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\England_IsthmianLeaguePremierDivision.csv`

### WARNING-005 · ST_PLAYED_SPREAD · England_ProfessionalDevelopmentLeague
- Area: `standings`
- Dettaglio: Played min=6, max=10, delta=4; min: Huddersfield U21, Millwall U21; max: QPR U21.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\England_ProfessionalDevelopmentLeague.csv`

### WARNING-006 · ST_PLAYED_SPREAD · England_SouthernLeaguePremierCentral
- Area: `standings`
- Dettaglio: Played min=14, max=18, delta=4; min: Worcester; max: Real Bedford, Bury Town, Rushall.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\England_SouthernLeaguePremierCentral.csv`

### WARNING-007 · ST_PLAYED_SPREAD · England_SouthernLeaguePremierSouth
- Area: `standings`
- Dettaglio: Played min=13, max=17, delta=4; min: Wimborne; max: Chichester, Evesham, Bracknell.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\England_SouthernLeaguePremierSouth.csv`

### WARNING-008 · ST_PLAYED_SPREAD · Estonia_Esiliiga
- Area: `standings`
- Dettaglio: Played min=28, max=35, delta=7; min: Maardu; max: Tartu Welco, Viimsi JK, FC Tallinn.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Estonia_Esiliiga.csv`

### WARNING-009 · ST_PLAYED_SPREAD · Filippine_PFL
- Area: `standings`
- Dettaglio: Played min=4, max=8, delta=4; min: Cebu FC; max: Maharlika, Tuloy.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Filippine_PFL.csv`

### WARNING-010 · ST_PLAYED_SPREAD · Finland_Veikkausliiga
- Area: `standings`
- Dettaglio: Played min=2, max=29, delta=27; min: PK-35; max: Inter Turku, HJK, KuPS, Oulu, Gnistan, VPS.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Veikkausliiga.csv`

### WARNING-011 · ST_PLAYED_SPREAD · Israele_LigaAlefNorth
- Area: `standings`
- Dettaglio: Played min=4, max=10, delta=6; min: Tzeirey Um El Fahem; max: Ironi Nesher, MS Tira, Hapoel Karmiel, Nahariya, Maccabi Neve Shaanan Eldad, M. Kiryat Ata-Bialik, Maccabi Nujeidat Ahmad, Hapoel Ihud Bnei Jatt, Hapoel Bnei Musmus, Hapoel Tirat Karmel, Araba.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Israele_LigaAlefNorth.csv`

### WARNING-012 · ST_PLAYED_SPREAD · Libano_PremierLeague
- Area: `standings`
- Dettaglio: Played min=1, max=6, delta=5; min: Al Ghazieh; max: Jwayya, Tadamon, Al Ahed, Tripoli, Al Hikma, Al Akhaa Al Ahli.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Libano_PremierLeague.csv`

### WARNING-013 · ST_PLAYED_SPREAD · Norway_OBOSLigaen
- Area: `standings`
- Dettaglio: Played min=1, max=30, delta=29; min: Bjarg, Kjelsås; max: Strömsgodset, Haugesund, Kongsvinger, Stabaek, Odd, Bryne, Ranheim, Egersund, Strømmen, Hodd, Lyn, Sandnes, Moss, Sogndal, Åsane, Raufoss.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Norway_OBOSLigaen.csv`

### WARNING-014 · ST_PLAYED_SPREAD · Ruanda_PremierLeague
- Area: `standings`
- Dettaglio: Played min=3, max=8, delta=5; min: APR; max: Marines, Gorilla, Sunrise, Amagaju, Etoile de L'Est, Police, Gasogi United.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Ruanda_PremierLeague.csv`

### WARNING-015 · ST_PLAYED_SPREAD · SaudiArabia_Division2
- Area: `standings`
- Dettaglio: Played min=2, max=6, delta=4; min: Hottain; max: Al Sharq, Al Sahel, Wej SC, Al Arabi, Al Entesar, Al Taraji, Al Qwarah, Al Najoom, Al Jubail, Afief, Al Qous, Jubbah.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\SaudiArabia_Division2.csv`

### WARNING-016 · ST_PLAYED_SPREAD · Sweden_Division2_SodraGotaland
- Area: `standings`
- Dettaglio: Played min=2, max=28, delta=26; min: Croatia Malmo; max: Torns.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_SodraGotaland.csv`

### WARNING-017 · ST_PLAYED_SPREAD · Uganda_PremierLeague
- Area: `standings`
- Dettaglio: Played min=6, max=10, delta=4; min: Kitara; max: NEC FC, Villa, Entebbe UPPC, Police, Blacks Power, Express, Lugazi, Kataka.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Uganda_PremierLeague.csv`

### WARNING-018 · ST_PLAYED_SPREAD · Venezuela_LigaFUTVE2
- Area: `standings`
- Dettaglio: Played min=12, max=16, delta=4; min: Mineros, Dynamo Puerto, Avila, Frontera, Maritimo; max: Barquisimeto.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Venezuela_LigaFUTVE2.csv`

## INFO (48)

### INFO-001 · LAB_UNMATCHED
- Area: `laboratory`
- Dettaglio: 06_unmatched_matches.csv contiene 2865 righe da esaminare.
- Verifica suggerita: Analizzare soprattutto LeagueId/team ricorrenti: possono indicare alias o ranking non agganciati.
- Sorgente: `analysis\laboratory\data\06_unmatched_matches.csv`

### INFO-002 · ST_ODD_TEAMS · Austria_Regionalliga_North
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Austria_Regionalliga_North.csv`

### INFO-003 · ST_ODD_TEAMS · Belgium_ChallengerProLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Belgium_ChallengerProLeague.csv`

### INFO-004 · ST_ODD_TEAMS · Bulgaria_ThirdLeagueNorthEast
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ThirdLeagueNorthEast.csv`

### INFO-005 · ST_PLAYED_SPREAD · Bulgaria_ThirdLeagueNorthEast
- Area: `standings`
- Dettaglio: Played min=10, max=13, delta=3; min: Aksakovo; max: Ludogorets III, Volov Shumen, Chernolomets.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ThirdLeagueNorthEast.csv`

### INFO-006 · ST_ODD_TEAMS · Bulgaria_ThirdLeagueNorthWest
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ThirdLeagueNorthWest.csv`

### INFO-007 · ST_PLAYED_SPREAD · Bulgaria_ThirdLeagueSouthWest
- Area: `standings`
- Dettaglio: Played min=12, max=15, delta=3; min: Septemvri Sofia 2; max: Minyor Pernik, Balkan Botevgrad, Slivnishki Geroy, Slavia Sofia 2, Belasitsa, Chavdar Etropole, Razlog.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Bulgaria_ThirdLeagueSouthWest.csv`

### INFO-008 · ST_PLAYED_SPREAD · Burundi_PrimusLeague
- Area: `standings`
- Dettaglio: Played min=9, max=12, delta=3; min: Rukinzo, Le Messager Ngozi, Inter Star; max: Royal Vision, Muzinga, Musongati, Bumamuru, Kayanza, Young Star.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Burundi_PrimusLeague.csv`

### INFO-009 · ST_ODD_TEAMS · Cambogia_CPL
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Cambogia_CPL.csv`

### INFO-010 · ST_PLAYED_SPREAD · Canada_CanadianPremierLeague
- Area: `standings`
- Dettaglio: Played min=25, max=28, delta=3; min: Vancouver FC, HFX Wanderers, Pacific FC; max: Supra du Quebec.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Canada_CanadianPremierLeague.csv`

### INFO-011 · ST_ODD_TEAMS · CzechRepublic_4Liga_GroupA
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\CzechRepublic_4Liga_GroupA.csv`

### INFO-012 · ST_ODD_TEAMS · EmiratiArabi_Division1
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\EmiratiArabi_Division1.csv`

### INFO-013 · ST_PLAYED_SPREAD · England_NPLPremierDivision
- Area: `standings`
- Dettaglio: Played min=16, max=19, delta=3; min: Guiseley, Bury, FC United; max: Emley, Bamber Bridge.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\England_NPLPremierDivision.csv`

### INFO-014 · ST_ODD_TEAMS · England_ProfessionalDevelopmentLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\England_ProfessionalDevelopmentLeague.csv`

### INFO-015 · ST_PLAYED_SPREAD · Etiopia_PremierLeague
- Area: `standings`
- Dettaglio: Played min=2, max=5, delta=3; min: Sidama Bunna, Welwalo Adigrat; max: Negele Arsi Ketema, Mechal, Welayta Dicha, Ethiopia Nigd Bank, Halaba Ketema, Ethio Electric, St. George, Adama City, Sheger Ketema, Ethiopia Bunna.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Etiopia_PremierLeague.csv`

### INFO-016 · ST_ODD_TEAMS · Finland_Veikkausliiga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Finland_Veikkausliiga.csv`

### INFO-017 · ST_PLAYED_SPREAD · Germany_Oberliga_Hessen
- Area: `standings`
- Dettaglio: Played min=14, max=17, delta=3; min: Darmstadt U21; max: Stadtallendorf, Unter-Flockenbach, Hadamar, Friedberg, Fernwald, Pohlheim, Alzenau, CSC 03 Kassel, Hunfelder, RW Walldorf, Baunatal, Hummetroth, Kassel 2, Giessen.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Oberliga_Hessen.csv`

### INFO-018 · ST_ODD_TEAMS · Germany_Regionalliga_Bayern
- Area: `standings`
- Dettaglio: Numero squadre dispari: 19.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Germany_Regionalliga_Bayern.csv`

### INFO-019 · ST_ODD_TEAMS · Gibilterra_NationalLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Gibilterra_NationalLeague.csv`

### INFO-020 · ST_ODD_TEAMS · HongKong_PremierLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\HongKong_PremierLeague.csv`

### INFO-021 · ST_PLAYED_SPREAD · HongKong_PremierLeague
- Area: `standings`
- Dettaglio: Played min=6, max=9, delta=3; min: Kitchee, Southern District, Hong Kong FC; max: Hong Kong Rangers.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\HongKong_PremierLeague.csv`

### INFO-022 · ST_ODD_TEAMS · Hungary_NBIIISouthwest
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Hungary_NBIIISouthwest.csv`

### INFO-023 · ST_PLAYED_SPREAD · Iceland_BestaDeildKvenna
- Area: `standings`
- Dettaglio: Played min=20, max=23, delta=3; min: Fram D, Thor/KA D, Vikingur Reykjavik D, Valur D; max: Breidablik D, Hafnarfjordur D, IBV Vestmannaeyjar D, Throttur D, Grindavik/Njardvik D, Stjarnan D.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Iceland_BestaDeildKvenna.csv`

### INFO-024 · ST_ODD_TEAMS · India_ISL
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\India_ISL.csv`

### INFO-025 · ST_ODD_TEAMS · Kuwait_Division1
- Area: `standings`
- Dettaglio: Numero squadre dispari: 7.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Kuwait_Division1.csv`

### INFO-026 · ST_ODD_TEAMS · Laos_LaoLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Laos_LaoLeague.csv`

### INFO-027 · ST_ODD_TEAMS · Libano_PremierLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Libano_PremierLeague.csv`

### INFO-028 · ST_ODD_TEAMS · Lithuania_Toplyga
- Area: `standings`
- Dettaglio: Numero squadre dispari: 9.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Lithuania_Toplyga.csv`

### INFO-029 · ST_PLAYED_SPREAD · Mexico_LigaExpansionMX_Apertura
- Area: `standings`
- Dettaglio: Played min=14, max=17, delta=3; min: Cruz Azul Hidalgo; max: Atletico La Paz, Leones Negros, Atl. Morelia, Piratas, Cancun, Alacranes, Venados.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Mexico_LigaExpansionMX_Apertura.csv`

### INFO-030 · ST_ODD_TEAMS · Moldova_Liga1_GroupB
- Area: `standings`
- Dettaglio: Numero squadre dispari: 5.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Moldova_Liga1_GroupB.csv`

### INFO-031 · ST_ODD_TEAMS · Mongolia_PremierLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 9.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Mongolia_PremierLeague.csv`

### INFO-032 · ST_PLAYED_SPREAD · Mozambico_Mocambola
- Area: `standings`
- Dettaglio: Played min=15, max=18, delta=3; min: Black Bulls, Costa do Sol, Ferroviario Maputo, Chingale de Tete; max: Ferroviario Nacala.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Mozambico_Mocambola.csv`

### INFO-033 · ST_PLAYED_SPREAD · SierraLeone_PremierLeague
- Area: `standings`
- Dettaglio: Played min=2, max=5, delta=3; min: Star Sport Academy; max: Wilberforce Strikers, Waterloo, Kamboi Eagles, Old Edwardians, Bhantal, Bo Rangers, Bai Bureh Warriors, Ports Authority, Western, Wusum Stars, Mighty Blackpool, Bullom Stars.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\SierraLeone_PremierLeague.csv`

### INFO-034 · ST_ODD_TEAMS · SouthKorea_KLeague2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\SouthKorea_KLeague2.csv`

### INFO-035 · ST_ODD_TEAMS · Suriname_SML
- Area: `standings`
- Dettaglio: Numero squadre dispari: 11.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Suriname_SML.csv`

### INFO-036 · ST_PLAYED_SPREAD · Suriname_SML
- Area: `standings`
- Dettaglio: Played min=4, max=7, delta=3; min: Inter Moengotapoe, SV Transvaal, Inter Wanica; max: Leo Victor.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Suriname_SML.csv`

### INFO-037 · ST_ODD_TEAMS · Sweden_Division2_SodraGotaland
- Area: `standings`
- Dettaglio: Numero squadre dispari: 15.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Sweden_Division2_SodraGotaland.csv`

### INFO-038 · ST_ODD_TEAMS · Turkey_2LigRedGroup
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Turkey_2LigRedGroup.csv`

### INFO-039 · ST_ODD_TEAMS · USA_MLSNextPro_WesternConference_PacificDivision
- Area: `standings`
- Dettaglio: Numero squadre dispari: 3.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\USA_MLSNextPro_WesternConference_PacificDivision.csv`

### INFO-040 · ST_ODD_TEAMS · USA_USLChampionship
- Area: `standings`
- Dettaglio: Numero squadre dispari: 25.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLChampionship.csv`

### INFO-041 · ST_ODD_TEAMS · USA_USLLeagueOne
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLLeagueOne.csv`

### INFO-042 · ST_PLAYED_SPREAD · USA_USLLeagueOne
- Area: `standings`
- Dettaglio: Played min=32, max=35, delta=3; min: Westchester SC, Sarasota Paradise, Corpus Christi FC, AV Alta, Greenville, New York Cosmos; max: Boise, Forward Madison, Chattanooga Red Wolves.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\USA_USLLeagueOne.csv`

### INFO-043 · ST_ODD_TEAMS · Uganda_BigLeague
- Area: `standings`
- Dettaglio: Numero squadre dispari: 13.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Uganda_BigLeague.csv`

### INFO-044 · ST_PLAYED_SPREAD · Ukraine_PershaLiga
- Area: `standings`
- Dettaglio: Played min=12, max=15, delta=3; min: FC Chernihiv; max: Viktoria, Fenix Mariupol, Oleksandriya, Kulikiv, SC Poltava, Nyva Ternopil, Metalist Kharkiv, Lokomotyv Kyiv, Prykarpattya, UCSA, Probiy Horodenka, Zhytomyr 2.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Ukraine_PershaLiga.csv`

### INFO-045 · ST_ODD_TEAMS · Venezuela_LigaFUTVE2
- Area: `standings`
- Dettaglio: Numero squadre dispari: 17.
- Verifica suggerita: Verificare solo se il formato reale del campionato prevede un numero pari.
- Sorgente: `data\storico\classifiche_calcolate\Venezuela_LigaFUTVE2.csv`

### INFO-046 · ST_PLAYED_SPREAD · Wales_CymruNorth
- Area: `standings`
- Dettaglio: Played min=10, max=13, delta=3; min: Gresford; max: Porthmadog, Guilsfield, Buckley, Llanuwchllyn, Rhyl.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Wales_CymruNorth.csv`

### INFO-047 · ST_PLAYED_SPREAD · Wales_CymruSouth
- Area: `standings`
- Dettaglio: Played min=11, max=14, delta=3; min: Aberystwyth, Pure Swansea, Ynyshir Albions, Pontardawe, Newport City, Cardiff Draconians; max: Afan Lido, Llanelli.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Wales_CymruSouth.csv`

### INFO-048 · ST_PLAYED_SPREAD · Zambia_SuperLeague
- Area: `standings`
- Dettaglio: Played min=4, max=7, delta=3; min: Red Arrows; max: Nkana, Zesco Utd, NAPSA Stars.
- Verifica suggerita: Spread euristico: controllare risultati mancanti, alias, rinvii, fasi a gruppi o formato sbilanciato. Da solo non prova corruzione del dato.
- Sorgente: `data\storico\classifiche_calcolate\Zambia_SuperLeague.csv`
