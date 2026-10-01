"""Fail-closed PIT lineage validation for official KRX investor-flow history.

This module validates source/time lineage only. It does not download KRX data,
fit a model, evaluate Alpha, authorize a performance experiment, consume the
sealed holdout or authorize trading.

Frozen timing rule: final day-D stock investor-trading results must not be
published before 20:00 Asia/Seoul and may enter a decision only after the
observation is actually available.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, time
import re
from typing import Iterable
from zoneinfo import ZoneInfo

import pandas as pd

from research_v1_krx_public_evidence import public_evidence_fingerprint_sha256


KST = ZoneInfo("Asia/Seoul")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_COLUMNS = (
    "symbol",
    "isu_cd",
    "event_time",
    "published_at",
    "available_at",
    "ingested_at",
    "source_contract_fingerprint_sha256",
    "public_contract_evidence_fingerprint_sha256",
)


class KRXInvestorFlowLineageError(ValueError):
    """Raised when investor-flow PIT lineage is incomplete or unsafe."""


@dataclass(frozen=True)
class InvestorFlowLineageAudit:
    rows: int
    unique_symbols: int
    unique_issue_ids: int
    event_start: str | None
    event_end: str | None
    source_contract_fingerprint_count: int
    public_contract_evidence_fingerprint: str
    timezone_lineage_complete: bool
    chronology_valid: bool
    publication_floor_valid: bool
    stable_identity_present: bool
    public_contract_evidence_matches_current: bool
    lineage_structurally_valid: bool
    feature_performance_testing_authorized: bool
    sealed_holdout_authorized: bool


def _require_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [name for name in columns if name not in df.columns]
    if missing:
        raise KRXInvestorFlowLineageError(
            f"investor-flow lineage missing required columns: {missing}"
        )


def _normalise_symbol(value) -> str:
    text = str(value).strip().upper()
    if not text or text in {"NAN", "NONE", "<NA>"}:
        raise KRXInvestorFlowLineageError("symbol is missing")
    text = re.sub(r"\.0$", "", text)
    if text.isdigit():
        text = text.zfill(6)
    if not re.fullmatch(r"[0-9A-Z]{6,12}", text):
        raise KRXInvestorFlowLineageError(f"invalid symbol format: {value!r}")
    return text


def _normalise_issue_id(value) -> str:
    text = str(value).strip().upper()
    if not text or text in {"NAN", "NONE", "<NA>"}:
        raise KRXInvestorFlowLineageError("isu_cd is missing")
    if not re.fullmatch(r"[0-9A-Z]{10,20}", text):
        raise KRXInvestorFlowLineageError(f"invalid isu_cd format: {value!r}")
    return text


def _aware_timestamp(value, field: str) -> pd.Timestamp:
    try:
        ts = pd.Timestamp(value)
    except Exception as exc:
        raise KRXInvestorFlowLineageError(
            f"{field} contains unparseable timestamp: {value!r}"
        ) from exc
    if pd.isna(ts):
        raise KRXInvestorFlowLineageError(f"{field} contains missing timestamp")
    if ts.tzinfo is None or ts.utcoffset() is None:
        raise KRXInvestorFlowLineageError(
            f"{field} must be timezone-aware; got {value!r}"
        )
    return ts


def _sha256(value, field: str) -> str:
    text = str(value).strip().lower()
    if not SHA256_RE.fullmatch(text):
        raise KRXInvestorFlowLineageError(
            f"{field} must be a lowercase 64-hex SHA256 fingerprint"
        )
    return text


def _publication_floor(event_time: pd.Timestamp) -> pd.Timestamp:
    local_event = event_time.tz_convert(KST)
    d = local_event.date()
    return pd.Timestamp(datetime.combine(d, time(20, 0), tzinfo=KST))


def normalise_investor_flow_lineage(table: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize PIT lineage without granting research permission.

    Required timestamp order is:
    `event_time <= published_at <= available_at <= ingested_at`.

    For final day-D investor-flow observations, `published_at` must also be at
    or after 20:00 Asia/Seoul on the local event date. All timestamps must be
    timezone-aware; naive historical timestamps fail closed.
    """
    if table is None or table.empty:
        raise KRXInvestorFlowLineageError("investor-flow lineage table is empty")
    _require_columns(table, REQUIRED_COLUMNS)

    current_public_fp = public_evidence_fingerprint_sha256()
    rows = []
    for idx, raw in table.iterrows():
        symbol = _normalise_symbol(raw["symbol"])
        isu_cd = _normalise_issue_id(raw["isu_cd"])
        event_time = _aware_timestamp(raw["event_time"], "event_time")
        published_at = _aware_timestamp(raw["published_at"], "published_at")
        available_at = _aware_timestamp(raw["available_at"], "available_at")
        ingested_at = _aware_timestamp(raw["ingested_at"], "ingested_at")
        source_fp = _sha256(
            raw["source_contract_fingerprint_sha256"],
            "source_contract_fingerprint_sha256",
        )
        public_fp = _sha256(
            raw["public_contract_evidence_fingerprint_sha256"],
            "public_contract_evidence_fingerprint_sha256",
        )

        event_utc = event_time.tz_convert("UTC")
        published_utc = published_at.tz_convert("UTC")
        available_utc = available_at.tz_convert("UTC")
        ingested_utc = ingested_at.tz_convert("UTC")
        if not (event_utc <= published_utc <= available_utc <= ingested_utc):
            raise KRXInvestorFlowLineageError(
                "timestamp chronology violation at row "
                f"{idx}: require event_time <= published_at <= available_at <= ingested_at"
            )

        publication_floor = _publication_floor(event_time)
        if published_at.tz_convert(KST) < publication_floor:
            raise KRXInvestorFlowLineageError(
                f"published_at violates KRX final-result floor at row {idx}: "
                f"must be >= {publication_floor.isoformat()}"
            )
        if public_fp != current_public_fp:
            raise KRXInvestorFlowLineageError(
                "public contract evidence fingerprint does not match the current "
                f"frozen manifest at row {idx}"
            )

        rows.append({
            "symbol": symbol,
            "isu_cd": isu_cd,
            "event_time": event_time,
            "published_at": published_at,
            "available_at": available_at,
            "ingested_at": ingested_at,
            "source_contract_fingerprint_sha256": source_fp,
            "public_contract_evidence_fingerprint_sha256": public_fp,
            "publication_floor_kst": publication_floor,
            "lineage_validated": True,
        })

    out = pd.DataFrame(rows, index=table.index)
    # A single historical dataset should not silently splice multiple acquisition
    # contracts together. If that is genuinely required later, it needs an
    # explicit multi-contract audit rather than an implicit merge here.
    if out["source_contract_fingerprint_sha256"].nunique() != 1:
        raise KRXInvestorFlowLineageError(
            "historical investor-flow lineage mixes multiple source-contract fingerprints"
        )
    return out


def attach_decision_eligibility(
    lineage: pd.DataFrame,
    decision_time,
) -> pd.DataFrame:
    """Mark rows usable at one decision timestamp under strict PIT availability.

    This function deliberately does not invent a KRX trading calendar. The
    caller supplies the actual decision timestamp. An observation is eligible
    only when `decision_time >= available_at`.
    """
    if lineage is None or lineage.empty:
        raise KRXInvestorFlowLineageError("validated lineage is required")
    if "lineage_validated" not in lineage.columns or not bool(
        lineage["lineage_validated"].all()
    ):
        raise KRXInvestorFlowLineageError(
            "decision eligibility requires lineage validated by this module"
        )
    decision = _aware_timestamp(decision_time, "decision_time")
    out = lineage.copy()
    out["decision_time"] = decision
    decision_utc = decision.tz_convert("UTC")
    out["eligible_at_decision"] = out["available_at"].map(
        lambda ts: decision_utc >= pd.Timestamp(ts).tz_convert("UTC")
    ).astype(bool)
    return out


def audit_investor_flow_lineage(lineage: pd.DataFrame) -> dict:
    """Summarize structural PIT evidence without authorizing performance tests."""
    if lineage is None or lineage.empty:
        raise KRXInvestorFlowLineageError("validated lineage is required")
    if "lineage_validated" not in lineage.columns or not bool(
        lineage["lineage_validated"].all()
    ):
        raise KRXInvestorFlowLineageError("lineage contains unvalidated rows")

    current_public_fp = public_evidence_fingerprint_sha256()
    public_fps = set(lineage["public_contract_evidence_fingerprint_sha256"])
    source_fps = set(lineage["source_contract_fingerprint_sha256"])
    event_times = pd.Series(lineage["event_time"])
    audit = InvestorFlowLineageAudit(
        rows=int(len(lineage)),
        unique_symbols=int(lineage["symbol"].nunique()),
        unique_issue_ids=int(lineage["isu_cd"].nunique()),
        event_start=str(min(event_times).isoformat()) if len(event_times) else None,
        event_end=str(max(event_times).isoformat()) if len(event_times) else None,
        source_contract_fingerprint_count=len(source_fps),
        public_contract_evidence_fingerprint=current_public_fp,
        timezone_lineage_complete=True,
        chronology_valid=True,
        publication_floor_valid=True,
        stable_identity_present=True,
        public_contract_evidence_matches_current=(public_fps == {current_public_fp}),
        lineage_structurally_valid=(
            len(source_fps) == 1 and public_fps == {current_public_fp}
        ),
        # Deliberately false: valid lineage is necessary evidence for Gate D/E,
        # but Gates A-F, historical coverage and experiment preregistration remain
        # separate blockers.
        feature_performance_testing_authorized=False,
        sealed_holdout_authorized=False,
    )
    out = asdict(audit)
    out["guardrail"] = (
        "PIT lineage validity does not close the KRX source contract, does not "
        "authorize investor-flow performance research, and does not consume the sealed holdout."
    )
    return out
