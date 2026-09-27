"""Research-only regularized multifeature challenger for v3.3.

Fits a ridge-logistic model at each forecast date using only earlier completed
sessions. The challenger is then blended with v3.3 and causally gated using only
prior scored forecasts. No production wiring.
"""
import json, math, time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np
import requests

import next_day_probability as data
from probability_model_v33_runtime import estimate_prices as v33

NY=ZoneInfo("America/New_York")
SYMBOLS=("SPY","QQQ","SCHD")
TRAIN=1260
MIN_TRAIN=504
RIDGE=10.0
BLENDS=(0.15,0.25,0.35)
GATE_WINDOW=504
GATE_HALF=60
RECENT_GATE=126


def fetch_daily(symbol):
    r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",params={"range":"10y","interval":"1d","includePrePost":"false","events":"div,splits"},headers={"User-Agent":"Mozilla/5.0 IndexAlert/research"},timeout=20)
    r.raise_for_status(); z=(r.json().get("chart",{}).get("result") or [None])[0]
    if not z: raise RuntimeError(symbol)
    q=(z.get("indicators",{}).get("quote") or [{}])[0]; out={}
    for i,ts in enumerate(z.get("timestamp") or []):
        day=datetime.fromtimestamp(int(ts),timezone.utc).astimezone(NY).date().isoformat()
        try: vals=tuple(float((q.get(k) or [])[i]) for k in ("open","high","low","close","volume"))
        except Exception: continue
        if all(np.isfinite(vals)): out[day]=vals
    return out


def build_features(rows,ohlc,vix):
    dates=[d for d,_ in rows]; p=np.array([x for _,x in rows],float); n=len(p)
    r=np.full(n,np.nan); r[1:]=p[1:]/p[:-1]-1
    X=np.full((n,10),np.nan)
    vixc=np.full(n,np.nan)
    for i,d in enumerate(dates):
        if d in vix: vixc[i]=vix[d][3]
    for t in range(21,n):
        d=dates[t]
        if d not in ohlc: continue
        o,h,l,c,v=ohlc[d]
        histv=[]
        for j in range(max(0,t-20),t):
            if dates[j] in ohlc: histv.append(ohlc[dates[j]][4])
        volratio=v/(np.median(histv) if histv else max(v,1))
        vv=vixc[t]
        vchg=(vv/vixc[t-1]-1) if np.isfinite(vv) and np.isfinite(vixc[t-1]) and vixc[t-1]>0 else np.nan
        X[t]=[
            np.clip(r[t],-.08,.08),
            np.clip(p[t]/p[t-5]-1,-.20,.20),
            np.clip(p[t]/p[t-20]-1,-.35,.35),
            np.clip(float(np.std(r[t-19:t+1],ddof=1)),0,.10),
            np.clip(o/p[t-1]-1,-.08,.08),
            np.clip(c/o-1,-.08,.08),
            np.clip((c-l)/max(h-l,1e-12),0,1),
            np.clip(math.log(max(volratio,1e-6)),-2,2),
            np.clip(vv/30.0 if np.isfinite(vv) else np.nan,0,3),
            np.clip(vchg,-.50,.50),
        ]
    return p,X


def sigmoid(z):
    return 1/(1+np.exp(-np.clip(z,-30,30)))


def fit_predict(X,y,t):
    lo=max(21,t-TRAIN); Xi=X[lo:t]; yi=y[lo:t]
    ok=np.all(np.isfinite(Xi),axis=1) & np.isfinite(yi)
    Xi=Xi[ok]; yi=yi[ok]
    if len(yi)<MIN_TRAIN or not np.all(np.isfinite(X[t])): return np.nan
    mu=Xi.mean(axis=0); sd=Xi.std(axis=0); sd=np.where(sd<1e-8,1.0,sd)
    Z=(Xi-mu)/sd; zt=(X[t]-mu)/sd
    A=np.column_stack([np.ones(len(Z)),Z]); xt=np.r_[1.0,zt]
    beta=np.zeros(A.shape[1]); penalty=np.r_[0.0,np.full(A.shape[1]-1,RIDGE)]
    for _ in range(20):
        ph=sigmoid(A@beta); w=np.maximum(ph*(1-ph),1e-5)
        grad=A.T@(ph-yi)+penalty*beta
        H=(A.T*w)@A+np.diag(penalty)+np.eye(A.shape[1])*1e-8
        try: step=np.linalg.solve(H,grad)
        except np.linalg.LinAlgError: return np.nan
        beta-=step
        if np.max(np.abs(step))<1e-6: break
    return float(sigmoid(xt@beta))


def causal_gate(base,cand,y):
    out=[]; used=[]
    for i in range(len(base)):
        use=False; lo=max(0,i-GATE_WINDOW)
        idx=np.array([j for j in range(lo,i) if np.isfinite(cand[j])],dtype=int)
        if len(idx)>=2*GATE_HALF:
            mid=len(idx)//2; gains=[]
            for h in (idx[:mid],idx[mid:]):
                gains.append(float(np.mean((base[h]-y[h])**2-(cand[h]-y[h])**2)))
            rr=idx[-RECENT_GATE:]
            rg=float(np.mean((base[rr]-y[rr])**2-(cand[rr]-y[rr])**2)) if len(rr)>=60 else -1
            use=bool(min(gains)>0 and rg>0)
        active=bool(use and np.isfinite(cand[i])); out.append(float(cand[i]) if active else float(base[i])); used.append(active)
    return np.array(out),used


def parts(p,y):
    z=(p-y)**2; m=len(z)//2
    return {"full":float(z.mean()),"first":float(z[:m].mean()),"second":float(z[m:].mean()),"recent252":float(z[-252:].mean())}


def main():
    vix=fetch_daily("^VIX"); result={}
    for sym in SYMBOLS:
        rows,meta=data.fetch_history(sym,time.time()); dates=[d for d,_ in rows]
        p,X=build_features(rows,fetch_daily(sym),vix); yfull=(p[1:]>p[:-1]).astype(float)
        old=v33(p,include_trace=True,dates=dates,target_date=meta["target_date"]); tr=old["audit_trace"]
        pos=np.array([int(x["t"]) for x in tr],int); base=np.array([float(x["probability"]) for x in tr]); yy=np.array([float(x["outcome"]) for x in tr])
        raw=np.array([fit_predict(X,yfull,int(t)) for t in pos],float)
        tests=[]; baseline=parts(base,yy)
        for blend in BLENDS:
            cand=np.where(np.isfinite(raw),(1-blend)*base+blend*raw,np.nan)
            served,used=causal_gate(base,cand,yy); lp=parts(served,yy); gain={k:float(baseline[k]-lp[k]) for k in baseline}
            passed=bool(all(gain[k]>0 for k in ("full","first","second","recent252")))
            current_raw=fit_predict(X,np.r_[yfull,np.nan][:-1],len(p)-1) if len(p)>MIN_TRAIN else np.nan
            tests.append({"blend":float(blend),"passed":passed,"used_days":int(sum(used)),"gain":gain,"current_logistic":None if not np.isfinite(current_raw) else float(current_raw*100)})
        result[sym]={"as_of":str(meta["as_of"]),"target_date":str(meta["target_date"]),"v33_probability":float(old["probability"]),"baseline":baseline,"tests":tests,"passes":[x for x in tests if x["passed"]]}
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__": main()
