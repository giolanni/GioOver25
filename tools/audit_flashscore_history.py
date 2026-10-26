"""Audit dry-run di uno storico GioOver contro una pagina risultati Flashscore."""
from __future__ import annotations
import argparse
from pathlib import Path
from tools.flashscore_history import fetch_embedded_results
from tools.bonifica_storici_diretta import load_local, key, team_overlap, Result, ROOT

RESULTS_DIR = ROOT / "data" / "storico" / "risultati"

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--league-id", required=True)
    ap.add_argument("--league-url", required=True)
    ap.add_argument("--local-file")
    ap.add_argument("--timeout", type=int, default=20)
    args = ap.parse_args()

    path = Path(args.local_file) if args.local_file else RESULTS_DIR / f"{args.league_id}.csv"
    if not path.is_absolute():
        path = ROOT / path
    if not path.exists():
        print(f"[LOCAL] NOT_FOUND {path}")
        print("[DRY-RUN] Nessuna modifica a registry o storici.")
        return

    _raw, local = load_local(path)
    ids, fs_rows, _payload = fetch_embedded_results(args.league_url, args.timeout)
    remote = [Result(x.date, x.home, x.away, x.hg, x.ag, x.round) for x in fs_rows]

    print(f"[FLASH] template={ids.get('template_id') or 'NOT_FOUND'} tournament={ids.get('tournament_id') or 'NOT_FOUND'} stage={ids.get('stage_id') or 'NOT_FOUND'}")
    print(f"[COUNT] local={len(local)} remote_embedded={len(remote)}")

    overlap, union = team_overlap(args.league_id, local, remote)
    ratio = overlap / union if union else 0.0
    print(f"[TEAMS] overlap={overlap}/{union} ratio={ratio:.3f}")

    lk = {key(args.league_id, r): r for r in local}
    rk = {key(args.league_id, r): r for r in remote}
    common = sorted(lk.keys() & rk.keys())
    missing_local = sorted(rk.keys() - lk.keys())
    extra_local = sorted(lk.keys() - rk.keys())
    score_diff = [k for k in common if (lk[k].hg, lk[k].ag) != (rk[k].hg, rk[k].ag)]

    print(f"[AUDIT] EQUAL={len(common)-len(score_diff)} MISSING_LOCAL={len(missing_local)} EXTRA_LOCAL={len(extra_local)} SCORE_DIFF={len(score_diff)}")
    for label, keys, source in (
        ("MISSING_LOCAL", missing_local, rk),
        ("EXTRA_LOCAL", extra_local, lk),
        ("SCORE_DIFF", score_diff, rk),
    ):
        for k in keys[:20]:
            r = source[k]
            if label == "SCORE_DIFF":
                old = lk[k]
                print(f"[{label}] {r.date};{r.home};{r.away}; local={old.hg}-{old.ag}; flash={r.hg}-{r.ag}")
            else:
                print(f"[{label}] {r.date};{r.home};{r.away};{r.hg}-{r.ag}")
    print("[DRY-RUN] Nessuna modifica a registry o storici.")

if __name__ == "__main__":
    main()
