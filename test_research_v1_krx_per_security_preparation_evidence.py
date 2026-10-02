import json
from pathlib import Path

import pytest

from research_v1_krx_per_security_preparation_evidence import (
    KRXPerSecurityPreparationEvidenceError,
    validate_evidence,
    validate_file,
)

PATH = Path("INDEXALERT_KRX_PER_SECURITY_HISTORY_PREPARATION_EVIDENCE.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_per_security_preparation_is_frozen_and_network_free():
    out = validate_file()
    assert out["valid"] is True
    assert out["task_count"] == 14296
    assert out["investor_task_count"] == 9485
    assert out["halt_task_count"] == 4811
    assert out["network_request_attempted"] is False
    assert out["execution_authorized"] is False


def test_preparation_rejects_count_or_hash_drift():
    data = _data()
    data["preparation"]["task_count"] = 14295
    with pytest.raises(KRXPerSecurityPreparationEvidenceError, match="task count drift"):
        validate_evidence(data)

    data = _data()
    data["preparation"]["task_set_fingerprint_sha256"] = "0" * 64
    with pytest.raises(KRXPerSecurityPreparationEvidenceError, match="task-set fingerprint drift"):
        validate_evidence(data)


def test_preparation_rejects_network_or_authority_escalation():
    data = _data()
    data["preparation"]["network_request_attempted"] = True
    with pytest.raises(KRXPerSecurityPreparationEvidenceError, match="attempted network"):
        validate_evidence(data)

    data = _data()
    data["authority"]["sealed_holdout_authorized"] = True
    with pytest.raises(KRXPerSecurityPreparationEvidenceError, match="illegally true"):
        validate_evidence(data)


def test_preparation_rejects_identity_guard_relaxation():
    data = _data()
    data["identity_boundary"]["lookahead_backfill_used"] = True
    with pytest.raises(KRXPerSecurityPreparationEvidenceError, match="lookahead"):
        validate_evidence(data)
