import json
from pathlib import Path

import pytest

from research_v1_krx_data_marketplace_terms import (
    KRXTermsAuditError,
    validate_file,
    validate_terms_audit,
)


PATH = Path("INDEXALERT_KRX_DATA_MARKETPLACE_TERMS_AUDIT.json")


def _data():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_committed_terms_audit_is_fail_closed():
    out = validate_file()
    assert out["valid"] is True
    assert out["data_marketplace_authenticated_probe_authorized"] is False
    assert out["bulk_historical_acquisition_authorized"] is False
    assert out["sealed_holdout_authorized"] is False
    assert out["live_trading_authorized"] is False


def test_automation_prohibition_cannot_be_removed():
    data = _data()
    data["clauses"]["unauthorized_automated_collection_reproduction_distribution_prohibited"] = False
    with pytest.raises(KRXTermsAuditError, match="must remain true"):
        validate_terms_audit(data)


def test_account_credentials_cannot_be_reinterpreted_as_permission():
    data = _data()
    data["project_interpretation"]["account_credentials_are_not_automation_permission"] = False
    with pytest.raises(KRXTermsAuditError, match="must remain true"):
        validate_terms_audit(data)


def test_terms_record_cannot_self_authorize_probe_or_live():
    data = _data()
    data["authority"]["data_marketplace_authenticated_probe_authorized"] = True
    with pytest.raises(KRXTermsAuditError, match="illegally true"):
        validate_terms_audit(data)

    data = _data()
    data["authority"]["live_trading_authorized"] = True
    with pytest.raises(KRXTermsAuditError, match="illegally true"):
        validate_terms_audit(data)
