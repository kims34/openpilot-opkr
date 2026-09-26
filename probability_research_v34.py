"""Held-out probability calibration research for deployed model 3.1.

No new directional signals are added.  The causal v3.1 probability is either
left unchanged or shrunk toward its fixed historical base rate / 50%.  A single
shared calibration is selected on an older development window across SPY, QQQ,
and SCHD, then evaluated once on the newer untouched window.
"""
import json
import numpy as np

import probability_research_v32 as r
import probability_research_v32b as b

DEV = 504
HOLDOUT = 504


def score(p, y):
    return float(np.mean((p - y) ** 2))


def transforms(p31, fixed):
    out={"v31":p31.copy()}
    for a in (0.25,0.5,0.75):
        out[f"toward_fixed_{a}"]=fixed+a*(p31-fixed)
    for a in (0.5,0.75):
        out[f"toward_half_{a}"]=0.5+a*(p31-0.5)
    return out


def main():
    cache={}; common_names=None
    for s in r.SYMBOLS:
        rows=r.fetch(s); dates=[d for d,_ in rows]; prices=np.array([p for _,p in rows],float)
        y,cands=r.candidate_probs(prices,dates)
        p31,_=b.build_v31_policy(y,cands)
        n=len(prices); hold_start=n-1-HOLDOUT; dev_start=hold_start-DEV
        tr=transforms(p31,cands["fixed"])
        common_names=list(tr) if common_names is None else common_names
        cache[s]=(y,tr,dev_start,hold_start,n)

    dev_rows=[]
    for name in common_names:
        losses=[]; base=[]; half=[[],[]]
        for s in r.SYMBOLS:
            y,tr,dev_start,hold_start,n=cache[s]
            idx=np.arange(dev_start,hold_start)
            losses.extend(((tr[name][idx]-y[idx])**2).tolist())
            base.extend(((tr["v31"][idx]-y[idx])**2).tolist())
            mid=dev_start+DEV//2
            for k,sub in enumerate((np.arange(dev_start,mid),np.arange(mid,hold_start))):
                half[k].extend((((tr["v31"][sub]-y[sub])**2)-((tr[name][sub]-y[sub])**2)).tolist())
        br=float(np.mean(losses)); bb=float(np.mean(base))
        dev_rows.append({"name":name,"brier":br,"v31":bb,"skill_vs_v31":(1-br/bb)*100,
                         "first_half_adv":float(np.mean(half[0])),"second_half_adv":float(np.mean(half[1]))})

    eligible=[x for x in dev_rows if x["name"]!="v31" and x["brier"]<x["v31"] and x["first_half_adv"]>0 and x["second_half_adv"]>0]
    chosen=min(eligible,key=lambda x:x["brier"]) if eligible else None
    if not chosen:
        print("FINAL",json.dumps({"dev":sorted(dev_rows,key=lambda x:x["brier"]),"chosen":None,"deploy":False,"reason":"no calibration beat v3.1 in both development halves"},ensure_ascii=False),flush=True)
        return

    hold=[]
    for s in r.SYMBOLS:
        y,tr,dev_start,hold_start,n=cache[s]
        idx=np.arange(hold_start,n-1); p=tr[chosen["name"]][idx]; q=tr["v31"][idx]
        br=score(p,y[idx]); bb=score(q,y[idx]); mid=hold_start+HOLDOUT//2
        f=score(tr[chosen["name"]][hold_start:mid],y[hold_start:mid]); fb=score(tr["v31"][hold_start:mid],y[hold_start:mid])
        z=score(tr[chosen["name"]][mid:n-1],y[mid:n-1]); zb=score(tr["v31"][mid:n-1],y[mid:n-1])
        hold.append({"symbol":s,"brier_v34":br,"brier_v31":bb,"skill_vs_v31":(1-br/bb)*100,
                     "first_half_skill_vs_v31":(1-f/fb)*100,"second_half_skill_vs_v31":(1-z/zb)*100,
                     "current_probability_v34":float(tr[chosen["name"]][n-2])*100,
                     "current_probability_v31":float(tr["v31"][n-2])*100})
    p34=float(np.mean([x["brier_v34"] for x in hold])); p31=float(np.mean([x["brier_v31"] for x in hold]))
    deploy=bool(p34<p31 and sum(x["skill_vs_v31"]>0 for x in hold)>=2 and sum(x["second_half_skill_vs_v31"]>0 for x in hold)>=2 and min(x["second_half_skill_vs_v31"] for x in hold)>-0.03)
    print("FINAL",json.dumps({"dev":sorted(dev_rows,key=lambda x:x["brier"]),"chosen":chosen,"holdout":hold,"pooled_brier_v34":p34,"pooled_brier_v31":p31,"pooled_skill_vs_v31":(1-p34/p31)*100,"deploy":deploy,"promotion_rule":"single shared calibration selected on older 504d; newer 504d pooled win; >=2 symbols overall/recent; worst recent regression > -0.03%"},ensure_ascii=False),flush=True)


if __name__=="__main__": main()
