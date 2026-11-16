"""One-year (252-session) empirical touch estimates; same fixed 50:50 method."""
import math
import statistics

MODEL='annual-historical-volatility-touch-v1'
HORIZON=252


def estimate_all(rows):
    if len(rows)<805:raise ValueError('insufficient history')
    if [r[0] for r in rows]!=sorted(set(r[0] for r in rows)):raise ValueError('unordered OHLC')
    if any(not all(math.isfinite(v) and v>0 for v in (h,l,c)) or not l<=c<=h for _,h,l,c in rows):
        raise ValueError('invalid OHLC')
    prices=[r[3] for r in rows]
    returns=[math.log(prices[i]/prices[i-1]) for i in range(1,len(prices))]
    def sigma(i):return max(statistics.stdev(returns[i-21:i])*math.sqrt(HORIZON),.005)
    t=len(rows)-1;current=sigma(t);paths=[]
    for i in range(252,t-HORIZON):
        future=rows[i+1:i+HORIZON+1]
        hi=max(r[1] for r in future)/prices[i];lo=min(r[2] for r in future)/prices[i]
        ratio=current/sigma(i)
        paths.append((hi,lo,math.log(hi)*ratio,math.log(lo)*ratio))
    count=len(paths);out={}
    for threshold in (5,10):
        fraction=threshold/100
        for direction in ('up','down'):
            if direction=='up':
                base=sum(p[0]>=1+fraction for p in paths)
                scaled=sum(p[2]>=math.log(1+fraction) for p in paths)
            else:
                base=sum(p[1]<=1-fraction for p in paths)
                scaled=sum(p[3]<=math.log(1-fraction) for p in paths)
            out[f'252:{direction}{threshold}_touch']=dict(probability=.5*(base+scaled)/count,
                baseline_probability=base/count,training_count=count,training_latest=rows[t-253][0])
    return out
