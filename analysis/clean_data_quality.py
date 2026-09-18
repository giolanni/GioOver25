"""Bonifica prudente degli storici risultati GioOver2.5.

Default = dry-run. Con --apply:
- rimuove duplicati con identica chiave canonica LeagueId+MatchDate+Home+Away;
- rimuove self-match (Home == Away dopo normalizzazione);
- crea backup dei soli file modificati;
- riscrive i risultati usando i nomi canonici già presenti nel dizionario;
- rigenera le classifiche delle sole leghe modificate.

Non prova a correggere automaticamente contaminazioni di lega o alias non censiti.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path

from gioover25.history import read_results_file, write_results_file
from gioover25.standings import generate_current_standings_file
from gioover25.team_names import normalize_team_name

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "data" / "storico" / "risultati"
STANDINGS_DIR = ROOT / "data" / "storico" / "classifiche_calcolate"
BACKUP_ROOT = ROOT / "data" / "debug" / "data_quality_backups"


def match_key(league_id, match):
    return (
        str(match.date).strip(),
        normalize_team_name(league_id, match.home),
        normalize_team_name(league_id, match.away),
    )


def clean_file(path: Path):
    league_id = path.stem
    matches = read_results_file(path)
    kept = []
    seen = set()
    duplicate_count = 0
    self_count = 0

    for match in matches:
        home_id = normalize_team_name(league_id, match.home)
        away_id = normalize_team_name(league_id, match.away)
        if home_id == away_id:
            self_count += 1
            continue
        key = match_key(league_id, match)
        if key in seen:
            duplicate_count += 1
            continue
        seen.add(key)
        kept.append(match)

    return matches, kept, duplicate_count, self_count


def main():
    parser = argparse.ArgumentParser(description="Bonifica prudente storici risultati")
    parser.add_argument("--apply", action="store_true", help="Applica la bonifica; senza flag esegue solo dry-run")
    args = parser.parse_args()

    changed = []
    total_dup = total_self = 0
    for path in sorted(RESULTS_DIR.glob("*.csv")):
        original, cleaned, dup, self_matches = clean_file(path)
        if not dup and not self_matches:
            continue
        changed.append((path, original, cleaned, dup, self_matches))
        total_dup += dup
        total_self += self_matches
        print(f"[FOUND] {path.stem}: duplicati={dup}, self_match={self_matches}")

    print(f"\nTotale: file={len(changed)}, duplicati={total_dup}, self_match={total_self}")
    if not args.apply:
        print("DRY-RUN: nessun file modificato. Usa --apply per applicare.")
        return

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_ROOT / stamp
    backup_dir.mkdir(parents=True, exist_ok=True)

    for path, original, cleaned, dup, self_matches in changed:
        shutil.copy2(path, backup_dir / path.name)
        write_results_file(cleaned, path)
        standings = STANDINGS_DIR / path.name
        generate_current_standings_file(path, standings)
        print(f"[CLEAN] {path.stem}: -{dup} duplicati, -{self_matches} self-match")

    print(f"Backup: {backup_dir}")
    print("Bonifica completata. Ora rigenerare il Laboratory e rilanciare data_quality --full.")


if __name__ == "__main__":
    main()
