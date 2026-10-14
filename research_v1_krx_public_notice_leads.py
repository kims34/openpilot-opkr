"""Offline review of published year-end holiday source *leads*, not PIT data.

The manifest is an audit trail of public references that may support a
calendar certification in a *different*, independently authenticated process.
Neither listed URL nor its date path constitutes original source bytes or a
first-published-at attestation. No network, private worker volume or trading.
"""
from __future__ import annotations
from datetime import date, timedelta
from urllib.parse import urlparse
import re

TIERS={
    "INSTITUTION_REPLY_RETROSPECTIVE":"www.kofia.or.kr",
    "BROKER_NOTICE_REPORTED":"m.hygood.co.kr",
    "BROKER_NOTICE_REPORTED_2":"m.eugenefn.com",
    "KRX_KIND_HOSTED_MARKET_NOTICE":"kind.krx.co.kr",
    "REPUBLICATION_OF_EXCHANGE_MARKET_NOTICE":"stock.mk.co.kr",
}
# Broker links can be hosted by more than one named broker.
HOSTS={
    "INSTITUTION_REPLY_RETROSPECTIVE":{"www.kofia.or.kr"},
    "BROKER_NOTICE_REPORTED":{"m.hygood.co.kr","m.eugenefn.com","www.samsungpop.com"},
    "KRX_KIND_HOSTED_MARKET_NOTICE":{"kind.krx.co.kr"},
    "REPUBLICATION_OF_EXCHANGE_MARKET_NOTICE":{"stock.mk.co.kr"},
}
PRECISION={"DATE_ONLY","URL_PUBLICATION_DATE_PATH_ONLY","UNKNOWN"}
LOCKS={
    "original_krx_source_document_verified":False,
    "original_notice_first_publication_instant_verified":False,
    "archived_web_page_bytes_hash_verified":False,
    "official_complete_2015_2026_market_calendar_attested":False,
    "krx_raw_provider_empty_day_receipts_date_matched":False,
    "calendar_dates_pit_admitted":0,
    "27_quarantined_securities_released":False,
    "profitability_testing_authorized":False,
    "independent_holdout_authorized":False,
    "real_orders_authorized":False,
    "ordering":"DISABLED",
    "provider_network_requests":0,
}


def _date(s):
    if type(s) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}",s):
        raise ValueError("BAD_DATE")
    d=date.fromisoformat(s)
    if d.isoformat()!=s:
        raise ValueError("BAD_DATE")
    return d


def review_public_year_end_sources(manifest:dict)->dict:
    output={"status":"FAIL_CLOSED_INVALID_PUBLIC_LEADS","recognized_sources":0,
            "krx_kind_hosted_years":[],"retrospective_or_undated_years":[],
            "recorded_holiday_date_candidates":[],"reported_after_2026_10_14":[],
            **LOCKS}
    try:
        if (type(manifest) is not dict
                or manifest.get("market")!="KOSPI_CASH_EQUITIES"
                or manifest.get("observed_184_ambiguous_days_still_unresolved")!=184
                or manifest.get("problem_27_securities_still_quarantined") is not True
                or manifest.get("source_gate_C_D")!="BLOCKED"
                or manifest.get("source_original_binary_document_bytes_downloaded") is not False
                or manifest.get("krx_original_notice_initial_publication_times_attested") is not False
                or manifest.get("underlying_krx_official_full_year_daily_calendar_verified") is not False
                or manifest.get("private_krx_source_receipts_date_level_compared") is not False
                or manifest.get("actual_profitability_backtest_authorized") is not False
                or manifest.get("ordering") is not False):
            return output
        entries=manifest.get("reported_year_end_market_closure_candidates")
        if type(entries) is not list or len(entries)!=6:
            return output
        seen_year=set(); seen_link=set(); dates=[]; primary=[]; retrospective=[]
        for row in entries:
            if type(row) is not dict or type(row.get("year")) is not int:
                return output
            year=row["year"]
            if year in seen_year or not (2015<=year<=2025):
                return output
            seen_year.add(year)
            closure=_date(row.get("closure_date"))
            last=_date(row.get("last_reported_cash_equity_session"))
            if (closure.year!=year or last.year!=year or closure.weekday()>=5
                    or last.weekday()>=5 or not (last<closure)
                    or (closure-last).days>5
                    or closure.month!=12 or last.month!=12):
                return output
            tier=row.get("source_tier")
            url=row.get("reference_url")
            if tier not in HOSTS or type(url) is not str or url in seen_link:
                return output
            parsed=urlparse(url)
            if (parsed.scheme!="https" or parsed.hostname not in HOSTS[tier]
                    or parsed.username or parsed.password):
                return output
            seen_link.add(url)
            precision=row.get("source_time_precision")
            observed=row.get("source_date_kst")
            if precision not in PRECISION or (precision=="UNKNOWN")!=(observed is None):
                return output
            if observed is not None:
                pub_day=_date(observed)
                if pub_day>date(2026,10,14):
                    return output
                if precision=="URL_PUBLICATION_DATE_PATH_ONLY":
                    if tier!="KRX_KIND_HOSTED_MARKET_NOTICE":
                        return output
                    marker="/"+observed.replace("-","/")+"/"
                    if marker not in parsed.path:
                        return output
                if pub_day>=closure:
                    retrospective.append(year)
            else:
                retrospective.append(year)
            if tier=="KRX_KIND_HOSTED_MARKET_NOTICE":
                primary.append(year)
            dates.append(row["closure_date"])
        output.update({
            "status":"DATED_PUBLIC_NOTICE_LEADS_ONLY_NO_OFFICIAL_SESSION_PIT",
            "recognized_sources":len(entries),
            "krx_kind_hosted_years":sorted(primary),
            "retrospective_or_undated_years":sorted(retrospective),
            "recorded_holiday_date_candidates":sorted(dates),
        })
        return output
    except (KeyError,TypeError,ValueError,AttributeError,OverflowError):
        return output
