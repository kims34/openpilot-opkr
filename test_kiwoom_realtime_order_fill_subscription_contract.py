import inspect
import unittest
import kiwoom_realtime_order_fill_subscription_contract as contract
from kiwoom_realtime_order_fill_subscription_contract import (
    KiwoomRealtimeEnvelopeError, build_order_fill_registration,
    validate_type00_field_allowlist,
)

class KiwoomRealtimeEnvelopeTests(unittest.TestCase):
    def test_official_registration_shape_is_frozen_offline(self):
        out=build_order_fill_registration()
        self.assertEqual(out["path"],"/api/dostk/websocket")
        self.assertEqual(out["body"],{
            "trnm":"REG","grp_no":"1","refresh":"1",
            "data":[{"item":[],"type":["00"]}],
        })
        self.assertFalse(out["websocket_opened"])
        self.assertFalse(out["subscription_sent"])
        self.assertFalse(out["real_orders_authorized"])

    def test_group_and_refresh_validation_fail_closed(self):
        for group in ("", "x", "1\n", 1, None):
            with self.assertRaises(KiwoomRealtimeEnvelopeError):
                build_order_fill_registration(group_no=group)
        for refresh in ("2", "", 1, None):
            with self.assertRaises(KiwoomRealtimeEnvelopeError):
                build_order_fill_registration(refresh=refresh)

    def test_type00_allowlist_never_promotes_capture(self):
        out=validate_type00_field_allowlist({
            "9201":"private-account","9203":"0000001","913":"체결",
            "908":"091501","909":"native-fill-1","914":"1000","915":"1",
        })
        self.assertTrue(out["broker_execution_id_present"])
        self.assertFalse(out["broker_native_execution_id_capture_tested"])
        self.assertFalse(out["genuine_live_provenance_verified"])

    def test_unknown_or_nonstring_fields_fail_closed(self):
        with self.assertRaises(KiwoomRealtimeEnvelopeError):
            validate_type00_field_allowlist({"999999":"x"})
        with self.assertRaises(KiwoomRealtimeEnvelopeError):
            validate_type00_field_allowlist({"909":123})

    def test_module_has_no_network_transport(self):
        source=inspect.getsource(contract)
        for forbidden in ("websockets", "requests.", "urllib", "http.client", "socket.", "get_ws_client", "collect_realtime"):
            self.assertNotIn(forbidden,source)

if __name__=="__main__": unittest.main()
