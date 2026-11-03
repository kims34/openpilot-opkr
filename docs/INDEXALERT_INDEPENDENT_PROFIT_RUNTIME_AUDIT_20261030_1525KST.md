# IndexAlert independent profitability and isolated runtime audit — 2026-10-30 15:25 KST

**Read-only verification, with this one new isolated documentation receipt only.** This does not authorize data admission, a backtest, deployment, PR merge, holdout access, model selection, capital movement, credentials, Champion promotion or orders. Avoids edits to source-owner and optimization branches. Prior detailed 14:51 audit: `docs/INDEXALERT_PROFITABILITY_READONLY_AUDIT_20261030_1451KST.md` (blob `c3498871a85d0fc1ac3dfe94fdb86ebc9dd68826`).

## Directly re-read GitHub refs (before this documentation commit)

| Scope | Exact SHA | Status |
|---|---|---|
| research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | frozen upstream; no admission |
| development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | not modified |
| Draft PR #414 integration head before write | `50d01a99b95be0f05ddc03746a2a0308c1798d65` | unmerged |
| Draft PR #412 DART | `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | unmerged |
| Draft PR #413 isolated optimization | `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` | unmerged |
| Draft PR #418 one-runner candidate | `2f98401cc50a6c6a25808a98516efd5bf0c944ee` | unmerged |
| KRX specialist `indexalert-krx-pit-source-audit-20261013` | `073d2d49e95f69fb10b943b93e51bb179fb3c698` | no source admission |
| Draft PR #416 investor-flow | `053de553646fc4765d2616544ca1e8d6bbdde35f` | unmerged |
| Draft PR #420/#422/#423 | `fab3cbbd63a951a4e081f9e7f08c1391ca308581` / `c14857620973531013799e44625d43080904fd5f` / `0e38004363cac9fc4475556b3a1c445de9af407f` | all draft/unmerged |

## Independent cross-check: runtime source lineage, not just CI conclusion

Direct `fetch_file` of `research_v1_runtime_manifest.py` Git blobs at three exact refs:
- PR #418 **head** blob = `108f66714602a1bd3ae42c34dcca7c16e38f460b` (original expected pin).
- PR #413 **head** blob = `e0055c66c59398fd4a1158077446d886b54c4e37`.
- PR #418 GitHub **merge commit** `052cf67e45500baad771527753744289529ecbc2` blob = `e0055c66c59398fd4a1158077446d886b54c4e37`.

Thus the [archived pinned-parallel CI #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`, fails for a **real branch/merge source-identity mismatch**; the archived pin must **not** be silently rewritten. Its log also says 22 package distributions checked and versions matched, but `exact_wheel_hashes_verified=false`, `os_native_dependency_identity_verified=false`. **Archived replay parity: FAIL / cache FAIL-CLOSED**. No claim of hostile tampering.

The separate [candidate merge source audit #39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494), job `117628139749`, reports 22 checked files and four candidate blobs verified, but `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`. **Candidate shape: limited PASS; full reproducibility: NOT VERIFIED**. This successful *candidate* check does not overturn the archived replay FAIL.

[PR #413 offline CI #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) six jobs PASS and immutable 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; job `115670744341` serial **1.7650 s**, parallel longest **2.7079 s** (ratio **0.652**, *slower*). [PR #418 one-runner CI #39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562), job `117628139856`, pinned **34-case** serial **2.3911 s**, parallel **2.0755 s**, ratio **1.1521x** test-phase only. Its separate **4-case synthetic** checks are not the 34-case benchmark; no 15x headline extrapolation. **Full GitHub CI / real admitted-data backtest acceleration: NOT VERIFIED.** No new benchmark was executed in this audit.

## Original financial and KRX source gates

[OpenDART 2021 original #40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066), job `121379096007`: declared original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, 1,728 table shapes, 13 operating-label candidate tables, **0** strict same-table Q3 period matches; original 2021 standalone 3-month CFS profit, 2022 comparator, complete amendments, exact public available-at **NOT VERIFIED**. [OpenDART 2022 original #38392847048](https://github.com/kims34/openpilot-opkr/actions/runs/38392847048): original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb`, 15 candidate rows, no approved strict 2022 Q3 3-month CFS binding or original-vs-correction lineage. These SHA values were read from official job logs, **not independently recomputed from downloaded original bytes in this audit**.

KRX Railway historical private 2017–2022 weekday pair SHA integrity **1565/1565 prior PASS only**, 90 session/calendar-source-gap cases, 12,003 zero-activity OHLC cases, and separate prospective 2026-09-28 27 nonpositive common-stock OHLC remain **quarantined**. Official session, security/issuer PIT history, halts, delistings, corporate actions, realistic fills, lot-size, costs, sell taxes and 2x-cost stress: **NOT VERIFIED**. Draft PR #422/#423 exact-day comparators have no independently authorized real private volume audit; offline fixtures are not official PIT.

## Railway production and safety — direct read-only 2026-10-30

Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, production environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS, **1 running**; runtime logs show `COMMON_OHLC_NONPOSITIVE`, admission/order flags false. Last returned runtime evidence remains from 2026-10-29, not proof of fresh successful market collection.
- 100 returned proxy HTTP entries for `/anchor/latest`: **100 HTTP 404**, latest returned 2026-10-29 17:21:16 UTC; a 404 may mean missing/invalid anchor rather than missing API route. Response body/private anchor file not independently verified.
- `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` marked SUCCESS, but **0 running / 1 crashed** replica; prior token 8050 and WS disconnected remain unremediated by verified new evidence. Do not mistake dashboard Online label for healthy execution.
- KRX historical worker `16c93d7c-7cd0-4d84-a327-298d2805376c` deployed SUCCESS, with no fresh private source replay in this run.
- Environment has a **staged** patch ID `e113dacb-6705-4416-9997-dc694539d382`, with zero listed changes; **do not accept/deploy** without separate approval. No deployment or service setting changed here.

[Read-only Watchdog #40988735313](https://github.com/kims34/openpilot-opkr/actions/runs/40988735313), job `123845746566`, passed policy tests but explicitly says `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`.

## Final decision and next independently admissible evidence

- Original filing + 2021/2022 strict standalone Q3 CFS 3-month period/lineage/public available-at: **NOT VERIFIED**.
- KRX official calendar/security-day PIT, issuer mapping, corporate actions, executable costs/tax/fills: **NOT VERIFIED**.
- Frozen H5 and consumed Holdout: **NO REUSE**; M20 horizon20/purge20, WF504/126/126, sealed Holdout/Purged/CPCV, Champion/Top3/NO_TRADE and predeclared risk/fee thresholds unchanged.
- M20 source gate and performance run: **NO-GO**; after-tax NetEV/PF/CAGR/MDD/ES95/ES99/concentration and annual risk-adjusted net profit: **NOT EVALUABLE**.
- Cache: **FAIL-CLOSED** unless independently approved source/data/code/Frozen policy/runtime/evidence SHA-256 and full dependency chain all match. Only immutable independent read-only postprocessing may parallelize; no dependent retraining or capital transition parallelization.
- `ORDERING=false` maintained as a policy and observed in offline CI; no new order authority inferred from service health. No market replay, economic run, workflow edit, merge, deploy, trade, money movement, permission change or Champion promotion.

**Next step:** source owners must provide independently checkable original archive bytes/first-publication and correction vintage with exact period semantics, plus official KRX day/security/issuer/tradability/price and execution evidence. After separate gate approval, evaluate only the preregistered one-time Frozen M20; never reuse consumed H5/Dynamic Holdout or infer alpha from synthetic parity.
