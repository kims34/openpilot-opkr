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

## 2026-10-29 KST — cash-cost sensitivity, NOT measured returns

Previous chronology-fix commit `96fee34cf5a81ef59e0f67256886fa15c8b9bd40` has completed PR CI SUCCESS: https://github.com/kims34/openpilot-opkr/actions/runs/40796553100 . This only validates synthetic code.

Added `hypothetical_round_trip`: long-only hypothetical round-trip cash arithmetic. All seven fields are mandatory: assumed entry and exit execution prices, quantity, total entry fee, total exit fee, total tax and total other costs. Prices must already reflect execution spread/slippage; do not subtract them twice as cash costs. Missing taxes/exit/quantity or negative costs and non-integer/bool inputs are rejected. This function is separate from the quote detector and never converts a detected discount into an exit price, fill probability or return series. The breakeven price is an integer KRW ceiling under fixed assumed cash costs, not a tax-aware schedule or a valid exchange-tick order.

Executed nine **arbitrary sensitivity scenarios**, each assuming 100 shares bought at KRW 10,000 (KRW 1,000,000 entry notional). Rows are assumed execution-price increases; columns are assumed total costs expressed as a percentage of that entry notional, not published brokerage/tax rates. The runner groups all hypothetical cash deductions in other_cost and explicitly sets the three remaining components to zero **for arithmetic only**, not because real taxes/commissions are zero.

| Assumed executed price increase | KRW 1,000 total cost (0.10%) | KRW 3,000 (0.30%) | KRW 5,000 (0.50%) |
| --- | ---: | ---: | ---: |
| +0.10% (sell 10,010) | 0 | -2,000 | -4,000 |
| +0.30% (sell 10,030) | +2,000 | 0 | -2,000 |
| +0.50% (sell 10,050) | +4,000 | +2,000 | 0 |

Values are **hypothetical net KRW**, conditional on both assumed executions and fully specified assumed costs. No fill process, adverse selection distribution, attempt rate, observed opportunity frequency, no-fill/partial-fill economics, markout series, actual tax model or annualisation exists. Thus this table does NOT validate the opening-dislocation hypothesis. A positive quote-to-fair discount does not establish a positive realised exit.

Local verification: **27/27 synthetic tests PASS** (21 snapshot/replay + 6 cash arithmetic). Tests include independent expected cash reconciliation, omitted cost rejection, each cost's monotonic effect on net, explicit non-admission flags, invalid/zero fill-size rejection and breakeven ceiling at fractional per-share cost. Remote CI for the new code must be checked separately.

Official source review: Kiwoom's own REST examples identify ka40009 as ETF intraday NAV status and 0G as ETF NAV subscription:
- https://github.com/Kiwoom-Securities/Kiwoom-REST-API/blob/main/examples/%EA%B5%AD%EB%82%B4%EC%A3%BC%EC%8B%9D/ETF/get_domestic_etf_intraday_nav_status.py
- https://github.com/Kiwoom-Securities/Kiwoom-REST-API/blob/main/examples/%EA%B5%AD%EB%82%B4%EC%A3%BC%EC%8B%9D/%EC%8B%A4%EC%8B%9C%EA%B0%84%EC%8B%9C%EC%84%B8/subscribe_domestic_etf_nav_async.py

API existence alone does not demonstrate subsecond historical depth/receipt chronology, access entitlement, foreign futures/FX fair-value lineage or successful registered-PC REAL WS authentication. No new provider acquisition performed.

**Current outcome: EMPIRICAL PROFITABILITY UNVERIFIED / NO-GO.** Actual verified opening datasets and trades used in this continuation: zero. EV, win rate, PF, CAGR, MDD and ES remain unavailable, never zero-filled. Next necessary evidence is authorised source-original, timestamp-defined book/trade/NAV plus independent futures/FX observations and ETF/account-specific charge treatment. No live trades, deployment, broker login, merge, permission/Frozen/Holdout/Champion changes. ORDERING remains DISABLED.

## 2026-10-29 KST — actual source-path audit and operational access blocker

This continuation investigated acquisition dependencies instead of treating further synthetic test counts as empirical progress.

### Direct repository evidence

Read current development branch `index-alert-position-regen-fix-v1` file `kiwoom_real_type00_readonly_smoke.py`, Git blob `a8c24b14464b14ca1bdd86ef82a05db72a1bb9d8`. The existing module logs in and subscribes exactly `{"item": [], "type": ["00"]}`. It processes only type `00` events and retains `REAL_ORDERS_AUTHORIZED=False`.

PR #349 is confirmed closed/merged into the development branch; its purpose is read-only transport/account-event smoke, not ETF market capture. A successful type00 subscription is NOT book/trade/NAV dataset admission. Do not simply repurpose this account-event observer or weaken its guard to collect new market types.

### Official NAV timestamp semantics

The Kiwoom-Securities official `subscribe_domestic_etf_nav_async.py` example labels:
- realtime type `0G`: ETF NAV;
- field `36`: NAV;
- field `20`: **체결시간 (trade execution time)**.

Source:
https://github.com/Kiwoom-Securities/Kiwoom-REST-API/blob/main/examples/%EA%B5%AD%EB%82%B4%EC%A3%BC%EC%8B%9D/%EC%8B%A4%EC%8B%9C%EA%B0%84%EC%8B%9C%EC%84%B8/subscribe_domestic_etf_nav_async.py

This example alone does **not** establish field 20 as NAV computation/publication time. A future adapter must not automatically populate `nav_at_ms` with field 20 or local receipt time and claim NAV freshness. Preserve separately original field semantics, receipt UTC/KST and monotonic capture time, clock uncertainty, NAV valuation-age unknown status, gaps and source bytes/digest privately. Unknown NAV age must remain an explicit blocker for real-data freshness validation. Local receipt proves when a value arrived, not when its underlying basket was valued.

### Operational check result

Railway `list_projects` read failed with `UNAUTHORIZED`: **This app connection requires reauthentication. Reconnect the app and try again.** Therefore no current service, worker, volume, source count, WS status or deployed ORDERING variable was observed. Do not report the old 8050 as a newly reproduced failure or claim the deployed ordering state verified. Source code disables orders; current remote runtime remains unobserved.

### Concrete handoff

1. Reauthenticate the existing Railway app connection to resume **read-only** service/log discovery. No new project/service/credential, deploy/restart or config change is needed for this access recovery.
2. Read the latest existing smoke's redacted terminal result, including WS_LOGIN_OK and TYPE00_REG_ACK_OK, without rerunning brokerage authentication.
3. Independently define and verify the market observation path: ETF trades/book/NAV, market-session/VI timeline and separately licensed futures/FX. Type00 account events cannot supply these market records.
4. Before any newly authorised observation, resolve NAV timestamp/update policy, capture original receipt chronology and explicit data rights; do not infer millisecond precision from HHMMSS trade time.
5. Only admitted real observations may support fill-aware after-tax performance. Current actual original datasets/trades newly accessed: **0**. Net EV/win rate/PF/CAGR/MDD remain unavailable. No fresh synthetic scenarios were presented as measured returns.

No collection, broker login, service mutation, merge, deployment, Frozen/Holdout/Champion or order authority changes occurred. The research branch remains Draft and code-level ORDERING=DISABLED.

## 2026-10-29 15:22 KST — Railway restored; ONE actual isolated auth probe failed at TOKEN

### Restored platform visibility and actual packaging evidence
Railway IndexAlert project and production environment are readable again; previous UNAUTHORIZED snapshot is historical. Current `indexalert-kiwoom-real-readonly-run` start command only prints `INDEXALERT_START_COMMAND_ATTESTED_NO_NETWORK=true` and exits. Its platform SUCCESS does not establish broker transport.

Retrieved 52 historical build log entries for failed Oct-8 deployment `028c7110-5cbf-457b-b1a6-539c818280b0`. They prove that build selected `Dockerfile.krx-historical-worker` and failed due to missing KRX/model COPY inputs, rather than completing a Kiwoom smoke.

Inspected existing pinned commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`: dedicated smoke Git blob `a8c24b14464b14ca1bdd86ef82a05db72a1bb9d8`, root dedicated Dockerfile and config exist. Current isolated repo-service config already specifies `/kiwoom_real_readonly`, `Dockerfile`, `python -B smoke.py`, restart NEVER. Attempt to stage a legacy custom railway.json path was rejected as deprecated (INVALID_ARGUMENT); no patch resulted. A subsequent exact current-config stage request was a no-op; get-staged-changes confirmed nothing staged. No legacy-config workaround or project-wide IaC migration was applied.

### Actual one-shot execution
Re-executed existing isolated repo-service `indexalert-kiwoom-real-readonly` from its existing archived deployment build path, without changing credentials, variables, order/account permissions or production runtime. New deployment:
`a77fb922-b679-4d88-92c4-03054ec579cd`, created 2026-10-29 15:21:36 KST.

New build actually installed the two smoke dependencies and copied `smoke.py`. Railway terminal status **SUCCESS**, but the application diagnostic at **2026-10-29 15:22:02 KST** is **authentication FAILURE**:
- STAGE=TOKEN, RETURN_CODE=3, DETAIL_CODE=8050.
- TOKEN_OK=false; ACCOUNT_ENDPOINT_OK=false.
- WS_CONNECTED=false; WS_LOGIN_OK=false; TYPE00_REG_SENT=false; TYPE00_REG_ACK_OK=false.
- ORDERING=DISABLED; REAL_ORDERS_AUTHORIZED=false; FUNDS_MOVEMENT_AUTHORIZED=false; PERMISSION_CHANGE_AUTHORIZED=false.
- Zero market data, account events, broker executions or empirical strategy observations admitted.

**Interpretation correction:** existing old smoke reports ERROR_CLASS=TOKEN_OR_LOGIN_AUTH for 8050. Kiwoom-Securities' current official helper source places 8050 in DEVICE_AUTH_CODES and raises DeviceAuthenticationError:
https://github.com/Kiwoom-Securities/Kiwoom-REST-API/blob/main/kiwoom/core/errors.py
Preserve the actual old raw classification for audit, but interpret this fresh receipt as a **device-authentication class failure at OAuth token issuance**. It is NOT a newly observed WebSocket-login failure, stale-token expiry proof or proof that a particular IP registration is missing. The exact designated-device/account policy cause still needs confirmation in Kiwoom's authenticated device settings. Keys/secret values were never retrieved or printed.

No blind retries after this failure. The one-shot policy is NEVER, not a recurring authentication loop. No staging patch remains. No H5/M20/Frozen/Holdout/Champion change, no merge, no empirical backtest or trade. Platform build/deploy SUCCESS must never be promoted to authenticated broker success or profitability acceptance.

### Next blocking dependency
Resolve the existing credential's designated-device authorisation for the actual intended execution environment (the server request and a registered local-PC request are distinct). Do not weaken device controls, rotate/expose keys, or assume a user's PC registration authorises this Railway request. After that issue is resolved, a separately controlled single read-only check is required before any ETF observation path or after-cost performance test.
