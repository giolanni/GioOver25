"""GioOver2.5 - experiment estensione v201dev.

FIX:
- supporta storici ranking che usano `Over25` come colonna esito;
- se non trova una colonna esito esplicita, prova a ricavarlo da HG + AG.

REGOLA ORIGINALE
v20=MEDIA-ALTA, Score_v20>=71, v22=ALTA, v25=ALTA.

OBIETTIVO
Cercare su TUTTE le partite comuni v20/v22/v25 altri segmenti ad altissima
precisione. Priorità: %OK, poi meno KO, poi numerosità.

PARAMETRI MODIFICABILI
V20_SCORE_THRESHOLDS = (60,65,67,69,71,73,75)
V20_SCORE_BUCKETS = ((0,60),(60,65),(65,67),(67,69),(69,71),(71,73),(73,75),(75,None))
MIN_SAMPLE_FOR_CANDIDATE = 10
EXCLUDE_AUSTRALIA_ALSO = True

ESECUZIONE
python -m analysis.experiments.v201dev_extension_experiment
"""
from pathlib import Path
import pandas as pd

ENGINES=("v20","v22","v25")
V20_SCORE_THRESHOLDS=(60,65,67,69,71,73,75)
V20_SCORE_BUCKETS=((0,60),(60,65),(65,67),(67,69),(69,71),(71,73),(73,75),(75,None))
MIN_SAMPLE_FOR_CANDIDATE=10
EXCLUDE_AUSTRALIA_ALSO=True
OUTPUT_DIR=Path("analysis/experiments/v201dev_extension")
ROOTS=(Path("data/storico/ranking"),Path("data/storico"),Path("data"))

# FIX: aggiunto Over25 / over25
OUTCOMES=(
    "Outcome","Esito","esito","Result","result","esito_bet",
    "Over25","over25"
)

BANDS=("Band","band","Fascia","fascia")
SCORES=("Score","score","Ranking","ranking")
DATES=("MatchDate","matchdate","Date","date")
LEAGUES=("LeagueId","leagueid","League","league")
HG_COLS=("HG","HomeGoals","home_goals","HomeScore")
AG_COLS=("AG","AwayGoals","away_goals","AwayScore")

def read(path):
    s=path.read_text(encoding="utf-8-sig",errors="replace")[:4096]
    sep=";" if s.count(";")>=s.count(",") else ","
    return pd.read_csv(path,sep=sep,dtype=str,encoding="utf-8-sig",low_memory=False)

def col(df,names,required=True):
    m={str(c).strip().casefold():c for c in df.columns}
    for n in names:
        if n.casefold() in m:
            return m[n.casefold()]
    if required:
        raise KeyError("Colonna assente: "+"/".join(names))
    return None

def find_history(engine):
    # Preferisce struttura canonica per-engine.
    canonical=Path("data/storico/ranking")/engine/f"storico_ranking_{engine}.csv"
    if canonical.exists():
        return canonical

    for root in ROOTS:
        p=root/f"storico_ranking_{engine}.csv"
        if p.exists():
            return p

    found=[]
    for root in ROOTS:
        if root.exists():
            found += [
                p for p in root.rglob(f"storico_ranking*{engine}*.csv")
                if "old" not in p.name.lower()
                and "bak" not in p.name.lower()
            ]

    if not found:
        raise FileNotFoundError(f"Storico {engine} non trovato")

    return sorted(found,key=lambda p:(len(p.name),str(p)))[0]

def norm(s):
    return s.fillna("").astype(str).str.strip()

def normalize_outcome(x):
    raw=str(x or "").strip().upper()

    if raw in ("OK","KO"):
        return raw

    if raw in ("1","TRUE","OVER","YES"):
        return "OK"

    if raw in ("0","FALSE","UNDER","NO"):
        return "KO"

    return ""

def derive_outcome_from_goals(df):
    hg_col=col(df,HG_COLS,required=False)
    ag_col=col(df,AG_COLS,required=False)

    if hg_col is None or ag_col is None:
        return pd.Series("",index=df.index,dtype=str)

    hg=pd.to_numeric(df[hg_col],errors="coerce")
    ag=pd.to_numeric(df[ag_col],errors="coerce")

    result=pd.Series("",index=df.index,dtype=str)
    valid=hg.notna() & ag.notna()

    result.loc[valid & ((hg+ag)>=3)]="OK"
    result.loc[valid & ((hg+ag)<3)]="KO"

    return result

def prepare(engine,path):
    d=read(path)

    lc=col(d,LEAGUES,False)
    dc=col(d,DATES,False)
    hc=col(d,("Home","home"))
    ac=col(d,("Away","away"))
    bc=col(d,BANDS)
    sc=col(d,SCORES)
    oc=col(d,OUTCOMES,required=False)

    x=pd.DataFrame(index=d.index)

    x["LeagueId"]=norm(d[lc]) if lc else ""
    x["MatchDate"]=norm(d[dc]) if dc else ""
    x["Home"]=norm(d[hc])
    x["Away"]=norm(d[ac])

    x[f"Band_{engine}"]=norm(d[bc]).str.upper()

    x[f"Score_{engine}"]=pd.to_numeric(
        norm(d[sc]).str.replace(",",".",regex=False),
        errors="coerce",
    )

    if oc is not None:
        outcome_series=d[oc].map(normalize_outcome)
    else:
        outcome_series=derive_outcome_from_goals(d)

    # Se la colonna esito esiste ma contiene celle vuote/non interpretabili,
    # prova comunque a completarle da HG/AG.
    fallback=derive_outcome_from_goals(d)
    outcome_series=outcome_series.where(
        outcome_series.isin(["OK","KO"]),
        fallback
    )

    x[f"Outcome_{engine}"]=outcome_series

    return x[
        x[f"Outcome_{engine}"].isin(["OK","KO"])
    ].copy()

def common_data():
    paths={e:find_history(e) for e in ENGINES}
    fs={e:prepare(e,paths[e]) for e in ENGINES}

    has_date=all(
        f["MatchDate"].astype(str).str.strip().ne("").any()
        for f in fs.values()
    )

    has_league=all(
        f["LeagueId"].astype(str).str.strip().ne("").any()
        for f in fs.values()
    )

    key=(
        ["LeagueId","MatchDate","Home","Away"]
        if has_date and has_league
        else ["LeagueId","Home","Away"]
        if has_league
        else ["Home","Away"]
    )

    for e in ENGINES:
        fs[e]["_Occurrence"]=fs[e].groupby(
            key,
            dropna=False
        ).cumcount()

    mk=key+["_Occurrence"]

    c=fs["v20"].copy()

    for e in ("v22","v25"):
        c=c.merge(
            fs[e][
                mk+[
                    f"Band_{e}",
                    f"Score_{e}",
                    f"Outcome_{e}",
                ]
            ],
            on=mk,
            how="inner",
            validate="one_to_one",
        )

    same=(
        (c.Outcome_v20==c.Outcome_v22)
        & (c.Outcome_v20==c.Outcome_v25)
    )

    discordant=int((~same).sum())

    if discordant:
        print(
            f"ATTENZIONE: {discordant} partite con esito discordante "
            "tra gli engine; escluse."
        )

    c=c[same].copy()
    c["Outcome"]=c["Outcome_v20"]

    summ=pd.DataFrame([
        {
            "Engine":e,
            "HistoryFile":str(paths[e]),
            "EvaluableRows":len(fs[e]),
            "CommonRows":len(c),
            "UnmatchedApprox":len(fs[e])-len(c),
            "MergeKey":" + ".join(mk),
        }
        for e in ENGINES
    ])

    return c.reset_index(drop=True),summ

def stats(d):
    ok=int((d.Outcome=="OK").sum())
    ko=int((d.Outcome=="KO").sum())
    n=ok+ko

    return {
        "OK":ok,
        "KO":ko,
        "Total":n,
        "HitRate":round(ok/n*100,4) if n else 0.0,
    }

def scenarios(c):
    yield "ALL",c

    if EXCLUDE_AUSTRALIA_ALSO:
        yield (
            "NO_AUSTRALIA",
            c[
                ~c.LeagueId
                .fillna("")
                .astype(str)
                .str.startswith("Australia_")
            ].copy()
        )

def bands(d,c):
    return sorted(
        v
        for v in d[c]
        .dropna()
        .astype(str)
        .str.strip()
        .unique()
        if v
    )

def grids(scenario,d):
    threshold=[]
    bucket=[]

    for b20 in bands(d,"Band_v20"):
        for b22 in bands(d,"Band_v22"):
            for b25 in bands(d,"Band_v25"):
                base=d[
                    (d.Band_v20==b20)
                    & (d.Band_v22==b22)
                    & (d.Band_v25==b25)
                ]

                if base.empty:
                    continue

                for t in V20_SCORE_THRESHOLDS:
                    q=base[base.Score_v20>=t]

                    if not q.empty:
                        r={
                            "Scenario":scenario,
                            "Band_v20":b20,
                            "Band_v22":b22,
                            "Band_v25":b25,
                            "ScoreRule":f">={t}",
                            "ScoreMin":t,
                            "ScoreMax":"",
                        }
                        r.update(stats(q))
                        threshold.append(r)

                for lo,hi in V20_SCORE_BUCKETS:
                    if hi is None:
                        q=base[base.Score_v20>=lo]
                        rule=f">={lo}"
                    else:
                        q=base[
                            (base.Score_v20>=lo)
                            & (base.Score_v20<hi)
                        ]
                        rule=f">={lo} AND <{hi}"

                    if not q.empty:
                        r={
                            "Scenario":scenario,
                            "Band_v20":b20,
                            "Band_v22":b22,
                            "Band_v25":b25,
                            "ScoreRule":rule,
                            "ScoreMin":lo,
                            "ScoreMax":"" if hi is None else hi,
                        }
                        r.update(stats(q))
                        bucket.append(r)

    return pd.DataFrame(threshold),pd.DataFrame(bucket)

def main():
    OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

    c,u=common_data()

    c.to_csv(
        OUTPUT_DIR/"07_common_matches.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    u.to_csv(
        OUTPUT_DIR/"08_unmatched_summary.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    bases=[]
    ts=[]
    bs=[]
    focuses=[]

    for scenario,d in scenarios(c):
        orig=d[
            (d.Band_v20=="MEDIA-ALTA")
            & (d.Score_v20>=71)
            & (d.Band_v22=="ALTA")
            & (d.Band_v25=="ALTA")
        ]

        r={
            "Scenario":scenario,
            "Rule":"v20=MEDIA-ALTA;Score>=71;v22=ALTA;v25=ALTA",
        }
        r.update(stats(orig))
        bases.append(r)

        t,b=grids(scenario,d)

        ts.append(t)
        bs.append(b)

        focus=pd.concat([t,b],ignore_index=True)

        focus=focus[
            (focus.Band_v22=="ALTA")
            & (focus.Band_v25=="ALTA")
        ].copy()

        focuses.append(focus)

    base=pd.DataFrame(bases)
    t=pd.concat(ts,ignore_index=True)
    b=pd.concat(bs,ignore_index=True)
    focus=pd.concat(focuses,ignore_index=True)

    base.to_csv(
        OUTPUT_DIR/"01_baseline_original_rule.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    t.to_csv(
        OUTPUT_DIR/"02_threshold_grid.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    b.to_csv(
        OUTPUT_DIR/"03_score_buckets.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    focus.sort_values(
        ["Scenario","HitRate","KO","Total"],
        ascending=[True,False,True,False],
    ).to_csv(
        OUTPUT_DIR/"04_consensus_v22_v25.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    allseg=pd.concat(
        [
            t.assign(AnalysisType="THRESHOLD"),
            b.assign(AnalysisType="BUCKET"),
        ],
        ignore_index=True,
    )

    cand=allseg[
        allseg.Total>=MIN_SAMPLE_FOR_CANDIDATE
    ].copy()

    cand["IsOriginalRule"]=(
        (cand.Band_v20=="MEDIA-ALTA")
        & (cand.Band_v22=="ALTA")
        & (cand.Band_v25=="ALTA")
        & (cand.AnalysisType=="THRESHOLD")
        & (cand.ScoreMin==71)
    )

    cand=cand.sort_values(
        ["Scenario","HitRate","KO","Total"],
        ascending=[True,False,True,False],
    )

    cand.to_csv(
        OUTPUT_DIR/"05_candidate_segments.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    cmp=cand.merge(
        base[
            ["Scenario","HitRate"]
        ].rename(
            columns={
                "HitRate":"OriginalRuleHitRate"
            }
        ),
        on="Scenario",
        how="left",
    )

    cmp["DeltaVsOriginalRule"]=(
        cmp.HitRate
        - cmp.OriginalRuleHitRate
    ).round(4)

    cmp["AtLeastAsPreciseAsOriginal"]=(
        cmp.DeltaVsOriginalRule>=0
    )

    cmp=cmp.sort_values(
        [
            "Scenario",
            "AtLeastAsPreciseAsOriginal",
            "HitRate",
            "KO",
            "Total",
        ],
        ascending=[
            True,
            False,
            False,
            True,
            False,
        ],
    )

    cmp.to_csv(
        OUTPUT_DIR/"06_candidate_segments_vs_original.csv",
        sep=";",
        index=False,
        encoding="utf-8-sig",
    )

    print(
        f"Partite comuni valutabili: {len(c)}"
    )
    print()
    print("Regola originale:")
    print(base.to_string(index=False))
    print()
    print(f"Output: {OUTPUT_DIR}")

if __name__=="__main__":
    main()
