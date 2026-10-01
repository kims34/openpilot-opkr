import ast
from pathlib import Path


ROOT = Path(__file__).resolve().parent
KIWOOM = (ROOT / "research_v1_kiwoom_native_execution.py").read_text(encoding="utf-8")
PROMOTION_AUDIT = (ROOT / "research_v1_promotion_audit.py").read_text(encoding="utf-8")
PROMOTION_REPORT = (ROOT / "research_v1_promotion_report.py").read_text(encoding="utf-8")


FORBIDDEN_NETWORK_IMPORT_ROOTS = {
    "requests",
    "httpx",
    "aiohttp",
    "socket",
    "websocket",
    "websockets",
    "urllib",
    "subprocess",
}


def _import_roots(source: str) -> set[str]:
    tree = ast.parse(source)
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".", 1)[0])
    return roots


def _function_names(source: str) -> set[str]:
    tree = ast.parse(source)
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def test_kiwoom_native_normalizer_remains_offline_and_secret_agnostic():
    imports = _import_roots(KIWOOM)
    assert not (imports & FORBIDDEN_NETWORK_IMPORT_ROOTS)

    lowered = KIWOOM.lower()
    for marker in (
        "https://",
        "http://",
        "mockapi.kiwoom.com",
        "api.kiwoom.com",
        "/oauth2/token",
        "kiwoom_app_key",
        "kiwoom_app_secret",
    ):
        assert marker not in lowered


def test_kiwoom_native_normalizer_exposes_no_order_capable_function():
    names = {name.lower() for name in _function_names(KIWOOM)}
    forbidden_fragments = (
        "submit_order",
        "create_order",
        "place_order",
        "send_order",
        "amend_order",
        "modify_order",
        "cancel_order",
    )
    for name in names:
        assert not any(fragment in name for fragment in forbidden_fragments)


def test_promotion_consumers_do_not_depend_on_kiwoom_demo_or_reconciliation_state():
    combined = (PROMOTION_AUDIT + "\n" + PROMOTION_REPORT).lower()
    for marker in (
        "kiwoom",
        "indexalert_kiwoom_demo_connectivity_evidence",
        "token_ok",
        "account_ok",
        "balance_ok",
        "fills_ok",
        "rest_snapshot_structure_reconciled",
        "genuine_live_provenance_verified",
    ):
        assert marker not in combined


def test_promotion_consumers_remain_explicitly_non_production_authority():
    assert '"production_promotion_allowed": False' in PROMOTION_AUDIT
    assert '"production_promotion_allowed": False' in PROMOTION_REPORT
    assert "sealed holdout" in PROMOTION_AUDIT.lower()
    assert "prospective shadow" in PROMOTION_AUDIT.lower()
    assert "sealed holdout" in PROMOTION_REPORT.lower()
    assert "prospective shadow" in PROMOTION_REPORT.lower()
