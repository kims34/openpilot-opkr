"""Immutable prospective broker execution-evidence ledger for IndexAlert.

This is operational evidence infrastructure, not model promotion logic.
Execution tiers are deliberately separated:
- SHADOW decisions submit no broker order and are rejected by this fill ledger.
- PAPER observations are actual responses from an approved paper/simulation
  broker environment; they validate plumbing, not live-market fill quality.
- LIVE-labelled observations are caller-declared real-account execution rows.
  The label alone is structural input and does not authenticate genuine broker
  provenance or empirical execution sufficiency.

The endpoint is fail-closed unless INDEXALERT_EXECUTION_LOG_TOKEN is configured.
Existing observations are immutable. Historical rows written under the former
`PROSPECTIVE_SHADOW_EXECUTION_LOG` label are preserved but quarantined in
summary output as legacy-invalid-for-live-evidence; they are never rewritten.

Genuine LIVE provenance remains a separate research-contract admission step.
This server ledger cannot set genuine_live_provenance_verified, promotion,
sealed-holdout or live-trading authority true from a caller-supplied source.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import math
import os
from datetime import datetime, timezone

from fastapi import Header, HTTPException
from pydantic import BaseModel

import monitor

SHADOW_DECISION_SOURCE = "PROSPECTIVE_SHADOW_DECISION_LOG"
PAPER_EXECUTION_SOURCE = "PROSPECTIVE_PAPER_EXECUTION_LOG"
LIVE_EXECUTION_SOURCE = "PROSPECTIVE_LIVE_EXECUTION_LOG"
LEGACY_SHADOW_FILL_SOURCE = "PROSPECTIVE_SHADOW_EXECUTION_LOG"
ACCEPTED_EXECUTION_SOURCES = frozenset({PAPER_EXECUTION_SOURCE, LIVE_EXECUTION_SOURCE})

# Deprecated compatibility alias for code that imports SOURCE. New callers must
# still send an explicit `source` in the request body; the model has no default.
SOURCE = LIVE_EXECUTION_SOURCE


class ExecutionObservation(BaseModel):
    decision_date: str
    symbol: str
    side: str = "BUY"
    recommendation_at: str
    order_submitted_at: str
    requested_qty: float
    filled_qty: float
    first_fill_at: str | None = None
    final_fill_at: str | None = None
    avg_fill_price: float | None = None
    reference_open: float
    markout_5m_price: float | None = None
    markout_30m_price: float | None = None
    markout_close_price: float | None = None
    source: str
    ingested_at: str | None = None


def _utc(value: str | None, field: str) -> datetime | None:
    if value is None:
        return None
    try:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception as exc:
        raise HTTPException(400, f"invalid {field}") from exc
    if dt.tzinfo is None:
        raise HTTPException(400, f"{field} must be timezone-aware")
    return dt.astimezone(timezone.utc)


def _date(value: str) -> str:
    try:
        return datetime.fromisoformat(str(value)[:10]).date().isoformat()
    except Exception as exc:
        raise HTTPException(400, "invalid decision_date") from exc


def _symbol(value: str) -> str:
    s = str(value).strip().upper()
    if s.isdigit():
        s = s.zfill(6)
    if not s or len(s) > 24:
        raise HTTPException(400, "invalid symbol")
    return s


def _positive(value, field: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise HTTPException(400, f"invalid {field}") from exc
    if not math.isfinite(x) or x <= 0:
        raise HTTPException(400, f"{field} must be positive")
    return x


def _nonnegative(value, field: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise HTTPException(400, f"invalid {field}") from exc
    if not math.isfinite(x) or x < 0:
        raise HTTPException(400, f"{field} must be non-negative")
    return x


def _auth(token: str | None) -> None:
    expected = os.getenv("INDEXALERT_EXECUTION_LOG_TOKEN", "").strip()
    if not expected:
        raise HTTPException(503, "execution evidence logging is not configured")
    supplied = (token or "").strip()
    if not supplied or not hmac.compare_digest(supplied, expected):
        raise HTTPException(401, "invalid execution evidence token")


def init_db() -> None:
    monitor.init_db()
    with monitor.db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS execution_evidence(
            observation_key TEXT PRIMARY KEY,
            decision_date TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            recommendation_at TEXT NOT NULL,
            order_submitted_at TEXT NOT NULL,
            requested_qty REAL NOT NULL,
            filled_qty REAL NOT NULL,
            first_fill_at TEXT,
            final_fill_at TEXT,
            avg_fill_price REAL,
            reference_open REAL NOT NULL,
            markout_5m_price REAL,
            markout_30m_price REAL,
            markout_close_price REAL,
            source TEXT NOT NULL,
            ingested_at TEXT NOT NULL,
            payload_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)


def _normalise(body: ExecutionObservation) -> dict:
    if str(body.side).strip().upper() != "BUY":
        raise HTTPException(400, "current frozen execution evidence supports BUY only")

    source = str(body.source).strip()
    if source == SHADOW_DECISION_SOURCE:
        raise HTTPException(400, "Shadow decisions cannot be recorded as broker fill evidence")
    if source == LEGACY_SHADOW_FILL_SOURCE:
        raise HTTPException(400, "legacy Shadow fill source is closed; use explicit PAPER or LIVE broker source")
    if source not in ACCEPTED_EXECUTION_SOURCES:
        raise HTTPException(400, "source must be PROSPECTIVE_PAPER_EXECUTION_LOG or PROSPECTIVE_LIVE_EXECUTION_LOG")

    recommendation = _utc(body.recommendation_at, "recommendation_at")
    submitted = _utc(body.order_submitted_at, "order_submitted_at")
    if submitted < recommendation:
        raise HTTPException(400, "order_submitted_at cannot precede recommendation_at")

    requested = _positive(body.requested_qty, "requested_qty")
    filled = _nonnegative(body.filled_qty, "filled_qty")
    if filled > requested:
        raise HTTPException(400, "filled_qty cannot exceed requested_qty")
    reference_open = _positive(body.reference_open, "reference_open")

    first = _utc(body.first_fill_at, "first_fill_at")
    final = _utc(body.final_fill_at, "final_fill_at")
    avg = None if body.avg_fill_price is None else _positive(body.avg_fill_price, "avg_fill_price")
    m5 = None if body.markout_5m_price is None else _positive(body.markout_5m_price, "markout_5m_price")
    m30 = None if body.markout_30m_price is None else _positive(body.markout_30m_price, "markout_30m_price")
    mc = None if body.markout_close_price is None else _positive(body.markout_close_price, "markout_close_price")

    if filled == 0:
        if any(v is not None for v in (first, final, avg)):
            raise HTTPException(400, "zero-fill rows cannot contain fill timestamps or fill price")
        if any(v is not None for v in (m5, m30, mc)):
            raise HTTPException(400, "zero-fill rows cannot fabricate markout prices")
    else:
        if any(v is None for v in (first, final, avg, m5, m30, mc)):
            raise HTTPException(400, "filled rows require fill timestamps, fill price and all markouts")
        if first < submitted:
            raise HTTPException(400, "first fill cannot precede order submission")
        if final < first:
            raise HTTPException(400, "final fill cannot precede first fill")

    ingested = _utc(body.ingested_at, "ingested_at") if body.ingested_at else datetime.now(timezone.utc)
    if ingested < recommendation:
        raise HTTPException(400, "ingested_at cannot precede recommendation_at")

    item = {
        "decision_date": _date(body.decision_date),
        "symbol": _symbol(body.symbol),
        "side": "BUY",
        "recommendation_at": recommendation.isoformat(),
        "order_submitted_at": submitted.isoformat(),
        "requested_qty": requested,
        "filled_qty": filled,
        "first_fill_at": first.isoformat() if first else None,
        "final_fill_at": final.isoformat() if final else None,
        "avg_fill_price": avg,
        "reference_open": reference_open,
        "markout_5m_price": m5,
        "markout_30m_price": m30,
        "markout_close_price": mc,
        "source": source,
        "ingested_at": ingested.isoformat(),
    }
    # V2 key includes source so Paper and Live-labelled rows for the same
    # decision can coexist. The source remains a caller label, not provenance.
    item["observation_key"] = hashlib.sha256(
        f"v2|{item['source']}|{item['decision_date']}|{item['symbol']}|{item['recommendation_at']}".encode()
    ).hexdigest()
    payload_json = json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    item["payload_hash"] = hashlib.sha256(payload_json.encode()).hexdigest()
    return item


def _record_result(*, created: bool, item: dict) -> dict:
    return {
        "ok": True,
        "created": bool(created),
        "observation_key": item["observation_key"],
        "source": item["source"],
        "source_label_only": True,
        "genuine_live_provenance_verified": False,
        "project_live_evidence_admitted": False,
        "promotion_ready": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
    }


def record(body: ExecutionObservation) -> dict:
    init_db()
    item = _normalise(body)
    with monitor.db() as con:
        old = con.execute(
            "SELECT payload_hash FROM execution_evidence WHERE observation_key=?",
            (item["observation_key"],),
        ).fetchone()
        if old:
            if old[0] != item["payload_hash"]:
                raise HTTPException(409, "immutable execution observation already exists with different payload")
            return _record_result(created=False, item=item)
        con.execute("""
            INSERT INTO execution_evidence(
                observation_key,decision_date,symbol,side,recommendation_at,order_submitted_at,
                requested_qty,filled_qty,first_fill_at,final_fill_at,avg_fill_price,reference_open,
                markout_5m_price,markout_30m_price,markout_close_price,source,ingested_at,payload_hash,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            item["observation_key"], item["decision_date"], item["symbol"], item["side"],
            item["recommendation_at"], item["order_submitted_at"], item["requested_qty"], item["filled_qty"],
            item["first_fill_at"], item["final_fill_at"], item["avg_fill_price"], item["reference_open"],
            item["markout_5m_price"], item["markout_30m_price"], item["markout_close_price"], item["source"],
            item["ingested_at"], item["payload_hash"], datetime.now(timezone.utc).isoformat(),
        ))
    return _record_result(created=True, item=item)


def summary() -> dict:
    init_db()
    with monitor.db() as con:
        row = con.execute("""
            SELECT COUNT(*),
                   SUM(CASE WHEN filled_qty=0 THEN 1 ELSE 0 END),
                   SUM(CASE WHEN filled_qty>0 AND filled_qty<requested_qty THEN 1 ELSE 0 END),
                   SUM(CASE WHEN filled_qty=requested_qty THEN 1 ELSE 0 END),
                   AVG(filled_qty/requested_qty)
            FROM execution_evidence
        """).fetchone()
        source_rows = con.execute("""
            SELECT source, COUNT(*) FROM execution_evidence GROUP BY source
        """).fetchall()

    source_counts = {str(source): int(count) for source, count in source_rows}
    paper = source_counts.get(PAPER_EXECUTION_SOURCE, 0)
    live_labelled = source_counts.get(LIVE_EXECUTION_SOURCE, 0)
    legacy = source_counts.get(LEGACY_SHADOW_FILL_SOURCE, 0)
    shadow_decision_misfiled = source_counts.get(SHADOW_DECISION_SOURCE, 0)
    recognized = {PAPER_EXECUTION_SOURCE, LIVE_EXECUTION_SOURCE, LEGACY_SHADOW_FILL_SOURCE, SHADOW_DECISION_SOURCE}
    unrecognized = sum(count for source, count in source_counts.items() if source not in recognized)

    return {
        "observations": int(row[0] or 0),
        "no_fill": int(row[1] or 0),
        "partial_fill": int(row[2] or 0),
        "full_fill": int(row[3] or 0),
        "mean_fill_ratio": None if row[4] is None else float(row[4]),
        "paper_observations": int(paper),
        # Backward-compatible count name: this is a caller-labelled tier count,
        # not an independently authenticated real-account provenance count.
        "live_observations": int(live_labelled),
        "live_labelled_observations": int(live_labelled),
        "legacy_shadow_fill_observations": int(legacy),
        "misfiled_shadow_decision_observations": int(shadow_decision_misfiled),
        "unrecognized_source_observations": int(unrecognized),
        "live_structural_execution_rows_present": bool(live_labelled > 0),
        # Deprecated misleading legacy field. It must never become true from a
        # caller-supplied LIVE label; genuine provenance is admitted elsewhere.
        "contains_live_execution_evidence": False,
        "contains_live_execution_evidence_semantics": "DEPRECATED_FAIL_CLOSED_USE_LIVE_LABELLED_OBSERVATIONS",
        "genuine_live_provenance_verified": False,
        "live_empirical_execution_evidence_ready": False,
        "empirical_execution_sufficiency_assessed": False,
        "empirical_execution_blocker_closed": False,
        "project_live_evidence_admitted": False,
        "promotion_ready": False,
        "sealed_holdout_authorized": False,
        "live_trading_authorized": False,
        "note": (
            "PAPER validates broker plumbing only. PROSPECTIVE_LIVE_EXECUTION_LOG is a caller source label only in "
            "this operational ledger and does not authenticate genuine real-account provenance. Independent "
            "broker-native provenance admission plus the frozen numerical sufficiency assessment remain mandatory."
        ),
    }


def attach(app) -> None:
    existing = {getattr(route, "path", None) for route in app.router.routes}
    if "/execution-evidence" not in existing:
        @app.post("/execution-evidence")
        def execution_evidence(body: ExecutionObservation, x_indexalert_execution_token: str | None = Header(default=None)):
            _auth(x_indexalert_execution_token)
            return record(body)
    if "/execution-evidence/summary" not in existing:
        @app.get("/execution-evidence/summary")
        def execution_evidence_summary(x_indexalert_execution_token: str | None = Header(default=None)):
            _auth(x_indexalert_execution_token)
            return summary()
