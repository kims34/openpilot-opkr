"""Private offline kt00018 quantities; no ownership or settlement admission."""
from datetime import datetime
from decimal import Decimal, InvalidOperation
import re


FIELDS=frozenset('''stk_cd stk_nm evltv_prft prft_rt pur_pric pred_close_pric
rmnd_qty trde_able_qty cur_prc pred_buyq pred_sellq tdy_buyq tdy_sellq pur_amt
pur_cmsn evlt_amt sell_cmsn tax sum_cmsn poss_rt crd_tp crd_tp_nm crd_loan_dt'''.split())


class HoldingsDiagnosticError(ValueError):
    pass


def require(condition):
    if not condition:raise HoldingsDiagnosticError('HOLDINGS_DIAGNOSTICS_BLOCKED')


def quantity(value):
    require(type(value) is str and len(value)<=64 and bool(re.fullmatch(r'[0-9]+(?:,[0-9]{3})*',value)))
    result=int(value.replace(',',''))
    require(result<=2**63-1)
    return result


def amount(value):
    require(type(value) is str and len(value)<=64 and bool(re.fullmatch(r'[0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?',value)))
    try:parsed=Decimal(value.replace(',',''))
    except InvalidOperation:raise HoldingsDiagnosticError('HOLDINGS_DIAGNOSTICS_BLOCKED') from None
    require(parsed.is_finite() and parsed>=0)
    return value


class PrivateHoldingsDiagnostic:
    __slots__=('rows','account_fingerprint','captured_at')
    def __init__(self,rows,account_fingerprint,captured_at):
        self.rows,self.account_fingerprint,self.captured_at=rows,account_fingerprint,captured_at
    def __repr__(self):return '<PrivateHoldingsDiagnostic redacted; unadmitted>'
    def report(self):
        return dict(mode='OFFLINE_KIWOOM_HOLDINGS_DIAGNOSTICS',row_count=len(self.rows),
            source_account_origin_authenticated=False,snapshot_completeness_attested=False,
            snapshot_freshness_attested=False,automation_ownership_attested=False,
            available_cash_attested=False,fees_settled=False,capital_release_authorized=False,
            genuine_live_provenance_verified=False,project_live_evidence_admitted=False,
            live_trading_authorized=False,network_request_attempted=False,
            database_or_file_mutation_attempted=False)


def normalize_holdings_rows(rows,*,account_fingerprint,captured_at):
    """Validate declared diagnostic scope and holdings quantities only.

    A kt00018 valuation includes estimates; it cannot establish realized PnL,
    settled sale proceeds, independently owned automation lots or reusable cash.
    Credit/loan lots remain distinct. Never sum their fees into executed costs.
    """
    require(type(account_fingerprint) is str and bool(re.fullmatch(r'sha256:[0-9a-f]{64}',account_fingerprint)))
    require(type(captured_at) is str and len(captured_at)<=64)
    try:stamp=datetime.fromisoformat(captured_at)
    except ValueError:raise HoldingsDiagnosticError('HOLDINGS_DIAGNOSTICS_BLOCKED') from None
    require(stamp.tzinfo is not None and stamp.utcoffset() is not None)
    require(type(rows) is list and len(rows)<=10000)
    output=[];seen=set()
    for row in rows:
        require(type(row) is dict and set(row)<=FIELDS)
        require({'stk_cd','rmnd_qty','trde_able_qty','evlt_amt','crd_tp','crd_loan_dt'}<=set(row))
        require(all(type(v) is str and len(v)<=4096 for v in row.values()))
        symbol=row['stk_cd'];require(bool(symbol.strip()) and len(symbol)<=32)
        lot=(symbol,row['crd_tp'],row['crd_loan_dt']);require(lot not in seen);seen.add(lot)
        held,tradeable=quantity(row['rmnd_qty']),quantity(row['trde_able_qty'])
        require(tradeable<=held)
        output.append(dict(symbol=symbol,credit_type=row['crd_tp'],loan_date=row['crd_loan_dt'],
            held_quantity=held,broker_reported_tradeable_quantity=tradeable,
            reported_valuation_amount=amount(row['evlt_amt'])))
    return PrivateHoldingsDiagnostic(output,account_fingerprint,captured_at)
