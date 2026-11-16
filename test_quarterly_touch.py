import math
import sqlite3
import tempfile
import unittest
from unittest.mock import patch
import exchange_calendars as xcals
import quarterly_touch as quarter


class QuarterlyLedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.db=self.temp.name+'/ledger.db'
        dates=xcals.get_calendar('XNYS',start='2023-01-01',end='2027-06-01').sessions
        self.rows=[]
        for i,d in enumerate(dates):
            p=100*math.exp(.0001*i+.02*math.sin(i/13))
            self.rows.append((d.date().isoformat(),p*1.001,p*.999,p))
        self.t=next(i for i,r in enumerate(self.rows) if r[0]=='2026-11-13')
        self.opening,self.expires,self.maturity=quarter.calendar('2026-11-13')
        self.meta={'as_of':'2026-11-13','target_open':self.opening}
    def tearDown(self):self.temp.cleanup()
    def issue(self,clock=None):
        return quarter.observe('SPY',[(d,c) for d,h,l,c in self.rows[:self.t+1]],self.meta,self.db,
            lambda symbol,closes:self.rows[:len(closes)],clock or (lambda:self.opening-100))
    def test_issued_once_historical_status_and_expiry(self):
        self.issue();self.issue()
        f=quarter.summary(self.db,self.opening-50)
        self.assertEqual(len(f),1);self.assertEqual(f[0]['stored_count'],1)
        self.assertEqual(f[0]['horizon_sessions'],63)
        self.assertFalse(f[0]['independent_confirmed'])
        self.assertEqual(quarter.summary(self.db,self.expires),[])
    def test_open_crossing_cannot_backdate_forecast(self):
        times=iter([self.opening-1,self.opening+1])
        self.issue(lambda:next(times))
        self.assertEqual(quarter.summary(self.db,self.opening+2),[])
    def test_unaccepted_target_and_changed_model_stay_hidden(self):
        self.issue()
        with patch.object(quarter,'DIGEST','changed'):
            self.assertEqual(quarter.summary(self.db,self.opening-50),[])
        with quarter.connect(self.db) as con:
            con.execute("UPDATE quarterly_touch_v1 SET event='up10_touch'")
        self.assertEqual(quarter.summary(self.db,self.opening-50),[])
    def test_only_complete_63_session_path_scores_and_intraday_touch_counts(self):
        self.issue();d,h,l,c=self.rows[self.t+1];anchor=self.rows[self.t][3]
        self.rows[self.t+1]=(d,max(h,anchor*1.06),l,c)
        for offset,scored in [(62,0),(63,1)]:
            cut=self.t+offset;closes=[(d,c) for d,h,l,c in self.rows[:cut+1]]
            quarter.observe('SPY',closes,{'as_of':closes[-1][0],'target_open':0},self.db,
                lambda symbol,closes:self.rows[:len(closes)],lambda:self.opening+10000000)
            with quarter.connect(self.db) as con:
                count=con.execute('SELECT COUNT(outcome) FROM quarterly_touch_v1').fetchone()[0]
                self.assertEqual(count,scored)
                if scored:self.assertEqual(con.execute('SELECT outcome FROM quarterly_touch_v1').fetchone()[0],1)


if __name__=='__main__':unittest.main()
