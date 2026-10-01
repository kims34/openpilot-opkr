import pytest

from research_v1_kiwoom_native_execution import (
    KiwoomNativeExecutionError,
    canonical_event_sha256,
    normalize_realtime_order_fill_event,
)


ACCOUNT_FP = "sha256:" + "a" * 64


def _fill_event():
    return {
        "9201": "1234567890",
        "9203": "0000123456",
        "9001": "005930",
        "912": "JJ",
        "913": "체결",
        "900": "10",
        "901": "70000",
        "902": "6",
        "903": "280040",
        "904": "",
        "905": "+매수",
        "906": "보통",
        "907": "2",
        "908": "091501",
        "909": "FILL-0001",
        "910": "70010",
        "911": "4",
        "914": "70010",
        "915": "4",
        "938": "140",
        "939": "0",
        "919": "",
        "2134": "KRX",
        "2135": "한국거래소",
        "2136": "N",
    }


def test_fill_event_preserves_native_order_and_execution_ids_but_drops_raw_account():
    raw = _fill_event()
    row = normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)

    assert row["broker_order_id"] == raw["9203"]
    assert row["broker_execution_id"] == raw["909"]
    assert row["symbol"] == "005930"
    assert row["fill_qty"] == "4"
    assert row["fee"] == "140"
    assert row["account_fingerprint"] == ACCOUNT_FP
    assert "9201" not in row
    assert raw["9201"] not in row.values()


def test_normalizer_can_never_self_authenticate_project_live_provenance():
    row = normalize_realtime_order_fill_event(
        _fill_event(), account_fingerprint=ACCOUNT_FP
    )
    assert row["broker_native_structure_normalized"] is True
    assert row["genuine_live_provenance_verified"] is False
    assert row["project_live_evidence_admitted"] is False


def test_positive_fill_requires_broker_native_execution_number():
    raw = _fill_event()
    raw["909"] = ""
    with pytest.raises(KiwoomNativeExecutionError, match="execution number"):
        normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)


def test_nonfill_lifecycle_event_may_have_no_execution_number():
    raw = _fill_event()
    raw["913"] = "접수"
    raw["909"] = ""
    raw["910"] = ""
    raw["911"] = ""
    raw["914"] = ""
    raw["915"] = ""
    row = normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)
    assert row["broker_execution_id"] == ""
    assert row["fill_qty"] == ""


def test_raw_account_binding_and_privacy_safe_fingerprint_are_required():
    raw = _fill_event()
    raw["9201"] = ""
    with pytest.raises(KiwoomNativeExecutionError, match="account number"):
        normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)

    with pytest.raises(KiwoomNativeExecutionError, match="account_fingerprint"):
        normalize_realtime_order_fill_event(_fill_event(), account_fingerprint="unsafe")


def test_event_hash_is_deterministic_identity_only():
    raw = _fill_event()
    reordered = dict(reversed(list(raw.items())))
    assert canonical_event_sha256(raw) == canonical_event_sha256(reordered)
    row = normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)
    assert row["raw_event_sha256"] == canonical_event_sha256(raw)
    assert row["genuine_live_provenance_verified"] is False


def test_invalid_numeric_broker_field_fails_closed():
    raw = _fill_event()
    raw["911"] = "four"
    with pytest.raises(KiwoomNativeExecutionError, match="fill_qty"):
        normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)
