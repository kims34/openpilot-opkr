# IndexAlert independent profitability and isolated runtime gate — 2026-10-25 04:15 KST

Read-only independent review; this is the **only** attempted write in this pass. No specialist source/workflow edits, no backtest, market profitability, holdout, order, deployment, PR merge, permissions, funds or Champion change. This document is not a source-admission authority.

## Directly resolved immutable refs
- Research `index-alert-research-v1` HEAD `3b8b7830612a6284d7c7a60628cb527cb741627a` (GitHub branch endpoint).
- Development `index-alert-position-regen-fix-v1` HEAD `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branch endpoint).
- Integration Draft PR #414 HEAD `d90d95888a0c4dcbb3b5b41227be7452a83853b0`, source gate blob Git SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft #412 HEAD `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Optimization Draft #413 HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Single-runner Draft #418 HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420 HEAD `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; Draft #423 HEAD `0e38004363cac9fc4475556b3a1c445de9af407f`. #422 independently recorded in preceding note as `c14857620973531013799e44625d43080904fd5f` (not directly refreshed here).
- All listed PR metadata read as open Draft, not merged.

## Direct source-identity and optimization separation
- `research_v1_runtime_manifest.py` on #413 has Git blob SHA-1 `e0055c66c59398fd4a1158077446d886b54c4e37`; on #418 has `108f66714602a1bd3ae42c34dcca7c16e38f460b`. These are **Git blob SHA-1**, not independent raw-data SHA-256 receipts.
- Exact commit compare `#413...#418`: diverged; common ancestor `ca6c5d915d2c0e018f4aa9f82b4488038c16f8d3`, #418 49 ahead/18 behind. The #413 variant contains no-follow component opening and file-identity checks absent in #418's manifest; a passing #418 isolated synthetic runner cannot certify retention of #413's current safety fixes. Do not merge/rebase or change archived expected digest automatically.
- [#418 archived source CI #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) decoded job log: **FAIL**, expected archived manifest blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`; dependent tests SKIPPED. Python minor and 22 package versions matched, but exact wheel hashes/native transitive closure are **NOT VERIFIED**.
- [#413 offline parity #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 6/6 jobs SUCCESS, pinned 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`; serial 1.765 s, parallel longest 2.7079 s, 0.652x (slower). Whole-CI and official full-backtest acceleration **NOT VERIFIED**. GitHub Actions artifact receipt ZIP SHA-256 `b5a14cc645b8c490ff8f1c4e5376524b3a67f5074531415ac899f5a6c0b72651` is an upload digest, not a financial-data source hash.

## Source, calendar and operational admission
- [OpenDART HEAD offline #39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) job SUCCESS, synthetic no-network only. Earlier official first-edition ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` remains a prior receipt, **not rehashed** here. Exact 2022/2021 first-edition standalone three-month consolidated operating-income cells, units, original-versus-correction edition lineage and precise public available-at/PIT are **NOT VERIFIED**.
- KRX [#422 #39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000) and [#423 #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) decoded logs: synthetic guards SUCCESS; #423 explicitly asserts default `2022_private_candidate_date_sets_equal == False` (dry-run, not an actual private source comparison). Official historical exchange-day, security status, corporate actions, 27 vetoed OHLC cases, order-book/lot fillability remain **NOT VERIFIED**. Prior 1,565/1,565 private weekday-pair SHA storage integrity does not grant market PIT.
- [Latest read-only watchdog #40119156828](https://github.com/kims34/openpilot-opkr/actions/runs/40119156828) decoded job log SUCCESS at 2026-10-24 18:06 UTC: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`; upload receipt ZIP SHA-256 `cb85374b9a08e51e2ebb3cee453331c83b820515e9df82281c136d868a3755d9`. This is not direct Railway state evidence.
- [Prospective chronology #39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) FAIL on public anchor retrieval, downstream skipped. Cannot infer historical public time.
- Railway `list_projects` read attempt: **interactive user input required**; latest deployment, runtime logs and live `ORDERING` value **NOT VERIFIED**. Requires interactive connector authorization by account owner; do not bypass or assume watchdog equals live runtime.

## Independent verdict and next evidence
- **PASS limited:** immutable GitHub refs/metadata; synthetic CI parity and guard results; direct source-blob difference; watchdog denial.
- **FAIL-CLOSED:** #418 archived manifest identity mismatch, chronology source failure; no cross-branch cache admission.
- **NOT VERIFIED:** original public PIT and 2022/2021 3-month CFS, historical issuer-security mapping, official KRX tradability/adjustments/actual fills, fees/tax/slippage, after-tax NetEV/PF/CAGR/MDD/ES95/99, profit concentration and temporal robustness, complete runtime provenance, whole-CI acceleration, live Railway flags.
- **M20 PIT/financial RUN NO-GO.** Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/labels/Purged/CPCV, sealed/consumed Holdout, Champion/Top3/NO_TRADE, costs/risk/promotion rules unchanged. `ORDERING=false` mandatory, **not live-attested**. Cache remains fail-closed until independent source/data/code/policy/runtime/approval SHA-256 admission; only independent read-only postprocessing may parallelize.
- OpenDART specialist: official first-original 2022/2021 CFS cells + precise publication chronology; KRX specialist: official market/session/security/corporate-action and actual private-source SHA comparison; optimization specialist: reconcile #413/#418 branch divergence and archived source/runtime identity with immutable test evidence, then comparable whole-CI timing **without financial runs**. Integration only adjudicates supplied independently verified evidence. No trading, funds, permission, production or PR changes.
