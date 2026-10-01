"""Frozen KRX source-gate audit semantics for IndexAlert.

This module is source-governance infrastructure only. It does not evaluate
Alpha, performance, Final-Judge promotion or live-trading readiness.

The six source gates consolidate requirements that were already distributed
across the KRX source contract, status/investor-flow probes and Master Spec.
They must not be weakened to create feature availability or to consume the
sealed holdout.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


VALID_GATE_STATUSES = frozenset({"PASS", "PARTIAL", "BLOCKED"})

SOURCE_GATE_DEFINITIONS = {
    "A": {
        "name": "AUTHORIZED_OFFICIAL_ROUTE",
        "rule": (
            "The exact official KRX access route/product is identified and the "
            "dataset is accessed under the appropriate authorization. KRX OpenAPI "
            "AUTH_KEY, Data Marketplace web-session credentials and purchased/" 
            "distributed products must never be substituted for one another."
        ),
    },
    "B": {
        "name": "EXACT_DATASET_SCHEMA_MAPPING",
        "rule": (
            "The exact API service, screen/feed contract and required fields/schema "
            "are verified for the intended data family. A similarly named API or a "
            "provisional low-level transport does not close this gate."
        ),
    },
    "C": {
        "name": "HISTORICAL_COVERAGE_SECURITY_MAPPING",
        "rule": (
            "Historical coverage spans the requested research/Judge period and "
            "relevant securities, with stable security mapping and common-stock "
            "identity where required. A non-empty probe or a current snapshot is "
            "not evidence of complete historical coverage."
        ),
    },
    "D": {
        "name": "PIT_AVAILABILITY_LINEAGE",
        "rule": (
            "Point-in-time lineage is explicit: event_time, published_at when "
            "applicable, available_at and ingested_at are preserved, and no value "
            "is used before it was officially available. Final day-D investor flow "
            "is eligible only for the next decision after its official publication."
        ),
    },
    "E": {
        "name": "REPRODUCIBLE_INTEGRITY_FAIL_CLOSED",
        "rule": (
            "Retrieval and source metadata are reproducible/auditable, source and "
            "schema ambiguity fails closed, and undocumented proxy/synthetic "
            "substitution is forbidden. Source reachability alone is not enough."
        ),
    },
    "F": {
        "name": "INTENDED_USE_RIGHTS",
        "rule": (
            "Data-use/licensing rights are explicitly verified for the intended "
            "use scope. Internal research and future external/commercial product "
            "use are separate scopes and must not be conflated."
        ),
    },
}


@dataclass(frozen=True)
class SourceGateResult:
    gate: str
    name: str
    status: str
    evidence: str
    rule: str


def audit_source_gates(
    *,
    source_family: str,
    intended_use_scope: str,
    statuses: Mapping[str, str],
    evidence: Mapping[str, str],
) -> dict:
    """Return a strict A-F KRX source-contract audit.

    Every gate must be supplied explicitly. `PARTIAL` is intentionally not a
    pass. Even six PASS results are only source-contract evidence; they never
    authorize Alpha promotion, holdout consumption or live trading by themselves.
    """
    required = set(SOURCE_GATE_DEFINITIONS)
    status_keys = set(statuses)
    evidence_keys = set(evidence)
    if status_keys != required:
        raise ValueError(
            f"source-gate statuses must contain exactly A-F; got={sorted(status_keys)}"
        )
    if evidence_keys != required:
        raise ValueError(
            f"source-gate evidence must contain exactly A-F; got={sorted(evidence_keys)}"
        )
    if not str(source_family).strip():
        raise ValueError("source_family is required")
    if not str(intended_use_scope).strip():
        raise ValueError("intended_use_scope is required")

    results: dict[str, dict] = {}
    for gate in "ABCDEF":
        status = str(statuses[gate]).strip().upper()
        if status not in VALID_GATE_STATUSES:
            raise ValueError(
                f"invalid status for gate {gate}: {status!r}; "
                f"allowed={sorted(VALID_GATE_STATUSES)}"
            )
        note = str(evidence[gate]).strip()
        if not note:
            raise ValueError(f"gate {gate} requires non-empty evidence/justification")
        definition = SOURCE_GATE_DEFINITIONS[gate]
        result = SourceGateResult(
            gate=gate,
            name=definition["name"],
            status=status,
            evidence=note,
            rule=definition["rule"],
        )
        results[gate] = {
            "name": result.name,
            "status": result.status,
            "evidence": result.evidence,
            "rule": result.rule,
        }

    all_pass = all(results[g]["status"] == "PASS" for g in "ABCDEF")
    return {
        "contract": "INDEXALERT_KRX_SOURCE_GATES_A_TO_F",
        "source_family": str(source_family).strip(),
        "intended_use_scope": str(intended_use_scope).strip(),
        "gates": results,
        "all_source_gates_pass": all_pass,
        "source_contract_closed_for_declared_scope": all_pass,
        # Source governance can only unblock source use. It cannot promote a
        # model or authorize the sealed holdout/live execution by itself.
        "alpha_or_final_judge_promotion_authorized": False,
        "sealed_holdout_authorized_by_source_audit_alone": False,
        "live_trading_authorized_by_source_audit_alone": False,
        "guardrail": (
            "A-F are necessary source-governance gates for the declared scope, "
            "not Alpha evidence. Existing PIT, purged/WF/CPCV, cost, NetEV, tail, "
            "execution, holdout and prospective-promotion gates remain independent."
        ),
    }
