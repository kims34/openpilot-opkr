import unittest
from kiwoom_real_readonly_preparation import (
    RealReadOnlyPreparationError, assess_real_readonly_preparation, require_readonly_api,
)


class RealReadOnlyPreparationTests(unittest.TestCase):
    def setUp(self):
        self.cfg={"KIWOOM_ENV":"REAL","KIWOOM_BASE_URL":"https://api.kiwoom.com",
                  "KIWOOM_ORDERING_ENABLED":"false","KIWOOM_APP_KEY":"synthetic-key",
                  "KIWOOM_APP_SECRET":"synthetic-secret"}

    def test_exact_real_readonly_configuration_is_non_authorizing(self):
        r=assess_real_readonly_preparation(self.cfg)
        self.assertTrue(r["configuration_admitted"])
        for k in ("network_request_attempted","credentials_validated","account_origin_authenticated",
                  "broker_connectivity_verified","account_settlement_admitted",
                  "genuine_live_provenance_verified","early_live_authorized","real_orders_authorized",
                  "funds_movement_authorized","broker_permission_change_authorized"):
            self.assertFalse(r[k])
        self.assertNotIn(self.cfg["KIWOOM_APP_KEY"],repr(r))
        self.assertNotIn(self.cfg["KIWOOM_APP_SECRET"],repr(r))

    def test_ambiguous_or_order_enabled_configuration_fails_closed(self):
        for change in ({"KIWOOM_ENV":"DEMO"},{"KIWOOM_BASE_URL":"https://api.kiwoom.com/"},
                       {"KIWOOM_ORDERING_ENABLED":"true"},{"KIWOOM_APP_KEY":""},{"KIWOOM_APP_SECRET":""}):
            with self.assertRaises(RealReadOnlyPreparationError):
                assess_real_readonly_preparation(dict(self.cfg,**change))

    def test_only_reviewed_query_ids_are_admitted(self):
        for api in ("ka00001","kt00007","ka10076","kt00018"):
            self.assertEqual(require_readonly_api(api),api)
        for api in ("kt10000","kt10001","kt10002","kt10003","/oauth2/revoke","KA00001",""):
            with self.assertRaises(RealReadOnlyPreparationError):
                require_readonly_api(api)


if __name__=="__main__":
    unittest.main()
