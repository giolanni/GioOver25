"""Daily shareable PDF report generated after rank_matches_v2 --engine all."""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

from .engines.factory import get_available_engines

OUTPUT_DIR = Path("data/output_report")
HISTORY_DIR = Path("data/storico/ranking")
MIN_WEEK_SAMPLE = 5

V20_FAMILY = [
    "v20plus", "v20defplus_v3", "v20defplus_v2", "v20defplus",
    "v20", "v20def", "v20select", "v20defselect",
]
PERMISSIVE_EXCLUDED = {"v27", "v30", "veg90"}
SPECIAL_ENGINES = ("v27", "v30", "vg2.2", "vg2.6")

INK = colors.HexColor("#182230")
MUTED = colors.HexColor("#667085")
LINE = colors.HexColor("#D0D5DD")
LIGHT = colors.HexColor("#F8FAFC")
BLUE = colors.HexColor("#175CD3")
GREEN = colors.HexColor("#067647")
AMBER = colors.HexColor("#B54708")
RED = colors.HexColor("#B42318")
VG_LOW = colors.HexColor("#FFF3CD")
VG_MID = colors.HexColor("#FFE0B2")
VG_HIGH = colors.HexColor("#D1FADF")


def _read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open("r", newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh, delimiter=";"))


def _history(engine: str) -> list[dict]:
    return _read_csv(HISTORY_DIR / engine / f"storico_ranking_{engine}.csv")


def _parse_date(value) -> date | None:
    try:
        return date.fromisoformat(str(value or "").strip())
    except ValueError:
        return None


def _weekly_stats(engine: str, report_date: date) -> dict:
    start = report_date - timedelta(days=7)
    ok = ko = 0
    for row in _history(engine):
        d = _parse_date(row.get("MatchDate"))
        if d is None or not (start <= d < report_date):
            continue
        # Confrontiamo gli engine sulla stessa popolazione che puo'
        # comparire nel report: pronostici Over con score > 70.
        if _num(row.get("Score")) <= 70:
            continue
        outcome = str(row.get("Over25", "") or "").strip().upper()
        if outcome == "OK":
            ok += 1
        elif outcome == "KO":
            ko += 1
    total = ok + ko
    return {
        "engine": engine, "ok": ok, "ko": ko, "total": total,
        "pct": (ok / total * 100.0) if total else 0.0,
    }


def _rank_engines(candidates: list[str], report_date: date) -> list[dict]:
    available = [e for e in candidates if e in get_available_engines()]
    stats = [_weekly_stats(e, report_date) for e in available]
    eligible = [s for s in stats if s["total"] >= MIN_WEEK_SAMPLE]
    pool = eligible if eligible else stats
    return sorted(
        pool,
        key=lambda s: (s["pct"], s["total"], s["ok"]),
        reverse=True,
    )


def _best_engine(candidates: list[str], report_date: date, fallback: str | None = None) -> dict:
    ranked = _rank_engines(candidates, report_date)
    if ranked:
        return ranked[0]
    available = [e for e in candidates if e in get_available_engines()]
    if fallback and fallback in available:
        return _weekly_stats(fallback, report_date)
    return {"engine": "", "ok": 0, "ko": 0, "total": 0, "pct": 0.0}


def _permissive_candidates() -> list[str]:
    result = []
    for engine in get_available_engines():
        low = engine.lower()
        if low.startswith("v20") or low.startswith("vg") or low.startswith("veg"):
            continue
        if low in PERMISSIVE_EXCLUDED:
            continue
        result.append(engine)
    return result


def _num(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _match(row: dict) -> str:
    return f"{row.get('Home','')} - {row.get('Away','')}"


def _display_band(row: dict) -> str:
    band = str(row.get("Band", "") or "")
    score = _num(row.get("Score"))
    if band == "MEDIA" and score > 70:
        return "MEDIA-ALTA"
    if band.startswith("IMM-MEDIA-") and score > 70:
        return band.replace("IMM-MEDIA-", "IMM-MEDIA-ALTA-", 1)
    return band


def _over_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if _num(r.get("Score")) > 70]


def _vg1_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if _num(r.get("Score")) > 65]


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontName="Helvetica-Bold",
                                fontSize=20, leading=23, textColor=INK, alignment=TA_CENTER, spaceAfter=3*mm),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontName="Helvetica",
                                   fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER),
        "section": ParagraphStyle("section", parent=base["Heading2"], fontName="Helvetica-Bold",
                                  fontSize=14, leading=17, textColor=INK, spaceBefore=4*mm, spaceAfter=2*mm),
        "meta": ParagraphStyle("meta", parent=base["Normal"], fontName="Helvetica",
                               fontSize=8.5, leading=11, textColor=MUTED),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontName="Helvetica",
                               fontSize=7.5, leading=9, textColor=INK),
        "cell_bold": ParagraphStyle("cell_bold", parent=base["Normal"], fontName="Helvetica-Bold",
                                    fontSize=7.5, leading=9, textColor=INK),
        "empty": ParagraphStyle("empty", parent=base["Normal"], fontName="Helvetica-Oblique",
                                fontSize=8.5, leading=11, textColor=MUTED),
        "legend": ParagraphStyle("legend", parent=base["Normal"], fontName="Helvetica",
                                 fontSize=7.5, leading=10, textColor=MUTED),
    }


def _p(text, style):
    safe = str(text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return Paragraph(safe, style)


def _table(rows: list[dict], styles, *, show_score=True, gs1=False, vg1=False):
    if not rows:
        return _p("Nessuna selezione per oggi.", styles["empty"])

    if gs1:
        headers = ["Lega", "Partita", "Fascia", "MinOver", "DeltaGA"]
        data = [[
            _p(r.get("LeagueId"), styles["cell"]),
            _p(_match(r), styles["cell_bold"]),
            _p(r.get("Band"), styles["cell_bold"]),
            f"{_num(r.get('MinOverRateFull')):.2f}",
            f"{_num(r.get('DeltaGA')):+.2f}",
        ] for r in rows]
        widths = [35*mm, 78*mm, 20*mm, 21*mm, 21*mm]
    elif show_score:
        headers = ["Lega", "Partita", "Score", "Fascia"]
        data = [[
            _p(r.get("LeagueId"), styles["cell"]),
            _p(_match(r), styles["cell_bold"]),
            f"{_num(r.get('Score')):.1f}",
            _p(_display_band(r), styles["cell_bold"]),
        ] for r in rows]
        widths = [39*mm, 91*mm, 18*mm, 27*mm]
    else:
        headers = ["Lega", "Partita", "Fascia"]
        data = [[
            _p(r.get("LeagueId"), styles["cell"]),
            _p(_match(r), styles["cell_bold"]),
            _p(_display_band(r), styles["cell_bold"]),
        ] for r in rows]
        widths = [43*mm, 105*mm, 27*mm]

    table = Table([headers] + data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    commands = [
        ("BACKGROUND", (0,0), (-1,0), INK),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,0), 7.5),
        ("ALIGN", (2,1), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("GRID", (0,0), (-1,-1), 0.35, LINE),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 4),
        ("RIGHTPADDING", (0,0), (-1,-1), 4),
    ]
    if vg1:
        for idx, row in enumerate(rows, start=1):
            score = _num(row.get("Score"))
            bg = VG_LOW if score < 68 else VG_MID if score < 72 else VG_HIGH
            commands.append(("BACKGROUND", (0,idx), (-1,idx), bg))
    table.setStyle(TableStyle(commands))
    return table


def _engine_meta(stats: dict, styles, label: str):
    if not stats.get("engine"):
        return _p(f"{label}: nessun engine disponibile.", styles["meta"])
    if stats["total"]:
        text = (f"{label}: {stats['engine']} - ultimi 7 giorni: "
                f"{stats['ok']} OK / {stats['ko']} KO ({stats['pct']:.1f}%, n={stats['total']})")
    else:
        text = f"{label}: {stats['engine']} - nessun esito concluso negli ultimi 7 giorni"
    return _p(text, styles["meta"])


def generate_daily_report(*, results_by_engine: dict[str, list[dict]], gs1_rows: list[dict],
                          report_date: date | None = None) -> Path:
    report_date = report_date or date.today()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = OUTPUT_DIR / f"GioOver_{report_date.isoformat()}.pdf"
    styles = _styles()

    cautious = _best_engine(V20_FAMILY, report_date, fallback="v20plus")
    permissive_ranked = _rank_engines(_permissive_candidates(), report_date)
    permissive = (
        permissive_ranked[0]
        if permissive_ranked
        else {"engine": "", "ok": 0, "ko": 0, "total": 0, "pct": 0.0}
    )
    permissive_second = (
        permissive_ranked[1]
        if permissive.get("engine") == "v31" and len(permissive_ranked) > 1
        else None
    )

    doc = SimpleDocTemplate(
        str(output), pagesize=A4, rightMargin=10*mm, leftMargin=10*mm,
        topMargin=10*mm, bottomMargin=11*mm,
        title=f"GioOver - Pronostici {report_date.isoformat()}",
        author="GioOver",
    )
    story = [
        _p("GioOver - Pronostici giornalieri", styles["title"]),
        _p(report_date.strftime("%d/%m/%Y"), styles["subtitle"]),
        Spacer(1, 4*mm),
    ]

    def section(title, body, meta=None):
        block = [_p(title, styles["section"])]
        if meta is not None:
            block += [meta, Spacer(1, 1.5*mm)]
        block += [body, Spacer(1, 2*mm)]
        story.append(KeepTogether(block[:2]) if len(block) >= 2 else block[0])
        story.extend(block[2:] if len(block) >= 2 else [])

    c_rows = _over_rows(results_by_engine.get(cautious["engine"], []))
    section("ALGORITMO CAUTO", _table(c_rows, styles),
            _engine_meta(cautious, styles, "Selezionato"))

    p_rows = _over_rows(results_by_engine.get(permissive["engine"], []))
    section("ALGORITMO PERMISSIVO", _table(p_rows, styles),
            _engine_meta(permissive, styles, "Selezionato"))
    if permissive_second is not None:
        second_rows = _over_rows(
            results_by_engine.get(permissive_second["engine"], [])
        )
        first_keys = {
            (r.get("LeagueId"), r.get("MatchDate"), r.get("Home"), r.get("Away"))
            for r in p_rows
        }
        second_rows = [
            r for r in second_rows
            if (r.get("LeagueId"), r.get("MatchDate"), r.get("Home"), r.get("Away"))
            not in first_keys
        ]
        section(
            "PERMISSIVO - SECONDA SCELTA",
            _table(second_rows, styles),
            _engine_meta(
                permissive_second,
                styles,
                "Supporto a V31 per ampliare le selezioni",
            ),
        )

    goal_rows = _vg1_rows(results_by_engine.get("vg1", []))
    section("GOL - VG1", _table(goal_rows, styles, vg1=True),
            _p("Score >65 | giallo 65-67.9 | arancio 68-71.9 | verde >=72", styles["meta"]))

    for engine in SPECIAL_ENGINES:
        rows = results_by_engine.get(engine, [])
        if engine in {"v27", "v30"}:
            section(engine.upper(), _table(rows, styles, show_score=False),
                    _p("Tutte le selezioni prodotte dall'algoritmo.", styles["meta"]))
        else:
            section(engine.upper(), _table(rows, styles),
                    _p("Sezione GOAL dedicata.", styles["meta"]))

    section("GS1 - OVER 2.5", _table(gs1_rows, styles, gs1=True),
            _p("Selezione indipendente: ALTA e MEDIA.", styles["meta"]))

    story += [
        Spacer(1, 3*mm),
        _p("<b>Legenda.</b> ALTA = confidenza elevata. MEDIA-ALTA = fascia MEDIA con score >70. "
           "IMM = almeno una squadra ha meno di 5 partite pregresse; il numero finale e' il totale "
           "delle gare pregresse delle due squadre. GOL = entrambe le squadre segnano. "
           "OVER 2.5 = almeno 3 gol complessivi.", styles["legend"]),
    ]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(10*mm, 6*mm, f"GioOver | {report_date.strftime('%d/%m/%Y')}")
        canvas.drawRightString(A4[0]-10*mm, 6*mm, f"Pagina {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"[REPORT] PDF giornaliero generato: {output}")
    return output
