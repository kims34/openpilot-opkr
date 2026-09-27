"""Research-only cross-market ridge-logistic challenger for v3.3.
Uses only completed daily data available by each forecast close.
"""
import json,time
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import numpy as np, requests
import next_day_probability as data
from probability_model_v33_runtime import estimate_prices as v33
import probability_research_v34c as c

NY=ZoneInfo('America/New_York'); SYMBOLS=('SPY','QQQ','SCHD'); BLEND=.15; RIDGE=20.; TRAIN=1260; MIN_TRAIN=504
CROSS=('^VIX','^TNX','DX-Y.NYB','HYG','TLT','SPY','QQQ')

def close_map(symbol):
    r=requests.get(f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}',params={'range':'10y','interval':'1d','includePrePost':'false','events':'div,splits'},headers={'User-Agent':'Mozilla/5.0 IndexAlert/research'},timeout=20); r.raise_for_status()
    z=(r.json().get('chart',{}).get('result') or [None])[0]
    if not z: raise RuntimeError(symbol)
    q=(z.get('indicators',{}).get('quote') or [{}])[0].get('close') or []; out={}
    for ts,v in zip(z.get('timestamp') or [],q):
        if v is None: continue
        d=datetime.fromtimestamp(int(ts),timezone.utc).astimezone(NY).date().isoformat(); x=float(v)
        if np.isfinite(x) and x>0: out[d]=x
    return out

def build(rows,maps):
    dates=[d for d,_ in rows]; p=np.array([x for _,x in rows],float); n=len(p); r=np.full(n,np.nan); r[1:]=p[1:]/p[:-1]-1
    X=np.full((n,11),np.nan)
    for t in range(21,n):
        d=dates[t]; prev=dates[t-1]
        vals=[]; ok=True
        for sym in CROSS:
            m=maps[sym]
            if d not in m or prev not in m: ok=False; break
            if sym=='^VIX': vals.extend([m[d]/30.,m[d]/m[prev]-1])
            elif sym=='^TNX': vals.append(m[d]-m[prev])
            else: vals.append(m[d]/m[prev]-1)
        if not ok: continue
        X[t]=[np.clip(r[t],-.08,.08),np.clip(p[t]/p[t-5]-1,-.2,.2),np.clip(p[t]/p[t-20]-1,-.35,.35),np.clip(float(np.std(r[t-19:t+1],ddof=1)),0,.1),*vals]
    return p,X

def fit(X,y,t):
    lo=max(21,t-TRAIN); A=X[lo:t]; yy=y[lo:t]; ok=np.all(np.isfinite(A),axis=1)&np.isfinite(yy); A=A[ok]; yy=yy[ok]
    if len(yy)<MIN_TRAIN or not np.all(np.isfinite(X[t])): return np.nan
    mu=A.mean(0); sd=A.std(0); sd=np.where(sd<1e-8,1.,sd); Z=(A-mu)/sd; z=(X[t]-mu)/sd; D=np.column_stack([np.ones(len(Z)),Z]); xt=np.r_[1.,z]
    b=np.zeros(D.shape[1]); pen=np.r_[0.,np.full(D.shape[1]-1,RIDGE)]
    for _ in range(20):
        ph=c.sigmoid(D@b); w=np.maximum(ph*(1-ph),1e-5); g=D.T@(ph-yy)+pen*b; H=(D.T*w)@D+np.diag(pen)+np.eye(D.shape[1])*1e-8
        try: step=np.linalg.solve(H,g)
        except np.linalg.LinAlgError: return np.nan
        b-=step
        if np.max(np.abs(step))<1e-6: break
    return float(c.sigmoid(xt@b))

def parts(p,y):
    z=(p-y)**2;m=len(z)//2;return {'full':float(z.mean()),'first':float(z[:m].mean()),'second':float(z[m:].mean()),'recent252':float(z[-252:].mean())}

def main():
    maps={s:close_map(s) for s in CROSS}; out={}
    for sym in SYMBOLS:
        rows,meta=data.fetch_history(sym,time.time()); dates=[d for d,_ in rows]; p,X=build(rows,maps); yf=(p[1:]>p[:-1]).astype(float)
        old=v33(p,include_trace=True,dates=dates,target_date=meta['target_date']); tr=old['audit_trace']; pos=np.array([int(x['t']) for x in tr]); base=np.array([float(x['probability']) for x in tr]); yy=np.array([float(x['outcome']) for x in tr])
        raw=np.array([fit(X,yf,int(t)) for t in pos]); cand=np.where(np.isfinite(raw),(1-BLEND)*base+BLEND*raw,np.nan); served,used=c.causal_gate(base,cand,yy); bl=parts(base,yy); lp=parts(served,yy); gain={k:float(bl[k]-lp[k]) for k in bl}
        out[sym]={'as_of':meta['as_of'],'v33_probability':float(old['probability']),'passed':bool(all(gain[k]>0 for k in gain)),'active_days':int(sum(used)),'gain':gain,'raw_current':None if not np.isfinite(fit(X,yf,len(p)-1)) else float(fit(X,yf,len(p)-1)*100)}
    print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
