"""Gestione del ciclo di vita dei PDF GioOver.

Root: pronostici di oggi/futuri e risultati di ieri.
OLD: report datati da due a sette giorni fa.
Oltre sette giorni: eliminazione.
"""
from __future__ import annotations

import re
from datetime import date, timedelta
from pathlib import Path

OUTPUT_DIR = Path("data/output_report")
PDF_DATE = re.compile(
    r"^GioOver_(?:Risultati_)?(\\d{4}-\\d{2}-\\d{2})(?:_(\\d{4}-\\d{2}-\\d{2}))?\\.pdf$",
    re.IGNORECASE,
)


def organize_reports(today: date | None = None, root: Path = OUTPUT_DIR) -> dict[str, int]:
    today = today or date.today()
    old = root / "OLD"
    old.mkdir(parents=True, exist_ok=True)
    cutoff = today - timedelta(days=7)
    previous = today - timedelta(days=1)
    counts = {"spostati": 0, "ripristinati": 0, "eliminati": 0}
    for folder in (root, old):
        for path in list(folder.glob("*.pdf")):
            match = PDF_DATE.fullmatch(path.name)
            if not match:
                continue  # Non toccare documenti non riconosciuti.
            try:
                report_day = date.fromisoformat(match.group(2) or match.group(1))
            except ValueError:
                continue
            if report_day < cutoff:
                path.unlink()
                counts["eliminati"] += 1
                continue
            is_results = path.name.lower().startswith("gioover_risultati_")
            keep_root = report_day >= today or (is_results and report_day == previous)
            target_folder = root if keep_root else old
            if path.parent != target_folder:
                target = target_folder / path.name
                path.replace(target)
                counts["ripristinati" if keep_root else "spostati"] += 1
    return counts
