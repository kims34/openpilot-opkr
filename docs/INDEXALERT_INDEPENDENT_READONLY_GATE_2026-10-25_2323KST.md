# IndexAlert independent read-only gate — 2026-10-25 23:23 KST

Scope: isolated audit note only. No production, PR merge, workflow edits, strategy changes, source admission, market replay, holdout reuse, orders, funds, permissions or Champion promotion. This note is NOT authorization.

## Exact checked heads (GitHub REST branch/PR reads)
- research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- profitability Draft PR #414: `6d040efd23cb4144e35ca84962155921e5f32d83` (pre-note)
- runtime Draft PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`
- one-runner Draft PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`
- OpenDART Draft PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`
- KRX Draft PR #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422: `c14857620973531013799e44625d43080904fd5f`; #423: `0e38004363cac9fc4475556b3a1c445de9af407f`. Historical PR #404 is closed, not new authority.

## Independently read CI/log evidence
- [Latest watchdog run 40188482673](https://github.com/kims34/openpilot-opkr/actions/runs/40188482673), created 2026-10-25 11:20:54 UTC, completed SUCCESS, job 121154222723. Actual job log: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Flags-only artifact ID 12596892663, ZIP SHA256 `a08b8ada6653856bf9ce825e2da1a7d48c1cdbdcc9cd7abf6a256abd07dc1bb2`. This is a governance check, not a Railway runtime attestation or official financial-data proof.
- [KRX #420 run 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) SUCCESS, synthetic-only; its tests explicitly distinguish market closure from absent source rows and deny equity-calendar authority for wrong venue.
- [KRX #423 run 39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925) SUCCESS, 32 synthetic/offline tests, including 14-day candidate shape and wrong-date/source-vintage rejection; NOT actual official KOSPI session/tradability PIT.
- [OpenDART #412 latest head offline Actions 39884427765 / 39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) SUCCESS; this does not supersede official original ZIP `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` and amended ZIP `606be9d03928808f0a2a05f052444587bd2457bdef7a47a8f4bff3d2ea098a30` previously proven in official source-only runs. No verified 2022/2021 standalone 3-month CFS cells, exact intraday public available-at or full issuer/security mapping.
- [PR #413 run 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 6/6 jobs PASS; 34-case pinned SHA256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` matched; serial 1.7650 s vs longest parallel 2.7079 s, test-phase speed ratio 0.652 (slower), full CI/backtest acceleration NOT VERIFIED.
- [PR #418 run 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478): FAIL at archived source blob gate before tests; expected `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37` for `research_v1_runtime_manifest.py`. Observed blob is also independently fetched from #413 branch. Do not re-pin to force PASS or merge.
- [Prospective chronology anchor run 39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) remains FAILURE; do not infer prospective evidence continuity.

## Gate verdicts (strict)
- Historical OpenDART original ZIP byte identity: **PASS limited to pinned ZIP**; 2022/2021 original 3-month consolidated operating-income facts, correction lineage tied to cells, exact publication instant and PIT: **NOT VERIFIED**.
- Private KRX stored raw pairs: **historical storage-integrity PASS only** per previously recorded worker evidence; independent current Railway logs **NOT VERIFIED** because Railway connector required interactive user input during this unattended run. Official cash-equity calendar/status, issuer/security history, corporate actions, executable fill, slippage, costs and taxes: **NOT VERIFIED**.
- Runtime offline parity #413: **PASS**; #418 immutable archived-source gate: **FAIL**; whole-CI and official backtest acceleration: **NOT VERIFIED**.
- NetEV, PF, CAGR, MDD, ES95/99, annual risk-adjusted after-tax net profit, return concentration, date-cluster and temporal robustness: **NOT VERIFIED**; no M20 profitability test permitted.
- Frozen H5 / M20 horizon20 purge20 / WF504-126-126 / PIT, Purged-CPCV, independent Holdout, Champion, Top3/NO_TRADE and fixed economic gates: **unchanged**. Consumed H5 holdout cannot be treated as new independent evidence. `ORDERING=false` is mandatory; latest watchdog reports orders disabled but Railway live config remains unverified.

## Next proof dependencies (read-only until independently admitted)
1. OpenDART owner: official first-original 2022/2021 standalone 3-month consolidated operating-profit semantic cells, original/amendment as-of lineage and exact public available-at; issuer/security history.
2. KRX owner: official market-specific historical calendar, suspensions, corporate actions, price/volume/lot executable fill and contemporaneous cost/tax receipts; verify against private raw-pair SHA without treating storage as tradability.
3. Runtime owner: reconcile #413/#418 source identities and full dependency hashes in isolated offline CI; no silent re-pin, no dependent fitting/capital transition parallelism, no cache use without independent source/policy/runtime/evidence SHA approval.
4. Orchestrator: only after all sources pass, seek separate explicit approval for a single preregistered M20 economic evaluation; continue NO-GO now.

Railway project/deployment/log reads were attempted via connected Railway service and stopped at an interactive-authentication boundary. No bypass, retry, deploy or change. No other team-owned code/workflow touched.
