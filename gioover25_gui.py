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
from gioover25 import missing_results as missing_audit
from tools.prepare_input import norm, canonical_team
from datetime import timezone

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data/input_partite/partite.csv"
HISTORY = ROOT / "data/storico/ranking"
OUTPUT = ROOT / "data/output_ranking"
GROUP_REGISTRY = ROOT / 'docs/league_group_registry.csv'
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
        self.engine = tk.StringVar(value="v20")
        self.only_best = tk.BooleanVar(value=False)
        self.status = tk.StringVar(value="Pronto")
        self.view = "rankings"
        self.live_poll_busy = False
        self.alert_rows = []
        self.build()
        self.refresh()

    def build(self):
        sidebar = tk.Frame(self, bg=NAVY, width=215)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="⚽ GioOver2.5", bg=NAVY, fg=WHITE,
                 font=("Segoe UI", 19, "bold")).pack(pady=(25, 30))
        for label, action in [("Home", self.refresh), ("Avvisi e anomalie", self.show_alerts), ("Ranking giornalieri", self.show_rankings),
                              ("Analisi fasce Score", self.show_bands), ("Monitor LIVE", self.open_live), ("Aggiorna repository", self.update_repo),
                              ("Genera ranking", self.run_ranking), ("Aggiorna fasce", self.run_bands)]:
            tk.Button(sidebar, text=label, command=action, bg=NAVY, fg=WHITE,
                      activebackground=BLUE, activeforeground=WHITE,
                      relief="flat", anchor="w", padx=18, pady=12,
                      font=("Segoe UI", 11)).pack(fill="x", padx=8, pady=2)
        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        tk.Label(main, text="Centro di controllo", bg=BG, fg=NAVY,
                 font=("Segoe UI", 23, "bold")).pack(anchor="w", padx=22, pady=(18, 12))
        self.summary = tk.Frame(main, bg=BG)
        self.summary.pack(fill="x", padx=20)
        self.controls = tk.Frame(main, bg=BG)
        self.controls.pack(fill="x", padx=20, pady=(12, 5))
        tk.Label(self.controls, text="Engine:", bg=BG).pack(side="left")
        self.engine_box = ttk.Combobox(self.controls, textvariable=self.engine, width=20, state="readonly")
        self.engine_box.pack(side="left", padx=8)
        self.engine_box.bind("<<ComboboxSelected>>", lambda _: self.show_live() if self.view == "live" else self.show_rankings())
        ttk.Checkbutton(self.controls, text="Solo fascia migliore", variable=self.only_best,
                        command=self.show_rankings).pack(side="left", padx=10)
        ttk.Button(self.controls, text="Aggiorna LIVE", command=self.refresh_live).pack(side="right", padx=5)
        ttk.Button(self.controls, text="Ricarica", command=self.refresh).pack(side="right")
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
        tk.Label(main, textvariable=self.status, bg=BG, fg=NAVY,
                 anchor="w").pack(fill="x", padx=20)
        self.log = tk.Text(main, height=7, bg="#142b46", fg="#e7f1ff",
                           font=("Consolas", 9), state="disabled")
        self.log.pack(fill="x", padx=20, pady=(6, 15))

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

    def show_alerts(self):
        self.view = "alerts"
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
        for child in self.summary.winfo_children():
            child.destroy()
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        fixtures = csv_rows(INPUT)
        today_rows = [r for r in fixtures if r.get("MatchDate", "").strip() == today]
        self.card("Partite di oggi", f"{len(today_rows)} presenti" if today_rows else "Da verificare",
                  "Input odierno presente" if today_rows else "Nessuna partita con MatchDate odierna")
        unresolved, resolved = 0, 0
        engines = sorted(p.parent.name for p in HISTORY.glob("*/storico_ranking_*.csv"))
        for path in HISTORY.glob("*/storico_ranking_*.csv"):
            for r in csv_rows(path):
                if r.get("MatchDate", "").strip() != yesterday:
                    continue
                if r.get("Over25", "").upper() in ("OK", "KO") or r.get("BTTS", "").upper() in ("OK", "KO"):
                    resolved += 1
                else:
                    unresolved += 1
        self.card("Esiti di ieri", f"{resolved} risolti", f"{unresolved} righe non risolte negli storici engine")
        try:
            self.alert_rows = self.collect_alerts()
            missing = sum(1 for r in self.alert_rows if r[3] == "SCHEDULED")
            postponed = sum(1 for r in self.alert_rows if r[3] == "POSTPONED")
            maps = sum(1 for r in self.alert_rows if r[3].startswith("MAPPA"))
            self.card("Avvisi", f"{missing} da recuperare",
                      f"{postponed} rinviate | {maps} mappe (clicca Avvisi e anomalie)")
        except (OSError, ValueError, KeyError) as exc:
            self.alert_rows = []
            self.card("Avvisi", "Errore controllo", str(exc)[:100])
            self.write_log("Controllo avvisi: " + str(exc))
        self.card("Ranking / engine", str(len(engines)) + " storici",
                  "Controllo generazione disponibile nella tabella")
        self.card("Fasce Score", "Disponibili" if BANDS.exists() else "Da generare",
                  f"CSV: {BANDS.name}")
        self.engine_box["values"] = engines
        if engines and self.engine.get() not in engines:
            self.engine.set(engines[0])
        self.status.set("Controlli locali completati. La presenza dei dati non certifica la completezza del download.")
        if self.view == "live":
            self.show_live()
        elif self.view == "alerts":
            self.show_alerts()
        else:
            self.show_rankings()
        self.check_git()

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
        self.view = "live"
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
        market = "BTTS" if engine.lower().startswith("vg") else "Over25"
        normalized_live = {
            (lid, day, norm(canonical_team(home)), norm(canonical_team(away))): item
            for (lid, day, home, away), item in live.items()
        }
        for r in rows:
            key = (r.get("LeagueId", "").strip().casefold(), today,
                   norm(canonical_team(r.get("Home", ""))),
                   norm(canonical_team(r.get("Away", ""))))
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
            self.table.insert("", "end",
                values=(today, r.get("LeagueId", ""),
                        r.get("Home", "") + " – " + r.get("Away", ""),
                        r.get("Score", ""), r.get("Band", ""), minute, score, outcome),
                tags=(outcome.lower(),))
        total = sum(finals.values())
        rate = f"{100 * finals['OK'] / total:.1f}%" if total else "n.d."
        self.status.set(
            f"LIVE {engine}: OK {counts['OK']} | KO {counts['KO']} | "
            f"In attesa {counts['PENDING']} | Senza dati {counts['UNKNOWN']} | "
            f"Finali {finals['OK']}/{total} ({rate}). "
            "Fonte: Diretta, aggiornamento manuale.")

    def show_rankings(self):
        self.view = "rankings"
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

    def show_bands(self):
        self.view = "bands"
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

    def task(self, command, on_done=None):
        if self.busy:
            messagebox.showwarning("Operazione in corso", "Attendere la conclusione dell'operazione precedente.")
            return
        self.busy = True
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
                    self.status.set(f"Comando terminato (codice {rc})")
                    if rc == 0 and on_done:
                        on_done()
                    elif rc:
                        messagebox.showerror("Errore", f"Comando terminato con codice {rc}. Consultare il log.")
                self.after(0, done)
            except Exception as exc:
                def failed():
                    self.busy = False
                    self.write_log(str(exc))
                    messagebox.showerror("Errore", str(exc))
                self.after(0, failed)
        threading.Thread(target=work, daemon=True).start()

    def git_sequence(self, commands):
        """Run Git commands sequentially; stop on first failure."""
        if self.busy:
            return
        self.busy = True
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
                            self.status.set("Git interrotto: " + " ".join(args))
                            messagebox.showerror("Git", "Comando fallito: git " +
                                " ".join(args) + f" (codice {rc}). Verificare il log. "
                                "I comandi successivi non sono stati eseguiti.")
                        self.after(0, fail)
                        return
                except Exception as exc:
                    def fail_exception(error=str(exc)):
                        self.busy = False
                        self.status.set("Errore Git")
                        messagebox.showerror("Git", error)
                    self.after(0, fail_exception)
                    return
            def done():
                self.busy = False
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

    def run_ranking(self):
        if messagebox.askyesno("Genera ranking", "Eseguire il ranking per tutti gli engine senza --erase?"):
            self.task([sys.executable, "-m", "gioover25.rank_matches_v2",
                       "data/input_partite/partite.csv", "--engine", "all"], self.refresh)

    def run_bands(self):
        self.task([sys.executable, "-m", "analysis.metrics.score_band_analysis"], self.refresh)


if __name__ == "__main__":
    Dashboard().mainloop()
