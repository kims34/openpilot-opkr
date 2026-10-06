import unittest
from deferred_user_validations import current_deferred_validations

class DeferredUserValidationTests(unittest.TestCase):
    def test_current_scope_is_completed_without_blocking_independent_development(self):
        out=current_deferred_validations()
        self.assertEqual(out["pending_count"],0)
        self.assertFalse(out["blocks_independent_development"])
        self.assertEqual(out["items"][0]["validation_id"],"KIWOOM_REAL_ACCOUNT_SCOPE_READONLY_v1")
        self.assertTrue(out["items"][0]["completed"])

    def test_tracker_never_grants_sensitive_authority(self):
        out=current_deferred_validations()
        self.assertFalse(out["real_orders_authorized"])
        self.assertFalse(out["funds_movement_authorized"])
        self.assertFalse(out["broker_permission_change_authorized"])

if __name__=="__main__":
    unittest.main()
