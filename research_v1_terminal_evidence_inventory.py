"""Network-free schema audit for terminal-treatment evidence.

This module validates evidence shape only. It never infers a recovery value,
never performs network access, and never opens downstream research/live gates.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping

from research_v1_krx_economics_admission import KRXEconomicsAdmissionError

_ALLOWED_TREATMENTS = {
    "REALIZED_FILL",
    "CASH_RECOVERY",
    "STOCK_OR_EXCHANGE_RECOVERY",
    "ZERO_RECOVERY_PROVEN",
}


def audit_terminal_evidence_inventory(
    rows: Iterable[Mapping[str, Any]],
    *,
    expected_no_cleanup_episode_count: int = 56,
) -> dict[str, Any]:
    material = list(rows)
    if expected_no_cleanup_episode_count < 0:
        raise KRXEconomicsAdmissionError("expected episode count cannot be negative")

    seen: set[str] = set()
    valid = 0
    for row in material:
        key = str(row.get("episode_evidence_key") or "").strip()
        if not key:
            raise KRXEconomicsAdmissionError("missing episode evidence key")
        if key in seen:
            raise KRXEconomicsAdmissionError("duplicate episode evidence key")
        seen.add(key)

        treatment = str(row.get("terminal_treatment") or "").strip().upper()
        if treatment not in _ALLOWED_TREATMENTS:
            raise KRXEconomicsAdmissionError("unsupported terminal treatment")

        source_sha = str(row.get("source_artifact_sha256") or "").strip().lower()
        if len(source_sha) != 64 or any(c not in "0123456789abcdef" for c in source_sha):
            raise KRXEconomicsAdmissionError("invalid source artifact SHA-256")

        if row.get("pit_available_at") in (None, ""):
            raise KRXEconomicsAdmissionError("missing PIT availability timestamp")

        if treatment == "ZERO_RECOVERY_PROVEN" and row.get("amount") not in (0, 0.0, "0", "0.0"):
            raise KRXEconomicsAdmissionError("zero-recovery proof cannot carry nonzero amount")

        if treatment != "ZERO_RECOVERY_PROVEN" and row.get("amount") in (None, ""):
            raise KRXEconomicsAdmissionError("terminal treatment amount is missing")
        valid += 1

    unresolved = max(int(expected_no_cleanup_episode_count) - valid, 0)
    if valid > int(expected_no_cleanup_episode_count):
        raise KRXEconomicsAdmissionError("evidence rows exceed expected no-cleanup scope")

    return {
        "expected_no_cleanup_episode_count": int(expected_no_cleanup_episode_count),
        "valid_terminal_evidence_count": valid,
        "unresolved_terminal_evidence_count": unresolved,
        "terminal_evidence_inventory_complete": unresolved == 0,
        "exact_status_economics_ready": False,
        "sealed_holdout_authorized": False,
        "shadow_s1_authorized": False,
        "fresh_confirmation_s2_authorized": False,
        "live_trading_authorized": False,
        "security_identifiers_emitted": False,
    }
