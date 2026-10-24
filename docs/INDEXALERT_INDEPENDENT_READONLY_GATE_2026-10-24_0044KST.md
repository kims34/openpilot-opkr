# IndexAlert independent read-only profitability gate — 2026-10-24 00:44 KST

This is an isolated documentation-only evidence ledger, not a source/PIT admission, strategy backtest, financial result, workflow change, trading authorization or merge approval. Observed refs are live GitHub API results for this run.

## Immutable GitHub refs checked

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft integration PR #414: `ea9e828b1fc3dad7dbbba0a4a566865063f28d73`. Gate document `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` Git blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft OpenDART PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Draft optimization PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft downstream single-runner PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- Draft KRX PRs #420/#422/#423: `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Earlier isolated audit file `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-23_1623KST.md` Git blob SHA `0864fc755c90cfbb675bdade098e0178b7b7e8e9`.

## Fresh workflow evidence, with provenance limitations

- [Prospective Chronology Anchor run #39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700), created 2026-10-23 14:43 UTC, failed. Direct job #120476944660 logs: request to `/anchor/latest` produced `HTTP Error 404: Not Found` after fetch retries; subsequent immutable chronology record steps and validation were skipped. No chronology artifact was produced. **FAIL for this prospective anchor attempt, not proof of historical PIT.** This is a recurring known endpoint blocker, not newly confirmed root cause; do not bypass or modify workflow in this track.
- [Hourly read-only proof watchdog #39960664266](https://github.com/kims34/openpilot-opkr/actions/runs/39960664266), created 2026-10-23 13:22 UTC: job #120437538193 success, offline governance checks success. Log explicitly reports `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Flags-only uploaded artifact ID `12503843353`; uploader-reported ZIP SHA-256 `ddbf120309eacc2918e78831f59b8ed63f48143b4a759b12fdcee37bf3f6b38c`. **This SHA is CI-reported, not independently downloaded/rehashed.** Watchdog order flag is not a live Railway production setting attestation.
- Latest #412 HEAD offline-only [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) and [#39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) success; official source chronology, original first-public timestamp and exact 2022/2021 standalone CFS 3-month operating profit remain NOT VERIFIED.
- Latest #420 offline [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), #422 [#39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), #423 [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) success. No actual private day-set comparison or official as-of tradability/corporate-action/fillability admission.
- Latest #413 offline [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) success. #418 [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) pinned original source gate FAIL due to archived blob SHA mismatch, while [#39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) candidate audit and [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) offline probe success with non-admitting limitations. No end-to-end official PIT backtest speedup proven.

## Independent gate decision

- **PASS (narrow):** source-file provenance only to extent supported by previous bounded SHA receipts, isolated offline safety regressions and watchdog fail-closed checks.
- **FAIL / blocked:** prospective chronology `/anchor/latest` returned HTTP 404 and produced no immutable anchor; #418 archived original manifest blob identity mismatch remains rejected.
- **NOT VERIFIED:** exact original-filing 2022/2021 standalone 3-month consolidated operating-profit facts, period/sign/unit, first public available-at/PIT and correction lineage, issuer/security historical mapping, official KRX day/security trading states, corporate actions, fillability, true commissions/taxes/slippage, and independently reproducible after-tax NetEV, PF, CAGR, MDD, ES95/99, concentration and time robustness. H5 consumed Holdout and Dynamic retrospective results cannot be reused.
- **Railway:** direct read-only `list_projects` call returned `User input required but current turn is running in a non-interactive mode.` Latest production deployment, replica, runtime logs and actual `ORDERING` status **NOT REVERIFIED**. Reauthentication must occur in an interactive authorized session, without account changes in this run.
- **Decision:** M20 source PIT admission NO-GO; M20 profitability RUN prohibited. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV, sealed Holdout, Champion, Top3/NO_TRADE, risk, costs/tax and promotion policies unchanged. `ORDERING=false` is mandatory but production value unverified. No orders, funds, credential/permission changes, deployment, PR merge, Champion promotion, new official financial performance experiments, or specialist-code changes.

Next proof dependencies: delegated OpenDART original publication-time and CFS cell/lineage evidence; delegated KRX original private day-set and official security/day mapping and execution evidence; optimization full dependency SHA graph and end-to-end CI timing; Railway read-only session restoration. Do not treat a synthetic PASS or watcher flags as official economic performance admission.
