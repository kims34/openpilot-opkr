"""Conservative next-day probability v3.2 research.

Compares new regime-conditioned challengers against the already-promoted
model-3.1 policy. All feature states are computed with information available
at the forecast close. A new challenger is allowed only when it beats the
causal model-3.1 prediction in every chronological third of the prior 504
known forecasts. Nothing here changes production unless the final gate passes.
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
MIN_SEG=50
BLEND=0.20


def fetch(symbol):
    r=requests.get(
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}",
        params={"range":"10y","interval":"1d","includePrePost":"false","events":"div,splits"},
        headers={"User-Agent":"Mozilla/5.0 IndexAlert v3.2 research"},timeout=30)
    r.raise_for_status(); x=(r.json().get('chart',{}).get('result') or [None])[0]
    if not x: raise RuntimeError(f"no data {symbol}")
    ts=x.get('timestamp') or []; close=(x.get('indicators',{}).get('quote') or [{}])[0].get('close') or []
    rows=[]
    for t,p in zip(ts,close):
        if p is None: continue
        p=float(p)
        if not math.isfinite(p) or p<=0: continue
        d=datetime.fromtimestamp(int(t),timezone.utc).astimezone(NY).date().isoformat()
        if rows and rows[-1][0]==d: rows[-1]=(d,p)
        else: rows.append((d,p))
    return rows


def weighted_rate(y,t,hl,mask=None):
    idx=np.arange(max(0,t-2520),t)
    if mask is not None: idx=idx[mask[idx]]
    if len(idx)<30: return None
    age=t-1-idx; w=0.5**(age/hl)
    return float((w@y[idx]+10)/(w.sum()+20))


def rolling_features(prices):
    n=len(prices); rets=np.zeros(n); rets[1:]=prices[1:]/prices[:-1]-1
    vol20=np.full(n,np.nan); zret=np.full(n,np.nan); trend20=np.full(n,np.nan); dd60=np.full(n,np.nan); volratio=np.full(n,np.nan)
    for t in range(20,n):
        window=rets[max(1,t-19):t+1]
        v=float(np.std(window,ddof=1)) if len(window)>=10 else np.nan
        vol20[t]=v
        if math.isfinite(v) and v>1e-8: zret[t]=rets[t]/v
        trend20[t]=prices[t]/float(np.mean(prices[t-19:t+1]))-1
        start=max(0,t-59); dd60[t]=prices[t]/float(np.max(prices[start:t+1]))-1
        hist=vol20[max(20,t-252):t]
        hist=hist[np.isfinite(hist) & (hist>0)]
        if len(hist)>=60 and math.isfinite(v):
            med=float(np.median(hist))
            if med>0: volratio[t]=v/med
    mag=np.full(n,-1,int); two=np.full(n,-1,int); trend=np.full(n,-1,int); dd=np.full(n,-1,int); vol=np.full(n,-1,int)
    for t in range(20,n):
        if math.isfinite(zret[t]): mag[t]=0 if zret[t]<-1 else 1 if zret[t]<0 else 2 if zret[t]<1 else 3
        if t>=2: two[t]=(1 if rets[t-1]>0 else 0)*2+(1 if rets[t]>0 else 0)
        if math.isfinite(trend20[t]): trend[t]=0 if trend20[t]<-0.01 else 1 if trend20[t]<=0.01 else 2
        if math.isfinite(dd60[t]): dd[t]=0 if dd60[t]<=-0.05 else 1 if dd60[t]<=-0.02 else 2
        if math.isfinite(volratio[t]): vol[t]=0 if volratio[t]<0.8 else 1 if volratio[t]<=1.2 else 2
    return rets, {"ret_strength":mag,"two_day":two,"trend20":trend,"drawdown60":dd,"vol_regime":vol}


def base_candidates(prices,dates):
    n=len(prices); y=(prices[1:]>prices[:-1]).astype(float)
    rets=np.zeros(n); rets[1:]=prices[1:]/prices[:-1]-1
    weekdays=np.array([datetime.fromisoformat(d).weekday() for d in dates])
    hl_probs={hl:np.full(n-1,np.nan) for hl in HALF_LIVES}
    for hl in HALF_LIVES:
        for t in range(300,n-1): hl_probs[hl][t]=weighted_rate(y,t,hl)
    out={name:np.full(n-1,np.nan) for name in ['fixed','adaptive_hl','prev_sign','weekday']}
    out['fixed'][:]=hl_probs[1260.]
    for t in range(300,n-1):
        fixed=out['fixed'][t]; hist=np.arange(max(300,t-LOOKBACK),t); best=(1e9,1260.)
        for hl in HALF_LIVES:
            p=hl_probs[hl][hist]; valid=~np.isnan(p)
            if valid.sum()>=126:
                loss=float(np.mean((p[valid]-y[hist][valid])**2))
                if loss<best[0]: best=(loss,hl)
        out['adaptive_hl'][t]=hl_probs[best[1]][t]
        sign=rets[t]>0; mask=np.zeros(n-1,dtype=bool); mask[1:t]=((rets[1:t]>0)==sign)
        cond=weighted_rate(y,t,756.,mask); out['prev_sign'][t]=fixed if cond is None else 0.75*fixed+0.25*cond
        target_wd=weekdays[t+1]; mask=np.zeros(n-1,dtype=bool); mask[:t]=(weekdays[1:t+1]==target_wd)
        cond=weighted_rate(y,t,1260.,mask); out['weekday'][t]=fixed if cond is None else 0.75*fixed+0.25*cond
    return y,out


def selector31(y,preds,t):
    fixed=preds['fixed']; start=max(300,t-LOOKBACK); mid=start+(t-start)//2; best=('fixed',0.0)
    for name in ['adaptive_hl','prev_sign','weekday']:
        p=preds[name]
        if np.isnan(p[t]): continue
        gains=[]; ok=True
        for a,b in ((start,mid),(mid,t)):
            idx=np.arange(a,b); idx=idx[~np.isnan(p[idx]) & ~np.isnan(fixed[idx])]
            if len(idx)<60: ok=False; break
            gains.append(float(np.mean((fixed[idx]-y[idx])**2-(p[idx]-y[idx])**2)))
        if ok and min(gains)>0 and sum(gains)>best[1]: best=(name,sum(gains))
    return best[0]


def new_candidates(prices,y,fixed):
    n=len(prices); _,states=rolling_features(prices)
    out={k:np.full(n-1,np.nan) for k in states}
    for name,state in states.items():
        for t in range(300,n-1):
            base=fixed[t]
            if not math.isfinite(base) or state[t]<0: continue
            mask=np.zeros(n-1,dtype=bool)
            usable=np.arange(0,t)
            mask[usable]=(state[usable]==state[t])
            cond=weighted_rate(y,t,756.,mask)
            out[name][t]=base if cond is None else (1-BLEND)*base+BLEND*cond
    return out


def enhanced_selector(y,policy31,newp,t):
    start=max(300,t-LOOKBACK); edges=[start,start+(t-start)//3,start+2*(t-start)//3,t]
    best=('model31',0.0)
    for name,p in newp.items():
        if np.isnan(p[t]): continue
        gains=[]; ok=True
        for a,b in zip(edges[:-1],edges[1:]):
            idx=np.arange(a,b); valid=~np.isnan(p[idx]) & ~np.isnan(policy31[idx]); idx=idx[valid]
            if len(idx)<MIN_SEG: ok=False; break
            gains.append(float(np.mean((policy31[idx]-y[idx])**2-(p[idx]-y[idx])**2)))
        if ok and min(gains)>0 and sum(gains)>best[1]: best=(name,sum(gains))
    return best[0]


def safe_logloss(p,y):
    p=np.clip(p,1e-6,1-1e-6); return float(np.mean(-(y*np.log(p)+(1-y)*np.log(1-p))))


def main():
    results=[]
    for s in SYMBOLS:
        rows=fetch(s); dates=[d for d,_ in rows]; prices=np.array([p for _,p in rows],float)
        y,base=base_candidates(prices,dates); n=len(prices)
        policy31=np.full(n-1,np.nan); choice31=[]
        for t in range(300,n-1):
            name=selector31(y,base,t); policy31[t]=base[name][t]; choice31.append(name)
        newp=new_candidates(prices,y,base['fixed'])
        start=n-1-EVAL; enhanced=np.full(n-1,np.nan); choices=[]
        for t in range(start,n-1):
            name=enhanced_selector(y,policy31,newp,t)
            enhanced[t]=policy31[t] if name=='model31' else newp[name][t]
            choices.append(name)
        idx=np.arange(start,n-1); valid=np.isfinite(enhanced[idx]) & np.isfinite(policy31[idx]); idx=idx[valid]
        eb=float(np.mean((enhanced[idx]-y[idx])**2)); b31=float(np.mean((policy31[idx]-y[idx])**2))
        ell=safe_logloss(enhanced[idx],y[idx]); l31=safe_logloss(policy31[idx],y[idx])
        mid=start+EVAL//2
        halves=[]
        for a,b in ((start,mid),(mid,n-1)):
            ii=np.arange(a,b); vv=np.isfinite(enhanced[ii]) & np.isfinite(policy31[ii]); ii=ii[vv]
            e=float(np.mean((enhanced[ii]-y[ii])**2)); q=float(np.mean((policy31[ii]-y[ii])**2)); halves.append((1-e/q)*100)
        counts={k:choices.count(k) for k in ['model31','ret_strength','two_day','trend20','drawdown60','vol_regime']}
        results.append(dict(symbol=s,brier=eb,model31_brier=b31,skill_vs_31=(1-eb/b31)*100,logloss=ell,model31_logloss=l31,first_half_skill=halves[0],second_half_skill=halves[1],choices=counts,current_choice=choices[-1],current_probability=float(enhanced[n-2])*100,model31_probability=float(policy31[n-2])*100))
    pooled=np.mean([r['brier'] for r in results]); basep=np.mean([r['model31_brier'] for r in results])
    deploy=bool(pooled<basep and all(r['skill_vs_31']>0 for r in results) and all(r['second_half_skill']>0 for r in results))
    final={"model":"3.2-regime-research","results":results,"pooled_skill_vs_31":float((1-pooled/basep)*100),"deploy":deploy}
    print('FINAL',json.dumps(final,ensure_ascii=False),flush=True)

if __name__=='__main__': main()
