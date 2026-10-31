# IndexAlert independent profitability + runtime audit — 2026-10-31 00:24 KST

**Mode:** read-only verification of GitHub/Railway, documentation-only record. No source/model/CI workflow modification, no backtest, no merge/deploy/order, no authority change. The read-only checks below were executed in this audit; previous proof is labelled as historical rather than fresh independent replay.

## Exact HEAD and ownership boundaries (GitHub connector reads)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- KRX PIT owner `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`
- Draft PR #412 OpenDART: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`
- Draft PR #413 parallel optimizer: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- Draft PR #414 integration: `df04df9ed5ce23610f7e89d2214c915224d03cad`; integration document blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`
- Draft PR #416 investor-flow: `053de553646fc4765d2616544ca1e8d6bbdde35f`
- Draft PR #418 one-runner: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- Draft PR #420 KRX session: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`
- Draft PR #422 KRX 2021: `c14857620973531013799e44625d43080904fd5f`
- Draft PR #423 KRX 2022: `0e38004363cac9fc4475556b3a1c445de9af407f`
- No owner branch or specialist code was edited. Drafts remain unmerged.

## Profitability gate — source-to-economics
- **PASS, limited:** historical 2017–2022 private KRX 1,565/1,565 weekday daily/master source-pair hash/integrity receipt previously verified. This is **not** a fresh private-volume re-hash in this run and is **not** official calendar/tradability admission.
- **PASS, limited:** prior first-edition 2022 OpenDART original SGML source identity / raw ZIP integrity; [Action 38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) has 2/2 successful jobs and 15 original/correction candidate-row signatures, **not** 15 proven original CFS 3-month facts.
- **NOT VERIFIED:** 2022 and 2021 original first-3-month CFS operating-income account/period semantics, amendment lineage, exact first-public available-at, issuer/security historical mapping. [Action 38508181214](https://github.com/kims34/openpilot-opkr/actions/runs/38508181214) is 1 success / 1 failure; original current-normalized CFS attempt failed, evidence artifact ZIP SHA-256 `53bc73cef55f4484be1f3cd43d9a4fcaa706c49d0629c5dbb526f5e48e29a03f`. Current-vintage API cannot prove original-as-of even if it succeeds.
- **NOT VERIFIED:** 90 uncertain historical exchange-calendar/source-gap sessions, 2021/2022 private exact-set market-day admission, KRX stock-day official trading state, corporate actions, fillability, realistic fees/slippage/taxes. KRX synthetic CI success is not original market authority. PR #420 Action 39714369438 1/1 success; PR #422 Action 39001836000 1/1 success; PR #423 Action 39714207925 1/1 success.
- **NOT EVALUABLE:** post-cost/tax annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, return concentration and temporal robustness. M20 official market profitability run **NO-GO**; H5 failed/consumed holdout and Dynamic results cannot be recycled.
- Source-only new CI: PR #412 Actions [40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758) and [40263181687](https://github.com/kims34/openpilot-opkr/actions/runs/40263181687) each 1/1 synthetic/offline success, not real original-edition semantic admission. PR #416 Action 40262192831 2/2 offline source-boundary success, not investment alpha.

## Isolated runtime optimizer gate
- PR #413 historical Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), and newer [38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) all 6/6 jobs successful. Historical archived 34-case outcome digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is the immutable parity reference, not a speed or economic proof.
- PR #418 [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711) 1/1 historical success. Later [39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) 1/1 one-runner synthetic success, 34-case parity digest unchanged; observed test-phase serial 2.3484s, parallel 2.0154s, phase ratio 1.1650x (run-specific, **not** full CI or official backtest speedup). [39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) 1/1 candidate source audit success **but** report explicitly `candidate_approved_for_merge=false` and `all_transitive_imports_pinned=false`.
- **FAIL (correct fail-closed behavior):** [39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job 117628139395, aborted with `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`. These are 40-hex Git blob identifiers in the log, not SHA-256 data approvals. Do not treat other green CI jobs as overriding this failure; no merge or acceleration admission.
- Cache must require independent SHA-256 of admitted source/data/code/Frozen policy/runtime/approval evidence, and fail closed on absent/mismatch. Only independent read-only postprocessing may parallelize; dependent refit/capital transitions may not.

## Railway read-only production evidence
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- `indexalert-pit-rebuild` live deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS; most recent returned explicit prospective log at **2026-10-30 14:46:37Z = 23:46:37 KST**: `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `27/803 common-stock OHLC nonpositive`, `source_failure_session=2026-09-28`, `fresh_alpha_observation_admitted=false`, `independent_source_admission_verified=false`, `ordering=DISABLED`, `live_order_authorized=false`, `real_orders_authorized=false`, `funds_movement_authorized=false`.
- `indexalert-krx-historical-worker` deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` SUCCESS, attached volume; no fresh worker deploy log entries returned; do not claim private raw volume was rehashed.
- `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS, one running replica; live ETF alert quotes observed through 2026-10-30 15:23Z, but those public quote logs are **not** M20 PIT admission.
- **Operational monitoring discrepancy (NOT VERIFIED for health):** `indexalert-kiwoom-real-readonly` status API says `online` while replica counts say `running=0, crashed=1, total=1`, despite deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS. Deployment logs contain only container start and blank message. Do not infer broker connectivity or permissions; no changes made.
- Other service status: `indexalert-push`, `indexalert-backend`, `db-query-readonly` show `offline` and warning/critical counts; not enough to conclude the installed app push has stopped. `environment_status` additionally lists a **staged** patch `e113dacb-6705-4416-9997-dc694539d382` started 2026-10-29 06:20:53Z, `changes=[]`. Do not apply, discard, or assume it is live. This differs from previous audit's 'no pending work' wording and should be tracked as read-only anomaly.

## Verdict and next safe step
1. Original-filing/PIT **NOT VERIFIED**; historical private source storage integrity **limited PASS**; 27 bad OHLC **FAIL_CLOSED**; actual tradeable KRX states **NOT VERIFIED**.
2. Offline optimizer fixed-case parity **limited PASS**; pinned parallel-only PR #418 check **FAIL** on source blob drift; actual CI / full-backtest speedup **NOT VERIFIED**.
3. All market economics **NOT EVALUABLE**. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/Holdout/Champion/Top3/NO_TRADE, taxes, fills and promotion gates unchanged.
4. Next: obtain independent original 2022/2021 CFS 3-month public-at semantic receipts and official KRX calendar/tradability/CA before M20; reconcile #418 pinned source blob and transitive imports *only in its specialist isolated workspace* with synthetic tests; read-only recheck staged patch and contradictory Railway replica state. No authorization to deploy, merge, change credentials, trade, or lift ORDERING=false.
