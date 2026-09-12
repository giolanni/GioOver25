from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path

from analysis.experiments.match_history_features import build_feature_rows, write_csv

OUT = Path("analysis/experiments/output/v30_delta_ablation")


def _date(value):
    return date.fromisoformat(str(value).strip())


def _enrich(row):
    for suffix in ("Full", "L5", "L7"):
        row[f"MinGF{suffix}"] = min(
            float(row[f"HomeGF{suffix}"]), float(row[f"AwayGF{suffix}"])
        )
        row[f"MinOver{suffix}"] = min(
            float(row[f"HomeOverRate{suffix}"]),
            float(row[f"AwayOverRate{suffix}"]),
        )
        row[f"AvgOver{suffix}"] = (
            float(row[f"HomeOverRate{suffix}"])
            + float(row[f"AwayOverRate{suffix}"])
        ) / 2

    row["AvgGFFull"] = (
        float(row["HomeGFFull"]) + float(row["AwayGFFull"])
    ) / 2
    row["AvgGFL5"] = (
        float(row["HomeGFL5"]) + float(row["AwayGFL5"])
    ) / 2
    row["DeltaGFL5"] = row["AvgGFL5"] - row["AvgGFFull"]
    return row


RULES = (
    # Solo livello offensivo assoluto: nessun DeltaGF.
    ("GF14", lambda r: r["MinGFFull"] >= 1.4),
    ("GF16", lambda r: r["MinGFFull"] >= 1.6),
    ("GF18", lambda r: r["MinGFFull"] >= 1.8),
    ("GFL5_14", lambda r: r["MinGFL5"] >= 1.4),
    ("GFL5_16", lambda r: r["MinGFL5"] >= 1.6),
    ("GFL5_18", lambda r: r["MinGFL5"] >= 1.8),

    # Solo ambiente Over recente: nessun DeltaGF.
    ("OVERL5_60", lambda r: r["MinOverL5"] >= 0.60),
    ("OVERL5_70", lambda r: r["MinOverL5"] >= 0.70),
    ("OVERL7_70", lambda r: r["MinOverL7"] >= 0.70),

    # Livello assoluto + Over recente: test principale senza DeltaGF.
    ("GF14_OVERL5_70", lambda r: r["MinGFFull"] >= 1.4 and r["MinOverL5"] >= 0.70),
    ("GF16_OVERL5_70", lambda r: r["MinGFFull"] >= 1.6 and r["MinOverL5"] >= 0.70),
    ("GF18_OVERL5_70", lambda r: r["MinGFFull"] >= 1.8 and r["MinOverL5"] >= 0.70),
    ("GFL5_14_OVERL5_70", lambda r: r["MinGFL5"] >= 1.4 and r["MinOverL5"] >= 0.70),
    ("GFL5_16_OVERL5_70", lambda r: r["MinGFL5"] >= 1.6 and r["MinOverL5"] >= 0.70),
    ("GFL5_18_OVERL5_70", lambda r: r["MinGFL5"] >= 1.8 and r["MinOverL5"] >= 0.70),

    # Regole DeltaGF già emerse: confronto A/B diretto.
    ("OVERL5_70_DGF20", lambda r: r["MinOverL5"] >= 0.70 and r["DeltaGFL5"] >= 0.20),
    ("OVERL5_70_DGF30", lambda r: r["MinOverL5"] >= 0.70 and r["DeltaGFL5"] >= 0.30),

    # Livello assoluto + Over + Delta: misura il contributo marginale del Delta.
    ("GF14_OVERL5_70_DGF20", lambda r: r["MinGFFull"] >= 1.4 and r["MinOverL5"] >= 0.70 and r["DeltaGFL5"] >= 0.20),
    ("GF16_OVERL5_70_DGF20", lambda r: r["MinGFFull"] >= 1.6 and r["MinOverL5"] >= 0.70 and r["DeltaGFL5"] >= 0.20),
    ("GF14_OVERL5_70_DGF30", lambda r: r["MinGFFull"] >= 1.4 and r["MinOverL5"] >= 0.70 and r["DeltaGFL5"] >= 0.30),
    ("GF16_OVERL5_70_DGF30", lambda r: r["MinGFFull"] >= 1.6 and r["MinOverL5"] >= 0.70 and r["DeltaGFL5"] >= 0.30),
)


def _stats(rows):
    n = len(rows)
    ok = sum(int(r["Over25"]) for r in rows)
    return ok, n, (100.0 * ok / n if n else 0.0)


def main():
    rows = [
        _enrich(r)
        for r in build_feature_rows(min_history=5, windows=(5, 7, 8))
        if 7 <= int(r["MinPlayedBefore"]) <= 8
    ]

    baseline_ok, baseline_n, baseline_hit = _stats(rows)
    print(f"V30 ablation 7-8 | baseline {baseline_ok}/{baseline_n} = {baseline_hit:.2f}%")
    print("Confronto livello assoluto / Over recente / DeltaGF. Nessuna riottimizzazione mensile.\n")

    months = sorted({_date(r["MatchDate"]).strftime("%Y-%m") for r in rows})
    monthly_output = []
    summary = []

    for name, rule in RULES:
        selected_all = [r for r in rows if rule(r)]
        ok, n, hit = _stats(selected_all)
        lift = hit - baseline_hit
        positive = negative = 0
        month_parts = []

        for month in months:
            month_base = [
                r for r in rows
                if _date(r["MatchDate"]).strftime("%Y-%m") == month
            ]
            month_selected = [r for r in month_base if rule(r)]
            if not month_selected:
                continue

            mok, mn, mhit = _stats(month_selected)
            _, _, mbase = _stats(month_base)
            mlift = mhit - mbase
            positive += int(mlift > 0)
            negative += int(mlift < 0)
            month_parts.append(f"{month} {mok}/{mn}={mhit:.1f}%({mlift:+.1f})")
            monthly_output.append({
                "Rule": name,
                "Month": month,
                "OK": mok,
                "N": mn,
                "HitRate": round(mhit, 2),
                "Baseline": round(mbase, 2),
                "Lift": round(mlift, 2),
            })

        summary.append({
            "Rule": name,
            "OK": ok,
            "N": n,
            "HitRate": round(hit, 2),
            "Baseline": round(baseline_hit, 2),
            "Lift": round(lift, 2),
            "PositiveMonths": positive,
            "NegativeMonths": negative,
            "Months": len(month_parts),
        })

        print(
            f"{name}: {ok}/{n}={hit:.2f}% | lift {lift:+.2f} | "
            f"mesi + {positive}/{len(month_parts)}, - {negative}/{len(month_parts)}"
        )
        if month_parts:
            print("  " + " | ".join(month_parts))

    summary.sort(key=lambda x: (x["HitRate"], x["N"]), reverse=True)
    print("\nCLASSIFICA")
    for item in summary:
        print(
            f"  {item['Rule']}: {item['OK']}/{item['N']}={item['HitRate']:.2f}% "
            f"| lift {item['Lift']:+.2f} | mesi + {item['PositiveMonths']}/{item['Months']}"
        )

    write_csv(OUT / "monthly.csv", monthly_output)
    write_csv(OUT / "summary.csv", summary)
    print("\nOutput:", OUT / "summary.csv")


if __name__ == "__main__":
    main()
