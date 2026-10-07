"""Label-free current-session inputs; never research admission or a signal.

Uses the frozen reference's feature/context functions and ordering. Availability
timestamps are checked as supplied claims, not independently authenticated PIT
evidence. A stored input snapshot is neither a decision nor a NO_TRADE session.
"""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re

import numpy as np
import pandas as pd

from research_v1_context import CONTEXT_FEATURES, add_context
from research_v1_pit_features import add_pit_features
from research_v1_pit_labels import FEATURES
from research_v1_krx_private_store import validate_private_root

RAW_COLUMNS = (
    "decision_date", "symbol", "open", "high", "low", "close", "volume",
    "value", "krx_change_return", "available_at",
)
NUMERIC_COLUMNS = RAW_COLUMNS[2:-1]


class ProspectiveInputError(ValueError):
    pass


def _aware(value) -> pd.Timestamp:
    if not isinstance(value, (str, datetime, pd.Timestamp)) or pd.isna(value):
        raise ProspectiveInputError("explicit timezone-aware timestamp required")
    try:
        t = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ProspectiveInputError("invalid timestamp") from exc
    if t.tzinfo is None:
        raise ProspectiveInputError("explicit timezone-aware timestamp required")
    return t.tz_convert("UTC")


def _canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def build_current_session_inputs(raw: pd.DataFrame, *, decision_at: str) -> dict:
    """Prepare today's matrix without training, predictions or future outcomes.

    Late rows fail the entire supplied cross-section instead of silently
    deleting names and changing ranks. Later sessions are excluded before
    checking values/availability or deriving any features.
    """
    moment = _aware(decision_at)
    session = moment.tz_convert("Asia/Seoul").tz_localize(None).normalize()
    missing = sorted(set(RAW_COLUMNS) - set(raw.columns))
    if missing:
        raise ProspectiveInputError(f"missing raw columns: {missing}")
    x = raw.loc[:, RAW_COLUMNS].copy()
    dates = pd.to_datetime(x["decision_date"], errors="coerce")
    if dates.isna().any() or dates.dt.tz is not None or not dates.eq(dates.dt.normalize()).all():
        raise ProspectiveInputError("decision_date must be an exact naive market date")
    x["decision_date"] = dates
    x = x[x.decision_date <= session].copy()
    if x.empty or not x.decision_date.eq(session).any():
        raise ProspectiveInputError("current session absent; stale input is not NO_TRADE")
    if not x.symbol.map(lambda v: type(v) is str and bool(v) and v == v.strip()).all():
        raise ProspectiveInputError("nonempty original security identifiers required")
    if x.duplicated(["decision_date", "symbol"]).any():
        raise ProspectiveInputError("duplicate security/session input")
    availability = x.available_at.map(_aware)
    if (availability > moment).any():
        raise ProspectiveInputError("late source row; supplied cross-section incomplete at decision time")
    earliest = x.decision_date.dt.tz_localize("Asia/Seoul").dt.tz_convert("UTC")
    if (availability < earliest).any():
        raise ProspectiveInputError("availability precedes source session")
    for col in NUMERIC_COLUMNS:
        if x[col].map(lambda v: isinstance(v, (bool, np.bool_))).any():
            raise ProspectiveInputError(f"boolean market value: {col}")
        x[col] = pd.to_numeric(x[col], errors="coerce")
        if not np.isfinite(x[col]).all():
            raise ProspectiveInputError(f"unknown/nonfinite market value: {col}")
    if (x[["open", "high", "low", "close"]] <= 0).any().any():
        raise ProspectiveInputError("nonpositive OHLC")
    if (x[["volume", "value"]] < 0).any().any() or (x.krx_change_return <= -1).any():
        raise ProspectiveInputError("invalid volume/value/return")
    if ((x.low > x[["open", "close"]].min(axis=1)) |
        (x.high < x[["open", "close"]].max(axis=1)) | (x.low > x.high)).any():
        raise ProspectiveInputError("inconsistent OHLC")

    x["available_at"] = availability.map(lambda v: v.isoformat())
    x = x.sort_values(["decision_date", "symbol"]).reset_index(drop=True)
    source_hash = hashlib.sha256()
    for row in x.itertuples(index=False):
        record = row._asdict()
        record["decision_date"] = row.decision_date.strftime("%Y-%m-%d")
        source_hash.update(_canonical(record) + b"\n")
    source_digest = source_hash.hexdigest()
    features = add_pit_features(x)
    features["log_adv20"] = np.log1p(features["adv20"].clip(lower=0))
    for col in ("ret5", "ret20", "vol20", "adv20"):
        features[f"{col}_rank"] = features.groupby("decision_date")[col].rank(pct=True)
    # Match make_pit_supervised's feature-completeness test, then the frozen
    # runner's liquidity filter BEFORE calculating market context.
    complete = features.loc[features[FEATURES].notna().all(axis=1), ["decision_date", "symbol", *FEATURES]]
    liquid = complete[complete.adv20_rank >= .20].copy()
    contextual = add_context(liquid)
    current = contextual[contextual.decision_date.eq(session)].copy()
    current = current.sort_values("symbol").reset_index(drop=True)
    if current.empty or not np.isfinite(current[CONTEXT_FEATURES]).all().all():
        raise ProspectiveInputError("current feature matrix unavailable; not a NO_TRADE decision")
    return {
        "classification": "INPUT_SNAPSHOT_ONLY_NOT_DECISION",
        "decision_at": moment.isoformat(), "session": session.strftime("%Y-%m-%d"),
        "input_sha256": source_digest, "source_rows": len(x),
        "feature_columns": list(CONTEXT_FEATURES), "features": current,
        "independent_source_admission_verified": False,
        "signal_generation_complete": False, "decision_recorded": False,
        "no_trade_recorded": False, "live_order_authorized": False,
    }


def store_input_snapshot(snapshot: dict, *, root: str, git_worktree: str) -> dict:
    """Durably create one private immutable input checkpoint per session.

    Identical retry is idempotent. A different checkpoint for the same session
    is rejected; it cannot replace the original snapshot. Local durability does
    not authenticate source claims or establish prospective decision chronology.
    """
    if snapshot.get("classification") != "INPUT_SNAPSHOT_ONLY_NOT_DECISION":
        raise ProspectiveInputError("input snapshot required")
    for key in ("independent_source_admission_verified", "signal_generation_complete",
                "decision_recorded", "no_trade_recorded", "live_order_authorized"):
        if snapshot.get(key) is not False:
            raise ProspectiveInputError("input snapshot cannot claim decision/admission authority")
    session = snapshot.get("session")
    if type(session) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", session):
        raise ProspectiveInputError("canonical session required")
    body = dict(snapshot)
    frame = body.pop("features").copy()
    frame["decision_date"] = frame.decision_date.dt.strftime("%Y-%m-%d")
    body["features"] = frame.to_dict("records")
    payload = _canonical(body)
    digest = hashlib.sha256(payload).hexdigest()
    base = validate_private_root(root, git_worktree=git_worktree)
    target = base / f"input-{session}.json"
    # A same-directory temp file followed by link gives atomic no-overwrite
    # publication. Readers never see a partial JSON file after a crash.
    import tempfile
    fd, name = tempfile.mkstemp(prefix=".input-", dir=base)
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
                raise ProspectiveInputError("conflicting or tampered existing input checkpoint")
            created = False
        directory = os.open(base, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        temp.unlink(missing_ok=True)
    return {"snapshot_sha256": digest, "created": created,
            "decision_recorded": False, "no_trade_recorded": False,
            "independent_source_admission_verified": False, "live_order_authorized": False}
