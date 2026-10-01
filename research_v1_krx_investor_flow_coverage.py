"""Fail-closed historical coverage audit for KRX investor-flow source evidence.

This module never invents a trading calendar, expected universe, zero-flow row or
security mapping. The caller must supply an independently attested expected
(event_date, symbol, isu_cd) scope. Coverage passes structurally only when the
validated investor-flow lineage matches that expected key set exactly.

Structural coverage evidence is necessary for KRX source Gate C, but it never
by itself authorizes feature-performance research, sealed holdout use or live
trading.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import re
from typing import Iterable

import pandas as pd

from research_v1_krx_investor_flow_lineage import KRXInvestorFlowLineageError


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_COLUMNS = (
    "event_date",
    "symbol",
    "isu_cd",
    "common_stock_identity_official",
    "scope_contract_fingerprint_sha256",
)


class KRXInvestorFlowCoverageError(ValueError):
    """Raised when expected-scope or observed coverage evidence is ambiguous."""


@dataclass(frozen=True)
class InvestorFlowCoverageAudit:
    requested_start: str
    requested_end: str
    expected_records: int
    observed_records: int
    expected_event_dates: int
    observed_event_dates: int
    expected_symbols: int
    observed_symbols: int
    expected_issue_ids: int
    observed_issue_ids: int
    missing_key_count: int
    extra_key_count: int
    duplicate_observed_key_count: int
    expected_scope_contract_fingerprint_count: int
    common_stock_identity_attested: bool
    exact_key_coverage: bool
    coverage_structurally_complete: bool
    feature_performance_testing_authorized: bool
    sealed_holdout_authorized: bool


def _require_columns(df: pd.DataFrame, columns: Iterable[str], label: str) -> None:
    missing = [name for name in columns if name not in df.columns]
    if missing:
        raise KRXInvestorFlowCoverageError(
            f"{label} missing required columns: {missing}"
        )


def _symbol(value) -> str:
    text = str(value).strip().upper()
    text = re.sub(r"\.0$", "", text)
    if text.isdigit():
        text = text.zfill(6)
    if not re.fullmatch(r"[0-9A-Z]{6,12}", text):
        raise KRXInvestorFlowCoverageError(f"invalid symbol in expected scope: {value!r}")
    return text


def _issue(value) -> str:
    text = str(value).strip().upper()
    if not re.fullmatch(r"[0-9A-Z]{10,20}", text):
        raise KRXInvestorFlowCoverageError(f"invalid isu_cd in expected scope: {value!r}")
    return text


def _date(value, field: str) -> pd.Timestamp:
    try:
        ts = pd.Timestamp(value)
    except Exception as exc:
        raise KRXInvestorFlowCoverageError(
            f"{field} contains unparseable date: {value!r}"
        ) from exc
    if pd.isna(ts):
        raise KRXInvestorFlowCoverageError(f"{field} contains missing date")
    # Expected scope is a date key, not an availability timestamp. Reject a
    # non-midnight timestamp rather than silently truncating it.
    if ts != ts.normalize():
        raise KRXInvestorFlowCoverageError(
            f"{field} must be a date/midnight key; got {value!r}"
        )
    return ts.tz_localize(None).normalize() if ts.tzinfo else ts.normalize()


def _sha256(value, field: str) -> str:
    text = str(value).strip().lower()
    if not SHA256_RE.fullmatch(text):
        raise KRXInvestorFlowCoverageError(
            f"{field} must be a lowercase 64-hex SHA256 fingerprint"
        )
    return text


def normalise_expected_investor_flow_scope(expected_scope: pd.DataFrame) -> pd.DataFrame:
    """Normalize an externally attested expected common-stock coverage grid.

    `expected_scope` must already contain the exact event dates and securities
    that an authorized source contract says should be represented. This function
    must never generate business days, fill missing dates, infer security identity
    or create zero-flow records.
    """
    if expected_scope is None or expected_scope.empty:
        raise KRXInvestorFlowCoverageError("expected investor-flow scope is empty")
    _require_columns(expected_scope, EXPECTED_COLUMNS, "expected investor-flow scope")

    rows = []
    for idx, raw in expected_scope.iterrows():
        common = raw["common_stock_identity_official"]
        if not isinstance(common, bool):
            raise KRXInvestorFlowCoverageError(
                f"common_stock_identity_official must be bool at row {idx}"
            )
        if not common:
            raise KRXInvestorFlowCoverageError(
                f"expected scope contains non-common/unattested security at row {idx}"
            )
        rows.append({
            "event_date": _date(raw["event_date"], "event_date"),
            "symbol": _symbol(raw["symbol"]),
            "isu_cd": _issue(raw["isu_cd"]),
            "common_stock_identity_official": True,
            "scope_contract_fingerprint_sha256": _sha256(
                raw["scope_contract_fingerprint_sha256"],
                "scope_contract_fingerprint_sha256",
            ),
        })

    out = pd.DataFrame(rows, index=expected_scope.index)
    key_cols = ["event_date", "symbol", "isu_cd"]
    if out.duplicated(key_cols).any():
        dup = out.loc[out.duplicated(key_cols, keep=False), key_cols].head(10)
        raise KRXInvestorFlowCoverageError(
            "expected investor-flow scope contains duplicate keys: "
            + dup.astype(str).to_dict(orient="records").__repr__()
        )
    if out["scope_contract_fingerprint_sha256"].nunique() != 1:
        raise KRXInvestorFlowCoverageError(
            "expected investor-flow scope mixes multiple scope-contract fingerprints"
        )
    return out.sort_values(key_cols).reset_index(drop=True)


def _observed_keys(validated_lineage: pd.DataFrame) -> pd.DataFrame:
    if validated_lineage is None or validated_lineage.empty:
        raise KRXInvestorFlowCoverageError("validated investor-flow lineage is empty")
    required = ["event_time", "symbol", "isu_cd", "lineage_validated"]
    _require_columns(validated_lineage, required, "validated investor-flow lineage")
    if not bool(validated_lineage["lineage_validated"].all()):
        raise KRXInvestorFlowCoverageError("investor-flow lineage contains unvalidated rows")

    rows = []
    for idx, raw in validated_lineage.iterrows():
        try:
            event_ts = pd.Timestamp(raw["event_time"])
        except Exception as exc:
            raise KRXInvestorFlowCoverageError(
                f"lineage event_time is unparseable at row {idx}"
            ) from exc
        if event_ts.tzinfo is None or event_ts.utcoffset() is None:
            # This should already be impossible after lineage validation, but
            # fail closed here rather than trusting a hand-edited frame.
            raise KRXInvestorFlowCoverageError(
                f"lineage event_time must remain timezone-aware at row {idx}"
            )
        event_date = event_ts.tz_convert("Asia/Seoul").tz_localize(None).normalize()
        rows.append({
            "event_date": event_date,
            "symbol": _symbol(raw["symbol"]),
            "isu_cd": _issue(raw["isu_cd"]),
        })
    return pd.DataFrame(rows, index=validated_lineage.index)


def audit_investor_flow_coverage(
    expected_scope: pd.DataFrame,
    validated_lineage: pd.DataFrame,
) -> dict:
    """Compare explicit expected keys against validated observed lineage exactly."""
    expected = normalise_expected_investor_flow_scope(expected_scope)
    observed = _observed_keys(validated_lineage)
    key_cols = ["event_date", "symbol", "isu_cd"]

    duplicate_observed = int(observed.duplicated(key_cols, keep=False).sum())
    if duplicate_observed:
        raise KRXInvestorFlowCoverageError(
            "observed investor-flow lineage contains duplicate event/security keys"
        )

    expected_idx = pd.MultiIndex.from_frame(expected[key_cols])
    observed_idx = pd.MultiIndex.from_frame(observed[key_cols])
    missing = expected_idx.difference(observed_idx)
    extra = observed_idx.difference(expected_idx)
    exact = len(missing) == 0 and len(extra) == 0 and len(expected_idx) == len(observed_idx)

    audit = InvestorFlowCoverageAudit(
        requested_start=str(expected["event_date"].min().date()),
        requested_end=str(expected["event_date"].max().date()),
        expected_records=int(len(expected)),
        observed_records=int(len(observed)),
        expected_event_dates=int(expected["event_date"].nunique()),
        observed_event_dates=int(observed["event_date"].nunique()),
        expected_symbols=int(expected["symbol"].nunique()),
        observed_symbols=int(observed["symbol"].nunique()),
        expected_issue_ids=int(expected["isu_cd"].nunique()),
        observed_issue_ids=int(observed["isu_cd"].nunique()),
        missing_key_count=int(len(missing)),
        extra_key_count=int(len(extra)),
        duplicate_observed_key_count=duplicate_observed,
        expected_scope_contract_fingerprint_count=int(
            expected["scope_contract_fingerprint_sha256"].nunique()
        ),
        common_stock_identity_attested=bool(
            expected["common_stock_identity_official"].all()
        ),
        exact_key_coverage=exact,
        coverage_structurally_complete=exact,
        # Deliberately false. Exact structural coverage is only one Gate C input;
        # Gates A/B/D/E/F, source authorization, experiment preregistration and
        # research promotion rules remain independent.
        feature_performance_testing_authorized=False,
        sealed_holdout_authorized=False,
    )
    out = asdict(audit)
    out["missing_key_sample"] = [tuple(map(str, key)) for key in list(missing[:10])]
    out["extra_key_sample"] = [tuple(map(str, key)) for key in list(extra[:10])]
    out["guardrail"] = (
        "Coverage is evaluated only against caller-supplied attested keys. The "
        "auditor never invents trading dates, securities or zero-flow observations. "
        "Structural completeness does not authorize performance testing or holdout use."
    )
    return out
