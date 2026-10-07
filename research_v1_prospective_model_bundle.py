"""Deterministic identity bundle for the frozen H5 prospective scorer.

This module does not fit a production model, choose a refit cadence, admit a
source, create a trading decision, or authorize an order. It only converts an
already-fitted frozen Ridge pipeline plus calibration quantiles into an explicit
pickle-free state whose exact bytes can be fingerprinted and replayed later.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping, Sequence

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline

from research_v1_context import CONTEXT_FEATURES
from research_v1_krx_private_store import validate_private_root


SCHEMA_VERSION = "1"
CLASSIFICATION = "STRUCTURAL_MODEL_BUNDLE_NOT_ADMITTED"
FRESH_ALPHA_PROTOCOL_ID = "IA-FRESH-ALPHA-H5-TOP3-20261007"
DECISION_POLICY_ID = "INDEXALERT-H5-FROZEN-DECISION-v1"
SELECTION_POLICY_ID = (
    "FROZEN_H5_0_TO_3_SELECTION_CONDITIONED_Q25_NORMAL_MARKET_STRICT_TOP3_NO_BACKFILL"
)
MODEL_STATE_ID = "RIDGE_MEDIAN_STANDARDIZED_LINEAR_STATE_V1"
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_BUCKETS = ("__global__", "low", "mid", "high")
_BODY_FIELDS = (
    "schema_version", "classification", "fresh_alpha_protocol_id",
    "decision_policy_id", "selection_policy_id", "model_state_id",
    "feature_columns", "training_input_sha256", "calibration_input_sha256",
    "fit_code_commit", "fit_code_path", "train_end_session",
    "calibration_start_session", "calibration_end_session", "refit_policy_id",
    "horizon_sessions", "top_k", "train_sessions_reference",
    "calibration_sessions_reference", "purge_sessions", "embargo_sessions",
    "imputer_statistics", "scaler_mean", "scaler_scale", "ridge_coef",
    "ridge_intercept", "ridge_alpha", "calibration_quantiles",
    "model_identity_structurally_bound", "independent_model_admission_verified",
    "signal_generation_complete", "decision_recorded", "promotion_authority",
    "live_order_authorized",
)


class ProspectiveModelBundleError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _text(value: Any, field: str, *, max_len: int = 500) -> str:
    if type(value) is not str or not value or value != value.strip():
        raise ProspectiveModelBundleError(f"{field} must be a nonempty original string")
    if len(value) > max_len:
        raise ProspectiveModelBundleError(f"{field} is unexpectedly long")
    return value


def _digest(value: Any, field: str, pattern=HEX64) -> str:
    text = _text(value, field, max_len=64)
    if not pattern.fullmatch(text):
        raise ProspectiveModelBundleError(f"{field} must be canonical lowercase hex")
    return text


def _session(value: Any, field: str) -> str:
    text = _text(value, field, max_len=10)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise ProspectiveModelBundleError(f"{field} must be YYYY-MM-DD") from exc
    if parsed.isoformat() != text:
        raise ProspectiveModelBundleError(f"{field} must be canonical YYYY-MM-DD")
    return text


def _finite_list(values: Sequence[Any], field: str, expected: int) -> list[float]:
    if len(values) != expected:
        raise ProspectiveModelBundleError(f"{field} length mismatch")
    out = []
    for value in values:
        if isinstance(value, (bool, np.bool_)):
            raise ProspectiveModelBundleError(f"{field} contains boolean")
        try:
            x = float(value)
        except (TypeError, ValueError) as exc:
            raise ProspectiveModelBundleError(f"{field} must be numeric") from exc
        if not math.isfinite(x):
            raise ProspectiveModelBundleError(f"{field} must be finite")
        out.append(x)
    return out


def _quantiles(value: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    if not isinstance(value, Mapping) or "__global__" not in value:
        raise ProspectiveModelBundleError("calibration_quantiles require __global__")
    unknown = sorted(set(value) - set(_ALLOWED_BUCKETS))
    if unknown:
        raise ProspectiveModelBundleError(
            f"unsupported calibration quantile buckets: {unknown}"
        )
    out: dict[str, dict[str, Any]] = {}
    for bucket in _ALLOWED_BUCKETS:
        if bucket not in value:
            continue
        raw = value[bucket]
        if not isinstance(raw, Mapping):
            raise ProspectiveModelBundleError(f"quantile bucket {bucket} must be an object")
        row: dict[str, Any] = {}
        for key in ("low", "med", "high"):
            number = raw.get(key)
            if isinstance(number, (bool, np.bool_)):
                raise ProspectiveModelBundleError(f"{bucket}.{key} must be numeric")
            try:
                number = float(number)
            except (TypeError, ValueError) as exc:
                raise ProspectiveModelBundleError(f"{bucket}.{key} must be numeric") from exc
            if not math.isfinite(number):
                raise ProspectiveModelBundleError(f"{bucket}.{key} must be finite")
            row[key] = number
        n = raw.get("n")
        if type(n) is not int or n <= 0:
            raise ProspectiveModelBundleError(f"{bucket}.n must be a positive exact integer")
        row["n"] = n
        fallback = raw.get("fallback_global")
        if fallback is not None:
            if type(fallback) is not bool:
                raise ProspectiveModelBundleError(
                    f"{bucket}.fallback_global must be boolean when present"
                )
            row["fallback_global"] = fallback
        bucket_n = raw.get("bucket_n")
        if bucket_n is not None:
            if type(bucket_n) is not int or bucket_n < 0:
                raise ProspectiveModelBundleError(
                    f"{bucket}.bucket_n must be a nonnegative exact integer"
                )
            row["bucket_n"] = bucket_n
        source = raw.get("source")
        if source is not None:
            row["source"] = _text(source, f"{bucket}.source")
        out[bucket] = row
    return out


def build_model_bundle(
    model: Pipeline,
    calibration_quantiles: Mapping[str, Any],
    *,
    training_input_sha256: str,
    calibration_input_sha256: str,
    fit_code_commit: str,
    fit_code_path: str,
    train_end_session: str,
    calibration_start_session: str,
    calibration_end_session: str,
    refit_policy_id: str,
    feature_columns: Sequence[str] = CONTEXT_FEATURES,
) -> dict[str, Any]:
    """Extract the already-fitted scorer into deterministic, pickle-free state."""
    features = list(feature_columns)
    if features != list(CONTEXT_FEATURES):
        raise ProspectiveModelBundleError("feature_columns must equal frozen CONTEXT_FEATURES")
    if len(features) != len(set(features)) or any(type(x) is not str for x in features):
        raise ProspectiveModelBundleError("feature_columns must be unique original strings")
    if not isinstance(model, Pipeline):
        raise ProspectiveModelBundleError("fitted sklearn Pipeline required")
    if list(model.named_steps) != ["prep", "reg"]:
        raise ProspectiveModelBundleError("unexpected model pipeline steps")
    reg = model.named_steps["reg"]
    if not isinstance(reg, Ridge) or float(reg.alpha) != 1.0:
        raise ProspectiveModelBundleError("frozen Ridge(alpha=1.0) required")
    try:
        num = model.named_steps["prep"].named_transformers_["num"]
        imputer = num.named_steps["imputer"]
        scaler = num.named_steps["scaler"]
        imputer_stats = imputer.statistics_
        scaler_mean = scaler.mean_
        scaler_scale = scaler.scale_
        coef = reg.coef_
        intercept = reg.intercept_
    except (AttributeError, KeyError) as exc:
        raise ProspectiveModelBundleError("pipeline is not fitted frozen scorer state") from exc

    n = len(features)
    train_end = _session(train_end_session, "train_end_session")
    cal_start = _session(calibration_start_session, "calibration_start_session")
    cal_end = _session(calibration_end_session, "calibration_end_session")
    if not (train_end < cal_start <= cal_end):
        raise ProspectiveModelBundleError("training/calibration chronology is invalid")

    body = {
        "schema_version": SCHEMA_VERSION,
        "classification": CLASSIFICATION,
        "fresh_alpha_protocol_id": FRESH_ALPHA_PROTOCOL_ID,
        "decision_policy_id": DECISION_POLICY_ID,
        "selection_policy_id": SELECTION_POLICY_ID,
        "model_state_id": MODEL_STATE_ID,
        "feature_columns": features,
        "training_input_sha256": _digest(training_input_sha256, "training_input_sha256"),
        "calibration_input_sha256": _digest(
            calibration_input_sha256, "calibration_input_sha256"
        ),
        "fit_code_commit": _digest(fit_code_commit, "fit_code_commit", pattern=HEX40),
        "fit_code_path": _text(fit_code_path, "fit_code_path"),
        "train_end_session": train_end,
        "calibration_start_session": cal_start,
        "calibration_end_session": cal_end,
        "refit_policy_id": _text(refit_policy_id, "refit_policy_id"),
        "horizon_sessions": 5,
        "top_k": 3,
        "train_sessions_reference": 504,
        "calibration_sessions_reference": 126,
        "purge_sessions": 5,
        "embargo_sessions": 5,
        "imputer_statistics": _finite_list(imputer_stats, "imputer_statistics", n),
        "scaler_mean": _finite_list(scaler_mean, "scaler_mean", n),
        "scaler_scale": _finite_list(scaler_scale, "scaler_scale", n),
        "ridge_coef": _finite_list(np.ravel(coef), "ridge_coef", n),
        "ridge_intercept": _finite_list([intercept], "ridge_intercept", 1)[0],
        "ridge_alpha": 1.0,
        "calibration_quantiles": _quantiles(calibration_quantiles),
        "model_identity_structurally_bound": True,
        "independent_model_admission_verified": False,
        "signal_generation_complete": False,
        "decision_recorded": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }
    if any(scale <= 0 for scale in body["scaler_scale"]):
        raise ProspectiveModelBundleError("scaler_scale must be strictly positive")
    digest = hashlib.sha256(_canonical(body)).hexdigest()
    return {**body, "model_bundle_sha256": digest}


def validate_model_bundle(bundle: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(bundle, Mapping):
        raise ProspectiveModelBundleError("model bundle must be an object")
    expected = set(_BODY_FIELDS) | {"model_bundle_sha256"}
    if set(bundle) != expected:
        raise ProspectiveModelBundleError("model bundle fields mismatch")
    if bundle.get("schema_version") != SCHEMA_VERSION:
        raise ProspectiveModelBundleError("schema version mismatch")
    if bundle.get("classification") != CLASSIFICATION:
        raise ProspectiveModelBundleError("classification mismatch")
    if bundle.get("fresh_alpha_protocol_id") != FRESH_ALPHA_PROTOCOL_ID:
        raise ProspectiveModelBundleError("Fresh Alpha protocol mismatch")
    if bundle.get("decision_policy_id") != DECISION_POLICY_ID:
        raise ProspectiveModelBundleError("decision policy mismatch")
    if bundle.get("selection_policy_id") != SELECTION_POLICY_ID:
        raise ProspectiveModelBundleError("selection policy mismatch")
    if bundle.get("model_state_id") != MODEL_STATE_ID:
        raise ProspectiveModelBundleError("model state mismatch")
    if bundle.get("feature_columns") != list(CONTEXT_FEATURES):
        raise ProspectiveModelBundleError("feature schema mismatch")
    for field in (
        "training_input_sha256", "calibration_input_sha256", "model_bundle_sha256"
    ):
        _digest(bundle.get(field), field)
    _digest(bundle.get("fit_code_commit"), "fit_code_commit", pattern=HEX40)
    _text(bundle.get("fit_code_path"), "fit_code_path")
    _text(bundle.get("refit_policy_id"), "refit_policy_id")
    train_end = _session(bundle.get("train_end_session"), "train_end_session")
    cal_start = _session(
        bundle.get("calibration_start_session"), "calibration_start_session"
    )
    cal_end = _session(bundle.get("calibration_end_session"), "calibration_end_session")
    if not (train_end < cal_start <= cal_end):
        raise ProspectiveModelBundleError("training/calibration chronology is invalid")
    exact_numbers = {
        "horizon_sessions": 5, "top_k": 3, "train_sessions_reference": 504,
        "calibration_sessions_reference": 126, "purge_sessions": 5,
        "embargo_sessions": 5,
    }
    for field, expected_value in exact_numbers.items():
        if type(bundle.get(field)) is not int or bundle[field] != expected_value:
            raise ProspectiveModelBundleError(f"{field} mismatch")
    if type(bundle.get("ridge_alpha")) not in (int, float) or float(bundle["ridge_alpha"]) != 1.0:
        raise ProspectiveModelBundleError("ridge_alpha mismatch")
    n = len(CONTEXT_FEATURES)
    for field in ("imputer_statistics", "scaler_mean", "scaler_scale", "ridge_coef"):
        values = bundle.get(field)
        if not isinstance(values, list):
            raise ProspectiveModelBundleError(f"{field} must be a list")
        checked = _finite_list(values, field, n)
        if field == "scaler_scale" and any(x <= 0 for x in checked):
            raise ProspectiveModelBundleError("scaler_scale must be strictly positive")
    _finite_list([bundle.get("ridge_intercept")], "ridge_intercept", 1)
    _quantiles(bundle.get("calibration_quantiles"))

    if bundle.get("model_identity_structurally_bound") is not True:
        raise ProspectiveModelBundleError("structural model identity must be true")
    for field in (
        "independent_model_admission_verified", "signal_generation_complete",
        "decision_recorded", "promotion_authority", "live_order_authorized",
    ):
        if bundle.get(field) is not False:
            raise ProspectiveModelBundleError(f"{field} must remain exact false")

    body = {field: bundle[field] for field in _BODY_FIELDS}
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if bundle["model_bundle_sha256"] != actual:
        raise ProspectiveModelBundleError("model bundle fingerprint mismatch")
    return {
        "valid": True,
        "model_bundle_sha256": actual,
        "model_identity_structurally_bound": True,
        "independent_model_admission_verified": False,
        "signal_generation_complete": False,
        "decision_recorded": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }


def store_model_bundle(
    bundle: Mapping[str, Any], *, root: str, git_worktree: str
) -> dict[str, Any]:
    validation = validate_model_bundle(bundle)
    payload = _canonical(dict(bundle))
    base = validate_private_root(root, git_worktree=git_worktree)
    target = base / f"model-bundle-{validation['model_bundle_sha256']}.json"
    fd, name = tempfile.mkstemp(prefix=".model-bundle-", dir=base)
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
                raise ProspectiveModelBundleError("conflicting or tampered model bundle")
            created = False
        directory = os.open(base, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temp.unlink(missing_ok=True)
    return {
        "model_bundle_sha256": validation["model_bundle_sha256"],
        "created": created,
        "independent_model_admission_verified": False,
        "decision_recorded": False,
        "live_order_authorized": False,
    }
