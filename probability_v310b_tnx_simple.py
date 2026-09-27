"""Research-only simple prior-day 10Y Treasury yield challenger."""
import numpy as np
import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

CONFIGS=[(w,r,c) for w in (504,756,1008) for r in (100.0,300.0,1000.0,3000.0) for c in (0.005,0.01,0.02)]

def _trace(prices,dates,target_date):
    o=v33.estimate_prices(prices,include_trace=True,dates=dates,target_date=target_date)
    return o['audit_trace'] if o.get('calibration_gate_passed') else v32.estimate_prices(prices,include_trace=True,dates=dates,target_date=target_date)['audit_trace']

def _features(tnx):
    y=np.asarray(tnx,float)
    x=np.full((len(y),5),np.nan)
    for t in range(5,len(y)):
        d1=y[t]-y[t-1]
        x[t]=[y[t],d1,y[t]-y[t-5],abs(d1),1.0 if d1>0 else 0.0]
    return x

def _pred(x,outcomes,prev,cfg):
    w,ridge,cap=cfg; p=np.asarray(prev,float).copy()
    for j in range(len(outcomes)):
        if j<252 or not np.all(np.isfinite(x[j])): continue
        idx=np.arange(max(0,j-w),j)
        idx=idx[np.all(np.isfinite(x[idx]),axis=1)]
        if len(idx)<252: continue
        tr=x[idx]; mu=tr.mean(0); sd=np.maximum(tr.std(0,ddof=1),1e-6); z=(tr-mu)/sd
        res=outcomes[idx]-prev[idx]
        b=np.linalg.solve(z.T@z+ridge*np.eye(z.shape[1]),z.T@res)
        a=float(np.clip(((x[j]-mu)/sd)@b,-cap,cap))
        p[j]=float(np.clip(prev[j]+a,0.35,0.70))
    return p

def _b(p,y): return float(np.mean((np.asarray(p)-np.asarray(y))**2))

def evaluate(aligned,target_symbol,target_date):
    dates,target=aligned[target_symbol]; tr=_trace(target,dates,target_date)
    pos=np.asarray([int(r['t']) for r in tr]); prev=np.asarray([float(r['probability']) for r in tr]); out=np.asarray([float(r['outcome']) for r in tr])
    x=_features(aligned['^TNX'][1])[pos]; split=len(out)-252; devy=out[:split]; testy=out[split:]; pd=prev[:split]; pt=prev[split:]
    stable=[]
    for cfg in CONFIGS:
        p=_pred(x,out,prev,cfg); d=p[:split]; m=len(d)//2
        g=(_b(pd,devy)-_b(d,devy),_b(pd[:m],devy[:m])-_b(d[:m],devy[:m]),_b(pd[m:],devy[m:])-_b(d[m:],devy[m:]))
        if min(g)>0: stable.append((_b(d,devy),cfg,p,g))
    if not stable: return {'selected':None,'reason':'no stable development winner'}
    _,cfg,p,dg=min(stable,key=lambda z:z[0]); t=p[split:]; m=len(t)//2
    tg=(_b(pt,testy)-_b(t,testy),_b(pt[:m],testy[:m])-_b(t[:m],testy[:m]),_b(pt[m:],testy[m:])-_b(t[m:],testy[m:]))
    return {'selected':{'window':cfg[0],'ridge':cfg[1],'cap':cfg[2]},'dev_gain_all':dg[0],'dev_gain_first':dg[1],'dev_gain_second':dg[2],'previous_test_brier':_b(pt,testy),'test_brier':_b(t,testy),'test_gain_all':tg[0],'test_gain_first':tg[1],'test_gain_second':tg[2],'holdout_passed':min(tg)>0}
