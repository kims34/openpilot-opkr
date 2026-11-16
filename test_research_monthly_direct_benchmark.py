"""Regression tests: exact as-served legacy monthly model parity on fake OHLC."""
import unittest
from datetime import date, timedelta

import numpy as np

import research_monthly_direct_benchmark as bench
import research_monthly_touch_v1 as candidate


def synthetic(n=840):
    rng=np.random.default_rng(20261116)
    r=rng.normal(0.00025,0.013,size=n-1)
    p=100.0*np.exp(np.r_[0.0,np.cumsum(r)])
    start=date(2020,1,1)
    days=[(start+timedelta(days=i)).isoformat() for i in range(n)]
    close=list(zip(days,p.tolist()))
    bars=[(d,float(v*1.005),float(v*0.995),float(v)) for d,v in close]
    return close,bars


class ExactAppBaselineTest(unittest.TestCase):
    def test_replay_matches_original_unmodified_app_model(self):
        close,bars=synthetic()
        replay=bench.FastServedReplay(close,bars)
        t=820
        fast=replay.estimate(t)
        actual=replay.exact_app_estimate(t)
        for field in ("up","down","up_selected_k","down_selected_k",
                      "up_blend_weight","down_blend_weight"):
            self.assertAlmostEqual(fast[field],actual[field],places=8,
                                   msg=field)

    def test_future_prices_do_not_affect_past_forecast(self):
        close,bars=synthetic()
        t=740
        base=bench.FastServedReplay(close,bars).estimate(t)
        changed_close=close[:t+1]+[(d,v*4) for d,v in close[t+1:]]
        changed_bars=bars[:t+1]+[(d,hi*4,lo*4,c*4)
                                    for d,hi,lo,c in bars[t+1:]]
        altered=bench.FastServedReplay(changed_close,changed_bars).estimate(t)
        for field in ("up","down"):
            self.assertEqual(base[field],altered[field])

    def test_metric_gains_and_calibration(self):
        base=np.array([[.2,.3],[.4,.1],[.7,.2],[.3,.5]])
        improved=np.array([[.1,.1],[.1,.1],[.9,.1],[.1,.9]])
        y=np.array([[0,0],[0,0],[1,0],[0,1]],dtype=float)
        result=bench.metric(base,improved,y,block_size=2)
        self.assertEqual(result["n"],4)
        self.assertGreater(result["gain_combined"],0)
        self.assertEqual(result["event_count_up"],1)
        self.assertEqual(result["event_count_down"],1)

    def test_exact_asof_window_label_cutoff(self):
        close,bars=synthetic()
        a=bench.FastServedReplay(close,bars)
        t=790
        before=a.estimate(t)
        close2,bars2=list(close),list(bars)
        # Future-only intraday highs/lows cannot change today's prediction.
        for i in range(t+1,len(bars2)):
            d,high,low,c=bars2[i]
            bars2[i]=(d,high*1.2,low*.8,c)
        later=bench.FastServedReplay(close2,bars2).estimate(t)
        self.assertEqual(before["up"],later["up"])
        self.assertEqual(before["down"],later["down"])

    def test_no_close_substitution(self):
        close,bars=synthetic()
        with self.assertRaises(candidate.SourceQualityError):
            bench.FastServedReplay(close,bars[:-1])


if __name__=="__main__":
    unittest.main()
