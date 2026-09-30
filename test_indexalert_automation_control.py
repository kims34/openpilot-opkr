import unittest

from indexalert_automation_control import (
    AutomationCapitalState,
    AutomationControlError,
    AutomationUserControls,
    DecisionAction,
    EngineOrderIntent,
    no_trade_plan,
    validate_engine_plan,
)


class AutomationControlContractTest(unittest.TestCase):
    def test_no_trade_is_valid_and_does_not_force_capital_use(self):
        controls = AutomationUserControls(True, 100_000)
        state = AutomationCapitalState(0, 0)
        plan = validate_engine_plan(controls, state, no_trade_plan())
        self.assertEqual(plan[0].action, DecisionAction.NO_TRADE)

    def test_partial_use_below_maximum_is_valid(self):
        controls = AutomationUserControls(True, 100_000)
        state = AutomationCapitalState(20_000, 0)
        plan = validate_engine_plan(
            controls,
            state,
            [EngineOrderIntent(DecisionAction.BUY, "005930", 30_000)],
        )
        self.assertEqual(len(plan), 1)

    def test_maximum_capital_is_absolute_ceiling(self):
        controls = AutomationUserControls(True, 100_000)
        state = AutomationCapitalState(70_000, 10_000, fees_tax_buffer_krw=2_000)
        with self.assertRaises(AutomationControlError):
            validate_engine_plan(
                controls,
                state,
                [EngineOrderIntent(DecisionAction.BUY, "005930", 20_000)],
            )

    def test_disabled_automation_blocks_new_exposure(self):
        controls = AutomationUserControls(False, 100_000)
        state = AutomationCapitalState(0, 0)
        with self.assertRaises(AutomationControlError):
            validate_engine_plan(
                controls,
                state,
                [EngineOrderIntent(DecisionAction.BUY, "005930", 10_000)],
            )

    def test_disabled_automation_allows_non_exposure_intent(self):
        controls = AutomationUserControls(False, 100_000)
        state = AutomationCapitalState(50_000, 0)
        plan = validate_engine_plan(
            controls,
            state,
            [EngineOrderIntent(DecisionAction.EXIT, "005930", 0)],
        )
        self.assertEqual(plan[0].action, DecisionAction.EXIT)

    def test_no_trade_cannot_commit_capital(self):
        with self.assertRaises(AutomationControlError):
            EngineOrderIntent(DecisionAction.NO_TRADE, projected_additional_committed_krw=1).validate()

    def test_negative_maximum_is_invalid(self):
        with self.assertRaises(AutomationControlError):
            AutomationUserControls(True, -1).validate()

    def test_uncertain_submission_reserve_counts_toward_ceiling(self):
        controls = AutomationUserControls(True, 100_000)
        state = AutomationCapitalState(60_000, 0, uncertain_submission_reserve_krw=30_000)
        with self.assertRaises(AutomationControlError):
            validate_engine_plan(
                controls,
                state,
                [EngineOrderIntent(DecisionAction.BUY, "000660", 20_000)],
            )


if __name__ == "__main__":
    unittest.main()
