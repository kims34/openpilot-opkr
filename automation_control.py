"""Fail-closed control plane for IndexAlert automated operation.

This module implements the frozen minimal-control UX contract without enabling
broker ordering. Users control only automated-operation ON/OFF and an absolute
maximum automation capital ceiling. Strategy/execution parameters remain engine
owned and are deliberately not accepted as user controls.

A positive capital ceiling is permission to use *up to* that amount, never an
instruction to invest it. NO_TRADE / 100% cash is always a valid engine result.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence


USER_CONTROL_KEYS = frozenset({"automation_enabled", "max_automation_capital_krw"})
FORBIDDEN_USER_TRADING_KEYS = frozenset({
    "stop_loss_pct",
    "take_profit_pct",
    "holding_period",
    "holding_count",
    "max_positions",
    "position_weight",
    "position_weights",
    "buy_weight",
    "sell_threshold",
    "entry_threshold",
    "top_k",
    "q25",
})


class AutomationControlError(ValueError):
    pass


@dataclass(frozen=True)
class AutomationControl:
    automation_enabled: bool
    max_automation_capital_krw: int


@dataclass(frozen=True)
class PlannedOrder:
    symbol: str
    side: str
    quantity: int
    estimated_notional_krw: int


def _strict_bool(value: Any) -> bool:
    if type(value) is not bool:  # bool only; do not silently accept 0/1 or strings.
        raise AutomationControlError("automation_enabled must be a boolean")
    return value


def _positive_won(value: Any) -> int:
    if isinstance(value, bool):
        raise AutomationControlError("max_automation_capital_krw must be a positive integer amount")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise AutomationControlError("invalid max_automation_capital_krw") from exc
    if not amount.is_finite() or amount <= 0 or amount != amount.to_integral_value():
        raise AutomationControlError("max_automation_capital_krw must be a positive integer amount")
    return int(amount)


def parse_user_control(payload: Mapping[str, Any]) -> AutomationControl:
    """Validate the complete user-facing automation control payload.

    Unknown keys fail closed so advanced strategy parameters cannot accidentally
    become user-tunable through an API/client update.
    """
    if not isinstance(payload, Mapping):
        raise AutomationControlError("automation control payload must be an object")
    keys = set(payload)
    forbidden = sorted(keys & FORBIDDEN_USER_TRADING_KEYS)
    if forbidden:
        raise AutomationControlError(
            "strategy/risk/execution parameters are engine-owned, not user controls: "
            + ", ".join(forbidden)
        )
    unknown = sorted(keys - USER_CONTROL_KEYS)
    if unknown:
        raise AutomationControlError("unsupported automation control keys: " + ", ".join(unknown))
    missing = sorted(USER_CONTROL_KEYS - keys)
    if missing:
        raise AutomationControlError("missing automation control keys: " + ", ".join(missing))
    return AutomationControl(
        automation_enabled=_strict_bool(payload["automation_enabled"]),
        max_automation_capital_krw=_positive_won(payload["max_automation_capital_krw"]),
    )


def validate_engine_plan(
    control: AutomationControl,
    orders: Sequence[PlannedOrder],
    *,
    decision: str,
    live_ordering_authorized: bool = False,
) -> dict[str, Any]:
    """Apply user authority and capital ceiling to an engine-generated plan.

    This is a pre-broker safety gate, not an order sender. LIVE ordering stays
    disabled unless a later staged-release gate explicitly supplies
    ``live_ordering_authorized=True`` after all research/operational controls
    have been satisfied.
    """
    normalized_decision = str(decision).strip().upper()
    if normalized_decision not in {"TRADE", "NO_TRADE"}:
        raise AutomationControlError("decision must be TRADE or NO_TRADE")
    if not control.automation_enabled:
        if orders:
            raise AutomationControlError("automation is disabled; order plan must be empty")
        return {
            "decision": "NO_TRADE",
            "cash_allowed": True,
            "planned_notional_krw": 0,
            "max_automation_capital_krw": control.max_automation_capital_krw,
            "live_ordering_authorized": False,
        }
    if normalized_decision == "NO_TRADE":
        if orders:
            raise AutomationControlError("NO_TRADE requires an empty order plan")
        return {
            "decision": "NO_TRADE",
            "cash_allowed": True,
            "planned_notional_krw": 0,
            "max_automation_capital_krw": control.max_automation_capital_krw,
            "live_ordering_authorized": False,
        }
    if not orders:
        raise AutomationControlError("TRADE requires at least one planned order")

    total = 0
    for order in orders:
        if str(order.side).upper() != "BUY":
            raise AutomationControlError("current automated-entry contract supports BUY plans only")
        if not str(order.symbol).strip():
            raise AutomationControlError("planned order symbol is required")
        if isinstance(order.quantity, bool) or int(order.quantity) != order.quantity or order.quantity <= 0:
            raise AutomationControlError("planned order quantity must be a positive integer")
        if (
            isinstance(order.estimated_notional_krw, bool)
            or int(order.estimated_notional_krw) != order.estimated_notional_krw
            or order.estimated_notional_krw <= 0
        ):
            raise AutomationControlError("estimated order notional must be a positive integer amount")
        total += int(order.estimated_notional_krw)

    if total > control.max_automation_capital_krw:
        raise AutomationControlError(
            f"planned notional {total} exceeds automation capital ceiling {control.max_automation_capital_krw}"
        )

    # Deliberately do not require total == ceiling. The remainder stays cash.
    return {
        "decision": "TRADE",
        "cash_allowed": True,
        "planned_notional_krw": total,
        "uncommitted_cash_capacity_krw": control.max_automation_capital_krw - total,
        "max_automation_capital_krw": control.max_automation_capital_krw,
        "live_ordering_authorized": bool(live_ordering_authorized),
    }
