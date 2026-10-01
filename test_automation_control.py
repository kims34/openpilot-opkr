import unittest

from automation_control import (
    AutomationControl,
    AutomationControlError,
    PlannedOrder,
    parse_user_control,
    validate_engine_plan,
)


class AutomationControlTests(unittest.TestCase):
    def test_parse_accepts_only_minimal_user_controls(self):
        out = parse_user_control({
            "automation_enabled": True,
            "max_automation_capital_krw": 100_000,
        })
        self.assertEqual(out, AutomationControl(True, 100_000))

    def test_parse_rejects_strategy_parameter(self):
        with self.assertRaisesRegex(AutomationControlError, "engine-owned"):
            parse_user_control({
                "automation_enabled": True,
                "max_automation_capital_krw": 100_000,
                "q25": 0.1,
            })

    def test_parse_rejects_unknown_and_missing_keys(self):
        with self.assertRaisesRegex(AutomationControlError, "unsupported"):
            parse_user_control({
                "automation_enabled": True,
                "max_automation_capital_krw": 100_000,
                "foo": "bar",
            })
        with self.assertRaisesRegex(AutomationControlError, "missing"):
            parse_user_control({"automation_enabled": True})

    def test_automation_enabled_requires_literal_bool(self):
        for value in (1, 0, "true", "false", None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(AutomationControlError, "must be a boolean"):
                    parse_user_control({
                        "automation_enabled": value,
                        "max_automation_capital_krw": 100_000,
                    })

    def test_capital_ceiling_requires_positive_integral_amount(self):
        for value in (0, -1, True, 10.5, "nan", "inf", None):
            with self.subTest(value=value):
                with self.assertRaises(AutomationControlError):
                    parse_user_control({
                        "automation_enabled": True,
                        "max_automation_capital_krw": value,
                    })

    def test_disabled_automation_requires_empty_plan_and_forces_no_trade(self):
        control = AutomationControl(False, 100_000)
        out = validate_engine_plan(control, [], decision="TRADE")
        self.assertEqual(out["decision"], "NO_TRADE")
        self.assertTrue(out["cash_allowed"])
        self.assertEqual(out["planned_notional_krw"], 0)
        self.assertFalse(out["live_ordering_authorized"])

        with self.assertRaisesRegex(AutomationControlError, "disabled"):
            validate_engine_plan(
                control,
                [PlannedOrder("005930", "BUY", 1, 70_000)],
                decision="TRADE",
            )

    def test_no_trade_requires_empty_plan(self):
        control = AutomationControl(True, 100_000)
        out = validate_engine_plan(control, [], decision="NO_TRADE")
        self.assertEqual(out["decision"], "NO_TRADE")
        self.assertFalse(out["live_ordering_authorized"])
        with self.assertRaisesRegex(AutomationControlError, "NO_TRADE"):
            validate_engine_plan(
                control,
                [PlannedOrder("005930", "BUY", 1, 70_000)],
                decision="NO_TRADE",
            )

    def test_trade_requires_orders_and_buy_only(self):
        control = AutomationControl(True, 100_000)
        with self.assertRaisesRegex(AutomationControlError, "requires at least one"):
            validate_engine_plan(control, [], decision="TRADE")
        with self.assertRaisesRegex(AutomationControlError, "BUY plans only"):
            validate_engine_plan(
                control,
                [PlannedOrder("005930", "SELL", 1, 70_000)],
                decision="TRADE",
            )

    def test_plan_must_not_exceed_capital_ceiling(self):
        control = AutomationControl(True, 100_000)
        with self.assertRaisesRegex(AutomationControlError, "exceeds automation capital ceiling"):
            validate_engine_plan(
                control,
                [
                    PlannedOrder("005930", "BUY", 1, 70_000),
                    PlannedOrder("000660", "BUY", 1, 40_000),
                ],
                decision="TRADE",
            )

    def test_partial_capital_use_leaves_cash(self):
        control = AutomationControl(True, 100_000)
        out = validate_engine_plan(
            control,
            [PlannedOrder("005930", "BUY", 1, 70_000)],
            decision="TRADE",
        )
        self.assertEqual(out["planned_notional_krw"], 70_000)
        self.assertEqual(out["uncommitted_cash_capacity_krw"], 30_000)
        self.assertTrue(out["cash_allowed"])
        self.assertFalse(out["live_ordering_authorized"])

    def test_live_order_authority_requires_literal_bool(self):
        control = AutomationControl(True, 100_000)
        order = [PlannedOrder("005930", "BUY", 1, 70_000)]
        for value in (1, 0, "true", "false", None):
            with self.subTest(value=value):
                with self.assertRaisesRegex(AutomationControlError, "live_ordering_authorized must be a boolean"):
                    validate_engine_plan(
                        control,
                        order,
                        decision="TRADE",
                        live_ordering_authorized=value,
                    )

        out = validate_engine_plan(
            control,
            order,
            decision="TRADE",
            live_ordering_authorized=True,
        )
        self.assertTrue(out["live_ordering_authorized"])

    def test_orders_must_be_validated_planned_order_objects_with_strict_ints(self):
        control = AutomationControl(True, 100_000)
        with self.assertRaisesRegex(AutomationControlError, "sequence"):
            validate_engine_plan(control, "not-orders", decision="TRADE")
        with self.assertRaisesRegex(AutomationControlError, "PlannedOrder"):
            validate_engine_plan(control, [{"symbol": "005930"}], decision="TRADE")
        with self.assertRaisesRegex(AutomationControlError, "quantity"):
            validate_engine_plan(
                control,
                [PlannedOrder("005930", "BUY", 1.0, 70_000)],
                decision="TRADE",
            )
        with self.assertRaisesRegex(AutomationControlError, "notional"):
            validate_engine_plan(
                control,
                [PlannedOrder("005930", "BUY", 1, 70_000.0)],
                decision="TRADE",
            )


if __name__ == "__main__":
    unittest.main()
