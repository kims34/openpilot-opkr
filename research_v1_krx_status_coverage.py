"""Fail-closed coverage audit for KRX common-stock identity/status evidence.

The auditor does not invent historical snapshots, trading dates, common-stock
identity or stable security identifiers. The caller supplies an independently
attested expected snapshot scope. Current identity evidence can be evaluated,
but Gate-C structural completeness remains false unless the observed evidence
contains the stable full issue identifier required by that scope.

This is source-integrity infrastructure only. It cannot set Final-Judge ready,
consume sealed holdout or authorize performance/live trading.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable

import pandas as pd


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_COLUMNS = (
    "snapshot_date",
    "symbol",
    "isu_cd",
    "scope_contract_fingerprint_sha256",
)
OBSERVED_BASE_COLUMNS = (
    "decision_date",
    "symbol",
    "common_stock_identity_official",
    "security_scope_identity_validated",
    "available_at",
)


class KRXStatusCoverageError(ValueError):
    """Raised when status coverage evidence is ambiguous or malformed."""


@dataclass(frozen=True)
class StatusCoverageAudit:
    requested_start: str
    requested_end: str
    expected_records: int
    observed_common_stock_records: int
    expected_snapshot_dates: int
    observed_snapshot_dates: int
    expected_symbols: int
    observed_symbols: int
    stable_issue_id_present_in_observed: bool
    missing_key_count: int
    extra_key_count: int
    duplicate_observed_key_count: int
    availability_lineage_complete: bool
    identity_attestation_complete: bool
    exact_key_coverage: bool
    coverage_structurally_complete: bool
    judge_security_status_ready: bool
    sealed_holdout_authorized: bool


def _require_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [name for name in columns if name not in df.columns]
    if missing:
        raise KRXStatusCoverageError(f"{label} missing required columns: {missing}")


def _symbol(value) -> str:
    text = re.sub(r"\.0$", "", str(value).strip().upper())
    if text.isdigit():
        text = text.zfill(6)
    if not re.fullmatch(r"[0-9A-Z]{6,12}", text):
        raise KRXStatusCoverageError(f"invalid symbol: {value!r}")
    return text


def _issue(value) -> str:
    text = str(value).strip().upper()
    if not re.fullmatch(r"[0-9A-Z]{10,20}", text):
        raise KRXStatusCoverageError(f"invalid isu_cd: {value!r}")
    return text


def _date(value, field: str) -> pd.Timestamp:
    try:
        ts = pd.Timestamp(value)
    except Exception as exc:
        raise KRXStatusCoverageError(f"{field} contains unparseable date: {value!r}") from exc
    if pd.isna(ts):
        raise KRXStatusCoverageError(f"{field} contains missing date")
    if ts != ts.normalize():
        raise KRXStatusCoverageError(f"{field} must be a date/midnight key; got {value!r}")
    return ts.tz_localize(None).normalize() if ts.tzinfo else ts.normalize()


def _sha256(value, field: str) -> str:
    text = str(value).strip().lower()
    if not SHA256_RE.fullmatch(text):
        raise KRXStatusCoverageError(f"{field} must be a lowercase 64-hex SHA256 fingerprint")
    return text


def _aware(value, field: str) -> pd.Timestamp:
    try:
        ts = pd.Timestamp(value)
    except Exception as exc:
        raise KRXStatusCoverageError(f"{field} contains unparseable timestamp: {value!r}") from exc
    if pd.isna(ts) or ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXStatusCoverageError(f"{field} must be non-missing and timezone-aware")
    return ts


def normalise_expected_status_scope(expected_scope: pd.DataFrame) -> pd.DataFrame:
    """Normalize an externally attested date/security/stable-ID scope."""
    if expected_scope is None or expected_scope.empty:
        raise KRXStatusCoverageError("expected status scope is empty")
    _require_columns(expected_scope, EXPECTED_COLUMNS, "expected status scope")
    rows = []
    for _, raw in expected_scope.iterrows():
        rows.append({
            "snapshot_date": _date(raw["snapshot_date"], "snapshot_date"),
            "symbol": _symbol(raw["symbol"]),
            "isu_cd": _issue(raw["isu_cd"]),
            "scope_contract_fingerprint_sha256": _sha256(
                raw["scope_contract_fingerprint_sha256"],
                "scope_contract_fingerprint_sha256",
            ),
        })
    out = pd.DataFrame(rows)
    key_cols = ["snapshot_date", "symbol", "isu_cd"]
    if out.duplicated(key_cols).any():
        raise KRXStatusCoverageError("expected status scope contains duplicate keys")
    if out["scope_contract_fingerprint_sha256"].nunique() != 1:
        raise KRXStatusCoverageError("expected status scope mixes multiple scope-contract fingerprints")
    return out.sort_values(key_cols).reset_index(drop=True)


def _normalise_observed_identity(identity_snapshots: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    if identity_snapshots is None or identity_snapshots.empty:
        raise KRXStatusCoverageError("observed identity snapshots are empty")
    _require_columns(identity_snapshots, OBSERVED_BASE_COLUMNS, "observed identity snapshots")

    if not bool(identity_snapshots["security_scope_identity_validated"].all()):
        raise KRXStatusCoverageError("observed identity snapshots contain unvalidated identity rows")
    # Every row, including non-common securities, must retain availability lineage
    # before the common-stock subset is selected.
    for value in identity_snapshots["available_at"]:
        _aware(value, "available_at")

    common = identity_snapshots[
        identity_snapshots["common_stock_identity_official"].map(lambda x: x is True)
    ].copy()
    stable_present = "isu_cd" in common.columns and common["isu_cd"].notna().all()

    rows = []
    for _, raw in common.iterrows():
        row = {
            "snapshot_date": _date(raw["decision_date"], "decision_date"),
            "symbol": _symbol(raw["symbol"]),
        }
        if stable_present:
            row["isu_cd"] = _issue(raw["isu_cd"])
        rows.append(row)
    return pd.DataFrame(rows), bool(stable_present)


def audit_status_identity_coverage(
    expected_scope: pd.DataFrame,
    identity_snapshots: pd.DataFrame,
) -> dict:
    """Audit exact common-stock identity coverage against explicit expected keys."""
    expected = normalise_expected_status_scope(expected_scope)
    observed, stable_present = _normalise_observed_identity(identity_snapshots)

    availability_complete = bool(identity_snapshots["available_at"].notna().all())
    identity_complete = bool(identity_snapshots["security_scope_identity_validated"].all())
    duplicate_observed = 0
    missing_count = len(expected)
    extra_count = len(observed)
    missing_sample = []
    extra_sample = []
    exact = False

    if stable_present:
        key_cols = ["snapshot_date", "symbol", "isu_cd"]
        duplicate_observed = int(observed.duplicated(key_cols, keep=False).sum())
        if duplicate_observed:
            raise KRXStatusCoverageError("observed common-stock identity contains duplicate snapshot/security keys")
        expected_idx = pd.MultiIndex.from_frame(expected[key_cols])
        observed_idx = pd.MultiIndex.from_frame(observed[key_cols])
        missing = expected_idx.difference(observed_idx)
        extra = observed_idx.difference(expected_idx)
        missing_count = len(missing)
        extra_count = len(extra)
        missing_sample = [tuple(map(str, key)) for key in list(missing[:10])]
        extra_sample = [tuple(map(str, key)) for key in list(extra[:10])]
        exact = missing_count == 0 and extra_count == 0 and len(expected_idx) == len(observed_idx)

    structurally_complete = bool(
        stable_present
        and availability_complete
        and identity_complete
        and duplicate_observed == 0
        and exact
    )
    audit = StatusCoverageAudit(
        requested_start=str(expected["snapshot_date"].min().date()),
        requested_end=str(expected["snapshot_date"].max().date()),
        expected_records=int(len(expected)),
        observed_common_stock_records=int(len(observed)),
        expected_snapshot_dates=int(expected["snapshot_date"].nunique()),
        observed_snapshot_dates=int(observed["snapshot_date"].nunique()) if not observed.empty else 0,
        expected_symbols=int(expected["symbol"].nunique()),
        observed_symbols=int(observed["symbol"].nunique()) if not observed.empty else 0,
        stable_issue_id_present_in_observed=stable_present,
        missing_key_count=int(missing_count),
        extra_key_count=int(extra_count),
        duplicate_observed_key_count=int(duplicate_observed),
        availability_lineage_complete=availability_complete,
        identity_attestation_complete=identity_complete,
        exact_key_coverage=exact,
        coverage_structurally_complete=structurally_complete,
        # Deliberately false: identity coverage alone does not prove halt/cleanup/
        # delisting completeness, exact economics, all A-F gates or promotion.
        judge_security_status_ready=False,
        sealed_holdout_authorized=False,
    )
    out = asdict(audit)
    out["missing_key_sample"] = missing_sample
    out["extra_key_sample"] = extra_sample
    out["guardrail"] = (
        "The auditor never generates missing historical identity snapshots or stable IDs. "
        "Current identity evidence without an official stable issue identifier cannot close Gate C. "
        "Even exact identity coverage does not set Final-Judge ready or authorize holdout use."
    )
    return out
