"""Frozen full-history 21-session 5% touch candidate. Never a public forecast."""
import math
import statistics

DIRECTIONS={'SPY':'down','QQQ':'up'}
MODEL='volatility-scaled-5pct-touch-shadow-v1'


def estimate(rows,symbol):
    if symbol not in DIRECTIONS:raise ValueError('unsupported candidate')
    if len(rows)<574:raise ValueError('insufficient history')
    dates=[r[0] for r in rows]
    if dates!=sorted(set(dates)):raise ValueError('unordered daily rows')
    for _,h,l,c in rows:
        if not all(math.isfinite(v) and v>0 for v in (h,l,c)) or not l<=c<=h:raise ValueError('invalid OHLC')
    prices=[r[3] for r in rows]
    returns=[math.log(prices[i]/prices[i-1]) for i in range(1,len(rows))]
    def sigma(i):return max(statistics.stdev(returns[i-21:i])*math.sqrt(21),.005)
    t=len(rows)-1;vol=sigma(t);direction=DIRECTIONS[symbol];base=0;scaled=0;count=0
    for i in range(252,t-21):
        if direction=='up':
            ratio=max(r[1] for r in rows[i+1:i+22])/prices[i]
            base+=ratio>=1.05;scaled+=math.log(ratio)*vol/sigma(i)>=math.log(1.05)
        else:
            ratio=min(r[2] for r in rows[i+1:i+22])/prices[i]
            base+=ratio<=.95;scaled+=math.log(ratio)*vol/sigma(i)<=math.log(.95)
        count+=1
    return {'model':MODEL,'symbol':symbol,'direction':direction,'probability':.5*(base+scaled)/count,
        'baseline_probability':base/count,'training_count':count,'training_latest':dates[t-22]}
