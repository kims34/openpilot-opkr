"""Causal adaptive-baseline research.

Every forecast chooses among simple challengers using only outcomes already
known at that forecast time. There is no look-ahead model selection.
"""
import json, math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import numpy as np
import requests

SYMBOLS=["SPY","QQQ","SCHD"]
HALF_LIVES=[126.,252.,504.,756.,1260.,2520.]
NY=ZoneInfo("America/New_York")
EVAL=1008
LOOKBACK=504


def fetch(symbol):
    r=requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",params={"range":"10y","interval":"1d","includePrePost":"false","events":"div,splits"},headers={"User-Agent":"Mozilla/5.0 IndexAlert causal baseline research"},timeout=30)
    r.raise_for_status(); x=(r.json().get('chart',{}).get('result') or [None])[0]
    ts=x.get('timestamp') or []; close=(x.get('indicators',{}).get('quote') or [{}])[0].get('close') or []
    rows=[]
    for t,p in zip(ts,close):
        if p is None or not math.isfinite(float(p)) or float(p)<=0: continue
        d=datetime.fromtimestamp(int(t),timezone.utc).astimezone(NY).date().isoformat(); rows.append((d,float(p)))
    return rows


def weighted_rate(y,t,hl,mask=None):
    idx=np.arange(max(0,t-2520),t)
    if mask is not None: idx=idx[mask[idx]]
    if len(idx)<30: return None
    age=t-1-idx; w=0.5**(age/hl)
    return float((w@y[idx]+10)/(w.sum()+20))


def candidate_probs(prices,dates):
    n=len(prices); y=(prices[1:]>prices[:-1]).astype(float)
    rets=np.zeros(n); rets[1:]=prices[1:]/prices[:-1]-1
    weekdays=np.array([datetime.fromisoformat(d).weekday() for d in dates])

    # Precompute every half-life series once. This is mathematically identical
    # to recomputing inside each selector window but far faster.
    hl_probs={hl:np.full(n-1,np.nan) for hl in HALF_LIVES}
    for hl in HALF_LIVES:
        for t in range(300,n-1): hl_probs[hl][t]=weighted_rate(y,t,hl)

    out={name:np.full(n-1,np.nan) for name in ['fixed','adaptive_hl','prev_sign','weekday']}
    out['fixed'][:]=hl_probs[1260.]

    for t in range(300,n-1):
        fixed=out['fixed'][t]
        hist=np.arange(max(300,t-LOOKBACK),t)
        best=(1e9,1260.)
        for hl in HALF_LIVES:
            p=hl_probs[hl][hist]; valid=~np.isnan(p)
            if valid.sum()>=126:
                loss=float(np.mean((p[valid]-y[hist][valid])**2))
                if loss<best[0]: best=(loss,hl)
        out['adaptive_hl'][t]=hl_probs[best[1]][t]

        sign=rets[t]>0
        mask=np.zeros(n-1,dtype=bool); mask[1:t]=((rets[1:t]>0)==sign)
        cond=weighted_rate(y,t,756.,mask)
        out['prev_sign'][t]=fixed if cond is None else 0.75*fixed+0.25*cond

        target_wd=weekdays[t+1]
        mask=np.zeros(n-1,dtype=bool); mask[:t]=(weekdays[1:t+1]==target_wd)
        cond=weighted_rate(y,t,1260.,mask)
        out['weekday'][t]=fixed if cond is None else 0.75*fixed+0.25*cond
    return y,out


def causal_selector(y,preds,t):
    fixed=preds['fixed']; start=max(300,t-LOOKBACK); mid=start+(t-start)//2
    best=('fixed',0.0)
    for name in ['adaptive_hl','prev_sign','weekday']:
        p=preds[name]
        if np.isnan(p[t]): continue
        adv=[]; okay=True
        for a,b in ((start,mid),(mid,t)):
            idx=np.arange(a,b); idx=idx[~np.isnan(p[idx]) & ~np.isnan(fixed[idx])]
            if len(idx)<60: okay=False; break
            gain=float(np.mean((fixed[idx]-y[idx])**2-(p[idx]-y[idx])**2)); adv.append(gain)
        if okay and min(adv)>0 and sum(adv)>best[1]: best=(name,sum(adv))
    return best[0]


def main():
    results=[]
    for s in SYMBOLS:
        rows=fetch(s); dates=[d for d,_ in rows]; prices=np.array([p for _,p in rows],float)
        y,preds=candidate_probs(prices,dates); n=len(prices); start=n-1-EVAL
        policy=np.full(n-1,np.nan); choices=[]
        for t in range(start,n-1):
            name=causal_selector(y,preds,t); policy[t]=preds[name][t]; choices.append(name)
        idx=np.arange(start,n-1); fixed=preds['fixed'][idx]
        pb=float(np.mean((policy[idx]-y[idx])**2)); bb=float(np.mean((fixed-y[idx])**2))
        mid=start+EVAL//2
        first=float(np.mean((policy[start:mid]-y[start:mid])**2)); firstb=float(np.mean((preds['fixed'][start:mid]-y[start:mid])**2))
        second=float(np.mean((policy[mid:n-1]-y[mid:n-1])**2)); secondb=float(np.mean((preds['fixed'][mid:n-1]-y[mid:n-1])**2))
        counts={k:choices.count(k) for k in ['fixed','adaptive_hl','prev_sign','weekday']}
        results.append(dict(symbol=s,brier=pb,baseline=bb,skill=(1-pb/bb)*100,first_half_skill=(1-first/firstb)*100,second_half_skill=(1-second/secondb)*100,choices=counts,current_probability=float(policy[n-2])*100,current_fixed=float(preds['fixed'][n-2])*100))
    pooled=np.mean([r['brier'] for r in results]); base=np.mean([r['baseline'] for r in results])
    final={"results":results,"pooled_skill":float((1-pooled/base)*100),"deploy":bool(pooled<base and sum(r['skill']>0 for r in results)>=2 and sum(r['second_half_skill']>0 for r in results)>=2)}
    print('FINAL',json.dumps(final,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
