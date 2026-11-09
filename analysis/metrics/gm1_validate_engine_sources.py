"""GM1 source audit: trace engine wrappers, scoring modules and contextual rules.

Run: python -m analysis.metrics.gm1_validate_engine_sources
Read-only; no engine or ranking modifications. Static audit, not proof that
every runtime branch is covered. Manual review is mandatory for complex rules.
"""
from __future__ import annotations

import ast
import csv
import importlib.util
from collections import Counter
from pathlib import Path

from gioover25.engines.factory import get_engine
from .gm1_walkforward_v2 import read_dataset, read_drivers

OUT = Path("data/analysis")
FIELDS = ("Engine", "Version", "EngineSource", "ScoringSources",
          "ReferencedEngines", "SourceMetrics", "GM1DriverSet",
          "MissingGM1Drivers", "ExtraGM1Drivers", "ContextRules",
          "RequiresDefenseLast5", "SelectionOnly", "AuditStatus")
METRIC_TOKENS = ("RankingGapScore", "HomeAttackScore", "AwayAttackScore",
                 "HomeDefenseWeaknessScore", "AwayDefenseWeaknessScore",
                 "HomeLast10OverScore", "AwayLast10OverScore",
                 "HomeVenueOverScore", "AwayVenueOverScore",
                 "BTTSProfileScore", "HomePPG", "AwayPPG",
                 "home_ga_last5", "away_ga_last5", "home_played",
                 "away_played", "home_ppg", "away_ppg",
                 "HomePlayed", "AwayPlayed", "HomeGALast5",
                 "AwayGALast5")
RULE_TOKENS = ("apply_contextual_band", "apply_defense_penalty",
               "SELECTION_ONLY", "REQUIRES_DEFENSE_LAST5",
               "PROX_", "MIN_", "THRESHOLD", "PROMOTION",
               "selected", "promoted")


def imports_from_source(source):
    tree = ast.parse(source)
    modules = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                # engine wrappers frequently use 'from . import v20'
                if node.level == 1 and not base:
                    modules.update("gioover25.engines." + a.name for a in node.names)
                elif node.level == 1:
                    modules.add("gioover25.engines." + base)
            elif base.startswith("gioover25."):
                modules.add(base)
        elif isinstance(node, ast.Import):
            modules.update(a.name for a in node.names
                           if a.name.startswith("gioover25."))
    return modules


def source_path(module):
    # Resolve relative to repository package without importing modules.
    root = Path(__file__).resolve().parents[2]
    path = root.joinpath(*module.split(".")).with_suffix(".py")
    return path if path.is_file() else None


def trace(engine):
    start = "gioover25.engines." + engine
    queue = [start]
    visited = set()
    texts = {}
    while queue:
        module = queue.pop()
        if module in visited:
            continue
        visited.add(module)
        path = source_path(module)
        if path is None:
            continue
        src = path.read_text(encoding="utf-8-sig")
        texts[module] = src
        for dep in imports_from_source(src):
            if dep.startswith(("gioover25.engines.", "gioover25.scoring_")):
                queue.append(dep)
    return texts


def run():
    fixtures = read_dataset()
    _, driver_sets = read_drivers(fixtures)
    rows = []
    for engine in sorted(driver_sets):
        module = get_engine(engine)
        sources = trace(module.__name__.split(".")[-1])
        text = "\n".join(sources.values())
        metrics = {token for token in METRIC_TOKENS if token in text}
        drivers = set(driver_sets[engine])
        # These are string/token observations, not proof of runtime influence.
        missing = sorted(metrics.intersection({
            "RankingGapScore", "HomeAttackScore", "AwayAttackScore",
            "HomeDefenseWeaknessScore", "AwayDefenseWeaknessScore",
            "HomeLast10OverScore", "AwayLast10OverScore",
            "HomeVenueOverScore", "AwayVenueOverScore",
            "BTTSProfileScore", "HomePPG", "AwayPPG"}) - drivers)
        extra = sorted(drivers - metrics)
        rules = sorted(t for t in RULE_TOKENS if t in text)
        referenced = sorted(m.split(".")[-1] for m in sources
                            if m.startswith("gioover25.engines.") and
                            m != module.__name__)
        scoring = sorted(m for m in sources if m.startswith("gioover25.scoring_"))
        status = ("REVIEW_REQUIRED" if missing or extra or rules
                  or len(sources) <= 1 else "SOURCE_TRACED_REVIEW")
        rows.append({
            "Engine": engine,
            "Version": getattr(module, "ENGINE_VERSION", ""),
            "EngineSource": module.__name__.replace(".", "/") + ".py",
            "ScoringSources": ",".join(s.replace(".", "/") + ".py" for s in scoring),
            "ReferencedEngines": ",".join(referenced),
            "SourceMetrics": ",".join(sorted(metrics)),
            "GM1DriverSet": ",".join(driver_sets[engine]),
            "MissingGM1Drivers": ",".join(missing),
            "ExtraGM1Drivers": ",".join(extra),
            "ContextRules": ",".join(rules),
            "RequiresDefenseLast5": bool(getattr(module, "REQUIRES_DEFENSE_LAST5", False)),
            "SelectionOnly": bool(getattr(module, "SELECTION_ONLY", False)),
            "AuditStatus": status,
        })
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "gm1_engine_source_profiles.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, delimiter=";", fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    statuses = Counter(r["AuditStatus"] for r in rows)
    print(f"[WRITE] {path}: {len(rows)} righe")
    for status, count in sorted(statuses.items()):
        print(f"[GM1-SOURCE] {status}={count}")
    for r in rows:
        if r["MissingGM1Drivers"] or r["ExtraGM1Drivers"]:
            print(f"[GM1-REVIEW] {r['Engine']}: missing={r['MissingGM1Drivers'] or '-'} "
                  f"extra={r['ExtraGM1Drivers'] or '-'}")
    print("[NOTE] Analisi statica conservativa: presenza di un token non "
          "dimostra che sia un driver effettivo. Nessun profilo e' automaticamente "
          "validato; confrontare i casi REVIEW_REQUIRED con lo scoring sorgente.")


if __name__ == "__main__":
    run()
