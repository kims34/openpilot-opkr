import math
import tempfile
import unittest
from unittest.mock import patch
import exchange_calendars as xcals
import annual_touch as annual
import annual_touch_model as model


class AnnualTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.db=self.temp.name+'/annual.db'
        dates=xcals.get_calendar('XNYS',start='2023-01-01',end='2028-06-01').sessions
        self.rows=[]
        for i,d in enumerate(dates):
            p=100*math.exp(.0001*i+.02*math.sin(i/13))
            self.rows.append((d.date().isoformat(),p*1.001,p*.999,p))
        self.t=next(i for i,r in enumerate(self.rows) if r[0]=='2026-11-13')
        self.opening,self.expires,self.maturity=annual.calendar('2026-11-13')
        self.meta={'as_of':'2026-11-13','target_open':self.opening}
    def tearDown(self):self.temp.cleanup()
    def issue(self,symbol='SPY',when=None):
        return annual.observe(symbol,[(d,c) for d,h,l,c in self.rows[:self.t+1]],self.meta,self.db,
            lambda symbol,closes:self.rows[:len(closes)],lambda:self.opening-100 if when is None else when)
    def test_all_year_targets_and_expiry(self):
        for symbol in ('SPY','QQQ','SCHD'):self.issue(symbol)
        self.issue()
        rows=annual.summary(self.db,self.opening-50)
        self.assertEqual(len(rows),12)
        self.assertTrue(all(r['horizon_sessions']==252 and r['stored_count']==1 for r in rows))
        self.assertTrue(all(r['target_date']==self.rows[self.t+252][0] for r in rows))
        self.assertTrue(all(not r['independent_confirmed'] for r in rows))
        self.assertEqual(annual.summary(self.db,self.expires),[])
    def test_late_estimates_are_timestamped_and_never_prospectively_scored(self):
        self.issue(when=self.opening+10)
        rows=annual.summary(self.db,self.opening+20)
        self.assertEqual(len(rows),4)
        self.assertTrue(all(r['computed_at']==self.opening+10 and not r['prospective_eligible'] for r in rows))
        self.score(252)
        with annual.connect(self.db) as con:
            self.assertEqual(con.execute('SELECT COUNT(outcome) FROM annual_touch_v1').fetchone()[0],0)
    def score(self,offset):
        cut=self.t+offset;closes=[(d,c) for d,h,l,c in self.rows[:cut+1]]
        annual.observe('SPY',closes,{'as_of':closes[-1][0],'target_open':0},self.db,
            lambda symbol,closes:self.rows[:len(closes)],lambda:self.opening+100000000)
    def test_day252_scores_but_day251_cannot(self):
        self.issue();d,h,l,c=self.rows[self.t+252];anchor=self.rows[self.t][3]
        self.rows[self.t+252]=(d,max(h,anchor*1.11),min(l,anchor*.89),c)
        self.score(251)
        with annual.connect(self.db) as con:self.assertEqual(con.execute('SELECT COUNT(outcome) FROM annual_touch_v1').fetchone()[0],0)
        self.score(252)
        with annual.connect(self.db) as con:
            self.assertEqual(con.execute('SELECT COUNT(outcome) FROM annual_touch_v1').fetchone()[0],4)
            self.assertEqual(con.execute('SELECT SUM(outcome) FROM annual_touch_v1').fetchone()[0],4)
    def test_changed_model_or_bad_bars_stay_hidden(self):
        self.issue()
        with patch.object(annual,'DIGEST','changed'):
            self.assertEqual(annual.summary(self.db,self.opening-50),[])
        rows=self.rows[:self.t+1];d,h,l,c=rows[-1];rows[-1]=(d,l,h,c)
        with self.assertRaises(ValueError):model.estimate_all(rows)


if __name__=='__main__':unittest.main()
