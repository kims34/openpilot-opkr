"""Five additional frozen-issuer 2024/2025 original Q3 earnings pair diagnostics.

The sixth issuer 005930 already independently passed official original Q3
numeric representation and original-vs-current 2025Q3 API parity. This
standalone program repeats *original* Q3 earnings fact comparability checks
for the other FIVE prespecified cohort members, not selected by returns.

One authorized official corpCode ZIP and one filing index per issuer; two
first-filed original fnlttXbrl ZIPs in memory, discarded. Four calls per
issuer, five separate bounded workflow jobs, never any market or brokerage
route. No earnings values, signs, deltas, IDs, issuer names, ZIPs or keys in
artifacts/logs. Numeric candidate quality may fail for any issuer; never
substitute another account, context, financial figure or altered strategy.

This only tests XBRL representation of a ONE-YEAR quarterly operating-profit
difference. It is not historical original PIT, corporate-action status,
tradeable universe, decision-time market cap, M20 WF, Holdout, or Tiny Live.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path

from research_v1_opendart_lineage_pilot import _official_get
from research_v1_opendart_original_xbrl_pilot import (
    first_q3_original_receipts,_official_xbrl_get,
)
from research_v1_opendart_m20_q3_original_numeric_compat import (
    check_two_original_q3_numbers,OriginalQ3NumberCompatibilityError,
)
from research_v1_opendart_m20_six_issuer_q3_filing_coverage import _registry,COHORT
from research_v1_opendart_m20_vintage_pilot import BEGIN,END

FROZEN_SLOTS=tuple(i for i,code in enumerate(COHORT) if code!="005930")
OUTPUT_ROOT=Path("research_results/opendart_m20_original_extra_issuer_q3_pairs")
MAX_CALLS_PER_SLOT=4

AUTHORITY={
    "historical_issuer_mapping_verified":False,
    "original_statement_table_binding_verified":False,
    "original_filing_historical_publication_pit_verified":False,
    "historical_earnings_restatement_lineage_verified":False,
    "complete_quarter_history_and_universe_verified":False,
    "decision_time_mcap_and_security_status_verified":False,
    "m20_signal_pit_admitted":False,
    "m20_performance_run_authorized":False,
    "independent_holdout_authorized":False,
    "champion_change_authorized":False,
    "real_orders_authorized":False,
    "funds_movement_authorized":False,
    "permissions_change_authorized":False,
    "ordering":"DISABLED",
    "raw_earnings_filing_or_issuer_ids_saved":False,
}


class OriginalSourcePairError(ValueError):
    pass


def check_original_pair_slot(slot:int,session,api_key:str)->dict:
    if type(slot) is not int or slot not in FROZEN_SLOTS:
        raise OriginalSourcePairError("ISSUER_SAMPLE_SCOPE_INVALID")
    if not isinstance(api_key,str) or not api_key.strip():
        raise OriginalSourcePairError("OFFICIAL_OPENDART_KEY_MISSING")
    calls=0
    def official(endpoint,params,*,zip_response=False):
        nonlocal calls
        if endpoint not in ("corpCode.xml","list.json") or calls>=2:
            raise OriginalSourcePairError("OFFICIAL_METADATA_REQUEST_SCOPE_INVALID")
        calls+=1
        return _official_get(session,endpoint,params,zip_response=zip_response)
    lookup=_registry(official("corpCode.xml",{"crtfc_key":api_key},zip_response=True))
    symbol=COHORT[slot]
    corp=lookup.get(symbol)
    if corp is None:
        raise OriginalSourcePairError("EXISTING_REGISTRY_ISSUER_NOT_FOUND")
    listing=official("list.json",{
        "crtfc_key":api_key,"corp_code":corp,
        "bgn_de":BEGIN,"end_de":END,"pblntf_ty":"A","page_count":"100",
    })
    first=first_q3_original_receipts(listing)
    # Four requests in total; both original documents remain in memory only.
    original24=_official_xbrl_get(session,api_key,first["Q_MINUS_4"])
    original25=_official_xbrl_get(session,api_key,first["Q_CURRENT"])
    comparable=check_two_original_q3_numbers(
        original24=original24,original25=original25)
    return {
        "source_status":"ONE_NEW_ISSUER_ORIGINAL_Q3_NUMERIC_REPRESENTATION_SHAPE_ONLY",
        "actual_official_api_calls":4,
        "original_xbrl_reports_fetched":2,
        "same_exact_taxonomy_qname":comparable["same_exact_taxonomy_qname_across_years"],
        "same_declared_decimals_precision":comparable["same_declared_decimals_precision"],
        "same_xbrl_reporter_context":comparable["same_xbrl_context_entity_identifier"],
        "finite_original_difference_possible":comparable["finite_in_memory_numeric_difference_possible"],
        "minimal_original_pair_numeric_representation_consistent":comparable["minimal_original_pair_representation_consistent"],
        "historical_profit_amounts_saved":False,
    }


def run(slot:int,session=None)->dict:
    if type(slot) is not int or slot not in FROZEN_SLOTS:
        return {"source_status":"FAIL_CLOSED_SCOPE_INVALID",**AUTHORITY}
    key=os.environ.get("OPENDART_API_KEY","").strip()
    result={
        "purpose":"M20_ANOTHER_FROZEN_ISSUER_2024_2025_Q3_ORIGINAL_EARNINGS_SHAPE",
        "cohort_slot":slot,
        "cohort_size":len(COHORT),
        "source":"OFFICIAL_OPENDART_ONLY",
        "source_status":"AUTH_NOT_CONFIGURED" if not key else "PENDING",
        "credential_present":bool(key),
        "allowed_official_api_calls":MAX_CALLS_PER_SLOT,
        "actual_official_api_calls":0,
        "original_xbrl_reports_fetched":0,
        **AUTHORITY,
    }
    if not key:
        return result
    if session is None:
        import requests
        session=requests.Session()
    try:
        result.update(check_original_pair_slot(slot,session,key))
    except Exception as err:
        allowed={
            "ISSUER_SAMPLE_SCOPE_INVALID","OFFICIAL_OPENDART_KEY_MISSING",
            "OFFICIAL_METADATA_REQUEST_SCOPE_INVALID",
            "EXISTING_REGISTRY_ISSUER_NOT_FOUND",
            "FIXED_ORIGINAL_YEAR_SCOPE",
            "CONSOLIDATED_CANDIDATE_NOT_UNIQUE",
            "STRUCTURED_XML_TOO_LARGE","UNSAFE_XBRL_DOCUMENT",
            "CONTEXT_ID_AMBIGUOUS","UNIT_ID_AMBIGUOUS",
            "NUMERIC_ACCURACY_UNDECLARED","ORIGINAL_NUMERIC_SHAPE_INVALID",
            "CONSOLIDATED_VALUE_NOT_UNIQUE",
        }
        reason=str(err) if type(err) in (
            OriginalSourcePairError,OriginalQ3NumberCompatibilityError,
        ) else ""
        result["source_status"]="SOURCE_GAP_FAIL_CLOSED"
        result["failure_reason_code"]=reason if reason in allowed else "UNCLASSIFIED"
    return result


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--cohort-slot",type=int,required=True,choices=FROZEN_SLOTS)
    args=parser.parse_args()
    out=run(args.cohort_slot)
    OUTPUT_ROOT.mkdir(parents=True,exist_ok=True)
    dst=OUTPUT_ROOT/f"slot_{args.cohort_slot}.json"
    dst.write_text(json.dumps(out,sort_keys=True,indent=2),encoding="utf-8")
    print("OPENDART_M20_EXTRA_ISSUER_ORIGINAL_PAIR="+json.dumps(out,sort_keys=True),
          flush=True)
