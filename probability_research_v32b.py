"""Model 3.2b research: reduce selection overfit instead of adding signals.

Four pre-specified policies are compared with production model 3.1:
- strict3: existing challengers must beat fixed baseline in each of 3 thirds
- strict3_shrink75: strict3 challenger moved 25% back toward fixed
- strict3_shrink50: strict3 challenger moved 50% back toward fixed
- model31_shrink50: original 3.1 choice moved 50% back toward fixed

The first 504 forecasts choose one global policy across SPY/QQQ/SCHD. The
second 504 forecasts are the untouched promotion holdout. Production is only
eligible if the chosen policy improves Brier on every ETF on the holdout and
over the full 1,008 forecasts.
"""
import json, math
import numpy as np
from probability_research_v32 import SYMBOLS, EVAL, LOOKBACK, fetch, base_candidates, selector31

POLICIES=['strict3','strict3_shrink75','strict3_shrink50','model31_shrink50']


def selector_strict3(y,preds,t):
    fixed=preds['fixed']; start=max(300,t-LOOKBACK); edges=[start,start+(t-start)//3,start+2*(t-start)//3,t]
    best=('fixed',0.0)
    for name in ['adaptive_hl','prev_sign','weekday']:
        p=preds[name]
        if np.isnan(p[t]): continue
        gains=[]; ok=True
        for a,b in zip(edges[:-1],edges[1:]):
            idx=np.arange(a,b); idx=idx[~np.isnan(p[idx]) & ~np.isnan(fixed[idx])]
            if len(idx)<50: ok=False; break
            gains.append(float(np.mean((fixed[idx]-y[idx])**2-(p[idx]-y[idx])**2)))
        if ok and min(gains)>0 and sum(gains)>best[1]: best=(name,sum(gains))
    return best[0]


def build_policies(prices,dates):
    y,preds=base_candidates(prices,dates); n=len(prices); fixed=preds['fixed']
    p31=np.full(n-1,np.nan); strict=np.full(n-1,np.nan)
    p31_names=[]; strict_names=[]
    for t in range(300,n-1):
        a=selector31(y,preds,t); b=selector_strict3(y,preds,t)
        p31[t]=preds[a][t]; strict[t]=preds[b][t]; p31_names.append(a); strict_names.append(b)
    out={
        'strict3': strict,
        'strict3_shrink75': 0.75*strict+0.25*fixed,
        'strict3_shrink50': 0.50*strict+0.50*fixed,
        'model31_shrink50': 0.50*p31+0.50*fixed,
    }
    return y,p31,out,p31_names,strict_names


def brier(p,y,a,b):
    idx=np.arange(a,b); valid=np.isfinite(p[idx]); idx=idx[valid]
    return float(np.mean((p[idx]-y[idx])**2))


def main():
    data={}; dev_scores={k:[] for k in POLICIES}
    for s in SYMBOLS:
        rows=fetch(s); dates=[d for d,_ in rows]; prices=np.array([p for _,p in rows],float)
        y,p31,pol,p31names,strictnames=build_policies(prices,dates); n=len(prices); start=n-1-EVAL; mid=start+EVAL//2
        data[s]=(y,p31,pol,start,mid,n,p31names,strictnames)
        base_dev=brier(p31,y,start,mid)
        for k in POLICIES: dev_scores[k].append(brier(pol[k],y,start,mid)-base_dev)
    pooled_dev={k:float(np.mean(v)) for k,v in dev_scores.items()}
    selected=min(POLICIES,key=lambda k:pooled_dev[k])
    results=[]
    for s in SYMBOLS:
        y,p31,pol,start,mid,n,p31names,strictnames=data[s]; p=pol[selected]
        full=brier(p,y,start,n-1); full31=brier(p31,y,start,n-1)
        dev=brier(p,y,start,mid); dev31=brier(p31,y,start,mid)
        hold=brier(p,y,mid,n-1); hold31=brier(p31,y,mid,n-1)
        results.append({
            'symbol':s,'selected':selected,
            'full_brier':full,'model31_full':full31,'full_skill_vs_31':(1-full/full31)*100,
            'dev_skill_vs_31':(1-dev/dev31)*100,'holdout_skill_vs_31':(1-hold/hold31)*100,
            'current_probability':float(p[n-2])*100,'model31_probability':float(p31[n-2])*100,
            'model31_challenger_days':sum(x!='fixed' for x in p31names[-EVAL:]),
            'strict3_challenger_days':sum(x!='fixed' for x in strictnames[-EVAL:]),
        })
    deploy=bool(pooled_dev[selected]<0 and all(r['full_skill_vs_31']>0 for r in results) and all(r['holdout_skill_vs_31']>0 for r in results))
    print('FINAL',json.dumps({'model':'3.2b-selection-regularization','dev_delta_brier':pooled_dev,'selected':selected,'results':results,'deploy':deploy},ensure_ascii=False),flush=True)

if __name__=='__main__': main()
