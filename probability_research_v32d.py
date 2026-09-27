"""Model 3.2d research: asset-specific causal calibration.

Each ETF may have a different forecast bias. Candidate calibration is selected
separately using the first 756 forecasts of the latest 1,008. The most recent
252 forecasts (~1 trading year) are untouched final holdout. A calibration is
eligible only if it improves both Brier and log loss on the final holdout,
improves full-period Brier, and had non-negative skill in at least 2 of the 3
252-day development blocks. Otherwise that ETF remains exactly model 3.1.
This research branch never changes production unless the promotion gate passes.
"""
import json
import numpy as np
from probability_research_v32 import SYMBOLS,EVAL,fetch
from probability_research_v32c import CANDIDATES,build_model31,calibrated_series,brier,logloss


def main():
    results=[]; any_promoted=False
    for s in SYMBOLS:
        rows=fetch(s); dates=[d for d,_ in rows]; prices=np.array([p for _,p in rows],float)
        y,p31=build_model31(prices,dates); n=len(prices); start=n-1-EVAL
        dev_end=start+756; hold_start=dev_end
        series={name:calibrated_series(y,p31,hl,mult) for name,hl,mult in CANDIDATES}
        # Choose only from development period, with block-stability preference.
        candidates=[]
        for name,_,_ in CANDIDATES:
            if name=='identity': continue
            skills=[]
            for j in range(3):
                a=start+j*252; b=a+252
                cb=brier(series[name],y,a,b); bb=brier(p31,y,a,b)
                skills.append((1-cb/bb)*100)
            dev=brier(series[name],y,start,dev_end); dev31=brier(p31,y,start,dev_end)
            dev_skill=(1-dev/dev31)*100
            stable=sum(x>=0 for x in skills)>=2
            if stable and dev_skill>0:
                candidates.append((dev, name, dev_skill, skills))
        chosen='identity'; dev_skill=0.0; block_skills=[0.0,0.0,0.0]
        if candidates:
            _,chosen,dev_skill,block_skills=min(candidates,key=lambda x:x[0])
        p=series[chosen]
        full=brier(p,y,start,n-1); full31=brier(p31,y,start,n-1)
        hold=brier(p,y,hold_start,n-1); hold31=brier(p31,y,hold_start,n-1)
        hold_ll=logloss(p,y,hold_start,n-1); hold_ll31=logloss(p31,y,hold_start,n-1)
        hold_skill=(1-hold/hold31)*100
        full_skill=(1-full/full31)*100
        promoted=bool(chosen!='identity' and dev_skill>0 and full_skill>0 and hold_skill>0 and hold_ll<=hold_ll31)
        effective=chosen if promoted else 'identity'
        peff=series[effective]
        results.append({
            'symbol':s,'development_choice':chosen,'promoted':promoted,'effective':effective,
            'development_skill':dev_skill,'development_block_skills':block_skills,
            'holdout_252_skill':hold_skill,'full_1008_skill':full_skill,
            'holdout_logloss':hold_ll,'model31_holdout_logloss':hold_ll31,
            'candidate_current_probability':float(p[n-2])*100,
            'effective_current_probability':float(peff[n-2])*100,
            'model31_probability':float(p31[n-2])*100,
        })
        any_promoted=any_promoted or promoted
    print('FINAL',json.dumps({'model':'3.2d-asset-calibration','results':results,'any_promoted':any_promoted},ensure_ascii=False),flush=True)

if __name__=='__main__': main()
