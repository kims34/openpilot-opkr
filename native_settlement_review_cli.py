"""Offline native settlement file review against an existing read-only journal.

Run: python native_settlement_review_cli.py --input REVIEW_INPUT.json --journal EXISTING.sqlite
Input: account_fingerprint, opening/closing {body,captured_at}, history
{pages,request,captured_at}, review_manifest. Pages carry body, request_next_key,
response_cont_yn, response_next_key. No external admission flags are accepted.
Output contains aggregate diagnostic results only; never broker-native proof.
"""
import argparse
import json
import sqlite3

from account_cashflow_reconciliation import require
from account_settlement_binding import SettlementAdmission
from early_live_admission_gate import EarlyLiveAdmissionEvidence
from kiwoom_settlement_history import SettlementHistoryPage
from native_settlement_readiness import assess_native_settlement_readiness
from order_intent_journal import OrderIntentJournal


def _object(pairs):
    result = {}
    for key,value in pairs:
        require(key not in result)
        result[key] = value
    return result


def _reject_nonstandard_constant(_value):
    # Python's JSON decoder accepts NaN/Infinity extensions by default. Native
    # broker evidence must remain strict JSON even when the value is nested in
    # a response field this offline review does not otherwise interpret.
    require(False)


def review_native_settlement_file(input_path, journal_path):
    journal = None
    try:
        with open(input_path,encoding='utf-8') as source:
            try:
                payload = json.load(source, object_pairs_hook=_object,
                                    parse_constant=_reject_nonstandard_constant)
            except RecursionError:
                # Decoder depth exhaustion is invalid input, not a request
                # failure that may log the private file path/client address.
                require(False)
        require(type(payload) is dict and set(payload)=={'account_fingerprint','opening','closing','history','review_manifest'})
        for name in ('opening','closing'):
            require(type(payload[name]) is dict and set(payload[name])=={'body','captured_at'})
        history = payload['history']
        require(type(history) is dict and set(history)=={'pages','request','captured_at'})
        require(type(history['pages']) is list)
        pages = []
        for page in history['pages']:
            require(type(page) is dict and set(page)=={'body','request_next_key','response_cont_yn','response_next_key'})
            pages.append(SettlementHistoryPage(**page))
        journal = OrderIntentJournal.open_readonly(journal_path)
        epoch = journal.shadow_control()['epoch']
        revision = journal.db.execute('SELECT revision FROM reconciliation_barrier WHERE id=1').fetchone()[0]
        report = assess_native_settlement_readiness(EarlyLiveAdmissionEvidence(),SettlementAdmission(),journal,
            opening_body=payload['opening']['body'],closing_body=payload['closing']['body'],
            account_fingerprint=payload['account_fingerprint'],
            opening_captured_at=payload['opening']['captured_at'],closing_captured_at=payload['closing']['captured_at'],
            history_pages=pages,history_request=history['request'],history_captured_at=history['captured_at'],
            reviews=None,review_manifest=payload['review_manifest'],
            expected_epoch=epoch,expected_snapshot_revision=revision)
        report.update(assessment_completed=True,external_admissions_loaded=False,
                      journal_mutation_attempted=False)
        return report
    except (ValueError, TypeError, KeyError, IndexError, sqlite3.Error, OSError):
        return dict(mode='OFFLINE_NATIVE_SETTLEMENT_REVIEW',assessment_completed=False,
            review_errors=['NATIVE_SETTLEMENT_REVIEW_BLOCKED'],external_admissions_loaded=False,
            real_orders_authorized=False,genuine_live_provenance_verified=False,
            broker_request_sent=False,network_request_attempted=False,
            funds_movement_attempted=False,journal_mutation_attempted=False)
    finally:
        if journal is not None: journal.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',required=True)
    parser.add_argument('--journal',required=True)
    args = parser.parse_args(argv)
    report = review_native_settlement_file(args.input,args.journal)
    print(json.dumps(report,sort_keys=True))
    return 0 if report['assessment_completed'] else 2


if __name__ == '__main__': raise SystemExit(main())
