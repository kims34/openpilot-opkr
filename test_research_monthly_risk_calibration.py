"""Standalone prevention of future-label leakage in risk-calibration research."""
import copy
import math
import tempfile
import unittest
from datetime import date,timedelta
from pathlib import Path

import research_monthly_risk_calibration as model


def fixture(n=420):
    rows=[]
    d=date(2019,1,1)
    for i in range(n):
        day=d+timedelta(days=i)
        close=100.0*math.exp(0.001*i+0.017*math.sin(i/14))
        p=0.04+0.02*abs(math.sin(i/30))
        rows.append({
            "as_of":day.isoformat(),
            "maturity":(day+timedelta(days=21)).isoformat(),
            "close":close,
            "p":{"up":p,"down":p+0.03},
            "base":{"up":0.05,"down":0.08},
            "hit":{"up":int(i%27<3),"down":int(i%31<4)},
            "full10":True,
            "ret21":None,"vol21":None,"stress":False,"extreme":False,
        })
    for i,r in enumerate(rows):
        if i>=model.HORIZON:
            prev=rows[i-21]["close"]
            r["ret21"]=r["close"]/prev-1
            delta=[math.log(rows[j]["close"]/rows[j-1]["close"]) for j in range(i-20,i+1)]
            mean=sum(delta)/len(delta)
            variance=sum((x-mean)**2 for x in delta)/(len(delta)-1)
            r["vol21"]=math.sqrt(variance*252)
            r["stress"]=r["vol21"]>=.25 or r["ret21"]<=-.05
    return rows


class CalibrationResearchTests(unittest.TestCase):
    def test_maturity_guard_blocks_today_and_future(self):
        rows=fixture()
        current=360
        known=model.eligible_indices(rows,current)
        self.assertTrue(known)
        self.assertTrue(all(rows[t]["maturity"]<rows[current]["as_of"] for t in known))
        with self.assertRaises(ValueError):
            model.apply_on_date(rows,current,history_override=[current-21])
        with self.assertRaises(ValueError):
            model.apply_on_date(rows,current,history_override=[current+1])

    def test_unmatured_labels_can_never_alter_current_prediction(self):
        rows=fixture()
        t=350
        a=model.apply_on_date(rows,t)
        changed=copy.deepcopy(rows)
        for i in range(t-20,len(changed)):
            changed[i]["hit"]={"up":1-changed[i]["hit"]["up"],
                               "down":1-changed[i]["hit"]["down"]}
        b=model.apply_on_date(changed,t)
        self.assertEqual(a,b)

    def test_future_prices_never_used_in_regime_detection(self):
        rows=fixture()
        t=380
        original=model.apply_on_date(rows,t)
        after=copy.deepcopy(rows)
        for j in range(t+1,len(after)):
            after[j]["close"] *= 100.0
        self.assertEqual(original,model.apply_on_date(after,t))

    def test_logistic_calibration_clipped_and_regularized(self):
        self.assertEqual(model.fitted_offset([0.1]*20,[0]*20),0.0)
        self.assertEqual(model.fitted_offset([0.1]*300,[0]*300),0.0)
        self.assertGreater(model.fitted_offset([0.01]*400,[1]*50+[0]*350),0)
        self.assertLess(model.fitted_offset([0.3]*400,[1]*10+[0]*390),0)
        for p in (0.0,0.5,1.0):
            z=model.expit(model.clipped_logit(p))
            self.assertTrue(0<z<1)

    def test_diagnostic_never_labels_low_probability_as_correct_direction(self):
        rows=fixture()
        t=370
        probs,info=model.apply_on_date(rows,t)
        for candidate in model.CANDIDATES:
            for side in model.SIDES:
                self.assertGreaterEqual(probs[candidate][side],0)
                self.assertLessEqual(probs[candidate][side],1)
        self.assertEqual(probs["quarter_base"]["up"],
                         0.75*rows[t]["p"]["up"]+0.25*rows[t]["base"]["up"])

    def test_score_and_block_ci_no_promotion(self):
        sample=[]
        for t in range(50):
            item={"true_up":int(t%10==0),"true_down":int(t%9==0),
                  "stress":t%2==0}
            for candidate in model.CANDIDATES:
                for side in model.SIDES:
                    item[candidate+"_"+side]=.1 if candidate=="original" else .15
            sample.append(item)
        result=model._metric(sample)
        self.assertEqual(result["n"],50)
        self.assertEqual(result["events_up"],5)
        ci=model.bootstrap_gain(sample,"quarter_base")
        self.assertEqual(len(ci),2)
        self.assertTrue(all(math.isfinite(x) for x in ci))

    def test_expected_input_missing_blocks(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                model.run(d,Path(d)/"out")


if __name__=="__main__":
    unittest.main()
