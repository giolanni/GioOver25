"""Conservative Flashscore/Diretta polling for explicitly mapped fixture IDs.

Never guesses fixture IDs or team matches. Missing/unrecognized provider fields
are reported, never converted into invented scores or FINAL results.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from gioover25.live_monitor import FIELDS, save_snapshot

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "data/live/flashscore_match_ids.csv"
OUTPUT = ROOT / "data/live/partite_live.csv"
BASE = "https://global.flashscore.ninja/323/x/feed"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "*/*",
    "Referer": "https://www.diretta.it/",
    "Origin": "https://www.diretta.it",
    "x-fsign": "SW9D1eZo",
}
MATCH_ID = re.compile(r"^[A-Za-z0-9]{6,20}$")
FIELDS_ID = ("MatchDate", "LeagueId", "Home", "Away", "MatchId")


def fields_from_feed(payload):
    # Flashscore feed uses field/value separators. Decode only known keys.
    fields = {}
    for chunk in re.split(r"[¬~]", payload):
        if "÷" in chunk:
            key, value = chunk.split("÷", 1)
            if key in ("AG", "AH", "AC", "AB", "AD"):
                fields[key] = value.strip()
    return fields


def interpret(fields):
    home, away = fields.get("AG", ""), fields.get("AH", "")
    if not (home.isdecimal() and away.isdecimal()):
        raise ValueError("No verified score fields AG/AH")
    raw = fields.get("AC", "").casefold()
    if any(x in raw for x in ("finale", "finished", "full time", "after penalties", "dopo rigori")) or raw.strip() == "ft":
        status = "FINAL"
    elif any(x in raw for x in ("intervallo", "half time", "1 tempo", "2 tempo", "1st half", "2nd half", "supplementari")):
        status = "LIVE"
    else:
        raise ValueError("Unrecognized match state AC: " + repr(fields.get("AC", "")))
    minute = fields.get("AB", "")
    return home, away, status, minute


def fetch(match_id, timeout=12):
    url = BASE + "/df_su_1_" + match_id
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=timeout) as response:
        payload = response.read(150000).decode("utf-8", errors="replace")
    return payload


def collect(mapping=MAPPING, output=OUTPUT):
    if not mapping.exists():
        raise FileNotFoundError(f"Missing fixture-to-provider ID mapping: {mapping}")
    with mapping.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if not set(FIELDS_ID).issubset(reader.fieldnames or ()):
            raise ValueError("Mapping requires " + ";".join(FIELDS_ID))
        mappings = list(reader)
    valid = []
    failures = []
    for row in mappings:
        mid = row["MatchId"].strip()
        if not MATCH_ID.fullmatch(mid):
            failures.append(f"{row.get('Home')}: invalid MatchId")
            continue
        try:
            hg, ag, status, minute = interpret(fields_from_feed(fetch(mid)))
            valid.append({**{k: row[k].strip() for k in FIELDS_ID},
                          "Minute": minute, "HG": hg, "AG": ag,
                          "Status": status,
                          "LastUpdate": datetime.now(timezone.utc).isoformat()})
        except Exception as exc:
            failures.append(f"{mid}: {type(exc).__name__}: {exc}")
    if valid:
        import tempfile
        import os
        with tempfile.NamedTemporaryFile("w", suffix=".csv", encoding="utf-8",
                                         newline="", delete=False) as handle:
            temp = Path(handle.name)
            writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";")
            writer.writeheader()
            writer.writerows(valid)
        try:
            save_snapshot(temp, output)
        finally:
            os.unlink(temp)
    for message in failures:
        print("[LIVE] NOT VERIFIED:", message, file=sys.stderr)
    print(f"[LIVE] verified={len(valid)} unavailable={len(failures)} file={output}")
    return len(valid)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping", type=Path, default=MAPPING)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if collect(args.mapping, args.output) == 0:
        sys.exit("No verified live scores; previous CSV preserved")


if __name__ == "__main__":
    main()
