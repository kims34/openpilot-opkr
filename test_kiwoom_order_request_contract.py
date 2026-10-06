import inspect
import unittest
import kiwoom_order_request_contract as contract
from kiwoom_order_request_contract import (
    KiwoomOrderEnvelopeError, build_new_order, build_cancel_order, build_modify_order,
)

class KiwoomOrderRequestContractTests(unittest.TestCase):
    def test_buy_and_sell_match_reviewed_api_ids_without_authority(self):
        for side, api_id in (("BUY","kt10000"),("SELL","kt10001")):
            out=build_new_order(side=side,dmst_stex_tp="KRX",stk_cd="005930",
                ord_qty="1",trde_tp="3",ord_uv="",cond_uv="")
            self.assertEqual(out["api_id"],api_id)
            self.assertEqual(out["path"],"/api/dostk/ordr")
            self.assertFalse(out["broker_request_sent"])
            self.assertFalse(out["real_orders_authorized"])
            self.assertTrue(out["requires_separate_activation_authorization"])

    def test_cancel_and_modify_match_reviewed_api_ids(self):
        cancel=build_cancel_order(dmst_stex_tp="SOR",orig_ord_no="0000140",
            stk_cd="005930",cncl_qty="0")
        modify=build_modify_order(dmst_stex_tp="NXT",orig_ord_no="0000139",
            stk_cd="005930",mdfy_qty="0",mdfy_uv="199700")
        self.assertEqual(cancel["api_id"],"kt10003")
        self.assertEqual(modify["api_id"],"kt10002")
        self.assertFalse(cancel["broker_request_sent"])
        self.assertFalse(modify["broker_request_sent"])

    def test_invalid_values_fail_closed(self):
        cases = [
            lambda: build_new_order(side="OTHER",dmst_stex_tp="KRX",stk_cd="005930",ord_qty="1",trde_tp="3"),
            lambda: build_new_order(side="BUY",dmst_stex_tp="BAD",stk_cd="005930",ord_qty="1",trde_tp="3"),
            lambda: build_new_order(side="BUY",dmst_stex_tp="KRX",stk_cd="005930",ord_qty="0",trde_tp="3"),
            lambda: build_new_order(side="BUY",dmst_stex_tp="KRX",stk_cd="005930",ord_qty="1",trde_tp="999"),
            lambda: build_cancel_order(dmst_stex_tp="KRX",orig_ord_no="",stk_cd="005930",cncl_qty="1"),
            lambda: build_modify_order(dmst_stex_tp="KRX",orig_ord_no="1",stk_cd="005930",mdfy_qty="1",mdfy_uv="x"),
        ]
        for case in cases:
            with self.assertRaises(KiwoomOrderEnvelopeError): case()

    def test_module_has_no_network_client_or_sender(self):
        source=inspect.getsource(contract)
        for forbidden in ("requests.", "urllib", "http.client", "socket.", "Invoke-WebRequest", "fetch_page("):
            self.assertNotIn(forbidden,source)

if __name__=="__main__": unittest.main()
