import csv
import io
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

try:
    import laggards
except Exception as exc:
    laggards = None
    print("constituent patch import failed", type(exc).__name__, flush=True)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/csv;q=0.8,*/*;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
}


def _clean(symbol: str) -> str:
    return symbol.strip().upper().replace("\u00a0", "")


def _valid_equity_symbol(symbol: str) -> bool:
    return bool(re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,7}", symbol)) and not symbol.endswith("XX")


def _symbols_from_html_table(html: str, header_names):
    soup = BeautifulSoup(html, "html.parser")
    best = set()
    wanted = {x.lower() for x in header_names}
    for table in soup.find_all("table"):
        trs = table.find_all("tr")
        if not trs:
            continue
        for header_row_index in range(min(4, len(trs))):
            header_cells = trs[header_row_index].find_all(["th", "td"])
            headers = [c.get_text(" ", strip=True).lower() for c in header_cells]
            idx = next((i for i, h in enumerate(headers) if h in wanted), None)
            if idx is None:
                continue
            out = set()
            for tr in trs[header_row_index + 1:]:
                cells = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
                if idx >= len(cells):
                    continue
                sym = _clean(cells[idx].replace(":PR", ""))
                if _valid_equity_symbol(sym):
                    out.add(sym)
            if len(out) > len(best):
                best = out
    return best


def robust_nasdaq100_symbols():
    urls = [
        "https://indexes.nasdaq.com/Index/Weighting/NDX",
        "https://en.wikipedia.org/wiki/List_of_NASDAQ-100_companies",
        "https://stockanalysis.com/list/nasdaq-100-stocks/",
    ]
    for url in urls:
        try:
            r = requests.get(url, headers=BROWSER_HEADERS, timeout=30)
            print("nasdaq source", url, r.status_code, len(r.text), flush=True)
            r.raise_for_status()
            out = _symbols_from_html_table(r.text, ("security symbol", "symbol", "ticker", "ticker symbol"))
            print("nasdaq parsed", url, len(out), flush=True)
            if len(out) >= 90:
                return out
        except Exception as exc:
            print("nasdaq source failed", url, type(exc).__name__, flush=True)
    return set()


def _schd_from_all_holdings():
    url = "https://www.schwabassetmanagement.com/allholdings/schd"
    r = requests.get(url, headers=BROWSER_HEADERS, timeout=30)
    print("schd allholdings source", r.status_code, len(r.text), flush=True)
    r.raise_for_status()
    text = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True)
    out = {_clean(x) for x in re.findall(r"\bSymbol\s+([A-Z][A-Z0-9.\-]{0,7})\b", text)}
    return {x for x in out if _valid_equity_symbol(x)}


def _schd_from_export_csv():
    product_url = "https://www.schwabassetmanagement.com/products/schd"
    r = requests.get(product_url, headers=BROWSER_HEADERS, timeout=30)
    print("schd product source", r.status_code, len(r.text), flush=True)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    href = None
    for a in soup.find_all("a", href=True):
        label = a.get_text(" ", strip=True).lower()
        if "export all holdings" in label:
            href = a.get("href")
            break
    if not href:
        print("schd export link missing", flush=True)
        return set()
    csv_url = urljoin(product_url, href)
    cr = requests.get(csv_url, headers=BROWSER_HEADERS, timeout=30)
    print("schd export source", csv_url, cr.status_code, len(cr.content), flush=True)
    cr.raise_for_status()
    text = cr.content.decode("utf-8-sig", errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    header_idx = symbol_col = None
    for i, row in enumerate(rows[:30]):
        lowered = [c.strip().lower() for c in row]
        if "symbol" in lowered:
            header_idx = i
            symbol_col = lowered.index("symbol")
            break
    if header_idx is None or symbol_col is None:
        return set()
    out = set()
    for row in rows[header_idx + 1:]:
        if symbol_col >= len(row):
            continue
        sym = _clean(row[symbol_col])
        if _valid_equity_symbol(sym):
            out.add(sym)
    return out


def _schd_from_generic_table(url: str, label: str):
    r = requests.get(url, headers=BROWSER_HEADERS, timeout=30)
    print(label, r.status_code, len(r.text), flush=True)
    r.raise_for_status()
    out = _symbols_from_html_table(r.text, ("symbol", "ticker"))
    if len(out) >= 80:
        return out

    # Some full-list pages render simple text rows rather than semantic tables.
    text = BeautifulSoup(r.text, "html.parser").get_text("\n", strip=True)
    candidates = set()
    for line in text.splitlines():
        token = _clean(line.split()[0]) if line.split() else ""
        token = token.replace(":PR", "")
        if _valid_equity_symbol(token):
            candidates.add(token)
    # Restrict the loose text fallback to plausible portfolio sizes.
    if 80 <= len(candidates) <= 180:
        return candidates
    return out


def _schd_from_stockmarketwatch():
    return _schd_from_generic_table("https://stockmarketwatch.com/etf/schd/holdings", "schd stockmarketwatch source")


def _schd_from_marketxls():
    return _schd_from_generic_table("https://www.marketxls.com/etfs/schd/holdings", "schd marketxls source")


def _schd_from_stockanalysis():
    return _schd_from_generic_table("https://stockanalysis.com/etf/schd/holdings/", "schd stockanalysis source")


def robust_schd_symbols():
    best = set()
    loaders = (
        _schd_from_all_holdings,
        _schd_from_export_csv,
        _schd_from_stockmarketwatch,
        _schd_from_marketxls,
        _schd_from_stockanalysis,
    )
    for loader in loaders:
        try:
            out = loader()
            print("schd parsed", loader.__name__, len(out), flush=True)
            if len(out) > len(best):
                best = out
            if len(out) >= 80:
                return out
        except Exception as exc:
            print("schd source failed", loader.__name__, type(exc).__name__, flush=True)
    return best if len(best) >= 80 else set()


if laggards is not None:
    laggards.UA = BROWSER_HEADERS
    laggards.nasdaq100_symbols = robust_nasdaq100_symbols
    laggards.schd_symbols = robust_schd_symbols
    print("constituent source patch active", flush=True)
