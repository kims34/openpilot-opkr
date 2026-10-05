"""Fail-closed normalizer for broker-native Kiwoom account evidence.

Pure/offline: accepts already captured responses only. It performs no network,
order, cancellation, credential or fund action and grants no LIVE authority.
Official field names are pinned to Kiwoom-Securities/Kiwoom-REST-API commit
953e5dbff123f437ab4d11a78a95191a685eb51f.
"""
from decimal import Decimal, InvalidOperation
import hashlib, json, re

OFFICIAL_SCHEMA_COMMIT="953e5dbff123f437ab4d11a78a95191a685eb51f"
ACCOUNT_API="kt00018"
DEPOSIT_API="kt00001"

class SettlementEvidenceError(ValueError): pass

def _req(x, msg="INVALID_SETTLEMENT_EVIDENCE"):
    if not x: raise SettlementEvidenceError(msg)

def _num(v, *, nonnegative=False, integer=False):
    _req(isinstance(v,str) and v.strip()!="")
    try: n=Decimal(v.replace(",",""))
    except InvalidOperation: raise SettlementEvidenceError("INVALID_SETTLEMENT_NUMBER") from None
    _req(n.is_finite())
    if nonnegative: _req(n>=0)
    if integer: _req(n==n.to_integral_value())
    return int(n) if integer else n

def _fingerprint(v):
    _req(isinstance(v,str) and re.fullmatch(r"sha256:[0-9a-f]{64}",v))
    return v

def normalize_account_snapshot(*,account_fingerprint,trading_date,deposit,evaluation):
    """Normalize only fields with official semantics; never infer cash/proceeds."""
    account=_fingerprint(account_fingerprint)
    _req(isinstance(trading_date,str) and re.fullmatch(r"20[0-9]{2}-[0-9]{2}-[0-9]{2}",trading_date))
    _req(isinstance(deposit,dict) and isinstance(evaluation,dict))
    _req(deposit.get("api_id")==DEPOSIT_API and evaluation.get("api_id")==ACCOUNT_API)
    _req(deposit.get("official_schema_commit")==OFFICIAL_SCHEMA_COMMIT)
    _req(evaluation.get("official_schema_commit")==OFFICIAL_SCHEMA_COMMIT)
    _req(deposit.get("account_fingerprint")==account==evaluation.get("account_fingerprint"))
    _req(deposit.get("trading_date")==trading_date==evaluation.get("trading_date"))
    _req(deposit.get("return_code") in (None,0) and evaluation.get("return_code") in (None,0))

    ds=deposit.get("summary"); es=evaluation.get("summary"); positions=evaluation.get("positions")
    _req(isinstance(ds,dict) and isinstance(es,dict) and isinstance(positions,list))

    # Broker-reported cash/settlement values remain distinct. No arithmetic
    # turns D+1/D+2 estimates or sell settlement into immediately reusable cash.
    cash={
      "deposit":str(_num(ds.get("entr"))),
      "orderable":str(_num(ds.get("ord_alow_amt"),nonnegative=True)),
      "withdrawable":str(_num(ds.get("pymn_alow_amt"),nonnegative=True)),
      "d1_estimated_deposit":str(_num(ds.get("d1_entra"))),
      "d1_sell_settlement":str(_num(ds.get("d1_sel_exct_amt"))),
      "d2_estimated_deposit":str(_num(ds.get("d2_entra"))),
      "d2_sell_settlement":str(_num(ds.get("d2_sel_exct_amt"))),
    }
    summary={
      "total_purchase":str(_num(es.get("tot_pur_amt"),nonnegative=True)),
      "total_evaluation":str(_num(es.get("tot_evlt_amt"),nonnegative=True)),
      "estimated_deposit_assets":str(_num(es.get("prsm_dpst_aset_amt"))),
    }
    out=[]
    seen=set()
    for p in positions:
        _req(isinstance(p,dict))
        symbol=p.get("stk_cd"); _req(isinstance(symbol,str) and symbol.strip() and symbol not in seen)
        seen.add(symbol)
        row={
          "symbol":symbol,
          "quantity":_num(p.get("rmnd_qty"),nonnegative=True,integer=True),
          "tradable_quantity":_num(p.get("trde_able_qty"),nonnegative=True,integer=True),
          "purchase_amount":str(_num(p.get("pur_amt"),nonnegative=True)),
          "purchase_fee":str(_num(p.get("pur_cmsn"),nonnegative=True)),
          "evaluation_amount":str(_num(p.get("evlt_amt"),nonnegative=True)),
          "evaluation_sell_fee":str(_num(p.get("sell_cmsn"),nonnegative=True)),
          "tax":str(_num(p.get("tax"),nonnegative=True)),
          "commission_sum":str(_num(p.get("sum_cmsn"),nonnegative=True)),
        }
        _req(row["tradable_quantity"]<=row["quantity"])
        out.append(row)
    payload={"account_fingerprint":account,"trading_date":trading_date,
      "schema_commit":OFFICIAL_SCHEMA_COMMIT,"cash":cash,"summary":summary,
      "positions":sorted(out,key=lambda x:x["symbol"])}
    digest=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return {**payload,"snapshot_sha256":digest,
      "network_request_attempted":False,"broker_request_sent":False,
      "live_ordering_authorized":False,"sale_proceeds_reusable":False,
      "settlement_admitted":False}

def settlement_credit_allowed(snapshot):
    """This layer deliberately cannot grant reusable-capital authority."""
    _req(isinstance(snapshot,dict) and snapshot.get("settlement_admitted") is False)
    return False
