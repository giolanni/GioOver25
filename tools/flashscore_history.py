"""Provider read-only per risultati Flashscore incorporati nelle pagine lega."""
from __future__ import annotations
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.request import Request, urlopen

@dataclass(frozen=True)
class FlashscoreMatch:
    match_id: str
    date: str
    home: str
    away: str
    hg: int
    ag: int
    round: str = ""

def fetch_page(url: str, timeout: int = 20) -> str:
    req = Request(url, headers={"User-Agent":"Mozilla/5.0 (GioOver25 FlashscoreHistory)","Accept":"text/html,application/xhtml+xml","Accept-Language":"en-US,en;q=0.9"})
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode(response.headers.get_content_charset() or "utf-8", errors="replace")

def extract_ids(html: str) -> dict[str, str]:
    patterns = {
        "template_id": r'tournamentTemplateId:\s*["\x27]([A-Za-z0-9]+)',
        "tournament_id": r'tournamentId:\s*["\x27]([A-Za-z0-9]+)',
        "stage_id": r'tournamentStageId:\s*["\x27]([A-Za-z0-9]+)',
        "data_service": r'dataServiceBaseUrl:\s*["\x27]([^"\x27]+)',
    }
    out = {}
    for key, pattern in patterns.items():
        m = re.search(pattern, html, re.I)
        out[key] = m.group(1) if m else ""
    return out

def extract_initial_feed(html: str, name: str = "results") -> str:
    tick = chr(96)
    pattern = r'initialFeeds\s*\[\s*["\x27]' + re.escape(name) + r'["\x27]\s*\].*?data\s*:\s*' + tick + r'(.*?)' + tick
    m = re.search(pattern, html, re.S)
    return m.group(1) if m else ""

def _records(payload: str):
    for raw in (payload or "").split("~"):
        row = {}
        for item in raw.split("¬"):
            if "÷" in item:
                k, v = item.split("÷", 1)
                row[k] = v
        if row:
            yield row

def parse_results(payload: str) -> list[FlashscoreMatch]:
    out = []
    current_round = ""
    for row in _records(payload):
        label = row.get("ER") or ""
        m = re.search(r"(?:Round|Giornata)\s*(\d+)", label, re.I)
        if m:
            current_round = m.group(1)
        if not all(row.get(k) for k in ("AA","AD","AE","AF")):
            continue
        hg, ag = row.get("AG",""), row.get("AH","")
        if not (hg.isdigit() and ag.isdigit()):
            continue
        try:
            day = datetime.fromtimestamp(int(row["AD"])).astimezone().date().isoformat()
        except (ValueError, TypeError, OSError):
            continue
        out.append(FlashscoreMatch(row["AA"], day, row["AE"].strip(), row["AF"].strip(), int(hg), int(ag), current_round))
    unique = {}
    for match in out:
        unique[(match.date, match.home.casefold(), match.away.casefold())] = match
    return list(unique.values())

def fetch_embedded_results(url: str, timeout: int = 20):
    html = fetch_page(url, timeout)
    ids = extract_ids(html)
    payload = extract_initial_feed(html, "results") or extract_initial_feed(html, "summary-results")
    return ids, parse_results(payload), payload
