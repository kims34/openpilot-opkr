"""Validate dated *secondary* KRX holiday announcements offline.

Preserves distinct publication concepts:
- news article's independently published timestamp
- alleged KRX original notice publication (UNKNOWN)
- private KRX daily source receipt day (NOT READ)
A newspaper report may be read as a contemporaneous report at/after its own
publication time, but cannot be mistaken for original KRX PIT source evidence.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path

SOURCE_KIND="NEWS_REPORT_ATTRIBUTING_ANNOUNCEMENT_TO_KRX_NOT_PRIMARY_KRX_RELEASE"
AUDIT_LOCKS={
    "original_krx_notice_authenticated":False,
    "original_krx_published_at_confirmed":False,
    "original_krx_session_calendar_attested":False,
    "private_receipt_day_level_matched":False,
    "2015_2026_pit_data_admitted":False,
    "27_quarantined_securities_released":False,
    "m20_performance_authorized":False,
    "real_orders_authorized":False,
    "ordering":"DISABLED",
    "krx_provider_network_calls":0,
}


def validate_report_asof(raw:dict, *, decision_at_kst:str) -> dict:
    out={
        "status":"FAIL_CLOSED_BAD_SECONDARY_CLOSURE_EVIDENCE",
        "secondary_news_asof_candidate_dates":[],
        "secondary_reporting_published_before_event_count":0,
        "news_published_before_decision":False,
        **AUDIT_LOCKS,
    }
    if not isinstance(raw,dict):
        return out
    try:
        if (raw.get("covered_market")!="KOSPI_CASH_EQUITIES"
                or raw.get("krx_own_original_notice_document_retrieved") is not False
                or raw.get("private_volume_date_receipts_examined") is not False
                or raw.get("first_seen_at_krx_verified") is not False
                or raw.get("original_publication_pit_verified") is not False
                or raw.get("provider_source_receipt_day_set_equality_verified") is not False
                or raw.get("source_pit_admitted") is not False
                or raw.get("m20_profitability_authorized") is not False
                or raw.get("quarantine_27_released") is not False
                or raw.get("aggregate_184_unresolved_dates_remaining")!=184
                or raw.get("ordering") is not False):
            return out
        e=raw["contemporaneous_report_source"]
        another=raw["independent_secondary_reporting"]
        earlier=raw["earliest_independently_timestamped_secondary"]
        konex=raw["krx_hosted_different_market_correspondence"]
        if (earlier.get("publisher")!="연합뉴스 Yonhap"
                or earlier.get("article_url")!="https://www.yna.co.kr/amp/view/AKR20260520064200008"
                or earlier.get("article_claim_type")!=SOURCE_KIND
                or earlier.get("krx_original_first_release_instant_proven") is not False
                or earlier.get("source_market_scope")!="KOSPI_CASH_EQUITIES_REPORTED_SECONDARY_ONLY"
                or konex.get("document_url")!="https://kind.krx.co.kr/common/disclsviewer.do?acptNo=20260520000110&docno=&method=searchInitInfo"
                or konex.get("source_market")!="KONEX_NOT_KOSPI"
                or konex.get("notice_date_kst")!="2026-05-20"
                or konex.get("notice_timestamp_precision")!="DATE_ONLY"
                or konex.get("underlying_cited_closed_dates")!=["2026-06-03","2026-07-17"]
                or konex.get("direct_cash_equity_KOSPI_original_notice_authenticated") is not False):
            return out
        if (e.get("claim_type")!=SOURCE_KIND
                or e.get("article_url")!="https://www.newspim.com/news/view/20260520000433"
                or another.get("article_url")!="https://imnews.imbc.com/news/2026/econo/article/6823907_36932.html"
                or another.get("timestamp_precision")!="DATE_ONLY"):
            return out
        published=datetime.fromisoformat(e["article_published_at_kst"])
        updated=datetime.fromisoformat(e["article_last_updated_at_kst"])
        earliest=datetime.fromisoformat(earlier["article_published_at_kst"])
        decision=datetime.fromisoformat(decision_at_kst)
        offset=timedelta(hours=9)
        if (published.utcoffset()!=offset or updated.utcoffset()!=offset
                or earliest.utcoffset()!=offset or decision.utcoffset()!=offset
                or earliest.isoformat()!="2026-05-20T10:34:00+09:00"
                or published.isoformat()!="2026-05-20T10:58:00+09:00"
                or not (earliest<published<=updated)
                or updated.date()>date(2026,10,14)):
            return out
        report_day=date.fromisoformat(another["article_publication_date_kst"])
        if report_day!=date(2026,5,20) or published.date()!=report_day:
            return out
        days=raw["reported_cash_stock_market_closed_dates"]
        if (type(days) is not list or len(days)!=2 or
                days!=["2026-06-03","2026-07-17"] or len(days)!=len(set(days))
                or any(date.fromisoformat(d)<=earliest.date() for d in days)):
            return out
        if decision<earliest:
            out["status"]="SECONDARY_REPORT_NOT_AVAILABLE_AS_OF_DECISION"
            return out
        out.update({
            "status":"CONTEMPORANEOUS_SECONDARY_REPORT_ONLY_NO_KRX_PIT_ADMISSION",
            "secondary_news_asof_candidate_dates":list(days),
            "secondary_reporting_published_before_event_count":len(days),
            "news_published_before_decision":True,
            "earliest_secondary_article_asof_kst":earliest.isoformat(),
            "original_KRX_notice_asof_not_attested":True,
        })
        return out
    except (KeyError,TypeError,ValueError,AttributeError,OverflowError):
        return out
