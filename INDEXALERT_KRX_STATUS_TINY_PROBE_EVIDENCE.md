# IndexAlert KRX Status Tiny-Probe Evidence

Updated: 2026-10-02 KST  
Evidence ID: `INDEXALERT-KRX-STATUS-TINY-PROBE-2026-10-02-v1`  
Status: **AUTHENTICATED STATUS ROUTE REACHABILITY CONFIRMED — HISTORICAL/PIT AUDIT STILL OPEN**

GitHub Action `36976085781`, job `110740113447`, ran the explicitly consented KRX security/status tiny probe at research revision `db2612867b9abe90ba6d9639791904783c23e95b`.

The authenticated step succeeded. The push-safe dry-run step was skipped, as required.

## Safe observed results

- current listed-security identity: 2,873 rows
- new-listing history sample: 148 rows
- delisted-security history sample: 154 rows
- trading-halt candidate `MDCSTAT21301`: reachable, 1 row
- cleanup-trading candidate `MDCSTAT23701`: reachable, 10 rows
- `candidate_blds_live_validated=true`
- `authenticated_request_attempted=true`
- numeric market data persisted by probe: false

The exact observed column sets are frozen in `INDEXALERT_KRX_STATUS_TINY_PROBE_EVIDENCE.json`.

## Gate effect

After this tiny probe:

- Gate A `AUTHORIZED_OFFICIAL_ROUTE`: **PARTIAL**
- Gate B `EXACT_DATASET_SCHEMA_MAPPING`: **PARTIAL**
- Gate C `HISTORICAL_COVERAGE_SECURITY_MAPPING`: **BLOCKED**
- Gate D `PIT_AVAILABILITY_LINEAGE`: **BLOCKED**
- Gate E `REPRODUCIBLE_INTEGRITY_FAIL_CLOSED`: **PARTIAL**
- Gate F `INTENDED_USE_RIGHTS`: **PARTIAL**

Gate A is no longer blocked solely on authenticated route reachability. It is still not PASS because a tiny source probe cannot establish the complete historical source/product contract.

## Authority boundaries

This evidence does not authorize:

- Final Judge source readiness;
- bulk historical acquisition;
- Alpha/promotion;
- sealed holdout;
- live trading.

`judge_security_status_ready=false` and `source_contract_closed_for_declared_scope=false`.

The next legitimate status-source work is full historical coverage/security mapping, PIT availability lineage, reproducible acquisition receipts/batches, and exact status economics. No threshold may be weakened to compensate for missing evidence.
