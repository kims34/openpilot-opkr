import re
import time
from xml.etree import ElementTree

import requests

CACHE = {"updated": 0.0, "items": {}}
TTL_SECONDS = 1800

NEWS_QUERIES = {
    "sp500": "S&P 500 미국 증시 연준 금리 물가 기업 실적",
    "ndx": "나스닥 기술주 AI 반도체 미국 국채금리 실적",
    "djdiv": "SCHD 배당주 가치주 금융주 금리 미국 증시",
    "kospi100": "코스피 외국인 반도체 환율 미국 증시 금리",
    "usdkrw": "원달러 환율 달러 원화 미국 금리 연준",
}

DISPLAY_NAMES = {
    "sp500": "SPY",
    "ndx": "QQQ",
    "djdiv": "SCHD",
    "kospi100": "KOSPI",
    "usdkrw": "USD/KRW",
}

INDEX_FOCUS = {
    "sp500": "대형주 전반의 위험선호",
    "ndx": "AI·반도체와 메가캡 성장주의 주도력",
    "djdiv": "배당·가치주의 상대강도",
    "kospi100": "외국인 수급과 반도체 대형주의 방향",
    "usdkrw": "달러 강도와 원화 수급",
}

DEFAULT_WATCH = {
    "sp500": ["미 10년물 국채금리", "연준 발언", "대형주 실적/가이던스"],
    "ndx": ["미 10년물 국채금리", "AI·반도체 대형주", "메가캡 실적"],
    "djdiv": ["미 국채금리", "배당주 상대강도", "금융·산업·에너지 수급"],
    "kospi100": ["원/달러 환율", "외국인 현물·선물 수급", "삼성전자·SK하이닉스"],
    "usdkrw": ["달러인덱스", "미 국채금리", "외국인 국내주식 수급"],
}

EXTERNAL_GROUPS = [
    ("전쟁·지정학적 불확실성", ("전쟁", "중동", "이란", "우크라이나", "러시아", "지정학", "war", "geopolit")),
    ("금리·국채금리 변화", ("연준", "금리", "국채", "수익률", "fed", "rate", "yield", "treasury")),
    ("물가·인플레이션 지표", ("물가", "인플레이션", "cpi", "ppi", "inflation")),
    ("관세·무역정책", ("관세", "무역", "tariff", "trade")),
    ("유가·원자재 가격", ("유가", "원유", "원자재", "oil", "crude", "commodity")),
    ("달러·환율 변동", ("달러", "환율", "원화", "dollar", "currency", "won")),
    ("고용·경기지표", ("고용", "실업", "경기", "job", "payroll", "unemployment", "economy")),
]

INTERNAL_GROUPS = [
    ("기업 실적·가이던스", ("실적", "매출", "영업이익", "가이던스", "earnings", "revenue", "profit", "guidance")),
    ("기술주·AI·반도체 업종 흐름", ("기술주", "반도체", "ai", "인공지능", "chip", "semiconductor", "tech")),
    ("기업가치·밸류에이션 조정", ("기업가치", "밸류에이션", "고평가", "valuation", "multiple")),
    ("배당·금융·가치주 수급", ("배당", "금융주", "은행", "가치주", "dividend", "bank", "financial", "value stock")),
    ("외국인·기관 수급", ("외국인", "기관", "수급", "순매수", "순매도", "foreign investor", "institutional")),
]

DEFAULT_REASON = {
    "sp500": ("혼합", "미국 거시 변수와 대형주 수급"),
    "ndx": ("혼합", "금리 민감도와 기술주·AI/반도체 수급"),
    "djdiv": ("혼합", "금리 흐름과 배당·가치주 수급"),
    "kospi100": ("혼합", "환율·외국인 수급과 반도체 대형주 흐름"),
    "usdkrw": ("외부요인", "미국 금리·달러 흐름과 원화 수급"),
}

THEME_IMPLICATION = {
    "전쟁·지정학적 불확실성": "위험회피 심리와 원자재·달러 변동성이 가격에 번질 가능성이 큽니다.",
    "금리·국채금리 변화": "할인율 변화가 주식 밸류에이션과 위험선호를 동시에 흔드는 구간입니다.",
    "물가·인플레이션 지표": "연준의 금리 경로 재평가가 채권금리와 주가에 함께 반영되는 흐름입니다.",
    "관세·무역정책": "정책 불확실성이 기업 마진과 공급망 기대를 다시 가격에 반영시키고 있습니다.",
    "유가·원자재 가격": "원가와 인플레이션 기대가 업종별 실적 전망을 갈라놓을 수 있습니다.",
    "달러·환율 변동": "환율 변화가 외국인 수급과 위험자산 선호를 통해 지수에 영향을 주는 모습입니다.",
    "고용·경기지표": "경기 연착륙과 둔화 기대 사이의 재평가가 금리와 실적 전망을 함께 움직이고 있습니다.",
    "기업 실적·가이던스": "지수 전체보다 실적과 가이던스에 따른 종목 차별화가 중요해진 장입니다.",
    "기술주·AI·반도체 업종 흐름": "AI·반도체 대형주의 방향이 지수 탄력을 좌우하는 장세에 가깝습니다.",
    "기업가치·밸류에이션 조정": "높아진 멀티플에 대한 부담이 고평가 종목 중심으로 반영되는 흐름입니다.",
    "배당·금융·가치주 수급": "성장주와 가치주 사이의 자금 이동이 상대수익률을 결정하는 구간입니다.",
    "외국인·기관 수급": "대형주 중심의 수급 변화가 지수 움직임을 증폭시키는 모습입니다.",
}

THEME_WATCH = {
    "전쟁·지정학적 불확실성": "유가·달러·변동성지수",
    "금리·국채금리 변화": "미 10년물 국채금리와 연준 금리 기대",
    "물가·인플레이션 지표": "CPI·PCE·기대인플레이션",
    "관세·무역정책": "관세 발표와 기업별 비용 전가 여부",
    "유가·원자재 가격": "WTI 유가와 원자재 가격",
    "달러·환율 변동": "달러인덱스와 원/달러 환율",
    "고용·경기지표": "고용·실업·소비 지표",
    "기업 실적·가이던스": "실적 발표와 다음 분기 가이던스",
    "기술주·AI·반도체 업종 흐름": "반도체 지수와 AI 대형주 상대강도",
    "기업가치·밸류에이션 조정": "장기금리와 성장주 밸류에이션",
    "배당·금융·가치주 수급": "가치주·금융주 상대강도와 금리곡선",
    "외국인·기관 수급": "외국인·기관 순매수와 선물 포지션",
}


def _normalize_title(title: str):
    title = re.sub(r"\s+", " ", title).strip()
    # Google News 제목 끝의 매체명은 같은 기사를 중복 집계하게 만들 수 있어 제거한다.
    if " - " in title:
        title = title.rsplit(" - ", 1)[0].strip()
    return title


def _titles(query: str):
    try:
        r = requests.get(
            "https://news.google.com/rss/search",
            params={"q": query + " when:1d", "hl": "ko", "gl": "KR", "ceid": "KR:ko"},
            headers={"User-Agent": "Mozilla/5.0 IndexAlert/1.9"},
            timeout=12,
        )
        r.raise_for_status()
        root = ElementTree.fromstring(r.content)
        out = []
        seen = set()
        for item in root.findall(".//item")[:24]:
            title = _normalize_title(item.findtext("title") or "")
            key = re.sub(r"[^0-9a-z가-힣]+", "", title.lower())
            if not title or not key or key in seen:
                continue
            seen.add(key)
            out.append(title)
            if len(out) == 15:
                break
        return out
    except Exception as exc:
        print("briefing news failed", type(exc).__name__, flush=True)
        return []


def _score(titles, groups):
    scored = []
    lowered = [title.lower() for title in titles]
    for label, keywords in groups:
        # 같은 기사에서 같은 테마 단어가 여러 번 나와도 한 건으로 계산한다.
        hits = sum(1 for title in lowered if any(keyword.lower() in title for keyword in keywords))
        if hits:
            scored.append((hits, label))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return scored


def _pct_value(pct):
    try:
        return float(pct)
    except Exception:
        return 0.0


def _move_tone(p):
    magnitude = abs(p)
    if magnitude < 0.10:
        return "방향성이 뚜렷하지 않은 보합권"
    if magnitude < 0.50:
        return "완만한 상승" if p > 0 else "완만한 하락"
    if magnitude < 1.50:
        return "의미 있는 상승" if p > 0 else "의미 있는 하락"
    return "강한 상승" if p > 0 else "강한 하락"


def _ranked_themes(external, internal):
    ranked = [(score, label, "외부") for score, label in external]
    ranked += [(score, label, "내부") for score, label in internal]
    ranked.sort(key=lambda x: (-x[0], x[1]))
    return ranked


def _driver_list(ranked, fallback):
    if not ranked:
        return [f"복합 수급 · {fallback}을 중심으로 확인 필요"]
    out = []
    for score, label, kind in ranked[:3]:
        suffix = "기사" if score == 1 else "기사"
        out.append(f"{label} · 관련 {suffix} {score}건에서 확인 · {kind}요인")
    return out


def _summary(index_id, p, ranked, ext_score, int_score):
    name = DISPLAY_NAMES[index_id]
    tone = _move_tone(p)
    focus = INDEX_FOCUS[index_id]

    if not ranked:
        return (
            f"{name}은 {tone}입니다. 뚜렷한 단일 뉴스 재료가 포착되지 않아 "
            f"{focus}과 장중 수급을 함께 보는 편이 낫습니다."
        )

    top_label = ranked[0][1]
    implication = THEME_IMPLICATION.get(top_label, "여러 재료가 동시에 반영되는 구간입니다.")
    if ext_score >= max(2, int_score * 1.35):
        lead = "거시·정책 변수의 영향이 종목 내부 재료보다 강하게 포착됐습니다."
    elif int_score >= max(2, ext_score * 1.35):
        lead = "기업·업종 내부 재료가 거시 변수보다 강하게 포착됐습니다."
    else:
        lead = "거시 변수와 기업·업종 재료가 함께 가격에 반영되는 모습입니다."

    return f"{name}은 {tone}입니다. {lead} {implication}"


def _watch_text(index_id, ranked):
    picks = []
    for _, label, _ in ranked[:2]:
        point = THEME_WATCH.get(label)
        if point and point not in picks:
            picks.append(point)
    for point in DEFAULT_WATCH[index_id]:
        if point not in picks:
            picks.append(point)
        if len(picks) == 3:
            break
    return " · ".join(picks[:3])


def _make(index_id: str, pct):
    titles = _titles(NEWS_QUERIES[index_id])
    external = _score(titles, EXTERNAL_GROUPS)
    internal = _score(titles, INTERNAL_GROUPS)
    ext_score = sum(x[0] for x in external)
    int_score = sum(x[0] for x in internal)
    ranked = _ranked_themes(external, internal)

    if ext_score == 0 and int_score == 0:
        category, fallback = DEFAULT_REASON[index_id]
    elif ext_score >= max(2, int_score * 1.35):
        category = "외부 변수 중심"
        fallback = external[0][1]
    elif int_score >= max(2, ext_score * 1.35):
        category = "기업·업종 중심"
        fallback = internal[0][1]
    else:
        category = "복합"
        fallback = DEFAULT_REASON[index_id][1]

    p = _pct_value(pct)
    drivers = _driver_list(ranked, fallback)
    balance = (
        f"뉴스 신호 구성: 외부 {ext_score} · 내부 {int_score}"
        if titles else "뉴스 신호가 부족해 시세 중심으로 해석"
    )

    return {
        "id": index_id,
        "category": category,
        "text": _summary(index_id, p, ranked, ext_score, int_score),
        "drivers": drivers,
        "balance": balance,
        "watch": _watch_text(index_id, ranked),
        "confidence": f"최근 24시간 중복 제거 헤드라인 {len(titles)}건 분석 · 인과관계 확정이 아닌 시장 해석",
        "headline_count": len(titles),
        "day_change_percent": p,
    }


def get_all(extra_state: dict):
    now = time.time()
    if CACHE["items"] and now - CACHE["updated"] < TTL_SECONDS:
        return {"updated_at": CACHE["updated"], "items": list(CACHE["items"].values())}

    items = {}
    for index_id in NEWS_QUERIES:
        state = extra_state.get(index_id) or {}
        pct = state.get("day_change_percent")
        items[index_id] = _make(index_id, pct if pct is not None else 0.0)
    CACHE["updated"] = now
    CACHE["items"] = items
    return {"updated_at": now, "items": list(items.values())}
