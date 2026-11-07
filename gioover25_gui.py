"""GioOver2.5 desktop dashboard. Launch: python gioover25_gui.py"""
from __future__ import annotations

import csv
import subprocess
import sys
import threading
import tkinter as tk
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import messagebox, ttk

from gioover25.live import (
    DEFAULT_LIVE_CSV,
    OUTCOME_KO,
    OUTCOME_OK,
    OUTCOME_UNAVAILABLE,
    OUTCOME_WAITING,
    evaluate_market,
    freshness,
    load_engine_rankings,
    match_rankings,
    read_live_csv,
    refresh_live_csv,
    summarize_engine,
)


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data/input_partite/partite.csv"
HISTORY = ROOT / "data/storico/ranking"
OUTPUT = ROOT / "data/output_ranking"
BANDS = ROOT / "data/analysis/score_bands/score_band_best.csv"
LIVE_CSV = ROOT / "data/live/partite_live.csv"
NAVY, BLUE, BG, WHITE = "#122c4a", "#1769d2", "#eef3fa", "#ffffff"


def csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream, delimiter=";"))


def git(*args: str) -> tuple[int, str]:
    process = subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True,
        encoding="utf-8", errors="replace", timeout=45, check=False,
    )
    return process.returncode, (process.stdout + "\n" + process.stderr).strip()


def best_bands() -> dict[str, tuple[float, float, str, str, str]]:
    output = {}
    for row in csv_rows(BANDS):
        if (row.get("Scope"), row.get("Period"), row.get("Type")) != ("ALL", "HISTORY", "INTERVAL"):
            continue
        band = row.get("ScoreRange", "")
        try:
            left, right = band.strip("[]()").split(",")
            output[row["Engine"].lower()] = (
                float(left), float(right), band, row.get("HitRate", ""), row.get("Total", "")
            )
        except (ValueError, KeyError):
            continue
    return output


def _pct(value: float | None) -> str:
    return "n/d" if value is None else f"{value:.1f}%"


def _display_update(value: str) -> str:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%H:%M:%S")
    except ValueError:
        return value or "–"


class Dashboard(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("GioOver2.5 | Centro di controllo")
        self.geometry("1380x850")
        self.minsize(1100, 680)
        self.configure(bg=BG)
        self.busy = False
        self.live_refreshing = False
        self.live_job: str | None = None
        self.current_view = "rankings"
        self.engine = tk.StringVar(value="v20")
        self.only_best = tk.BooleanVar(value=False)
        self.live_auto = tk.BooleanVar(value=True)
        self.live_interval = tk.IntVar(value=60)
        self.status = tk.StringVar(value="Pronto")
        self.page_title = tk.StringVar(value="Centro di controllo")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.build()
        self.refresh()
        self.queue_live_refresh(1200)

    def build(self) -> None:
        sidebar = tk.Frame(self, bg=NAVY, width=215)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(
            sidebar, text="⚽ GioOver2.5", bg=NAVY, fg=WHITE,
            font=("Segoe UI", 19, "bold"),
        ).pack(pady=(25, 30))
        buttons = (
            ("Home", self.refresh),
            ("Ranking giornalieri", self.show_rankings),
            ("LIVE", self.show_live),
            ("Analisi fasce Score", self.show_bands),
            ("Aggiorna repository", self.update_repo),
            ("Genera ranking", self.run_ranking),
            ("Aggiorna fasce", self.run_bands),
        )
        for label, action in buttons:
            tk.Button(
                sidebar, text=label, command=action, bg=NAVY, fg=WHITE,
                activebackground=BLUE, activeforeground=WHITE,
                relief="flat", anchor="w", padx=18, pady=12,
                font=("Segoe UI", 11),
            ).pack(fill="x", padx=8, pady=2)

        main = tk.Frame(self, bg=BG)
        main.pack(side="left", fill="both", expand=True)
        tk.Label(
            main, textvariable=self.page_title, bg=BG, fg=NAVY,
            font=("Segoe UI", 23, "bold"),
        ).pack(anchor="w", padx=22, pady=(18, 12))

        self.summary = tk.Frame(main, bg=BG)
        self.summary.pack(fill="x", padx=20)
        self.controls = tk.Frame(main, bg=BG)
        self.controls.pack(fill="x", padx=20, pady=(12, 5))
        tk.Label(self.controls, text="Engine:", bg=BG).pack(side="left")
        self.engine_box = ttk.Combobox(
            self.controls, textvariable=self.engine, width=19, state="readonly"
        )
        self.engine_box.pack(side="left", padx=8)
        self.engine_box.bind("<<ComboboxSelected>>", lambda _event: self.render_current())
        ttk.Checkbutton(
            self.controls, text="Solo fascia migliore", variable=self.only_best,
            command=self.render_current,
        ).pack(side="left", padx=(4, 14))

        tk.Label(self.controls, text="LIVE:", bg=BG).pack(side="left", padx=(4, 2))
        ttk.Checkbutton(
            self.controls, text="Auto", variable=self.live_auto,
            command=self.toggle_live_auto,
        ).pack(side="left")
        self.interval_spin = tk.Spinbox(
            self.controls, from_=15, to=3600, increment=15,
            textvariable=self.live_interval, width=5,
        )
        self.interval_spin.pack(side="left", padx=(4, 2))
        self.interval_spin.bind("<Return>", lambda _event: self.apply_live_interval())
        self.interval_spin.bind("<FocusOut>", lambda _event: self.apply_live_interval())
        tk.Label(self.controls, text="s", bg=BG).pack(side="left")
        ttk.Button(
            self.controls, text="Aggiorna LIVE", command=lambda: self.refresh_live(manual=True)
        ).pack(side="left", padx=8)
        ttk.Button(self.controls, text="Ricarica", command=self.render_current).pack(side="right")

        self.table = ttk.Treeview(main, show="headings", height=17)
        self.table.tag_configure("best", background="#dcf6df")
        self.table.tag_configure(OUTCOME_OK, background="#d8f3dc", foreground="#155724")
        self.table.tag_configure(OUTCOME_KO, background="#ffd9d9", foreground="#8a1c1c")
        self.table.tag_configure(OUTCOME_WAITING, background="#fff3bf", foreground="#6a5400")
        self.table.tag_configure(OUTCOME_UNAVAILABLE, background="#e4e7eb", foreground="#59636e")
        self.table.pack(fill="both", expand=True, padx=20, pady=8)
        tk.Label(main, textvariable=self.status, bg=BG, fg=NAVY, anchor="w").pack(
            fill="x", padx=20
        )
        self.log = tk.Text(
            main, height=7, bg="#142b46", fg="#e7f1ff",
            font=("Consolas", 9), state="disabled",
        )
        self.log.pack(fill="x", padx=20, pady=(6, 15))

    def configure_table(self, definitions: tuple[tuple[str, str, int, str], ...]) -> None:
        columns = tuple(item[0] for item in definitions)
        self.table.configure(columns=columns, displaycolumns=columns)
        for column, title, width, anchor in definitions:
            self.table.heading(column, text=title)
            self.table.column(column, width=width, anchor=anchor, stretch=True)

    def clear_table(self) -> None:
        for item in self.table.get_children():
            self.table.delete(item)

    def write_log(self, text: str) -> None:
        self.log.configure(state="normal")
        self.log.insert("end", f"[{datetime.now():%H:%M:%S}] {text}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def card(self, title: str, value: str, note: str = "") -> None:
        frame = tk.Frame(self.summary, bg=WHITE, highlightbackground="#c9d7e7", highlightthickness=1)
        frame.pack(side="left", fill="both", expand=True, padx=4)
        tk.Label(frame, text=title, bg=WHITE, fg=NAVY, font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=12, pady=(10, 2)
        )
        tk.Label(
            frame, text=value, bg=WHITE, fg=BLUE, font=("Segoe UI", 13, "bold"),
            wraplength=240, justify="left",
        ).pack(anchor="w", padx=12)
        tk.Label(
            frame, text=note, bg=WHITE, fg="#57677b", font=("Segoe UI", 9),
            wraplength=240, justify="left",
        ).pack(anchor="w", padx=12, pady=(2, 10))

    def clear_cards(self) -> None:
        for child in self.summary.winfo_children():
            child.destroy()

    def home_cards(self) -> None:
        self.clear_cards()
        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        fixtures = csv_rows(INPUT)
        today_rows = [row for row in fixtures if row.get("MatchDate", "").strip() == today]
        self.card(
            "Partite di oggi", f"{len(today_rows)} presenti" if today_rows else "Da verificare",
            "Input odierno presente" if today_rows else "Nessuna partita con MatchDate odierna",
        )
        unresolved = resolved = 0
        engines = sorted(path.parent.name for path in HISTORY.glob("*/storico_ranking_*.csv"))
        for path in HISTORY.glob("*/storico_ranking_*.csv"):
            for row in csv_rows(path):
                if row.get("MatchDate", "").strip() != yesterday:
                    continue
                if row.get("Over25", "").upper() in ("OK", "KO") or row.get("BTTS", "").upper() in ("OK", "KO"):
                    resolved += 1
                else:
                    unresolved += 1
        self.card("Esiti di ieri", f"{resolved} risolti", f"{unresolved} righe non risolte negli storici engine")
        self.card("Ranking / engine", f"{len(engines)} storici", "Seleziona un engine per il dettaglio")
        self.card("Fasce Score", "Disponibili" if BANDS.exists() else "Da generare", f"CSV: {BANDS.name}")

    def refresh(self) -> None:
        engines = sorted(path.parent.name for path in HISTORY.glob("*/storico_ranking_*.csv"))
        self.engine_box["values"] = engines
        if engines and self.engine.get() not in engines:
            self.engine.set(engines[0])
        self.home_cards()
        self.show_rankings(update_cards=False)
        self.check_git()

    def check_git(self) -> None:
        def work() -> None:
            rc, status = git("status", "--porcelain")
            rc2, branch = git("branch", "--show-current")
            message = f"Repository: {branch.strip()} | " + (
                "modifiche locali presenti" if status else "working tree pulito"
            )
            if rc or rc2:
                message = "Git non disponibile o repository non accessibile"
            self.after(0, self.write_log, message)
        threading.Thread(target=work, daemon=True).start()

    def render_current(self) -> None:
        if self.current_view == "live":
            self.show_live()
        elif self.current_view == "bands":
            self.show_bands()
        else:
            self.show_rankings()

    def show_rankings(self, update_cards: bool = True) -> None:
        self.current_view = "rankings"
        self.page_title.set("Ranking giornalieri")
        if update_cards:
            self.home_cards()
        self.configure_table((
            ("date", "Data", 105, "w"),
            ("league", "Campionato", 220, "w"),
            ("match", "Partita", 320, "w"),
            ("score", "Score", 75, "center"),
            ("band", "Fascia", 120, "center"),
            ("best", "Indicatore", 160, "center"),
        ))
        self.clear_table()
        engine = self.engine.get()
        path = HISTORY / engine / f"storico_ranking_{engine}.csv"
        best = best_bands().get(engine.lower())
        today = date.today().isoformat()
        rows = [row for row in csv_rows(path) if row.get("MatchDate", "").strip() == today]
        shown = 0
        for row in rows:
            try:
                score = float(row.get("Score", "").replace(",", "."))
            except ValueError:
                continue
            marked = bool(best and best[0] <= score <= best[1] and (score < best[1] or best[1] == 100))
            if self.only_best.get() and not marked:
                continue
            self.table.insert(
                "", "end",
                values=(
                    today, row.get("LeagueId", ""),
                    f"{row.get('Home', '')} – {row.get('Away', '')}", f"{score:g}",
                    row.get("Band", ""), "★ Fascia migliore" if marked else "",
                ),
                tags=("best",) if marked else (),
            )
            shown += 1
        self.status.set(
            f"{engine}: {shown} pronostici odierni visualizzati; "
            f"fascia migliore: {best[2] if best else 'non disponibile'}"
        )

    def show_bands(self) -> None:
        self.current_view = "bands"
        self.page_title.set("Analisi fasce Score")
        self.home_cards()
        self.configure_table((
            ("empty", "", 80, "w"),
            ("range", "Intervallo", 180, "w"),
            ("outcomes", "Esiti", 300, "w"),
            ("rate", "Hit rate", 110, "center"),
            ("total", "Campione", 110, "center"),
            ("quality", "Qualità campione", 210, "w"),
        ))
        self.clear_table()
        engine = self.engine.get()
        rows = [
            row for row in csv_rows(ROOT / "data/analysis/score_bands/score_band_details.csv")
            if row.get("Engine") == engine and row.get("Scope") == "ALL"
            and row.get("Period") == "HISTORY" and row.get("Type") == "INTERVAL"
        ]
        for row in rows:
            self.table.insert(
                "", "end",
                values=(
                    "", row.get("ScoreRange", ""),
                    f"OK {row.get('OK')} / KO {row.get('KO')}",
                    row.get("HitRate", "") + "%", row.get("Total", ""),
                    "Campione sufficiente" if row.get("SufficientSample") == "YES" else "Campione ridotto",
                ),
            )
        self.status.set(f"Fasce Score di {engine}, ordinate per percentuale decrescente")

    def show_live(self) -> None:
        self.current_view = "live"
        self.page_title.set("Monitor LIVE")
        self.configure_table((
            ("engine", "Engine", 95, "center"),
            ("league", "Campionato", 190, "w"),
            ("match", "Partita", 285, "w"),
            ("score", "Punteggio", 85, "center"),
            ("phase", "Stato", 105, "center"),
            ("market", "Mercato", 100, "center"),
            ("outcome", "Esito LIVE", 115, "center"),
            ("updated", "Aggiornato", 145, "center"),
        ))
        self.clear_table()
        today = date.today().isoformat()
        engine = self.engine.get()
        try:
            live_matches = read_live_csv(LIVE_CSV)
        except Exception as exc:
            live_matches = []
            self.write_log(f"CSV LIVE non leggibile: {exc}")
        live_matches = [row for row in live_matches if row.match_date == today]
        rankings = load_engine_rankings(HISTORY, today, engine).get(engine, [])
        if self.only_best.get():
            best = best_bands().get(engine.lower())
            if best:
                filtered = []
                for row in rankings:
                    try:
                        score = float(row.get("Score", "").replace(",", "."))
                    except ValueError:
                        continue
                    if best[0] <= score <= best[1] and (score < best[1] or best[1] == 100):
                        filtered.append(row)
                rankings = filtered
            else:
                rankings = []
        matched = match_rankings(rankings, live_matches)
        for ranking, live in matched:
            score = "–" if live is None or live.hg is None or live.ag is None else f"{live.hg}-{live.ag}"
            phase = "Non disponibile" if live is None else (
                f"{live.status} {live.minute}".strip()
            )
            updated = "–" if live is None else _display_update(live.last_update)
            for market, label in (("Over2.5", "Over 2.5"), ("BTTS", "BTTS")):
                outcome = evaluate_market(live, market)
                outcome_label = {
                    OUTCOME_OK: "OK",
                    OUTCOME_KO: "KO",
                    OUTCOME_WAITING: "IN ATTESA",
                    OUTCOME_UNAVAILABLE: "N/D",
                }[outcome]
                self.table.insert(
                    "", "end",
                    values=(
                        engine, ranking.get("LeagueId", ""),
                        f"{ranking.get('Home', '')} – {ranking.get('Away', '')}",
                        score, phase, label, outcome_label, updated,
                    ),
                    tags=(outcome,),
                )

        summary = summarize_engine(engine, matched)
        stale_after = max(180, self.safe_interval() * 3)
        live_freshness = freshness(live_matches, LIVE_CSV, stale_after=stale_after)
        self.clear_cards()
        freshness_note = (
            "Nessun CSV LIVE disponibile" if live_freshness.state == "UNAVAILABLE"
            else f"eta {int(live_freshness.age_seconds or 0)} s · soglia {stale_after} s"
        )
        self.card("Dato LIVE", live_freshness.state, freshness_note)
        self.card("Partite feed", str(len(live_matches)), f"Ranking associati: {sum(live is not None for _, live in matched)}/{len(matched)}")
        self.card(
            "Over 2.5 · finali", _pct(summary.over_pct),
            f"{summary.over_ok} OK su {summary.over_total} finali valutabili",
        )
        self.card(
            "BTTS · finali", _pct(summary.btts_pct),
            f"{summary.btts_ok} OK su {summary.btts_total} finali valutabili",
        )
        stale_marker = " · DATO STALE" if live_freshness.state == "STALE" else ""
        self.status.set(
            f"{engine}: {len(rankings)} ranking · {summary.final_matches} partite finali; "
            f"percentuali calcolate esclusivamente sui finali{stale_marker}"
        )

    def safe_interval(self) -> int:
        try:
            return min(3600, max(15, int(self.live_interval.get())))
        except (tk.TclError, ValueError):
            return 60

    def apply_live_interval(self) -> None:
        interval = self.safe_interval()
        self.live_interval.set(interval)
        if self.live_auto.get():
            self.queue_live_refresh(interval * 1000)

    def toggle_live_auto(self) -> None:
        if self.live_auto.get():
            self.queue_live_refresh(0)
        elif self.live_job is not None:
            self.after_cancel(self.live_job)
            self.live_job = None
            self.write_log("Aggiornamento LIVE automatico disattivato")

    def queue_live_refresh(self, delay_ms: int | None = None) -> None:
        if self.live_job is not None:
            self.after_cancel(self.live_job)
            self.live_job = None
        if not self.live_auto.get():
            return
        delay = self.safe_interval() * 1000 if delay_ms is None else delay_ms
        self.live_job = self.after(delay, lambda: self.refresh_live(manual=False))

    def refresh_live(self, manual: bool = False) -> None:
        self.live_job = None
        if self.live_refreshing:
            if manual:
                self.write_log("Aggiornamento LIVE gia' in corso")
            return
        self.live_refreshing = True
        self.status.set("Aggiornamento LIVE in corso...")

        def work() -> None:
            report = None
            error = None
            try:
                report = refresh_live_csv(LIVE_CSV)
            except Exception as exc:
                error = exc
            self.after(0, self.live_finished, report, error, manual)

        threading.Thread(target=work, daemon=True).start()

    def live_finished(self, report, error: Exception | None, manual: bool) -> None:
        self.live_refreshing = False
        if error is not None:
            self.write_log(f"LIVE non aggiornato; conservato il CSV precedente: {error}")
            self.status.set("Aggiornamento LIVE non riuscito: dato precedente conservato")
            if manual:
                messagebox.showerror("LIVE", f"Aggiornamento non riuscito.\n{error}")
        else:
            warning = f", {len(report.errors)} feed parziali" if report.errors else ""
            self.write_log(f"LIVE aggiornato: {len(report.matches)} partite{warning}")
            if self.current_view == "live":
                self.show_live()
            else:
                self.status.set(f"LIVE aggiornato: {len(report.matches)} partite")
        if self.live_auto.get():
            self.queue_live_refresh()

    def task(self, command: list[str], on_done=None) -> None:
        if self.busy:
            messagebox.showwarning("Operazione in corso", "Attendere la conclusione dell'operazione precedente.")
            return
        self.busy = True
        self.status.set("Operazione in corso...")

        def work() -> None:
            try:
                process = subprocess.Popen(
                    command, cwd=ROOT, stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True,
                    encoding="utf-8", errors="replace", bufsize=1,
                )
                if process.stdout:
                    for line in process.stdout:
                        self.after(0, self.write_log, line.rstrip())
                return_code = process.wait()

                def done() -> None:
                    self.busy = False
                    self.status.set(f"Comando terminato (codice {return_code})")
                    if return_code == 0 and on_done:
                        on_done()
                    elif return_code:
                        messagebox.showerror("Errore", f"Comando terminato con codice {return_code}. Consultare il log.")
                self.after(0, done)
            except Exception as exc:
                def failed() -> None:
                    self.busy = False
                    self.write_log(str(exc))
                    messagebox.showerror("Errore", str(exc))
                self.after(0, failed)
        threading.Thread(target=work, daemon=True).start()

    def update_repo(self) -> None:
        if self.busy:
            return
        return_code, changes = git("status", "--porcelain")
        if return_code:
            messagebox.showerror("Git", changes)
            return
        if changes:
            messagebox.showwarning(
                "Modifiche locali",
                "Aggiornamento bloccato: sono presenti modifiche locali. Nessun file sara' sovrascritto.",
            )
            return
        if messagebox.askyesno("Aggiorna repository", "Eseguire git pull --ff-only sul branch corrente?"):
            self.task(["git", "pull", "--ff-only"], self.refresh)

    def run_ranking(self) -> None:
        if messagebox.askyesno("Genera ranking", "Eseguire il ranking per tutti gli engine senza --erase?"):
            self.task(
                [sys.executable, "-m", "gioover25.rank_matches_v2", "data/input_partite/partite.csv", "--engine", "all"],
                self.refresh,
            )

    def run_bands(self) -> None:
        self.task([sys.executable, "-m", "analysis.metrics.score_band_analysis"], self.refresh)

    def on_close(self) -> None:
        if self.live_job is not None:
            self.after_cancel(self.live_job)
            self.live_job = None
        self.destroy()


if __name__ == "__main__":
    Dashboard().mainloop()
