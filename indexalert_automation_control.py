"""Broker-neutral control contract for future IndexAlert automated operation.

This module deliberately does *not* submit broker orders. It freezes the minimal
user-facing control surface and validates engine-generated plans against the
user's absolute automation-capital ceiling.

User controls are intentionally limited to:
- automation enabled/disabled
- maximum automated-operation capital in KRW

Selection, sizing below the ceiling, cash retention, holding period, exit,
replacement and re-entry remain engine-owned decisions subject to the frozen
Decision/Risk/Execution policies and promotion gates.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable


class AutomationControlError(ValueError):
    """Raised when an automation control or proposed engine plan is invalid."""


class DecisionAction(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    EXIT = "EXIT"
    REPLACE = "REPLACE"
    NO_TRADE = "NO_TRADE"


@dataclass(frozen=True)
class AutomationUserControls:
    """The complete default user-facing automated-operation parameter set."""

    automation_enabled: bool
    max_automation_capital_krw: int

    def validate(self) -> "AutomationUserControls":
        if not isinstance(self.automation_enabled, bool):
            raise AutomationControlError("automation_enabled must be bool")
        if isinstance(self.max_automation_capital_krw, bool) or not isinstance(
            self.max_automation_capital_krw, int
        ):
            raise AutomationControlError("max_automation_capital_krw must be an integer KRW amount")
        if self.max_automation_capital_krw < 0:
            raise AutomationControlError("max_automation_capital_krw cannot be negative")
        return self


@dataclass(frozen=True)
class EngineOrderIntent:
    """Broker-neutral order intent produced by the engine, not by the user."""

    action: DecisionAction
    symbol: str | None = None
    projected_additional_committed_krw: int = 0

    def validate(self) -> "EngineOrderIntent":
        if isinstance(self.projected_additional_committed_krw, bool) or not isinstance(
            self.projected_additional_committed_krw, int
        ):
            raise AutomationControlError("projected_additional_committed_krw must be integer KRW")
        if self.projected_additional_committed_krw < 0:
            raise AutomationControlError("projected additional committed capital cannot be negative")
        if self.action == DecisionAction.BUY and not (self.symbol or "").strip():
            raise AutomationControlError("BUY intent requires symbol")
        if self.action == DecisionAction.NO_TRADE and self.projected_additional_committed_krw != 0:
            raise AutomationControlError("NO_TRADE cannot add committed capital")
        return self


@dataclass(frozen=True)
class AutomationCapitalState:
    """Conservative broker-neutral capital accounting before a new order."""

    automated_positions_value_krw: int
    reserved_open_buy_orders_krw: int
    uncertain_submission_reserve_krw: int = 0
    fees_tax_buffer_krw: int = 0

    def committed_automation_capital_krw(self) -> int:
        values = (
            self.automated_positions_value_krw,
            self.reserved_open_buy_orders_krw,
            self.uncertain_submission_reserve_krw,
            self.fees_tax_buffer_krw,
        )
        if any(isinstance(v, bool) or not isinstance(v, int) for v in values):
            raise AutomationControlError("capital state values must be integer KRW")
        if any(v < 0 for v in values):
            raise AutomationControlError("capital state values cannot be negative")
        return sum(values)


def validate_engine_plan(
    controls: AutomationUserControls,
    capital_state: AutomationCapitalState,
    intents: Iterable[EngineOrderIntent],
) -> tuple[EngineOrderIntent, ...]:
    """Fail closed if a proposed engine plan violates user authority/capital ceiling.

    This function intentionally has no minimum-investment or utilization target.
    An empty plan or explicit NO_TRADE is always valid when no other rule is
    violated. The user maximum is a ceiling, never a target.
    """

    controls.validate()
    current_committed = capital_state.committed_automation_capital_krw()
    plan = tuple(intent.validate() for intent in intents)

    if not controls.automation_enabled:
        if any(intent.action in {DecisionAction.BUY, DecisionAction.REPLACE} for intent in plan):
            raise AutomationControlError("automation disabled: new exposure is forbidden")
        return plan

    additional = sum(intent.projected_additional_committed_krw for intent in plan)
    projected = current_committed + additional
    if projected > controls.max_automation_capital_krw:
        raise AutomationControlError(
            "projected committed automation capital exceeds user maximum: "
            f"{projected} > {controls.max_automation_capital_krw}"
        )
    return plan


def no_trade_plan() -> tuple[EngineOrderIntent, ...]:
    """Canonical valid plan when no candidate passes the engine's frozen gates."""

    return (EngineOrderIntent(action=DecisionAction.NO_TRADE),)
