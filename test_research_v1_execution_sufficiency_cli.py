import hashlib
import json
from pathlib import Path

from research_v1_execution_sufficiency_cli import assess_execution_sufficiency_file
from test_research_v1_execution_sufficiency_assessment import _evidence


ROOT = Path(__file__).parent


def test_cli_writes_hash_bound_result_without_authorizing_promotion(tmp_path):
    csv_path = tmp_path / "live.csv"
    out_path = tmp_path / "assessment.json"
    _evidence().to_csv(csv_path, index=False)

    result = assess_execution_sufficiency_file(
        csv_path,
        output_json=out_path,
        protocol_dir=ROOT,
    )
    saved = json.loads(out_path.read_text(encoding="utf-8"))

    assert result == saved
    assert saved["evidence_rows_read"] == 600
    assert saved["evidence_file_sha256"] == hashlib.sha256(csv_path.read_bytes()).hexdigest()
    assert saved["empirical_execution_blocker_closed"] is True
    assert saved["promotion_ready"] is False
    assert saved["sealed_holdout_authorized"] is False
    assert saved["live_trading_authorized"] is False


def test_cli_preserves_failed_sample_gate(tmp_path):
    csv_path = tmp_path / "insufficient.csv"
    _evidence(300).to_csv(csv_path, index=False)

    result = assess_execution_sufficiency_file(csv_path, protocol_dir=ROOT)

    assert result["empirical_execution_blocker_closed"] is False
    assert "minimum_live_observations" in result["failed_gates"]
    assert "minimum_distinct_decision_dates" in result["failed_gates"]
    assert result["promotion_ready"] is False
    assert result["sealed_holdout_authorized"] is False
    assert result["live_trading_authorized"] is False
