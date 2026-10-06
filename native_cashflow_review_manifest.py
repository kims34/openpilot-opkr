"""Import an offline review artifact without manufacturing broker semantics.

Hashes bind reviews to bytes and scope, not authenticity or correctness. No
admission flags may be imported. Net KRW amounts, fees and settled timestamps
must come from an independently reviewed mapping outside this parser.
"""
import hashlib
import json
from decimal import Decimal, InvalidOperation
import re

from account_cashflow_reconciliation import account, instant, require, SettledCashMovement
from kiwoom_settlement_history import SettlementHistoryBatch, NativeSettlementTransaction
from native_cashflow_binding import ReviewedNativeCashflow


def native_row_digest(record):
    require(type(record) is NativeSettlementTransaction)
    encoded = json.dumps(dict(record.native_fields), sort_keys=True,
                         separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def review_money(value):
    require(type(value) is str and re.fullmatch(r'[+-]?[0-9]+(?:\.[0-9]+)?', value))
    try:
        result = Decimal(value)
    except InvalidOperation:
        require(False)
    require(result.is_finite())
    return result


def load_native_cashflow_review_manifest(manifest, batch):
    """Strict v1 account/capture/query/row binding; no defaults for exclusions.

    Each row carries native_row_sha256, disposition and movement. A movement
    uses transaction_id, account_fingerprint, settled_at, net_cash_delta_krw,
    fees_tax_krw. Exclusions carry explicit null. Unknown rows cannot pass.
    """
    require(type(batch) is SettlementHistoryBatch and type(manifest) is dict)
    require(set(manifest) == {'version','account_fingerprint','history_captured_at','history_request','rows'})
    require(type(manifest['version']) is int and manifest['version'] == 1)
    require(account(manifest['account_fingerprint']) == account(batch.account_fingerprint))
    require(manifest['history_captured_at'] == batch.captured_at)
    require(type(manifest['history_request']) is dict and manifest['history_request'] == dict(batch.request_fields))
    require(type(manifest['rows']) is list)
    expected = {native_row_digest(row):row for row in batch.records}
    require(len(expected) == len(batch.records))
    seen, reviews = set(), []
    for row in manifest['rows']:
        require(type(row) is dict and set(row) == {'native_row_sha256','disposition','movement'})
        digest, disposition, mapped = row['native_row_sha256'], row['disposition'], row['movement']
        require(type(digest) is str and digest in expected and digest not in seen)
        require(type(disposition) is str and disposition in ('SETTLED_KRW_NET','NON_CASH','OUTSIDE_WINDOW'))
        seen.add(digest)
        movement = None
        if disposition == 'SETTLED_KRW_NET':
            require(type(mapped) is dict and set(mapped) == {'transaction_id','account_fingerprint',
                'settled_at','net_cash_delta_krw','fees_tax_krw'})
            require(type(mapped['transaction_id']) is str and bool(mapped['transaction_id'])
                    and mapped['transaction_id'].strip() == mapped['transaction_id'])
            require(account(mapped['account_fingerprint']) == account(batch.account_fingerprint))
            instant(mapped['settled_at'])
            net, fees = review_money(mapped['net_cash_delta_krw']), review_money(mapped['fees_tax_krw'])
            require(fees >= 0)
            movement = SettledCashMovement(mapped['transaction_id'],mapped['account_fingerprint'],
                mapped['settled_at'],net,fees)
        else:
            require(mapped is None)
        reviews.append(ReviewedNativeCashflow(expected[digest],disposition,movement))
    require(seen == set(expected))
    return tuple(reviews)
