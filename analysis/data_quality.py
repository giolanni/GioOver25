"""GioOver2.5 data quality inspector.

Usage:
    python -m analysis.data_quality --quick
    python -m analysis.data_quality --full

Read-only: never modifies source data. Reports are written under
analysis/data_quality_report/ for human/AI review.
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path

from gioover25.team_names import normalize_team_name

ROOT = Path(__file__).resolve().parents[1]
STANDINGS_DIR = ROOT / "data" / "storico" / "classifiche_calcolate"
RESULTS_DIR = ROOT / "data" / "storico" / "risultati"
REGISTRY_FILE = ROOT / "data" / "league_registry.csv"
LAB_FILE = ROOT / "analysis" / "laboratory" / "data" / "01_matches.csv"
LAB_UNMATCHED = ROOT / "analysis" / "laboratory" / "data" / "06_unmatched_matches.csv"
REPORT_DIR = ROOT / "analysis" / "data_quality_report"

SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}


@dataclass
class Anomaly:
    severity: str
    area: str
    code: str
    league_id: str = ""
    match_date: str = ""
    home: str = ""
    away: str = ""
    detail: str = ""
    suggestion: str = ""
    source: str = ""


def add(items: list[Anomaly], severity: str, area: str, code: str, **kwargs) -> None:
    items.append(Anomaly(severity=severity, area=area, code=code, **kwargs))


def text(row: dict, key: str) -> str:
    return str(row.get(key, "") or "").strip()


def number(value, default=None):
    try:
        raw = str(value).strip().replace(",", ".")
        return float(raw) if raw else default
    except (TypeError, ValueError):
        return default


def integer(value, default=None):
    value = number(value, None)
    if value is None or not float(value).is_integer():
        return default
    return int(value)


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        try:
            delimiter = csv.Sniffer().sniff(sample, delimiters=";,\t").delimiter
        except csv.Error:
            delimiter = ";"
        return list(csv.DictReader(handle, delimiter=delimiter))


def check_standings(items: list[Anomaly]) -> tuple[int, int]:
    files = sorted(STANDINGS_DIR.glob("*.csv"))
    row_count = 0
    for path in files:
        league = path.stem
        rows = read_csv(path)
        row_count += len(rows)
        if not rows:
            add(items, "CRITICAL", "standings", "ST_EMPTY", league_id=league,
                detail="Classifica vuota o non leggibile.", source=str(path.relative_to(ROOT)))
            continue

        teams = [text(r, "Team") for r in rows]
        normalized = [t.casefold().strip() for t in teams if t]
        duplicates = [t for t, n in Counter(normalized).items() if n > 1]
        if duplicates:
            add(items, "CRITICAL", "standings", "ST_DUP_TEAM", league_id=league,
                detail=f"Squadre duplicate: {', '.join(duplicates[:10])}",
                suggestion="Verificare alias/normalizzazione nomi squadra.", source=str(path.relative_to(ROOT)))

        identity_groups: dict[str, list[str]] = defaultdict(list)
        for team in teams:
            if team:
                identity_groups[normalize_team_name(league, team)].append(team)
        aliases = [sorted(set(names)) for names in identity_groups.values() if len(set(names)) > 1]
        if aliases:
            rendered = [" / ".join(group) for group in aliases[:10]]
            add(items, "CRITICAL", "standings", "ST_ALIAS_SUSPECTED", league_id=league,
                detail=f"Più nomi risolvono alla stessa identità canonica: {', '.join(rendered)}.",
                suggestion="Consolidare tramite team_name_dictionary.csv e rigenerare classifica/Laboratory.",
                source=str(path.relative_to(ROOT)))

        if len(rows) % 2:
            add(items, "INFO", "standings", "ST_ODD_TEAMS", league_id=league,
                detail=f"Numero squadre dispari: {len(rows)}.",
                suggestion="Verificare solo se il formato reale del campionato prevede un numero pari.", source=str(path.relative_to(ROOT)))

        positions = [integer(r.get("Position")) for r in rows]
        valid_positions = [p for p in positions if p is not None]
        expected = set(range(1, len(rows) + 1))
        if set(valid_positions) != expected or len(valid_positions) != len(set(valid_positions)):
            add(items, "WARNING", "standings", "ST_POSITIONS", league_id=league,
                detail=f"Posizioni non consecutive/univoche: {valid_positions}.", source=str(path.relative_to(ROOT)))

        played_values = [integer(r.get("Played")) for r in rows]
        valid_played = [p for p in played_values if p is not None]
        if valid_played:
            delta = max(valid_played) - min(valid_played)
            severity = "CRITICAL" if delta >= 6 else "WARNING" if delta >= 4 else "INFO" if delta >= 3 else None
            if severity:
                low = [text(r, "Team") for r in rows if integer(r.get("Played")) == min(valid_played)]
                high = [text(r, "Team") for r in rows if integer(r.get("Played")) == max(valid_played)]
                add(items, severity, "standings", "ST_PLAYED_SPREAD", league_id=league,
                    detail=f"Played min={min(valid_played)}, max={max(valid_played)}, delta={delta}; min: {', '.join(low)}; max: {', '.join(high)}.",
                    suggestion="Controllare risultati mancanti, squadra duplicata/alias, rinvii o cambio formato.", source=str(path.relative_to(ROOT)))

        for r in rows:
            team = text(r, "Team")
            played = integer(r.get("Played")); wins = integer(r.get("Wins")); draws = integer(r.get("Draws")); losses = integer(r.get("Losses"))
            gf = integer(r.get("GF")); ga = integer(r.get("GA")); gd = integer(r.get("GD")); points = integer(r.get("Points")); ppg = number(r.get("PPG"))
            if None not in (played, wins, draws, losses) and played != wins + draws + losses:
                add(items, "CRITICAL", "standings", "ST_WDL", league_id=league,
                    detail=f"{team}: Played={played}, W+D+L={wins + draws + losses}.", source=str(path.relative_to(ROOT)))
            if None not in (gf, ga, gd) and gd != gf - ga:
                add(items, "CRITICAL", "standings", "ST_GD", league_id=league,
                    detail=f"{team}: GD={gd}, ma GF-GA={gf-ga}.", source=str(path.relative_to(ROOT)))
            if None not in (played, points, ppg) and played > 0 and not math.isclose(ppg, points / played, abs_tol=0.006):
                add(items, "WARNING", "standings", "ST_PPG", league_id=league,
                    detail=f"{team}: PPG={ppg}, atteso circa {points/played:.3f} da Points/Played.", source=str(path.relative_to(ROOT)))
    return len(files), row_count


def registry_ids() -> set[str]:
    return {text(r, "LeagueId") for r in read_csv(REGISTRY_FILE) if text(r, "LeagueId")}


def check_results(items: list[Anomaly], known_leagues: set[str]) -> tuple[int, int]:
    files = sorted(RESULTS_DIR.glob("*.csv"))
    total = 0
    global_keys: dict[tuple, str] = {}
    for path in files:
        league_from_file = path.stem
        rows = read_csv(path)
        total += len(rows)
        if known_leagues and league_from_file not in known_leagues:
            add(items, "WARNING", "registry", "REG_RESULT_MISSING", league_id=league_from_file,
                detail="File risultati con LeagueId non presente nel registry.", source=str(path.relative_to(ROOT)))
        for idx, r in enumerate(rows, 2):
            league = text(r, "LeagueId") or league_from_file
            md = text(r, "MatchDate"); home = text(r, "Home"); away = text(r, "Away")
            source = f"{path.relative_to(ROOT)}:{idx}"
            if home and away and home.casefold() == away.casefold():
                add(items, "CRITICAL", "results", "RS_SELF_MATCH", league_id=league, match_date=md, home=home, away=away,
                    detail="Home e Away coincidono.", source=source)
            if md:
                try:
                    date.fromisoformat(md)
                except ValueError:
                    add(items, "WARNING", "results", "RS_BAD_DATE", league_id=league, match_date=md, home=home, away=away,
                        detail="MatchDate non ISO YYYY-MM-DD.", source=source)
            key = (league, md, normalize_team_name(league, home), normalize_team_name(league, away))
            if all(key):
                previous = global_keys.get(key)
                if previous:
                    add(items, "CRITICAL", "results", "RS_DUP_MATCH", league_id=league, match_date=md, home=home, away=away,
                        detail=f"Partita duplicata; prima occorrenza: {previous}.", source=source)
                else:
                    global_keys[key] = source
            hg = integer(r.get("HG")); ag = integer(r.get("AG"))
            if (hg is None) != (ag is None):
                add(items, "WARNING", "results", "RS_HALF_SCORE", league_id=league, match_date=md, home=home, away=away,
                    detail=f"Risultato incompleto HG={text(r,'HG')} AG={text(r,'AG')}.", source=source)
            if hg is not None and ag is not None and (hg < 0 or ag < 0 or hg > 20 or ag > 20):
                add(items, "CRITICAL", "results", "RS_SCORE_RANGE", league_id=league, match_date=md, home=home, away=away,
                    detail=f"Punteggio anomalo {hg}-{ag}.", source=source)
    return len(files), total


def check_laboratory(items: list[Anomaly], known_leagues: set[str]) -> int:
    rows = read_csv(LAB_FILE)
    seen: dict[tuple, tuple[str, str, str]] = {}
    for idx, r in enumerate(rows, 2):
        league = text(r, "LeagueId"); md = text(r, "MatchDate"); home = text(r, "Home"); away = text(r, "Away")
        engine = text(r, "AlgorithmVersion")
        source = f"{LAB_FILE.relative_to(ROOT)}:{idx}"
        if known_leagues and league and league not in known_leagues:
            add(items, "WARNING", "laboratory", "LAB_REGISTRY", league_id=league, match_date=md, home=home, away=away,
                detail="LeagueId del Laboratory assente dal registry.", source=source)
        if home and away and home.casefold() == away.casefold():
            add(items, "CRITICAL", "laboratory", "LAB_SELF_MATCH", league_id=league, match_date=md, home=home, away=away,
                detail="Home e Away coincidono.", source=source)
        hg = integer(r.get("HG")); ag = integer(r.get("AG")); goals = integer(r.get("Goals"))
        if None not in (hg, ag, goals) and goals != hg + ag:
            add(items, "CRITICAL", "laboratory", "LAB_GOALS", league_id=league, match_date=md, home=home, away=away,
                detail=f"Goals={goals}, ma HG+AG={hg+ag}.", source=source)
        btts = text(r, "BTTS").casefold()
        if hg is not None and ag is not None and btts:
            expected = hg > 0 and ag > 0
            truthy = btts in {"1", "true", "yes", "si", "sì", "ok"}
            falsy = btts in {"0", "false", "no", "ko"}
            if (truthy or falsy) and truthy != expected:
                add(items, "WARNING", "laboratory", "LAB_BTTS", league_id=league, match_date=md, home=home, away=away,
                    detail=f"BTTS={text(r,'BTTS')} incompatibile con {hg}-{ag}.", source=source)
        key = (league, md, normalize_team_name(league, home), normalize_team_name(league, away), engine)
        signature = (text(r, "HG"), text(r, "AG"), text(r, "Outcome"))
        if all(key):
            if key in seen:
                previous = seen[key]
                severity = "CRITICAL" if previous != signature else "WARNING"
                add(items, severity, "laboratory", "LAB_DUP_MATCH", league_id=league, match_date=md, home=home, away=away,
                    detail=f"Duplicato per engine {engine}; valori precedenti={previous}, attuali={signature}.", source=source)
            else:
                seen[key] = signature
    if LAB_UNMATCHED.exists():
        unmatched = read_csv(LAB_UNMATCHED)
        if unmatched:
            add(items, "INFO", "laboratory", "LAB_UNMATCHED", detail=f"06_unmatched_matches.csv contiene {len(unmatched)} righe da esaminare.",
                suggestion="Analizzare soprattutto LeagueId/team ricorrenti: possono indicare alias o ranking non agganciati.", source=str(LAB_UNMATCHED.relative_to(ROOT)))
    return len(rows)


def write_reports(items: list[Anomaly], stats: dict) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    items.sort(key=lambda x: (SEVERITY_ORDER.get(x.severity, 9), x.area, x.league_id, x.code))
    csv_path = REPORT_DIR / "anomalies.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(Anomaly("", "", "")).keys()), delimiter=";")
        writer.writeheader()
        writer.writerows(asdict(item) for item in items)

    counts = Counter(item.severity for item in items)
    lines = [
        "# GioOver2.5 - Data Quality Report",
        "",
        "Report diagnostico READ-ONLY. Le anomalie euristiche non implicano automaticamente dati errati.",
        "",
        "## Riepilogo",
        "",
        f"- Modalità: **{stats['mode']}**",
        f"- Classifiche analizzate: **{stats['standings_files']}** ({stats['standings_rows']} squadre/righe)",
        f"- File risultati analizzati: **{stats['results_files']}** ({stats['results_rows']} partite)" if stats['mode'] == 'full' else "- Risultati storici: non analizzati in quick mode",
        f"- Righe Laboratory analizzate: **{stats['lab_rows']}**" if stats['mode'] == 'full' else "- Laboratory: non analizzato in quick mode",
        f"- CRITICAL: **{counts['CRITICAL']}**",
        f"- WARNING: **{counts['WARNING']}**",
        f"- INFO: **{counts['INFO']}**",
        "",
        "## Priorità per analisi IA",
        "",
        "Analizzare prima i CRITICAL. Prima di bonificare verificare sempre il formato reale della competizione e lo storico sorgente. WARNING/INFO possono essere legittimi (rinvii, campionati dispari, formati speciali).",
        "",
    ]
    for severity in ("CRITICAL", "WARNING", "INFO"):
        selected = [x for x in items if x.severity == severity]
        lines += [f"## {severity} ({len(selected)})", ""]
        if not selected:
            lines += ["Nessuna anomalia.", ""]
            continue
        for n, x in enumerate(selected, 1):
            subject = " | ".join(v for v in (x.league_id, x.match_date, f"{x.home} - {x.away}" if x.home or x.away else "") if v)
            lines.append(f"### {severity}-{n:03d} · {x.code}" + (f" · {subject}" if subject else ""))
            lines.append(f"- Area: `{x.area}`")
            lines.append(f"- Dettaglio: {x.detail}")
            if x.suggestion:
                lines.append(f"- Verifica suggerita: {x.suggestion}")
            if x.source:
                lines.append(f"- Sorgente: `{x.source}`")
            lines.append("")
    (REPORT_DIR / "report_ai.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="GioOver2.5 data quality inspector (read-only)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--quick", action="store_true", help="Controlla solo le classifiche calcolate")
    group.add_argument("--full", action="store_true", help="Controlla classifiche, risultati, registry e Laboratory")
    args = parser.parse_args()
    mode = "quick" if args.quick else "full"

    anomalies: list[Anomaly] = []
    standings_files, standings_rows = check_standings(anomalies)
    results_files = results_rows = lab_rows = 0
    if mode == "full":
        known = registry_ids()
        results_files, results_rows = check_results(anomalies, known)
        lab_rows = check_laboratory(anomalies, known)

    stats = {
        "mode": mode,
        "standings_files": standings_files,
        "standings_rows": standings_rows,
        "results_files": results_files,
        "results_rows": results_rows,
        "lab_rows": lab_rows,
    }
    write_reports(anomalies, stats)
    counts = Counter(x.severity for x in anomalies)
    print("[DATA QUALITY] completato")
    print(f"  mode={mode} | CRITICAL={counts['CRITICAL']} WARNING={counts['WARNING']} INFO={counts['INFO']}")
    print(f"  report: {REPORT_DIR / 'report_ai.md'}")
    print(f"  csv:    {REPORT_DIR / 'anomalies.csv'}")


if __name__ == "__main__":
    main()
