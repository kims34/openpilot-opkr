"""Cross-check KRX-hosted Dec 2017 market event PDF search-index claims.

Read-only offline metadata, not a PDF parser or original-source authentication.
Preserves KOSPI cash market versus OTC CCP, closure versus delayed opening, and
the incomplete/potentially retrospective publication timestamp. Full source
SHA/PIT remains unverified. No network, brokerage or Railway file operations.
"""
from __future__ import annotations
from datetime import date
from urllib.parse import urlparse

ORIGINAL_PDF="https://www.krx.co.kr/res/pc/banner/2017marketinfo_en.pdf"
BLOG="https://financedata.github.io/posts/pandas-market-days-krx.html"
EXPECTED=(
("2017-12-28","KOSPI_CASH_EQUITIES","FINAL_2017_TRADING_DAY",None),
("2017-12-29","KOSPI_CASH_EQUITIES","YEAR_END_CLOSED",None),
("2018-01-02","KOSPI_CASH_EQUITIES","TRADING_OPEN_DELAYED","10:00"),
)
LOCKED={
"source_kind":"KRX_FIRST_PARTY_WEB_SEARCH_SNIPPET_MARKET_NOTICE_ONLY",
"original_pdf_sha_attested":False,
"original_pdf_first_publication_pit_verified":False,
"complete_year_market_calendar_verified":False,
"2017_original_private_empty_day_receipts_matched":False,
"2015_2026_market_calendar_pit_admitted":False,
"27_securities_released":False,
"m20_performance_authorized":False,
"sealed_holdout_authorized":False,
"real_orders_authorized":False,
"ordering":"DISABLED",
"authenticated_KRX_provider_calls":0,
}
def inspect_official_2017_notice(m:dict,*,july_2017_candidate:list[str])->dict:
    report={"status":"FAIL_CLOSED_INVALID_FIRST_PARTY_PDF_EVIDENCE",
            "listed_2017_cash_close_dates":[],
            "next_year_delayed_open_dates":[],
            "2017_year_end_date_present_in_july_secondary":False,
            **LOCKED}
    if type(m) is not dict or type(july_2017_candidate) is not list:
        return report
    try:
        link=m.get("source_url")
        u=urlparse(link)
        if (link!=ORIGINAL_PDF or u.hostname!="www.krx.co.kr"
                or m.get("source_media_type")!="application/pdf"
                or m.get("source_access_state")!="KRX_HOST_SEARCH_INDEX_TEXT_FOUND_ORIGINAL_PDF_BYTES_NOT_DOWNLOADED"
                or m.get("original_pdf_binary_sha256_attested") is not False
                or m.get("original_pdf_initial_publication_instant_attested") is not False
                or m.get("original_notice_revision_lineage_complete") is not False
                or m.get("second_public_source_july_2017_blog")!=BLOG
                or m.get("krx_original_2017_10_02_first_published_at_verified") is not False
                or m.get("original_2017_private_source_empty_day_receipts_read") is not False
                or m.get("provider_2017_empty_day_count_unchanged")!=17
                or m.get("private_source_184_ambiguous_days_unresolved")!=184
                or m.get("securities_27_quarantined") is not True
                or m.get("market_calendar_2015_2026_pit_verified") is not False
                or m.get("source_C_D_gates")!="BLOCKED"
                or m.get("performance_run_authorized") is not False
                or m.get("sealed_holdout_authorized") is not False
                or m.get("real_orders_authorized") is not False
                or m.get("ordering") is not False):
            return report
        events=m.get("listed_cash_market_events")
        if type(events) is not list or len(events)!=3:
            return report
        for event,want in zip(events,EXPECTED):
            if type(event) is not dict or (
                event.get("date"),event.get("market"),
                event.get("event"),event.get("regular_market_open_kst")
            ) != want:
                return report
            d=date.fromisoformat(event["date"])
            if d.isoformat()!=event["date"] or d.weekday()>=5:
                return report
        if (m.get("july_2017_secondary_calendar_contains_2017_12_29") is not True
                or m.get("july_2017_secondary_calendar_contains_2017_10_02") is not False
                or "2017-12-29" not in july_2017_candidate
                or "2017-10-02" in july_2017_candidate
                or len(july_2017_candidate)!=16 or len(set(july_2017_candidate))!=16):
            return report
        report.update({
            "status":"FIRST_PARTY_KRX_DOMAIN_YEAR_END_EVENT_CORROBORATION_ONLY",
            "listed_2017_cash_close_dates":["2017-12-29"],
            "next_year_delayed_open_dates":["2018-01-02"],
            "2017_year_end_date_present_in_july_secondary":True,
        })
        return report
    except (TypeError,ValueError,AttributeError,OverflowError):
        return report
