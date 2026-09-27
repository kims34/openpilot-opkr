"""Model 3.2c research: causal residual calibration of model 3.1.

No new market signal is introduced. Each candidate only corrects persistent
past forecast bias using residuals (outcome - model31 probability) known before
the forecast. One global policy is selected on the first 504 audit forecasts;
the final 504 forecasts are untouched promotion holdout.
"""
import json, math
import numpy as np
from probability_research_v32 import SYMBOLS, EVAL, fetch, base_candidates, selector31

CANDIDATES=[('identity',None,0.0),('bias126',126.0,0.5),('bias252',252.0,0.5),('bias504',504.0,0.5),('bias252q',252.0,0.25)]
PRIOR_WEIGHT=100.0


def build_model31(prices,dates):
    y,preds=base_candidates(prices,dates); n=len(prices)
    p31=np.full(n-1,np.nan)
    for t in range(300,n-1):
        name=selector31(y,preds,t); p31[t]=preds[name][t]
    return y,p31


def calibrated_series(y,p31,hl,mult):
    if hl is None: return p31.copy()
    out=np.full_like(p31,np.nan,dtype=float)
    for t in range(300,len(p31)):
        if not np.isfinite(p31[t]): continue
        idx=np.arange(max(300,t-2520),t)
        valid=np.isfinite(p31[idx]); idx=idx[valid]
        if len(idx)<126:
            out[t]=p31[t]; continue
        residual=y[idx]-p31[idx]
        age=t-1-idx; w=0.5**(age/hl)
        # zero-centered prior keeps small samples from over-correcting.
        bias=float(np.dot(w,residual)/(w.sum()+PRIOR_WEIGHT))
        out[t]=float(np.clip(p31[t]+mult*bias,0.05,0.95))
    return out


def brier(p,y,a,b):
    idx=np.arange(a,b); valid=np.isfinite(p[idx]); idx=idx[valid]
    return float(np.mean((p[idx]-y[idx])**2))


def logloss(p,y,a,b):
    idx=np.arange(a,b); valid=np.isfinite(p[idx]); idx=idx[valid]
    pp=np.clip(p[idx],1e-6,1-1e-6); yy=y[idx]
    return float(np.mean(-(yy*np.log(pp)+(1-yy)*np.log(1-pp))))


def main():
    data={}; dev_delta={name:[] for name,_,_ in CANDIDATES}
    for s in SYMBOLS:
        rows=fetch(s); dates=[d for d,_ in rows]; prices=np.array([p for _,p in rows],float)
        y,p31=build_model31(prices,dates); n=len(prices); start=n-1-EVAL; mid=start+EVAL//2
        series={name:calibrated_series(y,p31,hl,mult) for name,hl,mult in CANDIDATES}
        base=brier(p31,y,start,mid)
        for name,_,_ in CANDIDATES: dev_delta[name].append(brier(series[name],y,start,mid)-base)
        data[s]=(y,p31,series,start,mid,n)
    pooled_dev={k:float(np.mean(v)) for k,v in dev_delta.items()}
    selected=min(pooled_dev,key=pooled_dev.get)
    results=[]
    for s in SYMBOLS:
        y,p31,series,start,mid,n=data[s]; p=series[selected]
        full=brier(p,y,start,n-1); full31=brier(p31,y,start,n-1)
        dev=brier(p,y,start,mid); dev31=brier(p31,y,start,mid)
        hold=brier(p,y,mid,n-1); hold31=brier(p31,y,mid,n-1)
        ll=logloss(p,y,start,n-1); ll31=logloss(p31,y,start,n-1)
        results.append({
            'symbol':s,'selected':selected,
            'full_brier':full,'model31_full':full31,'full_skill_vs_31':(1-full/full31)*100,
            'dev_skill_vs_31':(1-dev/dev31)*100,'holdout_skill_vs_31':(1-hold/hold31)*100,
            'full_logloss':ll,'model31_logloss':ll31,
            'current_probability':float(p[n-2])*100,'model31_probability':float(p31[n-2])*100,
        })
    deploy=bool(selected!='identity' and pooled_dev[selected]<0 and all(r['full_skill_vs_31']>0 for r in results) and all(r['holdout_skill_vs_31']>0 for r in results) and all(r['full_logloss']<=r['model31_logloss'] for r in results))
    print('FINAL',json.dumps({'model':'3.2c-causal-calibration','dev_delta_brier':pooled_dev,'selected':selected,'results':results,'deploy':deploy},ensure_ascii=False),flush=True)

if __name__=='__main__': main()
