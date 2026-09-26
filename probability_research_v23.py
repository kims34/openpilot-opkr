"""One-shot held-out research for next-close direction probabilities.

Model/hyperparameters are selected only on the development validation window.
The most recent 504 forecasts are a final untouched holdout and are never used
for selection.  The objective is Brier score, matching the production metric.
"""
import json, math, time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import requests

TARGETS = ["SPY", "QQQ", "SCHD"]
AUX = ["^VIX", "TLT", "HYG", "IWM"]
ALL = TARGETS + AUX
MIN_FEATURE_DAY = 252
DEV_EVAL = 504
HOLDOUT = 504
HALF_LIFE_BASE = 1260.0
HALF_LIFE_FIT = 756.0
WINDOWS = [756, 1260]
LAMBDAS = [10.0, 100.0]
ALPHAS = [0.25, 0.5, 0.75, 1.0]
NY = ZoneInfo("America/New_York")


def fetch(symbol):
    r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={"range":"10y","interval":"1d","includePrePost":"false","events":"div,splits"},
        headers={"User-Agent":"Mozilla/5.0 IndexAlert probability research"}, timeout=30)
    r.raise_for_status()
    x = (r.json().get("chart",{}).get("result") or [None])[0]
    if not x: raise RuntimeError(f"no data {symbol}")
    ts=x.get("timestamp") or []
    close=(x.get("indicators",{}).get("quote") or [{}])[0].get("close") or []
    out={}
    for t,p in zip(ts,close):
        if p is None or not math.isfinite(float(p)) or float(p)<=0: continue
        d=datetime.fromtimestamp(int(t),timezone.utc).astimezone(NY).date().isoformat()
        out[d]=float(p)
    return out


def aligned():
    raw={s:fetch(s) for s in ALL}
    dates=sorted(set.intersection(*(set(raw[s]) for s in ALL)))
    if len(dates)<2200: raise RuntimeError(f"insufficient common dates {len(dates)}")
    data={s:np.array([raw[s][d] for d in dates],float) for s in ALL}
    return dates,data


def ret(p,t,k): return p[t]/p[t-k]-1.0

def vol(p,t,k):
    r=p[t-k+1:t+1]/p[t-k:t]-1.0
    return float(np.std(r))

def dd(p,t,k): return p[t]/np.max(p[t-k+1:t+1])-1.0

def ma_dist(p,t,k): return p[t]/np.mean(p[t-k+1:t+1])-1.0

def sign_frac(p,t,k):
    r=p[t-k+1:t+1]/p[t-k:t]-1.0
    return float(np.mean(r>0))-0.5


def features(data,target,t,kind):
    p=data[target]
    compact=[ret(p,t,1),ret(p,t,5),ret(p,t,20),vol(p,t,20),dd(p,t,60),sign_frac(p,t,20)]
    if kind=="compact": return np.asarray(compact,float)
    own=[ret(p,t,k) for k in (1,2,5,10,20,60)]
    own += [vol(p,t,k) for k in (5,20,60)]
    own += [dd(p,t,k) for k in (20,60,252)]
    own += [ma_dist(p,t,k) for k in (5,20,60)]
    own += [sign_frac(p,t,k) for k in (5,20)]
    if kind=="own": return np.asarray(own,float)
    v=data["^VIX"]
    macro=[ret(v,t,1),ret(v,t,5),ma_dist(v,t,20)]
    for s in ("TLT","HYG","IWM"):
        q=data[s]; macro += [ret(q,t,1),ret(q,t,5),ret(q,t,20)]
    # Market context for non-SPY targets; harmless duplicate context for SPY is
    # intentionally omitted to keep the shared feature set compact.
    if target!="SPY":
        q=data["SPY"]; macro += [ret(q,t,1),ret(q,t,5),ret(q,t,20)]
    else:
        macro += [0.0,0.0,0.0]
    return np.asarray(own+macro,float)


def base_prob(y,t):
    # At forecast time t, y[t-1] is the newest known label (t-1 -> t).
    idx=np.arange(max(0,t-1260),t)
    if len(idx)==0: return 0.5
    age=(t-1-idx)
    w=0.5**(age/HALF_LIFE_BASE)
    return float(w@y[idx]/w.sum())


def ridge_pred(X,y,t,window,lam):
    start=max(MIN_FEATURE_DAY,t-window)
    idx=np.arange(start,t)
    Xi=X[idx]; yi=y[idx]
    age=t-1-idx
    w=0.5**(age/HALF_LIFE_FIT)
    mu=np.average(Xi,axis=0,weights=w)
    z=Xi-mu
    var=np.average(z*z,axis=0,weights=w)
    sd=np.sqrt(np.maximum(var,1e-8))
    Z=z/sd
    x=(X[t]-mu)/sd
    A=np.column_stack((np.ones(len(Z)),Z))
    sw=np.sqrt(w)[:,None]
    Aw=A*sw; yw=yi*np.sqrt(w)
    penalty=np.eye(A.shape[1])*lam; penalty[0,0]=0.0
    beta=np.linalg.solve(Aw.T@Aw+penalty,Aw.T@yw)
    return float(np.clip(np.r_[1.0,x]@beta,0.30,0.70))


def evaluate_segment(preds,bases,y,idx):
    p=preds[idx]; b=bases[idx]; yy=y[idx]
    return float(np.mean((p-yy)**2)), float(np.mean((b-yy)**2))


def main():
    dates,data=aligned(); n=len(dates)
    # y[t] is whether close[t+1] > close[t]. Last element is unused.
    ys={s:(data[s][1:]>data[s][:-1]).astype(float) for s in TARGETS}
    hold_start=n-1-HOLDOUT
    dev_start=hold_start-DEV_EVAL
    if dev_start < MIN_FEATURE_DAY+756: raise RuntimeError("not enough development history")
    eval_t=np.arange(dev_start,n-1)
    print("RESEARCH_WINDOW",json.dumps({"common_days":n,"dev": [dates[dev_start],dates[hold_start]],"holdout":[dates[hold_start],dates[n-1]]},ensure_ascii=False),flush=True)

    candidates=[]
    cache={}
    for s in TARGETS:
        y=ys[s]
        bases=np.full(n-1,np.nan)
        for t in eval_t: bases[t]=base_prob(y,t)
        cache[(s,"base")]=bases
        for kind in ("compact","own","macro"):
            X=np.full((n,6 if kind=="compact" else (17 if kind=="own" else 32)),np.nan)
            for t in range(MIN_FEATURE_DAY,n): X[t]=features(data,s,t,kind)
            for window in WINDOWS:
                for lam in LAMBDAS:
                    raw=np.full(n-1,np.nan)
                    for t in eval_t: raw[t]=ridge_pred(X,y,t,window,lam)
                    cache[(s,kind,window,lam)]=raw

    # Shared hyperparameter selection across all three ETFs on development only.
    for kind in ("compact","own","macro"):
        for window in WINDOWS:
            for lam in LAMBDAS:
                for alpha in ALPHAS:
                    losses=[]; base_losses=[]; half_adv=[[],[]]
                    for s in TARGETS:
                        y=ys[s]; b=cache[(s,"base")]; raw=cache[(s,kind,window,lam)]
                        p=b+alpha*(raw-b)
                        idx=np.arange(dev_start,hold_start)
                        losses.extend(((p[idx]-y[idx])**2).tolist())
                        base_losses.extend(((b[idx]-y[idx])**2).tolist())
                        mid=dev_start+DEV_EVAL//2
                        for h,sub in enumerate((np.arange(dev_start,mid),np.arange(mid,hold_start))):
                            half_adv[h].extend((((b[sub]-y[sub])**2)-((p[sub]-y[sub])**2)).tolist())
                    brier=float(np.mean(losses)); base=float(np.mean(base_losses))
                    candidates.append(dict(kind=kind,window=window,lam=lam,alpha=alpha,
                        dev_brier=brier,dev_base=base,dev_skill=(1-brier/base)*100,
                        first_half_adv=float(np.mean(half_adv[0])),second_half_adv=float(np.mean(half_adv[1]))))
    # Require improvement in both chronological halves of development validation.
    eligible=[c for c in candidates if c['first_half_adv']>0 and c['second_half_adv']>0 and c['dev_brier']<c['dev_base']]
    chosen=min(eligible,key=lambda c:c['dev_brier']) if eligible else None
    print("TOP_DEV",json.dumps(sorted(candidates,key=lambda c:c['dev_brier'])[:8],ensure_ascii=False),flush=True)
    print("CHOSEN",json.dumps(chosen,ensure_ascii=False),flush=True)
    if not chosen:
        print("FINAL",json.dumps({"deploy":False,"reason":"no candidate improved both development halves"},ensure_ascii=False),flush=True); return

    hold=[]
    for s in TARGETS:
        y=ys[s]; b=cache[(s,"base")]; raw=cache[(s,chosen['kind'],chosen['window'],chosen['lam'])]
        p=b+chosen['alpha']*(raw-b)
        idx=np.arange(hold_start,n-1)
        pb=float(np.mean((p[idx]-y[idx])**2)); bb=float(np.mean((b[idx]-y[idx])**2))
        mid=hold_start+HOLDOUT//2
        first=float(np.mean((p[hold_start:mid]-y[hold_start:mid])**2))
        firstb=float(np.mean((b[hold_start:mid]-y[hold_start:mid])**2))
        second=float(np.mean((p[mid:n-1]-y[mid:n-1])**2))
        secondb=float(np.mean((b[mid:n-1]-y[mid:n-1])**2))
        hold.append(dict(symbol=s,brier=pb,baseline=bb,skill=(1-pb/bb)*100,
            first_half_skill=(1-first/firstb)*100,second_half_skill=(1-second/secondb)*100,
            current_probability=float(p[n-2])*100,current_base=float(b[n-2])*100))
    pooled_b=np.mean([x['brier'] for x in hold]); pooled_base=np.mean([x['baseline'] for x in hold])
    result={"chosen":chosen,"holdout":hold,"pooled_skill":float((1-pooled_b/pooled_base)*100),
        "deploy":bool(pooled_b<pooled_base and sum(x['skill']>0 for x in hold)>=2)}
    print("FINAL",json.dumps(result,ensure_ascii=False),flush=True)

if __name__=="__main__": main()
