"""Offline-only private KRX OPEN API 2015-2026 acquisition contract tests.

Synthetic data, mocked HTTP and temporary private store; never any KRX
network, real securities, credentials, user storage or orders.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_v1_krx_openapi_private_history_batch as b
from research_v1_krx_private_store import read_private_json, verify_raw_object

ENV = {
    b.ENV_CONSENT: b.CONSENT,
    "KRX_AUTH_KEY": "SYNTHETIC_ONLY_NOT_REAL",
    "RAILWAY_SERVICE_NAME": b.WORKER,
    "KRX_PRIVATE_RAW_DIR": "/data/synthetic",
}


def master_records(n=12):
    return [{
        "ISU_CD": "KR70000000000",
        "ISU_SRT_CD": f"{i:06d}",
        "ISU_NM": f"private-synthetic-name-{i}",
        "LIST_DD": "20100104",
        "MKT_TP_NM": "KOSPI",
        "SECUGRP_NM": "주권",
        "KIND_STKCERT_TP_NM": "보통주",
        "LIST_SHRS": "100000",
    } for i in range(1, n+1)]


def daily_records(day, *, zero=0, n=12):
    rec = [{
        "BAS_DD": day, "ISU_CD": f"{i:06d}",
        "TDD_OPNPRC": "10000", "TDD_HGPRC": "10200",
        "TDD_LWPRC": "9800", "TDD_CLSPRC": "10100",
        "ACC_TRDVOL": "1000", "ACC_TRDVAL": "10100000",
        "MKTCAP": "1010000000", "LIST_SHRS": "100000",
        "FLUC_RT": "1.00",
    } for i in range(1, n+1)]
    for r in rec[:zero]:
        r.update(TDD_OPNPRC="0", TDD_HGPRC="0",
                 TDD_LWPRC="0", TDD_CLSPRC="10100",
                 ACC_TRDVOL="0", ACC_TRDVAL="0")
    return rec


class FakeResponse:
    status_code = 200
    def __init__(self, blob):
        self.blob = blob
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass
    def iter_content(self, chunk_size):
        for i in range(0,len(self.blob),chunk_size):
            yield self.blob[i:i+chunk_size]


class FakeSession:
    def __init__(self, transform=None):
        self.calls=[]
        self.transform=transform
    def get(self, url, *, headers, params, allow_redirects, stream, timeout):
        assert url in b.ENDPOINTS.values()
        assert headers == {"AUTH_KEY": ENV["KRX_AUTH_KEY"]}
        assert allow_redirects is False and stream is True and timeout == 25
        day=params["basDd"]
        name=next(k for k,v in b.ENDPOINTS.items() if v == url)
        self.calls.append((day,name))
        rows = daily_records(day, zero=2 if day == "20150105" else 0) if name=="daily_trade" else master_records()
        payload = {"OutBlock_1":rows}
        if self.transform:
            payload=self.transform(day,name,payload)
        return FakeResponse(json.dumps(payload).encode("utf-8"))


class KRXPrivateOpenAPIHistoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def evaluate(self, *, session=None, start="2015-01-05", end="2015-01-06", execute=True, env=None):
        with patch.object(b,"_preflight",return_value=self.root),patch.object(b.time,"sleep",return_value=None):
            return b.run(start=start,end=end,max_requests=60,execute=execute,
                         environment=ENV if env is None else env,
                         session=session or FakeSession())
    def test_default_dry_run_has_zero_network_or_storage(self):
        s=FakeSession()
        r=b.run(start="2015-01-05",end="2015-01-09",environment=ENV,session=s)
        self.assertEqual(r["status"],"DRY_RUN_NO_NETWORK")
        self.assertEqual(s.calls,[])
        self.assertEqual(list(self.root.rglob("*.json")),[])
        self.assertFalse(r["live_orders_authorized"])
    def test_history_pair_persists_private_hash_bound_raw_and_resumes(self):
        s=FakeSession()
        report=self.evaluate(session=s)
        self.assertEqual(report["status"],"PRIVATE_SAMPLE_STORED_NOT_SOURCE_ADMITTED")
        self.assertEqual(len(s.calls),4)
        self.assertEqual(report["new_completed_date_pairs"],2)
        self.assertEqual(report["batch_sampled_ohlc_zero_activity_rows"],2)
        cp=read_private_json(self.root,"acquisitions/20150105.json")["value"]
        self.assertTrue(cp["source_pair_complete"])
        self.assertFalse(cp["performance_run_authorized"])
        self.assertFalse(cp["historical_pit_source_admitted"])
        self.assertFalse(cp["official_trading_status_verified"])
        self.assertEqual(cp["quality"]["common_rows"],12)
        self.assertEqual(cp["quality"]["nonpositive_zero_activity_rows"],2)
        for service in ("daily_trade","security_master"):
            record=cp["sources"][service]
            self.assertEqual(record["source_access_route"],"KRX_APPROVED_OPENAPI_ONLY")
            self.assertFalse(record["official_original_publication_timestamp_verified"])
            obj=verify_raw_object(self.root,record["raw_sha256"],
                                  expected_size=record["raw_byte_length"])
            self.assertTrue(obj["verified"])
        joined = json.dumps(report,sort_keys=True)
        for private in ("SYNTHETIC_ONLY_NOT_REAL","private-synthetic-name","000001"):
            self.assertNotIn(private,joined)
        self.assertFalse(report["m20_performance_testing_authorized"])
        self.assertEqual(report["ordering"],"DISABLED")
        second=FakeSession()
        retry=self.evaluate(session=second)
        self.assertEqual(second.calls,[])
        self.assertEqual(retry["previous_verified_date_pairs_skipped"],2)
        self.assertEqual(retry["attempted_requests"],0)
    def test_tampered_private_raw_is_fail_closed_not_recollected(self):
        self.evaluate()
        saved=read_private_json(self.root,"acquisitions/20150105.json")["value"]
        key=saved["sources"]["daily_trade"]["raw_sha256"]
        p=self.root/"objects"/"sha256"/key[:2]/(key+".bin")
        p.write_bytes(b"TAMPERED")
        os.chmod(p,0o600)
        s=FakeSession()
        out=self.evaluate(session=s)
        self.assertEqual(out["status"],"FAIL_CLOSED_NO_PROFIT_AUTHORITY")
        self.assertEqual(out["failure_reason"],"PREVIOUS_CHECKPOINT_INVALID")
        self.assertEqual(s.calls,[])
    def test_historical_scope_outside_2015_2026_blocked(self):
        for start,end in (("2014-12-31","2015-01-02"),
                          ("2026-10-12","2026-10-13"),
                          ("2026-01-03","2026-01-02")):
            with self.subTest(start=start):
                out=b.run(start=start,end=end,execute=True,environment=ENV,session=FakeSession())
                self.assertEqual(out["status"],"FAIL_CLOSED_NO_PROFIT_AUTHORITY")
                self.assertEqual(out["failure_reason"],"USER_APPROVED_DATE_SCOPE_EXCEEDED")
    def test_oversized_span_and_request_budget_are_blocked_before_network(self):
        for budget in (1,61):
            with self.assertRaisesRegex(b.PrivateOpenAPIHistoryError,"REQUEST_BUDGET_INVALID"):
                b._calendar("2015-01-05","2015-01-06",budget)
        with self.assertRaisesRegex(b.PrivateOpenAPIHistoryError,"CALENDAR_SPAN_EXCEEDS_BATCH_LIMIT"):
            b._calendar("2015-01-05","2015-03-01",60)
        with self.assertRaisesRegex(b.PrivateOpenAPIHistoryError,"REQUEST_BUDGET_BELOW_PLANNED_CALLS"):
            b._calendar("2015-01-05","2015-01-30",4)
    def test_prefight_blocking_does_not_access_krx(self):
        root=Path("/nonexistent/data")
        for changes,code in (
            ({b.ENV_CONSENT:"NOT_CONSENT"},"SCOPED_USER_CONSENT_SENTINEL_REQUIRED"),
            ({"RAILWAY_SERVICE_NAME":"indexalert-runtime"},"PRIVATE_DEDICATED_WORKER_REQUIRED"),
            ({"KRX_AUTH_KEY":""},"APPROVED_OPENAPI_KEY_MISSING"),
            ({"KRX_PRIVATE_RAW_DIR":"/tmp/public"},"PERSISTENT_PRIVATE_VOLUME_REQUIRED"),
        ):
            env={**ENV,**changes}
            with self.subTest(code=code):
                s=FakeSession()
                r=b.run(start="2015-01-05",end="2015-01-06",execute=True,environment=env,session=s)
                self.assertEqual(r["failure_reason"],code)
                self.assertEqual(s.calls,[])
    def test_missing_master_identity_fails_before_storage(self):
        def corrupt(day,service,payload):
            if service=="security_master":payload["OutBlock_1"].pop()
            return payload
        r=self.evaluate(session=FakeSession(transform=corrupt))
        self.assertEqual(r["status"],"FAIL_CLOSED_NO_PROFIT_AUTHORITY")
        self.assertEqual(r["failure_reason"],"SOURCE_SECURITY_MASTER_UNMAPPED")
        self.assertEqual(list(self.root.rglob("*.json")),[])
    def test_wrong_bas_date_fails_closed(self):
        def corrupt(day,service,payload):
            if service=="daily_trade":payload["OutBlock_1"][0]["BAS_DD"]="20201010"
            return payload
        r=self.evaluate(session=FakeSession(transform=corrupt))
        self.assertEqual(r["failure_reason"],"SOURCE_DAILY_DATE_MISMATCH")
        self.assertEqual(list(self.root.rglob("*.json")),[])
    def test_source_schema_drift_fails_closed(self):
        def corrupt(day,service,payload):
            if service=="daily_trade":payload["OutBlock_1"][0].pop("MKTCAP")
            return payload
        r=self.evaluate(session=FakeSession(transform=corrupt))
        self.assertEqual(r["failure_reason"],"SOURCE_SCHEMA_DRIFT")
    def test_data_marketplace_endpoints_are_not_available(self):
        self.assertEqual(set(b.ENDPOINTS),{"daily_trade","security_master"})
        for url in b.ENDPOINTS.values():
            self.assertTrue(url.startswith("https://data-dbg.krx.co.kr/svc/apis/sto/"))
            self.assertNotIn("getJsonData.cmd",url)
        with self.assertRaisesRegex(b.PrivateOpenAPIHistoryError,"UNAPPROVED_API_REQUEST"):
            b._get(FakeSession(),"https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd",
                   "secret","20150105")
    def test_partial_and_full_empty_provider_day_semantics(self):
        row=b._inspect([],[],"20150105")
        self.assertEqual(row["calendar_day_class"],
                         "PROVIDER_BOTH_EMPTY_UNVERIFIED_CALENDAR_OR_SOURCE_GAP")
        self.assertFalse(row["daily_all_mapped_to_master"])
        with self.assertRaisesRegex(b.PrivateOpenAPIHistoryError,"PARTIAL_SOURCE_CALENDAR_SCOPE"):
            b._inspect(daily_records("20150105"),[],"20150105")
        master_only=b._inspect([],master_records(),"20150105")
        self.assertEqual(master_only["calendar_day_class"],
                         "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP")
        self.assertEqual(master_only["daily_rows"],0)
        self.assertEqual(master_only["master_rows"],12)
        self.assertFalse(master_only["daily_all_mapped_to_master"])
        self.assertEqual(master_only["normal_ohlc_common_rows"],0)
        self.assertNotIn("official_holiday_verified",master_only)
    def test_master_only_source_date_is_persisted_as_unverified_not_cash_trading_day(self):
        def no_daily(day,service,payload):
            if service=="daily_trade" and day=="20150105":
                return {"OutBlock_1":[]}
            return payload
        s=FakeSession(transform=no_daily)
        result=self.evaluate(session=s)
        self.assertEqual(result["status"],"PRIVATE_SAMPLE_STORED_NOT_SOURCE_ADMITTED")
        self.assertEqual(result["provider_empty_pairs_not_calendar_attested"],1)
        self.assertEqual(result["batch_sampled_common_rows"],12)
        saved=read_private_json(self.root,"acquisitions/20150105.json")["value"]
        self.assertEqual(saved["quality"]["calendar_day_class"],
                         "DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP")
        self.assertFalse(saved["historical_pit_source_admitted"])
        self.assertFalse(saved["official_trading_status_verified"])
    def test_duplicate_master_or_daily_security_fails(self):
        master=master_records()
        master[1]["ISU_SRT_CD"]=master[0]["ISU_SRT_CD"]
        with self.assertRaisesRegex(b.PrivateOpenAPIHistoryError,"DUPLICATE_BASIC_INFO_SECURITY"):
            b._inspect(daily_records("20150105"),master,"20150105")
        daily=daily_records("20150105")
        daily[1]["ISU_CD"]=daily[0]["ISU_CD"]
        with self.assertRaisesRegex(b.PrivateOpenAPIHistoryError,"SOURCE_DAILY_DUPLICATE_CODE"):
            b._inspect(daily,master_records(),"20150105")
    def test_nonpositive_zero_activity_never_autoadmitted(self):
        q=b._inspect(daily_records("20150105",zero=2),master_records(),"20150105")
        self.assertEqual(q["normal_ohlc_common_rows"],10)
        self.assertEqual(q["nonpositive_zero_activity_rows"],2)
        self.assertEqual(q["other_invalid_price_rows"],0)
        self.assertNotIn("trade_authorized",q)
    def test_private_data_digest_is_provider_bytes_not_reconstructed_record(self):
        self.evaluate()
        cp=read_private_json(self.root,"acquisitions/20150105.json")["value"]
        r=cp["sources"]["daily_trade"]
        self.assertEqual(len(r["raw_sha256"]),64)
        self.assertEqual(len(r["schema_sha256"]),64)
        self.assertNotEqual(r["raw_sha256"],r["schema_sha256"])


if __name__=="__main__":
    unittest.main()
