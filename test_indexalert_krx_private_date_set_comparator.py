"""Synthetic-only KRX date-by-date source vs reference calendar guards."""
import hashlib
import json
import unittest
from datetime import date, timedelta

from research_v1_krx_private_date_set_comparator import (
    reconcile_exact_date_sets as check, audit_private_scope,
)

NONEMPTY="NONEMPTY_OFFICIAL_KOSPI_PAIR_NOT_PIT_ADMITTED"
EMPTY="DAILY_EMPTY_MASTER_PRESENT_UNVERIFIED_CALENDAR_OR_SOURCE_GAP"
P="a"*64
START,END="2026-06-01","2026-06-05"
DAYS=["2026-06-01","2026-06-02","2026-06-03","2026-06-04","2026-06-05"]


def row(day,empty=False):
    return {"day":day.replace("-",""),"pair_sha256":P,
            "source_day_class":EMPTY if empty else NONEMPTY,
            "daily_rows":0 if empty else 800,
            "common_rows":0 if empty else 600}


def original(empties=("2026-06-03",)):
    return [row(d,d in empties) for d in DAYS]


class ExactPrivateDaySetBoundary(unittest.TestCase):
    def test_same_exact_dates_still_not_official_or_pit(self):
        x=check(start=START,end=END,verified_original_days=original(),
                reference_closed_iso_days=["2026-06-03"],expected_empty_count=1)
        self.assertEqual(x["status"],"EXACT_DATE_SET_AGREES_REFERENCE_ONLY_NOT_PIT")
        self.assertEqual(x["empty_on_reference_closed"],1)
        self.assertEqual(x["empty_on_reference_open"],0)
        self.assertEqual(x["nonempty_on_reference_closed"],0)
        for k in ("original_official_calendar_attested","source_contract_gates_C_D_open",
                  "historical_pit_available_at_verified","original_security_status_verified",
                  "performance_run_authorized","real_orders_authorized"):
            self.assertFalse(x[k])
        self.assertIsNone(x.get("actual_dates"))
        self.assertEqual(x["27_quarantined_securities_released"],False)

    def test_equal_counts_wrong_dates_fails(self):
        x=check(start=START,end=END,verified_original_days=original(),
                reference_closed_iso_days=["2026-06-04"],expected_empty_count=1)
        self.assertEqual(x["original_empty_day_count"],x["reference_closed_day_count"])
        self.assertEqual(x["empty_on_reference_open"],1)
        self.assertEqual(x["nonempty_on_reference_closed"],1)
        self.assertEqual(x["status"],"EXACT_DATE_SET_MISMATCH_SOURCE_ADMISSION_BLOCKED")

    def test_mismatch_old_aggregate_receipt_fails(self):
        x=check(start=START,end=END,verified_original_days=original(),
                reference_closed_iso_days=["2026-06-03"],expected_empty_count=2)
        self.assertEqual(x["status"],"FAIL_CLOSED_AGGREGATE_SOURCE_RECEIPT_DRIFT")
        self.assertFalse(x["source_contract_gates_C_D_open"])

    def test_missing_date_or_duplicate_never_passes(self):
        for rows in (original()[:-1],original()+[row(DAYS[0])]):
            self.assertEqual(check(start=START,end=END,verified_original_days=rows,
                reference_closed_iso_days=["2026-06-03"])["status"],
                "FAIL_CLOSED_INVALID_OR_MISSING_DATE_LEVEL_EVIDENCE")

    def test_wrong_raw_pair_digest_never_passes(self):
        rows=original()
        rows[0]["pair_sha256"]="corrupt"
        self.assertEqual(check(start=START,end=END,verified_original_days=rows,
            reference_closed_iso_days=["2026-06-03"])["status"],
            "FAIL_CLOSED_INVALID_OR_MISSING_DATE_LEVEL_EVIDENCE")

    def test_weekend_or_out_of_scope_reference_fails(self):
        for dates in (["2026-06-06"],["2026-07-17"],["2026-06-03","2026-06-03"]):
            self.assertEqual(check(start=START,end=END,verified_original_days=original(),
                reference_closed_iso_days=dates)["status"],
                "FAIL_CLOSED_INVALID_OR_MISSING_DATE_LEVEL_EVIDENCE")

    def test_nonempty_with_zero_common_invalid(self):
        rows=original()
        rows[0]["common_rows"]=0
        self.assertEqual(check(start=START,end=END,verified_original_days=rows,
            reference_closed_iso_days=["2026-06-03"])["status"],
            "FAIL_CLOSED_INVALID_OR_MISSING_DATE_LEVEL_EVIDENCE")

    def test_boolean_row_counts_invalid(self):
        rows=original()
        rows[1]["daily_rows"]=True
        self.assertEqual(check(start=START,end=END,verified_original_days=rows,
            reference_closed_iso_days=["2026-06-03"])["status"],
            "FAIL_CLOSED_INVALID_OR_MISSING_DATE_LEVEL_EVIDENCE")

    def test_fingerprints_consistent_and_no_raw_date_rows_returned(self):
        a=check(start=START,end=END,verified_original_days=original(),
                reference_closed_iso_days=["2026-06-03"])
        b=check(start=START,end=END,verified_original_days=list(reversed(original())),
                reference_closed_iso_days=["2026-06-03"])
        self.assertEqual(a["original_pair_scope_sha256"],b["original_pair_scope_sha256"])
        self.assertEqual(a["comparison_metadata_sha256"],b["comparison_metadata_sha256"])
        self.assertEqual(len(a["original_pair_scope_sha256"]),64)
        self.assertNotIn("2026-06-03",json.dumps(a))

    def test_injected_synthetic_callback_never_proves_original(self):
        by={r["day"]:r for r in original()}
        x=audit_private_scope(
            private_root="/tmp/synthetic-only",start=START,end=END,
            reference_closed_iso_days=["2026-06-03"],expected_empty_count=1,
            existing_audit=lambda root,day:by[day])
        self.assertEqual(x["status"],"SYNTHETIC_CALLBACK_NOT_ORIGINAL_SOURCE_PROOF")
        self.assertFalse(x["original_official_calendar_attested"])

    def test_no_execution_on_bad_private_volume(self):
        x=audit_private_scope(
            private_root="/tmp/not-railway-volume",start=START,end=END,
            reference_closed_iso_days=["2026-06-03"],expected_empty_count=1,
        )
        self.assertEqual(x["status"],"FAIL_CLOSED_NOT_AUTHORIZED_PRIVATE_AUDIT_ENV")


if __name__=="__main__":
    unittest.main()
