"""Read-only native input → reviewed cashflow → structural journal assessment.

External reviews and independent gate admissions remain separate requirements.
This entry point does not configure Shadow, enable permissions, create native
evidence, declare final-user readiness, or send broker requests.
"""
from account_cashflow_reconciliation import bind_reconciled_cashflow_to_early_live
from kiwoom_account_settlement_evidence import normalize_kt00001_settlement
from kiwoom_settlement_history import normalize_kt00015_history
from native_cashflow_binding import reconcile_reviewed_native_history
from native_cashflow_review_manifest import load_native_cashflow_review_manifest
from account_cashflow_reconciliation import require


def assess_native_settlement_readiness(base, settlement, journal, *,
        opening_body, closing_body, account_fingerprint,
        opening_captured_at, closing_captured_at,
        history_pages, history_request, history_captured_at, reviews,
        expected_epoch, expected_snapshot_revision,
        complete_settlement_scope_attested=False, signed_net_mapping_attested=False,
        fees_tax_completeness_attested=False, exclusions_attested=False,
        review_manifest=None):
    opening = normalize_kt00001_settlement(opening_body,
        account_fingerprint=account_fingerprint, captured_at=opening_captured_at)
    closing = normalize_kt00001_settlement(closing_body,
        account_fingerprint=account_fingerprint, captured_at=closing_captured_at)
    batch = normalize_kt00015_history(history_pages, request=history_request,
        account_fingerprint=account_fingerprint, captured_at=history_captured_at)
    if review_manifest is not None:
        require(reviews is None)  # Exactly one review input; no fallback/merge.
        reviews = load_native_cashflow_review_manifest(review_manifest, batch)
    cashflow = reconcile_reviewed_native_history(batch, opening, closing, reviews,
        complete_settlement_scope_attested=complete_settlement_scope_attested,
        signed_net_mapping_attested=signed_net_mapping_attested,
        fees_tax_completeness_attested=fees_tax_completeness_attested,
        exclusions_attested=exclusions_attested)
    result = bind_reconciled_cashflow_to_early_live(base, settlement, closing,
        journal, cashflow, expected_epoch=expected_epoch,
        expected_snapshot_revision=expected_snapshot_revision)
    result.update(mode='OFFLINE_NATIVE_SETTLEMENT_READINESS',
        native_history_intake=batch.report(), cashflow_reconciliation=cashflow.report())
    return result
