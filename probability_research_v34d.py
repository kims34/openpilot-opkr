"""Robustness audit for the frozen SCHD v3.4c challenger (ridge=10, blend=.15)."""
import json, time
import numpy as np
import next_day_probability as data
from probability_model_v33_runtime import estimate_prices as v33
import probability_research_v34c as c

SYMBOL="SCHD"
BLEND=0.15
BLOCK=20
BOOT=5000


def gain_stats(diff):
    n=len(diff)
    quarters=[]
    for k in range(4):
        a=k*n//4; b=(k+1)*n//4
        quarters.append(float(np.mean(diff[a:b])))
    blocks=[]
    for a in range(0,n,126):
        b=min(n,a+126)
        if b-a>=60: blocks.append(float(np.mean(diff[a:b])))
    rng=np.random.default_rng(20260927)
    boots=[]
    need=int(np.ceil(n/BLOCK))
    max_start=max(1,n-BLOCK+1)
    for _ in range(BOOT):
        starts=rng.integers(0,max_start,size=need)
        sample=np.concatenate([diff[s:s+BLOCK] for s in starts])[:n]
        boots.append(float(np.mean(sample)))
    lo,med,hi=np.quantile(boots,[.025,.5,.975])
    return {
        "full_gain":float(np.mean(diff)),
        "quarter_gains":quarters,
        "positive_quarters":int(sum(x>0 for x in quarters)),
        "block126_gains":blocks,
        "positive_126_blocks":int(sum(x>0 for x in blocks)),
        "total_126_blocks":len(blocks),
        "bootstrap95":[float(lo),float(med),float(hi)],
        "bootstrap_prob_positive":float(np.mean(np.array(boots)>0)),
    }


def main():
    vix=c.fetch_daily("^VIX")
    rows,meta=data.fetch_history(SYMBOL,time.time()); dates=[d for d,_ in rows]
    p,X=c.build_features(rows,c.fetch_daily(SYMBOL),vix); yfull=(p[1:]>p[:-1]).astype(float)
    old=v33(p,include_trace=True,dates=dates,target_date=meta["target_date"]); tr=old["audit_trace"]
    pos=np.array([int(x["t"]) for x in tr],int); base=np.array([float(x["probability"]) for x in tr]); yy=np.array([float(x["outcome"]) for x in tr])
    raw=np.array([c.fit_predict(X,yfull,int(t)) for t in pos],float)
    cand=np.where(np.isfinite(raw),(1-BLEND)*base+BLEND*raw,np.nan)
    served,used=c.causal_gate(base,cand,yy)
    diff=(base-yy)**2-(served-yy)**2
    active=np.array(used,dtype=bool)
    active_diff=diff[active]
    out={
        "symbol":SYMBOL,"as_of":meta["as_of"],"target_date":meta["target_date"],
        "audit_days":int(len(diff)),"active_days":int(active.sum()),
        "all_days":gain_stats(diff),
        "active_days_only":None if len(active_diff)<10 else gain_stats(active_diff),
        "active_win_rate":None if not active.any() else float(np.mean(diff[active]>0)),
        "max_single_day_harm":None if not active.any() else float(np.min(diff[active])),
        "max_single_day_gain":None if not active.any() else float(np.max(diff[active])),
    }
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
