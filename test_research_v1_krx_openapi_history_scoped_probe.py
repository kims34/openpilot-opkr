"""Synthetic-only KRX historical OPEN API first-stage scope/safety tests.

No actual KRX network, credentials, trading, licensed historical data storage,
or full PIT/alpha admission. Synthetic securities deliberately fake.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from research_v1_krx_openapi_history_scoped_probe import (
    ENDPOINTS, SAMPLE_DATES, MANUAL_CONSENT_ENV, MANUAL_CONSENT_SENTINEL,
    _read_scoped_consents, run, _inspect_pair, _rows, _fetch,
    KRXOpenAPIHistoricalSampleError,
)

APPROVED_ENV = {
    "KRX_AUTH_KEY": "SYNTHETIC-CREDENTIAL-NOT-A-REAL-KEY",
    MANUAL_CONSENT_ENV: MANUAL_CONSENT_SENTINEL,
}


def master_records(count=30):
    return [{
        "ISU_CD": f"KR7{i:010d}",
        "ISU_SRT_CD": f"{i:06d}",
        "ISU_NM": f"synthetic-{i}",
        "LIST_DD": "20100104",
        "MKT_TP_NM": "KOSPI",
        "SECUGRP_NM": "주권",
        "KIND_STKCERT_TP_NM": "보통주",
        "LIST_SHRS": "100000",
    } for i in range(1, count + 1)]


def daily_records(day, count=30, *, anomalies=False):
    rows = [{
        "BAS_DD": day,
        "ISU_CD": f"{i:06d}",
        "TDD_OPNPRC": "10,000",
        "TDD_HGPRC": "10,200",
        "TDD_LWPRC": "9,800",
        "TDD_CLSPRC": "10,100",
        "ACC_TRDVOL": "1,000",
        "ACC_TRDVAL": "10,100,000",
        "MKTCAP": "1010000000",
        "LIST_SHRS": "100000",
        "FLUC_RT": "1.0",
    } for i in range(1, count + 1)]
    if anomalies:
        for row in rows[:27]:
            row.update(TDD_OPNPRC="0", TDD_HGPRC="0",
                       TDD_LWPRC="0", TDD_CLSPRC="10000",
                       ACC_TRDVOL="0", ACC_TRDVAL="0")
    return rows


class Response:
    def __init__(self, payload, status=200):
        self.content = json.dumps(payload, ensure_ascii=False).encode()
        self.status_code = status
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True

    def iter_content(self, chunk_size):
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i:i + chunk_size]


class FakeSession:
    def __init__(self, mutate=None):
        self.mutate = mutate
        self.calls = []
        self.closed = []

    def get(self, endpoint, *, headers, params, timeout, allow_redirects, stream):
        assert endpoint in ENDPOINTS.values()
        assert headers == {"AUTH_KEY": APPROVED_ENV["KRX_AUTH_KEY"]}
        assert params == {"basDd": params["basDd"]}
        assert timeout == 20 and allow_redirects is False and stream is True
        self.calls.append((endpoint, params["basDd"]))
        day = params["basDd"]
        item = next(key for key,value in ENDPOINTS.items() if value == endpoint)
        data = (daily_records(day, anomalies=day=="20260928")
                if item == "daily_trade" else master_records())
        block = {"OutBlock_1": data}
        if self.mutate is not None:
            result = self.mutate(item, day, block)
            if result is not None:
                block = result
        return Response(block)


def evaluate(env=APPROVED_ENV, session=None):
    return run(
        env=env, session=session,
        now=datetime(2026, 10, 12, 3, 0, tzinfo=timezone.utc),
    )


class KRXOpenAPIHistoryFirstProbeTests(unittest.TestCase):
    def test_explicit_user_scope_and_known_two_service_evidence(self):
        scope = _read_scoped_consents()
        self.assertEqual(scope["earliest_date"], "2015-01-01")
        self.assertEqual(scope["latest_date"], "2026-10-12")
        self.assertEqual(len(scope["user_consent_sha256"]), 64)
        self.assertEqual(len(scope["pinned_connectivity_sha256"]), 64)

    def test_six_manual_gets_only_and_no_raw_data_persisted(self):
        s = FakeSession()
        result = evaluate(session=s)
        self.assertEqual(result["source_status"],
                         "SCOPED_OFFICIAL_SAMPLE_COMPLETED_NOT_ADMITTED")
        self.assertEqual(len(s.calls), 6)
        self.assertEqual(result["request_count"], 6)
        self.assertEqual(result["sample_dates"], list(SAMPLE_DATES))
        self.assertEqual(len(result["request_metadata_receipts"]), 6)
        self.assertEqual(len(result["session_aggregate_diagnostics"]), 3)
        self.assertEqual(result["session_aggregate_diagnostics"][1]
                         ["common_nonpositive_zero_activity_shape_rows"], 27)
        for record in result["request_metadata_receipts"]:
            self.assertEqual(len(record["raw_sha256"]), 64)
            self.assertEqual(len(record["schema_sha256"]), 64)
        for symbol in ("000001", "000002", "synthetic-2", "KR70000000001"):
            self.assertNotIn(symbol, json.dumps(result))
        self.assertNotIn(APPROVED_ENV["KRX_AUTH_KEY"], json.dumps(result))

    def test_all_authority_and_trading_flags_remain_false(self):
        got = evaluate(session=FakeSession())
        for key in (
            "source_data_bytes_or_securities_saved",
            "private_full_history_acquisition_complete",
            "complete_historical_calendar_coverage_verified",
            "official_halt_delisting_status_verified",
            "exact_pit_publication_times_verified",
            "historical_m20_market_cap_pit_verified",
            "source_gate_full_admission_verified",
            "performance_run_authorized",
            "sealed_holdout_authorized",
            "champion_change_authorized",
            "real_orders_authorized",
            "funds_movement_authorized",
            "permission_change_authorized",
        ):
            self.assertIs(got[key], False, key)
        self.assertEqual(got["ordering"], "DISABLED")
        for panel in got["session_aggregate_diagnostics"]:
            self.assertFalse(panel["remaining_symbols_approved_for_alpha"])
            self.assertFalse(panel["full_trading_status_independently_verified"])

    def test_push_without_consent_never_calls_network(self):
        s = FakeSession()
        result = evaluate(env={"KRX_AUTH_KEY": APPROVED_ENV["KRX_AUTH_KEY"]},
                          session=s)
        self.assertEqual(result["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(result["failure_reason_code"],
                         "MANUAL_EXECUTION_CONSENT_REQUIRED")
        self.assertEqual(s.calls, [])

    def test_missing_key_never_calls_network(self):
        s = FakeSession()
        result = evaluate(env={MANUAL_CONSENT_ENV: MANUAL_CONSENT_SENTINEL},
                          session=s)
        self.assertEqual(result["failure_reason_code"],
                         "OPENAPI_AUTH_KEY_NOT_CONFIGURED")
        self.assertEqual(s.calls, [])

    def test_expired_approval_never_calls_network(self):
        s = FakeSession()
        result = run(
            env=APPROVED_ENV, session=s,
            now=datetime(2028, 1, 1, tzinfo=timezone.utc),
        )
        self.assertEqual(result["failure_reason_code"],
                         "API_APPROVAL_VALIDITY_DATE_EXCEEDED")
        self.assertEqual(s.calls, [])

    def test_mutated_user_scope_never_calls_network(self):
        s = FakeSession()
        with tempfile.TemporaryDirectory() as td:
            d = json.loads(Path(
                "INDEXALERT_KRX_OPENAPI_HISTORY_USER_CONSENT_2026_10_12.json"
            ).read_text(encoding="utf8"))
            d["includes_kosdaq_apis"] = True
            path = Path(td) / "mutated.json"
            path.write_text(json.dumps(d), encoding="utf8")
            result = run(env=APPROVED_ENV, session=s, consent_file=path,
                         now=datetime(2026, 10, 12, tzinfo=timezone.utc))
        self.assertEqual(result["failure_reason_code"], "USER_SCOPE_NOT_EXACT")
        self.assertEqual(s.calls, [])

    def test_mutated_service_url_never_calls_network(self):
        s = FakeSession()
        with tempfile.TemporaryDirectory() as td:
            d = json.loads(Path(
                "INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json"
            ).read_text(encoding="utf8"))
            d["services"]["daily_trade"]["endpoint"] = (
                "https://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
            )
            path = Path(td) / "changed.json"
            path.write_text(json.dumps(d), encoding="utf8")
            result = run(env=APPROVED_ENV, session=s, connectivity_file=path,
                         now=datetime(2026, 10, 12, tzinfo=timezone.utc))
        self.assertEqual(result["failure_reason_code"], "PINNED_SERVICE_PROOF_MISMATCH")
        self.assertEqual(s.calls, [])

    def test_disallowed_endpoint_or_day_is_impossible(self):
        s = FakeSession()
        with self.assertRaisesRegex(KRXOpenAPIHistoricalSampleError,
                                    "UNAUTHORIZED_ENDPOINT_OR_DATE"):
            _fetch(s, endpoint="https://data.krx.co.kr/",key="hidden",day="20260928")
        with self.assertRaisesRegex(KRXOpenAPIHistoricalSampleError,
                                    "UNAUTHORIZED_ENDPOINT_OR_DATE"):
            _fetch(s, endpoint=ENDPOINTS["daily_trade"],key="hidden",day="20150106")
        self.assertEqual(s.calls, [])

    def test_requested_date_must_match_every_daily_row(self):
        s = FakeSession(mutate=lambda name, day, payload:
            {"OutBlock_1": [
                {**r, "BAS_DD": "20260927"} for r in payload["OutBlock_1"]
            ]} if name == "daily_trade" and day == "20260928" else None
        )
        out = evaluate(session=s)
        self.assertEqual(out["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_reason_code"], "DAILY_REQUEST_DATE_MISMATCH")
        self.assertFalse(out["source_gate_full_admission_verified"])
        self.assertNotIn("request_metadata_receipts", out)

    def test_duplicate_daily_code_fails_closed(self):
        def mutate(name,day,payload):
            if name=="daily_trade" and day=="20150105":
                payload["OutBlock_1"][-1]["ISU_CD"]="000001"
            return payload
        out=evaluate(session=FakeSession(mutate=mutate))
        self.assertEqual(out["failure_reason_code"], "DUPLICATE_DAILY_CODE")

    def test_unjoined_master_mapping_fails_closed(self):
        def mutate(name,day,payload):
            if name=="security_master" and day=="20150105":
                payload["OutBlock_1"].pop()
            return payload
        out=evaluate(session=FakeSession(mutate=mutate))
        self.assertEqual(out["failure_reason_code"], "UNJOINED_DAILY_SECURITY_MASTER")

    def test_source_row_block_http_error_never_assumed_empty(self):
        s=FakeSession(mutate=lambda name,day,payload:
                      {"status":"INVALID_AUTH_KEY"} if
                      day=="20150105" and name=="daily_trade" else None)
        out=evaluate(session=s)
        self.assertEqual(out["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_reason_code"], "OFFICIAL_API_ROW_BLOCK_INVALID")
        self.assertEqual(out["request_count"], 1)

    def test_schema_drift_is_not_silent(self):
        def mutate(name,day,payload):
            if name=="daily_trade" and day=="20150105":
                for row in payload["OutBlock_1"]:
                    row.pop("MKTCAP")
            return payload
        out=evaluate(session=FakeSession(mutate=mutate))
        self.assertEqual(out["failure_reason_code"], "OFFICIAL_API_SCHEMA_DRIFT")

    def test_incoherent_ohlc_does_not_become_clean_candidate(self):
        d=daily_records("20150105")
        m=master_records()
        d[0]["TDD_OPNPRC"]="10000"
        d[0]["TDD_LWPRC"]="11000"
        got=_inspect_pair(daily_rows=d,master_rows=m,day="20150105")
        self.assertEqual(got["common_other_invalid_ohlc_shape_rows"],1)
        self.assertEqual(got["common_positive_coherent_ohlc_rows"],29)
        self.assertFalse(got["remaining_symbols_approved_for_alpha"])

    def test_missing_krx_evidence_file_is_fail_closed(self):
        s=FakeSession()
        out=run(env=APPROVED_ENV,session=s,
                consent_file=Path("/definitely/nonexistent/file/krx.json"),
                now=datetime(2026,10,12,tzinfo=timezone.utc))
        self.assertEqual(out["failure_reason_code"],"EVIDENCE_FILES_INVALID")
        self.assertEqual(s.calls, [])


if __name__=="__main__":
    unittest.main()
