from pathlib import Path
import shutil

TARGET = Path('gioover25/rank_matches_v2.py')
BACKUP = Path('gioover25/rank_matches_v2.py.bak_immature_band')

if not TARGET.exists():
    raise FileNotFoundError(f'File non trovato: {TARGET}')

text = TARGET.read_text(encoding='utf-8')
original = text

# 1) Parametri di maturità.
old = 'MIN_COMPLETED_ROUNDS_PER_LEAGUE = 5\nREGISTRY_FILE = Path("data/league_registry.csv")'
new = '''# Regola campione immaturo:\n# - HomePlayed + AwayPlayed < 4  -> partita esclusa\n# - totale >= 4 ma almeno una squadra < 5 gare -> score calcolato comunque\n#   e, se sarebbe ALTA, Band = IMM-ALTA-# dove # è il totale gare\n# - entrambe >= 5 -> fascia normale\nMIN_TOTAL_TEAM_MATCHES = 4\nMATURE_TEAM_MATCHES = 5\nREGISTRY_FILE = Path("data/league_registry.csv")'''
if old not in text:
    raise RuntimeError('Anchor 1 non trovato: costante MIN_COMPLETED_ROUNDS_PER_LEAGUE')
text = text.replace(old, new, 1)

# 2) Nessuno storico: ora il messaggio riflette la soglia totale minima.
old = '''        # Se non esiste ancora alcun file storico, la competizione è appena iniziata\n        # oppure non sono stati ancora acquisiti risultati.\n        #\n        # In questa situazione la lega equivale ad avere zero partite concluse:\n        # non deve interrompere l'elaborazione degli altri campionati, ma deve essere\n        # semplicemente esclusa dal ranking fino al raggiungimento della soglia minima.\n        if not histories:\n            print(\n                f"[SKIP] {league_id}: nessuno storico risultati disponibile "\n                f"(0 partite concluse, minimo richiesto: 5)."\n            )\n            continue\n\n        # Per le leghe ordinarie il controllo usa lo storico della singola lega.\n        # Per play-in/playoff e CompetitionGroup usa gli storici divisionali\n        # disponibili, perché la fase dedicata può non avere ancora un file proprio.\n        readiness_matches = (\n            [\n                match\n                for source_matches in histories.values()\n                for match in source_matches\n            ]\n            if competition_group\n            else histories.get(league_id, [])\n        )\n\n        completed_rounds = count_completed_rounds_before(\n            readiness_matches,\n            match_date_value,\n        )\n\n        if completed_rounds < MIN_COMPLETED_ROUNDS_PER_LEAGUE:\n            print(\n                f"[SKIP] {league_id}: solo {completed_rounds} turni conclusi "\n                f"prima del {match_date_text}; minimo richiesto: "\n                f"{MIN_COMPLETED_ROUNDS_PER_LEAGUE}."\n            )\n            continue\n'''
new = '''        # Se non esiste alcuno storico, Home + Away hanno complessivamente\n        # meno delle 4 gare minime richieste: la partita resta esclusa.\n        if not histories:\n            print(\n                f"[SKIP] {league_id}: nessuno storico risultati disponibile "\n                f"(minimo {MIN_TOTAL_TEAM_MATCHES} gare complessive Home+Away)."\n            )\n            continue\n'''
if old not in text:
    raise RuntimeError('Anchor 2 non trovato: vecchio blocco readiness/completed rounds')
text = text.replace(old, new, 1)

# 3) Dopo aver individuato HomeSource/AwaySource, calcola sempre GP/PPG e applica soglia totale 4.
old = '''        away_source = find_team_source_league(\n            away,\n            histories,\n            match_date_value,\n            fallback_league_id=fallback_league_id,\n        )\n        # L'unione è sicura perché build_match_statistics filtra per squadra.\n'''
new = '''        away_source = find_team_source_league(\n            away,\n            histories,\n            match_date_value,\n            fallback_league_id=fallback_league_id,\n        )\n\n        # --------------------------------------------------------------\n        # MATURITÀ DEL CAMPIONE - valutata sulle due squadre.\n        # --------------------------------------------------------------\n        (\n            home_played,\n            home_points,\n            home_ppg,\n        ) = calculate_team_ppg_before_match(\n            team=home,\n            source_league_id=home_source,\n            histories=histories,\n            match_date=match_date_value,\n        )\n\n        (\n            away_played,\n            away_points,\n            away_ppg,\n        ) = calculate_team_ppg_before_match(\n            team=away,\n            source_league_id=away_source,\n            histories=histories,\n            match_date=match_date_value,\n        )\n\n        total_played = home_played + away_played\n\n        if total_played < MIN_TOTAL_TEAM_MATCHES:\n            print(\n                f"[SKIP] {league_id} | {home} - {away}: "\n                f"GP={home_played}/{away_played}, totale={total_played}; "\n                f"minimo richiesto: {MIN_TOTAL_TEAM_MATCHES}."\n            )\n            continue\n\n        immature_sample = (\n            home_played < MATURE_TEAM_MATCHES\n            or away_played < MATURE_TEAM_MATCHES\n        )\n\n        # L'unione è sicura perché build_match_statistics filtra per squadra.\n'''
if old not in text:
    raise RuntimeError('Anchor 3 non trovato: blocco away_source')
text = text.replace(old, new, 1)

# 4) Non ricalcolare GP/PPG dentro il solo blocco contestuale: ora sono già disponibili per tutti gli engine.
old = '''        if callable(apply_contextual_band):\n            (\n                home_played,\n                home_points,\n                home_ppg,\n            ) = calculate_team_ppg_before_match(\n                team=home,\n                source_league_id=home_source,\n                histories=histories,\n                match_date=match_date_value,\n            )\n\n            (\n                away_played,\n                away_points,\n                away_ppg,\n            ) = calculate_team_ppg_before_match(\n                team=away,\n                source_league_id=away_source,\n                histories=histories,\n                match_date=match_date_value,\n            )\n\n            base_band = score_value(\n                score,\n                "band",\n            )\n'''
new = '''        if callable(apply_contextual_band):\n            base_band = score_value(\n                score,\n                "band",\n            )\n'''
if old not in text:
    raise RuntimeError('Anchor 4 non trovato: ricalcolo GP/PPG nel blocco contestuale')
text = text.replace(old, new, 1)

# 5) Aggiunge IMM-ALTA dopo gli eventuali driver contestuali e prima dell'output.
old = '''            if contextual_band != base_band:\n                print(\n                    f"[{engine_name}][PROX] "\n                    f"{home} - {away}: "\n                    f"{base_band} -> {contextual_band} | "\n                    f"GP={home_played}/{away_played} | "\n                    f"PPG={home_ppg:.3f}/{away_ppg:.3f} | "\n                    f"gap={abs(home_ppg - away_ppg):.3f}"\n                )\n\n        results.append(build_output_row(\n'''
new = '''            if contextual_band != base_band:\n                print(\n                    f"[{engine_name}][PROX] "\n                    f"{home} - {away}: "\n                    f"{base_band} -> {contextual_band} | "\n                    f"GP={home_played}/{away_played} | "\n                    f"PPG={home_ppg:.3f}/{away_ppg:.3f} | "\n                    f"gap={abs(home_ppg - away_ppg):.3f}"\n                )\n\n        # --------------------------------------------------------------\n        # CAMPIONE IMMATURO\n        # --------------------------------------------------------------\n        # Lo score resta invariato. Se almeno una squadra ha meno di 5 gare\n        # ma Home+Away totalizzano almeno 4 gare, una ALTA non viene certificata\n        # come ALTA piena: diventa IMM-ALTA-# (es. IMM-ALTA-7).\n        base_band = score_value(\n            score,\n            "band",\n        )\n\n        if immature_sample and base_band == "ALTA":\n            contextual_band = f"IMM-ALTA-{total_played}"\n\n            print(\n                f"[{engine_name}][IMM] {home} - {away}: "\n                f"ALTA -> {contextual_band} | "\n                f"GP={home_played}/{away_played} | totale={total_played}"\n            )\n\n        results.append(build_output_row(\n'''
if old not in text:
    raise RuntimeError('Anchor 5 non trovato: inserimento IMM-ALTA')
text = text.replace(old, new, 1)

if text == original:
    raise RuntimeError('Nessuna modifica applicata.')

if not BACKUP.exists():
    shutil.copy2(TARGET, BACKUP)

TARGET.write_text(text, encoding='utf-8')

# Controllo sintattico.
compile(text, str(TARGET), 'exec')

print(f'OK: modificato {TARGET}')
print(f'Backup: {BACKUP}')
print('Regola attiva:')
print('  totale Home+Away < 4 -> SKIP')
print('  totale >= 4 e almeno una squadra < 5 -> score calcolato')
print('  se Band base = ALTA -> IMM-ALTA-#')
print('  entrambe >= 5 -> comportamento normale')
