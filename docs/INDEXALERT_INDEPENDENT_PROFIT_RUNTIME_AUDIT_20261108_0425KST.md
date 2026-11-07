# IndexAlert independent profit and runtime audit — 2026-11-08 04:25 KST

Scope: read-only evidence review; no official economic run, no code/workflow/production changes. Independent isolation branch indexalert-independent-audit-20261108-0425kst.

## Pinned refs
- research index-alert-research-v1 HEAD df474df348f22aa38b1dedaa59fcff66e548b406 (GitHub fetch_commit by branch).
- development index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485.
- PR #414 head indexalert-profitability-integration-evidence-20261013 SHA 18c5418d9684d1717df58261ea27f28e514385b2.
- PRs #412/#413/#414/#418/#420/#422/#423 open and draft as observed via GitHub fetch_pr. Exact HEAD SHA for PRs other than #414 NOT VERIFIED this run; branch names are not commit evidence.
- Integration gate file was not accessible on research branch (404), so file content and blob SHA not revalidated this run.

## Actions independently read
- 38381997417, 38382214223, 38419111311, 38498552499: 6/6 job success each.
- 38419439742 OpenDART: 2/2 job success.
- 38419649711 one-runner offline: 1/1 job success.
- 41515392296 chronology anchor: auto-anchor failure; validation skipped.
- Existing 34-case digest 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial mocks, 28 synthetic tests and 1.1315x regression-phase timing remain historical claims; not independently recalculated from artifacts this run. Full CI and real-market speedup NOT VERIFIED.

## Railway production status (read-only)
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS, running 1/1. No deploy logs returned for 2026-11-07 18:00 UTC onward. Earlier 803 common rows/27 invalid OHLC/27 zero activity remain unresolved; latest PIT integrity PASS NOT VERIFIED.
- KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS, running 0/1, crashed 0/1. No recent logs. Historic 1565/1565 weekday private pair storage is not official calendar/market-state proof.
- Real-readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd SUCCESS but replica running 0, crashed 1: operational health FAIL; no recent deploy logs.
- Runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS, running 1/1; latest retrieved runtime messages include Investing USD/KRW HTTP errors and Yahoo fallback (2026-11-07 19:25 UTC).
- db-query-readonly one critical alert; indexalert-push one warning; indexalert-backend four warnings. Empty staged EnvironmentPatch e113dacb-6705-4416-9997-dc694539d382 persists despite zero changes; do not accept/deploy.

## Independent gate decisions
- OpenDART original filing / public available-at / 2021 and 2022 initial 3-month consolidated operating-profit period and amendment lineage: NOT VERIFIED (candidate rows or CI are not semantic/PIT approval).
- Historical issuer-security mapping, official KRX calendar, trade state, corporate actions, fills and executable costs/taxes: NOT VERIFIED.
- Post-cost/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, chronological robustness: NOT VERIFIED. No authorized M20 economics run.
- Offline CI job completion: PASS limited to jobs listed. Full speedup: NOT VERIFIED.
- PIT admission: FAIL_CLOSED; M20 NO-GO; ORDERING=false. Holdout consumed/failed H5 and Dynamic outputs may not be reused or tuned after the fact.

## Safe next steps
1. Obtain independently timestamped official original filings, 2021/2022 3-month consolidated lineages and corporate mapping with evidence SHA-256, then verify PIT.
2. Independently reconcile official KRX calendar, trade states, actions, fillability and tax/cost proofs; keep 27 bad OHLC and zero-activity records blocked.
3. Resolve chronology anchor failure and Railway crashed read-only replica, critical alert and empty staged patch without deployment or credential changes under this mandate.
4. Recheck isolated offline synthetic parity and complete wall-time evidence only; fail closed on cache SHA mismatch; never parallelize dependent retraining/capital transitions.
5. Only after independent gates and explicit required approval consider M20 economics; retain Frozen H5, horizon20/purge20, WF504/126/126, independent Holdout, Champion/Top3/NO_TRADE and ORDERING=false.

No merges, workflow edits, production deployments, orders, funds, credentials, Champion promotion, new model search or official-market performance experiments.
