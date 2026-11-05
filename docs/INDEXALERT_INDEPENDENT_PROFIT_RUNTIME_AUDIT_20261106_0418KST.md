# IndexAlert independent profitability/runtime audit — 2026-11-06 04:18 KST

Scope: read-only inspection; no PIT approval, economic backtest, deployment, merging, ordering or trading.

## Fresh independent evidence
- GitHub branches index-alert-research-v1 and index-alert-position-regen-fix-v1 exist; exact HEAD commit SHA not resolved by branch-search interface: NOT VERIFIED.
- Open PR search returned #412 #413 #414 #418 and KRX #420 #422 #423; exact HEAD SHA and draft flags were not supplied by this search: NOT VERIFIED.
- Integration gate document requested at docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md on research branch returned HTTP 404; not evidence that document is missing from PR #414.
- GitHub Actions jobs independently checked: 38381997417 6/6 success; 38382214223 6/6 success; 38419111311 6/6 success; 38419649711 1/1 success; OpenDART 38419439742 2/2 success. These are offline software tests only.
- Chronology Anchor 41515392296: auto-anchor FAILURE specifically at step 'Fetch today's public hash-only prospective payload'; validation SKIPPED. This is a concrete upstream chronology blocker, not a PIT approval.
- Railway project IndexAlert production: PIT rebuild service 225f2279-d728-4e1a-a3f3-2447ff0f9dc1 status SUCCESS, KRX historical worker 003812ee-102b-42b6-bda4-36925885b428 status SUCCESS. Deploy log query from 2026-11-05T18:00Z returned zero entries for both; cannot establish current OHLC behavior or successful ingestion.

## Evidence classifications
- Synthetic offline CI execution: PASS for enumerated jobs only.
- Prospective chronology anchor: FAIL for upstream payload fetch; validation NOT VERIFIED (skipped).
- KRX 2017–2022 private weekday pair 1565/1565: historical storage integrity PASS only (prior evidence, not rehashed this run).
- KRX official sessions, halts, corporate actions, fillability, costs and taxes: NOT VERIFIED.
- OpenDART original filing/public available-at and 2021/2022 first-quarter consolidated operating profit amendment lineage: NOT VERIFIED.
- Historical entity-security mapping: NOT VERIFIED.
- NetEV/PF/CAGR/MDD/ES95/ES99, concentration and temporal robustness after costs and tax: NOT VERIFIED.
- 34-case parity SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 and regression-phase 1.1315x: previous evidence only, not recomputed. End-to-end acceleration NOT VERIFIED.
- M20: NO-GO. ORDERING=false/disabled is required; current runtime flag was not independently fetched in this run.

## Next isolated work
Resolve the public chronology payload fetch failure with read-only log/artifact inspection; obtain exact immutable PR/branch HEADs and #414 document at PR head; reconcile 27 nonpositive OHLC rows against official KRX status/holiday/corporate-action provenance. Only synthetic offline safety and software validation before independent original-filing/PIT approvals. Preserve Frozen H5, horizon20/purge20, WF504/126/126, holdout protections, strict SHA cache gates, sequential capital transitions, and no live trading or deployment.
