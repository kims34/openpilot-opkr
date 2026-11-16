"""Historical empirical estimates for all 21/63-session 5/10-percent barriers."""
import math
import statistics

MODEL='historical-volatility-touch-all-v1'


def estimate_all(rows):
    if len(rows)<617:raise ValueError('insufficient history')
    if [r[0] for r in rows]!=sorted(set(r[0] for r in rows)):raise ValueError('unordered OHLC')
    if any(not all(math.isfinite(v) and v>0 for v in (h,l,c)) or not l<=c<=h for _,h,l,c in rows):
        raise ValueError('invalid OHLC')
    prices=[r[3] for r in rows]
    returns=[math.log(prices[i]/prices[i-1]) for i in range(1,len(prices))]
    sigma={i:statistics.stdev(returns[i-21:i]) for i in range(252,len(rows))}
    t=len(rows)-1;out={}
    for horizon in (21,63):
        scale=math.sqrt(horizon);current=max(sigma[t]*scale,.005)
        paths=[]
        for i in range(252,t-horizon):
            future=rows[i+1:i+horizon+1]
            hi=max(r[1] for r in future)/prices[i];lo=min(r[2] for r in future)/prices[i]
            ratio=current/max(sigma[i]*scale,.005)
            paths.append((hi,lo,math.log(hi)*ratio,math.log(lo)*ratio))
        count=len(paths)
        for threshold in (5,10):
            fraction=threshold/100
            for direction in ('up','down'):
                if direction=='up':
                    base=sum(p[0]>=1+fraction for p in paths)
                    scaled=sum(p[2]>=math.log(1+fraction) for p in paths)
                else:
                    base=sum(p[1]<=1-fraction for p in paths)
                    scaled=sum(p[3]<=math.log(1-fraction) for p in paths)
                event=f'{horizon}:{direction}{threshold}_touch'
                out[event]=dict(probability=.5*(base+scaled)/count,baseline_probability=base/count,
                    training_count=count,training_latest=rows[t-horizon-1][0])
    return out
