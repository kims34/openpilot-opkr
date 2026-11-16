import ast
import copy
from pathlib import Path
import unittest
from types import SimpleNamespace
from verified_probability_display import public_probability_payload


class VerifiedDisplayTests(unittest.TestCase):
    def setUp(self):
        self.payload={'items':{'sp500':{'symbol':'SPY','model_version':'3.3-calibration-gated',
            'probability':58.,'base_rate':53.,'candidate_probability':65.,
            'backtest_skill':15.,'verified_advantage':True,'live_gate_status':'live_confirmed',
            'display_allowed':True,'verification_status':'independent_confirmed',
            'one_month':{'up_10_probability':30.,'down_10_probability':20.,
                'terminal_return_six_bins':[{'probability':60.}]},
            'first_hour':{'probability':80.,'available':True,'model_version':'4.0'},
            'unknown_new_overlay':{'probability':90.}}}}

    def test_historical_or_self_declared_success_cannot_enable_display(self):
        result=public_probability_payload(self.payload)
        item=result['items']['sp500']
        self.assertIsNone(item['probability'])
        self.assertFalse(item['display_allowed'])
        self.assertIn('검증 완료',item['error'])
        self.assertNotIn('base_rate',item)
        self.assertNotIn('candidate_probability',item)
        self.assertNotIn('unknown_new_overlay',item)
        for layer in ('one_month','first_hour'):
            self.assertFalse(item[layer]['available'])
            self.assertIsNone(item[layer]['probability'])
        self.assertNotIn('terminal_return_six_bins',item['one_month'])

    def test_no_50_percent_or_base_rate_replacement(self):
        result=public_probability_payload({'items':{'ndx':{'probability':None,'base_rate':50.,'served_from':'previous_stage'}}})
        self.assertIsNone(result['items']['ndx']['probability'])
        self.assertNotIn('base_rate',result['items']['ndx'])

    def test_raw_shadow_record_and_cache_are_not_mutated(self):
        before=copy.deepcopy(self.payload)
        result=public_probability_payload(self.payload)
        self.assertEqual(self.payload,before)
        result['items']['sp500']['symbol']='changed'
        self.assertEqual(self.payload,before)

    def test_malformed_and_cached_payloads_fail_closed(self):
        for payload in (None,[],{'items':[]},{'items':{'kospi100':None}}):
            result=public_probability_payload(payload)
            self.assertFalse(result['display_allowed'])
        result=public_probability_payload({'items':{'kospi100':{'up_10_probability':99.,'cached':True}}})
        self.assertNotIn('up_10_probability',result['items']['kospi100'])

    def test_actual_public_route_functions_use_the_boundary(self):
        # Execute the real route bodies with suppliers isolated from providers,
        # Firebase, startup jobs and external databases.
        for filename,name,supplier in (('production_v20.py','next_day_probabilities','next_day_probability'),
                ('production_v20.py','one_month_probabilities','kospi_monthly'),
                ('production_v23.py','next_day_probabilities','probability_pipeline')):
            tree=ast.parse(Path(filename).read_text())
            function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
            function.decorator_list=[]
            namespace={'public_probability_payload':public_probability_payload,
                supplier:SimpleNamespace(get_all=lambda:self.payload,get=lambda:self.payload)}
            module=ast.Module(body=[function],type_ignores=[])
            exec(compile(ast.fix_missing_locations(module),filename,'exec'),namespace)
            self.assertFalse(namespace[name]()['items']['sp500']['display_allowed'])


if __name__=='__main__':unittest.main()
