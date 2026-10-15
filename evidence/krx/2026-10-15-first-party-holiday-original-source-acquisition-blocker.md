# KRX official original calendar blocker — action-ready source acquisition

Reviewed 2026-10-15 KST. Audit-only branch `indexalert-krx-pit-source-audit-20261013`.

**Priority:** obtaining and proving an official historical KOSPI cash-equity session calendar, NOT running more artificial parser tests. No production deployment, volume reads, authenticated KRX OpenAPI calls, or trading occurred in this review.

## Confirmed first-party source route and constraints

- [KRX original public holiday search/download](https://open.krx.co.kr/contents/MKD/01/0110/01100305/MKD01100305.jsp): KRX vs CME/EUREX selector and holiday/year export controls; public text indexing does **not** expose the actual original year-date rows. Direct web fetch returned HTTP 403. This is a source *route*, not an acquired export.
- [KRX KOSPI cash-equity holiday rules](https://global.krx.co.kr/contents/GLB/06/0602/0602010201/GLB0602010201T1.jsp): national holidays, elections, May 1, final year-end session and other KRX-designated closures. Do not substitute KRX derivatives, gold, CME/EUREX, or a third-party XKRX calendar as full first-party PIT evidence.
- The official holiday page identifies **KRX 주식시장운영팀 02-3774-8605** as its content owner/contact. This was observed on the first-party indexed holiday page, but **the team has not been contacted or agreed to supply archives**.
- Original public archived [July 2017 KRX XLS transcription](https://financedata.github.io/posts/pandas-market-days-krx.html) and later September exchange-holiday news show a calendar revised mid-year. Neither its inaccessible original XLS bytes nor a date-by-date matching private source snapshot has been authenticated.
- Direct attempts to read the official KRX calendar and a previously cited original 2017 KRX PDF were blocked/unavailable via the current external fetch. These are access constraints, not evidence of market holidays.
- The repository's GitHub Issues feature is **disabled** (GitHub returned HTTP 410 on issue creation), so this auditable blocker is stored as a committed repository document instead.

## Required source request if an authorized person or tool obtains first-party records

```text
한국거래소 주식시장운영팀 담당자님께,

한국 유가증권시장(KOSPI 보통주) 2015~2026년 연도별
실제 매매거래일·휴장일의 공식 원본 파일(XLS/CSV/XLSX)
또는 공식 다운로드 경로를 연구·검증 목적에 한해 문의드립니다.

선거일, 임시공휴일, 연말 휴장, 특별 개장시간 등
변경 사항의 최초 게시일시, 버전/정정 이력, 해당
시장 범위, 출처와 이용허락·보관·비상업적 자동검증
가능 범위도 안내 부탁드립니다.

파생상품, 금시장, CME/EUREX 등의 캘린더와 구분된
KOSPI 주식 현물시장 자료가 필요합니다. 감사합니다.
```

**This request text has NOT been sent.** No phone call, email, staff representation or exchange login is implied.

## Acceptance checklist; no shortcuts

1. Obtain permitted full-original dated official holiday/session source for 2015–2025; through **2026-10-08** for pinned private 2026 snapshot. Record actual raw file bytes, independently verified SHA256, market applicability, original publication and amendments' earliest supported available-at times.
2. Keep original source in protected Railway/private `/data` store, never in public GitHub, Actions artifacts or logs. Unsupported legacy XLS/HTML: fail closed; inspect exact original format before designing new adapter, never silently convert and pretend the converted artifact is the original.
3. Run read-only private `research_v1_krx_private_calendar_year_runner.py --audit` ONLY when source rights, actual original bytes, sidecar and independent SHA are staged in a trusted approved worker. The protected worker currently runs **only the original integrity audit** from the dev branch; this audit-branch runner has not been deployed.
4. Compare exact **per-day** source-empty vs independently authenticated official closed-day sets under historical PIT time, not counts. A matching day set establishes consistency ONLY, not stock status, PIT historical source publication or M20 profitability.
5. Record sanitized yearly aggregate mismatch counts and digests without original symbol rows/date receipts; keep PIT gates C/D closed until independently reviewed.

## Current checked results

- [Latest parser unit-suite run #38705795464](https://github.com/kims34/openpilot-opkr/actions/runs/38705795464): **149/149 offline tests passed**, no private original data read.
- Railway KRX historical worker: deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS (Oct 12), original dev branch, mounted `/data`; unchanged in this review.
- **3,071** SHA-backed weekday checkpoints, **184** ambiguous original provider-empty days, **27** quarantined securities: source-integrity evidence remains, date-specific original-vs-holiday classification still **NOT VERIFIED**.
- Frozen H5/Champion, 504/126/126 split, PIT/holdout gates, M20 NetEV and trading authorization unchanged. `ORDERING=false`, source C/D blocked, no live orders, broker credentials/rights changes, or funds movement.

**Unblock criterion:** original permitted KRX annual source bytes + publication/version evidence + controlled read-only private day-level reconciliation. Until those exist, keep the original calendar's 184 ambiguous dates blocked, even if parser/test count rises.
