from pathlib import Path

from research_v1_krx_historical_acquisition_preflight import (
    CONSENT_SENTINEL,
    evaluate_historical_acquisition_preflight,
)


def _safe_root(tmp_path: Path) -> str:
    return str((tmp_path / "private-krx").resolve())


def test_bulk_preflight_blocks_without_storage_and_exact_execution_consent(tmp_path):
    out=evaluate_historical_acquisition_preflight(
        environment={"KRX_ID":"present","KRX_PW":"present","KRX_AUTH_KEY":"present","INDEXALERT_KRX_HIST_WORKER_ROLE":"DEDICATED_ONE_SHOT"},
        git_worktree=(tmp_path / "repo").resolve(),
    )
    assert out["rights_authorized"] is True
    assert out["private_persistent_storage_required"] is True
    assert out["private_raw_dir_configured"] is False
    assert out["historical_acquisition_network_execution_authorized"] is False
    assert out["network_request_attempted"] is False
    assert out["missing_requirements"] == [
        "KRX_PRIVATE_RAW_DIR",
        "EXPLICIT_HISTORICAL_ACQUISITION_EXECUTION_CONSENT",
    ]
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_bulk_preflight_becomes_ready_only_for_safe_storage_and_exact_sentinel(tmp_path):
    worktree=(tmp_path / "repo").resolve()
    worktree.mkdir()
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_AUTH_KEY":"present",
            "KRX_PRIVATE_RAW_DIR":_safe_root(tmp_path),
            "INDEXALERT_KRX_HIST_WORKER_ROLE":"DEDICATED_ONE_SHOT",
            "KRX_HISTORICAL_ACQUISITION_CONSENT":CONSENT_SENTINEL,
        },
        git_worktree=worktree,
    )
    assert out["execution_contract_id"] == "INDEXALERT-KRX-HIST-EXEC-v3"
    assert out["private_raw_dir_configured"] is True
    assert out["private_raw_dir_valid"] is True
    assert out["historical_acquisition_network_execution_authorized"] is True
    assert out["network_request_attempted"] is False
    assert out["missing_requirements"] == []


def test_bulk_preflight_rejects_near_miss_consent(tmp_path):
    worktree=(tmp_path / "repo").resolve()
    worktree.mkdir()
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_AUTH_KEY":"present",
            "KRX_PRIVATE_RAW_DIR":_safe_root(tmp_path),
            "INDEXALERT_KRX_HIST_WORKER_ROLE":"DEDICATED_ONE_SHOT",
            "KRX_HISTORICAL_ACQUISITION_CONSENT":"yes",
        },
        git_worktree=worktree,
    )
    assert out["historical_acquisition_network_execution_authorized"] is False
    assert "EXPLICIT_HISTORICAL_ACQUISITION_EXECUTION_CONSENT" in out["missing_requirements"]


def test_bulk_preflight_rejects_raw_root_inside_git_worktree(tmp_path):
    worktree=(tmp_path / "repo").resolve()
    worktree.mkdir()
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_AUTH_KEY":"present",
            "KRX_PRIVATE_RAW_DIR":str((worktree / "raw").resolve()),
            "KRX_HISTORICAL_ACQUISITION_CONSENT":CONSENT_SENTINEL,
        },
        git_worktree=worktree,
    )
    assert out["private_raw_dir_valid"] is False
    assert "SAFE_KRX_PRIVATE_RAW_DIR" in out["missing_requirements"]
    assert "outside the git worktree" in out["private_raw_dir_error"]
    assert out["historical_acquisition_network_execution_authorized"] is False


def test_bulk_preflight_rejects_public_static_raw_root(tmp_path):
    worktree=(tmp_path / "repo").resolve()
    worktree.mkdir()
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_AUTH_KEY":"present",
            "KRX_PRIVATE_RAW_DIR":str((tmp_path / "public" / "krx").resolve()),
            "KRX_HISTORICAL_ACQUISITION_CONSENT":CONSENT_SENTINEL,
        },
        git_worktree=worktree,
    )
    assert out["private_raw_dir_valid"] is False
    assert "SAFE_KRX_PRIVATE_RAW_DIR" in out["missing_requirements"]
    assert "public/static" in out["private_raw_dir_error"]


def test_bulk_preflight_requires_openapi_key_for_identity_seed(tmp_path):
    worktree=(tmp_path / "repo").resolve()
    worktree.mkdir()
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_PRIVATE_RAW_DIR":_safe_root(tmp_path),
            "INDEXALERT_KRX_HIST_WORKER_ROLE":"DEDICATED_ONE_SHOT",
            "KRX_HISTORICAL_ACQUISITION_CONSENT":CONSENT_SENTINEL,
        },
        git_worktree=worktree,
    )
    assert out["krx_openapi_auth_key_present"] is False
    assert "KRX_AUTH_KEY" in out["missing_requirements"]
    assert out["historical_acquisition_network_execution_authorized"] is False


def test_bulk_preflight_rejects_public_runtime_even_with_safe_volume_and_consent(tmp_path):
    worktree=(tmp_path / "repo").resolve()
    worktree.mkdir()
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_AUTH_KEY":"present",
            "KRX_PRIVATE_RAW_DIR":_safe_root(tmp_path),
            "KRX_HISTORICAL_ACQUISITION_CONSENT":CONSENT_SENTINEL,
            "INDEXALERT_KRX_HIST_WORKER_ROLE":"DEDICATED_ONE_SHOT",
            "RAILWAY_SERVICE_NAME":"indexalert-runtime",
        },
        git_worktree=worktree,
    )
    assert out["forbidden_public_service"] is True
    assert out["dedicated_worker_isolation_ok"] is False
    assert "DEDICATED_WORKER_SERVICE_ISOLATION" in out["missing_requirements"]
    assert out["historical_acquisition_network_execution_authorized"] is False


def test_bulk_preflight_requires_exact_dedicated_worker_role(tmp_path):
    worktree=(tmp_path / "repo").resolve()
    worktree.mkdir()
    out=evaluate_historical_acquisition_preflight(
        environment={
            "KRX_ID":"present",
            "KRX_PW":"present",
            "KRX_AUTH_KEY":"present",
            "KRX_PRIVATE_RAW_DIR":_safe_root(tmp_path),
            "KRX_HISTORICAL_ACQUISITION_CONSENT":CONSENT_SENTINEL,
            "INDEXALERT_KRX_HIST_WORKER_ROLE":"WEB",
        },
        git_worktree=worktree,
    )
    assert out["dedicated_worker_role_present"] is False
    assert "DEDICATED_ONE_SHOT_WORKER_ROLE" in out["missing_requirements"]
    assert out["historical_acquisition_network_execution_authorized"] is False
