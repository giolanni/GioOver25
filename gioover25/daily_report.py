"""Daily shareable PDF report generated after rank_matches_v2 --engine all."""
from __future__ import annotations

import csv
import re
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


_REPORT_FILE_RE = re.compile(
    r"^GioOver_(\\d{4}-\\d{2}-\\d{2})(?:_(\\d{4}-\\d{2}-\\d{2}))?\\.pdf$",
    re.IGNORECASE,
)


def _cleanup_old_reports(reference_date: date) -> list[Path]:
    """Delete GioOver PDFs whose filename date is older than seven days."""
    if not OUTPUT_DIR.exists():
        return []
    cutoff = reference_date - timedelta(days=7)
    removed = []
    for path in OUTPUT_DIR.glob("*.pdf"):
        match = _REPORT_FILE_RE.match(path.name)
        if not match:
            continue
        file_date = _parse_date(match.group(2) or match.group(1))
        if file_date is not None and file_date < cutoff:
            path.unlink()
            removed.append(path)
    return removed


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
                               fontSize=10, leading=14, textColor=INK, spaceAfter=1*mm),
        "meta_stats": ParagraphStyle("meta_stats", parent=base["Normal"], fontName="Helvetica-Bold",
                                      fontSize=9.5, leading=13, textColor=INK),
        "cell": ParagraphStyle("cell", parent=base["Normal"], fontName="Helvetica",
                               fontSize=7.5, leading=9, textColor=INK),
        "cell_bold": ParagraphStyle("cell_bold", parent=base["Normal"], fontName="Helvetica-Bold",
                                    fontSize=7.5, leading=9, textColor=INK),
        "empty": ParagraphStyle("empty", parent=base["Normal"], fontName="Helvetica-Oblique",
                                fontSize=9.5, leading=13, textColor=INK),
        "legend": ParagraphStyle("legend", parent=base["Normal"], fontName="Helvetica",
                                 fontSize=9.5, leading=13, textColor=INK),
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


def _performance(engine: str, report_date: date, *, market="Over25", min_score=None, selected_only=False) -> str:
    rows = _history(engine)
    def calc(start=None):
        ok = ko = 0
        for row in rows:
            d = _parse_date(row.get("MatchDate"))
            if d is None or d >= report_date or (start is not None and d < start):
                continue
            if min_score is not None and _num(row.get("Score")) <= min_score:
                continue
            if selected_only and str(row.get("Band", "") or "").strip().upper() != "ALTA":
                continue
            outcome = str(row.get(market, "") or "").strip().upper()
            if outcome == "OK": ok += 1
            elif outcome == "KO": ko += 1
        total = ok + ko
        return ok, total, (ok / total * 100.0 if total else 0.0)
    w = calc(report_date - timedelta(days=7))
    a = calc()
    weekly = f"7 gg: {w[0]}/{w[1]} ({w[2]:.1f}%)" if w[1] else "7 gg: n.d."
    overall = f"storico: {a[0]}/{a[1]} ({a[2]:.1f}%)" if a[1] else "storico: n.d."
    return f"{weekly} | {overall}"


def _gs1_performance(report_date: date) -> str:
    rows = _read_csv(Path("data/storico/gs1_over/storico_gs1_over.csv"))
    def calc(start=None):
        ok = total = 0
        for row in rows:
            d = _parse_date(row.get("MatchDate"))
            if d is None or d >= report_date or (start is not None and d < start):
                continue
            outcome = str(row.get("Outcome", "") or "").strip().upper()
            if outcome in {"OK", "KO"}:
                total += 1
                if outcome == "OK": ok += 1
        return ok, total, (ok / total * 100.0 if total else 0.0)
    w = calc(report_date - timedelta(days=7))
    a = calc()
    weekly = f"7 gg: {w[0]}/{w[1]} ({w[2]:.1f}%)" if w[1] else "7 gg: n.d."
    overall = f"storico: {a[0]}/{a[1]} ({a[2]:.1f}%)" if a[1] else "storico: n.d."
    if not w[1] and not a[1]:
        return ""
    return f"{weekly} | {overall}"


def _description(text: str, stats: str, styles):
    # Nessun markup inline: evita che tag ReportLab possano comparire nel PDF.
    rows = [[_p(text, styles["meta"])]]
    if stats:
        rows.append([_p(f"Rendimento: {stats}", styles["meta_stats"])]
    box = Table(rows, colWidths=[185*mm])
    box.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2*mm),
    ]))
    return box


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
                          gs1_near_rows: list[dict] | None = None,
                          report_date: date | None = None) -> Path:
    # The PDF identifies the fixtures it actually contains, not its creation day.
    # Multiple MatchDates are represented by an inclusive date range.
    match_dates = set()
    for engine_rows in results_by_engine.values():
        for row in engine_rows:
            parsed = _parse_date(row.get("MatchDate"))
            if parsed is not None:
                match_dates.add(parsed)
    for row in list(gs1_rows) + list(gs1_near_rows or []):
        parsed = _parse_date(row.get("MatchDate"))
        if parsed is not None:
            match_dates.add(parsed)
    if not match_dates:
        raise ValueError("PDF pronostici: nessuna MatchDate valida negli output")
    first_day, last_day = min(match_dates), max(match_dates)
    report_date = last_day  # Historical statistics must not use a later generation date.
    date_label = (first_day.isoformat() if first_day == last_day
                  else f"{first_day.isoformat()}_{last_day.isoformat()}")
    display_date = (first_day.strftime("%d/%m/%Y") if first_day == last_day
                    else f"{first_day.strftime('%d/%m/%Y')} - {last_day.strftime('%d/%m/%Y')}")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    _cleanup_old_reports(report_date)
    output = OUTPUT_DIR / f"GioOver_{date_label}.pdf"
    styles = _styles()

    cautious_ranked = _rank_engines(V20_FAMILY, report_date)
    if cautious_ranked:
        cautious_best = cautious_ranked[0]
    else:
        cautious_best = _best_engine(V20_FAMILY, report_date, fallback="v20plus")

    def has_high_today(engine_name: str) -> bool:
        for row in results_by_engine.get(engine_name, []):
            band = str(row.get("Band", "") or "").strip().upper()
            if band == "ALTA" or band.startswith("IMM-ALTA-"):
                return True
        return False

    cautious = cautious_best
    for candidate in cautious_ranked:
        if has_high_today(candidate["engine"]):
            cautious = candidate
            break
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
        title=f"GioOver - Pronostici {date_label}",
        author="GioOver",
    )
    story = [
        _p("GioOver - Pronostici giornalieri", styles["title"]),
        _p(display_date, styles["subtitle"]),
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
    if cautious["engine"] != cautious_best["engine"]:
        cautious_text = (
            f"Il migliore della settimana e' {cautious_best['engine']}, ma oggi non produce "
            f"selezioni ALTA. Per la selezione odierna usiamo quindi {cautious['engine']}, "
            "primo engine successivo della famiglia V20 con almeno una ALTA."
        )
    elif has_high_today(cautious["engine"]):
        cautious_text = (
            f"Selezione prudente della famiglia V20. {cautious['engine']} e' il migliore "
            "della settimana e oggi produce almeno una selezione ALTA."
        )
    else:
        cautious_text = (
            f"Il migliore della settimana e' {cautious_best['engine']}. Nessun engine della "
            "famiglia V20 disponibile oggi produce selezioni ALTA; viene mantenuto il migliore "
            "settimanale come riferimento."
        )
    section("ALGORITMO CAUTO", _table(c_rows, styles),
            _description(cautious_text,
                         _performance(cautious["engine"], report_date, min_score=70), styles))

    p_rows = _over_rows(results_by_engine.get(permissive["engine"], []))
    section("ALGORITMO PERMISSIVO", _table(p_rows, styles),
            _description(f"Selezione piu' ampia fuori dalla famiglia V20. Oggi usa {permissive['engine']}, scelto sul rendimento recente tra gli engine ammessi.",
                         _performance(permissive["engine"], report_date, min_score=70), styles))
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
            _description(f"{permissive_second['engine']} affianca V31 per aumentare il numero di opportunita'; sono escluse le partite gia' indicate da V31.",
                         _performance(permissive_second["engine"], report_date, min_score=70), styles),
        )

    goal_rows = _vg1_rows(results_by_engine.get("vg1", []))
    section("GOL - VG1", _table(goal_rows, styles, vg1=True),
            _description("Engine dedicato al mercato GOL/BTTS. Nel report compaiono score >65: giallo 65-67.9, arancio 68-71.9, verde >=72.",
                         _performance("vg1", report_date, market="BTTS", min_score=65), styles))

    special_descriptions = {
        "v27": (
            "Over 2.5 molto selettivo: richiede forte attacco della squadra di casa "
            "(HomeAttack >=12.428) e almeno 2.20 gol subiti di media dall'ospite nelle ultime 5."
        ),
        "v30": (
            "Over 2.5 specializzato negli storici giovani: lavora con maturita' 7-8 gare, "
            "forte tendenza Over recente e crescita dei gol fatti rispetto allo storico."
        ),
        "vg2.2": (
            "Filtro GOL selettivo derivato da VG1: mantiene segnali VG1 ALTA con "
            "MinGF nelle ultime 5 superiore a 2.2."
        ),
        "vg2.6": (
            "Filtro GOL ancora piu' restrittivo: segnale VG1 ALTA e MinGF nelle "
            "ultime 5 superiore a 2.6. E' pensato per produrre poche selezioni molto mirate."
        ),
    }
    for engine in SPECIAL_ENGINES:
        rows = results_by_engine.get(engine, [])
        market = "BTTS" if engine.startswith("vg") else "Over25"
        meta = _description(
            special_descriptions[engine],
            _performance(engine, report_date, market=market, selected_only=engine in {"vg2.2", "vg2.6"}),
            styles,
        )
        section(engine.upper(), _table(rows, styles, show_score=True), meta)

    section(
        "GS1 - OVER 2.5",
        _table(gs1_rows, styles, gs1=True),
        _description(
            "GS1 e' un selettore Over 2.5 indipendente dagli engine di ranking, progettato per "
            "mettere a disposizione un gruppo ristretto di partite affidabili con cui costruire, "
            "quando il programma giornaliero lo consente, una schedina da 3 Over 2.5. Combina la "
            "frequenza Over storica minima delle due squadre con il peggioramento recente dei gol "
            "subiti (DeltaGA). Le ALTA costituiscono il nucleo piu' forte; MEDIA e Near ampliano "
            "il bacino quando servono alternative per completare il ticket.",
            _gs1_performance(report_date),
            styles,
        ),
    )
    section(
        "GS1 OVER - NEAR",
        _table(gs1_near_rows or [], styles, gs1=True),
        _p(
            "Zona di osservazione vicina alle soglie GS1: MinOverFull >=0.70 e DeltaGA >=0.22. "
            "Non e' una selezione ufficiale GS1: e' il bacino di supporto per individuare possibili "
            "alternative quando ALTA e MEDIA non bastano a costruire il ticket da 3 partite.",
            styles["meta"],
        ),
    )

    story += [
        Spacer(1, 3*mm),
        _p("LEGENDA", styles["section"]),
        _p("ALTA = confidenza elevata. MEDIA-ALTA = fascia MEDIA con score >70. "
           "IMM = almeno una squadra ha meno di 5 partite pregresse; il numero finale e' il totale "
           "delle gare pregresse delle due squadre. GOL = entrambe le squadre segnano. "
           "OVER 2.5 = almeno 3 gol complessivi.", styles["legend"]),
    ]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(MUTED)
        canvas.drawString(10*mm, 6*mm, f"GioOver | {display_date}")
        canvas.drawRightString(A4[0]-10*mm, 6*mm, f"Pagina {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"[REPORT] PDF giornaliero generato: {output}")
    return output
