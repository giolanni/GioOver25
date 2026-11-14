"""Persistent operational audit for GUI acquisition and processing steps."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "data" / "live" / "gui_operations.json"
STEPS = ("getmatches", "rank_matches", "getresults", "append_results")

def load():
    try:
        data = json.loads(PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

def record(step, state, *, day=None, count=None, detail=""):
    data = load()
    data[step] = {"state": state, "day": day, "count": count,
                  "detail": detail, "time": datetime.now().astimezone().isoformat(timespec="seconds")}
    PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = PATH.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(PATH)

def summary(step):
    entry = load().get(step)
    if not entry:
        return "Nessuna esecuzione registrata dalla GUI"
    state = entry.get("state", "sconosciuto")
    day = entry.get("day") or "data non specificata"
    count = entry.get("count")
    amount = f" | {count} righe" if count is not None else ""
    when = entry.get("time", "").replace("T", " ")[:19]
    return f"{state} | {day}{amount} | {when}"
