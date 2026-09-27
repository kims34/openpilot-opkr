"""Research-only completed-session OHLC/VIX regime overlays for v3.3."""
import json, time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np
import requests

import next_day_probability as data
import probability_model as core
from probability_model_v33_runtime import estimate_prices as v33

NY=ZoneInfo("America/New_York")
SYMBOLS=("SPY","QQQ","SCHD")
BLENDS=(0.125,0.25,0.375,0.5)
WINDOW=504; MIN_HALF=60; RECENT_GATE=126


def fetch_daily(symbol):
    r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",params={"range":"10y","interval":"1d","includePrePost":"false","events":"div,splits"},headers={"User-Agent":"Mozilla/5.0 IndexAlert/research"},timeout=20)
    r.raise_for_status(); result=(r.json().get("chart",{}).get("result") or [None])[0]
    if not result: raise RuntimeError(symbol)
    ts=result.get("timestamp") or []; q=(result.get("indicators",{}).get("quote") or [{}])[0]
    out={}
    for i,t in enumerate(ts):
        day=datetime.fromtimestamp(int(t),timezone.utc).astimezone(NY).date().isoformat()
        try:
            vals=tuple(float((q.get(k) or [])[i]) for k in ("open","high","low","close","volume"))
        except Exception: continue
        if all(np.isfinite(vals)): out[day]=vals
    return out


def build_states(rows,ohlc,vix):
    dates=[d for d,_ in rows]; p=np.array([x for _,x in rows],float); n=len(p)
    names=("intraday_up","gap_up","close_high","range_high","volume_high","vix_high","vix_up","vix_high_up")
    s={k:np.zeros(n,dtype=bool) for k in names}; valid={k:np.zeros(n,dtype=bool) for k in names}
    ranges=np.full(n,np.nan); vols=np.full(n,np.nan); vixc=np.full(n,np.nan)
    for i,d in enumerate(dates):
        if d in ohlc:
            o,h,l,c,v=ohlc[d]
            valid["intraday_up"][i]=valid["close_high"][i]=True
            s["intraday_up"][i]=c>o
            s["close_high"][i]=(c-l)/max(h-l,1e-12)>.5
            ranges[i]=(h-l)/max(c,1e-12); vols[i]=v
            if i>0:
                valid["gap_up"][i]=True; s["gap_up"][i]=o>p[i-1]
        if d in vix:
            vixc[i]=vix[d][3]
            if i>0 and np.isfinite(vixc[i-1]): valid["vix_up"][i]=True; s["vix_up"][i]=vixc[i]>vixc[i-1]
    for t in range(300,n):
        a=max(60,t-252)
        for name,arr in (("range_high",ranges),("volume_high",vols),("vix_high",vixc)):
            hist=arr[a:t]; hist=hist[np.isfinite(hist)]
            if len(hist)>=126 and np.isfinite(arr[t]):
                valid[name][t]=True; s[name][t]=arr[t]>float(np.median(hist))
        if valid["vix_high"][t] and valid["vix_up"][t]:
            valid["vix_high_up"][t]=True; s["vix_high_up"][t]=bool(s["vix_high"][t] and s["vix_up"][t])
    return p,s,valid


def candidate(base,y,state,valid,blend):
    n=len(base); q=np.full(n,np.nan)
    for t in range(300,n):
        if not valid[t] or not np.isfinite(base[t]): continue
        m=np.zeros(n-1,dtype=bool); upto=min(t,n-1)
        m[:upto]=valid[1:upto+1] & (state[1:upto+1]==state[t])
        cond=core._weighted_rate(y,t,core.BASE_HALF_LIFE,m)
        q[t]=base[t] if cond is None else (1-blend)*base[t]+blend*cond
    return q


def overlay(vprob,q,y,pos):
    out=[]; used=[]
    for i,t in enumerate(pos):
        use=False; idx=np.arange(max(0,i-WINDOW),i)
        idx=idx[np.isfinite(q[np.array([pos[j] for j in idx],int)])]
        if len(idx)>=2*MIN_HALF:
            mid=len(idx)//2; gains=[]
            for h in (idx[:mid],idx[mid:]):
                ts=np.array([pos[j] for j in h],int); b=vprob[h]; c=q[ts]
                gains.append(float(np.mean((b-y[ts])**2-(c-y[ts])**2)))
            rr=idx[-RECENT_GATE:]; ts=np.array([pos[j] for j in rr],int)
            rg=float(np.mean((vprob[rr]-y[ts])**2-(q[ts]-y[ts])**2)) if len(rr)>=60 else -1
            use=min(gains)>0 and rg>0
        out.append(float(q[t]) if use and np.isfinite(q[t]) else float(vprob[i])); used.append(use and np.isfinite(q[t]))
    return np.array(out),used


def parts(p,y):
    z=(p-y)**2; m=len(z)//2
    return {"full":float(z.mean()),"first":float(z[:m].mean()),"second":float(z[m:].mean()),"recent252":float(z[-252:].mean())}


def main():
    vix=fetch_daily("^VIX"); result={}
    for sym in SYMBOLS:
        rows,meta=data.fetch_history(sym,time.time()); dates=[d for d,_ in rows]
        p,states,valid=build_states(rows,fetch_daily(sym),vix); y=(p[1:]>p[:-1]).astype(float)
        core_y,cands=core._candidate_probabilities(p,dates); base=np.asarray(cands["fixed"],float)
        old=v33(p,include_trace=True,dates=dates,target_date=meta["target_date"]); tr=old["audit_trace"]
        pos=[int(x["t"]) for x in tr]; vp=np.array([float(x["probability"]) for x in tr]); yy=np.array([float(x["outcome"]) for x in tr])
        bl=parts(vp,yy); tests=[]
        for name in states:
            for blend in BLENDS:
                q=candidate(base,core_y,states[name],valid[name],blend); served,used=overlay(vp,q,core_y,pos); lp=parts(served,yy); gain={k:bl[k]-lp[k] for k in bl}
                passed=all(gain[k]>0 for k in ("full","first","second","recent252"))
                tests.append({"signal":name,"blend":blend,"passed":passed,"used_days":sum(used),"gain":gain,"current_candidate":None if not np.isfinite(q[-1]) else float(q[-1])*100})
        tests.sort(key=lambda x:x["gain"]["full"],reverse=True)
        result[sym]={"as_of":meta["as_of"],"target_date":meta["target_date"],"v33_probability":old["probability"],"passes":[x for x in tests if x["passed"]],"best":tests[:10]}
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
