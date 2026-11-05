# IndexAlert independent profitability and offline runtime audit — 2026-11-06 01:18 KST

Scope: read-only source, CI and Railway inspection; isolated documentation-only write. No backtest, order, deployment, workflow, model or gate change.

## Current GitHub evidence
- Research branch index-alert-research-v1 and development branch index-alert-position-regen-fix-v1 were located by branch search. Exact current branch tip SHAs NOT VERIFIED in this run (prior research df474df348f22aa38b1dedaa59fcff66e548b406 and development 1e6367d2863a86c3470da13d81a955d277eba485 are **historical**, not re-certified current tips).
- Draft OPEN unmerged PR HEADs:
  - [#412](https://github.com/kims34/openpilot-opkr/pull/412): `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
  - [#413](https://github.com/kims34/openpilot-opkr/pull/413): `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
  - [#414](https://github.com/kims34/openpilot-opkr/pull/414): `18c5418d9684d1717df58261ea27f28e514385b2`
  - [#418](https://github.com/kims34/openpilot-opkr/pull/418): `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
  - [#420](https://github.com/kims34/openpilot-opkr/pull/420): `fab3cbbd63a951a4e081f9e7f08c1391ca308581`
  - [#422](https://github.com/kims34/openpilot-opkr/pull/422): `c14857620973531013799e44625d43080904fd5f`
  - [#423](https://github.com/kims34/openpilot-opkr/pull/423): `0e38004363cac9fc4475556b3a1c445de9af407f`
- PR #414 gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` fetched on PR branch; blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Its policy explicitly blocks M20 pending independent PIT and market admissibility.
- CI jobs fetched directly: [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311): 6/6 success each. [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711): 1/1 success. [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): 2/2 success. [41515392296](https://github.com/kims34/openpilot-opkr/actions/runs/41515392296): auto-anchor FAILURE, validation SKIPPED. Job status does not independently attest fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, 13 adversarial mocks, 28 synthetic cases or the measured 1.1315x regression-phase ratio; these remain prior evidence, not recomputed.
- Offline optimization parity: PASS for observed CI job success only; end-to-end CI speedup, official PIT data backtest speedup and economic results NOT VERIFIED.

## Railway production evidence
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c`, runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`: latest deployment SUCCESS; Backend and Push latest deployment FAILED. Deployment success is not replica or data quality proof.
- Fresh read of PIT rebuild logs returned latest observed entry `2026-11-05T14:46:31.840674221Z` (23:46:31 KST), source failure session `2026-09-28`, `COMMON_OHLC_NONPOSITIVE`: 27/803 common-stock rows nonpositive OHLC and 27 zero-volume/value rows; `FAIL_CLOSED`, `session_manifest_sha256=null`, `fresh_alpha_observation_admitted=false`, `ordering=DISABLED`, `live_order_authorized=false`. Safety veto PASS; source session admission FAIL; official exchange status/causal reconciliation NOT VERIFIED.
- Narrow 15:00Z onward log query for PIT rebuild and KRX worker returned zero deploy entries; this does not prove absence of all events or correct execution. KRX 1565/1565 weekday pair integrity PASS is prior evidence, not official trading calendar proof. Existing staged work left untouched.

## Independent gate decision
- OpenDART original byte identity and SGML candidate row counts: prior narrow source-level evidence; exact first-public available-at, first 3-month 2021/2022 consolidated operating profit and corrections lineage NOT VERIFIED.
- Historical corp/security mapping, official KRX calendar/trading status/corporate actions, executable fills, taxes and fees NOT VERIFIED.
- NetEV, PF, CAGR, MDD, ES95/99, concentration, time stability and annualized risk-adjusted net profit NOT VERIFIED; M20 economic run NOT EVALUABLE / NO-GO.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE unchanged. Used H5 Holdout/Dynamic not reused. Cache requires exact independently approved evidence hashes, otherwise fail-closed. Dependent retraining/capital transitions remain serial. ORDERING=false.
- Next safe steps: original official KRX session-by-session status reconciliation for 27 rows without deleting veto; independently establish original-filing timestamps and corrected-period lineage; reconcile immutable SHA and full CI evidence for optimization. No official profitability tests or performance search before PIT approval. No live orders, authority changes, Champion promotion, merges or deployment.
