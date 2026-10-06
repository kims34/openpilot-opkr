"""Offline kt00015 history intake, never broker/account/settlement admission.

Retain native direction, currency, costs and dates without interpreting their
codes. A processing timestamp is not a proven settlement instant. Pagination
closure is a structural property, not authenticated whole-account coverage.
No conversion to SettledCashMovement is permitted here until native mapping,
date semantics and complete scope have independent evidence.
"""
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
import re

OFFICIAL_SCHEMA_COMMIT = '953e5dbff123f437ab4d11a78a95191a685eb51f'
ARRAY = 'trst_ovrl_trde_prps_array'
NATIVE_FIELDS = frozenset('''trde_dt trde_no rmrk_nm crd_deal_tp_nm exct_amt
loan_amt_rpya fc_trde_amt fc_exct_amt entra_remn crnc_cd trde_ocr_tp trde_kind_nm
stk_nm trde_amt trde_agri_tax rpy_diffa fc_trde_tax dly_sum fc_entra mdia_tp_nm
io_tp io_tp_nm orig_deal_no stk_cd trde_qty_jwa_cnt cmsn int_ls_usfe fc_cmsn
fc_dly_sum vlbl_nowrm proc_tm isin_cd stex_cd stex_nm trde_unit incm_resi_tax
loan_dt uncl_ocr rpym_sum cntr_dt rcpy_no prcsr proc_brch trde_stle txon_base_pric
tax_sum_cmsn frgn_pay_txam fc_uncl_ocr rpym_sum_fr rcpmnyer trde_prtc_tp'''.split())
REQUIRED_FIELDS = frozenset(('trde_dt','trde_no','exct_amt','entra_remn','crnc_cd',
                            'io_tp','cmsn','trde_agri_tax','tax_sum_cmsn'))
MONEY_FIELDS = ('exct_amt','entra_remn','cmsn','trde_agri_tax','tax_sum_cmsn')


class SettlementHistoryError(ValueError):
    pass


def require(condition):
    if not condition:
        # No account, transaction, source record or cursor in diagnostics.
        raise SettlementHistoryError('SETTLEMENT_HISTORY_INTAKE_BLOCKED')


def native_day(text):
    require(type(text) is str and re.fullmatch(r'[0-9]{8}',text))
    try:
        return date(int(text[:4]),int(text[4:6]),int(text[6:]))
    except ValueError:
        raise SettlementHistoryError('SETTLEMENT_HISTORY_INTAKE_BLOCKED') from None


def native_money(text):
    require(type(text) is str)
    if text == '':
        return None  # Explicit absence, never a fabricated zero.
    require(re.fullmatch(r'[+-]?(?:[0-9]+|[0-9]{1,3}(?:,[0-9]{3})+)(?:\.[0-9]+)?',text))
    try:
        value = Decimal(text.replace(',',''))
    except InvalidOperation:
        raise SettlementHistoryError('SETTLEMENT_HISTORY_INTAKE_BLOCKED') from None
    require(value.is_finite())
    return value


@dataclass(frozen=True)
class SettlementHistoryPage:
    body: dict
    request_next_key: str
    response_cont_yn: str
    response_next_key: str


@dataclass(frozen=True)
class NativeSettlementTransaction:
    native_fields: tuple
    # Exact native numbers; sign/cost inclusion/currency semantics unadmitted.
    money_fields: tuple


@dataclass(frozen=True)
class SettlementHistoryBatch:
    account_fingerprint: str
    captured_at: str
    request_fields: tuple
    records: tuple
    page_count: int
    duplicate_delivery_count: int

    def report(self):
        return dict(mode='OFFLINE_KT00015_HISTORY_INTAKE',source_api='kt00015',
            official_schema_commit=OFFICIAL_SCHEMA_COMMIT,
            page_count=self.page_count,unique_record_count=len(self.records),
            duplicate_delivery_count=self.duplicate_delivery_count,
            page_chain_closed=True,source_account_origin_authenticated=False,
            complete_settlement_scope_attested=False,signed_net_mapping_attested=False,
            fees_tax_completeness_attested=False,trading_date_origin_attested=False,
            account_settlement_admitted=False,genuine_live_provenance_verified=False,
            network_request_attempted=False,broker_request_sent=False,
            real_orders_authorized=False)


def normalize_kt00015_history(pages, *, request, account_fingerprint, captured_at):
    require(type(pages) in (list,tuple) and bool(pages))
    require(type(account_fingerprint) is str and
            re.fullmatch(r'(?:sha256:)?[0-9a-f]{64}',account_fingerprint))
    require(type(captured_at) is str and captured_at.strip()==captured_at)
    try:
        captured=datetime.fromisoformat(captured_at.replace('Z','+00:00'))
    except ValueError:
        raise SettlementHistoryError('SETTLEMENT_HISTORY_INTAKE_BLOCKED') from None
    require(captured.tzinfo is not None and captured.utcoffset() is not None)
    require(type(request) is dict)
    fields={'strt_dt','end_dt','tp','gds_tp','dmst_stex_tp','stk_cd','crnc_cd','frgn_stex_code','qry_sort_tp'}
    require(set(request)==fields and all(type(v) is str for v in request.values()))
    start,end=native_day(request['strt_dt']),native_day(request['end_dt'])
    require(start<=end)
    # Official all-type/all-product/all-venue query; a filtered subset must
    # not masquerade as the history input to whole-account reconciliation.
    require(request['tp']=='0' and request['gds_tp']=='0' and request['dmst_stex_tp']=='%')
    require(all(request[f]=='' for f in ('stk_cd','crnc_cd','frgn_stex_code')))
    require(request['qry_sort_tp'] in ('','1','2'))
    cursor,seen,records,duplicates='',{},[],0
    used_cursors=set()
    for index,page in enumerate(pages):
        require(type(page) is SettlementHistoryPage and type(page.body) is dict)
        require(all(type(v) is str for v in (page.request_next_key,page.response_cont_yn,page.response_next_key)))
        require(page.request_next_key==cursor)
        require(type(page.body.get('return_code')) is int and page.body['return_code']==0)
        material=page.body.get(ARRAY)
        require(type(material) is list)
        for row in material:
            require(type(row) is dict and REQUIRED_FIELDS<=set(row)<=NATIVE_FIELDS)
            require(all(type(v) is str for v in row.values()))
            require(start<=native_day(row['trde_dt'])<=end)
            require(bool(row['trde_no']) and row['trde_no'].strip()==row['trde_no'])
            native=tuple(sorted(row.items()))
            amounts=tuple((field,native_money(row[field])) for field in MONEY_FIELDS)
            key=(row['trde_dt'],row['trde_no'])
            if key in seen:
                require(seen[key]==native)
                duplicates+=1
            else:
                seen[key]=native
                records.append(NativeSettlementTransaction(native,amounts))
        if index==len(pages)-1:
            # Explicit closure required. A ten-page client limit with Y still
            # set is not complete; absent continuation headers are not N.
            require(page.response_cont_yn=='N' and page.response_next_key=='')
        else:
            require(page.response_cont_yn=='Y' and bool(page.response_next_key))
            require(page.response_next_key not in used_cursors)
            used_cursors.add(page.response_next_key)
            cursor=page.response_next_key
    return SettlementHistoryBatch(account_fingerprint,captured_at,tuple(sorted(request.items())),
                                  tuple(records),len(pages),duplicates)
