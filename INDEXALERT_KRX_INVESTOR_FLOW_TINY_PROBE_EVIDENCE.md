# IndexAlert KRX Investor-Flow Tiny-Probe Evidence

Updated: 2026-10-02 KST  
Evidence ID: `INDEXALERT-KRX-INVESTOR-FLOW-TINY-PROBE-2026-10-02-v1`  
Status: **AUTHENTICATED INVESTOR-FLOW ROUTE REACHABILITY CONFIRMED — HISTORICAL/PIT COVERAGE STILL OPEN**

GitHub Action `36976873119`, job `110742487933`, ran the explicitly consented KRX investor-flow tiny probe at research revision `1010e1001848800d76e27d902ecd3d20c6725ccc`.

The authenticated step succeeded and the push-safe dry-run step was skipped.

## Safe observed result

- source: `KRX_Data_Marketplace_MDCSTAT02303_via_authenticated_web_session`
- BLD: `dbms/MDC/STAT/standard/MDCSTAT02303`
- probe security: `005930`
- probe window: `2026-09-21` to `2026-09-23`
- rows: **3**
- columns: `일자, 금융투자, 보험, 투신, 사모, 은행, 기타금융, 연기금 등, 기타법인, 개인, 외국인, 기타외국인, 전체`
- `authenticated_request_attempted=true`
- numeric market data persisted by probe: false

## PIT rule

The project continues to freeze the official publication floor as **after 20:00 Asia/Seoul** for final day-D stock investor trading results. Day-D final values may therefore enter only a later eligible decision after publication.

## Gate effect

After this tiny probe:

- Gate A `AUTHORIZED_OFFICIAL_ROUTE`: **PARTIAL**
- Gate B `EXACT_DATASET_SCHEMA_MAPPING`: **PARTIAL**
- Gate C `HISTORICAL_COVERAGE_SECURITY_MAPPING`: **BLOCKED**
- Gate D `PIT_AVAILABILITY_LINEAGE`: **PARTIAL**
- Gate E `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`: **PARTIAL**
- Gate F `INTENDED_USE_RIGHTS`: **PARTIAL**

This tiny probe establishes authenticated reachability and the observed schema for the declared sample only. It does not establish complete history, stable security mapping across the research period, record-level PIT lineage, or full-route rights.

## Authority boundaries

The probe does not authorize:
- bulk historical acquisition;
- investor-flow feature-performance testing;
- Alpha/promotion;
- sealed holdout;
- live trading.

`feature_performance_testing_authorized=false`, `sealed_holdout_authorized=false`, and `live_trading_authorized=false`.

The next legitimate investor-flow work is historical coverage/security mapping and complete PIT lineage/provenance under a separately admitted acquisition contract.
