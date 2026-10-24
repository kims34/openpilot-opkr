# IndexAlert independent profitability gate — 2026-10-24 03:43 KST

This is a **read-only evidence review** plus this one documentation-only addition to isolated Draft PR #414. It does **not** admit PIT data, authorize M20 economics, change Frozen/Holdout/Champion/Top3 policy, permit orders, deployment, merge, capital movement, rights changes or promotion. ORDERING=false is a **required policy**, not a newly attested live Railway configuration.

## Direct GitHub HEAD and scope

- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (GitHub branch API).
- Integration Draft #414 **before** this write: `e41ccf67be18eb573019242ad18cd3da86941663`. That commit added only `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-24_0316KST.md` (GitHub commit API). Master gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft #412 `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`; runtime Draft #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; dependent single-runner Draft #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All seven specialist/integration PRs remain open Draft.

## Incremental evidence since 03:16 KST audit

- Latest repository-wide GitHub Actions run [#40002116199](https://github.com/kims34/openpilot-opkr/actions/runs/40002116199) created 2026-10-23 18:17:44 UTC, completed **SUCCESS**. Directly read job `120580600571` logs: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. This is **offline/governance watchdog evidence only**; it is not an attestation of live Railway ORDERING or of original DART/KRX data.
- The same job reported uploaded flags-only artifact ID `12523225244`, ZIP SHA-256 `f3cbc227c4990b437a075b43409e57ea23713db46c1fea7404b898a940195d64`. **Uploader-reported only; archive not independently downloaded/rehashed**. A green watchdog must not be promoted into source PIT PASS.
- Latest repository-wide chronology run [#39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) remains **FAIL**. Direct job `120476944660` log ends with HTTP 404 for prospective `/anchor/latest`; validation job `120476947705` skipped. No independently validated public available-at chronology. The endpoint's root cause is **NOT VERIFIED**; no live service changes authorized.
- OpenDART #412 latest HEAD [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) one synthetic no-network job PASS; [#39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) offline TOC guard PASS. Previous bounded official index [#39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351) PASS only for completed 2026-10-22 day (status 013, zero newly queried Q3 amendments). First-edition 2022/2021 July–September CFS operating-profit exact period, signed account, currency, corrections and public time **NOT VERIFIED**.
- KRX #420 [#39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) synthetic/offline calendar guard PASS, not official private exact-set trade-day, suspension, delisting, corporate-action or fillability proof. Historical 1,565/1,565 weekday raw pairs is storage integrity only; 90 uncertain sessions, 27 invalid OHLC candidates, and source gaps remain quarantined.
- Runtime #413 [#38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) offline six-job suite PASS, fixed 34-case test SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` as recorded by prior audit; this cycle did not independently rehash its artifact. #418 [#39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) archived merge-context gate FAIL-CLOSED. Direct GitHub blob re-read this cycle: #418 `research_v1_runtime_manifest.py` blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs #413 `e0055c66c59398fd4a1158077446d886b54c4e37`; no baseline rewrite, candidate approval, or real-backtest speedup claim.

## Independent admission verdict

| Required gate | Result | Scope |
| --- | --- | --- |
| GitHub ref and named blob identity | **PASS (limited)** | Direct GitHub API refs and two manifest blobs; not the full source/data artifact SHA chain |
| Original DART first-filed 2022/2021 three-month CFS, corrected lineage, earliest public available-at | **NOT VERIFIED** | Offline safeguards and bounded index are not original-vintage financial semantics or PIT |
| Historic issuer/security PIT map; KRX official calendar, state, corporate actions, fillability | **NOT VERIFIED** | Private storage integrity / synthetic CI not admission |
| Costs, tax, realistic execution, after-tax NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness | **NOT VERIFIED** | No admissible original PIT; M20 economic backtest **prohibited** |
| Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, consumed Holdout, Champion, Top3/NO_TRADE | **UNCHANGED / NOT RE-ADMITTED** | No threshold tuning, replay, or promotion |
| Live Railway deployment/logs and actual ORDERING=false | **NOT VERIFIED** | Railway list-projects read-only connector returned `User input required but current turn is running in a non-interactive mode`; no authentication or permission changes attempted |

**Final: M20 economic RUN NO-GO; PR #413/#414/#418 merge BLOCKED; no production, trading or promotion.** Next independent gate: source owners must produce original-edition CFS cell+public-time provenance, official KRX historical trade-state/fillability, and a pinned independent source/code/policy/runtime SHA receipt; then preapproved frozen protocol may be evaluated separately. Railway connection must become usable in a permitted interactive context to attest live deployment and ordering. No specialist-owned code or workflows modified.
