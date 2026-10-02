import pandas as pd
import pytest

from research_v1_krx_historical_batch_orchestrator import (
    EXECUTION_CONTRACT_ID,
    PLAN_ID,
    build_identity_seed_tasks,
    build_listing_date_master_tasks,
    build_per_security_history_tasks,
    build_status_economics_tasks,
    public_task_summary,
)


def _episode():
    return pd.DataFrame(
        [
            {
                "episode_key": "KOSPI|005930|1975-06-11",
                "standard_code": "KR7005930003",
                "short_code": "005930",
                "listing_date": pd.Timestamp("1975-06-11"),
                "source_new_listing": False,
                "coverage_start": pd.Timestamp("2015-06-15"),
                "coverage_end": pd.Timestamp("2026-10-01"),
            }
        ]
    )


def test_identity_seed_is_exactly_27_tasks_and_cleanup_is_current_only():
    tasks = build_identity_seed_tasks()
    assert len(tasks) == 27
    assert len({row["task_id"] for row in tasks}) == 27

    counts = {}
    for row in tasks:
        counts[row["request_spec"]["kind"]] = counts.get(row["request_spec"]["kind"], 0) + 1
        assert row["phase"] == "IDENTITY_SEED"
        assert row["contains_security_identifier"] is False

    assert counts == {
        "security_master": 2,
        "new_listing": 12,
        "delisted": 12,
        "cleanup_current_reconciliation": 1,
    }

    cleanup = next(
        row for row in tasks
        if row["request_spec"]["kind"] == "cleanup_current_reconciliation"
    )
    assert cleanup["request_spec"]["params"] == {"mktId": "ALL"}
    assert "strtDd" not in cleanup["request_spec"]["params"]
    assert "endDd" not in cleanup["request_spec"]["params"]


def test_seed_routes_and_menu_ids_are_frozen():
    tasks = build_identity_seed_tasks()

    masters = [x for x in tasks if x["request_spec"]["kind"] == "security_master"]
    assert {x["request_spec"]["params"]["basDd"] for x in masters} == {"20150615", "20261001"}

    new = [x for x in tasks if x["request_spec"]["kind"] == "new_listing"]
    assert len(new) == 12

    dl = [x for x in tasks if x["request_spec"]["kind"] == "delisted"]
    assert len(dl) == 12

    # BLD/menu/defaults are intentionally resolved only by the canonical
    # request executor, not duplicated in the orchestrator.
    for row in new + dl:
        assert set(row) == {
            "plan_id", "execution_contract_id", "phase", "source_family",
            "request_spec", "contains_security_identifier", "task_id",
        }


def test_listing_date_master_tasks_are_unique_bounded_and_identifier_free():
    tasks = build_listing_date_master_tasks(
        ["2015-06-15", "2015-06-15", "2020-01-02", "2010-01-01", "bad"]
    )
    assert len(tasks) == 2
    assert {x["request_spec"]["params"]["basDd"] for x in tasks} == {"20150615", "20200102"}
    assert all(x["phase"] == "IDENTITY_STANDARD_CODE_BINDING" for x in tasks)
    assert all(x["contains_security_identifier"] is False for x in tasks)


def test_per_security_tasks_preserve_standard_code_and_frozen_route_defaults():
    tasks = build_per_security_history_tasks(_episode())
    halt = [x for x in tasks if x["request_spec"]["kind"] == "trading_halt"]
    investor = [x for x in tasks if x["request_spec"]["kind"] == "investor_trading_individual_daily"]

    assert len(halt) == 6
    assert len(investor) == 12
    assert all(x["contains_security_identifier"] is True for x in tasks)

    for row in halt:
        assert row["request_spec"]["params"]["isuCd"] == "KR7005930003"
        assert row["request_spec"]["params"]["isuCd2"] == "005930"
        assert row["request_spec"]["kind"] == "trading_halt"
        start = pd.Timestamp(row["request_spec"]["params"]["strtDd"])
        end = pd.Timestamp(row["request_spec"]["params"]["endDd"])
        assert (end - start).days + 1 <= 730

    for row in investor:
        meta = row["request_spec"]["params"]
        assert meta["isuCd"] == "KR7005930003"
        assert "isuCd2" not in meta
        assert "inqTpCd" not in meta
        assert "trdVolVal" not in meta
        assert "askBid" not in meta
        assert "detailView" not in meta
        assert row["request_spec"]["kind"] == "investor_trading_individual_daily"


def test_public_summary_never_emits_security_identifiers_or_authority():
    tasks = build_identity_seed_tasks() + build_per_security_history_tasks(_episode())
    out = public_task_summary(tasks)
    assert out["plan_id"] == PLAN_ID
    assert out["execution_contract_id"] == EXECUTION_CONTRACT_ID
    assert out["task_count"] == 45
    assert out["security_identifiers_emitted"] is False
    assert out["raw_rows_emitted"] is False
    assert out["network_request_attempted"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False
    rendered = str(out)
    assert "005930" not in rendered
    assert "KR7005930003" not in rendered
    assert len(out["task_set_fingerprint_sha256"]) == 64


def test_orchestrator_is_deterministic_for_same_inputs():
    a = build_identity_seed_tasks()
    b = build_identity_seed_tasks()
    assert a == b
    assert public_task_summary(a) == public_task_summary(b)


def _delisted_episodes_for_economics():
    return pd.DataFrame([
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


def _delisted_history_for_economics():
    return pd.DataFrame([
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


def test_status_economics_tasks_use_only_exact_cleanup_intervals():
    tasks, summary = build_status_economics_tasks(
        _delisted_episodes_for_economics(),
        _delisted_history_for_economics(),
    )
    assert len(tasks) == 1
    task = tasks[0]
    assert task["phase"] == "STATUS_ECONOMICS"
    assert task["source_family"] == "KRX_SECURITY_STATUS"
    assert task["request_spec"]["kind"] == "delisted_stock_price"
    assert task["request_spec"]["params"] == {
        "isuCd": "KR7111110000",
        "strtDd": "20240610",
        "endDd": "20240618",
    }
    assert task["contains_security_identifier"] is True
    assert summary == {
        "delisted_episode_count": 2,
        "cleanup_price_task_count": 1,
        "delisted_without_cleanup_interval_count": 1,
    }


def test_status_economics_partial_cleanup_interval_fails_closed():
    history = _delisted_history_for_economics()
    history.loc[0, "정리매매기간_종료일"] = ""
    with pytest.raises(Exception, match="partial cleanup interval"):
        build_status_economics_tasks(
            _delisted_episodes_for_economics(),
            history,
        )


def test_status_economics_delisting_date_mismatch_fails_closed():
    history = _delisted_history_for_economics()
    history.loc[0, "폐지일"] = "20240621"
    with pytest.raises(Exception, match="delisting date mismatch"):
        build_status_economics_tasks(
            _delisted_episodes_for_economics(),
            history,
        )


def test_status_economics_cleanup_cannot_extend_beyond_delisting():
    history = _delisted_history_for_economics()
    history.loc[0, "정리매매기간_종료일"] = "20240621"
    with pytest.raises(Exception, match="extends beyond delisting"):
        build_status_economics_tasks(
            _delisted_episodes_for_economics(),
            history,
        )
