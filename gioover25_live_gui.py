"""LIVE window for GioOver2.5. Reads snapshots; never modifies official histories."""
import csv
import tkinter as tk
from datetime import date, datetime, timezone
from pathlib import Path
from tkinter import ttk

from gioover25.live_monitor import snapshot_index, evaluate, FINAL

ROOT = Path(__file__).resolve().parent
LIVE = ROOT / "data/live/partite_live.csv"
HISTORY = ROOT / "data/storico/ranking"


def rows(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


class LiveWindow(tk.Toplevel):
    def __init__(self, master, engine):
        super().__init__(master)
        self.engine = engine
        self.title("GioOver2.5 | LIVE")
        self.geometry("1120x650")
        self.configure(bg="#eef3fa")
        tk.Label(self, text="Monitor LIVE", bg="#eef3fa",
                 font=("Segoe UI", 19, "bold")).pack(anchor="w", padx=18, pady=12)
        self.summary = tk.StringVar(value="In attesa di dati")
        tk.Label(self, textvariable=self.summary, bg="#eef3fa").pack(anchor="w", padx=18)
        cols = ("match", "minute", "score", "status", "outcome")
        self.table = ttk.Treeview(self, columns=cols, show="headings")
        for col, title in zip(cols, ("Partita", "Minuto", "Risultato", "Stato", "Pronostico")):
            self.table.heading(col, text=title)
            self.table.column(col, width=380 if col == "match" else 130)
        for tag, color in (("OK", "#c9f2d1"), ("KO", "#ffd5d5"),
                           ("PENDING", "#fff2b8"), ("UNKNOWN", "#e7ebf0")):
            self.table.tag_configure(tag, background=color)
        self.table.pack(fill="both", expand=True, padx=18, pady=12)
        ttk.Button(self, text="Aggiorna ora", command=self.refresh).pack(pady=8)
        self.refresh()

    def refresh(self):
        self.table.delete(*self.table.get_children())
        engine = self.engine.get()
        path = HISTORY / engine / ("storico_ranking_" + engine + ".csv")
        try:
            live = snapshot_index(LIVE)
        except (OSError, ValueError) as exc:
            self.summary.set("Errore nel file LIVE: " + str(exc))
            self.after(60000, self.refresh)
            return
        today = date.today().isoformat()
        counts = {"OK": 0, "KO": 0, "PENDING": 0, "UNKNOWN": 0}
        final_ok = final_ko = 0
        for row in rows(path):
            if row.get("MatchDate", "").strip() != today:
                continue
            key = tuple(row.get(k, "").strip().casefold() for k in
                        ("LeagueId", "MatchDate", "Home", "Away"))
            match = live.get(key)
            outcome, minute, score, status = "UNKNOWN", "-", "-", "-"
            if match:
                minute, status = match["Minute"], match["Status"]
                score = (match["HG"] + "-" + match["AG"]) if match["HG"] and match["AG"] else "-"
                try:
                    updated = datetime.fromisoformat(match["LastUpdate"].replace("Z", "+00:00"))
                    fresh = updated.tzinfo is not None and 0 <= (
                        datetime.now(timezone.utc) - updated).total_seconds() <= 300
                except ValueError:
                    fresh = False
                if fresh:
                    outcome = evaluate(status, match["HG"], match["AG"],
                                       "BTTS" if engine.lower().startswith("vg") else "Over25")
                    if status in FINAL:
                        final_ok += outcome == "OK"
                        final_ko += outcome == "KO"
                else:
                    status += " (non aggiornato)"
            counts[outcome] += 1
            self.table.insert("", "end", values=(
                row.get("Home", "") + " – " + row.get("Away", ""),
                minute, score, status, outcome), tags=(outcome,))
        total = final_ok + final_ko
        pct = ("%.1f%%" % (100 * final_ok / total)) if total else "n.d."
        self.summary.set(
            f"{engine}: OK {counts['OK']} | KO {counts['KO']} | "
            f"in attesa {counts['PENDING']} | sconosciute {counts['UNKNOWN']} | "
            f"finali {final_ok}/{total} ({pct}). Aggiornamento file ogni 60 s.")
        self.after(60000, self.refresh)
