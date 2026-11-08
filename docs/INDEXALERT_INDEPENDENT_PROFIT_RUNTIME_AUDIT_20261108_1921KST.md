# IndexAlert independent audit — 2026-11-08 19:21 KST

Scope: read-only evidence inspection; no market profitability run, model search, merge, deployment or ordering.

## Exact source refs
- Research HEAD: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub branches API).
- Development HEAD: `1e6367d2863a86c3470da13d81a955d277eba485`.
- PR #414 head `18c5418d9684d1717df58261ea27f28e514385b2`; integration gate file content read from its branch; previous recorded blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be` not recomputed here.
- PR #412/#413/#414/#418/#420/#422/#423 all OPEN and Draft (fresh connector reads).
- Actions 38381997417, 38382214223, 38419111311: 6/6 success each; 38419649711: 1/1 success; 38419439742: 2/2 success; 41515392296: auto-anchor FAILURE, validation SKIPPED. These are job conclusions, not independent economic proof.
- Historical 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and serial 2.9656s vs concurrent 2.6209s were supplied prior evidence, not recalculated.

## Railway fresh evidence
Production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Backend and Push latest deployments FAILED; PIT rebuild, KRX worker, runtime and real-readonly latest deployments SUCCESS; numReplicas null for all in this status response, so actual health NOT VERIFIED. stagedChanges null; empty staged patch `e113dacb-6705-4416-9997-dc694539d382` remains pending. No deploys applied.

At 2026-11-08 18:30, 18:45, 19:00 and 19:15 KST, PIT rebuild runtime logs repeat `KRXProspectiveOpenAPISourceError`, `COMMON_OHLC_NONPOSITIVE`, 803 common stock rows, 27 nonpositive OHLC rows and 27 zero-volume/value rows; source_failure_session 2026-09-28; `status=FAIL_CLOSED`, `ordering=DISABLED`, `fresh_alpha_observation_admitted=false`, `session_manifest_sha256=null`. This is a repeated rejection of a historical source session, not evidence of 27 new bad stocks on 2026-11-08. KRX worker and real-readonly deploy logs: zero entries in queried 18:00–19:30 KST window. Runtime logs present, not source approval.

## Verdict
- Offline synthetic CI job outcomes: PASS for specified jobs only; actual full CI and market-backtest speed-up NOT VERIFIED.
- Chronology Anchor workflow: FAIL; validation SKIPPED.
- Prospective H5 source admission: FAIL_CLOSED (27 rejected OHLC rows, source failure session 2026-09-28); no new admission.
- 2017–2022 KRX 1565/1565 private raw-pair storage integrity: historical PASS only; official trading calendar, corporate actions, execution feasibility and taxes NOT VERIFIED.
- Original filing/public available-at PIT, 2021/2022 first three-month consolidated operating profit period and correction lineage, historic issuer/security mapping: NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, time robustness, risk-adjusted after-tax annual net returns: NOT VERIFIED.
- M20 admission: NO-GO. ORDERING=false. Frozen H5/M20 horizon20/purge20/WF504-126-126 unchanged. No holdout reuse, no economic tests, no champion promotion.

Next: independent original-filing chronology proof and official KRX status reconciliation from approved SHA-bound source artifacts; resolve repeated 2026-09-28 OHLC rejection in source-owner track without modifying frozen gates; compare SHA-anchored offline runner parity only. No workflow changes or other team code touched.
