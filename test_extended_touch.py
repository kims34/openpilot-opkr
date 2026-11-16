import unittest
from unittest.mock import patch
import test_annual_touch as fixtures
import extended_touch as extended
import extended_touch_model as model
import historical_touch_model as prior
import annual_touch_model as annual


class ExtendedTests(unittest.TestCase):
    def setUp(self):fixtures.AnnualTests.setUp(self)
    def tearDown(self):self.temp.cleanup()
    def issue(self,symbol='SPY',when=None):
        extended.observe(symbol,[(d,c) for d,h,l,c in self.rows[:self.t+1]],self.meta,self.db,
            lambda symbol,closes:self.rows[:len(closes)],lambda:self.opening-100 if when is None else when)
    def test_all_36_extended_targets_are_immutable_and_descriptive(self):
        for symbol in ('SPY','QQQ','SCHD'):self.issue(symbol)
        self.issue()
        rows=extended.summary(self.db,self.opening-50)
        self.assertEqual(len(rows),36)
        self.assertEqual({r['horizon_sessions'] for r in rows},{21,63,252})
        self.assertEqual({r['threshold_percent'] for r in rows},{15,20})
        self.assertTrue(all(r['stored_count']==1 and not r['independent_confirmed'] for r in rows))
        self.assertEqual(extended.summary(self.db,self.expires),[])
    def test_separate_21_63_252_maturities(self):
        self.issue()
        for offset,expected in [(20,0),(21,4),(62,4),(63,8),(251,8),(252,12)]:
            cut=self.t+offset;closes=[(d,c) for d,h,l,c in self.rows[:cut+1]]
            extended.observe('SPY',closes,{'as_of':closes[-1][0],'target_open':0},self.db,
                lambda symbol,closes:self.rows[:len(closes)],lambda:self.opening+100000000)
            with extended.connect(self.db) as con:
                self.assertEqual(con.execute('SELECT COUNT(outcome) FROM extended_touch_v1').fetchone()[0],expected)
    def test_late_estimates_cannot_be_prospective_scores(self):
        self.issue(when=self.opening+10)
        rows=extended.summary(self.db,self.opening+20)
        self.assertEqual(len(rows),12)
        self.assertTrue(all(not r['prospective_eligible'] for r in rows))
        cut=self.t+252;closes=[(d,c) for d,h,l,c in self.rows[:cut+1]]
        extended.observe('SPY',closes,{'as_of':closes[-1][0],'target_open':0},self.db,
            lambda symbol,closes:self.rows[:len(closes)],lambda:self.opening+100000000)
        with extended.connect(self.db) as con:
            self.assertEqual(con.execute('SELECT COUNT(outcome) FROM extended_touch_v1').fetchone()[0],0)
        with patch.object(extended,'DIGEST','changed'):
            self.assertEqual(extended.summary(self.db,self.opening+20),[])
    def test_threshold_probabilities_are_monotone_without_normalising(self):
        rows=self.rows[:self.t+1]
        p={**prior.estimate_all(rows),**annual.estimate_all(rows),**model.estimate_all(rows)}
        for h in (21,63,252):
            for side in ('up','down'):
                values=[p[f'{h}:{side}{t}_touch']['probability'] for t in (5,10,15,20)]
                self.assertEqual(values,sorted(values,reverse=True))
                self.assertTrue(all(0<=v<=1 for v in values))


if __name__=='__main__':unittest.main()
