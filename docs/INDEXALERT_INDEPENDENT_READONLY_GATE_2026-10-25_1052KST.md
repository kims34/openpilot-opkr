# IndexAlert independent read-only gate — 2026-10-25 10:52 KST

**Scope:** one scheduled integration read, no specialist edits or market/economic replay. Baseline audit: `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-25_1026KST.md` (pre-run PR #414 HEAD `2a1104a00fc2c4adf2c241621fc9f2c5aa3731bc`). No material new source-admission evidence since that audit. All SHA types are explicitly distinguished: Git commit SHA/blob SHA-1 are not provider original SHA-256.

## Exact independent GitHub metadata
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`; development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`. Both obtained by self-ref compare.
- Integration Draft PR #414: `2a1104a00fc2c4adf2c241621fc9f2c5aa3731bc` before this documentation-only write; existing integration gate blob Git SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft PR #412: `e82b26e2431ea15a42888f073a4b0b72a2e11ef6`.
- Runtime Draft #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; dependent one-runner Draft #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX Draft #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422: `c14857620973531013799e44625d43080904fd5f`; #423: `0e38004363cac9fc4475556b3a1c445de9af407f`. KRX #404 closed. No merge/deploy action taken.

## Independently checked Actions
- [Read-only watchdog #40149375759](https://github.com/kims34/openpilot-opkr/actions/runs/40149375759): job `121037468577` SUCCESS. Decoded log: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED`. Upload-log SHA-256 `06dbd1e269ff350fdf9c1c97e13ac634ef9d4f20c87c25c49f38ba0aee911b3c` matches artifact ID `12582197131` metadata digest. This is metadata/log parity only, not independently downloaded/rehashed ZIP bytes or proof of live Railway ordering configuration.
- [OpenDART #39884243351](https://github.com/kims34/openpilot-opkr/actions/runs/39884243351): 2/2 jobs SUCCESS (offline safety + bounded official Oct22 index). [#39884427765](https://github.com/kims34/openpilot-opkr/actions/runs/39884427765): 1/1 offline synthetic SUCCESS. Neither admits original first-filing CFS 2022/2021 standalone three-month operating income, exact available-at or complete correction lineage.
- [KRX #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [#39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925): each inspected job SUCCESS, synthetic/offline, not official historical session/tradability proof.
- [Runtime #413 #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773): 6/6 jobs SUCCESS. [#418 #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478): pinned parallel-only source-identity check FAIL. Existing 34-case fixed outcome SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` remains a prior offline parity receipt only. No end-to-end speed claim.

## Railway and source gate
Railway read-only `list_projects` was attempted and returned `User input required but current turn is running in a non-interactive mode`. No project/deployment/log/actual ORDERING variable read was possible; no authentication workaround. Interactive Railway connection authorisation is required before live operational verification.

**PASS (limited):** current GitHub ref/PR metadata, selected completed offline CI jobs, watchdog upload-log vs artifact-metadata SHA-256 parity.

**FAIL / BLOCKED:** #418 archived-source identity gate FAIL; Railway read-only access BLOCKED.

**NOT VERIFIED:** independent provider original byte SHA-256, earliest original-filing public available-at/PIT, 2022/2021 3-month CFS period/unit/meaning and amendment lineage, historical issuer/security mapping, official KRX calendar/halt/delist/corporate action/tradability/fill, pre-registered fees/slippage/taxes, after-cost NetEV/PF/CAGR/MDD/ES95/99, concentration/regime robustness, independent sealed Holdout, and whole-CI or real admitted-backtest speedup. Historical private KRX stored 1,565/1,565 pair integrity is not an official tradability attestation.

**Decision:** M20 PIT/economics NO-GO; no performance run. Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV, Holdout, Champion, Top3/NO_TRADE, fixed cost/tax/risk gates unchanged. `ORDERING=false` is required; actual Railway state NOT VERIFIED. No orders, funds, permission changes, deployment, PR merge, or Champion promotion. No cache admission unless independent original/data/code/policy/runtime/evidence SHA-256 all agree; only independent read-only post-processing can parallelise. Specialist-owned code untouched.

**Next:** OpenDART specialist proves first-edition CFS and chronology; KRX specialist proves official sessions/security/corporate actions/fills; runtime specialist resolves #418 identity and wall-time parity. Integration rechecks actual provider receipts before any single pre-registered M20 run. No new substantive admissible evidence in this interval.
