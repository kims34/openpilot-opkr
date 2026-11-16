"""Fixed 63-session volatility-scaled empirical barrier model."""
import math
import statistics

MODEL='quarterly-volatility-scaled-touch-v1'
HORIZON=63


def estimate(rows, threshold, direction):
    if threshold not in (.05,.10) or direction not in ('up','down'):
        raise ValueError('unsupported target')
    if len(rows)<617:raise ValueError('insufficient history')
    if [r[0] for r in rows]!=sorted(set(r[0] for r in rows)):raise ValueError('unordered OHLC')
    if any(not all(math.isfinite(v) and v>0 for v in (h,l,c)) or not l<=c<=h for _,h,l,c in rows):
        raise ValueError('invalid OHLC')
    prices=[r[3] for r in rows]
    returns=[math.log(prices[i]/prices[i-1]) for i in range(1,len(prices))]
    def sigma(i):return max(statistics.stdev(returns[i-21:i])*math.sqrt(63),.005)
    t=len(rows)-1;current=sigma(t);base=scaled=count=0
    for i in range(252,t-HORIZON):
        path=rows[i+1:i+HORIZON+1]
        ratio=(max(r[1] for r in path) if direction=='up' else min(r[2] for r in path))/prices[i]
        if direction=='up':
            base+=ratio>=1+threshold;scaled+=math.log(ratio)*current/sigma(i)>=math.log(1+threshold)
        else:
            base+=ratio<=1-threshold;scaled+=math.log(ratio)*current/sigma(i)<=math.log(1-threshold)
        count+=1
    return dict(probability=.5*(base+scaled)/count,baseline_probability=base/count,
                training_count=count,training_latest=rows[t-HORIZON-1][0])
