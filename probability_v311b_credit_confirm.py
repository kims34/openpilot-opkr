"""Robustness confirmation for the fixed SPY v3.11 credit/volatility challenger.

No hyperparameter selection occurs here. The configuration was frozen from the
prior development+holdout experiment: window=504, ridge=300, cap=0.03.
We inspect causal walk-forward gain across chronological 126-session blocks.
"""
import numpy as np
import probability_v311_market_regimes as v311
import probability_model_v31_runtime as v32
import probability_model_v33_runtime as v33

CFG=(504,300.0,0.03)

def _b(p,y): return float(np.mean((np.asarray(p)-np.asarray(y))**2))

def evaluate(aligned,target_date):
    dates,prices=aligned['SPY']
    o=v33.estimate_prices(prices,include_trace=True,dates=dates,target_date=target_date)
    trace=o['audit_trace'] if o.get('calibration_gate_passed') else v32.estimate_prices(prices,include_trace=True,dates=dates,target_date=target_date)['audit_trace']
    pos=np.asarray([int(r['t']) for r in trace]); prev=np.asarray([float(r['probability']) for r in trace]); y=np.asarray([float(r['outcome']) for r in trace])
    x=v311._features(aligned,'credit_vol')[pos]
    pred=v311._pred(x,y,prev,CFG)
    # Most recent 1008 sessions, eight 126-session blocks. Parameters are fixed.
    start=max(0,len(y)-1008); blocks=[]
    for a in range(start,len(y),126):
        b=min(a+126,len(y))
        if b-a<100: continue
        gain=_b(prev[a:b],y[a:b])-_b(pred[a:b],y[a:b])
        blocks.append({'start_index':int(a),'end_index':int(b-1),'count':int(b-a),'gain':gain,'previous_brier':_b(prev[a:b],y[a:b]),'candidate_brier':_b(pred[a:b],y[a:b])})
    overall=_b(prev[start:],y[start:])-_b(pred[start:],y[start:])
    positive=sum(1 for z in blocks if z['gain']>0)
    return {'config':{'window':504,'ridge':300.0,'cap':0.03},'overall_gain_1008':overall,'positive_blocks':positive,'total_blocks':len(blocks),'all_blocks_positive':positive==len(blocks),'blocks':blocks}
