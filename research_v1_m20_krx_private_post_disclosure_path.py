"""Read-only private KRX price/mcap *reachability* after pinned original Q3 dates.

ONE fixed preselected issuer (005930), original Q3 first-filing dates
independently confirmed from official OpenDART 2024-11-14 and 2025-11-14.
Strictly analyze the subsequent 65 calendar days of already privately stored
official KRX KOSPI OpenAPI daily + master raw responses. No KRX network, no
OpenDART network, no new source permissions, and NO model or broker calls.

Outputs ONLY counts and candidate price/mcap availability booleans: no actual
KRX OHLC, issuer identifiers, market caps, calculated returns or private
raw objects. An apparent post-filing marketcap and 21 daily observations
DO NOT prove historical publication PIT, contemporary source availability,
official status/tradability, corp-action-adjusted return path, frozen M20
signal, trade costs, WF/holdout alpha or live readiness.
"""
from __future__ import annotations

from datetime import date,timedelta
from decimal import Decimal
import json
import os
from pathlib import Path
from typing import Any,Callable,Mapping

from research_v1_krx_private_store import (
    read_private_json,read_raw_object,KRXPrivateStoreError,
)
from research_v1_krx_openapi_private_integrity_audit import (
    _trusted_private_root,_check_one,
)
from research_v1_krx_openapi_private_history_batch import (
    _parse,_number,ENDPOINTS,PRIVATE_SUBDIR,WORKER,
)

ORIGINAL_Q3_DATES=(("2024Q3",date(2024,11,14)),
                   ("2025Q3",date(2025,11,14)))
FIXED_CODE="005930"
WINDOW_CALENDAR_DAYS=65
# D decision close, tentative entry at next observed open, tentative D+20
# diagnostic close is 21 observed market sessions including D; this is
# NEVER accepted as an executable frozen strategy timeline.
MIN_OBSERVED_D_TO_DPLUS20=21
AUTHORITY={
    "original_disclosure_pubtime_pit_verified":False,
    "historical_security_master_pit_verified":False,
    "official_security_status_halt_delist_verified":False,
    "corporate_actions_and_true_fill_economics_verified":False,
    "usable_entry_exit_price_path_source_admitted":False,
    "m20_signal_pit_admitted":False,
    "m20_performance_run_authorized":False,
    "independent_holdout_authorized":False,
    "champion_change_authorized":False,
    "real_orders_authorized":False,
    "funds_movement_authorized":False,
    "permissions_change_authorized":False,
    "ordering":"DISABLED",
    "raw_security_rows_or_earnings_saved":False,
    "network_requests_made":False,
    "private_storage_mutated":False,
}


class SourcePathError(ValueError):
    """Fixed reason codes only, never expose provider rows or identifiers."""


def _weekdays_after_filing(filed:date):
    if filed not in {p[1] for p in ORIGINAL_Q3_DATES}:
        raise SourcePathError("UNAPPROVED_FILING_DATE_SCOPE")
    return [
        filed+timedelta(days=step) for step in range(1,WINDOW_CALENDAR_DAYS+1)
        if (filed+timedelta(days=step)).weekday()<5
    ]


def _private_day_state(root:Path,day:date)->dict[str,Any]:
    d=day.strftime("%Y%m%d")
    # Cryptographically authenticate the full original official source pair,
    # including year/day, schema/row count, immutable checksum and KOSPI
    # ordinary-security mapping before inspecting this issuer.
    try:
        _check_one(root,d)
        manifest=read_private_json(root,f"acquisitions/{d}.json")["value"]
        parsed={}
        for service in ("daily_trade","security_master"):
            record=manifest["sources"][service]
            raw=read_raw_object(root,record["raw_sha256"],
                                expected_size=record["raw_byte_length"])
            parsed[service]=_parse(raw,service)[0]
        daily,master=parsed["daily_trade"],parsed["security_master"]
        if not daily:
            return {"kind":"DAILY_EMPTY_CALENDAR_UNVERIFIED"}
        meta=[r for r in master if r.get("ISU_SRT_CD")==FIXED_CODE]
        hits=[r for r in daily if r.get("ISU_CD")==FIXED_CODE]
        if len(meta)!=1 or len(hits)!=1:
            return {"kind":"TARGET_IDENTITY_ABSENT_OR_NOT_UNIQUE"}
        origin=meta[0]
        if (origin.get("SECUGRP_NM")!="주권"
                or origin.get("KIND_STKCERT_TP_NM")!="보통주"
                or origin.get("MKT_TP_NM") not in ("KOSPI","유가증권")):
            return {"kind":"TARGET_EQUITY_CLASS_UNVERIFIED"}
        row=hits[0]
        op,hi,lo,cl=(
            _number(row[name]) for name in
            ("TDD_OPNPRC","TDD_HGPRC","TDD_LWPRC","TDD_CLSPRC")
        )
        volume=_number(row["ACC_TRDVOL"],integer=True)
        value=_number(row["ACC_TRDVAL"],integer=True)
        marketcap=_number(row["MKTCAP"])
        shares=_number(row["LIST_SHRS"],integer=True)
        if (min(op,hi,lo,cl,volume,value,marketcap,shares)<=0
                or not lo<=op<=hi or not lo<=cl<=hi):
            return {"kind":"TARGET_OHLC_OR_MCAP_PATH_INVALID"}
        return {"kind":"VALID_PRICE_MCAP_OBSERVATION","shares_private":shares}
    except (KRXPrivateStoreError,SourcePathError,ValueError,OSError,
            KeyError,TypeError):
        raise SourcePathError("ORIGINAL_PRIVATE_PRICE_SOURCE_UNREADABLE") from None


def _evaluate_period(
    filed:date,*,reader:Callable[[date],Mapping[str,Any]],
)->dict:
    counts={
        "weekday_source_pairs_checked":0,
        "calendar_source_empty_not_holiday_verified":0,
        "target_missing_or_ambiguous_market_days":0,
        "target_invalid_price_mcap_days":0,
        "valid_observed_price_mcap_days":0,
        "observed_share_quantity_changed":False,
        "first_post_filing_positive_mcap_candidate_observed":False,
        "has_at_least_21_tentative_market_price_observations":False,
        "tentative_price_source_path_without_known_target_anomalies":False,
    }
    shares_seen=set()
    for day in _weekdays_after_filing(filed):
        try:
            record=reader(day)
            kind=record["kind"]
        except Exception:
            raise SourcePathError("PRIVATE_DAY_OBSERVATION_UNVERIFIED") from None
        counts["weekday_source_pairs_checked"]+=1
        if kind=="DAILY_EMPTY_CALENDAR_UNVERIFIED":
            counts["calendar_source_empty_not_holiday_verified"]+=1
        elif kind=="VALID_PRICE_MCAP_OBSERVATION":
            share=record.get("shares_private")
            if type(share) is not Decimal or share<=0:
                raise SourcePathError("PRIVATE_SHARE_CONTEXT_INVALID")
            shares_seen.add(share)
            counts["valid_observed_price_mcap_days"]+=1
        elif kind in ("TARGET_IDENTITY_ABSENT_OR_NOT_UNIQUE",
                      "TARGET_EQUITY_CLASS_UNVERIFIED"):
            counts["target_missing_or_ambiguous_market_days"]+=1
        elif kind=="TARGET_OHLC_OR_MCAP_PATH_INVALID":
            counts["target_invalid_price_mcap_days"]+=1
        else:
            raise SourcePathError("UNKNOWN_PRIVATE_OBSERVATION_CLASS")
    n=counts["valid_observed_price_mcap_days"]
    counts["observed_share_quantity_changed"]=len(shares_seen)>1
    counts["first_post_filing_positive_mcap_candidate_observed"]=n>0
    counts["has_at_least_21_tentative_market_price_observations"]=(
        n>=MIN_OBSERVED_D_TO_DPLUS20)
    counts["tentative_price_source_path_without_known_target_anomalies"]=(
        n>=MIN_OBSERVED_D_TO_DPLUS20
        and counts["target_missing_or_ambiguous_market_days"]==0
        and counts["target_invalid_price_mcap_days"]==0
        and not counts["observed_share_quantity_changed"]
    )
    # Do not return shares, dates, prices, cap or raw source security symbols.
    return counts


def run(
    *, execute:bool=False,env:Mapping[str,str]|None=None,
    reader:Callable[[Path,date],Mapping[str,Any]]=_private_day_state,
)->dict:
    out={
        "purpose":"M20_ONE_ISSUER_FIRST_Q3_DISCLOSURE_VS_PRIVATE_KRX_MCAP_PRICE_PATH",
        "source_status":"DRY_RUN_NO_STORAGE_OR_NETWORK",
        "study_period_count":len(ORIGINAL_Q3_DATES),
        "private_source_pairs_examined":0,
        "fixed_historical_decision_publication_times_known":False,
        "stage_results":[],
        **AUTHORITY,
    }
    if not execute:
        return out
    variables=os.environ if env is None else env
    if variables.get("RAILWAY_SERVICE_NAME")!=WORKER:
        out["source_status"]="FAIL_CLOSED_WRONG_SERVICE"
        return out
    private=variables.get("KRX_PRIVATE_RAW_DIR")
    if type(private) is not str or not private.startswith("/data/"):
        out["source_status"]="FAIL_CLOSED_NO_PERSISTENT_PRIVATE_ROOT"
        return out
    try:
        root=_trusted_private_root(Path(private)/PRIVATE_SUBDIR)
        for label,filed in ORIGINAL_Q3_DATES:
            row=_evaluate_period(filed,reader=lambda day:reader(root,day))
            out["stage_results"].append({"q3_original_period":label,**row})
            out["private_source_pairs_examined"]+=row["weekday_source_pairs_checked"]
        out["source_status"]="PRIVATE_KRX_MCAP_PRICE_REACHABILITY_NOT_TRADABLE_NOT_PIT"
    except SourcePathError as ex:
        out["source_status"]="FAIL_CLOSED_PRIVATE_PRICE_PATH_GAP"
        out["failure_code"]=str(ex)
    except Exception:
        out["source_status"]="FAIL_CLOSED_PRIVATE_PRICE_SOURCE_ERROR"
    return out


if __name__=="__main__":
    import argparse
    parser=argparse.ArgumentParser()
    parser.add_argument("--audit",action="store_true")
    args=parser.parse_args()
    out=run(execute=args.audit)
    print("INDEXALERT_M20_KRX_MCAP_PRICE_SOURCE_PROBE="+json.dumps(out,sort_keys=True),
          flush=True)
    if args.audit and out["source_status"]!="PRIVATE_KRX_MCAP_PRICE_REACHABILITY_NOT_TRADABLE_NOT_PIT":
        raise SystemExit(1)
