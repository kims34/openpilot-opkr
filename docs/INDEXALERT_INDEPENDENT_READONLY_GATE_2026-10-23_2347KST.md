# IndexAlert independent read-only gate — 2026-10-23 23:47 KST

**Purpose:** periodic immutable-ref check only; no duplicated specialist experiment, strategy change, official market backtest, workflow edit, deployment, merge, or trading authority. This is a new audit snapshot, not a source/PIT approval.

## Directly read GitHub refs
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Integration Draft PR #414 at audit start: `34447a64e4379c66559722158baf39b142584a65`; existing frozen ledger `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Latest prior audit `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-23_2324KST.md` blob `6015d44a931d04bc33a036fddb784c6ccf46df4f`.
- OpenDART Draft PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Optimization Draft PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; dependent Draft PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft PR #420/#422/#423: `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f`. All these PRs remain open Draft and unmerged.

## Directly checked GitHub Actions job logs
- [OpenDART official bounded #39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351): 2/2 SUCCESS. Job `120188625190` returned 2026-10-22 official index status `013`, zero newly indexed target 2022-Q3 corrections/attachments **within that single elapsed day**. Artifact `12471308613`, uploader-reported ZIP SHA-256 `02e829d3a5fdde8754f649431363c74221eb192b78b8237c911f74b54325820c`; **not independently downloaded/rehashed**. Does not prove original public available-at or standalone 2022/2021 3-month CFS accounting cells.
- [KRX synthetic #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438): job `119612852155` SUCCESS on offline synthetic exception checks. No actual private source-day set or official issuer/day tradability reconciliation.
- [Optimization archived source gate #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478): job `117628139395` FAIL CLOSED: `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Intentional frozen archive drift rejection, not demonstrated corruption. Limited candidate audit does not pin all transitive imports/wheel/native environment or authorize merge. Prior 34-case fixed outcome digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` remains only an offline regression control.
- [Repository watchdog #39960664266](https://github.com/kims34/openpilot-opkr/actions/runs/39960664266): job `120437538193` SUCCESS at 2026-10-23 22:22 KST; log `read-only evidence metadata: COMPLETE`, `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Artifact `12503843353`, uploader-reported SHA-256 `ddbf120309eacc2918e78831f59b8ed63f48143b4a759b12fdcee37bf3f6b38c`. Metadata completeness is not source/PIT, economics or live production proof.

## Railway read-only check
- Direct `list_projects` call returned `User input required but current turn is running in a non-interactive mode.` Latest production deployment, runtime logs, replica health and actual live `ORDERING` **NOT REVERIFIED**. No credentials, permission or configuration were changed. Interactive Railway connection resolution is required for a future live attestation.

## Independent decision
- **PASS (narrow):** cited offline CI, bounded completed-day DART index query, and previously documented raw storage integrity only.
- **FAIL CLOSED:** immutable archived #418 manifest implementation blob drift.
- **NOT VERIFIED:** original first-filing exact public available-at; first-edition 2022 and 2021 standalone July–September consolidated operating-income cells (period/sign/unit/currency) and amendment lineage; historical issuer/security PIT mapping; official KRX exchange calendar, status, corporate actions, execution feasibility; independent fees/taxes/slippage and after-tax NetEV/PF/CAGR/MDD/ES95/99, concentration, time robustness. No new independent economic source admission compared with 23:24 audit.
- **M20 PIT and economic RUN NO-GO.** Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/sealed Holdout, Champion, Top3/NO_TRADE and pre-fixed cost/tax/risk/promotion gates unchanged. Consumed H5 Holdout and retrospective Dynamic outcomes cannot be reused. Require `ORDERING=false`; GitHub offline flags do not attest actual live config.
- No official-market return experiment, new model search, M20 economics, cache authority promotion, orders, funds, permissions, deployment, workflow edits, PR merge or Champion promotion. Specialist branches untouched.

**Next independent proofs:** DART owner original 3-month CFS accounting semantics/publication clock; KRX owner exact private day-set and official as-of tradeability/corporate actions; optimization owner transitive SHA closure/full CI timing; Railway interactive read-only access for live evidence. No routine user notification warranted.
