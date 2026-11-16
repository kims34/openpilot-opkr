import math
import sqlite3
import tempfile
import unittest
from datetime import date,timedelta
from unittest.mock import patch,Mock
import monthly_touch_shadow as shadow
import monthly_touch_shadow_model as model


def sample_rows(n=900):
    rows=[];day=date(2022,1,3);p=100.
    while len(rows)<n:
        if day.weekday()<5:
            i=len(rows);p*=math.exp(.003*math.sin(i/7)+.0002)
            rows.append((day.isoformat(),p*1.008,p*.992,p))
        day+=timedelta(days=1)
    return rows


class CandidateObserverTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.db=self.temp.name+'/test.db';self.rows=sample_rows();self.t=650
        self.meta={'as_of':self.rows[self.t][0],'target_date':self.rows[self.t+1][0],'target_open':200}
        self.supplier=lambda symbol,closes:self.rows[:len(closes)]
    def tearDown(self):self.temp.cleanup()
    def closes(self,t):return [(d,c) for d,h,l,c in self.rows[:t+1]]
    def issue(self,symbol='SPY',clock=lambda:100):
        with patch('monthly_prospective._maturity',return_value=self.rows[self.t+21][0]):
            return shadow.observe(symbol,self.closes(self.t),self.meta,self.db,self.supplier,clock)

    def test_first_preopen_forecast_is_never_replaced(self):
        self.assertTrue(self.issue()['inserted'])
        with sqlite3.connect(self.db) as con:before=con.execute('SELECT * FROM monthly_touch_shadow_v1').fetchone()
        supplier=Mock(side_effect=AssertionError('no duplicate fetch'))
        result=shadow.observe('SPY',self.closes(self.t),self.meta,self.db,supplier,lambda:110)
        self.assertFalse(result['inserted'])
        with sqlite3.connect(self.db) as con:self.assertEqual(before,con.execute('SELECT * FROM monthly_touch_shadow_v1').fetchone())

    def test_late_reconstructed_forecast_is_not_admitted(self):
        self.assertFalse(self.issue(clock=lambda:201)['inserted'])
        self.assertEqual(shadow.summary(self.db)['SPY']['stored_count'],0)

    def test_inference_crossing_open_is_not_backdated(self):
        times=iter((100,201))
        self.assertFalse(self.issue(clock=lambda:next(times))['inserted'])

    def test_requires_all_twenty_one_complete_future_sessions(self):
        self.issue()
        for offset,expected in ((20,0),(21,1)):
            t=self.t+offset;meta=dict(self.meta,as_of=self.rows[t][0])
            result=shadow.observe('SPY',self.closes(t),meta,self.db,self.supplier,lambda:300)
            self.assertEqual(result['scored'],expected)
        self.assertEqual(shadow.summary(self.db)['SPY']['scored_count'],1)

    def test_intraday_touch_counts_when_terminal_close_does_not(self):
        for symbol,side in (('SPY','down'),('QQQ','up')):
            self.issue(symbol)
        d,h,l,c=self.rows[self.t+1];anchor=self.rows[self.t][3]
        self.rows[self.t+1]=(d,max(h,anchor*1.06),min(l,anchor*.94),c)
        t=self.t+21;meta=dict(self.meta,as_of=self.rows[t][0])
        for symbol in ('SPY','QQQ'):
            shadow.observe(symbol,self.closes(t),meta,self.db,self.supplier,lambda:300)
        with sqlite3.connect(self.db) as con:
            self.assertEqual(con.execute('SELECT SUM(outcome) FROM monthly_touch_shadow_v1').fetchone()[0],2)

    def test_missing_scoring_bar_does_not_invent_result(self):
        self.issue();t=self.t+21;meta=dict(self.meta,as_of=self.rows[t][0])
        def incomplete(symbol,closes):return [r for r in self.rows[:t+1] if r[0]!=self.rows[self.t+3][0]]
        self.assertEqual(shadow.observe('SPY',self.closes(t),meta,self.db,incomplete,lambda:300)['scored'],0)

    def test_source_revision_of_original_anchor_blocks_score(self):
        self.issue();t=self.t+21;closes=self.closes(t);d,p=closes[self.t];closes[self.t]=(d,p*.9)
        self.assertEqual(shadow.observe('SPY',closes,dict(self.meta,as_of=self.rows[t][0]),self.db,self.supplier,lambda:300)['scored'],0)

    def test_summary_never_exposes_forecast_or_self_promotes(self):
        self.issue();r=shadow.summary(self.db)['SPY']
        self.assertFalse(r['display_allowed']);self.assertNotIn('probability',r)
        self.assertEqual(r['target_label'],'SPY 21거래일 내 -5% 도달')
        self.assertEqual(r['next_maturity_session'],self.rows[self.t+21][0])

    def test_unknown_symbol_and_anchor_metadata_fail_closed(self):
        self.assertEqual(shadow.observe('SCHD',[],{},self.db)['status'],'not_tracked')
        with self.assertRaises(ValueError):shadow.observe('SPY',self.closes(self.t),dict(self.meta,as_of='2000-01-01'),self.db,self.supplier,lambda:100)

    def test_model_has_minimum_data_and_bounded_probabilities(self):
        with self.assertRaises(ValueError):model.estimate(self.rows[:500],'SPY')
        for symbol in ('SPY','QQQ'):
            r=model.estimate(self.rows,symbol)
            self.assertTrue(0<=r['probability']<=1)
            self.assertEqual(r['training_latest'],self.rows[-23][0])


if __name__=='__main__':unittest.main()
