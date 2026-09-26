import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import probability_model as model
import next_day_probability as api


def synthetic_prices(n=1500):
    return (100 * np.exp(np.cumsum(np.random.default_rng(741).normal(0.0002,0.012,n)))).tolist()


class ModelTests(unittest.TestCase):
    def test_core_ignores_future_prices_and_future_scaling(self):
        p = synthetic_prices()
        altered = p.copy()
        altered[900:] = [v*20 for v in altered[900:]]
        self.assertEqual(model.Model(p).core(899), model.Model(altered).core(899))

    def test_selection_can_find_real_signal(self):
        y = np.tile([0.,1.],300)
        past = np.column_stack((0.2+0.6*y, np.full(600,0.5), y)).tolist()
        self.assertEqual(model.choose_alpha(past),1.0)
        past = np.column_stack((0.8-0.6*y, np.full(600,0.5), y)).tolist()
        self.assertEqual(model.choose_alpha(past),0.0)

    def test_outer_predictions_unchanged_by_their_outcomes(self):
        p = synthetic_prices(1200)
        before = model.estimate_prices(p,True)
        t = before['audit_trace'][12]['t']
        changed = p.copy()
        changed[t+1] *= 1.2
        after = model.estimate_prices(changed,True)
        self.assertEqual(before['audit_trace'][12]['probability'],after['audit_trace'][12]['probability'])
        self.assertEqual(before['audit_trace'][12]['alpha'],after['audit_trace'][12]['alpha'])
        self.assertTrue(all(r['probability']==s['probability'] for r,s in zip(before['audit_trace'][:12],after['audit_trace'][:12])))

    def test_underperformance_is_not_clipped_to_zero(self):
        rows = [(0.9,0.5,float(i%2)) for i in range(504)]
        stats=model.summarize_audit(rows,0.9)
        self.assertLess(stats['backtest_skill'],0)
        self.assertEqual(stats['evidence'],'예측 우위 미확인')

    def test_no_pseudo_sample_probability_interval(self):
        r=model.estimate_prices(synthetic_prices(1200))
        self.assertIsNone(r['range_low']);self.assertIsNone(r['range_high'])
        self.assertEqual(r['validation_count'],375)
        json.dumps(r,allow_nan=False)

    def test_invalid_prices_fail(self):
        for price in [float('nan'),0,float('inf')]:
            p=synthetic_prices(1200);p[700]=price
            with self.assertRaises(ValueError):model.estimate_prices(p)


class DataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cal=api.calendar(2026)
        schedule=cls.cal.schedule.loc['2020-01-02':'2026-11-27']
        cls.raw={'timestamp':[int(t.timestamp()) for t in schedule['open']],
            'indicators':{'quote':[{'close':[100.+i*.01 for i in range(len(schedule))]}],
                          'adjclose':[{'adjclose':[999.]*len(schedule)}]}}

    def test_early_close_and_holiday(self):
        rows,meta=api.parse_history(self.raw,pd.Timestamp('2026-11-27T17:50Z').timestamp())
        self.assertEqual(meta['as_of'],'2026-11-25')
        self.assertEqual(meta['target_date'],'2026-11-27')
        self.assertEqual(meta['target_close'],int(pd.Timestamp('2026-11-27T18:00Z').timestamp()))
        _,meta=api.parse_history(self.raw,pd.Timestamp('2026-11-27T18:16Z').timestamp())
        self.assertEqual(meta['as_of'],'2026-11-27')
        self.assertEqual(meta['target_date'],'2026-11-30')
        self.assertNotEqual(rows[0][1],999.)

    def test_gaps_and_duplicates_rejected(self):
        for duplicate in [False,True]:
            raw=json.loads(json.dumps(self.raw))
            if duplicate:raw['timestamp'][10]=raw['timestamp'][9]
            else:raw['indicators']['quote'][0]['close'][10]=None
            with self.assertRaises(ValueError):api.parse_history(raw,pd.Timestamp('2026-11-28T00:00Z').timestamp())

    def test_stale_series_rejected(self):
        raw=json.loads(json.dumps(self.raw));raw['timestamp'].pop();raw['indicators']['quote'][0]['close'].pop()
        with self.assertRaises(ValueError):api.parse_history(raw,pd.Timestamp('2026-11-28T00:00Z').timestamp())

    def test_forecast_is_immutable_and_scored_once(self):
        with tempfile.TemporaryDirectory() as d,patch.object(api,'DB_PATH',d+'/forecast.db'):
            r=dict(as_of='2026-09-25',target_date='2026-09-28',target_open=100,probability=55.,base_rate=54.)
            api.record_forecast('SPY',r,[('2026-09-25',100)],90)
            r['probability']=90.
            stats=api.record_forecast('SPY',r,[('2026-09-25',100),('2026-09-28',101)],110)
            self.assertEqual(stats['prospective_count'],1)
            self.assertAlmostEqual(stats['prospective_brier'],(0.55-1)**2)
            stats2=api.record_forecast('SPY',r,[('2026-09-25',100),('2026-09-28',90)],120)
            self.assertEqual(stats,stats2)

    def test_late_prediction_not_added_to_prospective_test(self):
        with tempfile.TemporaryDirectory() as d,patch.object(api,'DB_PATH',d+'/forecast.db'):
            r=dict(as_of='2026-09-25',target_date='2026-09-28',target_open=100,probability=55.,base_rate=54.)
            api.record_forecast('SPY',r,[('2026-09-25',100)],110)
            with api.sqlite3.connect(api.DB_PATH) as con:
                self.assertEqual(con.execute('SELECT COUNT(*) FROM probability_forecasts').fetchone()[0],0)

    def test_expired_probability_not_served(self):
        with patch.object(api,'CACHE',{'updated':0,'items':{'sp500':{'probability':99,'valid_until':1}}}),patch.object(api.threading.Thread,'start'):
            result=api.get_all()
            self.assertNotIn('probability',result['items']['sp500'])

if __name__=='__main__':unittest.main()
