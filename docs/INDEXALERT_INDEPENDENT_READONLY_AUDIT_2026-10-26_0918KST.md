# IndexAlert independent read-only gate — 2026-10-26 09:18 KST

Scope: incremental verification since the 08:47 KST audit, without modifying delegated code, workflow, data, strategy, deployment, or permissions. No new official PIT/market original was admitted. This note is an evidence delta, not a profitability result.

## Freshly fetched immutable GitHub refs
- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485`.
- Profitability Draft PR #414 HEAD before this note `500464ee690b5ead018ce2b33836211085e2d47c`; original integration gate blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` (unchanged).
- Offline optimization Draft #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; dependent runner Draft #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; OpenDART Draft #412 `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. Historical #404 closed.
- Independent PR #414 all-page changed-file enumeration: **135/135 are docs/ paths**; no non-document paths in PR diff. This proves scope of the current PR diff only, not that every document's claims are validated. Latest pre-write commit `500464ee...` changes one isolated audit markdown.

## Direct job-log rechecks this run
- OpenDART [run #39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765), job `120189157379`: SUCCESS, **synthetic-no-network**; code output `m20_feature_pit_admitted=False`, `m20_performance_run_authorized=False`, `ordering=DISABLED`. No original publication timestamp or financial-semantic PIT PASS.
- KRX [run #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), job `119612852155`: SUCCESS offline/synthetic; `m20_performance_run_authorized=False`, `ordering=DISABLED`. KRX [run #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677`: `DRY_RUN_NO_PRIVATE_STORAGE_READ`, `2022_private_candidate_date_sets_equal=False`, `ordering=DISABLED`. The false equality is a **non-admission dry-run flag**, not proof of a real private-versus-official day-set mismatch.
- Optimization [run #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: FAIL (archived source blob expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`). Offline package-version parity across 22 distributions PASS; exact wheel SHA and OS-native dependency identity NOT VERIFIED. Prior pinned 34-case SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is not rehashed here. Full CI/economic backtest speed NOT VERIFIED.
- Watchdog [run #40236925132](https://github.com/kims34/openpilot-opkr/actions/runs/40236925132), job `121300369761`: SUCCESS; `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded artifact digest `sha256:e88e266662c36879f74773b39fbb0095beff484f4f6f2d76e69f4e4e819cc159` appears in direct log; metadata match recorded in prior 08:47 audit. Neither attests Railway live configuration.

## Railway
A single read-only `list_projects({})` request this pass required interactive user input; the non-interactive execution could not proceed. No service, deployment, logs, private source, live ORDERING, or private volume was read. No alternate credential, bypass, or retry. To close this evidence gap requires user-initiated interactive Railway connector authorization, not a deployment or rights mutation.

## Independent gate matrix
- **PASS (scoped):** GitHub refs and PR #414 documentation-only file scope; directly observed offline synthetic CI and Watchdog artifact upload digest.
- **FAIL (scoped):** PR #418 strict archived blob identity; previously observed chronology anchor #39972035700 HTTP 404, not re-run.
- **NOT VERIFIED:** independently rehashed original OpenDART ZIP, original 2022/2021 first-filed standalone three-month CFS operating-income semantics, complete correction lineage, exact public available-at and issuer/security historical mapping; independently rehashed private KRX originals, official session/security trading state, corporate actions, fill realism, commission/slippage/taxes; annual after-tax risk-adjusted NetEV/PF/CAGR/MDD/ES95/99, concentration/date robustness; end-to-end acceleration; Railway live configuration. Historical 1,565/1,565 private weekday storage receipt is **not** current independent market/PIT admission.

**Decision: M20 PIT and profitability NO-GO.** Preserve Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV, sealed or consumed Holdout, Champion, Top3/NO_TRADE, original costs/taxes/NetEV/execution/risk/promotion gates. Require `ORDERING=false`; actual Railway value unobserved. No M20 returns, model exploration, official-data performance experiment, H5/Dynamic retuning, reused Holdout, orders, funds, credentials, deployment, PR merge, or Champion promotion.

Next non-overlapping gates: #412 owner original-vintage semantic and exact available-at proof; KRX #420/#422/#423 owners real private-vs-official session/tradability/corporate-action/realistic fill; #413/#418 owners source/runtime SHA closure and offline-only timing. Integration #414 performs a single preregistered independent after-tax evaluation only after all source gates PASS.
