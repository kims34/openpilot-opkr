import copy
import threading
import time
import unittest
import tempfile
from unittest.mock import Mock
from unittest.mock import patch

from probability_pipeline import ProbabilityPipeline, install_scheduler


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.now = 1790600000.0
        self.payload = {"model_version": "3.3-calibration-gated", "items": {
            key: {"probability": 55.0, "target_date": "2026-09-28",
                  "as_of": "2026-09-25", "target_open": self.now+3600,
                  "target_close": self.now+27000, "data_digest": "fixed"}
            for key in ("sp500", "ndx", "djdiv")}}

    def make(self, enrich):
        return ProbabilityPipeline(lambda: copy.deepcopy(self.payload), [enrich], clock=lambda: self.now)

    @staticmethod
    def enrich(payload):
        for item in payload["items"].values():
            item["extended_session"] = {"available": True, "probability": 60.0}
        return payload

    def wait(self, pipeline):
        deadline = time.monotonic()+3
        while pipeline.running and time.monotonic()<deadline:
            time.sleep(.005)
        self.assertFalse(pipeline.running)

    def test_slow_provider_does_not_block_or_start_duplicate_workers(self):
        started, release = threading.Event(), threading.Event()
        calls=[]
        def slow(payload):
            calls.append(1); started.set(); release.wait(3)
            return self.enrich(payload)
        p=self.make(slow)
        try:
            before=time.monotonic(); out=p.get()
            self.assertLess(time.monotonic()-before,.5)
            self.assertTrue(started.wait(1))
            self.assertEqual(out['items']['sp500']['probability'],55.)
            self.assertFalse(out['items']['sp500']['extended_session']['available'])
            for _ in range(10): p.get()
            self.assertEqual(len(calls),1)
        finally: release.set()
        self.wait(p)
        self.assertTrue(p.get()['items']['sp500']['extended_session']['available'])

    def test_session_boundary_suppresses_previous_overlay_immediately(self):
        p=self.make(self.enrich);p.get();self.wait(p)
        self.now=self.payload['items']['sp500']['target_open']
        out=p.get()
        self.assertFalse(out['items']['sp500']['extended_session']['available'])
        self.wait(p)

    def test_expired_cache_does_not_serve_old_market_signal(self):
        p=self.make(self.enrich);p.get();self.wait(p)
        self.now+=121
        self.assertFalse(p.get()['items']['sp500']['extended_session']['available'])
        self.wait(p)

    def test_new_daily_probability_is_not_replaced_by_cached_base(self):
        p=self.make(self.enrich);p.get();self.wait(p)
        self.payload['items']['sp500']['probability']=51.
        out=p.get()
        self.assertEqual(out['items']['sp500']['probability'],51.)
        self.assertFalse(out['items']['sp500']['extended_session']['available'])
        self.wait(p)

    def test_mutating_response_cannot_mutate_shared_cache(self):
        p=self.make(self.enrich);p.get();self.wait(p)
        out=p.get();out['items']['sp500']['extended_session']['probability']=99.
        self.assertEqual(p.get()['items']['sp500']['extended_session']['probability'],60.)

    def test_worker_crossing_market_boundary_is_not_published(self):
        def crosses(payload):
            self.now=self.payload['items']['sp500']['target_open']
            return self.enrich(payload)
        p=self.make(crosses);p.get();self.wait(p)
        self.assertIsNone(p.cached)

    def test_scheduler_is_installed_once_without_a_phone_request(self):
        scheduler=Mock();scheduler.get_job.return_value=None
        p=self.make(self.enrich)
        install_scheduler(scheduler,p)
        args,kwargs=scheduler.add_job.call_args
        self.assertEqual(args,(p.get,'interval'))
        self.assertEqual(kwargs['seconds'],60)
        self.assertEqual(kwargs['max_instances'],1)
        scheduler.get_job.return_value=object()
        install_scheduler(scheduler,p)
        self.assertEqual(scheduler.add_job.call_count,1)

    def test_forecast_model_identity_does_not_depend_on_shared_global(self):
        import next_day_probability as ledger
        with tempfile.TemporaryDirectory() as tmp, patch.object(ledger, 'DB_PATH', tmp+'/ledger.db'), patch.object(ledger, 'MODEL_VERSION', 'unrelated-global'):
            record=dict(as_of='2026-09-25',target_date='2026-09-28',target_open=100,
                        probability=60.,base_rate=55.,model_version='us-model')
            ledger.record_forecast('SPY',record,[('2026-09-25',100)],90)
            record['model_version']='kr-model'
            ledger.record_forecast('^KS11',record,[('2026-09-25',100)],90)
            record['model_version']='us-model'
            stats=ledger.record_forecast('SPY',record,[('2026-09-25',100),('2026-09-28',101)],110)
            self.assertEqual(stats['prospective_count'],1)
            with ledger.sqlite3.connect(ledger.DB_PATH) as con:
                self.assertEqual(set(con.execute('SELECT model,symbol FROM probability_forecasts')),
                                 {('us-model','SPY'),('kr-model','^KS11')})

    def test_late_preopen_request_is_not_counted_as_prospective(self):
        import next_day_probability as ledger
        import probability_live_gate_patch as wiring
        item=dict(as_of='2026-09-25',target_date='2026-09-28',target_open=100)
        result=dict(probability=60.,baseline_probability=55.)
        with tempfile.TemporaryDirectory() as tmp, patch.object(ledger,'DB_PATH',tmp+'/ledger.db'), patch.object(ledger,'fetch_history',return_value=([('2026-09-25',100)],{})):
            wiring._score_preopen('SPY',item,dict(result),101)
            with ledger.sqlite3.connect(ledger.DB_PATH) as con:
                self.assertEqual(con.execute('SELECT COUNT(*) FROM preopen_futures_forecasts').fetchone()[0],0)
            wiring._score_preopen('SPY',item,dict(result),99)
            with ledger.sqlite3.connect(ledger.DB_PATH) as con:
                self.assertEqual(con.execute('SELECT COUNT(*) FROM preopen_futures_forecasts').fetchone()[0],1)


if __name__=='__main__':unittest.main()
