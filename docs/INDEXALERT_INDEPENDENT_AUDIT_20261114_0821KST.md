# IndexAlert independent audit — 2026-11-14 08:21 KST

Read-only verification, no economic experiment, deployment, merge, order, credential change or Champion promotion. Evidence below is scoped to this run; historic values are not fresh independent hashes.

## GitHub identity
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`, self-compare identical.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`, self-compare identical.
- Independent audit branch pre-write HEAD `bf2665af4980959ed7e4d5dff20a68812b4a7a77`.
- PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All open Draft unmerged.
- PR #414 integration gate file Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be` read this run. Git blob SHA-1 is not independent evidence SHA-256.

## Actions evidence (latest-attempt job status refreshed)
- [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417) 6/6 PASS; [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223) 6/6 PASS; [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311) 6/6 PASS.
- [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 PASS; [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) 2/2 PASS. Action success does not approve source semantics or PIT.
- [38486028854](https://github.com/kims34/openpilot-opkr/actions/runs/38486028854) 1/1 FAIL at step 6 `Enforce original CI regression-source blob identities before any test`; downstream test not run. Archived manifest mismatch unresolved. 34-case fixed digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` historical only, independent recomputation NOT VERIFIED. Historical serial 2.9656s / simultaneous 2.6209s = 1.1315x regression-phase ratio, NOT full-CI or official backtest speedup.

## Railway production
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. Latest deployments PIT/KRX/Runtime SUCCESS, Kiwoom real-readonly FAILED; actual replica count from get_status is null for all, therefore current process health NOT VERIFIED (describe_environment's configured numReplicas=1 is not runtime health).
- `stagedChanges=null`, but `pendingWork` still contains staged patch `e113dacb-6705-4416-9997-dc694539d382` since 2026-10-29: inconsistent control-plane views, NOT VERIFIED resolved.
- UTC 2026-11-13 22:00–23:25: PIT and KRX deploy logs each 0 entries; Runtime 181 entries, with Investing USD/KRW HTTP errors and Yahoo fallback at 23:20–23:21 UTC. No evidence of PIT or KRX source gate recovery; no inference from empty logs.

## Independent profitability gate
- Historical KRX 2017–2022 private raw-pair storage 1565/1565 PASS only for storage integrity; official trading calendar, statuses, corporate actions, historical security mapping, fillability and taxes NOT VERIFIED. 90 uncertain sessions, 12003 zero-activity records and prior 27/803 bad OHLC remain blocked; no fresh source remediation evidence.
- OpenDART SGML 15 candidate rows and matching adjacent numeric signatures are syntactic observations only; original filing semantics, 2021/2022 exact first three months consolidated operating profit, correction lineage and exact public available-at/PIT NOT VERIFIED.
- Frozen H5 consumed/failed holdout and dynamic outcomes cannot be reused. M20 horizon20/purge20, WF504/126/126, label/Purged/CPCV/independent holdout, Champion/Top3/NO_TRADE and cost/tax/NetEV/execution/risk gates unchanged.
- NetEV/PF/CAGR/MDD/ES95/ES99, return concentration, regime robustness after transaction costs and taxes: NOT VERIFIED; no approved economic run. M20 NO-GO, ORDERING=false. No performance experiment or source-PIT approval inferred from CI PASS.
- Offline optimisation permitted only for synthetic software/security checks; cache requires all independently approved input/data/code/Frozen/runtime/evidence SHA-256 and fail-closed; only read-only postprocessing parallelism; no dependent retraining or capital transition parallelism.

## Next safe steps
1. Independently resolve PR #418 archived manifest/blob identity mismatch using original immutable regression sources, with synthetic-only CI; do not alter original tests or workflow bypass.
2. Obtain official first-filing/PIT and historical KRX calendar/status/corporate-action evidence with immutable SHA and independent lineage approval before any M20 economic run.
3. Reconcile Railway pending patch vs staged=null read-only; separately verify actual running replicas; do not deploy or commit patch.
4. Independently recompute fixed 34-case SHA-256 and benchmark whole offline CI on pinned runner/environment without changing Frozen policy or consuming holdout.
