"""Model 3.3 OHLCV research against deployed model 3.1.

This intentionally tests a different information family from prior close-only
regime experiments: overnight gap, intraday move, close location, daily range,
volume regime, and gap/intraday sign pattern. Extra signals may override the
causal v3.1 forecast only after beating v3.1 in both halves of a trailing
validation window using already-realised outcomes.
"""
import json, math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
import requests

import probability_research_v32 as r
import probability_research_v32b as b

NY = ZoneInfo("America/New_York")
EXTRAS = ["gap", "intraday", "close_location", "range_regime", "volume_regime", "session_pattern"]
SHRINK = 0.25


def fetch_ohlcv(symbol):
    req = requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={"range":"10y","interval":"1d","includePrePost":"false","events":"div,splits"},
        headers={"User-Agent":"Mozilla/5.0 IndexAlert model-3.3 research"}, timeout=30,
    )
    req.raise_for_status()
    x = (req.json().get("chart",{}).get("result") or [None])[0]
    if not x:
        raise RuntimeError(f"no data {symbol}")
    q = (x.get("indicators",{}).get("quote") or [{}])[0]
    ts = x.get("timestamp") or []
    keys = ("open","high","low","close","volume")
    cols = {k:q.get(k) or [] for k in keys}
    rows=[]
    for i,t in enumerate(ts):
        try:
            vals={k:cols[k][i] for k in keys}
        except Exception:
            continue
        if any(vals[k] is None for k in ("open","high","low","close")):
            continue
        o,h,l,c = map(float,(vals["open"],vals["high"],vals["low"],vals["close"]))
        v = float(vals["volume"] or 0.0)
        if not all(math.isfinite(z) and z>0 for z in (o,h,l,c)) or not math.isfinite(v) or v<0:
            continue
        d=datetime.fromtimestamp(int(t),timezone.utc).astimezone(NY).date().isoformat()
        rows.append((d,o,h,l,c,v))
    return rows


def rolling_std(x, window):
    out=np.full(len(x),np.nan)
    for t in range(window,len(x)):
        z=x[t-window+1:t+1]
        if np.all(np.isfinite(z)):
            out[t]=float(np.std(z))
    return out


def bucket(x,cuts):
    out=np.full(len(x),-1,dtype=int)
    ok=np.isfinite(x)
    out[ok]=np.digitize(x[ok],cuts)
    return out


def build_regimes(o,h,l,c,v):
    n=len(c)
    ret=np.full(n,np.nan); ret[1:]=c[1:]/c[:-1]-1.0
    vol20=rolling_std(np.nan_to_num(ret,nan=0.0),20)

    gap=np.full(n,np.nan); gap[1:]=o[1:]/c[:-1]-1.0
    intraday=c/o-1.0
    gap_z=np.full(n,np.nan); intra_z=np.full(n,np.nan)
    ok=np.isfinite(vol20)&(vol20>1e-8)
    gap_z[ok]=gap[ok]/vol20[ok]
    intra_z[ok]=intraday[ok]/vol20[ok]

    clv=np.full(n,np.nan)
    spread=h-l
    ok2=np.isfinite(spread)&(spread>1e-12)
    clv[ok2]=(c[ok2]-l[ok2])/spread[ok2]

    range_reg=np.full(n,-1,dtype=int)
    daily_range=np.full(n,np.nan); daily_range[1:]=(h[1:]-l[1:])/c[:-1]
    for t in range(272,n):
        hist=daily_range[t-252:t]; hist=hist[np.isfinite(hist)]
        if len(hist)>=126 and np.isfinite(daily_range[t]):
            q1,q2=np.quantile(hist,[1/3,2/3])
            range_reg[t]=int(daily_range[t]>q1)+int(daily_range[t]>q2)

    volume_reg=np.full(n,-1,dtype=int)
    for t in range(60,n):
        hist=v[max(0,t-60):t]
        hist=hist[np.isfinite(hist)&(hist>0)]
        if len(hist)>=30 and v[t]>0:
            med=float(np.median(hist))
            ratio=v[t]/med if med>0 else np.nan
            if np.isfinite(ratio):
                volume_reg[t]=int(ratio>0.85)+int(ratio>1.25)+int(ratio>1.75)

    session=np.full(n,-1,dtype=int)
    for t in range(1,n):
        if np.isfinite(gap[t]) and np.isfinite(intraday[t]):
            session[t]=2*int(gap[t]>0)+int(intraday[t]>0)

    return {
        "gap":bucket(gap_z,[-1.0,-0.25,0.25,1.0]),
        "intraday":bucket(intra_z,[-1.0,-0.25,0.25,1.0]),
        "close_location":bucket(clv,[0.25,0.5,0.75]),
        "range_regime":range_reg,
        "volume_regime":volume_reg,
        "session_pattern":session,
    }


def extra_probs(c, regimes, y, fixed):
    n=len(c); out={k:np.full(n-1,np.nan) for k in EXTRAS}
    for t in range(r.MIN_TRAIN,n-1):
        base=float(fixed[t])
        for name in EXTRAS:
            code=regimes[name][t]
            if code<0:
                out[name][t]=base; continue
            mask=np.zeros(n-1,dtype=bool); mask[:t]=(regimes[name][:t]==code)
            cond=r.weighted_rate(y,t,r.COND_HL,mask)
            out[name][t]=base if cond is None else (1-SHRINK)*base+SHRINK*cond
    return out


def select_overlay(y, incumbent, extras, t):
    start=max(r.MIN_TRAIN+120,t-r.LOOKBACK); mid=start+(t-start)//2
    best=("v31",0.0)
    for name,p in extras.items():
        if not np.isfinite(p[t]): continue
        gains=[]; ok=True
        for a,z in ((start,mid),(mid,t)):
            idx=np.arange(a,z); valid=np.isfinite(incumbent[idx])&np.isfinite(p[idx]); idx=idx[valid]
            if len(idx)<60: ok=False; break
            gains.append(float(np.mean((incumbent[idx]-y[idx])**2-(p[idx]-y[idx])**2)))
        if ok and min(gains)>0 and sum(gains)>best[1]: best=(name,sum(gains))
    return best[0]


def score(p,y): return float(np.mean((p-y)**2))


def main():
    results=[]
    for s in r.SYMBOLS:
        rows=fetch_ohlcv(s)
        dates=[x[0] for x in rows]
        o=np.array([x[1] for x in rows],float); h=np.array([x[2] for x in rows],float)
        l=np.array([x[3] for x in rows],float); c=np.array([x[4] for x in rows],float); v=np.array([x[5] for x in rows],float)
        y,base_candidates=r.candidate_probs(c,dates)
        incumbent,inc_names=b.build_v31_policy(y,base_candidates)
        regs=build_regimes(o,h,l,c,v)
        extras=extra_probs(c,regs,y,base_candidates["fixed"])
        n=len(c); start=n-1-r.EVAL
        policy=np.full(n-1,np.nan); choices=[]
        for t in range(start,n-1):
            name=select_overlay(y,incumbent,extras,t)
            policy[t]=incumbent[t] if name=="v31" else extras[name][t]
            choices.append(name)
        idx=np.arange(start,n-1); mid=start+r.EVAL//2
        b33=score(policy[idx],y[idx]); b31=score(incumbent[idx],y[idx])
        f33=score(policy[start:mid],y[start:mid]); f31=score(incumbent[start:mid],y[start:mid])
        s33=score(policy[mid:n-1],y[mid:n-1]); s31=score(incumbent[mid:n-1],y[mid:n-1])
        counts={k:choices.count(k) for k in ["v31"]+EXTRAS}
        results.append({
            "symbol":s,"brier_v33":b33,"brier_v31":b31,
            "skill_vs_v31":(1-b33/b31)*100,
            "first_half_skill_vs_v31":(1-f33/f31)*100,
            "second_half_skill_vs_v31":(1-s33/s31)*100,
            "choices":counts,"override_days":sum(counts[k] for k in EXTRAS),
            "current_probability_v33":float(policy[n-2])*100,
            "current_probability_v31":float(incumbent[n-2])*100,
            "current_v31_strategy":str(inc_names[n-2]),
        })
    p33=float(np.mean([x["brier_v33"] for x in results])); p31=float(np.mean([x["brier_v31"] for x in results]))
    overall=sum(x["skill_vs_v31"]>0 for x in results); recent=sum(x["second_half_skill_vs_v31"]>0 for x in results)
    deploy=bool(p33<p31 and overall>=2 and recent>=2 and min(x["second_half_skill_vs_v31"] for x in results)>-0.03)
    print("FINAL",json.dumps({"results":results,"pooled_brier_v33":p33,"pooled_brier_v31":p31,"pooled_skill_vs_v31":(1-p33/p31)*100,"deploy":deploy,"promotion_rule":"beat v3.1 pooled; >=2 symbols overall/recent; worst recent-half regression > -0.03%"},ensure_ascii=False),flush=True)


if __name__=="__main__": main()
