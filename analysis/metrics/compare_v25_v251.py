"""
===============================================================================
GioOver2.5 - analysis/metrics/compare_v25_v251.py
===============================================================================

SCOPO
-----
Confrontare v25 e v251 partita per partita sulla stessa intersezione di gare
concluse, misurando anche effetti molto piccoli che la sola percentuale finale
potrebbe nascondere.

REPORT PRODOTTI
---------------
1. `01_v25_v251_summary.csv`
   Statistiche complessive per fascia e motore.

2. `02_v25_v251_transitions.csv`
   Matrice dei cambi di fascia, separata per esito OK/KO.

3. `03_v25_v251_changed_matches.csv`
   Tutte le partite il cui score o fascia cambia, con le micro-correzioni.

4. `04_v251_adjustment_effects.csv`
   Frequenza, OK, KO e precisione delle singole correzioni.

5. `05_v25_v251_daily.csv`
   Confronto giornaliero della fascia ALTA.

6. `06_v25_v251_topn.csv`
   Confronto a parità di copertura sulle migliori N partite per score.

INPUT PREDEFINITI
-----------------
    data/storico/ranking/v25/storico_ranking_v25.csv
    data/storico/ranking/v251/storico_ranking_v251.csv

ESEMPIO
-------
    python -m analysis.metrics.compare_v25_v251

    python -m analysis.metrics.compare_v25_v251 --exclude-australia
===============================================================================
"""

from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


DEFAULT_V25 = Path("data/storico/ranking/v25/storico_ranking_v25.csv")
DEFAULT_V251 = Path("data/storico/ranking/v251/storico_ranking_v251.csv")
DEFAULT_OUTPUT_DIR = Path("analysis/metrics/output/v25_vs_v251")

# Espressione regolare usata per leggere il blocco scritto dalla v251 nel Reason.
DIAGNOSTICS_PATTERN = re.compile(r"V251_DIAGNOSTICS\[([^\]]+)\]")



def _text(value) -> str:
    """Restituisce una stringa pulita anche quando il valore è None."""

    return str(value or "").strip()



def _float(value, default: float = 0.0) -> float:
    """Converte valori CSV in float senza interrompere il report."""

    try:
        return float(_text(value).replace(",", "."))
    except ValueError:
        return default



def _normalize_team(value) -> str:
    """Normalizza il nome squadra usato per costruire la chiave della gara."""

    return " ".join(_text(value).casefold().split())



def _match_key(row: dict) -> tuple[str, str, str, str]:
    """Crea la chiave stabile LeagueId + MatchDate + Home + Away."""

    return (
        _text(row.get("LeagueId")),
        _text(row.get("MatchDate")),
        _normalize_team(row.get("Home")),
        _normalize_team(row.get("Away")),
    )



def _is_finished(row: dict) -> bool:
    """Considera conclusa una riga soltanto se Over25 vale OK oppure KO."""

    return _text(row.get("Over25")).upper() in {"OK", "KO"}



def _read_csv(path: Path) -> list[dict]:
    """Legge un CSV semicolon e produce una lista di dizionari."""

    if not path.exists():
        raise FileNotFoundError(f"File non trovato: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))



def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    """Scrive un report CSV creando automaticamente la cartella di output."""

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            delimiter=";",
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)



def _parse_diagnostics(reason: str) -> dict[str, float]:
    """Estrae BaseScore e singoli adjustment dal Reason della v251."""

    match = DIAGNOSTICS_PATTERN.search(_text(reason))

    defaults = {
        "BaseScore": 0.0,
        "StrongDefense": 0.0,
        "RecentForm": 0.0,
        "Restart": 0.0,
        "Total": 0.0,
    }

    if not match:
        return defaults

    result = dict(defaults)

    for item in match.group(1).split(";"):
        if "=" not in item:
            continue

        key, value = item.split("=", 1)
        key = key.strip()

        if key in result:
            result[key] = _float(value)

    return result



def _precision(ok: int, ko: int) -> float:
    """Calcola la precisione percentuale evitando divisioni per zero."""

    total = ok + ko
    return round((ok / total) * 100, 2) if total else 0.0



def _summary_rows(pairs: list[tuple[dict, dict]]) -> list[dict]:
    """Costruisce il riepilogo per motore e fascia."""

    output: list[dict] = []

    for engine_index, engine_name in ((0, "v25"), (1, "v251")):
        rows = [pair[engine_index] for pair in pairs]

        for band in ("ALTA", "MEDIA", "BASSA"):
            selected = [row for row in rows if _text(row.get("Band")) == band]
            ok = sum(_text(row.get("Over25")).upper() == "OK" for row in selected)
            ko = sum(_text(row.get("Over25")).upper() == "KO" for row in selected)

            output.append({
                "Engine": engine_name,
                "Band": band,
                "OK": ok,
                "KO": ko,
                "Total": ok + ko,
                "Precision": _precision(ok, ko),
            })

    return output



def _transition_rows(pairs: list[tuple[dict, dict]]) -> list[dict]:
    """Conta tutti i cambi di fascia separandoli per esito finale."""

    counts: Counter[tuple[str, str, str]] = Counter()

    for v25, v251 in pairs:
        key = (
            _text(v25.get("Band")),
            _text(v251.get("Band")),
            _text(v25.get("Over25")).upper(),
        )
        counts[key] += 1

    return [
        {
            "BandV25": band_v25,
            "BandV251": band_v251,
            "Result": result,
            "Matches": count,
        }
        for (band_v25, band_v251, result), count in sorted(counts.items())
    ]



def _changed_match_rows(pairs: list[tuple[dict, dict]]) -> list[dict]:
    """Elenca le partite con score diverso o cambio di fascia."""

    output: list[dict] = []

    for v25, v251 in pairs:
        score_v25 = _float(v25.get("Score"))
        score_v251 = _float(v251.get("Score"))
        diagnostics = _parse_diagnostics(v251.get("Reason", ""))

        if (
            abs(score_v25 - score_v251) < 0.0001
            and _text(v25.get("Band")) == _text(v251.get("Band"))
        ):
            continue

        output.append({
            "MatchDate": _text(v25.get("MatchDate")),
            "LeagueId": _text(v25.get("LeagueId")),
            "Home": _text(v25.get("Home")),
            "Away": _text(v25.get("Away")),
            "Over25": _text(v25.get("Over25")).upper(),
            "ScoreV25": score_v25,
            "ScoreV251": score_v251,
            "ScoreDelta": round(score_v251 - score_v25, 2),
            "BandV25": _text(v25.get("Band")),
            "BandV251": _text(v251.get("Band")),
            "StrongDefenseAdjustment": diagnostics["StrongDefense"],
            "RecentFormAdjustment": diagnostics["RecentForm"],
            "RestartAdjustment": diagnostics["Restart"],
            "TotalAdjustment": diagnostics["Total"],
            "ReasonV251": _text(v251.get("Reason")),
        })

    output.sort(key=lambda row: (row["MatchDate"], row["LeagueId"], row["Home"]))
    return output



def _adjustment_effect_rows(pairs: list[tuple[dict, dict]]) -> list[dict]:
    """Misura separatamente le partite in cui si attiva ogni correzione."""

    names = {
        "StrongDefense": "StrongDefenseAdjustment",
        "RecentForm": "RecentFormAdjustment",
        "Restart": "RestartAdjustment",
        "Total": "AnyAdjustment",
    }

    output: list[dict] = []

    for diagnostic_key, label in names.items():
        selected: list[tuple[dict, dict, float]] = []

        for v25, v251 in pairs:
            diagnostics = _parse_diagnostics(v251.get("Reason", ""))
            value = diagnostics[diagnostic_key]

            if value < 0:
                selected.append((v25, v251, value))

        ok = sum(_text(v25.get("Over25")).upper() == "OK" for v25, _, _ in selected)
        ko = sum(_text(v25.get("Over25")).upper() == "KO" for v25, _, _ in selected)
        changed_band = sum(
            _text(v25.get("Band")) != _text(v251.get("Band"))
            for v25, v251, _ in selected
        )

        output.append({
            "Adjustment": label,
            "Occurrences": len(selected),
            "OK": ok,
            "KO": ko,
            "Precision": _precision(ok, ko),
            "BandChanges": changed_band,
            "AveragePenalty": round(
                sum(value for _, _, value in selected) / len(selected),
                3,
            ) if selected else 0.0,
        })

    return output



def _daily_rows(pairs: list[tuple[dict, dict]]) -> list[dict]:
    """Confronta giorno per giorno la sola fascia ALTA."""

    grouped: dict[str, list[tuple[dict, dict]]] = defaultdict(list)

    for pair in pairs:
        grouped[_text(pair[0].get("MatchDate"))].append(pair)

    output: list[dict] = []

    for match_date in sorted(grouped):
        day_pairs = grouped[match_date]
        row = {"MatchDate": match_date}

        for index, name in ((0, "V25"), (1, "V251")):
            alta = [pair[index] for pair in day_pairs if _text(pair[index].get("Band")) == "ALTA"]
            ok = sum(_text(item.get("Over25")).upper() == "OK" for item in alta)
            ko = sum(_text(item.get("Over25")).upper() == "KO" for item in alta)

            row[f"{name}AltaOK"] = ok
            row[f"{name}AltaKO"] = ko
            row[f"{name}AltaTotal"] = ok + ko
            row[f"{name}AltaPrecision"] = _precision(ok, ko)

        row["AltaKOAvoided"] = max(0, row["V25AltaKO"] - row["V251AltaKO"])
        row["AltaOKLost"] = max(0, row["V25AltaOK"] - row["V251AltaOK"])
        row["ProtectiveBalance"] = row["AltaKOAvoided"] - row["AltaOKLost"]
        output.append(row)

    return output



def _topn_rows(pairs: list[tuple[dict, dict]]) -> list[dict]:
    """Confronta la precisione delle migliori N prediction per score."""

    output: list[dict] = []
    available = len(pairs)

    for n in (25, 50, 100, 200, 300, 500):
        if n > available:
            continue

        for index, engine_name in ((0, "v25"), (1, "v251")):
            ranked = sorted(
                (pair[index] for pair in pairs),
                key=lambda row: _float(row.get("Score")),
                reverse=True,
            )[:n]

            ok = sum(_text(row.get("Over25")).upper() == "OK" for row in ranked)
            ko = sum(_text(row.get("Over25")).upper() == "KO" for row in ranked)

            output.append({
                "TopN": n,
                "Engine": engine_name,
                "OK": ok,
                "KO": ko,
                "Precision": _precision(ok, ko),
                "MinimumScore": min(_float(row.get("Score")) for row in ranked),
            })

    return output



def main() -> None:
    """Legge gli storici, costruisce l'intersezione e scrive tutti i report."""

    parser = argparse.ArgumentParser(
        description="Confronta v25 e v251 sulla stessa intersezione di partite concluse."
    )
    parser.add_argument("--v25", type=Path, default=DEFAULT_V25)
    parser.add_argument("--v251", type=Path, default=DEFAULT_V251)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--exclude-australia", action="store_true")
    args = parser.parse_args()

    v25_rows = [row for row in _read_csv(args.v25) if _is_finished(row)]
    v251_rows = [row for row in _read_csv(args.v251) if _is_finished(row)]

    if args.exclude_australia:
        v25_rows = [
            row for row in v25_rows
            if not _text(row.get("LeagueId")).startswith("Australia_")
        ]
        v251_rows = [
            row for row in v251_rows
            if not _text(row.get("LeagueId")).startswith("Australia_")
        ]

    v25_index = {_match_key(row): row for row in v25_rows}
    v251_index = {_match_key(row): row for row in v251_rows}
    common_keys = sorted(set(v25_index).intersection(v251_index))
    pairs = [(v25_index[key], v251_index[key]) for key in common_keys]

    if not pairs:
        raise ValueError("Nessuna partita conclusa comune tra v25 e v251.")

    summary = _summary_rows(pairs)
    transitions = _transition_rows(pairs)
    changed = _changed_match_rows(pairs)
    effects = _adjustment_effect_rows(pairs)
    daily = _daily_rows(pairs)
    topn = _topn_rows(pairs)

    _write_csv(
        args.output_dir / "01_v25_v251_summary.csv",
        summary,
        ["Engine", "Band", "OK", "KO", "Total", "Precision"],
    )
    _write_csv(
        args.output_dir / "02_v25_v251_transitions.csv",
        transitions,
        ["BandV25", "BandV251", "Result", "Matches"],
    )
    _write_csv(
        args.output_dir / "03_v25_v251_changed_matches.csv",
        changed,
        [
            "MatchDate", "LeagueId", "Home", "Away", "Over25",
            "ScoreV25", "ScoreV251", "ScoreDelta", "BandV25", "BandV251",
            "StrongDefenseAdjustment", "RecentFormAdjustment",
            "RestartAdjustment", "TotalAdjustment", "ReasonV251",
        ],
    )
    _write_csv(
        args.output_dir / "04_v251_adjustment_effects.csv",
        effects,
        [
            "Adjustment", "Occurrences", "OK", "KO", "Precision",
            "BandChanges", "AveragePenalty",
        ],
    )
    _write_csv(
        args.output_dir / "05_v25_v251_daily.csv",
        daily,
        [
            "MatchDate",
            "V25AltaOK", "V25AltaKO", "V25AltaTotal", "V25AltaPrecision",
            "V251AltaOK", "V251AltaKO", "V251AltaTotal", "V251AltaPrecision",
            "AltaKOAvoided", "AltaOKLost", "ProtectiveBalance",
        ],
    )
    _write_csv(
        args.output_dir / "06_v25_v251_topn.csv",
        topn,
        ["TopN", "Engine", "OK", "KO", "Precision", "MinimumScore"],
    )

    print("Confronto v25/v251 completato.")
    print(f"Partite concluse comuni : {len(pairs)}")
    print(f"Partite con variazioni  : {len(changed)}")
    print(f"Output                  : {args.output_dir.resolve()}")


if __name__ == "__main__":
    main()
