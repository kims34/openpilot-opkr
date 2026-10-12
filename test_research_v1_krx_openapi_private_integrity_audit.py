"""Strict offline tests for read-only KRX private source integrity audit."""
from __future__ import annotations

from datetime import datetime
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import research_v1_krx_openapi_private_history_batch as batch
from research_v1_krx_openapi_private_integrity_audit import (
    audit_private_range, _bounds,
    OfflinePrivateAuditError,
)
from research_v1_krx_private_store import (
    read_private_json, write_private_json,
)
from test_research_v1_krx_openapi_private_history_batch import FakeSession, ENV


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)/batch.PRIVATE_SUBDIR
        self.root.mkdir(mode=0o700)
        self.override=patch.dict(os.environ,{"INDEXALERT_TEST_PRIVATE_AUDIT":"1"},clear=False)
        self.override.start()
    def tearDown(self):
        self.override.stop()
        self.tmp.cleanup()
    def seed(self, *, transform=None):
        session=FakeSession(transform=transform)
        with patch.object(batch,"_preflight",return_value=self.root),\
             patch.object(batch.time,"sleep",return_value=None):
            report=batch.run(
                start="2015-01-05",end="2015-01-06",
                max_requests=4,execute=True,environment=ENV,session=session)
        self.assertEqual(report["status"],"PRIVATE_SAMPLE_STORED_NOT_SOURCE_ADMITTED")
        self.assertEqual(len(session.calls),4)
        return report
    def audit(self,start="2015-01-05",end="2015-01-06"):
        return audit_private_range(root=self.root,start=start,end=end)
    def test_full_two_day_range_passes_without_admission_or_writing(self):
        self.seed()
        before={str(p):p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        report=self.audit()
        self.assertEqual(report["status"],"ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED")
        self.assertEqual(report["verified_date_pairs"],2)
        self.assertEqual(report["expected_weekdays"],2)
        self.assertEqual(report["missing_weekday_pair_count"],0)
        self.assertEqual(report["sampled_ohlc_zero_activity_rows"],2)
        self.assertEqual(len(report["snapshot_fingerprint_sha256"]),64)
        for key in ("raw_source_rows_exposed","network_request_attempted",
                    "storage_mutated","historical_publication_pit_verified",
                    "official_halt_and_delist_status_verified","source_admitted",
                    "m20_performance_testing_authorized","sealed_holdout_authorized",
                    "champion_change_authorized","real_orders_authorized",
                    "funds_movement_authorized","permission_change_authorized"):
            self.assertIs(report[key],False,key)
        self.assertEqual(report["ordering"],"DISABLED")
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        dumped=json.dumps(report)
        for sensitive in ("private-synthetic-name",ENV["KRX_AUTH_KEY"],"000001","10000"):
            self.assertNotIn(sensitive,dumped)
    def test_missing_date_is_explicitly_incomplete_not_zero_return(self):
        self.seed()
        out=self.audit(start="2015-01-05",end="2015-01-09")
        self.assertEqual(out["status"],"INCOMPLETE_WEEKDAY_COVERAGE_NOT_PIT_ADMITTED")
        self.assertEqual(out["expected_weekdays"],5)
        self.assertEqual(out["verified_date_pairs"],2)
        self.assertEqual(out["missing_weekday_pair_count"],3)
        self.assertFalse(out["source_admitted"])
    def test_tampered_raw_bytes_fail(self):
        self.seed()
        saved=read_private_json(self.root,"acquisitions/20150105.json")["value"]
        digest=saved["sources"]["daily_trade"]["raw_sha256"]
        target=self.root/"objects"/"sha256"/digest[:2]/(digest+".bin")
        target.write_bytes(b"invalid private raw content")
        os.chmod(target,0o600)
        out=self.audit()
        self.assertEqual(out["status"],"FAIL_CLOSED_PRIVATE_SOURCE_INTEGRITY_ERROR")
        self.assertEqual(out["failure_codes"].get("PRIVATE_SOURCE_OBJECT_DAMAGED"),1)
        self.assertEqual(out["invalid_pair_count"],1)
        self.assertFalse(out["m20_performance_testing_authorized"])
    def test_private_source_schema_quality_tampering_fail(self):
        self.seed()
        rel="acquisitions/20150105.json"
        original=read_private_json(self.root,rel)["value"]
        for mode in ("quality","wrongdate","admission","endpoint","observed_time"):
            with self.subTest(mode=mode):
                data=json.loads(json.dumps(original))
                if mode=="quality":
                    data["quality"]["common_rows"]+=1
                elif mode=="wrongdate":
                    data["trading_day"]="20150106"
                elif mode=="admission":
                    data["historical_pit_source_admitted"]=True
                elif mode=="endpoint":
                    data["sources"]["daily_trade"]["source_endpoint_suffix"]="getJsonData.cmd"
                else:
                    data["sources"]["daily_trade"]["observed_available_by"]="2015-01-05T00:00:00+00:00"
                write_private_json(self.root,rel,data)
                out=self.audit()
                self.assertEqual(out["status"],"FAIL_CLOSED_PRIVATE_SOURCE_INTEGRITY_ERROR")
                self.assertEqual(out["invalid_pair_count"],1)
            write_private_json(self.root,rel,original)
    def test_master_present_daily_empty_stays_unknown_calendar(self):
        def omit_daily(day,service,payload):
            if day=="20150105" and service=="daily_trade":
                return {"OutBlock_1":[]}
            return payload
        self.seed(transform=omit_daily)
        out=self.audit()
        self.assertEqual(out["status"],"ALL_REQUESTED_WEEKDAYS_VERIFIED_NOT_PIT_ADMITTED")
        self.assertEqual(out["empty_daily_unverified_calendar_or_source_gap_days"],1)
        self.assertFalse(out["official_halt_and_delist_status_verified"])
        self.assertFalse(out["historical_publication_pit_verified"])
    def test_bad_permissions_symlink_and_missing_private_root_fail_closed(self):
        self.seed()
        target=self.root/"acquisitions"/"20150105.json"
        os.chmod(target,0o644)
        out=self.audit()
        self.assertEqual(out["status"],"FAIL_CLOSED_PRIVATE_SOURCE_INTEGRITY_ERROR")
        self.assertEqual(out["failure_codes"]["CHECKPOINT_READ_INVALID"],1)
        os.chmod(target,0o600)
        target.unlink()
        target.symlink_to(self.root/"acquisitions"/"20150106.json")
        out=self.audit()
        self.assertEqual(out["failure_codes"]["CHECKPOINT_SYMLINK_INVALID"],1)
        bad=audit_private_range(root=self.root/"absent",start="2015-01-05",end="2015-01-06")
        self.assertEqual(bad["status"],"FAIL_CLOSED_AUDIT_SCOPE_INVALID")
    def test_year_scope_strict(self):
        for start,end in (
            ("2014-12-31","2015-01-05"),
            ("2015-12-31","2016-01-01"),
            ("2018-01-31","2018-01-01"),
            ("2015-02-30","2015-03-01"),
            ("2026-10-12","2026-10-13"),
        ):
            with self.subTest(start=start):
                with self.assertRaises(OfflinePrivateAuditError):
                    _bounds(start,end)
        self.assertEqual(len(_bounds("2015-01-01","2015-12-31")),261)
    def test_no_audit_admission_on_weekend_empty_scope(self):
        out=self.audit(start="2015-01-03",end="2015-01-04")
        self.assertEqual(out["status"],"FAIL_CLOSED_AUDIT_SCOPE_INVALID")
        self.assertEqual(out["failure_codes"]["EMPTY_AUDIT_WORKDAY_SCOPE"],1)
        self.assertFalse(out["real_orders_authorized"])


if __name__=="__main__":
    unittest.main()
