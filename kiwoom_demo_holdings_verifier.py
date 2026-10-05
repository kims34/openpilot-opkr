"""Explicit DEMO holdings diagnostics; private values never leave memory."""
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
import secrets
import sys
import time

from kiwoom_demo_readonly_transport import KiwoomDemoReadOnlyTransport
from kiwoom_demo_snapshot_collection import collect_demo_holdings_snapshot


def verify_holdings(configuration,*,execute=False,transport_factory=KiwoomDemoReadOnlyTransport):
    report=dict(mode='ISOLATED_DEMO_READ_ONLY_HOLDINGS',status='NOT_REQUESTED',
        request_attempted=False,demo_token_response_validated=False,account_field_present=False,
        snapshot_pages_received=0,holdings_row_count=None,cursor_collection_terminated=False,
        source_account_origin_authenticated=False,snapshot_completeness_attested=False,
        snapshot_freshness_attested=False,trading_date_origin_attested=False,
        automation_ownership_attested=False,available_cash_attested=False,fees_settled=False,
        capital_release_authorized=False,genuine_live_provenance_verified=False,
        project_live_evidence_admitted=False,empirical_execution_blocker_closed=False,
        sealed_holdout_authorized=False,live_trading_authorized=False,orders_requested=False,
        database_or_file_mutation_attempted=False,secrets_or_accounts_emitted=False)
    if not execute:return report
    try:
        transport=transport_factory(configuration)
        report['request_attempted']=True
        report['demo_token_response_validated']=transport.authenticate()['demo_token_response_validated'] is True
        if not report['demo_token_response_validated']:raise ValueError('blocked')
        time.sleep(0.3)
        account=transport.query('ka00001',{}).body.get('acctNo')
        if type(account) is not str or not account.strip() or len(account)>256:raise ValueError('blocked')
        report['account_field_present']=True
        # Ephemeral keyed diagnostic scope. It is never persisted, logged or
        # treated as independently authenticated account or automation ownership.
        fingerprint='sha256:'+hmac.new(secrets.token_bytes(32),
            b'indexalert-kiwoom-account-fingerprint-v1\x00'+account.encode(),hashlib.sha256).hexdigest()
        time.sleep(0.3)
        snapshot=collect_demo_holdings_snapshot(transport,account_fingerprint=fingerprint,
            captured_at=datetime.now(timezone.utc).isoformat())
        report['snapshot_pages_received']=snapshot.page_count
        report['holdings_row_count']=len(snapshot.rows)
        report['cursor_collection_terminated']=True
        report['status']='DEMO_READ_ONLY_HOLDINGS_DIAGNOSTICS_ONLY'
    except Exception:
        report['status']='DEMO_READ_ONLY_HOLDINGS_BLOCKED'
    return report


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    report=verify_holdings(dict(os.environ),execute=args==['--execute-demo-holdings-readonly'])
    print(json.dumps(report,sort_keys=True,separators=(',',':')))
    return 1 if report['status']=='DEMO_READ_ONLY_HOLDINGS_BLOCKED' else 0


if __name__=='__main__':raise SystemExit(main())
