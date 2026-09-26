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

WATCH_POINTS = {
    "sp500": "미 10년물 국채금리 · 연준 발언 · 대형주 실적/가이던스 · 경기·물가 지표",
    "ndx": "미 10년물 국채금리 · AI/반도체 대형주 흐름 · 메가캡 실적 · 밸류에이션 부담",
    "djdiv": "미 국채금리 · 금융/산업/에너지 가치주 수급 · 배당주 상대강도 · 경기민감 업종 흐름",
    "kospi100": "원/달러 환율 · 외국인 현물/선물 수급 · 삼성전자·SK하이닉스 등 반도체 대형주 · 미국 증시",
    "usdkrw": "달러인덱스 · 미국 국채금리 · 연준 기대 · 외국인 국내주식 수급 · 위안화/엔화 움직임",
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


def _titles(query: str):
    try:
        r = requests.get(
            "https://news.google.com/rss/search",
            params={"q": query + " when:1d", "hl": "ko", "gl": "KR", "ceid": "KR:ko"},
            headers={"User-Agent": "Mozilla/5.0 IndexAlert/1.8"},
            timeout=12,
        )
        r.raise_for_status()
        root = ElementTree.fromstring(r.content)
        return [
            (item.findtext("title") or "").strip()
            for item in root.findall(".//item")[:15]
            if (item.findtext("title") or "").strip()
        ]
    except Exception as exc:
        print("briefing news failed", type(exc).__name__, flush=True)
        return []


def _score(text: str, groups):
    lower = text.lower()
    scored = []
    for label, keywords in groups:
        count = sum(lower.count(keyword.lower()) for keyword in keywords)
        if count:
            scored.append((count, label))
    scored.sort(reverse=True)
    return scored


def _movement_label(pct):
    try:
        p = float(pct)
    except Exception:
        p = 0.0
    if p > 0.05:
        return "상승"
    if p < -0.05:
        return "하락"
    return "보합"


def _pct_value(pct):
    try:
        return float(pct)
    except Exception:
        return 0.0


def _driver_list(external, internal, fallback):
    combined = [(score, label, "외부") for score, label in external] + [
        (score, label, "내부") for score, label in internal
    ]
    combined.sort(key=lambda x: x[0], reverse=True)
    out = []
    seen = set()
    for score, label, kind in combined:
        if label in seen:
            continue
        seen.add(label)
        out.append(f"{label} · {kind}요인 뉴스 언급 강도 {score}")
        if len(out) == 3:
            break
    if not out:
        out.append(f"{fallback} · 뚜렷한 단일 뉴스 요인보다 복합 수급 가능성")
    return out


def _make(index_id: str, pct):
    titles = _titles(NEWS_QUERIES[index_id])
    joined = " ".join(titles)
    external = _score(joined, EXTERNAL_GROUPS)
    internal = _score(joined, INTERNAL_GROUPS)
    ext_score = sum(x[0] for x in external)
    int_score = sum(x[0] for x in internal)

    if ext_score == 0 and int_score == 0:
        category, reason = DEFAULT_REASON[index_id]
    elif ext_score >= max(2, int_score * 1.35):
        category = "외부요인 우세"
        reason = external[0][1]
    elif int_score >= max(2, ext_score * 1.35):
        category = "내부요인 우세"
        reason = internal[0][1]
    else:
        category = "혼합"
        ext = external[0][1] if external else None
        intr = internal[0][1] if internal else None
        reason = f"{ext} + {intr}" if ext and intr else (ext or intr or DEFAULT_REASON[index_id][1])

    p = _pct_value(pct)
    move = _movement_label(p)
    name = DISPLAY_NAMES[index_id]
    drivers = _driver_list(external, internal, reason)
    direction = f"{name}은 전일 대비 {p:+.2f}% {move}했습니다."
    context = (
        f"최근 24시간 관련 뉴스에서는 '{reason}'가 상대적으로 두드러졌습니다. "
        "다만 뉴스 제목과 시세의 동시 움직임을 바탕으로 한 추정이므로 단일 원인으로 단정하지 않습니다."
    )
    balance = f"외부요인 신호 {ext_score} / 내부요인 신호 {int_score}"

    return {
        "id": index_id,
        "category": category,
        "text": f"{direction} {context}",
        "drivers": drivers,
        "balance": balance,
        "watch": WATCH_POINTS[index_id],
        "confidence": f"최근 24시간 뉴스 제목 {len(titles)}건 + 당일 시세 기반 추정 · 원인 확정 아님",
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
