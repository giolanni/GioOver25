"""GM1 - audit in sola lettura dei dati disponibili per la somiglianza.

Esecuzione: python -m analysis.metrics.gm1_data_audit
Non modifica ranking, engine o storici. Genera report in data/analysis/.
"""
from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path

from .build_engine_league_high_rankings import detect_delimiter, find_engine_histories

OUT = Path("data/analysis")
FIELDS = (
    "PredictionDate", "MatchDate", "LeagueId", "Home", "Away", "Score", "Band",
    "MatchStatus", "HG", "AG", "Goals", "Over25", "BTTS", "Reason",
    "RankingGapScore", "HomeAttackScore", "AwayAttackScore",
    "HomeDefenseWeaknessScore", "AwayDefenseWeaknessScore",
    "HomeLast10OverScore", "AwayLast10OverScore", "HomeVenueOverScore",
    "AwayVenueOverScore", "BTTSProfileScore", "AlgorithmVersion",
    "ExpectedGoals", "HomePlayed", "AwayPlayed", "HomePPG", "AwayPPG",
    "HomeGFLast5", "AwayGFLast5", "HomeGALast5", "AwayGALast5",
)
FEATURES = (
    "Score", "RankingGapScore", "HomeAttackScore", "AwayAttackScore",
    "HomeDefenseWeaknessScore", "AwayDefenseWeaknessScore",
    "HomeLast10OverScore", "AwayLast10OverScore",
    "HomeVenueOverScore", "AwayVenueOverScore", "BTTSProfileScore",
    "ExpectedGoals", "HomePlayed", "AwayPlayed", "HomePPG", "AwayPPG",
    "HomeGFLast5", "AwayGFLast5", "HomeGALast5", "AwayGALast5",
)
KEY = ("LeagueId", "MatchDate", "Home", "Away")
REQUIRED = KEY + ("Band", "Score", "Over25")
COLUMNS = ("Engine", "Rows", "Resolved", "ValidKey", "WithScore", "WithBand",
           "WithExpectedGoals", "WithAllBaseDrivers", "UniqueResolvedMatches",
           "DuplicateResolvedRows", "ConflictingResolvedOutcomes",
           "MissingColumns")


def write(path: Path, rows: list[dict], fields: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")


def audit() -> None:
    summaries, coverage, warnings = [], [], []
    paths = [(engine, path) for engine, path in find_engine_histories()
             if not engine.lower().startswith("vg")]
    if not paths:
        raise SystemExit("Nessuno storico Over2.5 trovato.")
    for engine, path in paths:
        with path.open(encoding="utf-8-sig", errors="replace", newline="") as stream:
            reader = csv.DictReader(stream, delimiter=detect_delimiter(path))
            headers = set(reader.fieldnames or [])
            missing = sorted(set(REQUIRED) - headers)
            if missing:
                warnings.append({"Engine": engine, "Issue": "MISSING_REQUIRED_COLUMNS",
                                 "Detail": ",".join(missing)})
            counts = Counter()
            nonempty = Counter()
            outcome_by_key = defaultdict(set)
            duplicate_counts = Counter()
            for row in reader:
                counts["rows"] += 1
                for field in FEATURES:
                    if str(row.get(field) or "").strip():
                        nonempty[field] += 1
                if all(str(row.get(k) or "").strip() for k in KEY):
                    counts["valid_key"] += 1
                if str(row.get("Score") or "").strip():
                    counts["score"] += 1
                if str(row.get("Band") or "").strip():
                    counts["band"] += 1
                if str(row.get("ExpectedGoals") or "").strip():
                    counts["eg"] += 1
                if all(str(row.get(k) or "").strip() for k in FEATURES[1:11]):
                    counts["drivers"] += 1
                outcome = str(row.get("Over25") or "").strip().upper()
                if outcome in ("OK", "KO"):
                    counts["resolved"] += 1
                    key = tuple(str(row.get(k) or "").strip() for k in KEY)
                    if all(key):
                        outcome_by_key[key].add(outcome)
                        duplicate_counts[key] += 1
            n = counts["rows"]
            summaries.append({
                "Engine": engine, "Rows": n, "Resolved": counts["resolved"],
                "ValidKey": counts["valid_key"], "WithScore": counts["score"],
                "WithBand": counts["band"], "WithExpectedGoals": counts["eg"],
                "WithAllBaseDrivers": counts["drivers"],
                "UniqueResolvedMatches": len(outcome_by_key),
                "DuplicateResolvedRows": sum(v - 1 for v in duplicate_counts.values()),
                "ConflictingResolvedOutcomes": sum(len(v) > 1 for v in outcome_by_key.values()),
                "MissingColumns": ",".join(missing),
            })
            for field in FEATURES:
                coverage.append({"Engine": engine, "Feature": field,
                                 "ColumnExists": int(field in headers),
                                 "NonEmptyRows": nonempty[field],
                                 "TotalRows": n,
                                 "CoveragePct": round(100 * nonempty[field] / n, 2) if n else 0})
            print(f"[GM1] {engine}: {n} righe, {counts['resolved']} con esito, "
                  f"{counts['drivers']} con driver base completi")
    write(OUT / "gm1_data_audit_summary.csv", summaries, COLUMNS)
    write(OUT / "gm1_data_audit_features.csv", coverage,
          ("Engine", "Feature", "ColumnExists", "NonEmptyRows", "TotalRows", "CoveragePct"))
    write(OUT / "gm1_data_audit_warnings.csv", warnings,
          ("Engine", "Issue", "Detail"))
    print("[GM1] Audit completato. Nessun ranking modificato.")


if __name__ == "__main__":
    audit()
