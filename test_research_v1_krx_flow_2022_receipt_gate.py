"""Synthetic and adversarial KRX 2022 investor-flow receipt tests; no auth/network."""
from __future__ import annotations

import unittest

from research_v1_krx_flow_2022_receipt_gate import (
    COLUMNS, KRXFlow2022ReceiptError, audit_krx_2022_flow_receipt,
)


def candidate(**changes):
    value = {
        "source": "KRX_DATA_MARKETPLACE_MDCSTAT02303",
        "access_route": "DATA_MARKETPLACE_AUTHENTICATED_WEB_SESSION",
        "api_bld": "dbms/MDC/STAT/standard/MDCSTAT02303",
        "market_scope": "KOSPI",
        "symbol": "005930",
        "isu_cd": "KR7005930003",
        "year": 2022,
        "request_start_date": "2022-10-04",
        "request_end_date": "2022-10-07",
        "ask_bid": "3",
        "trade_volume_value": "2",
        "observed_first_date": "2022-10-04",
        "observed_last_date": "2022-10-07",
        "observed_row_count": 3,
        "columns": sorted(COLUMNS),
        "raw_response_sha256": "a"*64,
        "schema_sha256": "b"*64,
        "retrieved_at": "2026-10-14T08:25:00+09:00",
        "capture_mode": "HISTORICAL_RECONSTRUCTION",
    }
    value.update(changes)
    return value


class KRX2022ReceiptTest(unittest.TestCase):
    def test_declared_shape_cannot_admit_original_2022_vintage(self):
        r = audit_krx_2022_flow_receipt(candidate())
        self.assertTrue(r["source_receipt_shape_compatible"])
        for k in (
            "institution_aggregate_mapping_independently_verified",
            "foreign_aggregate_mapping_independently_verified",
            "exact_krw_units_independently_verified",
            "raw_response_bytes_independently_verified",
            "authenticated_2022_acquisition_independently_verified",
            "original_as_published_2022_vintage_verified",
            "original_publication_time_independently_verified",
            "historical_revision_lineage_verified",
            "historical_identity_episode_verified", "full_universe_coverage_verified",
            "source_admitted", "performance_testing_authorized",
            "sealed_holdout_authorized", "live_trading_authorized",
            "ordering_enabled",
        ):
            self.assertIs(r[k], False, k)
        self.assertNotIn("raw_response_sha256", r)
        self.assertNotIn("isu_cd", r)

    def test_cannot_launder_claimed_proof_flags(self):
        c = candidate(source_admitted=True, original_as_published_2022_vintage_verified=True)
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "allowlist"):
            audit_krx_2022_flow_receipt(c)

    def test_no_raw_value_or_token_field_is_published(self):
        c = candidate(token="DO_NOT_PRINT", 외국인="-1000")
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "allowlist"):
            audit_krx_2022_flow_receipt(c)

    def test_missing_source_digest_rejected(self):
        c = candidate()
        c.pop("raw_response_sha256")
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "allowlist"):
            audit_krx_2022_flow_receipt(c)

    def test_fake_digest_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "fingerprint"):
            audit_krx_2022_flow_receipt(candidate(raw_response_sha256="not-real"))

    def test_route_drift_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "route"):
            audit_krx_2022_flow_receipt(candidate(api_bld="MDCSTAT02203"))

    def test_non_kospi_scope_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "scope"):
            audit_krx_2022_flow_receipt(candidate(market_scope="ALL"))

    def test_2026_probe_cannot_substitute_for_2022(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "year"):
            audit_krx_2022_flow_receipt(candidate(
                year=2026,
                request_start_date="2026-09-21",
                request_end_date="2026-09-23",
                observed_first_date="2026-09-21",
                observed_last_date="2026-09-23",
            ))

    def test_2022_crossed_window_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "bounds"):
            audit_krx_2022_flow_receipt(candidate(observed_last_date="2022-10-11"))

    def test_future_observation_beyond_request_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "bounds"):
            audit_krx_2022_flow_receipt(candidate(observed_first_date="2022-12-31"))

    def test_missing_institution_bucket_rejected(self):
        names = list(COLUMNS - {"사모"})
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "schema"):
            audit_krx_2022_flow_receipt(candidate(columns=names))

    def test_false_foreign_total_promotion_rejected(self):
        names = list(COLUMNS - {"기타외국인"}) + ["외국인 합계"]
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "schema"):
            audit_krx_2022_flow_receipt(candidate(columns=names))

    def test_duplicate_investor_category_rejected(self):
        names = sorted(COLUMNS)
        names[1] = names[0]
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "schema"):
            audit_krx_2022_flow_receipt(candidate(columns=names))

    def test_volume_instead_of_net_value_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "mode mismatch"):
            audit_krx_2022_flow_receipt(candidate(trade_volume_value="1"))

    def test_buy_instead_of_net_buy_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "mode mismatch"):
            audit_krx_2022_flow_receipt(candidate(ask_bid="1"))

    def test_unexpected_historical_capture_mode_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "capture"):
            audit_krx_2022_flow_receipt(candidate(capture_mode="PROSPECTIVE_CAPTURE"))

    def test_naive_retrieval_timestamp_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "timezone offset"):
            audit_krx_2022_flow_receipt(candidate(retrieved_at="2026-10-14T08:25:00"))

    def test_retrieval_predates_requested_history_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "retrieval"):
            audit_krx_2022_flow_receipt(candidate(retrieved_at="2022-10-05T09:00:00+09:00"))

    def test_noninteger_row_count_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "row count"):
            audit_krx_2022_flow_receipt(candidate(observed_row_count=True))

    def test_empty_rows_are_not_proof(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "row count"):
            audit_krx_2022_flow_receipt(candidate(observed_row_count=0))

    def test_invalid_identity_cannot_be_joined(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "identity"):
            audit_krx_2022_flow_receipt(candidate(isu_cd="005930"))

    def test_unhashable_category_type_rejected(self):
        with self.assertRaisesRegex(KRXFlow2022ReceiptError, "schema"):
            audit_krx_2022_flow_receipt(candidate(columns=[["일자"]]*13))


if __name__ == "__main__":
    unittest.main()
