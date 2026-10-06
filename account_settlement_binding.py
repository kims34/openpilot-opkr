from dataclasses import dataclass
from early_live_admission_gate import EarlyLiveAdmissionEvidence, assess_early_live_readiness
class SettlementBindingError(ValueError): pass
@dataclass(frozen=True)
class SettlementAdmission:
    source_account_origin_authenticated: bool=False
    snapshot_freshness_attested: bool=False
    trading_date_origin_attested: bool=False
    settlement_fields_verified: bool=False
    unresolved_reconciliation_count: int=0
def settlement_admitted(e):
    if type(e) is not SettlementAdmission: raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    flags=(e.source_account_origin_authenticated,e.snapshot_freshness_attested,e.trading_date_origin_attested,e.settlement_fields_verified)
    if any(type(v) is not bool for v in flags): raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    if type(e.unresolved_reconciliation_count) is not int or e.unresolved_reconciliation_count<0: raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    return all(flags) and e.unresolved_reconciliation_count==0
def bind_settlement_to_early_live(base,settlement):
    if type(base) is not EarlyLiveAdmissionEvidence: raise SettlementBindingError("SETTLEMENT_BINDING_BLOCKED")
    admitted=settlement_admitted(settlement); fields=dict(base.__dict__); fields["account_settlement_tested"]=admitted
    out=assess_early_live_readiness(EarlyLiveAdmissionEvidence(**fields)); out["account_settlement_admitted"]=admitted
    out["real_orders_authorized"]=False; out["early_live_authorized"]=False
    return out
