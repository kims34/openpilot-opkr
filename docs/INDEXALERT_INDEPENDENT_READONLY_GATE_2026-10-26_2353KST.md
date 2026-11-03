# IndexAlert independent profitability admission audit — 2026-10-26 23:53 KST

This is a read-only evidence review plus a single isolated documentation-only commit to existing Draft PR #414. No provider call, live trade, funds/account/permission change, workflow or specialist code edit, model/backtest execution, Holdout access, deployment, or PR merge.

## Exact checked refs
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Integration Draft PR #414 before this write: `85ca75382140104fe0577b689810279464f73cd8`; existing frozen integration gate Git blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- OpenDART Draft PR #412: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- Offline runtime Draft PR #413: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; downstream one-runner Draft PR #418: `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX session Draft PR #420: `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; KRX 2021 comparator Draft PR #422: `c14857620973531013799e44625d43080904fd5f`; KRX 2022 comparator Draft PR #423: `0e38004363cac9fc4475556b3a1c445de9af407f`. Earlier KRX integrity PR #404 is already merged into development (not an M20 PIT approval).
- Cross-check: immediately preceding integration audit `docs/INDEXALERT_INDEPENDENT_READONLY_GATE_2026-10-26_2330KST.md` at `85ca753...`; this audit adds bounded exact negative-control interpretation, not another claim of newly admitted source data.

## Independent Actions verification and additional interpretation
- GitHub repository-wide recent Actions listing: newest listed run [watchdog #40326183435](https://github.com/kims34/openpilot-opkr/actions/runs/40326183435) created 2026-10-26 12:54:42 UTC, completed SUCCESS. Prior read-only job evidence: M20 PIT NOT ATTESTED, orders DISABLED, Holdout NOT AUTHORIZED. A green watchdog is **not** production Railway configuration attestation.
- OpenDART [#40262558066](https://github.com/kims34/openpilot-opkr/actions/runs/40262558066) verified 2021 first-original ZIP SHA-256 `8728c0a3c12761ca19e9c6455bea8f1bed0e4c1ebc2e21dc263c373a82a2b625`, one SGML, 1,728 table shapes, 13 operating-label candidates, zero strict standalone Q3 3-month CFS profit cells. Earlier separate 2022 first-original ZIP SHA-256 `56639d8f6ebbecf14cd8bc3179d75d01162e2cd7bbdf8f6a3c9479b44f5084bb` remains historical source-only evidence, not re-downloaded here. The latest [2022 original DART viewer TOC offline #40263193758](https://github.com/kims34/openpilot-opkr/actions/runs/40263193758), job `121379780273`, passes **13 synthetic tests**, including refusal of revised-edition mixing and unsafe receipt; it performs no new official financial-cell/clock attestation.
- Independently fetched [KRX 2022 candidate #39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925), job `119612335677` logs: **32/32 synthetic tests PASS** (13 private 2022 date/receipt controls plus 19 source/venue/as-of notice guards). The dry-run CI explicitly asserts `2022_private_candidate_date_sets_equal is False` and `official_market_status_admitted is False`. **Interpretation:** this is a deliberate **no-provider/no-private-volume dry-run denial**, NOT evidence that a real 14-day private-vs-official calendar comparison was run and mismatched. It must not be labeled real market-calendar FAIL or PASS.
- Independently fetched [KRX 2021 candidate #39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), job `117306218697` logs: **12/12 synthetic tests PASS**; default run does not read private storage, and asserts `official_market_status_admitted is False`. Its 13 candidate dates are **not** an official as-of historical session calendar approval.
- [KRX #420 #39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438) synthetic fail-closed CI SUCCESS; no original private KRX volume, corporate-action, security mapping or fill evidence was admitted. Historical 2017–2022 1,565/1,565 stored weekday raw pairs remains a **historical limited SHA storage PASS** with 90 calendar/source-gap uncertainty days, 27 nonpositive OHLC rows and 12,003 zero-activity rows excluded from economic admission.
- [PR #418 archived pinned #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) still FAIL-CLOSED on source blob expected `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs observed `e0055c66c59398fd4a1158077446d886b54c4e37`; the separately green synthetic parity 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is not a runtime dependency/whole CI speed proof. No baseline repin.

## Railway access boundary
A single direct Railway `list_projects` READ-ONLY call returned `User input required but current turn is running in a non-interactive mode`. No retry, interactive bypass or privilege change. Latest Railway production deployment/runtime logs and actual live `ORDERING=false` remain NOT VERIFIED this run; interactive legitimate read-only authorization is required. The **policy** remains `ORDERING=false` and no orders.

## Admission matrix (actual proof, not inference)
| Gate | Decision | Evidence limitation |
| --- | --- | --- |
| Selected 2021 first-original ZIP SHA identity | PASS (bounded) | Source bytes/shape only, not accounting semantic cell |
| Selected 2022 original ZIP SHA identity | PASS (historical bounded) | Not independently refreshed this run |
| Original 2022/2021 exact 3-month CFS operating-profit amounts, units, comparative and corrections | NOT VERIFIED | No authoritative numeric statement cell lineage |
| First public available-at/PIT and issuer-to-security as-of history | NOT VERIFIED | No original public-time and historical mapping attestation |
| KRX private pair SHA storage | PASS (historical limited) | 1,565 pairs only; no venue/session/trade-state authority |
| 2021 13-day and 2022 14-day actual private vs authoritative calendar comparison | NOT VERIFIED / NOT RUN in inspected CI | Synthetic dry runs explicitly deny authority |
| KRX corporate actions, official trade state, executable fills, slippage, costs and taxes | NOT VERIFIED | Source PIT/tradability unavailable |
| PR #418 archived source pin | FAIL (fail-closed by design) | Implementation Git blob changed |
| Runtime full transitive SHA, cache admission, whole CI and real backtest speed | NOT VERIFIED | Test-only parity is insufficient |
| NetEV, PF, CAGR, MDD, ES95, ES99, return concentration, temporal robustness, annual after-cost/tax risk-adjusted profit | NOT VERIFIED / NOT RUN | M20 economic testing prohibited pending source approval |
| Live Railway `ORDERING` and deployment logs | NOT VERIFIED | Interactive authentication blocked |

**Final gate: M20 economic RUN NO-GO.** Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV, spent sealed Holdout, Champion/Top3/NO_TRADE, cost/tax/risk/promotion thresholds unchanged. No model exploration or H5/Dynamic post-hoc Holdout reuse. Cache only on independently approved exact source/data/code/Frozen/runtime/evidence SHA-256; fail closed otherwise; only independent read-only postprocessing may parallelize, never retraining or capital transition. Next authorized work belongs to existing source owners: original DART financial-cell and publication-time proof; KRX genuine official historical trade-state/CA/identity and private receipt comparison; runtime owner full dependency provenance. Do not merge Drafts or deploy.
