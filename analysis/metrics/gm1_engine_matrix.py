"""GM1: matrice comparativa per partita e engine, senza alterare gli engine.

Esecuzione: python -m analysis.metrics.gm1_engine_matrix
Input: gm1_pre_match_dataset.csv + storici ranking (driver originali).
Output: matrice long, confronto per partita e audit.
ALTA = previsione Over2.5; MEDIA = previsione Over1.5.
Le altre fasce restano NON_VALUTATE: non si attribuisce una scommessa
Under o un KO implicito. Engine sullo stesso mercato condividono esito.
"""
from __future__ import annotations
import csv
from collections import Counter, defaultdict
from pathlib import Path
from .gm1_walkforward_v2 import DRIVERS, KEY, read_dataset, read_drivers

OUT = Path("data/analysis")
LONG_FIELDS = (*KEY, "Engine", "Band", "Score", "Market", "PredictionResult",
               "Over25", "Over15", "HomePlayed", "AwayPlayed", "HomePPG",
               "AwayPPG", "HomeGFLast5", "AwayGFLast5",
               "HomeGALast5", "AwayGALast5", "HomeOver25Last5",
               "AwayOver25Last5", "HomeBTTSLast5", "AwayBTTSLast5",
               "HomeVenueOver25", "AwayVenueOver25", "DriverSet",
               *DRIVERS)
FIXTURE_FIELDS = (*KEY, "Engines", "ALTA_Engines", "MEDIA_Engines",
                  "Other_Engines", "DifferentMarkets", "Over25", "Over15",
                  "AltaOK", "AltaKO", "MediaOK", "MediaKO",
                  "AltaEngineNames", "MediaEngineNames", "OtherEngineNames")
AUDIT_FIELDS = ("Issue", "Count")


def write(name, columns, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, delimiter=";")
        w.writeheader()
        w.writerows(rows)
    print(f"[WRITE] {path}: {len(rows)} righe")


def classify(band):
    band = (band or "").strip().upper()
    if band == "ALTA":
        return "Over25"
    if band == "MEDIA":
        return "Over15"
    return ""


def run():
    fixtures = read_dataset()
    values, selected = read_drivers(fixtures)
    long_rows, fixture_rows = [], []
    audit = Counter()
    engines = set()
    for key, fixture in sorted(fixtures.items()):
        rows = fixture["rows"]
        if not rows:
            continue
        audit["fixtures"] += 1
        engines.update(rows)
        # Outcome must be fixture-level, independent of engine.
        over25 = {r["Over25"] for r in rows.values()
                  if r.get("Over25") in ("OK", "KO")}
        over15 = {r["Over15"] for r in rows.values()
                  if r.get("Over15") in ("OK", "KO")}
        if len(over25) != 1 or len(over15) != 1:
            audit["outcome_conflicts"] += 1
            continue
        actual = {"Over25": next(iter(over25)), "Over15": next(iter(over15))}
        buckets = defaultdict(list)
        for engine, row in sorted(rows.items()):
            market = classify(row.get("Band"))
            outcome = actual[market] if market else "NOT_EVALUATED"
            buckets[market].append(engine)
            raw = values.get((engine, key), {})
            if not raw:
                audit["missing_driver_rows"] += 1
            record = dict(zip(KEY, key))
            record.update({
                "Engine": engine, "Band": row.get("Band", ""),
                "Score": row.get("Score", ""), "Market": market or "NOT_EVALUATED",
                "PredictionResult": outcome,
                "Over25": actual["Over25"], "Over15": actual["Over15"],
                "DriverSet": ",".join(selected.get(engine, ())),
            })
            for field in LONG_FIELDS:
                if field in row and field not in record:
                    record[field] = row[field]
            for field in DRIVERS:
                value = raw.get(field)
                record[field] = "" if value is None else value
            long_rows.append(record)
            audit["engine_predictions"] += 1
            if market:
                audit["evaluated_" + market] += 1
            else:
                audit["not_evaluated"] += 1
        alta, media, other = buckets["Over25"], buckets["Over15"], buckets[""]
        if alta and media:
            audit["cross_market_disagreement"] += 1
        if alta and other or media and other:
            audit["with_unscored_bands"] += 1
        if len(alta) > 1:
            audit["same_market_alta_ties"] += 1
        if len(media) > 1:
            audit["same_market_media_ties"] += 1
        fixture_rows.append({
            **dict(zip(KEY, key)), "Engines": len(rows),
            "ALTA_Engines": len(alta), "MEDIA_Engines": len(media),
            "Other_Engines": len(other),
            "DifferentMarkets": int(bool(alta and media)),
            **actual,
            "AltaOK": len(alta) if actual["Over25"] == "OK" else 0,
            "AltaKO": len(alta) if actual["Over25"] == "KO" else 0,
            "MediaOK": len(media) if actual["Over15"] == "OK" else 0,
            "MediaKO": len(media) if actual["Over15"] == "KO" else 0,
            "AltaEngineNames": ",".join(alta),
            "MediaEngineNames": ",".join(media),
            "OtherEngineNames": ",".join(other),
        })
    write("gm1_engine_matrix_long.csv", LONG_FIELDS, long_rows)
    write("gm1_engine_matrix_fixtures.csv", FIXTURE_FIELDS, fixture_rows)
    audit["engines"] = len(engines)
    write("gm1_engine_matrix_audit.csv", AUDIT_FIELDS,
          [{"Issue": k, "Count": v} for k, v in sorted(audit.items())])
    for k, v in sorted(audit.items()):
        print(f"[GM1-MATRIX] {k}={v}")
    if audit["outcome_conflicts"]:
        raise RuntimeError("Esiti discordanti: controllare audit e storici.")
    print("[NOTE] Nessun engine modificato. Le fasce diverse da ALTA/MEDIA "
          "non ricevono un esito di pronostico inventato. "
          "La matrice e' diagnostica, non un selettore addestrato.")


if __name__ == "__main__":
    run()
