import unittest
from indexalert_automation_control import (
    AutomationCapitalState, AutomationControlError, AutomationUserControls,
    DecisionAction, EngineOrderIntent, validate_engine_plan,
)

class RiskBoundaryTests(unittest.TestCase):
    def test_unknown_or_string_actions_cannot_bypass_disabled_control(self):
        for action in ("BUY", "EXIT", "UNKNOWN", None, 1):
            with self.subTest(action=action), self.assertRaises(AutomationControlError):
                validate_engine_plan(AutomationUserControls(False,100000), AutomationCapitalState(0,0), [EngineOrderIntent(action,"005930",10000)])

    def test_idle_or_exit_cannot_hide_new_exposure_even_when_disabled(self):
        for action in (DecisionAction.HOLD, DecisionAction.EXIT, DecisionAction.NO_TRADE):
            for enabled in (True,False):
                with self.subTest(action=action,enabled=enabled), self.assertRaises(AutomationControlError):
                    validate_engine_plan(AutomationUserControls(enabled,100000),AutomationCapitalState(0,0),[EngineOrderIntent(action,"005930",10000)])

    def test_entry_cannot_claim_zero_reservation(self):
        for action in (DecisionAction.BUY,DecisionAction.REPLACE):
            with self.subTest(action=action), self.assertRaises(AutomationControlError):
                EngineOrderIntent(action,"005930",0).validate()

    def test_lowered_ceiling_does_not_trap_positions(self):
        state=AutomationCapitalState(120000,20000,10000,2000)
        for enabled in (True,False):
            controls=AutomationUserControls(enabled,0)
            for action,symbol in ((DecisionAction.EXIT,"005930"),(DecisionAction.HOLD,"005930"),(DecisionAction.NO_TRADE,None)):
                with self.subTest(enabled=enabled,action=action):
                    self.assertEqual(len(validate_engine_plan(controls,state,[EngineOrderIntent(action,symbol,0)])),1)

    def test_existing_over_capital_cannot_add_exposure(self):
        for action in (DecisionAction.BUY,DecisionAction.REPLACE):
            with self.subTest(action=action), self.assertRaises(AutomationControlError):
                validate_engine_plan(AutomationUserControls(True,100000),AutomationCapitalState(100001,0),[EngineOrderIntent(action,"005930",1)])

    def test_partial_and_uncertain_reservations_enforce_aggregate_ceiling(self):
        state=AutomationCapitalState(30000,30000,30000,5000)
        controls=AutomationUserControls(True,100000)
        self.assertEqual(len(validate_engine_plan(controls,state,[EngineOrderIntent(DecisionAction.BUY,"005930",5000)])),1)
        with self.assertRaises(AutomationControlError):
            validate_engine_plan(controls,state,[EngineOrderIntent(DecisionAction.BUY,"005930",3000),EngineOrderIntent(DecisionAction.BUY,"000660",3000)])

    def test_malformed_types_fail_closed(self):
        for intents in (None,"BUY",[{}],[object()]):
            with self.subTest(intents=intents), self.assertRaises(AutomationControlError):
                validate_engine_plan(AutomationUserControls(True,100000),AutomationCapitalState(0,0),intents)
        with self.assertRaises(AutomationControlError):
            EngineOrderIntent(DecisionAction.BUY,123,1000).validate()

    def test_position_actions_require_identity(self):
        for action in (DecisionAction.HOLD,DecisionAction.EXIT,DecisionAction.REPLACE):
            with self.subTest(action=action), self.assertRaises(AutomationControlError):
                EngineOrderIntent(action,None,1000 if action==DecisionAction.REPLACE else 0).validate()

if __name__ == '__main__': unittest.main()
