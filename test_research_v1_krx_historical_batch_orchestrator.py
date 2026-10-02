import pandas as pd

from research_v1_krx_historical_batch_orchestrator import (
    EXECUTION_CONTRACT_ID,
    PLAN_ID,
    build_identity_seed_tasks,
    build_listing_date_master_tasks,
    build_per_security_history_tasks,
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
        counts[row["dataset_identifier"]] = counts.get(row["dataset_identifier"], 0) + 1
        assert row["phase"] == "IDENTITY_SEED"
        assert row["contains_security_identifier"] is False

    assert counts == {
        "stk_isu_base_info": 2,
        "MDCSTAT20001": 12,
        "MDCSTAT23801": 12,
        "MDCSTAT23701_CURRENT_RECONCILIATION": 1,
    }

    cleanup = next(
        row for row in tasks
        if row["dataset_identifier"] == "MDCSTAT23701_CURRENT_RECONCILIATION"
    )
    assert cleanup["request_metadata"] == {"mktId": "ALL"}
    assert "strtDd" not in cleanup["request_metadata"]
    assert "endDd" not in cleanup["request_metadata"]


def test_seed_routes_and_menu_ids_are_frozen():
    tasks = build_identity_seed_tasks()

    masters = [x for x in tasks if x["dataset_identifier"] == "stk_isu_base_info"]
    assert {x["request_metadata"]["basDd"] for x in masters} == {"20150615", "20261001"}
    assert all(x["access_route"] == "KRX_OPENAPI_APPROVED_SERVICE" for x in masters)

    new = [x for x in tasks if x["dataset_identifier"] == "MDCSTAT20001"]
    assert len(new) == 12
    assert all(x["bld"] == "dbms/MDC/STAT/issue/MDCSTAT20001" for x in new)
    assert all(x["menu_id"] == "MDC0201" for x in new)
    assert all(x["method"] == "csv" for x in new)

    dl = [x for x in tasks if x["dataset_identifier"] == "MDCSTAT23801"]
    assert len(dl) == 12
    assert all(x["bld"] == "dbms/MDC/STAT/issue/MDCSTAT23801" for x in dl)
    assert all(x["menu_id"] == "MDC0202" for x in dl)


def test_listing_date_master_tasks_are_unique_bounded_and_identifier_free():
    tasks = build_listing_date_master_tasks(
        ["2015-06-15", "2015-06-15", "2020-01-02", "2010-01-01", "bad"]
    )
    assert len(tasks) == 2
    assert {x["request_metadata"]["basDd"] for x in tasks} == {"20150615", "20200102"}
    assert all(x["phase"] == "IDENTITY_STANDARD_CODE_BINDING" for x in tasks)
    assert all(x["contains_security_identifier"] is False for x in tasks)


def test_per_security_tasks_preserve_standard_code_and_frozen_route_defaults():
    tasks = build_per_security_history_tasks(_episode())
    halt = [x for x in tasks if x["dataset_identifier"] == "MDCSTAT21301"]
    investor = [x for x in tasks if x["dataset_identifier"] == "MDCSTAT02303"]

    assert len(halt) == 6
    assert len(investor) == 12
    assert all(x["contains_security_identifier"] is True for x in tasks)

    for row in halt:
        assert row["request_metadata"]["isuCd"] == "KR7005930003"
        assert row["request_metadata"]["isuCd2"] == "005930"
        assert row["bld"] == "dbms/MDC/STAT/issue/MDCSTAT21301"
        assert row["menu_id"] == "MDC0202"
        start = pd.Timestamp(row["request_metadata"]["strtDd"])
        end = pd.Timestamp(row["request_metadata"]["endDd"])
        assert (end - start).days + 1 <= 730

    for row in investor:
        meta = row["request_metadata"]
        assert meta["isuCd"] == "KR7005930003"
        assert meta["isuCd2"] == ""
        assert meta["inqTpCd"] == "2"
        assert meta["trdVolVal"] == "2"
        assert meta["askBid"] == "3"
        assert meta["detailView"] == "1"
        assert row["bld"] == "dbms/MDC/STAT/standard/MDCSTAT02303"
        assert row["menu_id"] == "MDC0201020302"


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
