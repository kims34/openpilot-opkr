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

DEFAULT_WATCH = {
    "sp500": ["미 10년물 국채금리", "연준 발언", "대형주 시장폭"],
    "ndx": ["미 10년물 국채금리", "AI·반도체 상대강도", "메가캡 실적"],
    "djdiv": ["미 국채금리", "배당주 상대강도", "금융·산업·에너지 수급"],
    "kospi100": ["원/달러 환율", "외국인 현물·선물 수급", "삼성전자·SK하이닉스"],
    "usdkrw": ["달러인덱스", "미 국채금리", "위안화·엔화 동조"],
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
    "sp500": ("복합", "미국 거시 변수와 대형주 수급"),
    "ndx": ("복합", "금리 민감도와 기술주·AI/반도체 수급"),
    "djdiv": ("복합", "금리 흐름과 배당·가치주 수급"),
    "kospi100": ("복합", "환율·외국인 수급과 반도체 대형주 흐름"),
    "usdkrw": ("외부 변수 중심", "미국 금리·달러 흐름과 원화 수급"),
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
    lowered = [title.lower() for title in titles]
    scored = []
    for label, keywords in groups:
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
        return "보합권"
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
        return [f"복합 수급 · {fallback}"]
    return [f"[{kind}] {label} · 헤드라인 {score}건" for score, label, kind in ranked[:3]]


def _dominance_sentence(index_id, ext_score, int_score):
    if ext_score >= max(2, int_score * 1.35):
        return {
            "sp500": "오늘 뉴스 흐름은 개별 기업보다 거시 변수 쪽에 무게가 실립니다.",
            "ndx": "헤드라인 구성상 성장주 내부 이슈보다 거시 변수의 비중이 높습니다.",
            "djdiv": "배당주 자체 재료보다 금리·경기 같은 바깥 변수가 더 많이 포착됩니다.",
            "kospi100": "국내 개별 이슈보다 해외 거시 재료의 비중이 높게 잡힙니다.",
            "usdkrw": "환율 뉴스는 국내 재료보다 글로벌 달러·금리 변수에 더 집중돼 있습니다.",
        }[index_id]
    if int_score >= max(2, ext_score * 1.35):
        return {
            "sp500": "거시 변수보다 기업 실적과 업종 수급의 영향이 더 강하게 포착됩니다.",
            "ndx": "오늘은 금리보다 AI·반도체·메가캡 자체 재료의 설명력이 더 커 보입니다.",
            "djdiv": "배당·금융·가치주 내부 수급이 거시 변수보다 더 두드러집니다.",
            "kospi100": "해외 변수보다 반도체 대형주와 외국인·기관 수급의 영향이 더 선명합니다.",
            "usdkrw": "글로벌 재료보다 국내 수급 요인의 비중이 이례적으로 높게 포착됩니다.",
        }[index_id]
    return {
        "sp500": "거시 변수와 기업·업종 재료가 비슷한 비중으로 섞여 있습니다.",
        "ndx": "금리 변수와 기술주 내부 재료가 동시에 가격에 반영되는 모습입니다.",
        "djdiv": "금리와 가치주 수급이 함께 작용하는 전형적인 혼합 구간입니다.",
        "kospi100": "해외 변수와 국내 수급이 동시에 지수 방향에 영향을 주는 모습입니다.",
        "usdkrw": "글로벌 달러 흐름과 국내 원화 수급이 함께 작용하는 구간입니다.",
    }[index_id]


def _asset_lens(index_id, top_label):
    if index_id == "sp500":
        if top_label == "금리·국채금리 변화":
            return "미 10년물 금리의 실제 방향과 대형주 상승 종목 수가 같이 개선되는지 확인해야 상승의 질을 판단할 수 있습니다."
        return "대형주 몇 종목만 움직였는지, 시장 전반으로 강도가 확산됐는지가 다음 판단 포인트입니다."
    if index_id == "ndx":
        if top_label in {"금리·국채금리 변화", "기업가치·밸류에이션 조정"}:
            return "QQQ는 금리 민감도가 높아 장기금리 방향과 AI·반도체 상대강도가 추세 지속 여부를 가를 가능성이 큽니다."
        return "메가캡과 AI·반도체가 같은 방향으로 움직이는지 확인하면 지수 움직임의 지속성을 판단하기 쉽습니다."
    if index_id == "djdiv":
        return "SCHD는 성장주보다 금리와 경기민감 업종의 영향이 커 금융·산업·에너지의 동반 강도가 더 중요한 확인 지점입니다."
    if index_id == "kospi100":
        if top_label in {"금리·국채금리 변화", "달러·환율 변동"}:
            return "해외 재료가 원/달러 환율과 외국인 수급을 거쳐 삼성전자·SK하이닉스에 실제로 연결되는지 보는 것이 핵심입니다."
        return "외국인 현·선물 수급과 반도체 대형주가 같은 방향인지 확인해야 지수 움직임의 지속성을 판단할 수 있습니다."
    if top_label == "금리·국채금리 변화":
        return "미 금리 뉴스 자체보다 달러인덱스와 위안화·엔화가 같은 방향으로 움직이는지 확인하는 편이 환율 해석에 더 유효합니다."
    return "달러인덱스와 아시아 통화의 동조 여부를 같이 보면 원화만의 움직임인지 글로벌 달러 흐름인지 구분하기 쉽습니다."


def _summary(index_id, p, ranked, ext_score, int_score):
    name = DISPLAY_NAMES[index_id]
    tone = _move_tone(p)
    dominance = _dominance_sentence(index_id, ext_score, int_score)

    if not ranked:
        no_signal = {
            "sp500": "뚜렷한 단일 재료가 없어 대형주 전반의 시장폭과 장중 수급을 보는 편이 낫습니다.",
            "ndx": "뚜렷한 뉴스 한 가지보다 AI·반도체와 메가캡의 동행 여부가 더 중요합니다.",
            "djdiv": "단일 뉴스보다 배당·가치주 내 업종 순환과 금리 민감도 차이를 확인할 구간입니다.",
            "kospi100": "환율·외국인 수급·반도체 대형주의 방향이 일치하는지 확인하는 편이 유효합니다.",
            "usdkrw": "특정 뉴스보다 달러인덱스와 아시아 통화 전반의 움직임을 함께 봐야 합니다.",
        }[index_id]
        return f"{name}는 {tone}입니다. {no_signal}"

    top_label = ranked[0][1]
    return f"{name}는 {tone}입니다. {dominance} {_asset_lens(index_id, top_label)}"


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
        f"뉴스 신호: 외부 {ext_score} · 내부 {int_score}"
        if titles else "뉴스 신호 부족 · 시세 중심 해석"
    )

    return {
        "id": index_id,
        "category": category,
        "text": _summary(index_id, p, ranked, ext_score, int_score),
        "drivers": drivers,
        "balance": balance,
        "watch": _watch_text(index_id, ranked),
        "confidence": f"중복 제거 헤드라인 {len(titles)}건 분석 · 시장 해석용",
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
