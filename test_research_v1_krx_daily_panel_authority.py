from pathlib import Path


SOURCE = Path("research_v1_krx.py")


def test_legacy_krx_daily_panel_cannot_self_grant_judge_or_live_authority():
    text = SOURCE.read_text(encoding="utf-8")

    assert "judge_eligible: bool = False" in text
    assert "source_governance_admission_required: bool = True" in text
    assert "sealed_holdout_authorized: bool = False" in text
    assert "live_trading_authorized: bool = False" in text

    assert "judge_eligible: bool = True" not in text
    assert "This is the Judge-grade path" not in text


def test_pykrx_transport_is_not_mislabeled_as_authenticated_source_admission():
    text = SOURCE.read_text(encoding="utf-8")

    assert 'KRX via authenticated pykrx' not in text
    assert "route not source-gate admitted" in text
    assert "successful retrieval" in text
    assert "never Final-Judge admission" in text
