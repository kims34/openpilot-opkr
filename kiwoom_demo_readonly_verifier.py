"""Isolated manual DEMO-only connectivity probe; emits safe counts only."""
import json
import os
import sys
import time

from kiwoom_demo_readonly_transport import KiwoomDemoReadOnlyTransport


def verify(configuration, *, execute=False, transport_factory=KiwoomDemoReadOnlyTransport):
    report = dict(mode='ISOLATED_DEMO_READ_ONLY_CONNECTIVITY',
        status='NOT_REQUESTED', request_attempted=False,
        demo_token_response_validated=False, account_field_present=False,
        snapshot_pages_received=0, snapshot_row_counts={},
        broker_account_origin_authenticated=False, snapshot_completeness_attested=False,
        trading_date_origin_attested=False, fees_settled=False,
        genuine_live_provenance_verified=False, project_live_evidence_admitted=False,
        empirical_execution_blocker_closed=False, sealed_holdout_authorized=False,
        live_trading_authorized=False, orders_requested=False,
        database_or_file_mutation_attempted=False, secrets_or_accounts_emitted=False)
    if not execute:
        return report
    try:
        transport = transport_factory(configuration)
        # Factory configuration checks finish before any network request.
        report['request_attempted'] = True
        auth = transport.authenticate()
        report['demo_token_response_validated'] = auth['demo_token_response_validated'] is True
        time.sleep(0.3)
        account = transport.query('ka00001', {}).body.get('acctNo')
        report['account_field_present'] = type(account) is str and bool(account.strip())
        if not report['account_field_present']:
            raise ValueError('blocked')
        for api_id, body, table in (
            ('kt00007', dict(qry_tp='1', stk_bond_tp='1', sell_tp='0',
                dmst_stex_tp='KRX', ord_dt='', stk_cd='', fr_ord_no=''), 'acnt_ord_cntr_prps_dtl'),
            ('ka10076', dict(qry_tp='0', sell_tp='0', stex_tp='1', stk_cd='', ord_no=''), 'cntr'),
        ):
            time.sleep(0.3)
            page = transport.query(api_id, body)
            rows = page.body.get(table)
            if type(rows) is not list or any(type(row) is not dict for row in rows):
                raise ValueError('blocked')
            report['snapshot_pages_received'] += 1
            report['snapshot_row_counts'][api_id] = len(rows)
        report['status'] = 'DEMO_READ_ONLY_CONNECTIVITY_ONLY'
    except Exception:
        # Do not expose provider error text or partially returned private data.
        report['status'] = 'DEMO_READ_ONLY_CONNECTIVITY_BLOCKED'
    return report


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    # Exact explicit invocation only; no environment flag or automatic startup.
    report = verify(dict(os.environ), execute=args == ['--execute-demo-readonly'])
    print(json.dumps(report, sort_keys=True, separators=(',', ':')))
    return 0 if report['status'] != 'DEMO_READ_ONLY_CONNECTIVITY_BLOCKED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
