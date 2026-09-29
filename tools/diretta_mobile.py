"""Scarica partite/risultati da m.diretta.it e genera gli input GioOver25."""
from __future__ import annotations

import argparse
import html
import re
import sys
from dataclasses import dataclass
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.prepare_input import Match, load_registry, resolve_match, unique, write_csv

BASE_URL = "https://m.diretta.it/"
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

    @property
    def borderline(self) -> bool:
        return self.time.startswith("00:")


class MobileParser(HTMLParser):
    """Estrae testo per blocchi H4, senza dipendenze esterne."""

    BREAK_TAGS = {"br", "p", "div", "li", "tr", "td"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_h4 = False
        self.h4_parts: list[str] = []
        self.current_heading: str | None = None
        self.block_parts: list[str] = []
        self.blocks: list[tuple[str, str]] = []

    def _flush_block(self):
        if self.current_heading:
            text = " ".join("".join(self.block_parts).split())
            self.blocks.append((self.current_heading, text))
        self.block_parts = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag in {"h3", "h4"}:
            self._flush_block()
            self.in_h4 = True
            self.h4_parts = []
        elif tag in self.BREAK_TAGS and not self.in_h4:
            self.block_parts.append(" ")

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "h4":
            self.in_h4 = False
            self.current_heading = " ".join("".join(self.h4_parts).split())
        elif tag in self.BREAK_TAGS and not self.in_h4:
            self.block_parts.append(" ")

    def handle_data(self, data):
        if self.in_h4:
            self.h4_parts.append(data)
        elif self.current_heading:
            self.block_parts.append(data)

    def close(self):
        super().close()
        self._flush_block()


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
    out: list[RawMatch] = []
    for heading, block in parser.blocks:
        hm = HEAD_RE.match(html.unescape(heading))
        if not hm:
            continue
        country, league = hm.group(1).strip(), hm.group(2).strip()
        # "Classifiche" e altre etichette possono precedere la prima partita.
        block = re.sub(r"^\s*(?:Classifiche(?: Live)?|Tabellone)\s*", "", html.unescape(block), flags=re.I)
        for m in MATCH_RE.finditer(block):
            out.append(
                RawMatch(
                    country=country,
                    league=league,
                    time=m.group("time"),
                    home=" ".join(m.group("home").split()),
                    away=" ".join(m.group("away").split()),
                    score=m.group("score").replace(" ", ""),
                    status=(m.group("status") or "").strip(),
                )
            )
    return out


def convert(raw: list[RawMatch], day_offset: int, mode: str, registry):
    match_date = (date.today() + timedelta(days=day_offset)).isoformat()
    converted: list[Match] = []
    unmapped: set[tuple[str, str]] = set()
    borderline: list[RawMatch] = []
    skipped_status = 0

    for r in raw:
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
    page = fetch_html(offset)
    raw = parse_mobile(page)
    if not raw:
        raise SystemExit("[ERRORE] Nessuna partita riconosciuta: formato HTML forse cambiato.")

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
