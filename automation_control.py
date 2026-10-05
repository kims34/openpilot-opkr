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


@dataclass(frozen=True)
class CommittedCapital:
    """Conservative input snapshot; not broker reconciliation evidence."""
    positions_krw: int = 0
    reserved_buy_orders_krw: int = 0
    uncertain_submissions_krw: int = 0
    fee_buffer_krw: int = 0

    def total(self) -> int:
        amounts = (
            self.positions_krw, self.reserved_buy_orders_krw,
            self.uncertain_submissions_krw, self.fee_buffer_krw,
        )
        if any(type(value) is not int or value < 0 for value in amounts):
            raise AutomationControlError("committed capital must contain nonnegative integer amounts")
        return sum(amounts)


def _strict_bool(value: Any, field: str) -> bool:
    if type(value) is not bool:  # bool only; do not silently accept 0/1 or strings.
        raise AutomationControlError(f"{field} must be a boolean")
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
        automation_enabled=_strict_bool(payload["automation_enabled"], "automation_enabled"),
        max_automation_capital_krw=_positive_won(payload["max_automation_capital_krw"]),
    )


def validate_engine_plan(
    control: AutomationControl,
    orders: Sequence[PlannedOrder],
    *,
    decision: str,
    live_ordering_authorized: bool = False,
    committed_capital: CommittedCapital | None = None,
) -> dict[str, Any]:
    """Apply user authority and capital ceiling to an engine-generated plan.

    This is a structural pre-broker gate, not an order sender or admission adapter.
    Caller flags never grant LIVE authority. New exposure requires an explicit
    conservative capital snapshot including existing and uncertain commitments.
    """
    _strict_bool(live_ordering_authorized, "live_ordering_authorized")
    if not isinstance(control, AutomationControl):
        raise AutomationControlError("control must be a validated AutomationControl")
    _strict_bool(control.automation_enabled, "automation_enabled")
    if type(control.max_automation_capital_krw) is not int or control.max_automation_capital_krw <= 0:
        raise AutomationControlError("control capital ceiling must be a positive integer amount")
    if committed_capital is not None and not isinstance(committed_capital, CommittedCapital):
        raise AutomationControlError("committed_capital must be a CommittedCapital snapshot")
    committed = committed_capital.total() if committed_capital is not None else 0
    if isinstance(orders, (str, bytes)) or not isinstance(orders, Sequence):
        raise AutomationControlError("orders must be a sequence of PlannedOrder values")

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

    if committed_capital is None:
        raise AutomationControlError("TRADE requires an explicit committed capital snapshot")

    total = 0
    for order in orders:
        if not isinstance(order, PlannedOrder):
            raise AutomationControlError("orders must contain only PlannedOrder values")
        if not isinstance(order.side, str) or order.side.upper() != "BUY":
            raise AutomationControlError("current automated-entry contract supports BUY plans only")
        if not isinstance(order.symbol, str) or not order.symbol.strip():
            raise AutomationControlError("planned order symbol is required")
        if type(order.quantity) is not int or order.quantity <= 0:
            raise AutomationControlError("planned order quantity must be a positive integer")
        if type(order.estimated_notional_krw) is not int or order.estimated_notional_krw <= 0:
            raise AutomationControlError("estimated order notional must be a positive integer amount")
        total += order.estimated_notional_krw

    projected = committed + total
    if projected > control.max_automation_capital_krw:
        raise AutomationControlError(
            f"projected committed capital {projected} exceeds automation capital ceiling {control.max_automation_capital_krw}"
        )

    # Deliberately do not require total == ceiling. The remainder stays cash.
    return {
        "decision": "TRADE",
        "cash_allowed": True,
        "planned_notional_krw": total,
        "committed_capital_krw": committed,
        "projected_committed_capital_krw": projected,
        "uncommitted_cash_capacity_krw": control.max_automation_capital_krw - projected,
        "max_automation_capital_krw": control.max_automation_capital_krw,
        "live_ordering_authorized": False,
        "independent_gate_admission_verified": False,
    }
