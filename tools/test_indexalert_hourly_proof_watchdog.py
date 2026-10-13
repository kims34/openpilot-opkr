"""Offline tests for fail-closed proof watchdog (never call the network)."""
import unittest
from indexalert_hourly_proof_watchdog import build_report, extract_pr_fields

SHA = "a" * 40

def sample(number):
    return {
        "number": number, "state": "open", "draft": True,
        "head": {"sha": SHA}, "updated_at": "2026-10-13T10:00:00Z",
        "html_url": f"https://github.com/kims34/openpilot-opkr/pull/{number}",
    }

class ProofWatchdogTests(unittest.TestCase):
    def test_complete_snapshot_never_grants_authority(self):
        report = build_report(lambda url, token: sample(int(url.rsplit("/", 1)[-1])))
        self.assertTrue(report["checks_completed"])
        self.assertEqual(len(report["workstreams"]), 5)
        for flag in (
            "m20_performance_run_authorized", "independent_holdout_authorized",
            "automatic_promotion_authorized", "real_order_authorized",
            "funds_movement_authorized", "ordering_switch_change_authorized",
        ):
            self.assertIs(report[flag], False)
        self.assertEqual(report["source_pit_admission"], "NOT_ATTESTED_BY_WATCHDOG")

    def test_partial_failed_fetch_cannot_claim_success(self):
        def fetch(url, token):
            if url.endswith("/414"):
                raise TimeoutError("blocked")
            return sample(int(url.rsplit("/", 1)[-1]))
        report = build_report(fetch)
        self.assertFalse(report["checks_completed"])
        self.assertEqual(report["workstreams"]["profitability"]["status"], "UNVERIFIED")
        self.assertIn("READ_ONLY_GITHUB_METADATA_INCOMPLETE", report["blockers"])

    def test_reject_missing_head_and_non_boolean_draft(self):
        for bad in ({}, {"state": "open", "draft": "false", "head": {"sha": SHA}}):
            with self.assertRaises(ValueError):
                extract_pr_fields(bad)

    def test_never_accept_non_sha(self):
        bad = sample(412)
        bad["head"]["sha"] = "not-an-original-hash"
        with self.assertRaises(ValueError):
            extract_pr_fields(bad)

if __name__ == "__main__":
    unittest.main()
