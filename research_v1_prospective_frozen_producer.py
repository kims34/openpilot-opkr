"""Freeze-anchor-compatible H5 prospective producer schedule.

This module makes explicit the refit/block schedule that already existed in
research_v1_selected_calibration.py at freeze anchor
5f19026e320ed8aec49f61b5273d03467d7437aa.

It does not search a new model, read the consumed v1 holdout, score the current
session, admit Alpha evidence or authorize trading.  It only reconstructs the
pre-existing anchored expanding-WF fit/calibration block for a target session
and binds the resulting deterministic model bundle to that schedule.
"""
from __future__ import annotations

from datetime import date
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES
from research_v1_distributional_netev import _pipe
from research_v1_krx_private_store import validate_private_root
from research_v1_prospective_model_bundle import (
    ProspectiveModelBundleError,
    build_model_bundle,
    validate_model_bundle,
)
from research_v1_policy_aligned_calibration import _policy_aligned_residual_quantiles


CLASSIFICATION = "FROZEN_PRODUCER_BINDING_NOT_ADMITTED"
FREEZE_ANCHOR_COMMIT = "5f19026e320ed8aec49f61b5273d03467d7437aa"
FIT_CODE_PATH = "research_v1_policy_aligned_calibration.py"
CALIBRATION_SOURCE_ID = (
    "calibration_daily_top3_by_pred_mean_then_same_normal_market_veto_no_backfill"
)
REFIT_POLICY_ID = (
    "ANCHOR_EXPANDING_TRAIN_INITIAL504__CAL126__TEST126__"
    "PURGE5_BOTH_SIDES__POLICY_ALIGNED_CAL_TOP3_NORMAL_MARKET_VETO__"
    "REFIT_PER_TEST_BLOCK_v2"
)
INITIAL_TRAIN_SESSIONS = 504
CALIBRATION_SESSIONS = 126
TEST_SESSIONS = 126
PURGE_SESSIONS = 5
FROZEN_CALENDAR_ORIGIN_SESSION = "2015-07-10"
FROZEN_CALENDAR_REFERENCE_ACTION_ID = 36643183157
# Exact test-block starts emitted by the adopted policy-alignment Action.
# These are schedule identity, not performance metrics.
FROZEN_TEST_BLOCK_STARTS = {
    640: "2018-02-19",
    766: "2018-08-23",
    892: "2019-03-05",
    1018: "2019-09-03",
    1144: "2020-03-10",
    1270: "2020-09-09",
    1396: "2021-03-18",
    1522: "2021-09-15",
    1648: "2022-03-25",
    1774: "2022-09-27",
    1900: "2023-03-30",
    2026: "2023-10-05",
    2152: "2024-04-09",
    2278: "2024-10-18",
    2404: "2025-04-24",
    2530: "2025-11-03",
    2656: "2026-05-11",
}
FIRST_TEST_START_ORDINAL = (
    INITIAL_TRAIN_SESSIONS + CALIBRATION_SESSIONS + 2 * PURGE_SESSIONS
)
_BINDING_FIELDS = (
    "classification", "freeze_anchor_commit", "fit_code_path", "refit_policy_id",
    "target_session", "target_session_ordinal", "test_block_index",
    "test_block_start_ordinal", "test_block_end_ordinal_exclusive",
    "test_block_start_session", "target_ordinal_in_test_block",
    "calendar_origin_session", "calendar_reference_action_id",
    "calendar_milestones_verified_through_target",
    "session_calendar_prefix_sha256",
    "initial_train_sessions", "actual_train_sessions",
    "calibration_sessions", "test_sessions", "purge_sessions",
    "train_end_session", "calibration_start_session", "calibration_end_session",
    "training_input_sha256", "calibration_input_sha256", "model_bundle_sha256",
    "historical_backfill_forbidden", "consumed_v1_holdout_used",
    "current_session_features_consumed_for_fit",
    "current_or_test_outcomes_consumed_for_fit",
    "independent_model_admission_verified", "fresh_alpha_observation_admitted",
    "promotion_authority", "live_order_authorized",
)


class FrozenProspectiveProducerError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _canonical_session(value: Any, field: str) -> str:
    if isinstance(value, pd.Timestamp):
        if value.tzinfo is not None:
            raise FrozenProspectiveProducerError(f"{field} must be a naive market date")
        value = value.strftime("%Y-%m-%d")
    if type(value) is not str:
        raise FrozenProspectiveProducerError(f"{field} must be YYYY-MM-DD")
    text = value.strip()
    if text != value:
        raise FrozenProspectiveProducerError(f"{field} must be canonical")
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise FrozenProspectiveProducerError(f"{field} must be YYYY-MM-DD") from exc
    if parsed.isoformat() != text:
        raise FrozenProspectiveProducerError(f"{field} must be canonical YYYY-MM-DD")
    return text


def _session_calendar(values: Sequence[Any]) -> list[pd.Timestamp]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise FrozenProspectiveProducerError("session_calendar must be an ordered sequence")
    parsed = []
    for value in values:
        text = _canonical_session(value, "session_calendar item")
        parsed.append(pd.Timestamp(text))
    if len(parsed) != len(set(parsed)):
        raise FrozenProspectiveProducerError("session_calendar contains duplicate sessions")
    if parsed != sorted(parsed):
        raise FrozenProspectiveProducerError("session_calendar must be strictly increasing")
    if not parsed or parsed[0].strftime("%Y-%m-%d") != FROZEN_CALENDAR_ORIGIN_SESSION:
        raise FrozenProspectiveProducerError(
            "session_calendar must begin at frozen supervised calendar origin 2015-07-10"
        )
    for ordinal, expected in FROZEN_TEST_BLOCK_STARTS.items():
        if ordinal < len(parsed) and parsed[ordinal].strftime("%Y-%m-%d") != expected:
            raise FrozenProspectiveProducerError(
                f"session_calendar drift at frozen test-block ordinal {ordinal}"
            )
    return parsed


def resolve_anchored_schedule(
    session_calendar: Sequence[Any], *, target_session: str
) -> dict[str, Any]:
    """Reproduce exact block arithmetic on the freeze-anchor supervised-session calendar."""
    sessions = _session_calendar(session_calendar)
    target = pd.Timestamp(_canonical_session(target_session, "target_session"))
    try:
        target_ordinal = sessions.index(target)
    except ValueError as exc:
        raise FrozenProspectiveProducerError(
            "target_session is absent from session_calendar"
        ) from exc
    if target_ordinal < FIRST_TEST_START_ORDINAL:
        raise FrozenProspectiveProducerError(
            "target_session precedes first frozen anchored-WF test block"
        )
    prefix_dates = [
        d.strftime("%Y-%m-%d") for d in sessions[: target_ordinal + 1]
    ]
    prefix_sha256 = hashlib.sha256(_canonical(prefix_dates)).hexdigest()
    applicable_milestones = {
        ordinal: expected
        for ordinal, expected in FROZEN_TEST_BLOCK_STARTS.items()
        if ordinal <= target_ordinal
    }
    if not applicable_milestones:
        raise FrozenProspectiveProducerError(
            "target lacks frozen calendar reference milestone"
        )

    block_index = (target_ordinal - FIRST_TEST_START_ORDINAL) // TEST_SESSIONS
    test_start = FIRST_TEST_START_ORDINAL + block_index * TEST_SESSIONS
    test_end_exclusive = test_start + TEST_SESSIONS
    cal_end = test_start - PURGE_SESSIONS
    cal_start = cal_end - CALIBRATION_SESSIONS
    train_end = cal_start - PURGE_SESSIONS

    if train_end < INITIAL_TRAIN_SESSIONS:
        raise FrozenProspectiveProducerError("anchored schedule train boundary drift")
    train_dates = sessions[:train_end]
    cal_dates = sessions[cal_start:cal_end]
    if len(cal_dates) != CALIBRATION_SESSIONS:
        raise FrozenProspectiveProducerError("calibration block length mismatch")
    if not train_dates:
        raise FrozenProspectiveProducerError("empty training schedule")

    return {
        "target_session": target.strftime("%Y-%m-%d"),
        "target_session_ordinal": int(target_ordinal),
        "test_block_index": int(block_index),
        "test_block_start_ordinal": int(test_start),
        "test_block_end_ordinal_exclusive": int(test_end_exclusive),
        "test_block_start_session": sessions[test_start].strftime("%Y-%m-%d"),
        "target_ordinal_in_test_block": int(target_ordinal - test_start),
        "calendar_origin_session": FROZEN_CALENDAR_ORIGIN_SESSION,
        "calendar_reference_action_id": FROZEN_CALENDAR_REFERENCE_ACTION_ID,
        "calendar_milestones_verified_through_target": True,
        "session_calendar_prefix_sha256": prefix_sha256,
        "initial_train_sessions": INITIAL_TRAIN_SESSIONS,
        "actual_train_sessions": int(len(train_dates)),
        "calibration_sessions": CALIBRATION_SESSIONS,
        "test_sessions": TEST_SESSIONS,
        "purge_sessions": PURGE_SESSIONS,
        "train_dates": train_dates,
        "calibration_dates": cal_dates,
        "train_end_session": train_dates[-1].strftime("%Y-%m-%d"),
        "calibration_start_session": cal_dates[0].strftime("%Y-%m-%d"),
        "calibration_end_session": cal_dates[-1].strftime("%Y-%m-%d"),
    }


def _finite_float(value: Any, field: str) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise FrozenProspectiveProducerError(f"{field} must be finite numeric")
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise FrozenProspectiveProducerError(f"{field} must be finite numeric") from exc
    if not math.isfinite(out):
        raise FrozenProspectiveProducerError(f"{field} must be finite numeric")
    return out


def _hash_rows(frame: pd.DataFrame, *, include_prediction: bool = False) -> str:
    """Hash canonical sorted rows without materialising a Python record list.

    The emitted JSON byte stream is deliberately identical to the previous
    canonical list encoder. Streaming keeps the frozen identity stable while
    avoiding a second multi-million-row Python object graph during a real
    prospective refit.
    """
    columns = ["decision_date", "symbol", *CONTEXT_FEATURES, "fh_net_return"]
    if include_prediction:
        columns.append("pred_mean")
    work = frame.loc[:, columns].copy()
    work["decision_date"] = pd.to_datetime(
        work["decision_date"], errors="raise"
    ).dt.strftime("%Y-%m-%d")
    work["symbol"] = work["symbol"].astype(str)
    ordered = work.sort_values(
        ["decision_date", "symbol"], kind="mergesort"
    )
    digest = hashlib.sha256()
    digest.update(b"[")
    first = True
    for values in ordered.itertuples(index=False, name=None):
        clean = {}
        for key, value in zip(columns, values):
            if key in {"decision_date", "symbol"}:
                clean[key] = str(value)
            else:
                clean[key] = _finite_float(value, key)
        if not first:
            digest.update(b",")
        digest.update(_canonical(clean))
        first = False
    digest.update(b"]")
    return digest.hexdigest()


def _validate_supervised_frame(z: pd.DataFrame) -> pd.DataFrame:
    required = {
        "decision_date", "symbol", "fh_label_available", "fh_net_return",
        *CONTEXT_FEATURES,
    }
    if not isinstance(z, pd.DataFrame) or z.empty:
        raise FrozenProspectiveProducerError("nonempty supervised frame required")
    missing = sorted(required - set(z.columns))
    if missing:
        raise FrozenProspectiveProducerError(
            f"supervised frame missing columns: {missing}"
        )
    out = z.loc[:, [
        "decision_date", "symbol", "fh_label_available", "fh_net_return",
        *CONTEXT_FEATURES,
    ]].copy()
    dates = pd.to_datetime(out["decision_date"], errors="coerce")
    if dates.isna().any() or dates.dt.tz is not None:
        raise FrozenProspectiveProducerError("decision_date must be exact naive dates")
    out["decision_date"] = dates.dt.normalize()
    if not out["symbol"].map(
        lambda v: type(v) is str and bool(v) and v == v.strip()
    ).all():
        raise FrozenProspectiveProducerError("canonical original symbols required")
    if out.duplicated(["decision_date", "symbol"]).any():
        raise FrozenProspectiveProducerError("duplicate supervised security/session row")
    for column in CONTEXT_FEATURES:
        if out[column].map(lambda v: isinstance(v, (bool, np.bool_))).any():
            raise FrozenProspectiveProducerError(f"boolean feature: {column}")
        out[column] = pd.to_numeric(out[column], errors="coerce")
        if not np.isfinite(out[column].to_numpy(dtype=float)).all():
            raise FrozenProspectiveProducerError(f"nonfinite feature: {column}")
    return out


def fit_frozen_model_for_target(
    z: pd.DataFrame,
    *,
    session_calendar: Sequence[Any],
    target_session: str,
) -> dict[str, Any]:
    """Fit only the exact pre-existing train/cal block for one future target.

    Test/current-session rows and outcomes are never consumed for fitting.
    """
    schedule = resolve_anchored_schedule(
        session_calendar, target_session=target_session
    )
    frame = _validate_supervised_frame(z)
    train_dates = set(schedule["train_dates"])
    cal_dates = set(schedule["calibration_dates"])
    protected_start = pd.Timestamp(schedule["test_block_start_session"])

    observed_dates = set(frame["decision_date"].drop_duplicates())
    missing_train_dates = sorted(train_dates - observed_dates)
    missing_cal_dates = sorted(cal_dates - observed_dates)
    if missing_train_dates or missing_cal_dates:
        raise FrozenProspectiveProducerError(
            "scheduled train/calibration session coverage is incomplete"
        )
    train = frame[frame["decision_date"].isin(train_dates)].copy()
    cal = frame[frame["decision_date"].isin(cal_dates)].copy()
    if train.empty or cal.empty:
        raise FrozenProspectiveProducerError("scheduled train/calibration rows are missing")
    if (train["decision_date"] >= protected_start).any() or (
        cal["decision_date"] >= protected_start
    ).any():
        raise FrozenProspectiveProducerError("test/current rows entered fit boundary")

    train = train[train["fh_label_available"].map(lambda v: v is True or v == True)].copy()
    if train.empty:
        raise FrozenProspectiveProducerError("no label-available training rows")
    if set(train["decision_date"].drop_duplicates()) != train_dates:
        raise FrozenProspectiveProducerError(
            "training label availability does not cover every scheduled session"
        )
    train["fh_net_return"] = pd.to_numeric(train["fh_net_return"], errors="coerce")
    if train["fh_net_return"].isna().any() or not np.isfinite(
        train["fh_net_return"].to_numpy(dtype=float)
    ).all():
        raise FrozenProspectiveProducerError("training labels are nonfinite")

    model = _pipe(CONTEXT_FEATURES)
    model.fit(train[CONTEXT_FEATURES], train["fh_net_return"].astype(float))

    cal_for_hash = cal[
        cal["fh_label_available"].map(lambda v: v is True or v == True)
    ].copy()
    cal_for_hash["fh_net_return"] = pd.to_numeric(
        cal_for_hash["fh_net_return"], errors="coerce"
    )
    cal_for_hash = cal_for_hash[
        cal_for_hash["fh_net_return"].notna()
    ].copy()
    if set(cal_for_hash["decision_date"].drop_duplicates()) != cal_dates:
        raise FrozenProspectiveProducerError(
            "calibration label availability does not cover every scheduled session"
        )
    if cal_for_hash.empty or not np.isfinite(
        cal_for_hash["fh_net_return"].to_numpy(dtype=float)
    ).all():
        raise FrozenProspectiveProducerError("no finite calibration labels")
    cal_for_hash["pred_mean"] = model.predict(cal_for_hash[CONTEXT_FEATURES])
    quantiles, calibration_policy_diagnostics = _policy_aligned_residual_quantiles(
        cal_for_hash, top_k=3
    )
    if not quantiles:
        raise FrozenProspectiveProducerError(
            "policy-aligned selection-conditioned calibration failed"
        )
    if calibration_policy_diagnostics.get("backfill_allowed") is not False:
        raise FrozenProspectiveProducerError(
            "policy-aligned calibration illegally permits backfill"
        )
    if quantiles.get("__global__", {}).get("source") != CALIBRATION_SOURCE_ID:
        raise FrozenProspectiveProducerError(
            "policy-aligned calibration source identity mismatch"
        )

    train_sha = _hash_rows(train)
    cal_sha = _hash_rows(cal_for_hash, include_prediction=True)
    try:
        bundle = build_model_bundle(
            model,
            quantiles,
            training_input_sha256=train_sha,
            calibration_input_sha256=cal_sha,
            fit_code_commit=FREEZE_ANCHOR_COMMIT,
            fit_code_path=FIT_CODE_PATH,
            train_end_session=schedule["train_end_session"],
            calibration_start_session=schedule["calibration_start_session"],
            calibration_end_session=schedule["calibration_end_session"],
            refit_policy_id=REFIT_POLICY_ID,
            feature_columns=CONTEXT_FEATURES,
        )
    except ProspectiveModelBundleError as exc:
        raise FrozenProspectiveProducerError("model bundle extraction failed") from exc

    body = {
        "classification": CLASSIFICATION,
        "freeze_anchor_commit": FREEZE_ANCHOR_COMMIT,
        "fit_code_path": FIT_CODE_PATH,
        "refit_policy_id": REFIT_POLICY_ID,
        "target_session": schedule["target_session"],
        "target_session_ordinal": schedule["target_session_ordinal"],
        "test_block_index": schedule["test_block_index"],
        "test_block_start_ordinal": schedule["test_block_start_ordinal"],
        "test_block_end_ordinal_exclusive": schedule[
            "test_block_end_ordinal_exclusive"
        ],
        "test_block_start_session": schedule["test_block_start_session"],
        "target_ordinal_in_test_block": schedule["target_ordinal_in_test_block"],
        "calendar_origin_session": schedule["calendar_origin_session"],
        "calendar_reference_action_id": schedule["calendar_reference_action_id"],
        "calendar_milestones_verified_through_target": schedule[
            "calendar_milestones_verified_through_target"
        ],
        "session_calendar_prefix_sha256": schedule[
            "session_calendar_prefix_sha256"
        ],
        "initial_train_sessions": INITIAL_TRAIN_SESSIONS,
        "actual_train_sessions": schedule["actual_train_sessions"],
        "calibration_sessions": CALIBRATION_SESSIONS,
        "test_sessions": TEST_SESSIONS,
        "purge_sessions": PURGE_SESSIONS,
        "train_end_session": schedule["train_end_session"],
        "calibration_start_session": schedule["calibration_start_session"],
        "calibration_end_session": schedule["calibration_end_session"],
        "training_input_sha256": train_sha,
        "calibration_input_sha256": cal_sha,
        "model_bundle_sha256": bundle["model_bundle_sha256"],
        "historical_backfill_forbidden": True,
        "consumed_v1_holdout_used": False,
        "current_session_features_consumed_for_fit": False,
        "current_or_test_outcomes_consumed_for_fit": False,
        "independent_model_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }
    binding_sha = hashlib.sha256(_canonical(body)).hexdigest()
    binding = {**body, "producer_binding_sha256": binding_sha}
    return {"producer_binding": binding, "model_bundle": bundle}



def bind_prebuilt_model_for_target(
    model_bundle: Mapping[str, Any],
    *,
    session_calendar: Sequence[Any],
    target_session: str,
) -> dict[str, Any]:
    """Bind one already-built frozen model bundle to an exact target block.

    This path performs no fit and consumes no supervised outcomes.  It is for a
    model state that has already been reconstructed/verified elsewhere.  The
    bundle remains structural-only: independent model admission and every
    Alpha/promotion/live authority stay false.
    """
    schedule = resolve_anchored_schedule(
        session_calendar, target_session=target_session
    )
    try:
        validation = validate_model_bundle(model_bundle)
    except ProspectiveModelBundleError as exc:
        raise FrozenProspectiveProducerError(
            "invalid prebuilt model bundle"
        ) from exc

    if model_bundle.get("fit_code_commit") != FREEZE_ANCHOR_COMMIT:
        raise FrozenProspectiveProducerError(
            "prebuilt model bundle fit-code commit mismatch"
        )
    if model_bundle.get("fit_code_path") != FIT_CODE_PATH:
        raise FrozenProspectiveProducerError(
            "prebuilt model bundle fit-code path mismatch"
        )
    if model_bundle.get("refit_policy_id") != REFIT_POLICY_ID:
        raise FrozenProspectiveProducerError(
            "prebuilt model bundle refit-policy mismatch"
        )
    if (
        model_bundle.get("train_end_session") != schedule["train_end_session"]
        or model_bundle.get("calibration_start_session")
        != schedule["calibration_start_session"]
        or model_bundle.get("calibration_end_session")
        != schedule["calibration_end_session"]
    ):
        raise FrozenProspectiveProducerError(
            "prebuilt model bundle schedule does not match target block"
        )
    if (
        model_bundle.get("calibration_quantiles", {})
        .get("__global__", {})
        .get("source")
        != CALIBRATION_SOURCE_ID
    ):
        raise FrozenProspectiveProducerError(
            "prebuilt model bundle calibration population is not policy-aligned"
        )
    if validation.get("independent_model_admission_verified") is not False:
        raise FrozenProspectiveProducerError(
            "prebuilt model admission authority must remain false"
        )

    body = {
        "classification": CLASSIFICATION,
        "freeze_anchor_commit": FREEZE_ANCHOR_COMMIT,
        "fit_code_path": FIT_CODE_PATH,
        "refit_policy_id": REFIT_POLICY_ID,
        "target_session": schedule["target_session"],
        "target_session_ordinal": schedule["target_session_ordinal"],
        "test_block_index": schedule["test_block_index"],
        "test_block_start_ordinal": schedule["test_block_start_ordinal"],
        "test_block_end_ordinal_exclusive": schedule[
            "test_block_end_ordinal_exclusive"
        ],
        "test_block_start_session": schedule["test_block_start_session"],
        "target_ordinal_in_test_block": schedule["target_ordinal_in_test_block"],
        "calendar_origin_session": schedule["calendar_origin_session"],
        "calendar_reference_action_id": schedule["calendar_reference_action_id"],
        "calendar_milestones_verified_through_target": schedule[
            "calendar_milestones_verified_through_target"
        ],
        "session_calendar_prefix_sha256": schedule[
            "session_calendar_prefix_sha256"
        ],
        "initial_train_sessions": INITIAL_TRAIN_SESSIONS,
        "actual_train_sessions": schedule["actual_train_sessions"],
        "calibration_sessions": CALIBRATION_SESSIONS,
        "test_sessions": TEST_SESSIONS,
        "purge_sessions": PURGE_SESSIONS,
        "train_end_session": schedule["train_end_session"],
        "calibration_start_session": schedule["calibration_start_session"],
        "calibration_end_session": schedule["calibration_end_session"],
        "training_input_sha256": model_bundle["training_input_sha256"],
        "calibration_input_sha256": model_bundle["calibration_input_sha256"],
        "model_bundle_sha256": validation["model_bundle_sha256"],
        "historical_backfill_forbidden": True,
        "consumed_v1_holdout_used": False,
        "current_session_features_consumed_for_fit": False,
        "current_or_test_outcomes_consumed_for_fit": False,
        "independent_model_admission_verified": False,
        "fresh_alpha_observation_admitted": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }
    binding_sha = hashlib.sha256(_canonical(body)).hexdigest()
    binding = {**body, "producer_binding_sha256": binding_sha}
    validate_producer_binding(
        binding, model_bundle, target_session=schedule["target_session"]
    )
    return {"producer_binding": binding, "model_bundle": dict(model_bundle)}

def validate_producer_binding(
    binding: Mapping[str, Any],
    model_bundle: Mapping[str, Any],
    *,
    target_session: str | None = None,
) -> dict[str, Any]:
    if not isinstance(binding, Mapping):
        raise FrozenProspectiveProducerError("producer binding must be an object")
    expected = set(_BINDING_FIELDS) | {"producer_binding_sha256"}
    if set(binding) != expected:
        raise FrozenProspectiveProducerError("producer binding fields mismatch")
    if binding.get("classification") != CLASSIFICATION:
        raise FrozenProspectiveProducerError("producer classification mismatch")
    if binding.get("freeze_anchor_commit") != FREEZE_ANCHOR_COMMIT:
        raise FrozenProspectiveProducerError("freeze anchor mismatch")
    if binding.get("fit_code_path") != FIT_CODE_PATH:
        raise FrozenProspectiveProducerError("fit code path mismatch")
    if binding.get("refit_policy_id") != REFIT_POLICY_ID:
        raise FrozenProspectiveProducerError("refit policy mismatch")
    session = _canonical_session(binding.get("target_session"), "target_session")
    if binding.get("calendar_origin_session") != FROZEN_CALENDAR_ORIGIN_SESSION:
        raise FrozenProspectiveProducerError("frozen calendar origin mismatch")
    if binding.get("calendar_reference_action_id") != FROZEN_CALENDAR_REFERENCE_ACTION_ID:
        raise FrozenProspectiveProducerError("frozen calendar reference action mismatch")
    if binding.get("calendar_milestones_verified_through_target") is not True:
        raise FrozenProspectiveProducerError("frozen calendar milestones are not verified")
    calendar_sha = binding.get("session_calendar_prefix_sha256")
    if (
        type(calendar_sha) is not str or len(calendar_sha) != 64
        or any(c not in "0123456789abcdef" for c in calendar_sha)
    ):
        raise FrozenProspectiveProducerError("session calendar prefix fingerprint invalid")
    if target_session is not None and session != _canonical_session(
        target_session, "target_session"
    ):
        raise FrozenProspectiveProducerError("producer target-session mismatch")
    for field, exact in (
        ("initial_train_sessions", INITIAL_TRAIN_SESSIONS),
        ("calibration_sessions", CALIBRATION_SESSIONS),
        ("test_sessions", TEST_SESSIONS),
        ("purge_sessions", PURGE_SESSIONS),
    ):
        if type(binding.get(field)) is not int or binding[field] != exact:
            raise FrozenProspectiveProducerError(f"{field} mismatch")
    for field in (
        "target_session_ordinal", "test_block_index", "test_block_start_ordinal",
        "test_block_end_ordinal_exclusive", "target_ordinal_in_test_block",
        "actual_train_sessions",
    ):
        if type(binding.get(field)) is not int or binding[field] < 0:
            raise FrozenProspectiveProducerError(f"{field} invalid")
    if binding["actual_train_sessions"] < INITIAL_TRAIN_SESSIONS:
        raise FrozenProspectiveProducerError("actual_train_sessions below frozen minimum")
    if not 0 <= binding["target_ordinal_in_test_block"] < TEST_SESSIONS:
        raise FrozenProspectiveProducerError("target outside frozen test block")
    expected_start_ordinal = (
        FIRST_TEST_START_ORDINAL + binding["test_block_index"] * TEST_SESSIONS
    )
    if binding["test_block_start_ordinal"] != expected_start_ordinal:
        raise FrozenProspectiveProducerError("test block ordinal/refit index mismatch")
    if (
        binding["test_block_end_ordinal_exclusive"]
        != expected_start_ordinal + TEST_SESSIONS
    ):
        raise FrozenProspectiveProducerError("test block span mismatch")
    if (
        binding["target_session_ordinal"]
        != expected_start_ordinal + binding["target_ordinal_in_test_block"]
    ):
        raise FrozenProspectiveProducerError("target ordinal/test-block offset mismatch")
    if (
        binding["actual_train_sessions"]
        != INITIAL_TRAIN_SESSIONS + binding["test_block_index"] * TEST_SESSIONS
    ):
        raise FrozenProspectiveProducerError("expanding training span/refit index mismatch")
    frozen_start = FROZEN_TEST_BLOCK_STARTS.get(expected_start_ordinal)
    if (
        frozen_start is not None
        and binding.get("test_block_start_session") != frozen_start
    ):
        raise FrozenProspectiveProducerError(
            "test block start session disagrees with frozen reference action"
        )
    for field in (
        "test_block_start_session", "train_end_session",
        "calibration_start_session", "calibration_end_session",
    ):
        _canonical_session(binding.get(field), field)
    if not (
        binding["train_end_session"]
        < binding["calibration_start_session"]
        <= binding["calibration_end_session"]
        < binding["test_block_start_session"]
        <= session
    ):
        raise FrozenProspectiveProducerError("producer chronology mismatch")
    for field in (
        "training_input_sha256", "calibration_input_sha256",
        "model_bundle_sha256", "producer_binding_sha256",
    ):
        value = binding.get(field)
        if type(value) is not str or len(value) != 64 or any(
            c not in "0123456789abcdef" for c in value
        ):
            raise FrozenProspectiveProducerError(f"{field} invalid")

    try:
        model_validation = validate_model_bundle(model_bundle)
    except ProspectiveModelBundleError as exc:
        raise FrozenProspectiveProducerError("invalid bound model bundle") from exc
    if model_validation["model_bundle_sha256"] != binding["model_bundle_sha256"]:
        raise FrozenProspectiveProducerError("producer/model bundle fingerprint mismatch")
    if model_bundle.get("fit_code_commit") != FREEZE_ANCHOR_COMMIT:
        raise FrozenProspectiveProducerError("model bundle fit-code commit mismatch")
    if model_bundle.get("fit_code_path") != FIT_CODE_PATH:
        raise FrozenProspectiveProducerError("model bundle fit-code path mismatch")
    if model_bundle.get("refit_policy_id") != REFIT_POLICY_ID:
        raise FrozenProspectiveProducerError("model bundle refit-policy mismatch")
    if (
        model_bundle.get("calibration_quantiles", {})
        .get("__global__", {})
        .get("source")
        != CALIBRATION_SOURCE_ID
    ):
        raise FrozenProspectiveProducerError(
            "model bundle calibration population is not policy-aligned"
        )
    if model_bundle.get("training_input_sha256") != binding["training_input_sha256"]:
        raise FrozenProspectiveProducerError("training fingerprint mismatch")
    if model_bundle.get("calibration_input_sha256") != binding["calibration_input_sha256"]:
        raise FrozenProspectiveProducerError("calibration fingerprint mismatch")

    for field in (
        "historical_backfill_forbidden",
    ):
        if binding.get(field) is not True:
            raise FrozenProspectiveProducerError(f"{field} must remain exact true")
    for field in (
        "consumed_v1_holdout_used", "current_session_features_consumed_for_fit",
        "current_or_test_outcomes_consumed_for_fit",
        "independent_model_admission_verified", "fresh_alpha_observation_admitted",
        "promotion_authority", "live_order_authorized",
    ):
        if binding.get(field) is not False:
            raise FrozenProspectiveProducerError(f"{field} must remain exact false")

    body = {field: binding[field] for field in _BINDING_FIELDS}
    actual = hashlib.sha256(_canonical(body)).hexdigest()
    if binding["producer_binding_sha256"] != actual:
        raise FrozenProspectiveProducerError("producer binding fingerprint mismatch")
    return {
        "valid": True,
        "producer_binding_sha256": actual,
        "model_bundle_sha256": binding["model_bundle_sha256"],
        "target_session": session,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }


def store_producer_binding(
    binding: Mapping[str, Any],
    model_bundle: Mapping[str, Any],
    *,
    root: str,
    git_worktree: str,
) -> dict[str, Any]:
    validation = validate_producer_binding(binding, model_bundle)
    payload = _canonical(dict(binding))
    base = validate_private_root(root, git_worktree=git_worktree)
    target = base / f"producer-{binding['target_session']}.json"
    fd, name = tempfile.mkstemp(prefix=".producer-", dir=base)
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
                raise FrozenProspectiveProducerError(
                    "conflicting or tampered same-session producer binding"
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
        "producer_binding_sha256": validation["producer_binding_sha256"],
        "model_bundle_sha256": validation["model_bundle_sha256"],
        "created": created,
        "fresh_alpha_observation_admitted": False,
        "live_order_authorized": False,
    }
