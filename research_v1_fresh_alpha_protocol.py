"""Fail-closed validator for the future-only H5 Fresh Alpha diagnostic.

Research-only integrity tooling. It cannot generate signals, submit orders, mutate
Champion/Core, admit Shadow S1/Fresh Confirmation S2, or grant promotion/live authority.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

PROTOCOL_PATH = Path("INDEXALERT_FRESH_ALPHA_PROSPECTIVE_PROTOCOL.json")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
FROZEN_ANCHOR_COMMIT = "5f19026e320ed8aec49f61b5273d03467d7437aa"
FROZEN_ANCHOR_COMMITTED_AT_UTC = "2026-10-06T22:54:26Z"
FROZEN_PROTOCOL_FIELDS = frozenset({
    "schema_version", "protocol_id", "classification", "freeze_anchor_commit",
    "eligible_chronology", "data_role", "horizon_sessions",
    "anchored_walk_forward_reference", "selection_policy", "no_trade_valid",
    "checkpoints_completed_krx_sessions", "historical_backfill_forbidden",
    "consumed_v1_holdout_forbidden", "parameter_retuning_within_protocol_forbidden",
    "formal_shadow_s1", "fresh_confirmation_s2", "promotion_authority",
    "live_order_authorized", "terminal_disposition", "freeze_anchor_committed_at_utc",
})


def _parse_aware(value: object) -> datetime:
    if type(value) is not str or not value or value != value.strip():
        raise ValueError("exact timezone-aware timestamp string required")
    text = value.replace("Z", "+00:00")
    moment = datetime.fromisoformat(text)
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise ValueError("timezone-aware timestamp required")
    return moment


def _unique_object(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate protocol JSON key")
        out[key] = value
    return out


def load_protocol(path: Path = PROTOCOL_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    validate_protocol(data)
    return data


def validate_protocol(p: dict) -> dict:
    blockers: list[str] = []
    if type(p) is not dict or set(p) != FROZEN_PROTOCOL_FIELDS:
        blockers.append("PROTOCOL_FIELDS_MISMATCH")
        if type(p) is not dict:
            return {
                "valid": False, "blockers": blockers, "formal_shadow_s1": False,
                "promotion_authority": False, "live_order_authorized": False,
            }
    if p.get("schema_version") != "1.0":
        blockers.append("SCHEMA_VERSION_MISMATCH")
    if p.get("protocol_id") != "IA-FRESH-ALPHA-H5-TOP3-20261007":
        blockers.append("PROTOCOL_ID_MISMATCH")
    if p.get("classification") != "FROZEN_PROSPECTIVE_DIAGNOSTIC_NOT_SHADOW_S1":
        blockers.append("CLASSIFICATION_MISMATCH")
    anchor_commit = p.get("freeze_anchor_commit")
    if type(anchor_commit) is not str or not HEX40.fullmatch(anchor_commit):
        blockers.append("INVALID_FREEZE_ANCHOR_COMMIT")
    elif anchor_commit != FROZEN_ANCHOR_COMMIT:
        blockers.append("FREEZE_ANCHOR_COMMIT_MISMATCH")
    anchor_time = p.get("freeze_anchor_committed_at_utc")
    try:
        _parse_aware(anchor_time)
    except (TypeError, ValueError):
        blockers.append("INVALID_FREEZE_ANCHOR_TIME")
    else:
        if anchor_time != FROZEN_ANCHOR_COMMITTED_AT_UTC:
            blockers.append("FREEZE_ANCHOR_TIME_MISMATCH")

    if p.get("eligible_chronology") != "decision_timestamp_strictly_after_freeze_anchor_commit":
        blockers.append("ELIGIBLE_CHRONOLOGY_MISMATCH")
    if p.get("data_role") != "FUTURE_PROSPECTIVE_DIAGNOSTIC_ONLY":
        blockers.append("DATA_ROLE_MISMATCH")
    if p.get("selection_policy") != "FROZEN_H5_0_TO_3_SELECTION_CONDITIONED_Q25_NORMAL_MARKET_STRICT_TOP3_NO_BACKFILL":
        blockers.append("SELECTION_POLICY_MISMATCH")

    if p.get("horizon_sessions") != 5:
        blockers.append("H5_REQUIRED")
    wf = p.get("anchored_walk_forward_reference")
    if type(wf) is not dict or wf != {
        "train_sessions": 504,
        "calibration_sessions": 126,
        "test_sessions": 126,
        "purge_sessions": 5,
        "embargo_sessions": 5,
    }:
        blockers.append("FROZEN_WF_REFERENCE_MISMATCH")
    if p.get("checkpoints_completed_krx_sessions") != [126, 504]:
        blockers.append("CHECKPOINTS_MISMATCH")

    required_true = (
        "no_trade_valid",
        "historical_backfill_forbidden",
        "consumed_v1_holdout_forbidden",
        "parameter_retuning_within_protocol_forbidden",
    )
    required_false = (
        "formal_shadow_s1",
        "fresh_confirmation_s2",
        "promotion_authority",
        "live_order_authorized",
    )
    for key in required_true:
        if p.get(key) is not True:
            blockers.append("REQUIRED_TRUE:" + key)
    for key in required_false:
        if p.get(key) is not False:
            blockers.append("REQUIRED_FALSE:" + key)
    if p.get("terminal_disposition") != "CONTINUE VALIDATION":
        blockers.append("TERMINAL_DISPOSITION_MISMATCH")

    return {
        "valid": not blockers,
        "blockers": blockers,
        "formal_shadow_s1": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }


def eligible_decision_timestamp(decision_timestamp: object, protocol: dict) -> bool:
    """Only timestamps strictly after the immutable freeze anchor are eligible."""
    validation = validate_protocol(protocol)
    if not validation["valid"]:
        return False
    try:
        decision = _parse_aware(decision_timestamp)
        anchor = _parse_aware(protocol["freeze_anchor_committed_at_utc"])
    except (TypeError, ValueError):
        return False
    return decision > anchor


if __name__ == "__main__":
    protocol = load_protocol()
    print(json.dumps(validate_protocol(protocol), sort_keys=True))
