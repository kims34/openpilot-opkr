"""Fail-closed *structural* KRX-vs-Kiwoom investor-flow parity comparison.

Inputs are already independently normalized KRX-venue, final day-D net-buy
values. Neither a parsed response nor a matching numeric value proves an
authentic contemporaneous release, a licence, PIT data admission or Alpha.

No data fetch, persistence, orders or exposure of source rows.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from decimal import Decimal, InvalidOperation
import re
from typing import Any

SOURCES = ("KIWOOM_KA10059", "KRX_DMP_MDCSTAT02303")
METRICS = frozenset(("FOREIGN_NET_BUY_VALUE", "INSTITUTION_NET_BUY_VALUE"))
SHA256 = re.compile(r"^[0-9a-f]{64}$")
ISIN = re.compile(r"^KR[0-9A-Z]{10}$")
REQUIRED = (
    "source", "isin", "symbol", "event_date", "venue", "market_scope",
    "measure", "amount_krw", "normalization_contract_sha256",
    "response_sha256",
)


class InvestorFlowParityError(ValueError):
    """Refuse ambiguous vendor units, securities, venues or source schemas."""


def _normalized_amount(value: Any) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, str, Decimal)):
        raise InvestorFlowParityError("normalized KRW amount must be exact integer")
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise InvestorFlowParityError("invalid amount_krw") from exc
    if not amount.is_finite() or amount != amount.to_integral_value():
        raise InvestorFlowParityError("normalized KRW amount must be exact integer")
    return amount


def _normalize(rows: Sequence[Mapping[str, Any]], source: str) -> dict:
    result = {}
    contracts = set()
    for index, row in enumerate(rows):
        if not isinstance(row, Mapping):
            raise InvestorFlowParityError(f"{source}: row {index} is not a mapping")
        missing = [key for key in REQUIRED if key not in row]
        if missing:
            raise InvestorFlowParityError(f"{source}: row {index} missing {missing}")
        if row["source"] != source:
            raise InvestorFlowParityError("source family mismatch")
        if row["venue"] != "KRX" or row["market_scope"] != "KRX_ONLY":
            raise InvestorFlowParityError("cannot compare broker NXT/SOR/combined to KRX-only")
        if not isinstance(row["measure"], str) or row["measure"] not in METRICS:
            raise InvestorFlowParityError("only foreign/aggregate institution net-buy value allowed")
        if not isinstance(row["isin"], str) or ISIN.fullmatch(row["isin"]) is None:
            raise InvestorFlowParityError("invalid historical ISIN format")
        if not isinstance(row["symbol"], str) or re.fullmatch(r"[0-9]{6}", row["symbol"]) is None:
            raise InvestorFlowParityError("invalid historical symbol format")
        try:
            event_date = date.fromisoformat(row["event_date"])
        except (TypeError, ValueError) as exc:
            raise InvestorFlowParityError("unparseable trade day") from exc
        if not isinstance(row["event_date"], str) or event_date.isoformat() != row["event_date"]:
            raise InvestorFlowParityError("noncanonical trade day")
        for field in ("normalization_contract_sha256", "response_sha256"):
            v = row[field]
            if not isinstance(v, str) or SHA256.fullmatch(v) is None:
                raise InvestorFlowParityError(f"{field} missing")
        contracts.add(row["normalization_contract_sha256"])
        # No category double counting: institution aggregate is already its
        # own measure, never a sum of orgn + subcategories.
        key = (row["isin"], row["symbol"], event_date, row["measure"])
        if key in result:
            raise InvestorFlowParityError("duplicate issuer/day/measure")
        result[key] = _normalized_amount(row["amount_krw"])
    if len(contracts) != 1:
        raise InvestorFlowParityError(f"{source}: mixed normalization contracts")
    return result


def audit_cross_source_parity(
    broker_rows: Sequence[Mapping[str, Any]] | None,
    krx_rows: Sequence[Mapping[str, Any]] | None,
) -> dict[str, Any]:
    """Compare the *same declared scope*; never drop mismatched/missing rows.

    Passing is only **numeric structural parity** conditional on unverified
    caller-supplied KRW conversion and final market status. Immutable raw
    originals/contract/vintage proof must be validated separately.
    """
    if not isinstance(broker_rows, (list, tuple)) or not broker_rows:
        raise InvestorFlowParityError("nonempty broker candidate rows required")
    if not isinstance(krx_rows, (list, tuple)) or not krx_rows:
        raise InvestorFlowParityError("nonempty official KRX candidate rows required")
    broker = _normalize(broker_rows, SOURCES[0])
    krx = _normalize(krx_rows, SOURCES[1])
    keys_b = set(broker)
    keys_k = set(krx)
    matched = keys_b & keys_k
    # No arbitrary materiality tolerance. Any difference is a discrepancy
    # requiring source review, not proof of which vendor is wrong.
    mismatches = sum(broker[key] != krx[key] for key in matched)
    only_b, only_k = len(keys_b - keys_k), len(keys_k - keys_b)
    exact = bool(matched) and mismatches == 0 and only_b == 0 and only_k == 0
    return {
        "source_pair": list(SOURCES),
        "broker_rows": len(broker),
        "krx_rows": len(krx),
        "matched_rows": len(matched),
        "broker_only_rows": only_b,
        "krx_only_rows": only_k,
        "numeric_mismatch_rows": mismatches,
        "declared_scope_exact_numeric_match": exact,
        "historical_units_independently_attested": False,
        "source_originals_authenticated": False,
        "original_as_published_pit_verified": False,
        "historical_issuer_universe_complete": False,
        "source_admitted": False,
        "performance_testing_authorized": False,
        "holdout_authorized": False,
        "ordering_enabled": False,
        "note": (
            "Exact figures are conditional on unverified self-declared KRW normalization. "
            "There is no KRX-NXT venue inference, no missing-to-zero imputation, "
            "no original release-time proof and no research approval."
        ),
    }
