# IndexAlert independent profitability and runtime gate — 2026-10-25 17:20 KST

Scope: read-only evidence reconciliation; one isolated documentation-only commit. No source acquisition, official financial run, model search, Holdout access, deployment, workflow modification, PR merge, broker action, permission change, or order.

## Exact repository refs observed through GitHub connector
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a` (independently recorded in prior 16:22 KST audit; branch name rediscovered now, HEAD not independently ref-resolved in this pass).
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485` (same provenance limitation).
- Draft PR #414: HEAD before this document `6fe6357dd485df54cf3c0f25afc81432a70e34d7`, base `index-alert-research-v1`; integration-gate Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft PR #412: HEAD `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Draft PR #413: HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft PR #418: HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX specialist Draft PR #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422: `c14857620973531013799e44625d43080904fd5f`; #423: `0e38004363cac9fc4475556b3a1c445de9af407f`. Historical #404 head `1aef2de445b05883353a1d668acd89b194abbeab` is a private-storage integrity audit, not market PIT approval.

## Independent GitHub Actions job/log rechecks
- [Read-only watchdog 40167777488](https://github.com/kims34/openpilot-opkr/actions/runs/40167777488): actual job 121092240087 SUCCESS, 4 watchdog + 31 research governance synthetic tests PASS. Log explicitly says `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Uploaded ZIP SHA-256 `c0f90b91564348a8c958edab0ffcc958f5dcc7004e01a9aa2b89ae9935dd8b8b`. These are CI assertions, NOT a read of Railway live ORDERING.
- [KRX #420 run 39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [#422 run 39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), [#423 run 39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925): respective synthetic/no-provider jobs all SUCCESS; actual private volume and historical exchange session/stock state NOT rechecked.
- [OpenDART #412 runs 39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765) and [39884427805](https://github.com/kims34/openpilot-opkr/actions/runs/39884427805) successful offline jobs; 2022 original XBRL 014 and standalone 2022/2021 Q3 three-month CFS facts and publication instant remain NOT VERIFIED. Previously pinned original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` is byte integrity only, not earnings semantic PIT.
- [Optimization #413 run 38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): independently rechecked 6/6 jobs SUCCESS; actual parity job 115670744341 reports frozen 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`. Artifact parity ZIP SHA-256 `b5a14cc645b8c490ff8f1c4e5376524b3a67f5074531415ac899f5a6c0b72651`. No full-CI or admitted-backtest acceleration proof.
- [Independent #418 merge-context run 39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478): independently inspected job 117628139395, **FAIL** at immutable source gate: `research_v1_runtime_manifest.py` expected Git blob `108f66714602a1bd3ae42c34dcca7c16e38f460b`, observed `e0055c66c59398fd4a1158077446d886b54c4e37`. Do NOT repin or bypass. [Separate one-runner run 39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) SUCCESS for isolated offline parity, same 34-case SHA; full workflow and official-market acceleration NOT VERIFIED.
- [Prospective chronology 39972035700](https://github.com/kims34/openpilot-opkr/actions/runs/39972035700) prior FAILED anchor, so continuous as-published chronology is NOT VERIFIED.

## External Railway limitation
Railway `list_projects` was attempted read-only once in this noninteractive execution; connector returned `User input required but current turn is running in a non-interactive mode.` No projects/deployments/logs or live ORDERING settings were read. No authentication workaround, secrets, alternate service, or permission change. Historical 2017–2022 1565/1565 weekday private raw pairs remain a previously documented limited storage SHA PASS, not a fresh independent byte check and not trading-day or tradability PASS.

## Gate matrix and hard stop
- Repository PR metadata, cited offline CI, frozen 34-case parity: **PASS within the specified software-only scope**.
- PR #418 archived original source SHA in merge-context: **FAIL**; immutable runtime dependency/wheel/native identity: **NOT VERIFIED**.
- Original first-filing source available-at, 2022/2021 exact standalone three-month consolidated operating-profit units/periods, complete amendment lineage, historical issuer-security mapping: **NOT VERIFIED**.
- Official KRX historical session calendar, halt/delist, corporate actions, executable fills, liquidity, slippage, commissions, taxes, 27-veto securities: **NOT VERIFIED**.
- After-cost/tax NetEV, PF, CAGR, MDD, ES95/99, concentration, date/year robustness, cost stress: **NOT VERIFIED**; M20 economic RUN **NO-GO**.
- Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, Purged/CPCV, consumed independent Holdout, Champion, Top3/NO_TRADE and unchanged cost/risk thresholds. `ORDERING=false` is mandatory, but Railway production flag not re-attested.
- No official market-return experiment, new strategy search, model retraining, capital-transition parallelism, orders, money, auth, deploy, merge or promotion.

Next permitted step: obtain independently authenticated original OpenDART vintage/timestamp/CFS and KRX protected source + exchange session/tradability evidence through the assigned specialist tracks; independently establish safe noninteractive Railway read-only access; resolve #418 source/runtime identity without bypassing original SHA gate. Continue offline-only synthetic safety verification without duplicating specialist experiments.
