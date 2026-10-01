"""Fail-closed audit for exact economics of KRX status-affected positions.

This module is deliberately stricter than a price-path backtest. Daily OHLC,
cleanup-trading windows, delisting dates, synthetic/modelled fills, Shadow
intentions and paper executions are not treated as exact realized economics.

For every position independently attested as affected by a halt, cleanup-trading
or delisting event, the affected quantity must be fully resolved by verified
broker fills and/or verified cash recovery evidence. Any unresolved quantity,
unsupported evidence source, missing PIT availability, or accounting mismatch
keeps Final-Judge exact status economics blocked.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation
from typing import Iterable

import pandas as pd


ALLOWED_EVENT_TYPES = frozenset({"HALT", "CLEANUP_TRADING", "DELISTING"})
ALLOWED_FILL_EVIDENCE = frozenset({
    "PROSPECTIVE_LIVE_EXECUTION_LOG",
    "BROKER_HISTORICAL_EXECUTION_RECORD",
})
ALLOWED_RECOVERY_EVIDENCE = frozenset({
    "OFFICIAL_KRX_RECOVERY_RECORD",
    "OFFICIAL_ISSUER_RECOVERY_RECORD",
    "BROKER_CASH_DISTRIBUTION_RECORD",
})
FORBIDDEN_EXACT_EVIDENCE = frozenset({
    "BACKTEST_GENERATED_FILL",
    "SYNTHETIC_FILL",
    "MODELLED_FILL",
    "MARKET_OPEN_ASSUMPTION",
    "PROSPECTIVE_SHADOW_DECISION_LOG",
    "PROSPECTIVE_PAPER_EXECUTION_LOG",
    "DAILY_OHLC",
    "MDCSTAT239_DAILY_PRICE_ONLY",
})


class KRXStatusEconomicsError(ValueError):
    """Raised when status-economics evidence is malformed or contradictory."""


@dataclass(frozen=True)
class StatusEconomicsAudit:
    expected_affected_positions: int
    observed_positions: int
    missing_position_evidence: int
    extra_position_evidence: int
    accounting_mismatch_positions: int
    unresolved_positions: int
    unsupported_fill_evidence_positions: int
    unsupported_recovery_evidence_positions: int
    pit_lineage_invalid_positions: int
    source_contract_mismatch_positions: int
    exact_status_economics_ready: bool
    judge_security_status_ready: bool
    feature_performance_testing_authorized: bool
    sealed_holdout_authorized: bool
    alpha_or_final_judge_promotion_authorized: bool
    live_trading_authorized: bool


def _require_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise KRXStatusEconomicsError(f"{label} missing required columns: {missing}")


def _text(value, field: str) -> str:
    text = str(value or "").strip()
    if not text:
        raise KRXStatusEconomicsError(f"{field} must be non-empty")
    return text


def _dec(value, field: str, *, allow_zero: bool = True) -> Decimal:
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise KRXStatusEconomicsError(f"{field} must be numeric") from exc
    if not d.is_finite():
        raise KRXStatusEconomicsError(f"{field} must be finite")
    if d < 0 or (not allow_zero and d == 0):
        relation = "non-negative" if allow_zero else "positive"
        raise KRXStatusEconomicsError(f"{field} must be {relation}")
    return d


def _aware(value, field: str) -> pd.Timestamp:
    try:
        ts = pd.Timestamp(value)
    except Exception as exc:
        raise KRXStatusEconomicsError(f"{field} is not a valid timestamp") from exc
    if pd.isna(ts) or ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXStatusEconomicsError(f"{field} must be timezone-aware")
    return ts


def _position_id(value) -> str:
    return _text(value, "position_id")


def _symbol(value) -> str:
    text = _text(value, "symbol").upper()
    return text.zfill(6) if text.isdigit() else text


def audit_exact_status_economics(
    *,
    expected_positions: pd.DataFrame,
    economics_evidence: pd.DataFrame,
    expected_scope_attested: bool,
) -> dict:
    """Audit exact economic closure for all independently expected affected positions.

    `expected_positions` must come from an independently audited join between
    candidate/position history and official status events. Passing
    `expected_scope_attested=False` always keeps exact economics blocked, even if
    the evidence table is empty or internally consistent.

    This audit computes realized proceeds/returns only from supplied verified
    evidence. It never creates a fill price, recovery value, tax, fee or missing
    observation.
    """
    if expected_positions is None or economics_evidence is None:
        raise KRXStatusEconomicsError("expected_positions and economics_evidence are required")

    _require_columns(
        expected_positions,
        [
            "position_id",
            "symbol",
            "event_type",
            "affected_qty",
            "entry_cost_basis_total",
            "source_contract_fingerprint",
        ],
        "expected_positions",
    )
    _require_columns(
        economics_evidence,
        [
            "position_id",
            "symbol",
            "event_type",
            "affected_qty",
            "verified_exit_fill_qty",
            "verified_exit_avg_price",
            "exit_fill_evidence_type",
            "exit_fill_evidence_ref",
            "verified_recovery_qty",
            "verified_recovery_cash_per_share",
            "recovery_evidence_type",
            "recovery_evidence_ref",
            "explicit_fees_taxes_total",
            "economic_available_at",
            "source_contract_fingerprint",
        ],
        "economics_evidence",
    )

    expected: dict[str, dict] = {}
    for row in expected_positions.itertuples(index=False):
        pid = _position_id(row.position_id)
        if pid in expected:
            raise KRXStatusEconomicsError(f"duplicate expected position_id: {pid}")
        event_type = _text(row.event_type, f"expected[{pid}].event_type").upper()
        if event_type not in ALLOWED_EVENT_TYPES:
            raise KRXStatusEconomicsError(f"unsupported event_type for {pid}: {event_type}")
        expected[pid] = {
            "symbol": _symbol(row.symbol),
            "event_type": event_type,
            "affected_qty": _dec(row.affected_qty, f"expected[{pid}].affected_qty", allow_zero=False),
            "entry_cost_basis_total": _dec(
                row.entry_cost_basis_total,
                f"expected[{pid}].entry_cost_basis_total",
                allow_zero=False,
            ),
            "source_contract_fingerprint": _text(
                row.source_contract_fingerprint,
                f"expected[{pid}].source_contract_fingerprint",
            ),
        }

    observed_rows: dict[str, object] = {}
    for row in economics_evidence.itertuples(index=False):
        pid = _position_id(row.position_id)
        if pid in observed_rows:
            raise KRXStatusEconomicsError(f"duplicate economics position_id: {pid}")
        observed_rows[pid] = row

    expected_ids = set(expected)
    observed_ids = set(observed_rows)
    missing_ids = sorted(expected_ids - observed_ids)
    extra_ids = sorted(observed_ids - expected_ids)

    accounting_mismatch: list[str] = []
    unresolved: list[str] = []
    unsupported_fill: list[str] = []
    unsupported_recovery: list[str] = []
    pit_invalid: list[str] = []
    contract_mismatch: list[str] = []
    resolved_economics: list[dict] = []

    for pid in sorted(expected_ids & observed_ids):
        exp = expected[pid]
        row = observed_rows[pid]
        symbol = _symbol(row.symbol)
        event_type = _text(row.event_type, f"evidence[{pid}].event_type").upper()
        evidence_qty = _dec(row.affected_qty, f"evidence[{pid}].affected_qty", allow_zero=False)
        fill_qty = _dec(row.verified_exit_fill_qty, f"evidence[{pid}].verified_exit_fill_qty")
        recovery_qty = _dec(row.verified_recovery_qty, f"evidence[{pid}].verified_recovery_qty")
        fees_taxes = _dec(row.explicit_fees_taxes_total, f"evidence[{pid}].explicit_fees_taxes_total")

        if (
            symbol != exp["symbol"]
            or event_type != exp["event_type"]
            or evidence_qty != exp["affected_qty"]
        ):
            accounting_mismatch.append(pid)
            continue

        resolved_qty = fill_qty + recovery_qty
        if resolved_qty != exp["affected_qty"]:
            accounting_mismatch.append(pid)
        if resolved_qty < exp["affected_qty"]:
            unresolved.append(pid)

        fill_cash = Decimal("0")
        if fill_qty > 0:
            fill_type = _text(row.exit_fill_evidence_type, f"evidence[{pid}].exit_fill_evidence_type").upper()
            fill_ref = _text(row.exit_fill_evidence_ref, f"evidence[{pid}].exit_fill_evidence_ref")
            fill_price = _dec(
                row.verified_exit_avg_price,
                f"evidence[{pid}].verified_exit_avg_price",
                allow_zero=False,
            )
            if fill_type in FORBIDDEN_EXACT_EVIDENCE or fill_type not in ALLOWED_FILL_EVIDENCE:
                unsupported_fill.append(pid)
            if not fill_ref:
                unsupported_fill.append(pid)
            fill_cash = fill_qty * fill_price
        else:
            # Zero-fill positions must not carry a fabricated positive price.
            zero_fill_price = _dec(
                row.verified_exit_avg_price,
                f"evidence[{pid}].verified_exit_avg_price",
            )
            if zero_fill_price != 0:
                accounting_mismatch.append(pid)

        recovery_cash = Decimal("0")
        if recovery_qty > 0:
            recovery_type = _text(
                row.recovery_evidence_type,
                f"evidence[{pid}].recovery_evidence_type",
            ).upper()
            recovery_ref = _text(
                row.recovery_evidence_ref,
                f"evidence[{pid}].recovery_evidence_ref",
            )
            recovery_per_share = _dec(
                row.verified_recovery_cash_per_share,
                f"evidence[{pid}].verified_recovery_cash_per_share",
            )
            if (
                recovery_type in FORBIDDEN_EXACT_EVIDENCE
                or recovery_type not in ALLOWED_RECOVERY_EVIDENCE
            ):
                unsupported_recovery.append(pid)
            if not recovery_ref:
                unsupported_recovery.append(pid)
            recovery_cash = recovery_qty * recovery_per_share
        else:
            zero_recovery = _dec(
                row.verified_recovery_cash_per_share,
                f"evidence[{pid}].verified_recovery_cash_per_share",
            )
            if zero_recovery != 0:
                accounting_mismatch.append(pid)

        try:
            _aware(row.economic_available_at, f"evidence[{pid}].economic_available_at")
        except KRXStatusEconomicsError:
            pit_invalid.append(pid)

        evidence_contract = _text(
            row.source_contract_fingerprint,
            f"evidence[{pid}].source_contract_fingerprint",
        )
        if evidence_contract != exp["source_contract_fingerprint"]:
            contract_mismatch.append(pid)

        gross_exit_cash = fill_cash + recovery_cash
        net_exit_cash = gross_exit_cash - fees_taxes
        entry_cost = exp["entry_cost_basis_total"]
        exact_net_return = (net_exit_cash - entry_cost) / entry_cost
        resolved_economics.append({
            "position_id": pid,
            "symbol": symbol,
            "event_type": event_type,
            "affected_qty": str(exp["affected_qty"]),
            "verified_fill_cash": str(fill_cash),
            "verified_recovery_cash": str(recovery_cash),
            "explicit_fees_taxes_total": str(fees_taxes),
            "verified_net_exit_cash": str(net_exit_cash),
            "entry_cost_basis_total": str(entry_cost),
            "exact_net_return": str(exact_net_return),
        })

    def _unique(values: list[str]) -> list[str]:
        return sorted(set(values))

    accounting_mismatch = _unique(accounting_mismatch)
    unresolved = _unique(unresolved)
    unsupported_fill = _unique(unsupported_fill)
    unsupported_recovery = _unique(unsupported_recovery)
    pit_invalid = _unique(pit_invalid)
    contract_mismatch = _unique(contract_mismatch)

    exact_ready = bool(
        expected_scope_attested
        and not missing_ids
        and not extra_ids
        and not accounting_mismatch
        and not unresolved
        and not unsupported_fill
        and not unsupported_recovery
        and not pit_invalid
        and not contract_mismatch
    )

    audit = StatusEconomicsAudit(
        expected_affected_positions=len(expected_ids),
        observed_positions=len(observed_ids),
        missing_position_evidence=len(missing_ids),
        extra_position_evidence=len(extra_ids),
        accounting_mismatch_positions=len(accounting_mismatch),
        unresolved_positions=len(unresolved),
        unsupported_fill_evidence_positions=len(unsupported_fill),
        unsupported_recovery_evidence_positions=len(unsupported_recovery),
        pit_lineage_invalid_positions=len(pit_invalid),
        source_contract_mismatch_positions=len(contract_mismatch),
        exact_status_economics_ready=exact_ready,
        # Exact status economics is necessary but never sufficient for these.
        judge_security_status_ready=False,
        feature_performance_testing_authorized=False,
        sealed_holdout_authorized=False,
        alpha_or_final_judge_promotion_authorized=False,
        live_trading_authorized=False,
    )
    out = asdict(audit)
    out.update({
        "expected_scope_attested": bool(expected_scope_attested),
        "missing_position_ids_sample": missing_ids[:10],
        "extra_position_ids_sample": extra_ids[:10],
        "accounting_mismatch_position_ids_sample": accounting_mismatch[:10],
        "unresolved_position_ids_sample": unresolved[:10],
        "unsupported_fill_position_ids_sample": unsupported_fill[:10],
        "unsupported_recovery_position_ids_sample": unsupported_recovery[:10],
        "pit_invalid_position_ids_sample": pit_invalid[:10],
        "source_contract_mismatch_position_ids_sample": contract_mismatch[:10],
        "resolved_position_economics": resolved_economics,
        "guardrail": (
            "Exact status economics requires independently attested affected-position scope and full quantity closure with verified evidence. "
            "Daily OHLC, modelled/synthetic fills, Shadow/Paper evidence and unresolved quantities cannot close this gate. "
            "Even exact_status_economics_ready=true is only one Final-Judge input and grants no promotion, holdout or live authority."
        ),
    })
    return out
