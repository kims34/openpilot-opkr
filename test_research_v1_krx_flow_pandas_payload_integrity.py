"""Offline-only proof of matching pandas receipt hashes; no real KRX data."""
from __future__ import annotations

import csv
from io import BytesIO, StringIO
import unittest
from unittest.mock import patch

import pandas as pd
import numpy as np

from research_v1_krx_flow_pandas_payload_integrity import (
    KRXInvestorFlowPandasDigestError,
    verify_2022_krx_flow_pandas_payload,
)
from research_v1_krx_flow_private_triple_proof import RECEIPT_BODY, _sha
from test_research_v1_krx_flow_private_triple_proof import (
    fixture, retarget_original_bytes,
)


def _rebuild_receipt_for_original_csv(item):
    frame = pd.read_csv(BytesIO(item["original_raw_bytes"]), encoding="EUC-KR")
    columns = [str(c) for c in frame.columns]
    dtypes = [str(x) for x in frame.dtypes]
    rec = item["acquisition_receipt"]
    rec["response_rows"] = int(len(frame))
    rec["response_columns"] = columns
    rec["response_schema_sha256"] = _sha([
        {"name": col, "dtype": dtype} for col, dtype in zip(columns, dtypes)
    ])
    hashes = (
        pd.util.hash_pandas_object(frame, index=True)
        .astype("uint64").tolist()
    )
    rec["response_payload_sha256"] = _sha({
        "columns": columns,
        "dtypes": dtypes,
        "rows": int(len(frame)),
        "row_hashes": [int(x) for x in hashes],
    })
    rec["receipt_fingerprint_sha256"] = _sha({
        name: rec[name] for name in RECEIPT_BODY
    })
    comp = item["completion"]
    for key in (
        "response_rows", "response_schema_sha256",
        "response_payload_sha256", "receipt_fingerprint_sha256",
    ):
        comp[key] = rec[key]


def valid_case():
    data = fixture()
    _rebuild_receipt_for_original_csv(data)
    return data


def _retarget_rehash_one_investor_cell(item, investor_bucket, display):
    """Adversary changes EVERY related source/receipt/completion SHA in fixture."""
    reader = list(csv.reader(StringIO(
        item["original_raw_bytes"].decode("euc_kr"), newline=""
    )))
    column = reader[0].index(investor_bucket)
    reader[1][column] = display
    sink = StringIO(newline="")
    csv.writer(sink).writerows(reader)
    retarget_original_bytes(item, sink.getvalue().encode("euc_kr"))
    _rebuild_receipt_for_original_csv(item)


class OriginalKRXPandasPayloadTest(unittest.TestCase):
    def test_original_runtime_requirements_are_pinned(self):
        self.assertEqual(pd.__version__, "2.3.3")
        self.assertEqual(np.__version__, "2.5.3")

    def test_matching_synthetic_2022_source_bytes_derive_both_actual_digests(self):
        result = verify_2022_krx_flow_pandas_payload(**valid_case())
        self.assertTrue(result["original_pandas_schema_sha_independently_recomputed"])
        self.assertTrue(result["parsed_payload_digest_independently_recomputed"])
        self.assertTrue(result["original_pandas_payload_sha_matches_archived_receipt"])
        self.assertTrue(result["original_2022_foreign_institution_amount_display_format_checked"])
        self.assertFalse(result["original_2022_net_buy_amount_unit_or_scale_verified"])
        for key in (
            "source_admitted", "performance_testing_authorized",
            "sealed_holdout_authorized", "ordering_enabled",
            "provider_authenticity_independently_verified",
            "original_2022_as_published_vintage_verified",
            "historical_correction_lineage_verified",
            "source_numeric_rows_or_identifiers_emitted",
            "network_request_attempted",
        ):
            self.assertFalse(result[key], key)
        self.assertNotIn("KR7005930003", str(result))

    def test_numeric_tampering_with_matching_raw_object_hash_is_rejected(self):
        item = valid_case()
        raw = item["original_raw_bytes"].decode("euc_kr")
        self.assertIn(",0,0", raw)
        raw = raw.replace(",0,0", ",999,0", 1)
        retarget_original_bytes(item, raw.encode("euc_kr"))
        with self.assertRaisesRegex(
            KRXInvestorFlowPandasDigestError,
            "ORIGINAL_PANDAS_PAYLOAD_SHA_MISMATCH",
        ):
            verify_2022_krx_flow_pandas_payload(**item)

    def test_reordered_valid_unique_days_change_the_original_pandas_hash(self):
        item = valid_case()
        original = item["original_raw_bytes"].decode("euc_kr")
        lines = original.splitlines(keepends=True)
        lines[1], lines[2] = lines[2], lines[1]
        retarget_original_bytes(item, "".join(lines).encode("euc_kr"))
        with self.assertRaisesRegex(
            KRXInvestorFlowPandasDigestError,
            "ORIGINAL_PANDAS_PAYLOAD_SHA_MISMATCH",
        ):
            verify_2022_krx_flow_pandas_payload(**item)

    def test_dtype_change_caught_before_row_hash_check(self):
        item = valid_case()
        raw = item["original_raw_bytes"].decode("euc_kr")
        raw = raw.replace(",0,0", ",NOT_A_NUMBER,0", 1)
        retarget_original_bytes(item, raw.encode("euc_kr"))
        with self.assertRaisesRegex(
            KRXInvestorFlowPandasDigestError,
            "ORIGINAL_PANDAS_SCHEMA_SHA_MISMATCH",
        ):
            verify_2022_krx_flow_pandas_payload(**item)

    def test_wrong_schema_digest_even_if_checkpoint_and_receipt_are_rehashed(self):
        item = valid_case()
        receipt = item["acquisition_receipt"]
        receipt["response_schema_sha256"] = "a"*64
        receipt["receipt_fingerprint_sha256"] = _sha({
            name: receipt[name] for name in RECEIPT_BODY
        })
        item["completion"]["response_schema_sha256"] = receipt["response_schema_sha256"]
        item["completion"]["receipt_fingerprint_sha256"] = receipt["receipt_fingerprint_sha256"]
        with self.assertRaisesRegex(
            KRXInvestorFlowPandasDigestError,
            "ORIGINAL_PANDAS_SCHEMA_SHA_MISMATCH",
        ):
            verify_2022_krx_flow_pandas_payload(**item)

    def test_wrong_payload_digest_even_if_checkpoint_and_receipt_are_rehashed(self):
        item = valid_case()
        rec = item["acquisition_receipt"]
        rec["response_payload_sha256"] = "f"*64
        rec["receipt_fingerprint_sha256"] = _sha({
            name: rec[name] for name in RECEIPT_BODY
        })
        item["completion"]["response_payload_sha256"] = rec["response_payload_sha256"]
        item["completion"]["receipt_fingerprint_sha256"] = rec["receipt_fingerprint_sha256"]
        with self.assertRaisesRegex(
            KRXInvestorFlowPandasDigestError,
            "ORIGINAL_PANDAS_PAYLOAD_SHA_MISMATCH",
        ):
            verify_2022_krx_flow_pandas_payload(**item)

    def test_mismatched_pandas_version_blocks_even_valid_source(self):
        item = valid_case()
        with patch.object(pd, "__version__", "0.0.0"):
            with self.assertRaisesRegex(
                KRXInvestorFlowPandasDigestError,
                "ORIGINAL_PANDAS_VERSION_DRIFT",
            ):
                verify_2022_krx_flow_pandas_payload(**item)

    def test_mismatched_numpy_version_blocks_even_valid_source(self):
        item = valid_case()
        with patch.object(np, "__version__", "0.0.0"):
            with self.assertRaisesRegex(
                KRXInvestorFlowPandasDigestError,
                "ORIGINAL_NUMPY_VERSION_DRIFT",
            ):
                verify_2022_krx_flow_pandas_payload(**item)

    def test_forged_text_foreign_amount_with_every_hash_recomputed_is_rejected(self):
        item = valid_case()
        _retarget_rehash_one_investor_cell(item, "외국인", "NOT_A_NUMBER")
        with self.assertRaisesRegex(
            KRXInvestorFlowPandasDigestError,
            "ORIGINAL_INVESTOR_AMOUNT_NOT_FINITE_NUMERIC_FORMAT",
        ):
            verify_2022_krx_flow_pandas_payload(**item)

    def test_rehashed_missing_pension_numeric_cell_is_rejected(self):
        item = valid_case()
        _retarget_rehash_one_investor_cell(item, "연기금 등", "")
        with self.assertRaisesRegex(
            KRXInvestorFlowPandasDigestError,
            "ORIGINAL_INVESTOR_AMOUNT_NOT_FINITE_NUMERIC_FORMAT",
        ):
            verify_2022_krx_flow_pandas_payload(**item)

    def test_rehashed_bad_institution_thousands_grouping_is_rejected(self):
        item = valid_case()
        _retarget_rehash_one_investor_cell(item, "금융투자", "1,23,456")
        with self.assertRaisesRegex(
            KRXInvestorFlowPandasDigestError,
            "ORIGINAL_INVESTOR_AMOUNT_NOT_FINITE_NUMERIC_FORMAT",
        ):
            verify_2022_krx_flow_pandas_payload(**item)

    def test_forged_nonfinite_or_exponent_display_is_rejected(self):
        for bad in ("NaN", "inf", "1e+9", "--", "--120", "(10)", "N/A"):
            with self.subTest(value=bad):
                item = valid_case()
                _retarget_rehash_one_investor_cell(item, "보험", bad)
                with self.assertRaisesRegex(
                    KRXInvestorFlowPandasDigestError,
                    "ORIGINAL_INVESTOR_AMOUNT_NOT_FINITE_NUMERIC_FORMAT",
                ):
                    verify_2022_krx_flow_pandas_payload(**item)

    def test_original_display_negative_grouping_decimal_and_zero_remain_nonadmitted(self):
        for sample in ("-1,234", "+1,234.50", "0", "-12.25", "1200000"):
            with self.subTest(display=sample):
                item = valid_case()
                _retarget_rehash_one_investor_cell(item, "외국인", sample)
                proof = verify_2022_krx_flow_pandas_payload(**item)
                self.assertTrue(
                    proof["original_2022_foreign_institution_amount_display_format_checked"]
                )
                self.assertFalse(
                    proof["original_2022_net_buy_amount_unit_or_scale_verified"]
                )
                self.assertFalse(proof["source_admitted"])
                self.assertFalse(proof["performance_testing_authorized"])

    def test_header_only_empty_original_csv_has_zero_rows_without_pit_admission(self):
        item = valid_case()
        raw = item["original_raw_bytes"].decode("euc_kr")
        retarget_original_bytes(item, raw.splitlines(keepends=True)[0].encode("euc_kr"))
        _rebuild_receipt_for_original_csv(item)
        result = verify_2022_krx_flow_pandas_payload(**item)
        self.assertFalse(result["has_nonempty_source_response"])
        self.assertTrue(result["original_pandas_payload_sha_matches_archived_receipt"])
        self.assertFalse(result["source_admitted"])


if __name__ == "__main__":
    unittest.main()
