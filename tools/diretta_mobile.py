"""Scarica partite/risultati da m.diretta.it e genera gli input GioOver25."""
from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.prepare_input import Match, load_registry, resolve_match, unique, write_csv

BASE_URL = "https://m.diretta.it/"
FEED_URL = "https://global.flashscore.ninja/323/x/feed/f_1_{day}_3_it_1"
FEED_SIGN = "SW9D1eZo"
HEAD_RE = re.compile(r"^\s*([^:]+):\s*(.+?)\s*$")
MATCH_RE = re.compile(
    r"(?P<time>\d{1,2}:\d{2})\s+"
    r"(?:(?P<status>Posticipata|Rinviata|Sospesa)\s+)?"
    r"(?P<home>.+?)\s+-\s+(?P<away>.+?)\s+"
    r"(?P<score>\d+\s*-\s*\d+|-)\s*(?=(?:\d{1,2}:\d{2})|$)",
    re.I,
)


@dataclass
class RawMatch:
    country: str
    league: str
    time: str
    home: str
    away: str
    score: str
    status: str = ""
    match_date: str = ""

    @property
    def borderline(self) -> bool:
        return self.time.startswith("00:")


class MobileParser(HTMLParser):
    """Parser del blocco #score-data di m.diretta.it."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_score_data = False
        self.depth = 0
        self.in_heading = False
        self.heading_parts = []
        self.country = ""
        self.league = ""
        self.time = ""
        self.status = ""
        self.fixture_parts = []
        self.in_score = False
        self.score_parts = []
        self.matches = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if not self.in_score_data and tag == "div" and attrs.get("id") == "score-data":
            self.in_score_data = True
            self.depth = 1
            return
        if not self.in_score_data:
            return
        if tag == "div":
            self.depth += 1
        if tag == "h4":
            self.in_heading = True
            self.heading_parts = []
            self.fixture_parts = []
        elif tag == "a" and "fin" in attrs.get("class", "").split():
            self.in_score = True
            self.score_parts = []

    def handle_endtag(self, tag):
        if not self.in_score_data:
            return
        if tag == "h4":
            self.in_heading = False
            heading = " ".join("".join(self.heading_parts).split())
            heading = re.sub(r"\\s*Classifiche\\s*$", "", heading, flags=re.I)
            hm = HEAD_RE.match(heading)
            if hm:
                self.country, self.league = hm.group(1).strip(), hm.group(2).strip()
        elif tag == "a" and self.in_score:
            self.in_score = False
            score = " ".join("".join(self.score_parts).replace("\\xa0", " ").split())
            fixture = " ".join("".join(self.fixture_parts).split())
            if " - " in fixture and self.country and self.league:
                home, away = fixture.split(" - ", 1)
                self.matches.append(RawMatch(self.country, self.league, self.time, home.strip(), away.strip(), score, self.status))
            self.fixture_parts = []
            self.status = ""
        elif tag == "br":
            self.fixture_parts = []
            self.time = ""
            self.status = ""
        elif tag == "div":
            self.depth -= 1
            if self.depth <= 0:
                self.in_score_data = False

    def handle_data(self, data):
        if not self.in_score_data:
            return
        if self.in_heading:
            self.heading_parts.append(data)
            return
        if self.in_score:
            self.score_parts.append(data)
            return
        value = " ".join(data.split())
        if not value:
            return
        if re.fullmatch(r"\\d{1,2}:\\d{2}", value):
            self.time = value
        elif value in {"Rinviata", "Posticipata", "Sospesa"}:
            self.status = value
        else:
            self.fixture_parts.append(" " + value)


def fetch_feed(day_offset: int, timeout: int = 20) -> str:
    req = Request(FEED_URL.format(day=day_offset), headers={
        "User-Agent": "Mozilla/5.0", "Accept": "*/*",
        "Accept-Language": "it-IT,it;q=0.9",
        "Referer": "https://www.diretta.it/", "Origin": "https://www.diretta.it",
        "x-fsign": FEED_SIGN,
    })
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_feed(payload: str) -> list[RawMatch]:
    out, country, league = [], "", ""
    for record in payload.split("~"):
        fields = {}
        for item in record.split("¬"):
            if "÷" in item:
                k, v = item.split("÷", 1)
                fields[k] = v
        if "ZA" in fields:
            hm = HEAD_RE.match(fields["ZA"].strip())
            country, league = (hm.group(1).strip(), hm.group(2).strip()) if hm else ("", fields["ZA"].strip())
            continue
        if not all(k in fields for k in ("AA", "AE", "AF")):
            continue
        try:
            dt = datetime.fromtimestamp(int(fields.get("AD", ""))).astimezone()
            tm = dt.strftime("%H:%M")
            match_date = dt.date().isoformat()
        except (ValueError, TypeError, OSError):
            tm = ""
            match_date = ""
        hg, ag = fields.get("AG", ""), fields.get("AH", "")
        score = f"{hg}-{ag}" if hg.isdigit() and ag.isdigit() else "-"
        ab = fields.get("AB", "")
        # Lo stato amministrativo non è sempre confinato in AM e il testo può
        # arrivare localizzato. Cerca quindi gli indicatori di rinvio in tutti
        # i campi del record, mantenendo il vincolo score == "-" per non
        # confondere una partita conclusa con un rinvio.
        status_text = " ".join(str(value) for value in fields.values()).casefold()
        postponed_tokens = (
            "si disputer", "posticip", "rinvi", "sospes", "annull",
            "postpon", "cancel", "suspend",
            "verleg", "verschob", "abgesag", "abgesetz",
            "aplaz", "suspendid",
        )
        if score == "-" and any(token in status_text for token in postponed_tokens):
            status = "Posticipata"
        else:
            status = "" if ab in {"", "1", "3"} else ab
        out.append(RawMatch(country, league, tm, fields["AE"], fields["AF"], score, status, match_date))
    return out


def fetch_html(day_offset: int, timeout: int = 20) -> str:
    url = BASE_URL if day_offset == 0 else f"{BASE_URL}?d={day_offset}"
    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (GioOver25 DirettaMobileService)",
            "Accept-Language": "it-IT,it;q=0.9",
        },
    )
    with urlopen(req, timeout=timeout) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        return response.read().decode(charset, errors="replace")


def parse_mobile(page: str) -> list[RawMatch]:
    parser = MobileParser()
    parser.feed(page)
    parser.close()
    return parser.matches


def convert(raw: list[RawMatch], day_offset: int, mode: str, registry):
    match_date = (date.today() + timedelta(days=day_offset)).isoformat()
    converted: list[Match] = []
    unmapped: set[tuple[str, str]] = set()
    borderline: list[RawMatch] = []
    skipped_status = 0

    for r in raw:
        # Il feed giornaliero può includere eventi adiacenti: usa sempre la data reale AD.
        if r.match_date and r.match_date != match_date:
            continue
        if r.borderline:
            borderline.append(r)
        league_id = resolve_match(registry, r.country, r.league, r.home, r.away)
        if not league_id:
            unmapped.add((r.country, r.league))
            continue

        if mode == "rank":
            if r.status:
                skipped_status += 1
                continue
            converted.append(Match(league_id, match_date, r.home, r.away))
            continue

        # results: solo risultati con punteggio; rinviate/posticipate non entrano.
        sm = re.fullmatch(r"(\d+)-(\d+)", r.score)
        if not sm or r.status:
            skipped_status += 1
            continue
        converted.append(
            Match(
                league_id=league_id,
                date=match_date,
                home=r.home,
                away=r.away,
                hg=sm.group(1),
                ag=sm.group(2),
                status="Finale",
                notes="",
                round="",
            )
        )

    return unique(converted), unmapped, borderline, skipped_status


def default_output(mode: str) -> Path:
    if mode == "results":
        return ROOT / "data" / "input_risultati" / "risultati.csv"
    return ROOT / "data" / "input_partite" / "partite.csv"


def main():
    p = argparse.ArgumentParser(
        description="Scarica m.diretta.it e genera partite.csv o risultati.csv."
    )
    day = p.add_mutually_exclusive_group(required=True)
    day.add_argument("--yesterday", action="store_true")
    day.add_argument("--today", action="store_true")
    day.add_argument("--tomorrow", action="store_true")
    p.add_argument("--output", type=Path)
    p.add_argument("--registry", type=Path, default=ROOT / "data" / "league_registry.csv")
    p.add_argument("--dry-run", action="store_true", help="Analizza senza scrivere il CSV.")
    args = p.parse_args()

    offset = -1 if args.yesterday else (1 if args.tomorrow else 0)
    mode = "results" if offset == -1 else "rank"
    target_date = date.today() + timedelta(days=offset)
    url = BASE_URL if offset == 0 else f"{BASE_URL}?d={offset}"

    print(f"[DIRETTA] Download {url} -> {target_date.isoformat()} ({mode})")
    try:
        page = fetch_feed(offset)
        raw = parse_feed(page)
        print(f"[DIRETTA] Sorgente feed completo: {len(raw)} partite")
    except Exception as exc:
        print(f"[WARN] Feed non disponibile ({exc}); fallback pagina mobile.")
        page = fetch_html(offset)
        raw = parse_mobile(page)
    if not raw:
        debug_dir = ROOT / "data" / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        debug_file = debug_dir / f"diretta_mobile_{target_date.isoformat()}.html"
        debug_file.write_text(page, encoding="utf-8")
        print(f"[DEBUG] HTML ricevuto salvato in {debug_file}")
        print(f"[DEBUG] Dimensione risposta: {len(page)} caratteri")
        print(f"[DEBUG] Prime 300 battute: {page[:300]!r}")
        raise SystemExit("[ERRORE] Nessuna partita riconosciuta. Invia il file DEBUG per correggere il parser.")

    registry = load_registry(args.registry)
    matches, unmapped, borderline, skipped = convert(raw, offset, mode, registry)
    output = args.output or default_output(mode)

    print(f"[DIRETTA] Partite lette: {len(raw)}")
    print(f"[DIRETTA] Partite nel league_registry: {len(matches)}")
    print(f"[DIRETTA] Competizioni non mappate/escluse: {len(unmapped)}")
    if skipped:
        print(f"[DIRETTA] Partite senza risultato valido/rinviate: {skipped}")

    if borderline:
        print(f"[WARN] Partite borderline 00:xx: {len(borderline)}")
        for r in borderline:
            lid = resolve_match(registry, r.country, r.league, r.home, r.away)
            marker = lid or "FUORI REGISTRY"
            print(f"  - {r.time} {r.country}: {r.league} | {r.home} - {r.away} [{marker}]")

    if unmapped:
        print("[INFO] Competizioni Diretta non presenti/riconosciute nel registry:")
        for country, league in sorted(unmapped):
            print(f"  - {country}: {league}")

    if args.dry_run:
        print(f"[DRY-RUN] CSV non scritto. Sarebbero state prodotte {len(matches)} righe.")
        return

    write_csv(output, mode, matches)
    print(f"[OK] {len(matches)} righe scritte in {output}")


if __name__ == "__main__":
    main()
