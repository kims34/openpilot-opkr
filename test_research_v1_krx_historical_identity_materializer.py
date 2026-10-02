import pandas as pd
import pytest

import research_v1_krx_historical_identity_materializer as m


def _new_listing_rows():
    return pd.DataFrame([
        {
            "종목코드": "123456",
            "종목명": "신규보통",
            "시장구분": "유가증권",
            "증권구분": "주권",
            "주식종류": "보통주",
            "상장일": "20200102",
            "상장폐지일": "",
        },
        {
            "종목코드": "654321",
            "종목명": "코스닥",
            "시장구분": "코스닥",
            "증권구분": "주권",
            "주식종류": "보통주",
            "상장일": "20210104",
            "상장폐지일": "",
        },
        {
            "종목코드": "777777",
            "종목명": "우선주",
            "시장구분": "유가증권",
            "증권구분": "주권",
            "주식종류": "우선주",
            "상장일": "20220103",
            "상장폐지일": "",
        },
    ])


def test_binding_tasks_are_derived_only_from_private_seed_history(monkeypatch):
    material = {
        "security_master_snapshots": pd.DataFrame({"x": [1, 2]}),
        "new_listing_history": _new_listing_rows(),
        "delisted_history": pd.DataFrame(),
        "cleanup_current": pd.DataFrame(),
    }
    monkeypatch.setattr(m, "load_identity_seed_material", lambda *a, **k: material)
    tasks = m.build_identity_binding_tasks_from_private_seed("/private")
    assert len(tasks) == 1
    assert tasks[0]["phase"] == "IDENTITY_STANDARD_CODE_BINDING"
    assert tasks[0]["request_spec"]["kind"] == "security_master"
    assert tasks[0]["request_spec"]["params"] == {"basDd": "20200102"}
    assert tasks[0]["contains_security_identifier"] is False


def test_public_seed_summary_emits_counts_and_hashes_only(monkeypatch):
    material = {
        "security_master_snapshots": pd.DataFrame({"x": [1, 2, 3]}),
        "new_listing_history": _new_listing_rows(),
        "delisted_history": pd.DataFrame({"x": [1]}),
        "cleanup_current": pd.DataFrame({"x": [1, 2]}),
    }
    monkeypatch.setattr(m, "load_identity_seed_material", lambda *a, **k: material)
    out = m.public_identity_seed_material_summary("/private")
    assert out["seed_security_master_rows"] == 3
    assert out["seed_new_listing_rows"] == 3
    assert out["seed_delisted_rows"] == 1
    assert out["seed_cleanup_current_rows"] == 2
    assert out["listing_date_master_request_count"] == 1
    assert len(out["listing_date_task_set_fingerprint_sha256"]) == 64
    assert out["identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["network_request_attempted"] is False
    assert "123456" not in str(out)


def test_materializer_requires_timezone_aware_retrieval_timestamp():
    with pytest.raises(
        m.KRXHistoricalIdentityMaterializerError,
        match="timezone-aware",
    ):
        m._timestamp("2026-10-02T10:00:00", "retrieved_at")


def test_completed_seed_material_reassembles_exact_2_12_12_1_shape(monkeypatch):
    expected = []
    kinds = (
        ["security_master"] * 2
        + ["new_listing"] * 12
        + ["delisted"] * 12
        + ["cleanup_current_reconciliation"]
    )
    for idx, kind in enumerate(kinds):
        expected.append({
            "task_id": f"task-{idx}",
            "request_spec": {
                "kind": kind,
                "params": {"basDd": "20150615" if idx == 0 else "20261001"}
                if kind == "security_master"
                else {},
            },
        })

    batch = {
        "tasks": [
            {
                "task_id": row["task_id"],
                "raw_object_sha256": "a" * 64,
                "raw_bytes_size": 1,
                "response_rows": 1,
                "retrieved_at": "2026-10-02T10:00:00+00:00",
            }
            for row in expected
        ]
    }
    monkeypatch.setattr(m, "_load_seed_batch", lambda *a, **k: (batch, expected))
    monkeypatch.setattr(m, "read_raw_object", lambda *a, **k: b"x")

    def fake_parse(kind, raw):
        if kind == "security_master":
            return pd.DataFrame({"dummy": [kind]})
        if kind == "new_listing":
            return pd.DataFrame({
                "종목코드": ["123456"],
                "시장구분": ["코스닥"],
                "증권구분": ["주권"],
                "주식종류": ["보통주"],
                "상장일": ["20200102"],
            })
        if kind == "delisted":
            return pd.DataFrame({
                "종목코드": ["123456"],
                "시장구분": ["코스닥"],
                "증권구분": ["주권"],
                "주식종류": ["보통주"],
                "상장일": ["20200102"],
                "폐지일": ["20220103"],
            })
        return pd.DataFrame({"MKT_ID": ["ALL"]})

    monkeypatch.setattr(m, "_parse_raw", fake_parse)

    def fake_normalise(frame, *, asof_date, available_at):
        return pd.DataFrame({
            "decision_date": [pd.Timestamp(asof_date)],
            "standard_code": ["KR7005930003"],
            "symbol": ["005930"],
            "listing_date_official": [pd.Timestamp("1975-06-11")],
            "common_stock_identity_official": [True],
        })

    monkeypatch.setattr(m, "normalise_basic_info", fake_normalise)

    out = m.load_identity_seed_material("/private")
    assert len(out["security_master_snapshots"]) == 2
    assert len(out["new_listing_history"]) == 12
    assert len(out["delisted_history"]) == 12
    assert len(out["cleanup_current"]) == 1
