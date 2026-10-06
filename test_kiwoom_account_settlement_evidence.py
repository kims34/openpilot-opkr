import unittest
from kiwoom_account_settlement_evidence import (
    SettlementEvidenceError, normalize_kt00001_settlement,
)

FP = "a" * 64
TS = "2026-10-06T10:00:00+09:00"

class SettlementEvidenceTests(unittest.TestCase):
    def test_normalizes_without_admission(self):
        out = normalize_kt00001_settlement(
            {"entr":"100000","pymn_alow_amt":"90000","d2_entra":"95000"},
            account_fingerprint=FP, captured_at=TS,
        ).report()
        self.assertEqual(out["available_cash_krw"], "100000")
        self.assertFalse(out["account_settlement_admitted"])
        self.assertFalse(out["real_orders_authorized"])

    def test_missing_or_negative_fields_fail_closed(self):
        bad = [
            {},
            {"entr":"-1","pymn_alow_amt":"0","d2_entra":"0"},
            {"entr":"1","pymn_alow_amt":"","d2_entra":"1"},
        ]
        for row in bad:
            with self.assertRaises(SettlementEvidenceError):
                normalize_kt00001_settlement(row, account_fingerprint=FP, captured_at=TS)

    def test_rejects_coerced_numeric_types(self):
        with self.assertRaises(SettlementEvidenceError):
            normalize_kt00001_settlement(
                {"entr":1,"pymn_alow_amt":"1","d2_entra":"1"},
                account_fingerprint=FP, captured_at=TS,
            )

if __name__ == "__main__":
    unittest.main()
