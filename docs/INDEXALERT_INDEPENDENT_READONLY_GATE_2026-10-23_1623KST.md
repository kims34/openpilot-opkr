# IndexAlert independent source/optimization gate — 2026-10-23 16:23 KST

**Scope:** read-only evidence audit of delegated PRs and independent offline-only optimization; this document changes no source, workflow, market data, policy, deployment or authorization. It does not confer PIT, trading or merger approval.

## Immutable refs observed directly in GitHub (2026-10-23 KST)

- Research `index-alert-research-v1`: HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: HEAD `1e6367d2863a86c3470da13d81a955d277eba485`.
- Integration Draft PR #414: `b302a4cb9907a8908e6df142b58a0d25a23e3fde` at audit start; ledger `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Optimization Draft PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Downstream single-runner Draft PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft PRs #420/#422/#423: `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f`. All are open Draft, not merged.

## New official OpenDART source-index evidence (bounded, source-only)

- [2026-10-23 Actions #39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351): both offline synthetic and read-only official index jobs **PASS**. Offline job logged **16/16 tests**. The official job queried the frozen slot-5 issuer for exactly the **completed 2026-10-22 Korea-local day**, returned official status **013 (no queried periodic filings)** and zero newly indexed 2022 Q3 correction/attachment rows in that bounded query. The latest day, 2026-10-23, was deliberately not claimed complete.
- Actual official job log: `M20_2022_Q3_OCT22_INCREMENTAL_CENSUS` confirms `official_day_index_observed=true`, `query_status_013_no_periodic_filings=true`, `new_q3_2022_correction_rows=0`, `new_q3_2022_attachment_rows=0`, `m20_feature_pit_admitted=false`, `m20_performance_run_authorized=false`, `ordering=DISABLED`. Flags-only artifact ID `12471308613`, ZIP SHA-256 `02e829d3a5fdde8754f649431363c74221eb192b78b8237c911f74b54325820c`.
- Prior [Actions #39721626218](https://github.com/kims34/openpilot-opkr/actions/runs/39721626218): 2022 original-to-2026-10-21 current index bounded chronology 2/2 PASS; original first filing unique, 31 later periodic index rows, one 2022 Q3 correction and no attachment additions in queried index; flags-only artifact ID `12401173549`, SHA-256 `8deb40bd1fa9714277346d052f346dd570894bc5a356d63fcdd5580ef4d8b4d2`. Current index is not immutable historical release chronology.
- New #412 HEAD [Actions #39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) and [#39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) each 1/1 offline-only job PASS. **Not** a live original financial semantic or first-publication-time proof.

## KRX and optimization boundary

- KRX [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) and [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) offline-only PASS. Actual private 2021/2022 day-set reconciliation and issuer/security/day official tradability, corporate actions and fill feasibility remain **NOT VERIFIED**. Prior private 1,565/1,565 weekday raw-pair SHA integrity PASS is storage integrity, not PIT; 90 unresolved sessions and prospective bad OHLC remain quarantined.
- #413 [Actions #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) six jobs PASS, synthetic parity only. #418 [Actions #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) original archived source gate FAIL CLOSED: `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. This is an intended archive drift rejection, not proven corruption.
- #418 [Actions #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) candidate-source review PASS for 22 checked files, archived 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, but `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`. [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) offline one-runner job PASS; neither full CI nor actual official financial backtest speedup independently measured. Do not repin old baseline, use an unverified cache, or parallelize dependent retraining/capital transitions.

## Independent PASS / FAIL / NOT VERIFIED and execution gate

- **PASS (narrow only):** specified OpenDART current index lookup and offline fail-closed guards; synthetic KRX calendar safety checks; archived 34-case parity under documented limits.
- **FAIL (intentional safety block):** original archived #418 implementation blob SHA drift. No waiver, no merge.
- **NOT VERIFIED:** first-submitted 2022 and 2021 July–September *standalone consolidated* operating-profit accounting cells (period, sign, unit, currency), exact original first-public `available-at` timestamp, original-vs-correction cell lineage, issuer/security historical PIT mapping, KRX official trading status/corporate actions/execution, real commissions/taxes/slippage, independent after-tax NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness. H5 consumed Holdout and Dynamic retrospective results cannot be recycled.
- **Railway:** direct read-only `list_projects` returned `User input required but current turn is running in a non-interactive mode.` Latest deployment/runtime logs and actual production ORDERING setting **NOT REVERIFIED** in this run; do not claim actual live safety configuration from GitHub synthetic flags.
- **Gate:** M20 source PIT NO-GO; M20 economic RUN prohibited; Frozen H5/M20 horizon20/purge20, WF504/126/126, Purged/CPCV, independent sealed Holdout, Champion/Top3/NO_TRADE and tax/cost/risk policies unchanged. Require `ORDERING=false`. No live orders, funds, broker permissions, Champion promotion, workflow edits, production deployment or PR merge. Other specialist workspaces untouched.

**Next proof dependencies:** OpenDART owner must authenticate exact original CFS standalone 3-month cell and first-public clock plus correction lineage; KRX owner must reconcile actual private day set and as-of security status/corporate actions; optimization owner must close transitive source/environment SHA graph and measure full end-to-end CI independently. Railway session must be reauthenticated interactively before operational log attestations; do not change credentials or service settings.
