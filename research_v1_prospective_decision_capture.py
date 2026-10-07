"""Prospective H5 scoring and append-only decision capture.

This is chronology-preserving capture infrastructure, not admitted Alpha evidence.
It consumes only one current-session input snapshot and one deterministic model
bundle. Source/model/chronology admission remain separate and false.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES
from research_v1_distributional_netev import freeze_original_topk
from research_v1_market_eligibility import veto_frozen_topk_nonstandard_market
from research_v1_prospective_inputs import (
    ProspectiveInputError,
    input_snapshot_sha256 as compute_input_snapshot_sha256,
)
from research_v1_prospective_frozen_producer import (
    FrozenProspectiveProducerError,
    validate_producer_binding,
)
from research_v1_prospective_model_bundle import (
    ProspectiveModelBundleError,
    validate_model_bundle,
)
from research_v1_krx_private_store import validate_private_root


CLASSIFICATION = "PROSPECTIVE_DECISION_CAPTURE_PENDING_INDEPENDENT_ADMISSION"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
_CAPTURE_FIELDS = (
    "classification", "session", "decision_at", "captured_at",
    "capture_lag_seconds", "input_snapshot_sha256", "model_bundle_sha256",
    "producer_binding_sha256", "producer_refit_policy_id",
    "producer_test_block_index", "producer_test_block_start_session",
    "decision_policy_id", "selection_policy_id", "fresh_alpha_protocol_id",
    "ranked_scores", "eligible_lower_bound_positive_count", "original_top3",
    "vetoed_top3", "selected_candidates", "decision_count",
    "candidate_no_trade_recorded", "market_eligibility_diagnostics",
    "structural_scoring_complete", "decision_recorded",
    "independent_source_admission_verified",
    "independent_model_admission_verified",
    "independent_chronology_admission_verified",
    "fresh_alpha_observation_admitted", "formal_shadow_s1",
    "fresh_confirmation_s2", "promotion_authority", "outcome_attached",
    "live_order_authorized",
)


class ProspectiveDecisionCaptureError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _aware(value: Any, field: str) -> pd.Timestamp:
    if not isinstance(value, (str, datetime, pd.Timestamp)) or pd.isna(value):
        raise ProspectiveDecisionCaptureError(
            f"{field} must be an explicit timezone-aware timestamp"
        )
    try:
        ts = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ProspectiveDecisionCaptureError(f"{field} is invalid") from exc
    if ts.tzinfo is None or ts.utcoffset() is None:
        raise ProspectiveDecisionCaptureError(
            f"{field} must be an explicit timezone-aware timestamp"
        )
    return ts.tz_convert("UTC")


def _digest(value: Any, field: str) -> str:
    if type(value) is not str or not HEX64.fullmatch(value):
        raise ProspectiveDecisionCaptureError(f"{field} must be lowercase SHA-256")
    return value


def _finite(value: Any, field: str) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise ProspectiveDecisionCaptureError(f"{field} must be finite numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ProspectiveDecisionCaptureError(f"{field} must be finite numeric") from exc
    if not math.isfinite(number):
        raise ProspectiveDecisionCaptureError(f"{field} must be finite numeric")
    return number


def _bucket(value: float) -> str:
    x = _finite(value, "vol20_rank")
    if x < 0.0 or x > 1.0:
        raise ProspectiveDecisionCaptureError("vol20_rank outside [0,1]")
    if x < 1.0 / 3.0:
        return "low"
    if x < 2.0 / 3.0:
        return "mid"
    return "high"


def _quantile(bundle: Mapping[str, Any], bucket: str, key: str) -> float:
    q = bundle["calibration_quantiles"]
    row = q.get(bucket, q["__global__"])
    return _finite(row[key], f"calibration_quantiles.{bucket}.{key}")


def _records(frame: pd.DataFrame, columns: list[str]) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    out = frame.loc[:, columns].copy()
    if "decision_date" in out:
        out["decision_date"] = pd.to_datetime(
            out["decision_date"], errors="raise"
        ).dt.strftime("%Y-%m-%d")
    records = []
    for row in out.to_dict("records"):
        clean = {}
        for key, value in row.items():
            if isinstance(value, (np.bool_,)):
                value = bool(value)
            elif isinstance(value, (np.integer,)):
                value = int(value)
            elif isinstance(value, (np.floating,)):
                value = float(value)
            if isinstance(value, float) and not math.isfinite(value):
                raise ProspectiveDecisionCaptureError(
                    f"nonfinite capture value in {key}"
                )
            clean[key] = value
        records.append(clean)
    return records


def build_decision_capture(
    snapshot: Mapping[str, Any],
    model_bundle: Mapping[str, Any],
    *,
    producer_binding: Mapping[str, Any],
    input_snapshot_sha256: str,
    captured_at: str,
) -> dict[str, Any]:
    """Score one current session and freeze the full structural policy output."""
    try:
        model_validation = validate_model_bundle(model_bundle)
    except ProspectiveModelBundleError as exc:
        raise ProspectiveDecisionCaptureError("invalid model bundle") from exc
    if snapshot.get("classification") != "INPUT_SNAPSHOT_ONLY_NOT_DECISION":
        raise ProspectiveDecisionCaptureError("current-session input snapshot required")
    for field in (
        "independent_source_admission_verified", "signal_generation_complete",
        "decision_recorded", "no_trade_recorded", "live_order_authorized",
    ):
        if snapshot.get(field) is not False:
            raise ProspectiveDecisionCaptureError(
                "input snapshot cannot carry admission/decision authority"
            )
    supplied_input_digest = _digest(input_snapshot_sha256, "input_snapshot_sha256")
    try:
        actual_input_digest = compute_input_snapshot_sha256(dict(snapshot))
    except ProspectiveInputError as exc:
        raise ProspectiveDecisionCaptureError("invalid input snapshot") from exc
    if supplied_input_digest != actual_input_digest:
        raise ProspectiveDecisionCaptureError("input snapshot fingerprint mismatch")

    decision_at = _aware(snapshot.get("decision_at"), "decision_at")
    capture_at = _aware(captured_at, "captured_at")
    if capture_at < decision_at:
        raise ProspectiveDecisionCaptureError("capture cannot precede decision timestamp")
    session = snapshot.get("session")
    if type(session) is not str:
        raise ProspectiveDecisionCaptureError("canonical session required")
    expected_session = decision_at.tz_convert("Asia/Seoul").strftime("%Y-%m-%d")
    if session != expected_session:
        raise ProspectiveDecisionCaptureError("decision timestamp/session mismatch")
    try:
        producer_validation = validate_producer_binding(
            producer_binding, model_bundle, target_session=session
        )
    except FrozenProspectiveProducerError as exc:
        raise ProspectiveDecisionCaptureError(
            "invalid frozen producer binding"
        ) from exc
    if snapshot.get("feature_columns") != list(CONTEXT_FEATURES):
        raise ProspectiveDecisionCaptureError("input feature schema mismatch")

    frame = snapshot.get("features")
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ProspectiveDecisionCaptureError("nonempty feature DataFrame required")
    required = {"decision_date", "symbol", *CONTEXT_FEATURES}
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ProspectiveDecisionCaptureError(f"feature rows missing columns: {missing}")
    x = frame.loc[:, ["decision_date", "symbol", *CONTEXT_FEATURES]].copy()
    dates = pd.to_datetime(x["decision_date"], errors="coerce")
    if dates.isna().any() or dates.dt.tz is not None:
        raise ProspectiveDecisionCaptureError("feature decision_date invalid")
    if not dates.dt.strftime("%Y-%m-%d").eq(session).all():
        raise ProspectiveDecisionCaptureError("feature session mismatch")
    if not x["symbol"].map(
        lambda value: type(value) is str and value and value == value.strip()
    ).all():
        raise ProspectiveDecisionCaptureError("canonical original symbol required")
    if x["symbol"].duplicated().any():
        raise ProspectiveDecisionCaptureError("duplicate current-session symbol")
    symbols = x["symbol"].tolist()
    if symbols != sorted(symbols):
        raise ProspectiveDecisionCaptureError(
            "input features must preserve canonical symbol sort for deterministic ties"
        )

    matrix = x[CONTEXT_FEATURES].copy()
    for column in CONTEXT_FEATURES:
        if matrix[column].map(lambda value: isinstance(value, (bool, np.bool_))).any():
            raise ProspectiveDecisionCaptureError(f"boolean feature: {column}")
        matrix[column] = pd.to_numeric(matrix[column], errors="coerce")
    if not np.isfinite(matrix.to_numpy(dtype=float)).all():
        raise ProspectiveDecisionCaptureError("nonfinite prospective feature")

    values = matrix.to_numpy(dtype=float)
    imputer = np.asarray(model_bundle["imputer_statistics"], dtype=float)
    mean = np.asarray(model_bundle["scaler_mean"], dtype=float)
    scale = np.asarray(model_bundle["scaler_scale"], dtype=float)
    coef = np.asarray(model_bundle["ridge_coef"], dtype=float)
    intercept = float(model_bundle["ridge_intercept"])
    values = np.where(np.isnan(values), imputer, values)
    scaled = (values - mean) / scale
    pred = scaled @ coef + intercept

    x["pred_mean"] = pred.astype(float)
    x["vol_bucket"] = [_bucket(v) for v in x["vol20_rank"]]
    x["netev_low"] = [
        float(p) + _quantile(model_bundle, b, "low")
        for p, b in zip(x["pred_mean"], x["vol_bucket"])
    ]
    x["netev_median"] = [
        float(p) + _quantile(model_bundle, b, "med")
        for p, b in zip(x["pred_mean"], x["vol_bucket"])
    ]
    x["netev_high"] = [
        float(p) + _quantile(model_bundle, b, "high")
        for p, b in zip(x["pred_mean"], x["vol_bucket"])
    ]
    x["score"] = x["netev_low"]
    ranked = x.sort_values(
        ["decision_date", "score", "symbol"], ascending=[True, False, True],
        kind="mergesort",
    ).copy()
    eligible = ranked[ranked["netev_low"] > 0].copy()
    frozen = freeze_original_topk(eligible, int(model_bundle["top_k"]))
    # freeze_original_topk follows the historical scorer. Canonical symbol order
    # above makes equal-score ties deterministic without changing the score rule.
    selected, vetoed, market_diag = veto_frozen_topk_nonstandard_market(frozen)

    score_cols = [
        "decision_date", "symbol", "pred_mean", "vol_bucket",
        "netev_low", "netev_median", "netev_high", "score",
    ]
    top_cols = score_cols + [
        "normal_market_eligible", "market_eligibility_reason",
        "market_eligibility_policy",
    ]
    frozen_tagged = pd.concat([selected, vetoed], ignore_index=True)
    if not frozen_tagged.empty:
        frozen_tagged = frozen_tagged.sort_values(
            ["score", "symbol"], ascending=[False, True], kind="mergesort"
        )

    body = {
        "classification": CLASSIFICATION,
        "session": session,
        "decision_at": decision_at.isoformat(),
        "captured_at": capture_at.isoformat(),
        "capture_lag_seconds": float((capture_at - decision_at).total_seconds()),
        "input_snapshot_sha256": supplied_input_digest,
        "model_bundle_sha256": model_validation["model_bundle_sha256"],
        "producer_binding_sha256": producer_validation["producer_binding_sha256"],
        "producer_refit_policy_id": producer_binding["refit_policy_id"],
        "producer_test_block_index": producer_binding["test_block_index"],
        "producer_test_block_start_session": producer_binding["test_block_start_session"],
        "decision_policy_id": model_bundle["decision_policy_id"],
        "selection_policy_id": model_bundle["selection_policy_id"],
        "fresh_alpha_protocol_id": model_bundle["fresh_alpha_protocol_id"],
        "ranked_scores": _records(ranked, score_cols),
        "eligible_lower_bound_positive_count": int(len(eligible)),
        "original_top3": _records(frozen_tagged, top_cols),
        "vetoed_top3": _records(vetoed, top_cols),
        "selected_candidates": _records(selected, top_cols),
        "decision_count": int(len(selected)),
        "candidate_no_trade_recorded": bool(selected.empty),
        "market_eligibility_diagnostics": market_diag,
        "structural_scoring_complete": True,
        "decision_recorded": True,
        "independent_source_admission_verified": False,
        "independent_model_admission_verified": False,
        "independent_chronology_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "formal_shadow_s1": False,
        "fresh_confirmation_s2": False,
        "promotion_authority": False,
        "outcome_attached": False,
        "live_order_authorized": False,
    }
    digest = hashlib.sha256(_canonical(body)).hexdigest()
    return {**body, "decision_capture_sha256": digest}


def validate_decision_capture(capture: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(capture, Mapping):
        raise ProspectiveDecisionCaptureError("decision capture must be an object")
    expected = set(_CAPTURE_FIELDS) | {"decision_capture_sha256"}
    if set(capture) != expected:
        raise ProspectiveDecisionCaptureError("decision capture fields mismatch")
    if capture.get("classification") != CLASSIFICATION:
        raise ProspectiveDecisionCaptureError("decision capture classification mismatch")
    _digest(capture.get("input_snapshot_sha256"), "input_snapshot_sha256")
    _digest(capture.get("model_bundle_sha256"), "model_bundle_sha256")
    _digest(capture.get("producer_binding_sha256"), "producer_binding_sha256")
    _digest(capture.get("decision_capture_sha256"), "decision_capture_sha256")
    if type(capture.get("producer_refit_policy_id")) is not str or not capture[
        "producer_refit_policy_id"
    ]:
        raise ProspectiveDecisionCaptureError("producer_refit_policy_id invalid")
    if type(capture.get("producer_test_block_index")) is not int or capture[
        "producer_test_block_index"
    ] < 0:
        raise ProspectiveDecisionCaptureError("producer_test_block_index invalid")
    producer_start = capture.get("producer_test_block_start_session")
    if type(producer_start) is not str:
        raise ProspectiveDecisionCaptureError("producer_test_block_start_session invalid")
    decision = _aware(capture.get("decision_at"), "decision_at")
    captured = _aware(capture.get("captured_at"), "captured_at")
    if captured < decision:
        raise ProspectiveDecisionCaptureError("capture cannot precede decision timestamp")
    lag = _finite(capture.get("capture_lag_seconds"), "capture_lag_seconds")
    if lag < 0 or abs(lag - (captured - decision).total_seconds()) > 1e-6:
        raise ProspectiveDecisionCaptureError("capture lag mismatch")
    if type(capture.get("session")) is not str:
        raise ProspectiveDecisionCaptureError("canonical session required")
    if capture["session"] != decision.tz_convert("Asia/Seoul").strftime("%Y-%m-%d"):
        raise ProspectiveDecisionCaptureError("decision session mismatch")
    try:
        start_day = pd.Timestamp(producer_start)
        session_day = pd.Timestamp(capture["session"])
    except (TypeError, ValueError) as exc:
        raise ProspectiveDecisionCaptureError(
            "producer/session date invalid"
        ) from exc
    if start_day.tzinfo is not None or session_day.tzinfo is not None or start_day > session_day:
        raise ProspectiveDecisionCaptureError("producer test block/session chronology invalid")
    if type(capture.get("decision_count")) is not int:
        raise ProspectiveDecisionCaptureError("decision_count must be exact integer")
    selected = capture.get("selected_candidates")
    original = capture.get("original_top3")
    vetoed = capture.get("vetoed_top3")
    ranked = capture.get("ranked_scores")
    for field, rows in (
        ("selected_candidates", selected), ("original_top3", original),
        ("vetoed_top3", vetoed), ("ranked_scores", ranked),
    ):
        if not isinstance(rows, list):
            raise ProspectiveDecisionCaptureError(f"{field} must be a list")
    if len(original) > 3 or len(selected) > 3:
        raise ProspectiveDecisionCaptureError("Top3 boundary exceeded")
    if capture["decision_count"] != len(selected):
        raise ProspectiveDecisionCaptureError("decision_count mismatch")
    if capture.get("candidate_no_trade_recorded") is not (len(selected) == 0):
        raise ProspectiveDecisionCaptureError("candidate NO_TRADE mismatch")
    if capture.get("structural_scoring_complete") is not True:
        raise ProspectiveDecisionCaptureError("structural scoring must be complete")
    if capture.get("decision_recorded") is not True:
        raise ProspectiveDecisionCaptureError("capture must record the produced decision")
    for field in (
        "independent_source_admission_verified",
        "independent_model_admission_verified",
        "independent_chronology_admission_verified",
        "fresh_alpha_observation_admitted", "formal_shadow_s1",
        "fresh_confirmation_s2", "promotion_authority", "outcome_attached",
        "live_order_authorized",
    ):
        if capture.get(field) is not False:
            raise ProspectiveDecisionCaptureError(f"{field} must remain exact false")
    body = {field: capture[field] for field in _CAPTURE_FIELDS}
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if capture["decision_capture_sha256"] != actual:
        raise ProspectiveDecisionCaptureError("decision capture fingerprint mismatch")
    return {
        "valid": True,
        "decision_capture_sha256": actual,
        "decision_recorded": True,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }


def store_decision_capture(
    capture: Mapping[str, Any], *, root: str, git_worktree: str
) -> dict[str, Any]:
    validation = validate_decision_capture(capture)
    payload = _canonical(dict(capture))
    base = validate_private_root(root, git_worktree=git_worktree)
    target = base / f"decision-{capture['session']}.json"
    fd, name = tempfile.mkstemp(prefix=".decision-", dir=base)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o600)
        try:
            os.link(temp, target)
            created = True
        except FileExistsError:
            if target.is_symlink() or target.read_bytes() != payload:
                raise ProspectiveDecisionCaptureError(
                    "conflicting or tampered same-session decision capture"
                )
            created = False
        directory = os.open(base, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temp.unlink(missing_ok=True)
    return {
        "decision_capture_sha256": validation["decision_capture_sha256"],
        "created": created,
        "decision_recorded": True,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }
