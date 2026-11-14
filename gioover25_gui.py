"""GioOver2.5 desktop dashboard. Launch: python -m gioover25_gui"""
from __future__ import annotations
import csv
import subprocess
import sys
import threading
import tkinter as tk
from datetime import date, timedelta, datetime
from pathlib import Path
from tkinter import ttk, messagebox, simpledialog
from gioover25.live_monitor import snapshot_index, evaluate, FINAL
from gioover25 import history_stats, operations_audit, results_coverage
from tools.live_flashscore import key as live_fixture_key
from gioover25 import missing_results as missing_audit
from tools.prepare_input import norm, canonical_team
from datetime import timezone

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data/input_partite/partite.csv"
HISTORY = ROOT / "data/storico/ranking"
OUTPUT = ROOT / "data/output_ranking"
GROUP_REGISTRY = ROOT / 'docs/maps/league_group_registry.csv'
BANDS = ROOT / "data/analysis/score_bands/score_band_best.csv"
NAVY, BLUE, BG, WHITE = "#122c4a", "#1769d2", "#eef3fa", "#ffffff"


def csv_rows(path):
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, text=True,
                       capture_output=True, encoding="utf-8", errors="replace",
                       timeout=45, check=False)
    return p.returncode, (p.stdout + "\n" + p.stderr).strip()


def best_bands():
    out = {}
    for r in csv_rows(BANDS):
        if (r.get("Scope"), r.get("Period"), r.get("Type")) != ("ALL", "HISTORY", "INTERVAL"):
            continue
        band = r.get("ScoreRange", "")
        try:
            left, right = band.strip("[]()").split(",")
            low, high = float(left), float(right)
            out[r["Engine"].lower()] = (low, high, band, r.get("HitRate", ""), r.get("Total", ""))
        except (ValueError, KeyError):
            continue
    return out


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GioOver2.5 | Centro di controllo")
        self.geometry("1320x820")
        self.minsize(1050, 650)
        self.configure(bg=BG)
        self.busy = False
        self.loading_count = 0
        self.loading_window = None
        self.loading_bar = None
        self.engine = tk.StringVar(value="v20")
        self.only_best = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Pronto")
        self.view = "rankings"
        self.menu_buttons = {}
        self.live_poll_busy = False
        self.history_generation = 0
        self.history_period = tk.StringVar(value="Ultimi 7 giorni")
        self.history_mode = tk.StringVar(value="Confronto engine")
        self.history_market = tk.StringVar(value="OVER25")
        self.alert_rows = []
        self.refresh_generation = 0
        self.build()
        self.update_context_controls()
        self.show_home()
        self.refresh()

    def build(self):
        sidebar = tk.Frame(self, bg=NAVY, width=215)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="⚽ GioOver2.5", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 19, "bold")).pack(pady=(25, 30))
        menu = [
            ("Home", "home", self.open_home),
            ("Avvisi e anomalie", "alerts", self.show_alerts),
            ("Ranking giornalieri", "rankings", self.show_rankings),
            ("Analisi fasce Score", "bands", self.show_bands),
            ("Storico engine", "history", self.show_history),
            ("Monitor LIVE", "live", self.open_live),
            ("Aggiorna repository", None, self.update_repo),
            ("Gestione partite", "matches_ops", self.show_matches_ops),
            ("Gestione risultati", "results_ops", self.show_results_ops),
            ("Aggiorna fasce", None, self.run_bands),
        ]
        for label, section, action in menu:
            button = tk.Button(sidebar, text=label, command=action, bg=NAVY, fg=WHITE,
                               activebackground=BLUE, activeforeground=WHITE,
                               relief="flat", anchor="w", padx=18, pady=12,
                               font=("Segoe UI", 11))
            button.pack(fill="x", padx=8, pady=2)
            if section:
                self.menu_buttons[section] = button
        self.highlight_menu()
        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        tk.Label(main, text="Centro di controllo", bg=BG, fg=NAVY,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=22, pady=(18, 12))
        self.summary = tk.Frame(main, bg=BG)
        self.summary.pack(fill="x", padx=20)
        self.controls = tk.Frame(main, bg=BG)
        self.controls.pack(fill="x", padx=20, pady=(12, 5))
        self.engine_label = tk.Label(self.controls, text="Engine:", bg=BG)
        self.engine_label.pack(side="left")
        self.engine_box = ttk.Combobox(self.controls, textvariable=self.engine, width=20, state="readonly")
        self.engine_box.pack(side="left", padx=8)
        self.engine_box.bind("<<ComboboxSelected>>", self.on_engine_changed)
        self.best_filter = ttk.Checkbutton(self.controls, text="Solo fascia migliore", variable=self.only_best,
                                           command=self.show_rankings)
        self.best_filter.pack(side="left", padx=10)
        self.live_refresh_button = ttk.Button(self.controls, text="Aggiorna LIVE", command=self.refresh_live)
        self.live_refresh_button.pack(side="right", padx=5)
        self.reload_button = ttk.Button(self.controls, text="Ricarica", command=self.refresh)
        self.reload_button.pack(side="right")
        self.history_controls = tk.Frame(main, bg=BG)
        self.history_controls.pack(fill="x", padx=20)
        for title, variable, choices in (
            ("Periodo", self.history_period, history_stats.PERIODS),
            ("Vista", self.history_mode, ("Confronto engine", "Singolo engine")),
            ("Mercato", self.history_market, ("OVER25", "BTTS"))):
            tk.Label(self.history_controls, text=title + ":", bg=BG).pack(side="left", padx=(8, 3))
            combo = ttk.Combobox(self.history_controls, textvariable=variable,
                                 values=choices, state="readonly", width=19)
            combo.pack(side="left", padx=(0, 12))
            combo.bind("<<ComboboxSelected>>", lambda _: self.show_history())
        self.history_controls.pack_forget()
        self.operations_panel = tk.Frame(main, bg=BG)
        self.operations_panel.pack(fill="x", padx=20)
        self.operations_panel.pack_forget()
        self.columns = ("date", "league", "match", "score", "band", "best", "live_result", "live_outcome")
        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True, padx=20, pady=8)
        self.table = ttk.Treeview(table_frame, columns=self.columns, show="headings", height=16)
        for col, title, width in zip(self.columns,
                                     ("Data", "Campionato", "Partita", "Score", "Fascia", "Indicatore", "Risultato", "Esito LIVE"),
                                     (105, 220, 300, 75, 120, 160, 85, 110)):
            self.table.heading(col, text=title)
            self.table.column(col, width=width, anchor="center" if col in ("score", "best") else "w")
        self.table["displaycolumns"] = self.columns[:6]
        self.table.tag_configure("best", background="#dcf6df")
        for name, color in (("ok", "#c9f2d1"), ("ko", "#ffd5d5"), ("pending", "#fff2b8"), ("unknown", "#e7ebf0")):
            self.table.tag_configure(name, background=color)
        # Reserve the right edge for the scrollbar before packing the wide Treeview.
        # Otherwise the table can consume the full available width and hide it.
        table_scroll = tk.Scrollbar(table_frame, orient="vertical", width=18,
                                    command=self.table.yview, relief="raised",
                                    bg="#b4c4d8", activebackground="#7799bc")
        table_scroll.pack(side="right", fill="y")
        self.table.pack(side="left", fill="both", expand=True)
        self.table.configure(yscrollcommand=table_scroll.set)
        self.table.bind("<Control-c>", self.copy_alert_rows)
        self.table.bind("<Control-C>", self.copy_alert_rows)
        self.table.bind("<Button-3>", self.alert_context_menu)
        self.alert_menu = tk.Menu(self, tearoff=0)
        self.alert_menu.add_command(label="Copia partita", command=self.copy_alert_match)
        self.alert_menu.add_command(label="Copia righe selezionate", command=self.copy_alert_rows)
        tk.Label(main, textvariable=self.status, bg=BG, fg=NAVY,
                 anchor="w").pack(fill="x", padx=20)
        self.log = tk.Text(main, height=7, bg="#142b46", fg="#e7f1ff",
                           font=("Consolas", 9), state="disabled")
        self.log.pack(fill="x", padx=20, pady=(6, 15))

    def on_engine_changed(self, _event=None):
        """Refresh only the current engine-dependent view; never navigate."""
        handlers = {
            "live": self.show_live,
            "history": self.show_history,
            "rankings": self.show_rankings,
            "bands": self.show_bands,
        }
        handler = handlers.get(self.view)
        if handler is not None:
            handler()

    def highlight_menu(self):
        """Keep the selected navigation section visibly highlighted."""
        for section, button in self.menu_buttons.items():
            selected = section == self.view
            button.configure(
                bg=BLUE if selected else NAVY,
                fg=WHITE,
                activebackground="#0e4d9f" if selected else BLUE,
                font=("Segoe UI", 11, "bold" if selected else "normal"),
                relief="sunken" if selected else "flat",
                bd=1 if selected else 0,
            )

    def open_home(self):
        self.view = "home"
        self.highlight_menu()
        self.operations_panel.pack_forget()
        self.update_context_controls()
        self.show_home()
        self.refresh()

    def show_home(self):
        """Show a useful operational overview instead of a blank table."""
        self.view = "home"
        self.highlight_menu()
        self.update_context_controls()
        self.history_controls.pack_forget()
        self.table["displaycolumns"] = self.columns[:6]
        for col, heading, width in zip(self.columns,
                ("Area", "Situazione", "Dettaglio", "Vai a", "", ""),
                (195, 180, 425, 195, 30, 30)):
            self.table.heading(col, text=heading)
            self.table.column(col, width=width, anchor="w")
        self.table.delete(*self.table.get_children())
        today = date.today().isoformat()
        fixtures = csv_rows(INPUT)
        count = sum(r.get("MatchDate", "").strip() == today for r in fixtures)
        paths = list(HISTORY.glob("*/storico_ranking_*.csv"))
        missing = sum(r[3] == "SCHEDULED" for r in self.alert_rows)
        postponed = sum(r[3] == "POSTPONED" for r in self.alert_rows)
        entries = [
            ("Partite di oggi", str(count), "Fixture presenti nell'input", "Ranking giornalieri"),
            ("Esiti precedenti", "Statistiche OK/KO", "Sei periodi e confronti ALTA", "Storico engine"),
            ("Avvisi", str(missing) + " da recuperare", str(postponed) + " rinviate", "Avvisi e anomalie"),
            ("Storici engine", str(len(paths)), "Over 2.5 e BTTS separati", "Storico engine"),
            ("Monitor LIVE", "Manuale", "Risultati e verifica dei pronostici", "Monitor LIVE"),
            ("Fasce Score", "Disponibili" if BANDS.exists() else "Da generare",
             "Analisi della fascia migliore", "Analisi fasce Score"),
        ]
        for area, state, detail, destination in entries:
            self.table.insert("", "end", values=(area, state, detail, destination, "", ""))
        self.status.set("Home: panoramica operativa. Seleziona una sezione dal menu laterale.")

    def start_loading(self, message="Operazione in corso..."):
        """Modal progress overlay; the worker keeps Tk responsive."""
        self.loading_count += 1
        if self.loading_window is not None and self.loading_window.winfo_exists():
            return
        self.update_idletasks()
        overlay = tk.Toplevel(self)
        self.loading_window = overlay
        overlay.overrideredirect(True)
        overlay.configure(bg="#10253d")
        overlay.attributes("-alpha", 0.88)
        overlay.transient(self)
        overlay.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{self.winfo_rootx()}+{self.winfo_rooty()}")
        panel = tk.Frame(overlay, bg="#10253d")
        panel.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(panel, text="Operazione in corso", bg="#10253d", fg="white",
                 font=("Segoe UI", 20, "bold")).pack(pady=(0, 12))
        tk.Label(panel, text=message, bg="#10253d", fg="#d7e5f6",
                 font=("Segoe UI", 12)).pack(pady=(0, 18))
        self.loading_bar = ttk.Progressbar(panel, mode="indeterminate", length=260)
        self.loading_bar.pack()
        self.loading_bar.start(12)
        overlay.lift(self)
        overlay.grab_set()
        overlay.bind("<Escape>", lambda _event: "break")
        self.bind("<Configure>", self._position_loading, add="+")

    def _position_loading(self, _event=None):
        overlay = self.loading_window
        if overlay is not None and overlay.winfo_exists():
            overlay.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{self.winfo_rootx()}+{self.winfo_rooty()}")

    def stop_loading(self):
        if self.loading_count:
            self.loading_count -= 1
        if self.loading_count:
            return
        overlay = self.loading_window
        self.loading_window = None
        if overlay is not None and overlay.winfo_exists():
            if self.loading_bar is not None:
                self.loading_bar.stop()
            overlay.grab_release()
            overlay.destroy()
        self.loading_bar = None

    def write_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", f"[{datetime.now():%H:%M:%S}] {text}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def card(self, title, value, note=""):
        frame = tk.Frame(self.summary, bg=WHITE, highlightbackground="#c9d7e7", highlightthickness=1)
        frame.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(frame, text=title, bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
        tk.Label(frame, text=value, bg=WHITE, fg=BLUE, font=("Segoe UI", 13, "bold"),
                 wraplength=220, justify="left").pack(anchor="w", padx=12)
        tk.Label(frame, text=note, bg=WHITE, fg="#57677b", font=("Segoe UI", 9),
                 wraplength=220, justify="left").pack(anchor="w", padx=12, pady=(2, 10))

    def collect_alerts(self):
        """Read-only: identify overdue unresolved fixtures and seasonal maps."""
        alerts = []
        if HISTORY.exists():
            matches = []
            for path in missing_audit.find_csv_files(HISTORY, "storico_ranking*.csv"):
                matches.extend(missing_audit.read_missing_from_file(path))
            matches = missing_audit.filter_matches(
                missing_audit.deduplicate(matches), band=None, exclude_australia=False)
            results = missing_audit.load_results_index(ROOT / "data/storico/risultati")
            matches = missing_audit.annotate_postponed(
                missing_audit.exclude_matches_already_in_results(matches, results), results)
            for m in matches:
                state = (m.historical_status or "").upper()
                if m.postponed == "SI":
                    category = "POSTPONED"
                elif "SCHEDULED" in state or "NOT_FOUND" in state or not state:
                    category = "SCHEDULED"
                else:
                    category = "SENZA ESITO"
                alerts.append((m.match_date, m.league_id, m.home + " – " + m.away,
                               category, (date.today() - date.fromisoformat(m.match_date)).days))
        for r in csv_rows(GROUP_REGISTRY):
            season = (r.get("Season") or "").strip()
            if not season:
                continue
            # For split-year seasons, renewal is due when the next season begins.
            start_year = int(season[:4]) if season[:4].isdigit() else None
            if start_year is None:
                continue
            renewal_year = start_year + 1
            # A warning without an official start date is deliberately conservative.
            if date.today().year >= renewal_year and r.get("Structure", "").upper() in ("GROUPS", "CONFERENCES"):
                alerts.append(("", r.get("LeagueId", ""), season,
                               "MAPPA DA RINNOVARE", 0))
            elif not r.get("MappingFile", "").strip() and r.get("Structure", "").upper() == "GROUPS":
                alerts.append(("", r.get("LeagueId", ""), season,
                               "MAPPA MANCANTE", 0))
        return sorted(alerts, key=lambda x: (x[0] == "", x[0], x[1]))

    def _selected_alert_values(self):
        if self.view != "alerts":
            return []
        return [self.table.item(item, "values") for item in self.table.selection()]

    def _copy_alert_text(self, value):
        if not value:
            return
        self.clipboard_clear()
        self.clipboard_append(value)
        self.update_idletasks()
        self.status.set("Avvisi: testo copiato negli appunti.")

    def copy_alert_match(self):
        rows = self._selected_alert_values()
        if rows:
            self._copy_alert_text("\n".join(str(row[2]) for row in rows))

    def copy_alert_rows(self, _event=None):
        rows = self._selected_alert_values()
        if rows:
            lines = ["Data\tCampionato\tPartita\tTipo\tGiorni"]
            lines.extend("\t".join(str(value) for value in row[:5]) for row in rows)
            self._copy_alert_text("\n".join(lines))
        return "break" if self.view == "alerts" else None

    def alert_context_menu(self, event):
        if self.view != "alerts":
            return
        item = self.table.identify_row(event.y)
        if not item:
            return
        if item not in self.table.selection():
            self.table.selection_set(item)
        self.table.focus(item)
        try:
            self.alert_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.alert_menu.grab_release()

    def show_alerts(self):
        self.history_controls.pack_forget()
        self.view = "alerts"
        self.highlight_menu()
        self.operations_panel.pack_forget()
        self.update_context_controls()
        self.table["displaycolumns"] = self.columns[:6]
        for col, label in zip(self.columns, ("Data", "Campionato", "Partita / stagione", "Tipo", "Giorni", "Azione")):
            self.table.heading(col, text=label)
        self.table.delete(*self.table.get_children())
        for day, league, match, kind, age in self.alert_rows:
            self.table.insert("", "end", values=(day, league, match, kind,
                              str(age) if day else "", "Verificare"),
                              tags=("ko",) if kind == "SCHEDULED" else ("pending",))
        self.status.set(f"Avvisi: {len(self.alert_rows)} | controllo di sola lettura; nessun risultato modificato")

    def refresh(self):
        """Load large CSV histories off the Tk main thread."""
        self.refresh_generation += 1
        generation = self.refresh_generation
        self.status.set("Aggiornamento controlli in corso (puoi usare il menu)...")
        def work():
            try:
                today = date.today().isoformat()
                yesterday = (date.today() - timedelta(days=1)).isoformat()
                fixtures = csv_rows(INPUT)
                today_rows = sum(r.get("MatchDate", "").strip() == today for r in fixtures)
                paths = list(HISTORY.glob("*/storico_ranking_*.csv"))
                engines = sorted(p.parent.name for p in paths)
                unresolved = resolved = 0
                for path in paths:
                    # Stream instead of loading each large history in memory.
                    with path.open(encoding="utf-8-sig", newline="") as stream:
                        for r in csv.DictReader(stream, delimiter=";"):
                            if r.get("MatchDate", "").strip() != yesterday:
                                continue
                            if r.get("Over25", "").upper() in ("OK", "KO") or r.get("BTTS", "").upper() in ("OK", "KO"):
                                resolved += 1
                            else:
                                unresolved += 1
                alerts = self.collect_alerts()
                error = None
            except Exception as exc:
                today_rows, resolved, unresolved, engines, alerts = 0, 0, 0, [], []
                error = str(exc)
            def done():
                if generation != self.refresh_generation or not self.winfo_exists():
                    return
                self.alert_rows = alerts
                for child in self.summary.winfo_children():
                    child.destroy()
                self.card("Partite di oggi", f"{today_rows} presenti" if today_rows else "Da verificare",
                          "Input odierno presente" if today_rows else "Nessuna partita con MatchDate odierna")
                self.card("Esiti di ieri", f"{resolved} risolti",
                          f"{unresolved} righe non risolte negli storici engine")
                missing = sum(r[3] == "SCHEDULED" for r in alerts)
                postponed = sum(r[3] == "POSTPONED" for r in alerts)
                maps = sum(r[3].startswith("MAPPA") for r in alerts)
                self.card("Avvisi", f"{missing} da recuperare",
                          f"{postponed} rinviate | {maps} mappe")
                self.card("Ranking / engine", f"{len(engines)} storici",
                          "Controllo generazione disponibile nella tabella")
                self.card("Fasce Score", "Disponibili" if BANDS.exists() else "Da generare",
                          f"CSV: {BANDS.name}")
                self.engine_box["values"] = engines
                if engines and self.engine.get() not in engines:
                    self.engine.set(engines[0])
                if error:
                    self.write_log("Controllo dashboard: " + error)
                # Do not reset the user's selected view when a background refresh finishes.
                if self.view == "alerts":
                    self.show_alerts()
                elif self.view == "rankings":
                    self.show_rankings()
                elif self.view == "home":
                    self.show_home()
                self.check_git()
            self.after(0, done)
        threading.Thread(target=work, daemon=True).start()

    def check_git(self):
        def work():
            rc, status = git("status", "--porcelain")
            rc2, branch = git("branch", "--show-current")
            msg = f"Repository: {branch.strip()} | " + ("modifiche locali presenti" if status else "working tree pulito")
            if rc or rc2:
                msg = "Git non disponibile o repository non accessibile"
            self.after(0, lambda: self.write_log(msg))
        threading.Thread(target=work, daemon=True).start()

    def open_live(self):
        self.show_live()

    def refresh_live(self):
        if self.view != "live":
            self.open_live()
        self.poll_live()

    def poll_live(self):
        if self.live_poll_busy:
            return
        self.live_poll_busy = True
        self.start_loading("Acquisizione risultati LIVE da Diretta...")
        def work():
            try:
                result = subprocess.run([sys.executable, "-m", "tools.live_flashscore"],
                    cwd=ROOT, capture_output=True, text=True, timeout=100,
                    encoding="utf-8", errors="replace")
                msg = (result.stdout + " " + result.stderr).strip()
            except Exception as exc:
                msg = str(exc)
            def done():
                self.live_poll_busy = False
                self.stop_loading()
                self.write_log(msg[:1500])
                if self.view == "live":
                    self.show_live()
            self.after(0, done)
        threading.Thread(target=work, daemon=True).start()
    @staticmethod
    def ranking_score(row):
        """Numeric descending score; invalid or missing scores go last."""
        try:
            value = float(str(row.get("Score", "")).strip().replace(",", "."))
            return value if value == value else float("-inf")
        except (ValueError, TypeError):
            return float("-inf")

    def show_live(self):
        self.history_controls.pack_forget()
        self.view = "live"
        self.highlight_menu()
        self.operations_panel.pack_forget()
        self.update_context_controls()
        self.table["displaycolumns"] = self.columns
        for col, label, width in zip(self.columns,
                              ("Data", "Campionato", "Partita", "Score", "Fascia", "Minuto", "Risultato", "Esito LIVE"),
                              (105, 220, 300, 75, 125, 100, 85, 110)):
            self.table.heading(col, text=label)
            self.table.column(col, width=width, anchor="center" if col in ("score", "band", "best", "live_result", "live_outcome") else "w")
        self.table.delete(*self.table.get_children())
        try:
            live = snapshot_index(ROOT / "data/live/partite_live.csv")
        except (OSError, ValueError) as exc:
            self.status.set("LIVE: errore lettura dati: " + str(exc))
            return
        engine = self.engine.get()
        today = date.today().isoformat()
        history = HISTORY / engine / ("storico_ranking_" + engine + ".csv")
        rows = sorted((r for r in csv_rows(history) if r.get("MatchDate", "").strip() == today),
                      key=self.ranking_score, reverse=True)
        counts = {"OK": 0, "KO": 0, "PENDING": 0, "UNKNOWN": 0}
        finals = {"OK": 0, "KO": 0}
        alta_counts = {"OK": 0, "KO": 0, "PENDING": 0, "UNKNOWN": 0}
        alta_finals = {"OK": 0, "KO": 0}
        market = "BTTS" if engine.lower().startswith("vg") else "Over25"
        normalized_live = {
            live_fixture_key(lid, day, home, away): item
            for (lid, day, home, away), item in live.items()
        }
        for r in rows:
            key = live_fixture_key(r.get("LeagueId", "").strip(), today,
                                   r.get("Home", ""), r.get("Away", ""))
            item = normalized_live.get(key)
            outcome, minute, score = "UNKNOWN", "-", "-"
            if item:
                minute = item["Minute"] or item["Status"]
                if item["HG"] and item["AG"]:
                    score = item["HG"] + "-" + item["AG"]
                try:
                    ts = datetime.fromisoformat(item["LastUpdate"].replace("Z", "+00:00"))
                    fresh = ts.tzinfo is not None and 0 <= (
                        datetime.now(timezone.utc) - ts).total_seconds() <= 300
                except ValueError:
                    fresh = False
                if fresh:
                    outcome = evaluate(item["Status"], item["HG"], item["AG"], market)
                    if item["Status"] in FINAL and outcome in finals:
                        finals[outcome] += 1
                else:
                    minute += " (non aggiornato)"
            counts[outcome] += 1
            if (r.get("Band") or "").strip().upper() == "ALTA":
                alta_counts[outcome] += 1
                if item and fresh and item["Status"] in FINAL and outcome in alta_finals:
                    alta_finals[outcome] += 1
            self.table.insert("", "end",
                values=(today, r.get("LeagueId", ""),
                        r.get("Home", "") + " – " + r.get("Away", ""),
                        r.get("Score", ""), r.get("Band", ""), minute, score, outcome),
                tags=(outcome.lower(),))
        def summary(label, statuses, finished):
            total = sum(finished.values())
            percentage = f"{100 * finished['OK'] / total:.1f}%" if total else "n.d."
            return (f"{label}: OK {statuses['OK']} | KO {statuses['KO']} | "
                    f"In attesa {statuses['PENDING']} | Senza dati {statuses['UNKNOWN']} | "
                    f"Finali {finished['OK']}/{total} ({percentage})")
        self.status.set(
            f"LIVE {engine} — Fonte: Diretta, aggiornamento manuale.  "
            + summary("FASCIA ALTA", alta_counts, alta_finals)
            + "     ||     "
            + summary("TOTALE ENGINE", counts, finals))

    def show_rankings(self):
        self.history_controls.pack_forget()
        self.view = "rankings"
        self.highlight_menu()
        self.operations_panel.pack_forget()
        self.update_context_controls()
        self.table["displaycolumns"] = self.columns[:6]
        for col, label in zip(self.columns, ("Data", "Campionato", "Partita", "Score", "Fascia", "Indicatore")):
            self.table.heading(col, text=label)
        for item in self.table.get_children():
            self.table.delete(item)
        engine = self.engine.get()
        path = HISTORY / engine / f"storico_ranking_{engine}.csv"
        bands = best_bands()
        best = bands.get(engine.lower())
        today = date.today().isoformat()
        rows = sorted((r for r in csv_rows(path) if r.get("MatchDate", "").strip() == today),
                      key=self.ranking_score, reverse=True)
        for r in rows:
            try:
                score = float(r.get("Score", "").replace(",", "."))
            except ValueError:
                continue
            marked = bool(best and best[0] <= score <= best[1] and (score < best[1] or best[1] == 100))
            if self.only_best.get() and not marked:
                continue
            self.table.insert("", "end", values=(today, r.get("LeagueId", ""),
                r.get("Home", "") + " – " + r.get("Away", ""), f"{score:g}",
                r.get("Band", ""), "★ Fascia migliore" if marked else ""),
                tags=("best",) if marked else ())
        self.status.set(f"{engine}: {len(rows)} pronostici odierni nello storico; fascia migliore: {best[2] if best else 'non disponibile'}")

    def update_context_controls(self):
        """Display only actions relevant to the selected page."""
        self.update_engine_visibility()
        if self.view == "rankings":
            if not self.best_filter.winfo_manager():
                self.best_filter.pack(side="left", padx=10)
        else:
            self.best_filter.pack_forget()
        if self.view == "live":
            if not self.live_refresh_button.winfo_manager():
                self.live_refresh_button.pack(side="right", padx=5)
        else:
            self.live_refresh_button.pack_forget()
        if self.view in ("matches_ops", "results_ops"):
            self.reload_button.pack_forget()
        elif not self.reload_button.winfo_manager():
            self.reload_button.pack(side="right")
        self.reload_button.configure(
            text=("Aggiorna avvisi" if self.view == "alerts" else
                  "Aggiorna riepilogo" if self.view == "home" else "Ricarica"))

    def update_engine_visibility(self):
        visible = self.view not in ("history", "alerts", "home", "matches_ops", "results_ops") or (self.view == "history" and self.history_mode.get() == "Singolo engine")
        if visible:
            # Pack the label first without referring to a hidden combobox.
            # Tk raises TclError if "before" references an unpacked widget.
            if not self.engine_label.winfo_manager():
                self.engine_label.pack(side="left")
            if not self.engine_box.winfo_manager():
                self.engine_box.pack(side="left", padx=8, after=self.engine_label)
        else:
            self.engine_label.pack_forget()
            self.engine_box.pack_forget()

    def show_history(self):
        """Build historical statistics in a worker; never block Tk with CSV reads."""
        self.view = "history"
        self.highlight_menu()
        self.operations_panel.pack_forget()
        self.update_context_controls()
        if not self.history_controls.winfo_manager():
            self.history_controls.pack(fill="x", padx=20, before=self.table.master)
        self.history_generation += 1
        generation = self.history_generation
        period = self.history_period.get()
        mode = self.history_mode.get()
        engine = self.engine.get()
        market = self.history_market.get()
        if mode == "Singolo engine":
            market = history_stats.market_for(engine)
            self.history_market.set(market)
        self.table["displaycolumns"] = self.columns[:6]
        headers = (("Periodo", "Mercato", "ALTA OK", "ALTA KO", "Totale ALTA", "% ALTA OK")
                   if mode == "Singolo engine" else
                   ("Engine", "Mercato", "ALTA OK", "ALTA KO", "Totale ALTA", "% ALTA OK"))
        for col, label, width in zip(self.columns, headers, (185, 100, 105, 105, 115, 120)):
            self.table.heading(col, text=label)
            self.table.column(col, width=width, anchor="center")
        self.table.delete(*self.table.get_children())
        self.status.set("Storico: elaborazione in corso...")
        def work():
            try:
                histories = history_stats.read_histories(HISTORY)
                common_start = history_stats.common_start_dates(histories).get(market)
                common_count = history_stats.common_size(histories, market)
                result = ([(p, r) for p in history_stats.PERIODS
                           for r in history_stats.compute(histories, p)
                           if r["engine"] == engine]
                          if mode == "Singolo engine" else
                          [(period, r) for r in history_stats.compute(histories, period)
                           if r["market"] == market])
                error = None
            except Exception as exc:
                result, common_count, common_start, error = [], 0, None, str(exc)
            def done():
                if generation != self.history_generation or self.view != "history":
                    return
                if error:
                    self.status.set("Errore storico: " + error)
                    self.write_log("Storico: " + error)
                    return
                for label, r in result:
                    self.table.insert("", "end", values=(
                        label if mode == "Singolo engine" else r["engine"],
                        r["market"], r["ok"], r["ko"],
                        r["total"], history_stats.rate_text(r)))
                if mode == "Singolo engine":
                    self.status.set(
                        f"Storico {engine} ({market}) | sei periodi; ALTA OK/KO; "
                        "set comune = data iniziale condivisa per mercato.")
                else:
                    total_ok = sum(r["ok"] for _, r in result)
                    total_ko = sum(r["ko"] for _, r in result)
                    rate = (f"{100 * total_ok / (total_ok + total_ko):.2f}%"
                            if total_ok + total_ko else "n.d.")
                    common_note = (f" | Dal {common_start or 'n.d.'} | {common_count} gare distinte" if period == "Set comune" else "")
                    if period == "Set comune" and common_count == 0:
                        self.write_log(f"ATTENZIONE: nessuna gara dal periodo comune {market}; verificare le date iniziali degli storici.")
                    self.status.set(
                        f"Storico {period} | {market}{common_note} | "
                        f"ALTA aggregate: OK {total_ok}, KO {total_ko}, "
                        f"Totale {total_ok + total_ko}, {rate} | "
                        "classifica per % ALTA OK decrescente.")
            self.after(0, done)
        threading.Thread(target=work, daemon=True).start()

    def show_bands(self):
        self.history_controls.pack_forget()
        self.view = "bands"
        self.highlight_menu()
        self.operations_panel.pack_forget()
        self.update_context_controls()
        self.table["displaycolumns"] = self.columns[:6]
        for item in self.table.get_children():
            self.table.delete(item)
        engine = self.engine.get()
        rows = [r for r in csv_rows(ROOT / "data/analysis/score_bands/score_band_details.csv")
                if r.get("Engine") == engine and r.get("Scope") == "ALL" and
                r.get("Period") == "HISTORY" and r.get("Type") == "INTERVAL"]
        for r in rows:
            self.table.insert("", "end", values=("", r.get("ScoreRange", ""),
                f"OK {r.get('OK')} / KO {r.get('KO')}", r.get("HitRate", "") + "%",
                r.get("Total", ""), "Campione sufficiente" if r.get("SufficientSample") == "YES" else "Campione ridotto"))
        self.status.set(f"Fasce Score di {engine}, ordinate per percentuale decrescente")

    def task(self, command, on_done=None, *, audit_step=None, audit_day=None, audit_csv=None):
        if self.busy:
            messagebox.showwarning("Operazione in corso", "Attendere la conclusione dell'operazione precedente.")
            return
        self.busy = True
        if audit_step:
            operations_audit.record(audit_step, "IN CORSO", day=audit_day)
            self.write_log(f"[OPERAZIONE] Avviato {audit_step} | {audit_day or 'input corrente'}")
        self.start_loading("Elaborazione in corso, attendere...")
        self.status.set("Operazione in corso...")
        def work():
            try:
                p = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT, text=True,
                                     encoding="utf-8", errors="replace", bufsize=1)
                for line in p.stdout:
                    self.after(0, self.write_log, line.rstrip())
                rc = p.wait()
                def done():
                    self.busy = False
                    self.stop_loading()
                    self.status.set(f"Comando terminato (codice {rc})")
                    if audit_step:
                        count = len(csv_rows(audit_csv)) if rc == 0 and audit_csv else None
                        operations_audit.record(audit_step, "COMPLETATO" if rc == 0 else "ERRORE",
                                                day=audit_day, count=count, detail=f"exit={rc}")
                        self.write_log(f"[OPERAZIONE] {audit_step}: codice={rc}, righe={count}")
                        if self.view == "matches_ops":
                            self.show_matches_ops()
                        elif self.view == "results_ops":
                            self.show_results_ops()
                    if rc == 0 and on_done:
                        on_done()
                    elif rc:
                        messagebox.showerror("Errore", f"Comando terminato con codice {rc}. Consultare il log.")
                self.after(0, done)
            except Exception as exc:
                def failed():
                    self.busy = False
                    self.stop_loading()
                    self.write_log(str(exc))
                    if audit_step:
                        operations_audit.record(audit_step, "ERRORE", day=audit_day, detail=str(exc))
                    messagebox.showerror("Errore", str(exc))
                self.after(0, failed)
        threading.Thread(target=work, daemon=True).start()

    def git_sequence(self, commands):
        """Run Git commands sequentially; stop on first failure."""
        if self.busy:
            return
        self.busy = True
        self.start_loading("Sincronizzazione repository Git...")
        self.status.set("Sincronizzazione repository in corso...")
        def work():
            for args in commands:
                self.after(0, self.write_log, "$ git " + " ".join(args))
                try:
                    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                       text=True, encoding="utf-8", errors="replace",
                                       timeout=180, check=False)
                    detail = (p.stdout + "\n" + p.stderr).strip()
                    if detail:
                        self.after(0, self.write_log, detail)
                    if p.returncode:
                        def fail(args=args, rc=p.returncode):
                            self.busy = False
                            self.stop_loading()
                            self.status.set("Git interrotto: " + " ".join(args))
                            messagebox.showerror("Git", "Comando fallito: git " +
                                " ".join(args) + f" (codice {rc}). Verificare il log. "
                                "I comandi successivi non sono stati eseguiti.")
                        self.after(0, fail)
                        return
                except Exception as exc:
                    def fail_exception(error=str(exc)):
                        self.busy = False
                        self.stop_loading()
                        self.status.set("Errore Git")
                        messagebox.showerror("Git", error)
                    self.after(0, fail_exception)
                    return
            def done():
                self.busy = False
                self.stop_loading()
                self.refresh()
                self.status.set("Sincronizzazione Git completata")
            self.after(0, done)
        threading.Thread(target=work, daemon=True).start()

    def update_repo(self):
        if self.busy:
            return
        rc, branch = git("branch", "--show-current")
        if rc or not branch.strip():
            messagebox.showerror("Git", "Impossibile identificare il branch corrente.")
            return
        branch = branch.strip()
        rc, changes = git("status", "--porcelain")
        if rc:
            messagebox.showerror("Git", changes)
            return
        if changes:
            preview = changes[:1800]
            if not messagebox.askyesno("Modifiche locali",
                "Branch: " + branch + "\n\nModifiche rilevate:\n" + preview +
                "\n\nVuoi includere TUTTI i file modificati e non tracciati "
                "(git add -A), creare un commit, sincronizzare e fare push? "
                "Controlla che non ci siano dati riservati o file da escludere."):
                return
            message = simpledialog.askstring("Messaggio commit",
                "Inserisci il messaggio del commit:", parent=self)
            if not message or not message.strip():
                return
            commands = [
                ["add", "-A"],
                ["commit", "-m", message.strip()],
                ["pull", "--rebase", "origin", branch],
                ["push", "origin", branch],
            ]
        else:
            if not messagebox.askyesno("Aggiorna repository",
                "Nessuna modifica locale. Eseguire git pull --ff-only sul branch " +
                branch + "?"):
                return
            commands = [["pull", "--ff-only", "origin", branch]]
            if messagebox.askyesno("Push opzionale",
                "Vuoi anche pubblicare eventuali commit locali già presenti sul branch " +
                branch + "?"):
                commands.append(["push", "origin", branch])
        self.git_sequence(commands)

    def _operation_date(self, title, default):
        value = simpledialog.askstring(
            title, "Data (AAAA-MM-GG):", initialvalue=default, parent=self)
        if value is None:
            return None
        try:
            chosen = date.fromisoformat(value.strip())
            if chosen.isoformat() != value.strip():
                raise ValueError("Formato data non valido")
            return chosen
        except ValueError:
            messagebox.showerror("Data non valida", "Inserisci una data nel formato AAAA-MM-GG.")
            return None

    def _operation_page(self, section, heading, description, actions):
        self.view = section
        self.highlight_menu()
        self.update_context_controls()
        self.history_controls.pack_forget()
        self.operations_panel.pack_forget()
        for widget in self.operations_panel.winfo_children():
            widget.destroy()
        tk.Label(self.operations_panel, text=heading, bg=BG, fg=NAVY,
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", pady=(12, 8))
        tk.Label(self.operations_panel, text=description, bg=BG, fg=NAVY,
                 justify="left", wraplength=900).pack(anchor="w", pady=(0, 12))
        buttons = tk.Frame(self.operations_panel, bg=BG)
        buttons.pack(anchor="w", pady=(0, 10))
        for label, action in actions:
            ttk.Button(buttons, text=label, command=action).pack(side="left", padx=(0, 12))
        self.operations_panel.pack(fill="x", padx=20, before=self.table.master)
        self.table["displaycolumns"] = self.columns[:6]
        for col, heading in zip(self.columns, ("Operazione", "Input", "Output", "Note", "", "")):
            self.table.heading(col, text=heading)
        self.table.delete(*self.table.get_children())
        self.status.set(description)

    def _operation_status_row(self, label, step):
        entry = operations_audit.load().get(step, {})
        return (label, operations_audit.summary(step),
                str(entry.get("count") if entry.get("count") is not None else "-"),
                entry.get("detail", ""))

    def _operation_pending(self, earlier, later):
        data = operations_audit.load()
        first, second = data.get(earlier, {}), data.get(later, {})
        return (first.get("state") == "COMPLETATO" and
                (second.get("state") != "COMPLETATO" or
                 second.get("time", "") < first.get("time", "")))

    def show_matches_ops(self):
        self._operation_page(
            "matches_ops", "Gestione partite",
            "CONTROLLO DELLA GIORNATA: cosa abbiamo acquisito, quali engine "
            "hanno elaborato le gare e quale passaggio manca.",
            [("1  Scarica partite", self.run_getmatches),
             ("2  Genera pronostici", self.run_ranking)])
        day = date.today().isoformat()
        rows = csv_rows(INPUT)
        fixtures = [r for r in rows if (r.get("MatchDate") or "").strip() == day]
        latest_dates = sorted({r.get("MatchDate", "").strip() for r in rows
                               if r.get("MatchDate", "").strip()})
        latest = latest_dates[-1] if latest_dates else None
        audit = operations_audit.load()
        get, rank = audit.get("getmatches", {}), audit.get("rank_matches", {})
        self.table.insert("", "end", values=(
            "GIORNATA DA CONTROLLARE", day,
            f"{len(fixtures)} partite nel CSV",
            "Oggi: non la data più recente presente nel file"))
        if not fixtures:
            self.table.insert("", "end", values=(
                "ATTENZIONE", "Nessuna partita di oggi nell'input",
                f"Ultima data nel CSV: {latest or 'nessuna'}",
                "Scarica le partite di oggi prima di generare i ranking"))
        # Restrict the engine check to the actual date requested by the user.
        # A missing prediction is not necessarily a failure: selective engines may abstain.
        engine_files = sorted(HISTORY.glob("*/storico_ranking_*.csv"))
        engine_counts = []
        for path in engine_files:
            n = sum(1 for r in csv_rows(path)
                    if (r.get("MatchDate") or "").strip() == day)
            engine_counts.append((path.parent.name, n))
        active = [(name, n) for name, n in engine_counts if n]
        self.table.insert("", "end", values=(
            "PRONOSTICI DI OGGI", f"{len(active)}/{len(engine_files)} engine con selezioni",
            f"{sum(n for _, n in active)} pronostici",
            "Un engine selettivo può produrre zero gare senza errori"))
        self.table.insert("", "end", values=(
            "ULTIMO DOWNLOAD", get.get("day") or "Non registrato",
            get.get("state", "Non registrato"),
            (get.get("time") or "").replace("T", " ")[:19]))
        self.table.insert("", "end", values=(
            "ULTIMA GENERAZIONE", rank.get("day") or "Input corrente",
            rank.get("state", "Non registrata"),
            (rank.get("time") or "").replace("T", " ")[:19]))
        acquired_today = (get.get("state") == "COMPLETATO" and get.get("day") == day)
        rank_after_download = (rank.get("state") == "COMPLETATO" and acquired_today
                               and rank.get("time", "") >= get.get("time", ""))
        if not fixtures:
            verdict = "SCARICA LE PARTITE DI OGGI"
            reason = "Non risultano gare odierne nel file di input"
        elif not acquired_today:
            verdict = "ACQUISIZIONE ODIERNA NON CERTIFICATA"
            reason = "Il file contiene gare, ma manca una acquisizione odierna completata dalla GUI"
        elif not rank_after_download:
            verdict = "GENERA I PRONOSTICI"
            reason = "Non risulta una generazione completata dopo il download odierno"
        else:
            verdict = "FLUSSO COMPLETATO DALLA GUI"
            reason = "Download e ranking completati in ordine; verificare eventuali errori nel log"
        self.table.insert("", "end", values=("COSA FARE ORA", verdict, "", reason))
        for name, count in sorted(engine_counts, key=lambda x: (-x[1], x[0])):
            self.table.insert("", "end", values=(
                "ENGINE", name, f"{count} pronostici oggi",
                "Nessuna selezione" if count == 0 else "Pronostici presenti"))
        self.status.set(f"Gestione partite {day}: {len(fixtures)} gare nell'input; "
                        f"{len(active)} engine con pronostici. {verdict}.")

    def show_results_ops(self):
        self._operation_page(
            "results_ops", "Gestione risultati",
            "Obiettivo: controllare se le giornate fino a ieri hanno risultati disponibili "
            "e se gli engine li hanno recepiti. "
            "I risultati mancanti richiedono verifica: non sempre sono da scaricare.",
            [("1  Scarica risultati per data", self.run_getresults),
             ("2  Registra risultati negli storici", self.run_append_results),
             ("Ricontrolla giornate", self.verify_results_coverage)])
        self.table.insert("", "end", values=(
            "CONTROLLO", "Verifica delle giornate fino a ieri in corso...", "", ""))
        self.verify_results_coverage()

    def verify_results_coverage(self):
        if self.view != "results_ops":
            return
        self.status.set("Controllo delle giornate fino a ieri...")
        def work():
            try:
                report = results_coverage.inspect(ROOT)
                error = None
            except Exception as exc:
                report, error = {}, str(exc)
            def done():
                if self.view != "results_ops":
                    return
                self.table.delete(*self.table.get_children())
                if error:
                    self.table.insert("", "end", values=("ERRORE", error, "", ""))
                    self.status.set("Verifica non riuscita")
                    return
                get = operations_audit.load().get("getresults", {})
                app = operations_audit.load().get("append_results", {})
                total_missing = sum(x["missing"] for x in report.values())
                total_pending = sum(x["unregistered"] for x in report.values())
                incomplete = sum(bool(x["missing"] or x["unregistered"]) for x in report.values())
                complete = len(report) - incomplete
                self.table.insert("", "end", values=(
                    "SITUAZIONE GENERALE",
                    f"{complete} giornate senza anomalie",
                    f"{incomplete} giornate da verificare",
                    "Controllo sui pronostici conosciuti, non su tutte le gare del provider"))
                self.table.insert("", "end", values=(
                    "RISULTATI DA VERIFICARE", f"{total_missing} gare senza risultato",
                    f"{total_pending} gare con engine non aggiornati",
                    "Rinvii esclusi dal conteggio dei risultati mancanti"))
                self.table.insert("", "end", values=(
                    "ULTIMO DOWNLOAD", get.get("day") or "Non registrato",
                    get.get("state", "Non registrato"),
                    (get.get("time") or "").replace("T", " ")[:19]))
                self.table.insert("", "end", values=(
                    "ULTIMA REGISTRAZIONE", app.get("day") or "Data input corrente",
                    app.get("state", "Non registrata"),
                    (app.get("time") or "").replace("T", " ")[:19]))
                for day, info in report.items():
                    if info["missing"]:
                        action = "Verificare / scaricare risultati"
                    elif info["unregistered"]:
                        action = "Verificare registrazione negli engine"
                    else:
                        action = "Nessuna anomalia rilevata"
                    self.table.insert("", "end", values=(
                        day,
                        f'{info["available"]}/{info["total"]} risultati disponibili',
                        f'{info["registered"]} registrate | {info["unregistered"]} da verificare',
                        action + f' | {info["postponed"]} rinviate'))
                    if info["missing"] or info["unregistered"]:
                        for key, reason, engines in info["details"][:30]:
                            self.table.insert("", "end", values=(
                                "  PARTITA", key[0], key[2] + " - " + key[3], reason))
                self.status.set(
                    f"Fino a ieri: {complete} giornate senza anomalie, "
                    f"{incomplete} da verificare | {total_missing} gare senza risultato | "
                    f"{total_pending} con esito engine da verificare.")
            self.after(0, done)
        threading.Thread(target=work, daemon=True).start()

    def run_getmatches(self):
        chosen = self._operation_date("Acquisisci partite", date.today().isoformat())
        if chosen is not None:
            self.task([sys.executable, "getmatches.py", "--date", chosen.isoformat()], self.refresh, audit_step="getmatches", audit_day=chosen.isoformat(), audit_csv=INPUT)

    def run_getresults(self):
        missing_days = sorted({
            row[0] for row in self.alert_rows
            if row[3] == "SCHEDULED" and row[0] and row[0] < date.today().isoformat()
        }, reverse=True)
        suggested = missing_days[0] if missing_days else (date.today() - timedelta(days=1)).isoformat()
        chosen = self._operation_date("Aggiorna risultati", suggested)
        if chosen is None:
            return
        if chosen > date.today():
            messagebox.showwarning("Data futura", "Non è possibile acquisire risultati futuri.")
            return
        if messagebox.askyesno(
                "Conferma acquisizione",
                f"Scaricare i risultati del {chosen.isoformat()}?\\n"
                "Il file risultati.csv verrà sostituito, anche se la ricerca restituisce zero righe."):
            self.task([sys.executable, "getresults.py", "--date", chosen.isoformat()], self.refresh, audit_step="getresults", audit_day=chosen.isoformat(), audit_csv=ROOT / "data/input_risultati/risultati.csv")

    def run_append_results(self):
        path = ROOT / "data/input_risultati/risultati.csv"
        if not path.is_file():
            messagebox.showwarning("Input mancante", "Prima acquisisci i risultati: risultati.csv non esiste.")
            return
        rows = csv_rows(path)
        if not rows:
            messagebox.showwarning("Nessun risultato", "risultati.csv è vuoto: niente da registrare.")
            return
        days = sorted({r.get("MatchDate", r.get("Date", "")).strip() for r in rows})
        if messagebox.askyesno(
                "Conferma registrazione",
                f"Registrare {len(rows)} righe negli storici?\\n"
                f"Date rilevate: {', '.join(d for d in days if d) or 'non identificabili'}\\n"
                "Questa operazione aggiorna gli storici e i report."):
            self.task([sys.executable, "-m", "gioover25.append_results",
                       "data/input_risultati/risultati.csv"], self.refresh, audit_step="append_results", audit_csv=path)

    def run_ranking(self):
        if messagebox.askyesno("Genera ranking", "Eseguire il ranking per tutti gli engine sul partite.csv corrente, senza --erase?"):
            self.task([sys.executable, "-m", "gioover25.rank_matches_v2",
                       "data/input_partite/partite.csv", "--engine", "all"], self.refresh, audit_step="rank_matches", audit_csv=INPUT)

    def run_bands(self):
        self.task([sys.executable, "-m", "analysis.metrics.score_band_analysis"], self.refresh)


if __name__ == "__main__":
    Dashboard().mainloop()
