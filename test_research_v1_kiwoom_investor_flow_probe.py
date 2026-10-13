"""Offline contract tests of the existing ka10059 probe, no network calls."""
from __future__ import annotations

import json
import unittest

from research_v1_kiwoom_investor_flow_probe import BODY, run
from research_v1_kiwoom_flow_source_gate import audit_kiwoom_probe


ENV = {
    "KIWOOM_ORDERING_ENABLED": "false",
    "KIWOOM_ENV": "REAL",
    "KIWOOM_BASE_URL": "https://api.kiwoom.com",
    "KIWOOM_APP_KEY": "SYNTHETIC_TEST_APP",
    "KIWOOM_APP_SECRET": "SYNTHETIC_TEST_SECRET",
}


def stock_row(date="20261008", **changes):
    row = {
        "dt": date, "frgnr_invsr": "-5000", "orgn": "4000",
        "acc_trde_prica": "100000", "acc_trde_qty": "100",
    }
    row.update(changes)
    return row


def fake_sender(*, pages=None, auth_code=0, data_code=0, next_keys=None):
    seen = []
    pages = [[stock_row()]] if pages is None else pages
    next_keys = next_keys or [None] * len(pages)

    def send(path, body, token=None, continuation=None):
        seen.append((path, dict(body), continuation))
        if path == "/oauth2/token":
            return {"return_code": auth_code, "token": "EPHEMERAL_SYNTHETIC"}, {}, "a" * 64
        assert path == "/api/dostk/stkinfo"
        assert body == BODY
        assert token == "EPHEMERAL_SYNTHETIC"
        idx = len([event for event in seen if event[0] == "/api/dostk/stkinfo"]) - 1
        if idx >= len(pages):
            raise AssertionError("unexpected extra page")
        more = idx < len(pages) - 1
        headers = {"cont-yn": "Y" if more else "N"}
        if more and idx < len(next_keys) and next_keys[idx]:
            headers["next-key"] = next_keys[idx]
        return {"return_code": data_code, "stk_invsr_orgn": pages[idx]}, headers, "b" * 64

    return send, seen


class KiwoomBoundedSourceProbeOfflineTest(unittest.TestCase):
    def test_no_credentials_prevents_requests(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("must not call network")
        env = dict(ENV)
        env.pop("KIWOOM_APP_SECRET")
        self.assertEqual(run(env, send=forbidden)["status"], "AUTH_NOT_CONFIGURED")

    def test_ordering_enabled_prevents_requests(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("must not call network")
        env = dict(ENV, KIWOOM_ORDERING_ENABLED="true")
        self.assertEqual(run(env, send=forbidden)["status"], "ORDERING_CONFIG_BLOCKED")

    def test_wrong_host_prevents_requests(self):
        def forbidden(*args, **kwargs):
            raise AssertionError("must not call network")
        env = dict(ENV, KIWOOM_BASE_URL="https://example.org")
        self.assertEqual(run(env, send=forbidden)["status"], "REAL_HOST_CONFIG_BLOCKED")

    def test_broker_auth_failure_stops_before_data_request(self):
        send, seen = fake_sender(auth_code=8050)
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "AUTH_REJECTED")
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0][0], "/oauth2/token")

    def test_valid_synthetic_one_page_is_not_admitted_or_raw_persisted(self):
        send, seen = fake_sender()
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "SOURCE_REACHABLE_METADATA_ONLY")
        self.assertTrue(result["pagination_exhausted"])
        self.assertFalse(result["history_exhausted"])
        self.assertFalse(result["historical_retention_verified"])
        self.assertEqual(result["pages"][0]["rows"], 1)
        self.assertEqual(result["pages"][0]["negative_activity_rows"], 0)
        self.assertEqual(result["pages"][0]["nonmonotonic_date_pairs"], 0)
        self.assertEqual(len(seen), 2)
        published = json.dumps(result)
        for sensitive in ("SYNTHETIC_TEST_APP", "SYNTHETIC_TEST_SECRET", "EPHEMERAL_SYNTHETIC"):
            self.assertNotIn(sensitive, published)
        gate = audit_kiwoom_probe(result)
        self.assertTrue(gate["metadata_validation_pass"])
        self.assertFalse(gate["bounded_route_reachability"])
        self.assertFalse(gate["source_admitted"])
        self.assertFalse(gate["performance_testing_authorized"])

    def test_trading_volume_is_required(self):
        send, _ = fake_sender(pages=[[{
            "dt": "20261008", "frgnr_invsr": "-5000", "orgn": "4000", "acc_trde_prica": "100000",
        }]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "ROW_VALIDATION_REJECTED")
        self.assertEqual(result["pages"][0]["missing_required_rows"], 1)

    def test_negative_trading_value_is_rejected(self):
        send, _ = fake_sender(pages=[[stock_row(acc_trde_prica="-1")]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "ROW_VALIDATION_REJECTED")
        self.assertEqual(result["pages"][0]["negative_activity_rows"], 1)


    def test_negative_fractional_cumulative_value_is_rejected(self):
        send, _ = fake_sender(pages=[[stock_row(acc_trde_prica="-0.5")]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "ROW_VALIDATION_REJECTED")
        self.assertEqual(result["pages"][0]["negative_activity_rows"], 1)

    def test_negative_fractional_cumulative_quantity_is_rejected(self):
        send, _ = fake_sender(pages=[[stock_row(acc_trde_qty="-1.25")]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "ROW_VALIDATION_REJECTED")
        self.assertEqual(result["pages"][0]["negative_activity_rows"], 1)

    def test_large_negative_integer_is_rejected_without_float_overflow(self):
        send, _ = fake_sender(pages=[[stock_row(acc_trde_prica="-" + "9" * 500)]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "ROW_VALIDATION_REJECTED")
        self.assertEqual(result["pages"][0]["negative_activity_rows"], 1)

    def test_nonnegative_fractional_activity_preserves_schema_not_pit_authority(self):
        send, _ = fake_sender(pages=[[stock_row(acc_trde_prica="0.5", acc_trde_qty="1.25")]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "SOURCE_REACHABLE_METADATA_ONLY")
        self.assertFalse(audit_kiwoom_probe(result)["source_admitted"])

    def test_negative_net_buy_is_allowed_as_signed_numeric_data(self):
        send, _ = fake_sender(pages=[[stock_row(frgnr_invsr="-42", orgn="-1")]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "SOURCE_REACHABLE_METADATA_ONLY")

    def test_zero_liquidity_is_not_fabricated_into_missing(self):
        send, _ = fake_sender(pages=[[stock_row(acc_trde_prica="0", acc_trde_qty="0")]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "SOURCE_REACHABLE_METADATA_ONLY")
        self.assertFalse(audit_kiwoom_probe(result)["source_admitted"])

    def test_future_date_is_rejected(self):
        send, _ = fake_sender(pages=[[stock_row("20261009")]])
        self.assertEqual(run(ENV, send=send)["status"], "ROW_VALIDATION_REJECTED")

    def test_nonmonotonic_dates_fail(self):
        send, _ = fake_sender(pages=[[stock_row("20261007"), stock_row("20261008")]])
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "ROW_VALIDATION_REJECTED")
        self.assertEqual(result["pages"][0]["nonmonotonic_date_pairs"], 1)

    def test_missing_next_key_fails(self):
        send, _ = fake_sender(
            pages=[[stock_row("20261008")], [stock_row("20261007")]],
            next_keys=[None, None],
        )
        self.assertEqual(run(ENV, send=send)["status"], "CONTINUATION_REJECTED")

    def test_duplicate_days_across_pages_fail_gate(self):
        send, _ = fake_sender(
            pages=[[stock_row("20261008")], [stock_row("20261008")]],
            next_keys=["SYNTHETIC_NEXT_KEY", None],
        )
        result = run(ENV, send=send)
        self.assertEqual(result["duplicate_dates"], 1)
        self.assertEqual(result["status"], "PAGINATION_VALIDATION_REJECTED")
        self.assertFalse(audit_kiwoom_probe(result)["metadata_validation_pass"])

    def test_broker_data_error_is_not_source_success(self):
        send, _ = fake_sender(data_code=8050)
        result = run(ENV, send=send)
        self.assertEqual(result["status"], "DATA_REQUEST_REJECTED")
        self.assertFalse(audit_kiwoom_probe(result)["bounded_route_reachability"])


if __name__ == "__main__":
    unittest.main()
