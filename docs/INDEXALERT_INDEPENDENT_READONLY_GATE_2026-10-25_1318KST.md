# IndexAlert independent integration + isolated runtime audit — 2026-10-25 13:18 KST

Scope: independent **read-only** verification and this **one isolated documentation write**. No source-owner code edits, market backtests, Holdout access, authority changes, deployment, orders, or PR merges. This is a non-admitting audit.

## Exact GitHub refs independently read
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Integration Draft [#414](https://github.com/kims34/openpilot-opkr/pull/414) pre-write HEAD `f89e7a6593b5a2c0b73e403c2b4c1c8179c570c0`; integration gate doc Git blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Git blob SHA-1 is **not** independent provider-original SHA-256.
- OpenDART Draft [#412](https://github.com/kims34/openpilot-opkr/pull/412) HEAD `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Runtime optimization Draft [#413](https://github.com/kims34/openpilot-opkr/pull/413) HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; dependent single-runner Draft [#418](https://github.com/kims34/openpilot-opkr/pull/418) HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft [#420](https://github.com/kims34/openpilot-opkr/pull/420) HEAD `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; [#422](https://github.com/kims34/openpilot-opkr/pull/422) `c14857620973531013799e44625d43080904fd5f`; [#423](https://github.com/kims34/openpilot-opkr/pull/423) `0e38004363cac9fc4475556b3a1c445de9af407f`.
- Most recent prior integration note checked: `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-25_1243KST.md` blob `29e5ca3a16e0dd9d1d366482a79466776fb81896`. This run does not repeat delegated experiments.

## Direct Actions/log evidence (historical executions re-read now)
- [#418 archived-source guard run 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478), job `117628139395`: **FAIL**, `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Correct fail-closed source-drift signal, not proof of data corruption. Exact wheel hashes and native OS dependency identities explicitly `false`.
- [#418 candidate source audit run 39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494), job `117628139749`: **PASS limited candidate lineage**, `checked_files=22`, `exact_upstream_head=f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, archived 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, but `all_transitive_imports_pinned=false`, `candidate_approved_for_merge=false`, `actual_backtest_performance_measured=false`. Job artifact ZIP SHA256 `e3b11f93bd67cd246c0a81c599679c83dda15176ffc687699edf5bead5e46ad8` is CI artifact identity only. Four-case micro-benchmark ratio `0.0831` with `0.0001s` serial vs `0.0015s` parallel is not an end-to-end performance measurement.
- [#413 offline parity 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): six jobs SUCCESS, but not an official market run or demonstrated full CI speedup.
- [KRX offline 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) and [KRX 2022 synthetic 39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925): SUCCESS for no-provider synthetic fail-closed tests only; official exchange calendar/status and corporate actions not proven.
- [DART parser 39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805): no-network synthetic parser SUCCESS, not original-filing PIT admission.
- [Watchdog 40149375759](https://github.com/kims34/openpilot-opkr/actions/runs/40149375759), job `121037468577`: SUCCESS, log states `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded flags-only ZIP SHA256 `06dbd1e269ff350fdf9c1c97e13ac634ef9d4f20c87c25c49f38ba0aee911b3c`, artifact `12582197131`. This is GitHub watchdog status, **not live Railway ORDERING attestation**.

## Gate matrix (PASS / FAIL / NOT VERIFIED)
| Gate | Verdict | Boundary |
|---|---|---|
| Original OpenDART source edition/hash | Historical limited PASS (inherited), **not rehashed** | Source identity alone; no accounting cell/first public time approval |
| Original 2022 and 2021 standalone Q3 3-month consolidated operating profit, sign/period/unit | NOT VERIFIED | Original semantics and correction lineage missing |
| Original public available-at/PIT; historical issuer-security as-of map | NOT VERIFIED | No first-public timestamp + mapping chain |
| KRX 2017–2022 private weekday pair storage integrity | Historical limited PASS (1,565/1,565 inherited), **not rehashed** | 90 official calendar/source gaps and 27 nonpositive-OHLC candidates excluded |
| Official per-security tradability, corporate actions, realistic fill/volume | NOT VERIFIED | Synthetic CI cannot substitute for official originals |
| Fees/taxes/spread/slippage and after-tax NetEV/PF/CAGR/MDD/ES95/99, concentration and time robustness | NOT VERIFIED | No economic experiment authorized |
| #418 archived implementation SHA identity | **FAIL** | Archived manifest changed; preserve baseline and fail closed |
| #418 candidate reviewed blobs and synthetic parity | Limited PASS | Dependency closure/wheel/native runtime and whole-CI/market speedup NOT VERIFIED |
| Railway live deployment/logs and actual ORDERING value | NOT VERIFIED | `list_projects` read-only call blocked by interactive user-input requirement; no bypass |

## Final policy and next owner proofs
**M20 PIT/performance NO-GO**. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV, independent sealed Holdout, Champion, Top3/NO_TRADE and cost/risk/tax gates unchanged. `ORDERING=false` remains a **required invariant**, not independently verified on live Railway. No real orders, funds, credentials, account rights, deployment, PR merge, Champion promotion, reused failed H5/consumed Holdout or Dynamic post-hoc changes.

Owner-specific missing evidence: DART original connected CFS cells and exact release/correction chronology; KRX official session/security status, corporate-action and identity as-of originals; runtime complete transitive source + exact wheel/native hashes and comparable whole-CI profiling; Railway read-only interactive authorization. Do not modify other owners' code or workflows or retry blocked security operations.
