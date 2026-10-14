"""2017 KRX holiday *as-of* reconciliation against historical public snapshots.

The early-July 2017 article transcribes a then-current KRX XLS export's
16 weekdays. Government declared a new 10/02 holiday on 2017-09-05 and
the KRX cash equity market closure was reported in September.
Never replace the historical July snapshot with the later 17-day version
at an earlier decision time (look-ahead leakage). Neither version
authenticates the original KRX private source checkpoint/date receipts.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta

BASE=[
"2017-01-27","2017-01-30","2017-03-01","2017-05-01",
"2017-05-03","2017-05-05","2017-05-09","2017-06-06",
"2017-08-15","2017-10-03","2017-10-04","2017-10-05",
"2017-10-06","2017-10-09","2017-12-25","2017-12-29",
]
HOLIDAY="2017-10-02"
LOCKS={
"original_krx_holiday_export_byte_digest_verified":False,
"original_krx_2017_final_calendar_pit_admitted":False,
"source_2017_private_receipt_dates_matched":False,
"all_184_ambiguous_days_resolved":False,
"27_problem_securities_released":False,
"profitability_run_authorized":False,
"holdout_authorized":False,
"real_orders_authorized":False,
"ordering":"DISABLED",
"new_krx_provider_network_calls":0,
}

def reconcile_2017_public_sources(manifest:dict, worker_2017:dict, *,
                                  decision_at_kst:str)->dict:
    result={"status":"FAIL_CLOSED_INVALID_OR_UNATTESTED_SOURCE_LEADS",
            "published_july_snapshot_count":0,
            "asof_source_calendar_closures_candidate":[],
            "new_2017_10_02_status":"NOT_YET_REPORTED",
            "private_worker_reported_empty_count":None,
            "candidate_count_matches_worker_aggregate":False,
            **LOCKS}
    if not isinstance(manifest,dict) or not isinstance(worker_2017,dict):
        return result
    try:
        july=manifest["archived_july_publication"]
        update=manifest["date_change"]
        after=manifest["after_change_candidate"]
        a=datetime.fromisoformat(july["published_local"])
        decision=datetime.fromisoformat(decision_at_kst)
        govt=datetime.fromisoformat(update["news_report_at_kst"])
        if (a.utcoffset()!=timedelta(hours=9) or decision.utcoffset()!=timedelta(hours=9)
                or govt.utcoffset()!=timedelta(hours=9)
                or a.isoformat()!="2017-07-16T15:45:00+09:00"
                or govt.isoformat()!="2017-09-05T09:31:00+09:00"):
            return result
        if (july["article_url"]!="https://financedata.github.io/posts/pandas-market-days-krx.html"
                or july["original_export_xls_bytes_downloaded_and_SHA_authenticated"] is not False
                or july["table_date_set_count"]!=16
                or july["visible_text_tabled_2017_weekday_closures"]!=BASE
                or july["later_declared_date_missing_at_publication"]!=HOLIDAY
                or update["new_closed_weekday"]!=HOLIDAY
                or update["government_vote_date"]!="2017-09-05"
                or update["exchange_notice_reported_listing_date"]!="2017-09-18"
                or update["original_KRX_notice_bytes_or_first_publication_instant_authenticated"] is not False
                or after["closure_count"]!=17
                or after["weekday_closures"]!=sorted([*BASE,HOLIDAY])
                or after["original_Railway_2017_empty_response_dates_examined"] is not False
                or manifest["all_2017_historical_official_calendar_dates_attested"] is not False
                or manifest["full_KRX_2015_2026_trading_calendar_admitted"] is not False
                or manifest["original_source_publication_pit_attested"] is not False
                or manifest["27_problem_securities_remain_quarantined"] is not True
                or manifest["source_contract_C_D"]!="BLOCKED"
                or manifest["profitability_test_authorized"] is not False
                or manifest["real_orders_authorized"] is not False
                or manifest["ordering"] is not False):
            return result
        if (worker_2017.get("year")!=2017
                or worker_2017.get("verified_weekday_pairs")!=260
                or worker_2017.get("unverified_exchange_calendar_or_source_gap_days")!=17):
            return result
        if len(BASE)!=len(set(BASE)) or HOLIDAY in BASE:
            return result
        for item in [*BASE,HOLIDAY]:
            d=date.fromisoformat(item)
            if d.isoformat()!=item or d.year!=2017 or d.weekday()>=5:
                return result
        result["published_july_snapshot_count"]=16
        result["private_worker_reported_empty_count"]=17
        if decision<a:
            result["status"]="JULY_EXPORT_MIRROR_NOT_YET_AVAILABLE"
            return result
        result["asof_source_calendar_closures_candidate"]=list(BASE)
        result["status"]="JULY_16_SECONDARY_SNAPSHOT_ONLY"
        if decision>=govt:
            result["new_2017_10_02_status"]="GOVERNMENT_HOLIDAY_ANNOUNCED_NOT_KRX_SOURCE_ATTESTED"
            result["status"]="NEW_GOVERNMENT_HOLIDAY_PENDING_EXCHANGE_CONFIRMATION"
        # KRX notice has only a reported DATE, no original first instant.
        # Conservatively require next midnight local after 09/18; do not
        # claim precise official original notice as-of even then.
        if decision.date()>date(2017,9,18):
            result["asof_source_calendar_closures_candidate"]=sorted([*BASE,HOLIDAY])
            result["new_2017_10_02_status"]="EXCHANGE_CLOSURE_REPORTED_SECONDARY_NOT_PRIMARY_KRX_ORIGINAL"
            result["status"]="2017_17_CANDIDATES_AGREE_WITH_PRIVATE_YEARLY_COUNT_ONLY"
            result["candidate_count_matches_worker_aggregate"]=True
        return result
    except (KeyError,ValueError,TypeError,AttributeError,OverflowError):
        return result
