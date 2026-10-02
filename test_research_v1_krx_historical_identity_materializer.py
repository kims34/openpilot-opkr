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


def _normal_master_row(snapshot, standard, symbol, listing, name):
    return {
        "decision_date": pd.Timestamp(snapshot),
        "standard_code": standard,
        "symbol": symbol,
        "name": name,
        "market_type_official": "KOSPI",
        "security_group_official": "주권",
        "stock_type_official": "보통주",
        "listing_date_official": pd.Timestamp(listing),
        "common_stock_identity_official": True,
    }


def _non_overlapping_binding():
    return pd.DataFrame([
        _normal_master_row(
            "2025-01-02",
            "KR7999990000",
            "999999",
            "2025-01-02",
            "별도보통",
        )
    ])


def test_master_snapshot_overlap_is_deduped_only_when_identity_matches():
    seed = pd.DataFrame([
        _normal_master_row(
            "2026-10-01",
            "KR7005930003",
            "005930",
            "1975-06-11",
            "삼성전자",
        )
    ])
    binding = seed.copy()

    out = m._merge_master_snapshots_fail_closed(seed, binding)
    assert len(out) == 1
    assert out.duplicated(["decision_date", "symbol"]).sum() == 0


def test_master_snapshot_overlap_normalizes_equivalent_short_code_representations():
    seed = pd.DataFrame([
        _normal_master_row(
            "2026-10-01",
            "KR7005930003",
            "5930",
            "1975-06-11",
            "삼성전자",
        )
    ])
    binding = pd.DataFrame([
        _normal_master_row(
            "2026-10-01",
            "KR7005930003",
            "005930",
            "1975-06-11",
            "삼성전자",
        )
    ])

    out = m._merge_master_snapshots_fail_closed(seed, binding)
    assert len(out) == 1
    assert out.iloc[0]["symbol"] == "005930"


def test_master_snapshot_overlap_conflict_fails_closed():
    seed = pd.DataFrame([
        _normal_master_row(
            "2026-10-01",
            "KR7005930003",
            "005930",
            "1975-06-11",
            "삼성전자",
        )
    ])
    binding = pd.DataFrame([
        _normal_master_row(
            "2026-10-01",
            "KR7005939999",
            "005930",
            "1975-06-11",
            "삼성전자",
        )
    ])

    with pytest.raises(
        m.KRXHistoricalIdentityMaterializerError,
        match="overlap conflict: standard_code",
    ):
        m._merge_master_snapshots_fail_closed(seed, binding)


def test_duplicate_key_after_short_code_normalization_dedupes_when_identity_matches():
    seed = pd.DataFrame([
        _normal_master_row(
            "2026-10-01",
            "KR7005930003",
            "5930",
            "1975-06-11",
            "삼성전자",
        ),
        _normal_master_row(
            "2026-10-01",
            "KR7005930003",
            "005930",
            "1975-06-11",
            "삼성전자",
        ),
    ])
    binding = _non_overlapping_binding()

    out = m._merge_master_snapshots_fail_closed(seed, binding)
    assert len(out) == 2
    assert out.iloc[0]["symbol"] == "005930"


def test_identity_equivalent_duplicate_rows_inside_one_source_are_deduped():
    row = _normal_master_row(
        "2026-10-01",
        "KR7005930003",
        "005930",
        "1975-06-11",
        "삼성전자",
    )
    seed = pd.DataFrame([row, row])
    binding = _non_overlapping_binding()

    out = m._merge_master_snapshots_fail_closed(seed, binding)
    assert len(out) == 2


def test_conflicting_duplicate_rows_inside_one_source_fail_closed():
    seed = pd.DataFrame([
        _normal_master_row(
            "2026-10-01",
            "KR7005930003",
            "005930",
            "1975-06-11",
            "삼성전자",
        ),
        _normal_master_row(
            "2026-10-01",
            "KR7005939999",
            "005930",
            "1975-06-11",
            "삼성전자",
        ),
    ])
    binding = _non_overlapping_binding()

    with pytest.raises(
        m.KRXHistoricalIdentityMaterializerError,
        match="seed duplicate identity conflict: standard_code",
    ):
        m._merge_master_snapshots_fail_closed(seed, binding)


def test_public_master_code_shape_diagnostic_reports_counts_not_identifiers():
    numeric = _normal_master_row(
        "2026-10-01",
        "KR7005930003",
        "005930",
        "1975-06-11",
        "숫자보통",
    )
    prefixed = _normal_master_row(
        "2026-10-01",
        "KR7005939999",
        "A005930",
        "2026-01-02",
        "접두문자보통",
    )
    suffix = _normal_master_row(
        "2026-10-01",
        "KR7123459999",
        "12345K",
        "2026-01-02",
        "접미문자보통",
    )
    excluded = _normal_master_row(
        "2026-10-01",
        "KR7000088999",
        "00088K",
        "2000-01-03",
        "비보통",
    )
    excluded["common_stock_identity_official"] = False
    excluded["stock_type_official"] = "우선주"

    out = m._public_master_code_shape_counts(
        pd.DataFrame([numeric, prefixed, suffix, excluded])
    )
    assert out["kospi_common_row_count"] == 3
    assert out["raw_symbol_shape_counts"]["numeric_6"] == 1
    assert out["raw_symbol_shape_counts"]["prefix_letter_plus_6_digits"] == 1
    assert out["raw_symbol_shape_counts"]["five_digits_plus_suffix_letter"] == 1
    assert out["old_digit_strip_collision_row_count"] == 2
    assert out["old_digit_strip_conflicting_standard_code_group_count"] == 1
    assert out["identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["network_request_attempted"] is False
    assert "005930" not in str(out)
    assert "A005930" not in str(out)
    assert "12345K" not in str(out)


def test_non_common_alphanumeric_short_code_is_filtered_before_canonicalization():
    common = _normal_master_row(
        "2026-10-01",
        "KR7000088000",
        "000088",
        "2000-01-03",
        "보통주",
    )
    preferred = _normal_master_row(
        "2026-10-01",
        "KR7000088999",
        "00088K",
        "2000-01-03",
        "우선주",
    )
    preferred["stock_type_official"] = "신형우선주"
    preferred["common_stock_identity_official"] = False

    out = m._merge_master_snapshots_fail_closed(
        pd.DataFrame([common, preferred]),
        _non_overlapping_binding(),
    )
    assert set(out["symbol"]) == {"000088", "999999"}
    assert "KR7000088999" not in set(out["standard_code"])


def test_common_stock_alphanumeric_short_code_fails_closed():
    common_bad = _normal_master_row(
        "2026-10-01",
        "KR7000088000",
        "00088K",
        "2000-01-03",
        "잘못된보통주",
    )
    with pytest.raises(
        m.KRXHistoricalIdentityMaterializerError,
        match="seed KOSPI common-stock master has non-numeric short code",
    ):
        m._merge_master_snapshots_fail_closed(
            pd.DataFrame([common_bad]),
            _non_overlapping_binding(),
        )


def test_private_identity_reconstruction_combines_seed_and_listing_date_masters(monkeypatch):
    seed_masters = pd.DataFrame([
        _normal_master_row("2015-06-15", "KR7005930003", "005930", "1975-06-11", "삼성전자"),
        _normal_master_row("2026-10-01", "KR7005930003", "005930", "1975-06-11", "삼성전자"),
        _normal_master_row("2026-10-01", "KR7123450000", "123456", "2020-01-02", "신규보통"),
    ])
    binding = pd.DataFrame([
        _normal_master_row("2020-01-02", "KR7123450000", "123456", "2020-01-02", "신규보통"),
    ])
    new = pd.DataFrame([
        {
            "종목코드": "123456",
            "종목명": "신규보통",
            "시장구분": "유가증권",
            "증권구분": "주권",
            "주식종류": "보통주",
            "상장일": "20200102",
            "상장폐지일": "",
        }
    ])
    delisted = pd.DataFrame(columns=[
        "종목코드", "종목명", "시장구분", "증권구분", "주식종류", "상장일", "폐지일"
    ])
    monkeypatch.setattr(
        m,
        "load_identity_seed_material",
        lambda *a, **k: {
            "security_master_snapshots": seed_masters,
            "new_listing_history": new,
            "delisted_history": delisted,
            "cleanup_current": pd.DataFrame(),
        },
    )
    monkeypatch.setattr(
        m,
        "load_identity_binding_master_snapshots",
        lambda *a, **k: binding,
    )

    out = m.reconstruct_private_historical_episodes("/private")
    assert set(out["short_code"]) == {"005930", "123456"}
    assert out["standard_code"].str.fullmatch(r"[A-Z0-9]{12}").all()
    newer = out[out["short_code"].eq("123456")].iloc[0]
    assert newer["listing_date"] == pd.Timestamp("2020-01-02")
    assert newer["source_new_listing"]
    assert newer["source_end_master_reconciled"]


def test_per_security_private_plan_uses_reconstructed_episode_lifetimes(monkeypatch):
    episodes = pd.DataFrame([
        {
            "episode_key": "KOSPI|005930|1975-06-11",
            "market": "KOSPI",
            "short_code": "005930",
            "standard_code": "KR7005930003",
            "name": "삼성전자",
            "listing_date": pd.Timestamp("1975-06-11"),
            "delisting_date": pd.NaT,
            "coverage_start": pd.Timestamp("2015-06-15"),
            "coverage_end": pd.Timestamp("2026-10-01"),
            "source_start_master": True,
            "source_new_listing": False,
            "source_delisted": False,
            "source_end_master_reconciled": True,
        }
    ])
    monkeypatch.setattr(
        m,
        "reconstruct_private_historical_episodes",
        lambda *a, **k: episodes,
    )
    tasks = m.build_per_security_history_tasks_from_private_identity("/private")
    kinds = [row["request_spec"]["kind"] for row in tasks]
    assert kinds.count("trading_halt") == 6
    assert kinds.count("investor_trading_individual_daily") == 12
    assert len(tasks) == 18


def test_public_historical_identity_summary_never_emits_security_identifiers(monkeypatch):
    episodes = pd.DataFrame([
        {
            "episode_key": "KOSPI|005930|1975-06-11",
            "market": "KOSPI",
            "short_code": "005930",
            "standard_code": "KR7005930003",
            "name": "삼성전자",
            "listing_date": pd.Timestamp("1975-06-11"),
            "delisting_date": pd.NaT,
            "coverage_start": pd.Timestamp("2015-06-15"),
            "coverage_end": pd.Timestamp("2026-10-01"),
            "source_start_master": True,
            "source_new_listing": False,
            "source_delisted": False,
            "source_end_master_reconciled": True,
        }
    ])
    monkeypatch.setattr(
        m,
        "reconstruct_private_historical_episodes",
        lambda *a, **k: episodes,
    )
    out = m.public_historical_identity_summary("/private")
    assert out["episode_count"] == 1
    assert out["per_security_request_count"] == 18
    assert len(out["per_security_task_set_fingerprint_sha256"]) == 64
    assert out["security_identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert "005930" not in str(out)
    assert "KR7005930003" not in str(out)


def test_private_status_economics_tasks_derive_from_cleanup_intervals(monkeypatch):
    episodes = pd.DataFrame([
        {
            "episode_key": "KOSPI|111111|2020-01-02",
            "short_code": "111111",
            "standard_code": "KR7111110000",
            "listing_date": pd.Timestamp("2020-01-02"),
            "delisting_date": pd.Timestamp("2024-06-20"),
            "source_delisted": True,
        },
        {
            "episode_key": "KOSPI|222222|2021-03-04",
            "short_code": "222222",
            "standard_code": "KR7222220000",
            "listing_date": pd.Timestamp("2021-03-04"),
            "delisting_date": pd.Timestamp("2025-07-10"),
            "source_delisted": True,
        },
    ])
    delisted = pd.DataFrame([
        {
            "종목코드": "111111",
            "상장일": "20200102",
            "폐지일": "20240620",
            "정리매매기간_시작일": "20240610",
            "정리매매기간_종료일": "20240618",
        },
        {
            "종목코드": "222222",
            "상장일": "20210304",
            "폐지일": "20250710",
            "정리매매기간_시작일": "",
            "정리매매기간_종료일": "",
        },
    ])
    monkeypatch.setattr(
        m,
        "load_identity_seed_material",
        lambda *a, **k: {
            "security_master_snapshots": pd.DataFrame(),
            "new_listing_history": pd.DataFrame(),
            "delisted_history": delisted,
            "cleanup_current": pd.DataFrame(),
        },
    )
    monkeypatch.setattr(
        m,
        "reconstruct_private_historical_episodes",
        lambda *a, **k: episodes,
    )

    tasks, summary = m.build_status_economics_tasks_from_private_identity("/private")
    assert len(tasks) == 1
    assert tasks[0]["phase"] == "STATUS_ECONOMICS"
    assert tasks[0]["request_spec"]["kind"] == "delisted_stock_price"
    assert summary["delisted_episode_count"] == 2
    assert summary["cleanup_price_task_count"] == 1
    assert summary["delisted_without_cleanup_interval_count"] == 1


def test_public_status_economics_summary_never_claims_exact_fill_economics(monkeypatch):
    task = {
        "plan_id": "INDEXALERT-KRX-HIST-ACQ-v3",
        "execution_contract_id": "INDEXALERT-KRX-HIST-EXEC-v3",
        "phase": "STATUS_ECONOMICS",
        "source_family": "KRX_SECURITY_STATUS",
        "request_spec": {
            "kind": "delisted_stock_price",
            "params": {
                "isuCd": "KR7111110000",
                "strtDd": "20240610",
                "endDd": "20240618",
            },
        },
        "contains_security_identifier": True,
        "task_id": "a" * 64,
    }
    monkeypatch.setattr(
        m,
        "build_status_economics_tasks_from_private_identity",
        lambda *a, **k: (
            [task],
            {
                "delisted_episode_count": 2,
                "cleanup_price_task_count": 1,
                "delisted_without_cleanup_interval_count": 1,
            },
        ),
    )
    out = m.public_status_economics_task_summary("/private")
    assert out["task_count"] == 1
    assert out["exact_status_economics_ready"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    assert out["security_identifiers_emitted"] is False
    assert "111111" not in str(out)
    assert "KR7111110000" not in str(out)
