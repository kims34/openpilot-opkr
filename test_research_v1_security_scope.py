import pandas as pd

from research_v1_security_scope import (
    apply_common_like_heuristic,
    common_like_diagnostics,
)


def _panel():
    return pd.DataFrame([
        {"decision_date": "2026-09-01", "symbol": "005930", "name": "삼성전자"},
        {"decision_date": "2026-09-01", "symbol": "005935", "name": "삼성전자우"},
        {"decision_date": "2026-09-01", "symbol": "005387", "name": "현대차2우B"},
        {"decision_date": "2026-09-01", "symbol": "00088K", "name": "한화3우B"},
        {"decision_date": "2026-09-01", "symbol": "1234A0", "name": "가상보통주"},
        {"decision_date": "2026-09-01", "symbol": "432100", "name": "KB스타리츠"},
        # Plain Hangul '우' ending without preferred-looking code: record as a
        # hint, but keep as common-like to avoid false exclusion by name alone.
        {"decision_date": "2026-09-01", "symbol": "111110", "name": "가상동우"},
    ])


def test_common_like_scope_is_conservative_and_auditable():
    x = apply_common_like_heuristic(_panel()).set_index("symbol")

    assert bool(x.loc["005930", "common_like_heuristic"])
    assert not bool(x.loc["005935", "common_like_heuristic"])
    assert not bool(x.loc["005387", "common_like_heuristic"])
    assert not bool(x.loc["00088K", "common_like_heuristic"])
    assert bool(x.loc["1234A0", "common_like_heuristic"])
    assert bool(x.loc["432100", "common_like_heuristic"])

    assert bool(x.loc["111110", "preferred_by_name_plain_u_hint"])
    assert bool(x.loc["111110", "common_like_heuristic"])
    assert not bool(x["security_scope_identity_validated"].any())


def test_scope_diagnostics_do_not_claim_validation():
    tagged = apply_common_like_heuristic(_panel())
    d = common_like_diagnostics(tagged)

    assert d["judge_identity_validated"] is False
    assert d["unique_symbols"] == 7
    assert d["preferred_like_unique_symbols"] == 3
    assert d["common_like_unique_symbols"] == 4
    assert d["plain_u_hint_without_code_unique_symbols"] == 1
