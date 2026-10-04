import json

import pandas as pd
import pytest

from research_v1_krx_historical_fetchers import (
    CSV_URL,
    JSON_URL,
    KRXHistoricalFetchError,
    OTP_URL,
    fetch_data_marketplace_raw,
    fetch_openapi_raw,
    parse_data_marketplace_raw,
    parse_openapi_raw,
    resolve_pinned_endpoint_request,
)


class Resp:
    def __init__(self, *, status=200, content=b""):
        self.status_code = status
        self.content = content
        self.ok = 200 <= status < 300

    @property
    def text(self):
        return self.content.decode("utf-8", errors="replace")


class Session:
    def __init__(self, posts=None, gets=None):
        self.posts = list(posts or [])
        self.gets = list(gets or [])
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append(("POST", url, kwargs))
        return self.posts.pop(0)

    def get(self, url, **kwargs):
        self.calls.append(("GET", url, kwargs))
        return self.gets.pop(0)


def test_csv_parser_accepts_official_utf8_fallback_without_mutating_bytes():
    raw = "종목코드,종목명\n005930,삼성전자\n".encode("utf-8")
    frame = fetchers.parse_data_marketplace_raw("csv", raw)
    assert list(frame.columns) == ["종목코드", "종목명"]
    assert frame.iloc[0]["종목명"] == "삼성전자"


def test_adapter_blocks_before_any_network_when_not_authorized():
    s = Session()
    with pytest.raises(KRXHistoricalFetchError, match="preflight authorization required"):
        fetch_data_marketplace_raw(
            method="json",
            bld="dbms/MDC/STAT/issue/MDCSTAT21301",
            params={"isuCd":"KR7005930003"},
            menu_id="MDC0202",
            network_authorized=False,
            session=s,
        )
    assert s.calls == []


def test_csv_adapter_preserves_exact_raw_bytes_and_parses_frame():
    raw = "일자,개인\n20260921,100\n".encode("euc-kr")
    s = Session(posts=[Resp(content=b"OTP123"), Resp(content=raw)])
    out = fetch_data_marketplace_raw(
        method="csv",
        bld="dbms/MDC/STAT/standard/MDCSTAT02303",
        params={"isuCd":"KR7005930003","strtDd":"20260921","endDd":"20260921"},
        menu_id="MDC0201020302",
        network_authorized=True,
        session=s,
        retrieved_at_override="2026-10-02T10:00:00+00:00",
    )
    assert out.raw_bytes == raw
    assert out.response_frame.to_dict("records") == [{"일자":20260921,"개인":100}]
    assert out.transport_status == "HTTP_200_CSV"
    assert out.network_request_attempted is True
    assert [x[1] for x in s.calls] == [OTP_URL, CSV_URL]


def test_json_adapter_preserves_exact_raw_bytes_and_schema():
    payload={"CURRENT_DATETIME":"20261002190000","output":[{"ISU_CD":"KR7000300004","TRD_HALT_DD":"20240101"}]}
    raw=json.dumps(payload,ensure_ascii=False,separators=(",",":")).encode("utf-8")
    s=Session(posts=[Resp(content=raw)])
    out=fetch_data_marketplace_raw(
        method="json",
        bld="dbms/MDC/STAT/issue/MDCSTAT21301",
        params={"isuCd":"KR7000300004","isuCd2":"000300","strtDd":"20240101","endDd":"20241231"},
        menu_id="MDC0202",
        network_authorized=True,
        session=s,
        retrieved_at_override="2026-10-02T10:00:00+00:00",
    )
    assert out.raw_bytes == raw
    assert list(out.response_frame.columns) == ["ISU_CD","TRD_HALT_DD"]
    assert out.response_frame.attrs["current_datetime"] == "20261002190000"
    assert out.transport_status == "HTTP_200_JSON"
    assert s.calls[0][1] == JSON_URL


def test_injected_session_logout_fails_without_hidden_relogin():
    s=Session(posts=[Resp(status=400,content=b"LOGOUT")])
    with pytest.raises(KRXHistoricalFetchError, match="KRX_AUTH_SESSION_LOGOUT"):
        fetch_data_marketplace_raw(
            method="json",
            bld="dbms/MDC/STAT/issue/MDCSTAT21301",
            params={},
            menu_id="MDC0202",
            network_authorized=True,
            session=s,
        )
    assert len(s.calls) == 1


def test_openapi_adapter_preserves_raw_bytes_and_never_exposes_key_in_error():
    payload={"OutBlock_1":[{"ISU_CD":"KR7005930003","ISU_SRT_CD":"005930"}]}
    raw=json.dumps(payload,separators=(",",":")).encode()
    s=Session(gets=[Resp(content=raw)])
    out=fetch_openapi_raw(
        endpoint="https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info",
        params={"basDd":"20150615"},
        auth_key="PRIVATE_KEY_VALUE",
        network_authorized=True,
        session=s,
        retrieved_at_override="2026-10-02T10:00:00+00:00",
    )
    assert out.raw_bytes == raw
    assert out.response_frame.iloc[0]["ISU_SRT_CD"] == "005930"
    assert out.transport_status == "HTTP_200_OPENAPI"
    headers=s.calls[0][2]["headers"]
    assert headers["AUTH_KEY"] == "PRIVATE_KEY_VALUE"

    s2=Session(gets=[Resp(status=403,content=b"forbidden")])
    with pytest.raises(KRXHistoricalFetchError) as exc:
        fetch_openapi_raw(
            endpoint="https://data-dbg.krx.co.kr/svc/apis/sto/stk_isu_base_info",
            params={"basDd":"20150615"},
            auth_key="PRIVATE_KEY_VALUE",
            network_authorized=True,
            session=s2,
        )
    assert "PRIVATE_KEY_VALUE" not in str(exc.value)


def test_openapi_rejects_unexpected_endpoint_before_network():
    s=Session()
    with pytest.raises(KRXHistoricalFetchError, match="unexpected KRX OpenAPI endpoint"):
        fetch_openapi_raw(
            endpoint="https://example.com/x",
            params={},
            auth_key="x",
            network_authorized=True,
            session=s,
        )
    assert s.calls == []


def test_raw_parsers_support_resume_without_network():
    csv_raw = "일자,개인\n20260921,7\n".encode("euc-kr")
    csv_frame = parse_data_marketplace_raw("csv", csv_raw)
    assert csv_frame.iloc[0]["개인"] == 7

    json_raw = json.dumps(
        {"OutBlock_1":[{"ISU_CD":"KR7005930003","ISU_SRT_CD":"005930"}]},
        separators=(",",":"),
    ).encode("utf-8")
    frame = parse_openapi_raw(json_raw)
    assert frame.iloc[0]["ISU_SRT_CD"] == "005930"

    with pytest.raises(KRXHistoricalFetchError, match="method must be csv or json"):
        parse_data_marketplace_raw("xml", b"x")


def test_resolver_uses_pinned_catalog_defaults_required_and_period_limit():
    specs = {
        "investor": {
            "bld":"dbms/MDC/STAT/standard/MDCSTAT02303",
            "method":"csv",
            "menu_id":"MDC0201020302",
            "defaults":{"askBid":"3","trdVolVal":"2","isuCd2":""},
            "required":["isuCd","strtDd","endDd"],
        },
        "halt": {
            "bld":"dbms/MDC/STAT/issue/MDCSTAT21301",
            "method":"json",
            "menu_id":"MDC0202",
            "defaults":{"param1isuCd_finder_stkisu0_3":"ALL"},
            "required":["isuCd","isuCd2","strtDd","endDd"],
            "max_period_days":730,
        },
    }
    getter=lambda name: specs[name]

    out=resolve_pinned_endpoint_request(
        "investor",
        {"isuCd":"KR7005930003","strtDd":"20260101","endDd":"20261231"},
        catalog_getter=getter,
    )
    assert out["bld"].endswith("MDCSTAT02303")
    assert out["method"] == "csv"
    assert out["params"]["askBid"] == "3"
    assert out["params"]["trdVolVal"] == "2"
    assert out["pinned_client_commit"] == "e6ebac9b71482db127348d8a08ebc6743aa3b50e"

    with pytest.raises(KRXHistoricalFetchError, match="missing required params"):
        resolve_pinned_endpoint_request(
            "investor",
            {"strtDd":"20260101","endDd":"20261231"},
            catalog_getter=getter,
        )

    with pytest.raises(KRXHistoricalFetchError, match="exceeds max_period_days=730"):
        resolve_pinned_endpoint_request(
            "halt",
            {"isuCd":"KR7000300004","isuCd2":"000300","strtDd":"20240101","endDd":"20260102"},
            catalog_getter=getter,
        )
