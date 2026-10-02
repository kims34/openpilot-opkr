from pathlib import Path

from research_v1_krx_expected_scope_preflight import (
    CONSENT_SENTINEL,
    evaluate_expected_scope_preflight,
)


def _env(tmp_path, *, consent=False):
    out = {
        "KRX_AUTH_KEY": "present",
        "KRX_PRIVATE_RAW_DIR": str((tmp_path / "private").resolve()),
        "INDEXALERT_KRX_HIST_WORKER_ROLE": "DEDICATED_ONE_SHOT",
        "RAILWAY_SERVICE_NAME": "indexalert-krx-historical-worker",
    }
    if consent:
        out["KRX_EXPECTED_SCOPE_ATTESTATION_CONSENT"] = CONSENT_SENTINEL
    return out


def test_expected_scope_preflight_is_network_free_and_blocks_without_separate_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    out = evaluate_expected_scope_preflight(
        environment=_env(tmp_path, consent=False),
        git_worktree=str(worktree),
    )
    assert out["calendar_date_count"] == 4127
    assert out["krx_openapi_auth_key_present"] is True
    assert out["dedicated_worker_service_ok"] is True
    assert out["private_raw_dir_valid"] is True
    assert out["expected_scope_network_execution_authorized"] is False
    assert out["missing_requirements"] == ["EXPLICIT_EXPECTED_SCOPE_ATTESTATION_CONSENT"]
    assert out["network_request_attempted"] is False


def test_exact_expected_scope_consent_can_make_preflight_ready_but_grants_no_other_authority(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    out = evaluate_expected_scope_preflight(
        environment=_env(tmp_path, consent=True),
        git_worktree=str(worktree),
    )
    assert out["expected_scope_network_execution_authorized"] is True
    assert out["missing_requirements"] == []
    assert out["network_request_attempted"] is False
    assert out["source_gate_c_closed"] is False
    assert out["source_gate_d_closed"] is False
    assert out["source_gate_e_closed"] is False
    assert out["feature_performance_testing_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_historical_bulk_consent_does_not_substitute_for_expected_scope_consent(tmp_path):
    env = _env(tmp_path, consent=False)
    env["KRX_HISTORICAL_ACQUISITION_CONSENT"] = "I_AUTHORIZE_INDEXALERT_KRX_HIST_ACQ_v3"
    out = evaluate_expected_scope_preflight(
        environment=env,
        git_worktree=str((tmp_path / "repo").resolve()),
    )
    assert out["expected_scope_network_execution_authorized"] is False
    assert "EXPLICIT_EXPECTED_SCOPE_ATTESTATION_CONSENT" in out["missing_requirements"]


def test_public_runtime_service_is_rejected_even_with_consent(tmp_path):
    worktree = (tmp_path / "repo").resolve()
    worktree.mkdir()
    env = _env(tmp_path, consent=True)
    env["RAILWAY_SERVICE_NAME"] = "indexalert-runtime"
    out = evaluate_expected_scope_preflight(
        environment=env,
        git_worktree=str(worktree),
    )
    assert out["expected_scope_network_execution_authorized"] is False
    assert "DEDICATED_WORKER_SERVICE_ISOLATION" in out["missing_requirements"]
