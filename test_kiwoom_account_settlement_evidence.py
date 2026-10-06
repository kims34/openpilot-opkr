import unittest
from kiwoom_account_settlement_evidence import (
    SettlementEvidenceError, normalize_kt00001_settlement,
)

FP = "a" * 64
TS = "2026-10-06T10:00:00+09:00"

class SettlementEvidenceTests(unittest.TestCase):
    def test_normalizes_without_admission(self):
        out = normalize_kt00001_settlement(
            {"entr":"100000","pymn_alow_amt":"90000","d2_entra":"95000","ord_alow_amt":"50000"},
            account_fingerprint=FP, captured_at=TS,
        ).report()
        self.assertEqual(out["deposit_cash_krw"], "100000")
        self.assertEqual(out["orderable_amount_krw"], "50000")
        self.assertEqual(out["withdrawable_cash_krw"], "90000")
        self.assertEqual(out["d2_estimated_cash_krw"], "95000")
        self.assertNotIn("available_cash_krw", out)
        self.assertFalse(out["buying_power_verified"])
        self.assertFalse(out["account_settlement_admitted"])
        self.assertFalse(out["real_orders_authorized"])

    def test_missing_or_negative_fields_fail_closed(self):
        bad = [
            {},
            {"entr":"-1","pymn_alow_amt":"0","d2_entra":"0","ord_alow_amt":"0"},
            {"entr":"1","pymn_alow_amt":"","d2_entra":"1","ord_alow_amt":"1"},
        ]
        for row in bad:
            with self.assertRaises(SettlementEvidenceError):
                normalize_kt00001_settlement(row, account_fingerprint=FP, captured_at=TS)

    def test_rejects_coerced_numeric_types(self):
        with self.assertRaises(SettlementEvidenceError):
            normalize_kt00001_settlement(
                {"entr":1,"pymn_alow_amt":"1","d2_entra":"1","ord_alow_amt":"1"},
                account_fingerprint=FP, captured_at=TS,
            )

    def test_missing_orderable_amount_never_falls_back_to_deposit_or_d2(self):
        with self.assertRaises(SettlementEvidenceError):
            normalize_kt00001_settlement(
                {"entr":"100000","pymn_alow_amt":"90000","d2_entra":"95000"},
                account_fingerprint=FP, captured_at=TS)

    def test_invalid_capture_time_or_account_cannot_be_normalized(self):
        row = {"entr":"1","pymn_alow_amt":"1","d2_entra":"1","ord_alow_amt":"1"}
        for timestamp in ("not-a-dateZ", "2026-10-06T10:00:00", "2026-99-06T10:00:00+09:00"):
            with self.assertRaises(SettlementEvidenceError):
                normalize_kt00001_settlement(row, account_fingerprint=FP, captured_at=timestamp)
        with self.assertRaises(SettlementEvidenceError):
            normalize_kt00001_settlement(row, account_fingerprint="arbitrary-identity", captured_at=TS)

if __name__ == "__main__":
    unittest.main()
