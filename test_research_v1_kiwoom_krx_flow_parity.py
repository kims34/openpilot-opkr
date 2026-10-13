"""Synthetic-only test coverage for the quarantined Kiwoom/KRX value-parity auditor."""
import unittest

from research_v1_kiwoom_krx_flow_parity import (
    audit_cross_source_parity, InvestorFlowParityError,
)


def r(source="KIWOOM_KA10059", amount="1000", measure="FOREIGN_NET_BUY_VALUE", **changes):
    out = {
        "source": source,
        "isin": "KR7005930003",
        "symbol": "005930",
        "event_date": "2026-10-08",
        "venue": "KRX",
        "market_scope": "KRX_ONLY",
        "measure": measure,
        "amount_krw": amount,
        "normalization_contract_sha256": "a" * 64,
        "response_sha256": "b" * 64,
    }
    out.update(changes)
    return out


def krx(amount="1000", **changes):
    return r("KRX_DMP_MDCSTAT02303", amount, **changes)


class ValueParityTest(unittest.TestCase):
    def test_matching_synthetic_rows_not_admitted(self):
        result = audit_cross_source_parity([r()], [krx()])
        self.assertTrue(result["declared_scope_exact_numeric_match"])
        self.assertEqual(result["matched_rows"], 1)
        for key in (
            "historical_units_independently_attested",
            "source_originals_authenticated",
            "original_as_published_pit_verified",
            "historical_issuer_universe_complete", "source_admitted",
            "performance_testing_authorized", "holdout_authorized",
            "ordering_enabled",
        ):
            self.assertFalse(result[key], key)

    def test_broker_numeric_mismatch_never_rounded_into_pass(self):
        result = audit_cross_source_parity([r(amount="1000")], [krx("1001")])
        self.assertFalse(result["declared_scope_exact_numeric_match"])
        self.assertEqual(result["numeric_mismatch_rows"], 1)

    def test_negative_net_buy_is_permitted(self):
        result = audit_cross_source_parity([r(amount="-1000")], [krx("-1000")])
        self.assertTrue(result["declared_scope_exact_numeric_match"])

    def test_missing_broker_date_does_not_disappear(self):
        result = audit_cross_source_parity([r()], [krx(), krx(event_date="2026-10-09")])
        self.assertFalse(result["declared_scope_exact_numeric_match"])
        self.assertEqual(result["krx_only_rows"], 1)

    def test_missing_krx_date_does_not_disappear(self):
        result = audit_cross_source_parity([r(), r(event_date="2026-10-09")], [krx()])
        self.assertEqual(result["broker_only_rows"], 1)

    def test_wrong_venue_rejected(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "KRX-only"):
            audit_cross_source_parity([r(venue="SOR")], [krx()])

    def test_integrated_market_scope_rejected(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "KRX-only"):
            audit_cross_source_parity([r(market_scope="KRX_AND_NXT")], [krx()])

    def test_broker_foreign_and_institution_are_separate_metrics(self):
        broker = [r(), r(amount="-400", measure="INSTITUTION_NET_BUY_VALUE")]
        official = [krx(), krx(amount="-400", measure="INSTITUTION_NET_BUY_VALUE")]
        out = audit_cross_source_parity(broker, official)
        self.assertEqual(out["matched_rows"], 2)
        self.assertTrue(out["declared_scope_exact_numeric_match"])

    def test_duplicate_measure_rejected(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "duplicate"):
            audit_cross_source_parity([r(), r()], [krx()])

    def test_institution_subcategory_not_accepted_as_aggregate(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "only foreign"):
            audit_cross_source_parity([r(measure="INSURANCE_NET_BUY_VALUE")], [krx()])

    def test_numeric_krw_must_be_integer(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "exact integer"):
            audit_cross_source_parity([r(amount="1.5")], [krx()])

    def test_bool_cannot_be_numeric_amount(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "exact integer"):
            audit_cross_source_parity([r(amount=True)], [krx()])

    def test_unparseable_amount_rejected(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "invalid amount"):
            audit_cross_source_parity([r(amount="not-a-number")], [krx()])

    def test_unparseable_date_rejected(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "trade day"):
            audit_cross_source_parity([r(event_date="2026-02-30")], [krx()])

    def test_missing_normalization_contract_rejected(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "normalization_contract_sha256"):
            audit_cross_source_parity([r(normalization_contract_sha256="x")], [krx()])

    def test_mixed_contracts_on_one_provider_rejected(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "mixed normalization"):
            audit_cross_source_parity([r(), r(event_date="2026-10-09", normalization_contract_sha256="c"*64)], [krx()])

    def test_no_automatic_fill_for_absent_provider(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "nonempty"):
            audit_cross_source_parity([r()], [])

    def test_deceptive_claim_fields_cannot_grant_authority(self):
        broker = r()
        broker["original_as_published_pit_verified"] = True
        broker["performance_testing_authorized"] = True
        out = audit_cross_source_parity([broker], [krx()])
        self.assertFalse(out["original_as_published_pit_verified"])
        self.assertFalse(out["performance_testing_authorized"])

    def test_unhashable_measure_rejected_cleanly(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "only foreign"):
            audit_cross_source_parity([r(measure=["FOREIGN_NET_BUY_VALUE"])], [krx()])

    def test_null_amount_rejected_cleanly(self):
        with self.assertRaisesRegex(InvestorFlowParityError, "exact integer"):
            audit_cross_source_parity([r(amount=None)], [krx()])


if __name__ == "__main__":
    unittest.main()
