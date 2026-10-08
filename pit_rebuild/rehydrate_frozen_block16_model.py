"""Reconstruct the frozen block-16 H5 model without test/current outcomes.

Inputs are only the already verified long-history source and verified frozen
supervised cache.  The model is fitted on the exact anchored expanding training
window and calibrated on the exact policy-aligned 126-session calibration
window that preceded the 2026-05-11 test block.

This module deliberately does not evaluate test performance, read the consumed
v1 holdout artifact, score the current session, admit Fresh Alpha evidence, or
authorize trading.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any, Mapping

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


LONG_HISTORY_DIR = "marcap_kospi_pit_long_verified_36643183157"
SUPERVISED_DIR = "supervised_frozen_verified_36643183157"
OUTPUT_DIR = "frozen_block16_model_verified_36643183157"
ATTEMPT_PARENT = "frozen_block16_model_rehydration_attempts"
LONG_HISTORY_VERIFICATION_SHA256 = "6271e44d298621bbf4ba467c29aacc8b0402f041b5e478dac516a3c31cb545fb"
SUPERVISED_VERIFICATION_SHA256 = "ba60a9e489c7a4d9c3d8b4975b21925d1cc72b53f61bf25aa5524f8bc02f3a59"
REFERENCE_FILE = "frozen_block16_reference_36643183157.json"

FROZEN_ACTION_ID = 36643183157
FROZEN_ARTIFACT_ID = 11067383547
FROZEN_ARTIFACT_DIGEST = (
    "sha256:c8dd6a016103cf33d9219622f416fda25715c1cac19b371714d9308f2cb2c26f"
)
FROZEN_ACTION_HEAD = "4df26b6f5d2d9e645cd2c0242c9ac8cefb747a9d"
FREEZE_ANCHOR_COMMIT = "5f19026e320ed8aec49f61b5273d03467d7437aa"
FIT_CODE_PATH = "research_v1_policy_aligned_calibration.py"
REFIT_POLICY_ID = (
    "ANCHOR_EXPANDING_TRAIN_INITIAL504__CAL126__TEST126__"
    "PURGE5_BOTH_SIDES__POLICY_ALIGNED_CAL_TOP3_NORMAL_MARKET_VETO__"
    "REFIT_PER_TEST_BLOCK_v2"
)

SCHEMA_VERSION = "1"
MODEL_CLASSIFICATION = "STRUCTURAL_MODEL_BUNDLE_NOT_ADMITTED"
FRESH_ALPHA_PROTOCOL_ID = "IA-FRESH-ALPHA-H5-TOP3-20261007"
DECISION_POLICY_ID = "INDEXALERT-H5-FROZEN-DECISION-v1"
SELECTION_POLICY_ID = (
    "FROZEN_H5_0_TO_3_SELECTION_CONDITIONED_Q25_NORMAL_MARKET_STRICT_TOP3_NO_BACKFILL"
)
MODEL_STATE_ID = "RIDGE_MEDIAN_STANDARDIZED_LINEAR_STATE_V1"
CALIBRATION_SOURCE_ID = (
    "calibration_daily_top3_by_pred_mean_then_same_normal_market_veto_no_backfill"
)
SELECTION_CALIBRATION_SOURCE_ID = "calibration_daily_top3_by_pred_mean"
PLATFORM_NUMERIC_MAX_ULP = 64
PLATFORM_NUMERIC_MAX_ABS_DIFF = 2e-15

FROZEN_SOURCE_ORIGIN = "2015-06-15"
FROZEN_SUPERVISED_ORIGIN = "2015-07-10"
BLOCK_INDEX = 16
BLOCK_START_ORDINAL = 2656
BLOCK_TEST_START = "2026-05-11"
TRAIN_END = "2025-10-17"
CAL_START = "2025-10-27"
CAL_END = "2026-04-29"
TRAIN_SESSIONS = 2520
CAL_SESSIONS = 126
PURGE_SESSIONS = 5
TEST_SESSIONS = 126
TOP_K = 3
HORIZON = 5
NORMAL_MARKET_THRESHOLD = 0.305

BASE_FEATURES = [
    "ret1", "ret5", "ret20", "vol20", "log_adv20",
    "ret5_rank", "ret20_rank", "vol20_rank", "adv20_rank",
]
CONTEXT_FEATURES = BASE_FEATURES + [
    "market_ret1_median", "market_ret5_median", "market_ret20_median",
    "breadth1", "breadth5", "dispersion20",
    "resid_ret1", "resid_ret5", "resid_ret20",
]
SOURCE_COLUMNS = [
    "decision_date", "symbol", "open", "high", "low", "close",
    "volume", "value", "krx_change_return",
]
FROZEN_SOURCE_FINGERPRINT = {
    "rows": 2512128,
    "symbols": 1089,
    "date_min": "2015-06-15",
    "date_max": "2026-09-23",
    "columns": SOURCE_COLUMNS,
    "hash_xor_u64": "17836462952802001740",
    "hash_sum_u64": "17879387804724068608",
}


class FrozenBlock16ModelError(RuntimeError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _float_ulp_distance(actual: float, expected: float) -> int:
    """Return same-sign IEEE-754 float64 ULP distance.

    Cross-sign values are never considered platform-equivalent here.
    """
    a = np.float64(actual)
    e = np.float64(expected)
    if not np.isfinite(a) or not np.isfinite(e):
        raise FrozenBlock16ModelError("nonfinite platform numeric comparison")
    if a == e:
        return 0
    ua = int(a.view(np.uint64))
    ue = int(e.view(np.uint64))
    if (ua >> 63) != (ue >> 63):
        return 2**63
    mask = 0x7FFFFFFFFFFFFFFF
    return abs((ua & mask) - (ue & mask))


def _quantile_platform_equivalence(
    actual: Any,
    expected: Any,
    *,
    field: str,
) -> dict[str, Any]:
    """Require exact structure and machine-scale float64 equivalence only.

    This is not a research tolerance.  Integer/string/bool structure must match
    exactly.  Only floating leaves produced by the same frozen computation may
    differ, and then by at most the fixed ULP and absolute machine-scale caps.
    """
    max_ulp = 0
    max_abs = 0.0
    float_leaves = 0

    def walk(a: Any, e: Any, path: str) -> None:
        nonlocal max_ulp, max_abs, float_leaves
        if isinstance(e, bool) or isinstance(a, bool):
            if type(a) is not bool or type(e) is not bool or a is not e:
                raise FrozenBlock16ModelError(
                    f"{field} structural mismatch at {path}: {a!r} != {e!r}"
                )
            return
        if isinstance(e, dict) or isinstance(a, dict):
            if not isinstance(a, dict) or not isinstance(e, dict) or set(a) != set(e):
                raise FrozenBlock16ModelError(
                    f"{field} mapping mismatch at {path}"
                )
            for key in sorted(e):
                walk(a[key], e[key], f"{path}.{key}")
            return
        if isinstance(e, list) or isinstance(a, list):
            if not isinstance(a, list) or not isinstance(e, list) or len(a) != len(e):
                raise FrozenBlock16ModelError(
                    f"{field} list mismatch at {path}"
                )
            for index, (av, ev) in enumerate(zip(a, e)):
                walk(av, ev, f"{path}[{index}]")
            return
        if isinstance(e, float) or isinstance(a, float):
            if isinstance(a, bool) or isinstance(e, bool):
                raise FrozenBlock16ModelError(
                    f"{field} boolean/float mismatch at {path}"
                )
            try:
                af = float(a)
                ef = float(e)
            except (TypeError, ValueError) as exc:
                raise FrozenBlock16ModelError(
                    f"{field} numeric type mismatch at {path}"
                ) from exc
            ulp = _float_ulp_distance(af, ef)
            abs_diff = abs(af - ef)
            if (
                ulp > PLATFORM_NUMERIC_MAX_ULP
                or abs_diff > PLATFORM_NUMERIC_MAX_ABS_DIFF
            ):
                raise FrozenBlock16ModelError(
                    f"{field} float drift at {path}: "
                    f"actual={af!r} expected={ef!r} ulp={ulp} abs={abs_diff!r}"
                )
            max_ulp = max(max_ulp, ulp)
            max_abs = max(max_abs, abs_diff)
            float_leaves += 1
            return
        if type(a) is not type(e) or a != e:
            raise FrozenBlock16ModelError(
                f"{field} structural mismatch at {path}: {a!r} != {e!r}"
            )

    walk(actual, expected, field)
    return {
        "equivalent": True,
        "max_ulp_distance": int(max_ulp),
        "max_abs_diff": float(max_abs),
        "float_leaf_count": int(float_leaves),
        "ulp_limit": int(PLATFORM_NUMERIC_MAX_ULP),
        "abs_diff_limit": float(PLATFORM_NUMERIC_MAX_ABS_DIFF),
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path, field: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise FrozenBlock16ModelError(f"{field} is missing or unsafe")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise FrozenBlock16ModelError(f"{field} is invalid JSON") from exc
    if not isinstance(value, dict):
        raise FrozenBlock16ModelError(f"{field} must be an object")
    return value


def _require_parent_verifications(root: Path) -> tuple[Path, Path, dict[str, Any]]:
    long_dir = root / LONG_HISTORY_DIR
    sup_dir = root / SUPERVISED_DIR
    long_record = _load_json(
        long_dir / "frozen_long_history_verification.json",
        "long-history verification",
    )
    sup_record = _load_json(
        sup_dir / "frozen_supervised_verification.json",
        "supervised verification",
    )
    if long_record.get("verification_sha256") != LONG_HISTORY_VERIFICATION_SHA256:
        raise FrozenBlock16ModelError("long-history parent verification drift")
    if sup_record.get("verification_sha256") != SUPERVISED_VERIFICATION_SHA256:
        raise FrozenBlock16ModelError("supervised parent verification drift")
    parquet = sup_dir / "supervised.parquet"
    if _sha256_file(parquet) != sup_record.get("supervised_parquet_sha256"):
        raise FrozenBlock16ModelError("supervised parquet changed after verification")
    return long_dir, sup_dir, sup_record


def _stream_source_identity(long_dir: Path) -> dict[str, Any]:
    """Recheck raw-source identity only; the WF calendar comes from supervised z."""
    total = 0
    symbols: set[str] = set()
    date_min = None
    date_max = None
    xor_value = np.uint64(0)
    sum_value = np.uint64(0)
    files = sorted(long_dir.glob("kospi-pit-*.parquet"))
    if not files:
        raise FrozenBlock16ModelError("verified long-history parquet files missing")
    for path in files:
        frame = pd.read_parquet(path, columns=SOURCE_COLUMNS)
        frame["decision_date"] = pd.to_datetime(frame["decision_date"], errors="raise")
        frame["symbol"] = frame["symbol"].astype(str)
        hashes = pd.util.hash_pandas_object(
            frame[SOURCE_COLUMNS], index=False
        ).to_numpy(dtype=np.uint64)
        if len(hashes):
            xor_value ^= np.bitwise_xor.reduce(hashes)
            sum_value = np.uint64(sum_value + hashes.sum(dtype=np.uint64))
        total += len(frame)
        symbols.update(frame["symbol"].unique().tolist())
        lo = frame["decision_date"].min()
        hi = frame["decision_date"].max()
        date_min = lo if date_min is None else min(date_min, lo)
        date_max = hi if date_max is None else max(date_max, hi)
        del frame, hashes
        gc.collect()
    actual = {
        "rows": int(total),
        "symbols": int(len(symbols)),
        "date_min": str(pd.Timestamp(date_min).date()),
        "date_max": str(pd.Timestamp(date_max).date()),
        "columns": SOURCE_COLUMNS,
        "hash_xor_u64": str(int(xor_value)),
        "hash_sum_u64": str(int(sum_value)),
    }
    if actual != FROZEN_SOURCE_FINGERPRINT:
        raise FrozenBlock16ModelError(
            "long-history source identity mismatch before model fit"
        )
    if actual["date_min"] != FROZEN_SOURCE_ORIGIN:
        raise FrozenBlock16ModelError("frozen source origin mismatch")
    return actual


def _supervised_session_calendar(sup_dir: Path) -> list[pd.Timestamp]:
    """Recover the exact calendar used by selected_calibration_walk_forward(z).

    The adopted Action schedules folds from z["decision_date"], not from the
    raw OHLC source.  Feature warm-up therefore makes the supervised calendar
    begin later than the raw source.
    """
    parquet = sup_dir / "supervised.parquet"
    if not parquet.is_file() or parquet.is_symlink():
        raise FrozenBlock16ModelError("verified supervised parquet missing")
    dates = pd.read_parquet(parquet, columns=["decision_date"])
    values = pd.to_datetime(dates["decision_date"], errors="raise")
    sessions = sorted(pd.Timestamp(x).normalize() for x in values.drop_duplicates())
    del dates, values
    gc.collect()
    if not sessions or sessions[0].strftime("%Y-%m-%d") != FROZEN_SUPERVISED_ORIGIN:
        raise FrozenBlock16ModelError("frozen supervised calendar origin mismatch")
    if len(sessions) <= BLOCK_START_ORDINAL:
        raise FrozenBlock16ModelError(
            "frozen supervised calendar is too short for block16"
        )
    if sessions[BLOCK_START_ORDINAL].strftime("%Y-%m-%d") != BLOCK_TEST_START:
        raise FrozenBlock16ModelError("block16 test-start supervised calendar drift")
    if sessions[TRAIN_SESSIONS - 1].strftime("%Y-%m-%d") != TRAIN_END:
        raise FrozenBlock16ModelError("block16 train-end supervised calendar drift")
    cal_start_ordinal = BLOCK_START_ORDINAL - PURGE_SESSIONS - CAL_SESSIONS
    cal_end_exclusive = BLOCK_START_ORDINAL - PURGE_SESSIONS
    if sessions[cal_start_ordinal].strftime("%Y-%m-%d") != CAL_START:
        raise FrozenBlock16ModelError("block16 calibration-start supervised drift")
    if sessions[cal_end_exclusive - 1].strftime("%Y-%m-%d") != CAL_END:
        raise FrozenBlock16ModelError("block16 calibration-end supervised drift")
    return sessions


def _load_economic_raw(
    long_dir: Path,
    *,
    exit_cutoff: pd.Timestamp,
) -> pd.DataFrame:
    cols = ["decision_date", "symbol", "open", "close", "krx_change_return"]
    parts = []
    for path in sorted(long_dir.glob("kospi-pit-*.parquet")):
        frame = pd.read_parquet(path, columns=cols)
        frame["decision_date"] = pd.to_datetime(frame["decision_date"], errors="raise")
        frame = frame[frame["decision_date"] <= exit_cutoff].copy()
        if not frame.empty:
            parts.append(frame)
    if not parts:
        raise FrozenBlock16ModelError("economic source is empty")
    raw = pd.concat(parts, ignore_index=True)
    raw["symbol"] = raw["symbol"].astype(str)
    raw = raw.sort_values(["symbol", "decision_date"]).reset_index(drop=True)
    gross = 1.0 + pd.to_numeric(raw["krx_change_return"], errors="coerce")
    gross = gross.where(gross > 0)
    raw["economic_close"] = gross.groupby(raw["symbol"], sort=False).cumprod()
    raw["economic_open"] = raw["economic_close"] * (
        pd.to_numeric(raw["open"], errors="coerce")
        / pd.to_numeric(raw["close"], errors="coerce")
    )
    return raw


def _add_context(frame: pd.DataFrame) -> pd.DataFrame:
    x = frame.copy()
    g = x.groupby("decision_date")
    x["market_ret1_median"] = g["ret1"].transform("median")
    x["market_ret5_median"] = g["ret5"].transform("median")
    x["market_ret20_median"] = g["ret20"].transform("median")
    x["breadth1"] = g["ret1"].transform(lambda s: float((s > 0).mean()))
    x["breadth5"] = g["ret5"].transform(lambda s: float((s > 0).mean()))
    x["dispersion20"] = g["ret20"].transform(lambda s: float(s.std(ddof=0)))
    x["resid_ret1"] = x["ret1"] - x["market_ret1_median"]
    x["resid_ret5"] = x["ret5"] - x["market_ret5_median"]
    x["resid_ret20"] = x["ret20"] - x["market_ret20_median"]
    return x


def _build_train_cal_frame(
    sup_dir: Path,
    long_dir: Path,
    sessions: list[pd.Timestamp],
) -> pd.DataFrame:
    cal_start_ordinal = BLOCK_START_ORDINAL - PURGE_SESSIONS - CAL_SESSIONS
    cal_end_exclusive = BLOCK_START_ORDINAL - PURGE_SESSIONS
    train_dates = set(sessions[:TRAIN_SESSIONS])
    cal_dates = set(sessions[cal_start_ordinal:cal_end_exclusive])
    wanted_dates = train_dates | cal_dates

    columns = [
        "decision_date", "symbol", *BASE_FEATURES, "rec_cost_return",
    ]
    frame = pd.read_parquet(sup_dir / "supervised.parquet", columns=columns)
    frame["decision_date"] = pd.to_datetime(frame["decision_date"], errors="raise")
    frame["symbol"] = frame["symbol"].astype(str)
    frame = frame[
        frame["decision_date"].isin(wanted_dates)
        & (pd.to_numeric(frame["adv20_rank"], errors="coerce") >= 0.20)
    ].copy()
    if frame.empty:
        raise FrozenBlock16ModelError("block16 supervised train/cal frame is empty")
    if set(frame["decision_date"].drop_duplicates()) != wanted_dates:
        raise FrozenBlock16ModelError("block16 train/cal decision-date coverage is incomplete")
    context = _add_context(frame)
    del frame
    gc.collect()

    exit_cutoff = sessions[BLOCK_START_ORDINAL - 1]
    economic = _load_economic_raw(long_dir, exit_cutoff=exit_cutoff)

    pair = pd.DataFrame({
        "decision_date": sessions[:-HORIZON],
        "entry_date": sessions[1:1 + len(sessions) - HORIZON],
        "exit_date": sessions[HORIZON:],
    })
    pair = pair[pair["decision_date"].isin(wanted_dates)].copy()
    z = context.merge(pair, on="decision_date", how="left", validate="many_to_one")
    del context, pair
    gc.collect()

    entry = economic[[
        "decision_date", "symbol", "open", "economic_open"
    ]].rename(columns={
        "decision_date": "entry_date",
        "open": "fh_entry_open",
        "economic_open": "fh_entry_economic_price",
    })
    exit_ = economic[[
        "decision_date", "symbol", "close", "economic_close"
    ]].rename(columns={
        "decision_date": "exit_date",
        "close": "fh_exit_close",
        "economic_close": "fh_exit_economic_price",
    })
    z = z.merge(entry, on=["entry_date", "symbol"], how="left", validate="many_to_one")
    z = z.merge(exit_, on=["exit_date", "symbol"], how="left", validate="many_to_one")
    del economic, entry, exit_
    gc.collect()

    z["fh_cost"] = pd.to_numeric(z["rec_cost_return"], errors="coerce")
    z["fh_raw_price_ratio_return"] = z["fh_exit_close"] / z["fh_entry_open"] - 1.0
    z["fh_gross_return"] = (
        z["fh_exit_economic_price"] / z["fh_entry_economic_price"] - 1.0
    )
    z["fh_net_return"] = z["fh_gross_return"] - z["fh_cost"]
    z["fh_label_available"] = z[[
        "fh_entry_economic_price", "fh_exit_economic_price", "fh_cost"
    ]].notna().all(axis=1)

    train = z[
        z["decision_date"].isin(train_dates)
        & z["fh_label_available"].astype(bool)
    ][["decision_date", "symbol", *CONTEXT_FEATURES, "fh_net_return"]].copy()
    cal = z[
        z["decision_date"].isin(cal_dates)
        & z["fh_label_available"].astype(bool)
    ][["decision_date", "symbol", *CONTEXT_FEATURES, "fh_net_return"]].copy()
    del z
    gc.collect()

    if set(train["decision_date"].drop_duplicates()) != train_dates:
        raise FrozenBlock16ModelError("training labels do not cover every frozen session")
    if set(cal["decision_date"].drop_duplicates()) != cal_dates:
        raise FrozenBlock16ModelError("calibration labels do not cover every frozen session")
    train["partition"] = "train"
    cal["partition"] = "cal"
    return pd.concat([train, cal], ignore_index=True)


def _pipe() -> Pipeline:
    prep = ColumnTransformer([
        ("num", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]), CONTEXT_FEATURES)
    ], remainder="drop")
    return Pipeline([("prep", prep), ("reg", Ridge(alpha=1.0))])


def _bucket(vol_rank: pd.Series) -> pd.Series:
    return pd.cut(
        vol_rank.astype(float),
        bins=[0.0, 1.0 / 3.0, 2.0 / 3.0, 1.0000001],
        labels=["low", "mid", "high"],
        include_lowest=True,
        right=False,
    ).astype(str)


def _bootstrap_q25(frame: pd.DataFrame, *, reps: int = 400) -> dict[str, Any]:
    work = frame[["decision_date", "residual"]].dropna().copy()
    days = list(work["decision_date"].drop_duplicates())
    by_day = {
        d: work.loc[work["decision_date"] == d, "residual"].to_numpy(dtype=float)
        for d in days
    }
    rng = np.random.default_rng(20260930)
    qs = []
    for _ in range(reps):
        sampled = rng.choice(days, size=len(days), replace=True)
        vals = np.concatenate([by_day[d] for d in sampled])
        qs.append(float(np.quantile(vals, 0.25)))
    p05 = float(np.quantile(qs, 0.05))
    p95 = float(np.quantile(qs, 0.95))
    return {
        "rows": int(len(work)),
        "days": int(len(days)),
        "q25": float(work["residual"].quantile(0.25)),
        "bootstrap_p05": p05,
        "bootstrap_p95": p95,
        "bootstrap_width_90": float(p95 - p05),
        "reps": int(reps),
        "cluster": "decision_date",
        "diagnostic_only": True,
    }


def _selection_conditioned_quantiles(cal: pd.DataFrame) -> dict[str, Any]:
    """Exact pre-veto calibration Top3 residual quantiles from the frozen Action."""
    c = cal[cal["pred_mean"].notna() & cal["fh_net_return"].notna()].copy()
    ranked = (
        c.sort_values(["decision_date", "pred_mean"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(TOP_K)
        .copy()
    )
    if ranked.empty:
        raise FrozenBlock16ModelError("empty selection-conditioned calibration")
    ranked["residual"] = (
        ranked["fh_net_return"].astype(float) - ranked["pred_mean"].astype(float)
    )
    ranked["vol_bucket"] = _bucket(ranked["vol20_rank"])
    global_q = {
        "low": float(ranked["residual"].quantile(0.25)),
        "med": float(ranked["residual"].quantile(0.50)),
        "high": float(ranked["residual"].quantile(0.75)),
        "n": int(len(ranked)),
        "source": SELECTION_CALIBRATION_SOURCE_ID,
        "q25_uncertainty": _bootstrap_q25(ranked),
    }
    out: dict[str, Any] = {"__global__": global_q}
    for name, group in ranked.groupby("vol_bucket"):
        if len(group) < 30:
            out[str(name)] = {
                **global_q,
                "fallback_global": True,
                "bucket_n": int(len(group)),
            }
        else:
            out[str(name)] = {
                "low": float(group["residual"].quantile(0.25)),
                "med": float(group["residual"].quantile(0.50)),
                "high": float(group["residual"].quantile(0.75)),
                "n": int(len(group)),
                "fallback_global": False,
                "source": SELECTION_CALIBRATION_SOURCE_ID,
                "q25_uncertainty": _bootstrap_q25(group),
            }
    return out


def _policy_aligned_quantiles(cal: pd.DataFrame) -> tuple[dict[str, Any], dict[str, Any]]:
    c = cal[cal["pred_mean"].notna() & cal["fh_net_return"].notna()].copy()
    frozen = (
        c.sort_values(["decision_date", "pred_mean"], ascending=[True, False])
        .groupby("decision_date", group_keys=False)
        .head(TOP_K)
        .copy()
    )
    ret = pd.to_numeric(frozen["ret1"], errors="coerce")
    missing = ret.isna()
    outside = ret.abs() > NORMAL_MARKET_THRESHOLD
    eligible_mask = ~(missing | outside.fillna(False))
    ranked = frozen[eligible_mask].copy()
    vetoed = frozen[~eligible_mask].copy()
    if ranked.empty:
        raise FrozenBlock16ModelError("all frozen calibration rows were vetoed")

    ranked["residual"] = (
        ranked["fh_net_return"].astype(float) - ranked["pred_mean"].astype(float)
    )
    ranked["vol_bucket"] = _bucket(ranked["vol20_rank"])
    global_q = {
        "low": float(ranked["residual"].quantile(0.25)),
        "med": float(ranked["residual"].quantile(0.50)),
        "high": float(ranked["residual"].quantile(0.75)),
        "n": int(len(ranked)),
        "source": CALIBRATION_SOURCE_ID,
        "q25_uncertainty": _bootstrap_q25(ranked),
    }
    out: dict[str, Any] = {"__global__": global_q}
    for name, group in ranked.groupby("vol_bucket"):
        if len(group) < 30:
            out[str(name)] = {
                **global_q,
                "fallback_global": True,
                "bucket_n": int(len(group)),
            }
        else:
            out[str(name)] = {
                "low": float(group["residual"].quantile(0.25)),
                "med": float(group["residual"].quantile(0.50)),
                "high": float(group["residual"].quantile(0.75)),
                "n": int(len(group)),
                "fallback_global": False,
                "source": CALIBRATION_SOURCE_ID,
                "q25_uncertainty": _bootstrap_q25(group),
            }
    diag = {
        "policy": "POST_RANK_HARD_VETO__BLOCKED_SLOT_STAYS_EMPTY",
        "rows_before": int(len(frozen)),
        "rows_after": int(len(ranked)),
        "vetoed_rows": int(len(vetoed)),
        "vetoed_dates": int(vetoed["decision_date"].nunique()) if len(vetoed) else 0,
        "vetoed_symbols": int(vetoed["symbol"].nunique()) if len(vetoed) else 0,
        "threshold_abs_return": NORMAL_MARKET_THRESHOLD,
        "backfill_allowed": False,
        "official_status_validated": False,
        "frozen_rows": int(len(frozen)),
        "policy_eligible_rows": int(len(ranked)),
        "quantile_levels": [0.25, 0.50, 0.75],
    }
    return out, diag


def _finite(value: Any, field: str) -> float:
    if isinstance(value, (bool, np.bool_)):
        raise FrozenBlock16ModelError(f"{field} must be finite numeric")
    number = float(value)
    if not math.isfinite(number):
        raise FrozenBlock16ModelError(f"{field} must be finite numeric")
    return number


def _hash_rows(frame: pd.DataFrame, *, include_prediction: bool = False) -> str:
    columns = ["decision_date", "symbol", *CONTEXT_FEATURES, "fh_net_return"]
    if include_prediction:
        columns.append("pred_mean")
    work = frame.loc[:, columns].copy()
    work["decision_date"] = pd.to_datetime(
        work["decision_date"], errors="raise"
    ).dt.strftime("%Y-%m-%d")
    work["symbol"] = work["symbol"].astype(str)
    ordered = work.sort_values(["decision_date", "symbol"], kind="mergesort")
    digest = hashlib.sha256()
    digest.update(b"[")
    first = True
    for values in ordered.itertuples(index=False, name=None):
        row = {}
        for key, value in zip(columns, values):
            row[key] = str(value) if key in {"decision_date", "symbol"} else _finite(value, key)
        if not first:
            digest.update(b",")
        digest.update(_canonical(row))
        first = False
    digest.update(b"]")
    return digest.hexdigest()


def _model_quantiles(full: Mapping[str, Any]) -> dict[str, Any]:
    out = {}
    for bucket in ("__global__", "low", "mid", "high"):
        raw = full[bucket]
        row = {
            "low": float(raw["low"]),
            "med": float(raw["med"]),
            "high": float(raw["high"]),
            "n": int(raw["n"]),
        }
        for key in ("fallback_global", "bucket_n", "source"):
            if key in raw:
                row[key] = raw[key]
        out[bucket] = row
    return out


def _build_model_bundle(
    model: Pipeline,
    quantiles: Mapping[str, Any],
    *,
    training_input_sha256: str,
    calibration_input_sha256: str,
) -> dict[str, Any]:
    num = model.named_steps["prep"].named_transformers_["num"]
    imputer = num.named_steps["imputer"]
    scaler = num.named_steps["scaler"]
    reg = model.named_steps["reg"]
    body = {
        "schema_version": SCHEMA_VERSION,
        "classification": MODEL_CLASSIFICATION,
        "fresh_alpha_protocol_id": FRESH_ALPHA_PROTOCOL_ID,
        "decision_policy_id": DECISION_POLICY_ID,
        "selection_policy_id": SELECTION_POLICY_ID,
        "model_state_id": MODEL_STATE_ID,
        "feature_columns": list(CONTEXT_FEATURES),
        "training_input_sha256": training_input_sha256,
        "calibration_input_sha256": calibration_input_sha256,
        "fit_code_commit": FREEZE_ANCHOR_COMMIT,
        "fit_code_path": FIT_CODE_PATH,
        "train_end_session": TRAIN_END,
        "calibration_start_session": CAL_START,
        "calibration_end_session": CAL_END,
        "refit_policy_id": REFIT_POLICY_ID,
        "horizon_sessions": 5,
        "top_k": 3,
        "train_sessions_reference": 504,
        "calibration_sessions_reference": 126,
        "purge_sessions": 5,
        "embargo_sessions": 5,
        "imputer_statistics": [float(x) for x in imputer.statistics_],
        "scaler_mean": [float(x) for x in scaler.mean_],
        "scaler_scale": [float(x) for x in scaler.scale_],
        "ridge_coef": [float(x) for x in np.ravel(reg.coef_)],
        "ridge_intercept": float(reg.intercept_),
        "ridge_alpha": 1.0,
        "calibration_quantiles": _model_quantiles(quantiles),
        "model_identity_structurally_bound": True,
        "independent_model_admission_verified": False,
        "signal_generation_complete": False,
        "decision_recorded": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }
    if len(body["ridge_coef"]) != len(CONTEXT_FEATURES):
        raise FrozenBlock16ModelError("ridge coefficient length mismatch")
    if any(x <= 0 or not math.isfinite(x) for x in body["scaler_scale"]):
        raise FrozenBlock16ModelError("invalid frozen scaler state")
    return {
        **body,
        "model_bundle_sha256": hashlib.sha256(_canonical(body)).hexdigest(),
    }


def _write_private_json(path: Path, value: Mapping[str, Any]) -> None:
    payload = _canonical(value) + b"\n"
    fd, name = tempfile.mkstemp(prefix=".model-", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def rehydrate(*, root: Path, code_root: Path) -> dict[str, Any]:
    root = root.resolve()
    reference = _load_json(code_root / REFERENCE_FILE, "block16 reference")
    if reference.get("frozen_action_id") != FROZEN_ACTION_ID:
        raise FrozenBlock16ModelError("block16 reference action mismatch")
    long_dir, sup_dir, sup_record = _require_parent_verifications(root)
    source_identity = _stream_source_identity(long_dir)
    sessions = _supervised_session_calendar(sup_dir)

    if reference.get("block_index") != BLOCK_INDEX:
        raise FrozenBlock16ModelError("block16 reference index mismatch")
    if reference.get("test_start") != BLOCK_TEST_START:
        raise FrozenBlock16ModelError("block16 test start reference mismatch")
    if reference.get("train_end") != TRAIN_END:
        raise FrozenBlock16ModelError("block16 train end reference mismatch")
    if reference.get("cal_start") != CAL_START or reference.get("cal_end") != CAL_END:
        raise FrozenBlock16ModelError("block16 calibration date reference mismatch")

    combined = _build_train_cal_frame(sup_dir, long_dir, sessions)
    train = combined[combined["partition"] == "train"].drop(columns=["partition"]).copy()
    cal = combined[combined["partition"] == "cal"].drop(columns=["partition"]).copy()
    del combined
    gc.collect()

    for column in CONTEXT_FEATURES + ["fh_net_return"]:
        values = pd.to_numeric(train[column], errors="coerce")
        if values.isna().any() or not np.isfinite(values.to_numpy(dtype=float)).all():
            raise FrozenBlock16ModelError(f"nonfinite training field: {column}")
        train[column] = values.astype(float)
        cvalues = pd.to_numeric(cal[column], errors="coerce")
        if cvalues.isna().any() or not np.isfinite(cvalues.to_numpy(dtype=float)).all():
            raise FrozenBlock16ModelError(f"nonfinite calibration field: {column}")
        cal[column] = cvalues.astype(float)

    model = _pipe()
    model.fit(train[CONTEXT_FEATURES], train["fh_net_return"])
    cal["pred_mean"] = model.predict(cal[CONTEXT_FEATURES])

    selection_quantiles = _selection_conditioned_quantiles(cal)
    quantiles, diagnostics = _policy_aligned_quantiles(cal)

    expected_selection_quantiles = reference[
        "selection_conditioned_residual_quantiles"
    ]
    expected_quantiles = reference["policy_aligned_residual_quantiles"]
    expected_diagnostics = reference["calibration_policy_diagnostics"]

    selection_equivalence = _quantile_platform_equivalence(
        selection_quantiles,
        expected_selection_quantiles,
        field="selection_conditioned_residual_quantiles",
    )
    policy_equivalence = _quantile_platform_equivalence(
        quantiles,
        expected_quantiles,
        field="policy_aligned_residual_quantiles",
    )
    if diagnostics != expected_diagnostics:
        raise FrozenBlock16ModelError(
            "block16 calibration-policy diagnostics do not match Action artifact: "
            + json.dumps(
                {
                    "actual": diagnostics,
                    "expected": expected_diagnostics,
                    "training_rows": int(len(train)),
                    "calibration_rows": int(len(cal)),
                },
                sort_keys=True,
                default=str,
            )
        )

    selection_exact = selection_quantiles == expected_selection_quantiles
    policy_exact = quantiles == expected_quantiles
    max_platform_ulp = max(
        selection_equivalence["max_ulp_distance"],
        policy_equivalence["max_ulp_distance"],
    )
    max_platform_abs = max(
        selection_equivalence["max_abs_diff"],
        policy_equivalence["max_abs_diff"],
    )

    train_sha = _hash_rows(train)
    cal_sha = _hash_rows(cal, include_prediction=True)
    # Calibration thresholds are canonical Action artifact values.  The fitted
    # mean model remains current-platform float64 state and is not independently
    # admitted; the verification record below makes that distinction explicit.
    canonical_quantiles = expected_quantiles
    bundle = _build_model_bundle(
        model, canonical_quantiles,
        training_input_sha256=train_sha,
        calibration_input_sha256=cal_sha,
    )

    out_dir = root / OUTPUT_DIR
    if out_dir.exists():
        raise FrozenBlock16ModelError(
            "block16 model output already exists; no overwrite is permitted"
        )
    attempts = root / ATTEMPT_PARENT
    attempts.mkdir(parents=True, exist_ok=True)
    attempt = Path(tempfile.mkdtemp(prefix="attempt-", dir=attempts))
    bundle_path = attempt / "model_bundle.json"
    _write_private_json(bundle_path, bundle)

    body = {
        "classification": "FROZEN_BLOCK16_MODEL_PLATFORM_EQUIVALENCE_VERIFIED_NOT_ADMITTED",
        "frozen_action_id": FROZEN_ACTION_ID,
        "frozen_artifact_id": FROZEN_ARTIFACT_ID,
        "frozen_artifact_digest": FROZEN_ARTIFACT_DIGEST,
        "frozen_action_head_sha": FROZEN_ACTION_HEAD,
        "long_history_verification_sha256": LONG_HISTORY_VERIFICATION_SHA256,
        "supervised_verification_sha256": SUPERVISED_VERIFICATION_SHA256,
        "source_fingerprint": source_identity,
        "block_index": BLOCK_INDEX,
        "test_start_ordinal": BLOCK_START_ORDINAL,
        "test_start": BLOCK_TEST_START,
        "train_end": TRAIN_END,
        "calibration_start": CAL_START,
        "calibration_end": CAL_END,
        "training_rows": int(len(train)),
        "calibration_rows": int(len(cal)),
        "training_input_sha256": train_sha,
        "calibration_input_sha256": cal_sha,
        "model_bundle_sha256": bundle["model_bundle_sha256"],
        "selection_conditioned_quantiles_exact_artifact_match": selection_exact,
        "selection_conditioned_quantiles_platform_equivalent": True,
        "policy_aligned_quantiles_exact_artifact_match": policy_exact,
        "policy_aligned_quantiles_platform_equivalent": True,
        "calibration_policy_diagnostics_exact_artifact_match": True,
        "platform_numeric_max_ulp_distance": int(max_platform_ulp),
        "platform_numeric_max_abs_diff": float(max_platform_abs),
        "platform_numeric_ulp_limit": int(PLATFORM_NUMERIC_MAX_ULP),
        "platform_numeric_abs_diff_limit": float(PLATFORM_NUMERIC_MAX_ABS_DIFF),
        "canonical_action_quantiles_used_for_bundle": True,
        "model_state_exact_action_coefficients_verified": False,
        "mean_model_state_recomputed_on_current_platform": True,
        "test_rows_consumed_for_fit": False,
        "test_outcomes_consumed_for_fit": False,
        "current_session_features_consumed_for_fit": False,
        "consumed_v1_holdout_artifact_read": False,
        "performance_evaluation_executed": False,
        "fresh_alpha_observation_admitted": False,
        "independent_model_admission_verified": False,
        "promotion_authority": False,
        "live_order_authorized": False,
    }
    verification = {
        **body,
        "verification_sha256": hashlib.sha256(_canonical(body)).hexdigest(),
    }
    _write_private_json(attempt / "verification.json", verification)
    os.rename(attempt, out_dir)
    parent_fd = os.open(root, os.O_RDONLY)
    try:
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)
    directory_fd = os.open(out_dir, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)

    return {
        "verified": True,
        "created": True,
        "final_dir": str(out_dir),
        "verification_sha256": verification["verification_sha256"],
        "model_bundle_sha256": bundle["model_bundle_sha256"],
        "training_rows": int(len(train)),
        "calibration_rows": int(len(cal)),
        "selection_conditioned_quantiles_exact_artifact_match": selection_exact,
        "selection_conditioned_quantiles_platform_equivalent": True,
        "policy_aligned_quantiles_exact_artifact_match": policy_exact,
        "policy_aligned_quantiles_platform_equivalent": True,
        "platform_numeric_max_ulp_distance": int(max_platform_ulp),
        "platform_numeric_max_abs_diff": float(max_platform_abs),
        "canonical_action_quantiles_used_for_bundle": True,
        "model_state_exact_action_coefficients_verified": False,
        "performance_evaluation_executed": False,
        "independent_model_admission_verified": False,
        "live_order_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/pit")
    parser.add_argument("--code-root", default=str(Path(__file__).resolve().parent))
    args = parser.parse_args()
    out = rehydrate(root=Path(args.root), code_root=Path(args.code_root))
    print(
        "INDEXALERT_FROZEN_BLOCK16_MODEL_REHYDRATION="
        + json.dumps(out, ensure_ascii=False, sort_keys=True),
        flush=True,
    )


if __name__ == "__main__":
    main()
