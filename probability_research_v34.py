"""Research-only v3.4 overlays for next-session rise probability.

No production wiring here. Each overlay decides causally at forecast t whether to
replace the already-validated v3.3 probability, using only earlier scored days.
A candidate is reported as PASS only if it improves Brier loss versus v3.3 on
the full 1,008-session audit, both chronological halves, and the latest 252 days.
"""
import json, math, time
import numpy as np

import next_day_probability as data
from probability_model import _weighted_rate, BASE_HALF_LIFE
from probability_model_v33_runtime import estimate_prices as v33

SYMBOLS = ("SPY", "QQQ", "SCHD")
BLENDS = (0.125, 0.25, 0.375, 0.50)
WINDOW = 504
MIN_HALF = 60
RECENT_GATE = 126


def features(p):
    p=np.asarray(p,float); n=len(p)
    r=np.zeros(n); r[1:]=p[1:]/p[:-1]-1
    f={k:np.full(n,np.nan) for k in ("mom5","mom20","vol20","dd60")}
    for t in range(60,n):
        f["mom5"][t]=p[t]/p[t-5]-1
        f["mom20"][t]=p[t]/p[t-20]-1
        f["vol20"][t]=float(np.std(r[t-19:t+1],ddof=1))
        f["dd60"][t]=p[t]/np.max(p[t-59:t+1])-1
    return r,f


def states_for_t(f,name,t):
    arr=f[name]
    if name in ("mom5","mom20"):
        return arr>0, bool(arr[t]>0)
    hist=arr[max(60,t-252):t]
    hist=hist[np.isfinite(hist)]
    if len(hist)<126: return None,None
    threshold=float(np.median(hist))
    return arr>threshold, bool(arr[t]>threshold)


def candidate_series(p, base, y, f, name, blend):
    n=len(p); q=np.full(n,np.nan)
    for t in range(300,n):
        mask,state=states_for_t(f,name,t)
        if mask is None: continue
        m=np.zeros(n-1,dtype=bool)
        upto=min(t,len(m))
        m[:upto]=(mask[1:upto+1]==state)
        cond=_weighted_rate(y,t,BASE_HALF_LIFE,m)
        b=float(base[t])
        q[t]=b if cond is None else (1-blend)*b+blend*cond
    return q


def causal_overlay(vprob, cand, y, positions):
    served=[]; used=[]
    pos_to_i={t:i for i,t in enumerate(positions)}
    for i,t in enumerate(positions):
        use=False
        start=max(0,i-WINDOW)
        idx=np.arange(start,i)
        valid=idx[np.isfinite(cand[[positions[j] for j in idx]])]
        if len(valid)>=2*MIN_HALF:
            mid=len(valid)//2
            chunks=(valid[:mid],valid[mid:])
            gains=[]
            for chunk in chunks:
                ts=np.array([positions[j] for j in chunk],dtype=int)
                b=np.array([vprob[j] for j in chunk])
                c=cand[ts]
                yy=y[ts]
                gains.append(float(np.mean((b-yy)**2-(c-yy)**2)))
            recent=valid[-RECENT_GATE:]
            tsr=np.array([positions[j] for j in recent],dtype=int)
            rg=float(np.mean((np.array([vprob[j] for j in recent])-y[tsr])**2-(cand[tsr]-y[tsr])**2)) if len(recent)>=60 else -1
            use=min(gains)>0 and rg>0
        served.append(float(cand[t]) if use and np.isfinite(cand[t]) else float(vprob[i]))
        used.append(bool(use and np.isfinite(cand[t])))
    return np.array(served),used


def loss_parts(p,y):
    loss=(p-y)**2; n=len(loss); mid=n//2
    return dict(full=float(loss.mean()),first=float(loss[:mid].mean()),second=float(loss[mid:].mean()),recent252=float(loss[-252:].mean()))


def main():
    allout={}
    for symbol in SYMBOLS:
        rows,meta=data.fetch_history(symbol,time.time())
        dates=[d for d,_ in rows]; p=np.array([x for _,x in rows],float)
        y=(p[1:]>p[:-1]).astype(float)
        result=v33(p,include_trace=True,dates=dates,target_date=meta["target_date"])
        tr=result["audit_trace"]
        positions=[int(x["t"]) for x in tr]
        vprob=np.array([float(x["probability"]) for x in tr])
        yy=np.array([float(x["outcome"]) for x in tr])
        base=np.full(len(p),np.nan)
        for x in tr: base[int(x["t"])]=float(x["base"])
        # Fill base for non-audit dates using v3.3 preparation output indirectly via core candidates.
        import probability_model as core
        cy,cands=core._candidate_probabilities(p,dates)
        base=np.asarray(cands["fixed"],float)
        _,f=features(p)
        baseline=loss_parts(vprob,yy)
        candidates=[]
        for name in ("mom5","mom20","vol20","dd60"):
            for blend in BLENDS:
                q=candidate_series(p,base,cy,f,name,blend)
                served,used=causal_overlay(vprob,q,cy,positions)
                lp=loss_parts(served,yy)
                gains={k:baseline[k]-lp[k] for k in baseline}
                passed=all(gains[k]>0 for k in ("full","first","second","recent252"))
                candidates.append(dict(signal=name,blend=blend,passed=passed,used_days=sum(used),loss=lp,gain=gains,current_candidate=(None if not np.isfinite(q[len(p)-1]) else float(q[len(p)-1])*100)))
        candidates.sort(key=lambda x:x["gain"]["full"],reverse=True)
        allout[symbol]=dict(as_of=meta["as_of"],target_date=meta["target_date"],v33_probability=result["probability"],v33_loss=baseline,best=candidates[:8],passes=[c for c in candidates if c["passed"]])
    print(json.dumps(allout,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
