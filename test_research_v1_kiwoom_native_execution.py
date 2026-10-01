import pytest

from research_v1_kiwoom_native_execution import (
    OFFICIAL_SCHEMA_COMMIT,
    KiwoomNativeExecutionError,
    normalize_ka10076_filled_order,
    normalize_kt00007_order_fill_detail,
    normalize_realtime_order_fill_event,
    privacy_safe_event_sha256,
    reconcile_kiwoom_rest_order_snapshots,
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


def _kt00007_record():
    return {
        "ord_no": "0000123456",
        "stk_cd": "005930",
        "trde_tp": "2",
        "crd_tp": "0",
        "ord_qty": "10",
        "ord_uv": "70000",
        "cnfm_qty": "10",
        "acpt_tp": "접수",
        "rsrv_tp": "",
        "ord_tm": "091500",
        "ori_ord": "",
        "stk_nm": "삼성전자",
        "io_tp_nm": "+매수",
        "loan_dt": "",
        "cntr_qty": "4",
        "cntr_uv": "70010",
        "ord_remnq": "6",
        "comm_ord_tp": "",
        "mdfy_cncl": "",
        "cnfm_tm": "091501",
        "dmst_stex_tp": "KRX",
        "cond_uv": "0",
    }


def _ka10076_record():
    return {
        "ord_no": "0000123456",
        "stk_nm": "삼성전자",
        "io_tp_nm": "+매수",
        "ord_pric": "70000",
        "ord_qty": "10",
        "cntr_pric": "70010",
        "cntr_qty": "4",
        "oso_qty": "6",
        "tdy_trde_cmsn": "140",
        "tdy_trde_tax": "0",
        "ord_stt": "체결",
        "trde_tp": "2",
        "orig_ord_no": "",
        "ord_tm": "091500",
        "stk_cd": "005930",
        "stex_tp": "KRX",
        "stex_tp_txt": "한국거래소",
        "sor_yn": "N",
        "stop_pric": "0",
    }


def test_fill_event_preserves_native_order_and_execution_ids_but_drops_raw_account():
    raw = _fill_event()
    row = normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)

    assert row["broker_order_id"] == raw["9203"]
    assert row["broker_execution_id"] == raw["909"]
    assert row["broker_execution_id_available_in_source"] is True
    assert row["symbol"] == "005930"
    assert row["fill_qty"] == "4"
    assert row["fee"] == "140"
    assert row["account_fingerprint"] == ACCOUNT_FP
    assert row["official_schema_commit"] == OFFICIAL_SCHEMA_COMMIT
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


def test_privacy_safe_event_hash_is_deterministic_and_excludes_raw_account_number():
    raw = _fill_event()
    reordered = dict(reversed(list(raw.items())))
    assert privacy_safe_event_sha256(raw) == privacy_safe_event_sha256(reordered)

    other_account = dict(raw)
    other_account["9201"] = "9999999999"
    assert privacy_safe_event_sha256(raw) == privacy_safe_event_sha256(other_account)

    row = normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)
    assert row["privacy_safe_event_sha256"] == privacy_safe_event_sha256(raw)
    assert "raw_event_sha256" not in row
    assert row["genuine_live_provenance_verified"] is False


def test_invalid_numeric_broker_field_fails_closed():
    raw = _fill_event()
    raw["911"] = "four"
    with pytest.raises(KiwoomNativeExecutionError, match="fill_qty"):
        normalize_realtime_order_fill_event(raw, account_fingerprint=ACCOUNT_FP)


def test_kt00007_snapshot_preserves_order_identity_without_fabricating_execution_id():
    row = normalize_kt00007_order_fill_detail(
        _kt00007_record(), account_fingerprint=ACCOUNT_FP
    )
    assert row["source_api"] == "kt00007"
    assert row["record_granularity"] == "order_aggregate_snapshot"
    assert row["broker_order_id"] == "0000123456"
    assert row["broker_execution_id"] == ""
    assert row["broker_execution_id_available_in_source"] is False
    assert row["fill_qty"] == "4"
    assert row["remaining_qty"] == "6"
    assert row["genuine_live_provenance_verified"] is False
    assert row["project_live_evidence_admitted"] is False


def test_ka10076_snapshot_preserves_fee_tax_status_and_sor_without_fake_fill_id():
    row = normalize_ka10076_filled_order(
        _ka10076_record(), account_fingerprint=ACCOUNT_FP
    )
    assert row["source_api"] == "ka10076"
    assert row["broker_order_id"] == "0000123456"
    assert row["broker_execution_id"] == ""
    assert row["broker_execution_id_available_in_source"] is False
    assert row["fee"] == "140"
    assert row["tax"] == "0"
    assert row["order_status"] == "체결"
    assert row["sor_flag"] == "N"
    assert row["genuine_live_provenance_verified"] is False


def test_matching_kt00007_and_ka10076_snapshots_reconcile_structurally_only():
    kt = normalize_kt00007_order_fill_detail(
        _kt00007_record(), account_fingerprint=ACCOUNT_FP
    )
    ka = normalize_ka10076_filled_order(
        _ka10076_record(), account_fingerprint=ACCOUNT_FP
    )
    result = reconcile_kiwoom_rest_order_snapshots([kt, ka])

    assert result["source_apis"] == ["ka10076", "kt00007"]
    assert result["rest_snapshot_structure_reconciled"] is True
    assert result["rest_snapshot_count"] == 2
    assert result["genuine_live_provenance_verified"] is False
    assert result["project_live_evidence_admitted"] is False


@pytest.mark.parametrize(
    ("field", "bad_value", "expected"),
    [
        ("stk_cd", "000660", "symbol"),
        ("ord_qty", "11", "order_qty"),
        ("cntr_qty", "5", "fill_qty"),
        ("oso_qty", "5", "remaining_qty"),
        ("cntr_pric", "70020", "fill_price"),
    ],
)
def test_rest_snapshot_reconciliation_fails_closed_on_material_mismatch(
    field, bad_value, expected
):
    kt = normalize_kt00007_order_fill_detail(
        _kt00007_record(), account_fingerprint=ACCOUNT_FP
    )
    raw = _ka10076_record()
    raw[field] = bad_value
    ka = normalize_ka10076_filled_order(raw, account_fingerprint=ACCOUNT_FP)

    with pytest.raises(KiwoomNativeExecutionError, match=expected):
        reconcile_kiwoom_rest_order_snapshots([kt, ka])


def test_rest_snapshot_reconciliation_rejects_account_mismatch_and_realtime_rows():
    kt = normalize_kt00007_order_fill_detail(
        _kt00007_record(), account_fingerprint=ACCOUNT_FP
    )
    ka = normalize_ka10076_filled_order(
        _ka10076_record(), account_fingerprint="sha256:" + "b" * 64
    )
    with pytest.raises(KiwoomNativeExecutionError, match="account_fingerprint"):
        reconcile_kiwoom_rest_order_snapshots([kt, ka])

    realtime = normalize_realtime_order_fill_event(
        _fill_event(), account_fingerprint=ACCOUNT_FP
    )
    with pytest.raises(KiwoomNativeExecutionError, match="only kt00007/ka10076"):
        reconcile_kiwoom_rest_order_snapshots([kt, realtime])
