"""Synthetic-only M20 original XBRL archive identity and safety tests."""
import io
import json
import os
import unittest
from unittest.mock import patch
import zipfile

from research_v1_opendart_original_xbrl_pilot import (
    OriginalXbrlProbeError, first_q3_original_receipts,
    inspect_xbrl_zip, run,
)

CORP = "12345678"
R24 = "20241114000001"
R25 = "20251114000001"


def index():
    return {"status": "000", "total_count": "2", "total_page": "1", "page_no": "1", "list": [
        {"rcept_no": R24, "report_nm": "분기보고서 (2024.09)", "rcept_dt": "20241114"},
        {"rcept_no": R25, "report_nm": "분기보고서 (2025.09)", "rcept_dt": "20251114"},
    ]}


def zipp(files=None, *, compression=zipfile.ZIP_DEFLATED):
    files = files if files is not None else {"financial_2025.xbrl": b"<xbrl>private-numeric-value</xbrl>"}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", compression=compression) as obj:
        for name, value in files.items():
            obj.writestr(name, value)
    return buf.getvalue()


def corp_archive():
    return zipp({"CORPCODE.xml": (
        "<result><list><corp_code>12345678</corp_code>"
        "<stock_code>005930</stock_code></list></result>"
    ).encode()})


class FakeResponse:
    def __init__(self, content=b"", parsed=None, status=200):
        self.status_code = status
        self.content = content
        self.parsed = parsed
        self.closed = False

    def json(self):
        return self.parsed

    def iter_content(self, chunk_size):
        assert chunk_size == 65536
        for start in range(0, len(self.content), 65536):
            yield self.content[start:start + 65536]

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, response24=None, response25=None, index_payload=None):
        self.responses = {R24: response24, R25: response25}
        self.payload = index_payload if index_payload is not None else index()
        self.calls = []

    def get(self, url, *, params, timeout, allow_redirects, stream=False):
        assert url.startswith("https://opendart.fss.or.kr/api/")
        assert allow_redirects is False
        assert params["crtfc_key"] == "synthetic-only-key"
        service = url.split("/")[-1]
        self.calls.append(service)
        if service == "corpCode.xml":
            return FakeResponse(corp_archive())
        if service == "list.json":
            assert params["pblntf_ty"] == "A"
            assert params["bgn_de"] == "20241001"
            assert params["end_de"] == "20261012"
            return FakeResponse(b"{}", self.payload)
        if service == "fnlttXbrl.xml":
            assert timeout == 30 and stream is True
            assert params["reprt_code"] == "11014"
            receipt = params["rcept_no"]
            assert receipt in (R24, R25)
            selected = self.responses[receipt]
            return selected if selected is not None else FakeResponse(zipp())
        raise AssertionError("unknown OpenDART endpoint")


def call(session=None):
    with patch.dict(os.environ, {"OPENDART_API_KEY": "synthetic-only-key"}, clear=True):
        return run(session if session is not None else FakeSession())


class OriginalXbrlPilotTests(unittest.TestCase):
    def test_official_archive_two_years_shape_only(self):
        session = FakeSession()
        out = call(session)
        self.assertEqual(out["source_status"], "TWO_OFFICIAL_ORIGINAL_XBRL_ARCHIVES_SHAPE_ONLY")
        self.assertEqual(out["original_q3_archives_received"], 2)
        self.assertTrue(out["report_filing_date_level_verified"])
        self.assertEqual(session.calls, ["corpCode.xml", "list.json", "fnlttXbrl.xml", "fnlttXbrl.xml"])
        self.assertNotEqual(out["q_minus_4_archive_shape"]["xbrl_decompressed_entry_digest_sha256"], "")
        for key in (
            "corporation_to_issuer_historical_binding_verified",
            "original_document_timestamp_at_publication_verified",
            "xbrl_historical_revision_lineage_independently_verified",
            "q_and_q_minus_4_economic_comparability_verified",
            "decision_time_market_cap_verified", "krx_tradability_verified",
            "pit_source_admitted", "performance_testing_authorized",
            "sealed_holdout_authorized", "champion_change_authorized",
            "real_orders_authorized", "live_order_authorized",
            "funds_movement_authorized", "permission_change_authorized",
            "raw_bytes_or_financial_amounts_persisted",
        ):
            self.assertIs(out[key], False, key)
        self.assertEqual(out["ordering"], "DISABLED")
        for forbidden in (CORP, R24, R25, "private-numeric-value", "synthetic-only-key"):
            self.assertNotIn(forbidden, json.dumps(out))

    def test_original_receipt_does_not_substitute_later_correction(self):
        payload = index()
        payload["list"].append({"rcept_no": "20251201000002", "rcept_dt": "20251201",
                                "report_nm": "[기재정정]분기보고서 (2025.09)"})
        payload["total_count"] = "3"
        chosen = first_q3_original_receipts(payload)
        self.assertEqual(chosen, {"Q_MINUS_4": R24, "Q_CURRENT": R25})

    def test_same_day_duplicate_versions_block_original_selection(self):
        payload = index()
        payload["list"].append({"rcept_no": "20251114000002", "rcept_dt": "20251114",
                                "report_nm": "[기재정정]분기보고서 (2025.09)"})
        payload["total_count"] = "3"
        with self.assertRaisesRegex(OriginalXbrlProbeError, "INITIAL_DAY_VERSION_AMBIGUOUS"):
            first_q3_original_receipts(payload)

    def test_missing_or_renamed_original_only_is_not_admitted(self):
        payload = index()
        payload["list"][1]["report_nm"] = "[기재정정]분기보고서 (2025.09)"
        with self.assertRaisesRegex(OriginalXbrlProbeError, "ORIGINAL_EDITION_AMBIGUOUS"):
            first_q3_original_receipts(payload)

    def test_missing_historical_report_blocks_before_xbrl(self):
        payload = index()
        payload["list"].pop(0)
        payload["total_count"] = "1"
        out = call(FakeSession(index_payload=payload))
        self.assertEqual(out["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_stage"], "OFFICIAL_PERIODIC_FILING_INDEX")
        self.assertFalse(out["pit_source_admitted"])

    def test_non_zip_official_error_cannot_be_admitted(self):
        response = FakeResponse(b'<result><status>013</status></result>')
        out = call(FakeSession(response24=response))
        self.assertEqual(out["source_status"], "SOURCE_GAP_FAIL_CLOSED")
        self.assertEqual(out["failure_stage"], "OFFICIAL_Q_MINUS_4_XBRL_ZIP")
        self.assertEqual(out["failure_reason_code"], "OFFICIAL_XBRL_ZIP_ABSENT")
        self.assertTrue(response.closed)
        self.assertEqual(out["original_q3_archives_received"], 0)

    def test_wrong_status_or_missing_archive_fails_closed(self):
        for response in (FakeResponse(b"", status=503), FakeResponse(b"")):
            with self.subTest(status=response.status_code):
                out = call(FakeSession(response24=response))
                self.assertEqual(out["source_status"], "SOURCE_GAP_FAIL_CLOSED")
                self.assertFalse(out["live_order_authorized"])

    def test_zip_crc_integrity_and_stable_logical_fingerprint(self):
        raw1 = zipp({"a.xbrl": b"<xbrl>x</xbrl>", "b.xml": b"<other/>"})
        raw2 = zipp({"b.xml": b"<other/>", "a.xbrl": b"<xbrl>x</xbrl>"})
        left = inspect_xbrl_zip(raw1)
        right = inspect_xbrl_zip(raw2)
        self.assertEqual(left["xbrl_decompressed_entry_digest_sha256"],
                         right["xbrl_decompressed_entry_digest_sha256"])
        self.assertEqual(left["xbrl_archive_entries"], 2)
        broken = bytearray(zipp({"a.xbrl": b"<xbrl>x</xbrl>"}, compression=zipfile.ZIP_STORED))
        at = bytes(broken).index(b"<xbrl>")
        broken[at] ^= 1
        with self.assertRaises(OriginalXbrlProbeError):
            inspect_xbrl_zip(bytes(broken))

    def test_bad_archive_entries_fail_closed(self):
        for cases in ({"../secret.xml": b"x"}, {"x.txt": b"a"},
                      {"a.xbrl": b""}, {"a.xbrl": b"x", "A.XBRL": b"y"}):
            with self.subTest(names=list(cases)):
                with self.assertRaises(OriginalXbrlProbeError):
                    inspect_xbrl_zip(zipp(cases))

    def test_rejects_excessive_archive_and_untrusted_types(self):
        with self.assertRaisesRegex(OriginalXbrlProbeError, "XBRL_ZIP_BYTES_INVALID"):
            inspect_xbrl_zip(b"PK\x03\x04" + b"a" * (32 * 1024 * 1024))
        with self.assertRaisesRegex(OriginalXbrlProbeError, "XBRL_ZIP_BYTES_INVALID"):
            inspect_xbrl_zip("not bytes")

    def test_missing_key_does_not_contact_any_source(self):
        sess = FakeSession()
        with patch.dict(os.environ, {}, clear=True):
            out = run(sess)
        self.assertEqual(out["source_status"], "AUTH_NOT_CONFIGURED")
        self.assertEqual(sess.calls, [])
        self.assertFalse(out["pit_source_admitted"])


if __name__ == "__main__":
    unittest.main()
