# IndexAlert ETF Open — isolated 09:00 opening-price dislocation study

Status: **ISOLATED OFFLINE HYPOTHESIS / NO REAL DATA / NO PERFORMANCE / NO ORDERS**  
Created: 2026-10-29 KST  
Branch: `indexalert-etf-open-dislocation-research-v1`  
Base: `index-alert-research-v1`  
Frozen H5, preregistered M20, sealed Holdout, Champion, broker permissions and all existing runtime services **untouched**.

## Hypothesis and testable falsification

Hypothesis E1: for a small group of liquid **KRX-listed, overseas-index-tracking ETFs**, an independently measured low ask versus a point-in-time conservative synthetic fair-value *lower bound* between **09:00:00 and 09:04:59 KST** occasionally precedes positive **actually executable** after-all-costs markout. The hypothesis is rejected if paired out-of-sample fill-adjusted net economics are nonpositive, the effect depends on hindsight NAV, or the meaningful discount exists only on quotes that cannot be filled.

The official KRX ETF LP rules state that LP quote **submission is not mandatory before 09:05**, and during 09:05–15:20 LP must respond to a spread-trigger within the rules' interval rather than guaranteeing investors fills at their desired price. LPs may quote voluntarily even when there is no obligation. This is a *reason to measure*, not proof of exploitable mispricing:
https://regulation.krx.co.kr/contents/RGL/03/03060103/RGL03060103.jsp

Official Kiwoom REST API guide lists domestic real-time `0B` share trades, `0D` order-book depth, `0G` ETF NAV, as well as `ka10004` stock book and `ka40009` ETF intraday NAV endpoints:
https://openapi.kiwoom.com/m/guide/apiguide

Official Kiwoom open-source ETF NAV example specifically labels the real-time subscription `0G`, not a documented guarantee of precise live executable overseas-fair-value estimation:
https://github.com/Kiwoom-Securities/Kiwoom-REST-API/blob/main/examples/%EA%B5%AD%EB%82%B4%EC%A3%BC%EC%8B%9D/%EC%8B%A4%EC%8B%9C%EA%B0%84%EC%8B%9C%EC%84%B8/subscribe_domestic_etf_nav_async.py

**Unverified blockers:** actual registered-machine Kiwoom REAL WebSocket `805004/8050`, whether ETF and source timestamps can be gathered with required licensing on a particular user account, after-hours overseas futures and KRW FX available-at feeds, market-specific KRX sessions, exact tick-size schedule, clock discipline, and ETF-specific tax treatment. Access rights and historical availability must be confirmed **before any new network collection**. Do not move existing keys/permissions or bypass the existing Kiwoom WS fail-closed guard.

## What was implemented today

- `research_v1_etf_open_dislocation.py`: pure offline, exact-schema snapshot validator (six-digit code; KRX-only); uses explicit **received/observed millisecond** and separately timestamped quote, NAV, FX, US futures and valuation; rejects future-dated or stale inputs, crossed/locked/zero-size books and broad valuation intervals.
- The hypothetical discount must clear **lower**, not midpoint or stale iNAV, fair value and three **illustrative / uncalibrated** buffer components. The values are arbitrary research thresholds and cannot be read as a tested trading edge.
- Outputs `OFFLINE_WATCH_ONLY_NO_ORDER`, **never a broker order/position/fill**. There is no buy/sell executable, connection, paper fill simulation, strategy PnL, sealed holdout, approval switch, or production adapter.
- `replay_offline` rejects duplicate or out-of-order receipts, emits **aggregate counts only** (not raw instrument/quote data), and hard-codes all PIT/market order/performance/funds/Champion authorizations false.
- `test_research_v1_etf_open_dislocation.py` supplies synthetic 2026-10-26 Monday KST observations (fake ETF `123456`) and adversarial test cases. **Synthetic numbers are not KRX observations and not proof of an opportunity.**
- `.github/workflows/indexalert-etf-open-offline.yml`: Python 3.12 no-secret, no-network synthetic regression runner with explicit prohibition of broker/network imports.

## Minimum *independent* dataset before economic testing

For each approved ETF and trading day, collect **raw timestamped and receipt-time-bound** 08:59–09:30 KST sequence, accounting for exchange auction transition; distinguish quotes/orders/trades/indicative auction values and changing ticks. At minimum:

1. Exchange security identifier, KOSPI/KOSDAQ trading venue, listing status, ETF benchmark/hedge class, lot/tick size and authenticated market session timeline.
2. Complete top/depth bid/ask with **visible quantities, sequence, exchange event time and client receipt time**, trade prints and quote withdrawal/crossing, source-original SHA and usage rights.
3. Actual **current, accessible at that second** iNAV timestamp and its update policy; independent US index future, spot/forward KRW FX, relevant foreign exchange hours and ETF hedge status; valuation uncertainty interval. A stale iNAV must **never** be treated as executable fair value; futures+FX alone may still be insufficient.
4. Provider clock offset, disconnections/gaps, exchange halt/VI, best bid/ask changes and round-trip latency, verified original frozen data lineage.
5. Actual order attempts and **broker-native partial fill/reject/cancel reports** for any separately authorized simulation/paper protocol; avoid imputing buys on printed low and sells on printed high. Do not use a broker endpoint for any step before a separate controlled authorization.

Do not assume `ka40009` or a 1-minute chart is a full subsecond historical book. Verify field semantics, latency, retention and original feed entitlement for each source.

## Prespecified evaluation if authentic data become available

- First observation-only (zero orders). Count raw deviations conditional on 09:00–09:05, compare to equal-length **09:05–09:10** and **09:10–09:15** controls on the **same dates**, and a no-dislocation passive ETF benchmark. No claim of alpha from selecting the observed minimum tick.
- Distinguish 1) ask lower than conservative independently time-aligned fair value, 2) the quote existed after receiving the necessary market data, 3) feasible order size after visible displayed queue and latency, 4) actual realistic fill and cancellation, 5) exit after every fee, slippage, FX and correct tax basis. Measure adverse selection following near-touch fills; use censoring and zero-fill trades.
- Split dates chronologically with purge/embargo/strict preregistration, perform locked test and cross-day uncertainty; do not touch original H5/M20 sealed Holdout. Separate ETF-specific train/test for US-index, hedged/unhedged funds and compare concentration by day/ETF.
- Report **fill probability; gross and after-cost net return conditional on filled/attempted; win/loss; EV; PF; MDD; ES95/99; spread/premium distribution; cancel & reject rates; latency-tail; participation capacity; tax-model sensitivity**. Any missing market source, time misalignment, benchmark event, insufficient independent sample or unverified charge is a NO-GO, not a value to silently fill.
- Never use an IRP order route by default or assume intraday ETF tax treatment transfers across account types. The investor's account type is a later explicitly reviewed decision.

## Safe operational sequencing

`offline syntax + synthetic regression` → `authenticated entitlement & read-only local observer authorization` → `paper event replay with historical original as-of evidence` → `economic acceptance before separate broker-readonly stage` → `shadow/no-order forward record` → `explicit separate live order permission only if all gates succeed`.

**For now every stage after the first is blocked.** Never merge this branch into research core/production, deploy Railway, change credential or device authorization, start official network acquisition, modify Frozen/Holdout/Champion, or place a real order without dedicated gate and required approval. Keep `ORDERING=false`.

## 2026-10-29 KST continuation — chronology and uncertainty boundaries

- Reject a valuation if any NAV, FX or US futures reference timestamp is later than `valuation_at_ms`, even when all timestamps precede receipt. Equal timestamps remain allowed. This prevents an internally inconsistent synthetic valuation; it does not authenticate feed receipt times or prove valuation lineage.
- Compare valuation range uncertainty using exact integer products. An 81 KRW range over 10,000 KRW is 81 bps and is rejected; fractional excess such as 82 KRW over 10,200 KRW (~80.39 bps) is also rejected rather than floored to 80. Exactly 80 bps remains allowed.
- Local Python unittest run: **21/21 synthetic tests PASS**, including four new regression methods. No authentic market data, fill, performance or source admission was tested. Remote CI must be checked separately for the final commit.
- Next dependency remains licensed, timestamp-defined original ETF book/NAV/futures/FX observations and registered-machine read-only feed feasibility. No network collection, broker login, order, merge, deployment, Holdout or Champion change performed by this continuation. All authorisation flags remain denied and `ORDERING=DISABLED`.
