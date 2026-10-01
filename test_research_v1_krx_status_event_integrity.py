import pandas as pd
import pytest

from research_v1_krx_cleanup_status import KRX_CLEANUP_SOURCE
from research_v1_krx_official_status import (
    KRX_DELIST_PRICE_SOURCE,
    KRX_DELIST_SOURCE,
    KRX_HALT_SOURCE,
)
from research_v1_krx_status_event_integrity import (
    KRXStatusEventIntegrityError,
    audit_status_event_integrity,
)


AVAILABLE = pd.Timestamp("2026-09-09T20:00:00+09:00")


def _halts():
    return pd.DataFrame([
        {
            "symbol": "000300",
            "halt_date": pd.Timestamp("2026-09-01"),
            "resume_date": pd.Timestamp("2026-09-02"),
            "source": KRX_HALT_SOURCE,
            "available_at": AVAILABLE,
        }
    ])


def _cleanup(planned="2026-09-17", end="2026-09-16", symbol="000300"):
    return pd.DataFrame([
        {
            "symbol": symbol,
            "cleanup_start": pd.Timestamp("2026-09-10"),
            "cleanup_end": pd.Timestamp(end),
            "planned_delisting_date": pd.Timestamp(planned),
            "source": KRX_CLEANUP_SOURCE,
            "available_at": AVAILABLE,
        }
    ])


def _delist(date="2026-09-17", symbol="000300"):
    return pd.DataFrame([
        {
            "symbol": symbol,
            "delisting_date": pd.Timestamp(date),
            "source": KRX_DELIST_SOURCE,
            "available_at": AVAILABLE,
        }
    ])


def _prices(date="2026-09-16", symbol="000300"):
    return pd.DataFrame([
        {
            "date": pd.Timestamp(date),
            "symbol": symbol,
            "open": 1000,
            "high": 1050,
            "low": 900,
            "close": 950,
            "source": KRX_DELIST_PRICE_SOURCE,
            "available_at": AVAILABLE,
        }
    ])


def test_consistent_status_events_are_structural_only():
    out = audit_status_event_integrity(
        halts=_halts(),
        cleanup=_cleanup(),
        delistings=_delist(),
        delisted_prices=_prices(),
    )
    assert out["structurally_consistent"] is True
    assert out["planned_vs_actual_delisting_mismatch_symbols"] == 0
    assert out["exact_delisting_economics_ready"] is False
    assert out["judge_security_status_ready"] is False
    assert out["sealed_holdout_authorized"] is False


def test_planned_vs_actual_date_change_is_recorded_not_fabricated_as_contradiction():
    out = audit_status_event_integrity(
        halts=_halts(),
        cleanup=_cleanup(planned="2026-09-17"),
        delistings=_delist(date="2026-09-18"),
        delisted_prices=_prices(date="2026-09-17"),
    )
    assert out["structurally_consistent"] is True
    assert out["planned_vs_actual_delisting_mismatch_symbols"] == 1
    assert out["planned_vs_actual_delisting_mismatch_sample"] == ["000300"]
    assert out["exact_delisting_economics_ready"] is False


def test_cleanup_without_actual_delisting_remains_incomplete_evidence():
    empty_delist = pd.DataFrame(columns=[
        "symbol", "delisting_date", "source", "available_at"
    ])
    empty_prices = pd.DataFrame(columns=[
        "date", "symbol", "open", "high", "low", "close", "source", "available_at"
    ])
    out = audit_status_event_integrity(
        halts=_halts(),
        cleanup=_cleanup(),
        delistings=empty_delist,
        delisted_prices=empty_prices,
    )
    assert out["structurally_consistent"] is True
    assert out["cleanup_without_actual_delisting_symbols"] == 1
    assert out["cleanup_without_actual_delisting_sample"] == ["000300"]
    assert out["exact_delisting_economics_ready"] is False


def test_orphan_delisted_price_symbol_is_rejected():
    with pytest.raises(KRXStatusEventIntegrityError, match="absent from actual delisting"):
        audit_status_event_integrity(
            halts=_halts(),
            cleanup=_cleanup(),
            delistings=_delist(symbol="000300"),
            delisted_prices=_prices(symbol="000660"),
        )


def test_regular_session_price_on_delisting_date_is_rejected():
    with pytest.raises(KRXStatusEventIntegrityError, match="on/after actual delisting"):
        audit_status_event_integrity(
            halts=_halts(),
            cleanup=_cleanup(),
            delistings=_delist(date="2026-09-17"),
            delisted_prices=_prices(date="2026-09-17"),
        )


def test_actual_delisting_on_cleanup_end_is_rejected():
    with pytest.raises(KRXStatusEventIntegrityError, match="must be after cleanup-trading end"):
        audit_status_event_integrity(
            halts=_halts(),
            cleanup=_cleanup(end="2026-09-16", planned="2026-09-17"),
            delistings=_delist(date="2026-09-16"),
            delisted_prices=pd.DataFrame(columns=[
                "date", "symbol", "open", "high", "low", "close", "source", "available_at"
            ]),
        )


def test_unexpected_source_label_is_rejected():
    halts = _halts()
    halts.loc[0, "source"] = "UNOFFICIAL_PROXY"
    with pytest.raises(KRXStatusEventIntegrityError, match="unexpected source"):
        audit_status_event_integrity(
            halts=halts,
            cleanup=_cleanup(),
            delistings=_delist(),
            delisted_prices=_prices(),
        )


def test_naive_availability_lineage_is_rejected():
    cleanup = _cleanup()
    cleanup.loc[0, "available_at"] = pd.Timestamp("2026-09-09T20:00:00")
    with pytest.raises(KRXStatusEventIntegrityError, match="timezone-aware"):
        audit_status_event_integrity(
            halts=_halts(),
            cleanup=cleanup,
            delistings=_delist(),
            delisted_prices=_prices(),
        )


def test_all_frames_are_required_even_if_some_are_empty():
    with pytest.raises(KRXStatusEventIntegrityError, match="all official status frames"):
        audit_status_event_integrity(
            halts=_halts(),
            cleanup=None,
            delistings=_delist(),
            delisted_prices=_prices(),
        )
