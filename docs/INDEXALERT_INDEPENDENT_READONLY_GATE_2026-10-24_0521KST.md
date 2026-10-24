# IndexAlert independent read-only evidence gate — 2026-10-24 05:21 KST

Scope: integration-only audit on isolated Draft PR #414. No strategy execution, official market performance trial, Holdout access, production change, order, funds, credentials, permissions, merge, or Champion promotion. Other delegated workstreams unchanged.

## Immutable GitHub refs observed directly

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (direct branch-ref commit read).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (direct branch-ref commit read).
- Draft integration PR #414 before this write: `f979eee12464ddfecf8944ea622a8b8b6e2f4a3b`. Original gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft OpenDART PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`; optimization PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; downstream runner PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft PRs #420/#422/#423: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, `c14857620973531013799e44625d43080904fd5f`, `0e38004363cac9fc4475556b3a1c445de9af407f`. All remain Draft, open, unmerged.

## Independently strengthened original-vs-merged optimization SHA proof

- Direct GitHub `fetch_file` of `research_v1_runtime_manifest.py` at **current PR #413 HEAD** returned Git blob `e0055c66c59398fd4a1158077446d886b54c4e37`. The same file at **PR #418 HEAD** returned Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`. These are directly retrieved blob identities, not merely values copied from a previous CI narrative.
- [PR #418 pinned archived CI #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`, failed closed because it expected the PR #418 original blob `108f667...` but observed upstream merged-context `e0055c66...`. This proves the archived original implementation is not the same as the merge-context implementation. It **does not** prove file corruption or justify repinning.
- [Candidate-only CI #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494), job `117628139749`, succeeded on bounded reviewed source evidence: `checked_files=22`, `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`, fixed archived 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` as logged. Artifact ID `12130632455`, GitHub artifact-metadata ZIP digest `sha256:e3b11f93bd67cd246c0a81c599679c83dda15176ffc687699edf5bead5e46ad8` (not independently downloaded/rehashed).
- Direct compare PR #418 HEAD to current PR #413 HEAD: `diverged`, ahead `18`, behind `49`, merge-base `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`. Original PR #413 [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) offline CI PASS; #418 standalone [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) offline-only PASS. Neither validates full transitive SHA/environment/wheel closure or end-to-end backtest/CI acceleration.
- Cache eligibility remains fail-closed on exact independently approved source/data/calculation code/Frozen policy/runtime/evidence SHA-256; receipt publisher authority, POSIX mode drift, atomic input snapshot, exact wheels and native dependencies NOT VERIFIED. Only read-only independent postprocessing may be parallelized, not dependent retraining or capital transitions.

## Official-source and KRX read-only gates

- [OpenDART official bounded #39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351) jobs `120188574365`/`120188625190` 2/2 PASS. Completed 2026-10-22 day returned official `013` no new 2022-Q3 correction/attachment in that bounded index query. Artifact `12471308613` digest `sha256:02e829d3a5fdde8754f649431363c74221eb192b78b8237c911f74b54325820c` from GitHub metadata, not independent bytes rehash. PR #412 HEAD [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) offline-only PASS.
- Earlier 2022 original ZIP `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, corrected ZIP `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30` were Action-attested source fingerprints, **not** authenticated first-public CFS 3-month financial facts. Original/corrected SGML 15 candidate operating-profit rows are not an exact 2022/2021 July–September consolidated statement lineage.
- [Prospective anchor #39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700), job `120476944660`, returned HTTP 404 for the configured `/anchor/latest` endpoint; chronology validation skipped. This is an **observed failure**, not proof of the endpoint's root cause or production health.
- KRX [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), job `119612852155`, synthetic safety PASS only. [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) offline PASS. Historical private weekday-pair 1565/1565 storage integrity previously attested PASS, but official exact session-day set, security trade state, corporate actions, order fill and 27 bad OHLC quarantine are NOT independently admitted.
- [Read-only watchdog #40002116199](https://github.com/kims34/openpilot-opkr/actions/runs/40002116199), job `120580600571`, states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. These are CI flags, **not** live Railway ORDERING verification.
- Railway read-only `list_projects` again returned `User input required but current turn is running in a non-interactive mode.` No deployment, runtime logs, replica state, or live ORDERING status can be attested; no authentication change attempted.

## Explicit adjudication and next evidence

**PASS (bounded):** GitHub branch/PR refs and two directly fetched implementation blob identities, named offline CI outcomes, selected bounded official OpenDART current index, historic raw storage SHA as previously attested.

**FAIL / FAIL-CLOSED:** original archived #418 manifest SHA on merged candidate; prospective chronology anchor HTTP 404. Do not bypass/re-pin either gate.

**NOT VERIFIED:** original 2022 and 2021 standalone consolidated Q3 three-month operating-profit values and period/unit/sign, exact first-public available-at and correction lineage, historical issuer/security PIT mapping, official KRX as-of trade state/calendar/corporate actions/fillability, source/data/code/runtime/Frozen/evidence SHA-256 closure, actual fees/taxes/slippage, independent after-tax NetEV/PF/CAGR/MDD/ES95/99/concentration/time robustness, end-to-end speedup, live Railway ORDERING.

**M20 economic RUN NO-GO.** Maintain Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/sealed independent Holdout/Champion/Top3/NO_TRADE and fixed cost/tax/risk thresholds. H5 consumed Holdout and Dynamic retrospective results cannot be reused. `ORDERING=false` mandatory, live setting not verified. Next proof ownership: OpenDART original-public-clock + CFS-cell lineage; KRX private official as-of calendar/trade status/actions; independent optimization combined transitive/runtime/wheel SHA proof and controlled whole-CI timing; interactive Railway session reauthorization before any operational attestation. No M20 performance test, source owner code edit, workflow change, order, funds, permission, deploy, merge, or promotion.
