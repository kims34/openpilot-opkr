# IndexAlert independent profitability and isolated runtime audit — 2026-11-01 22:18 KST

**Read-only evidence check; no market-profit replay, new model search, holdout reuse, deployment, merge, order, or authority change.** This is an independent audit note on the isolated audit branch, not PIT admission or a runtime change.

## Exact repository anchors verified live

| Scope | Verified HEAD / source blob | Admission consequence |
|---|---|---|
| Research `index-alert-research-v1` | `3b8b7830612a6284d7c7a60628cb527cb741627a` | Frozen, unchanged |
| Development `index-alert-position-regen-fix-v1` | `1e6367d2863a86c3470da13d81a955d277eba485` | No changes |
| Profitability Draft [#414](https://github.com/kims34/openpilot-opkr/pull/414) | HEAD `437ea3982642ba925c0b917c9a9bdcaa9dcb050a`; `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` | Integration evidence, not permission |
| Offline optimization Draft [#413](https://github.com/kims34/openpilot-opkr/pull/413) | HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; runtime manifest blob `e0055c66c59398fd4a1158077446d886b54c4e37` | Offline parity only |
| Dependent single runner Draft [#418](https://github.com/kims34/openpilot-opkr/pull/418) | HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; runtime manifest blob `108f66714602a1bd3ae42c34dcca7c16e38f460b` | Archived replay FAIL-CLOSED |
| OpenDART Draft [#412](https://github.com/kims34/openpilot-opkr/pull/412) | HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` | Original byte evidence only |
| KRX PIT specialist branch | HEAD `073d2d49e95f69fb10b943b93e51bb179fb3c698`; source integrity [#404](https://github.com/kims34/openpilot-opkr/pull/404) HEAD `1aef2de445b05883353a1d668acd89b194abbeab` | Stored pairs ≠ official tradability |
| Other specialists | Draft #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`; #424 `a4ae98f40b3e6dcaf565cc402679497e42cdabb5` | Separate workspaces left untouched |

## Newly independently cross-checked chronology blocker

- Failed [Prospective Chronology Anchor Actions #41091128151](https://github.com/kims34/openpilot-opkr/actions/runs/41091128151) (2026-10-30) has `auto-anchor` FAILED and `validation` SKIPPED. Original job log ends in `urllib.error.HTTPError: HTTP Error 404: Not Found`.
- **New cross-system check:** Railway production HTTP proxy logs for `indexalert-pit-rebuild`, 2026-10-30 **16:35:22–17:13:23 UTC**, show **20 distinct GET `/anchor/latest` requests**, all HTTP **404** on `indexalert-pit-rebuild-production.up.railway.app`, at approximately two-minute intervals. This corroborates the exact route/status seen by the GitHub job and rules out a single transient GitHub-side 404. HTTP proxy records do **not** preserve response bodies, and there were no matching deploy-stream records in that historical interval.
- Live deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, source commit `e57054ecdb3e734ced3c9a981b887d9b5fc60f97`, HTTP implementation `research_v1_prospective_http_runtime.py` blob `026710d8d48b3db666832e199fd3bca95a113d3b`: route `/anchor/latest` is implemented; returns **404 `NO_ANCHOR`** if no private anchor payload, **503 `ANCHOR_UNAVAILABLE`** on read/validation exception, or **200** on available payload. Without the actual 404 response body, exact origin remains **NOT VERIFIED**; missing receipt is a plausible explanation, **not proven**. Do not fabricate or backfill an anchor.
- Latest prospective runtime log 2026-11-01 **13:16:05.978 UTC = 22:16:05 KST**: `status=FAIL_CLOSED`, `error_reason_code=COMMON_OHLC_NONPOSITIVE`, `source_failure_session=2026-09-28`, common stock rows 803, nonpositive OHLC 27, zero-volume/value 27; `independent_source_admission_verified=false`, `independent_chronology_admission_verified=false`, `real_orders_authorized=false`, `ordering=DISABLED`. `chronology_anchor_pending=false` is **not** evidence of chronology admission.

## Other independently rechecked source and CI verdicts

| Evidence | Result | Scope |
|---|---|---|
| [OpenDART #38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742) | 2/2 jobs PASS; 15 first-edition and 15 corrected SGML candidate operating rows | **LIMITED PASS** byte/candidate signatures only; no certified 2021/2022 first-published standalone three-month consolidated operating income, public available-at, correction-vintage PIT or historical issuer mapping |
| KRX 2017–2022 private worker `16c93d7c-7cd0-4d84-a327-298d2805376c` | Historical 1,565/1,565 weekday source pairs, integrity PASS (prior evidence); fresh worker deploy log query 0 entries | **LIMITED PASS** storage only; 90 uncertain sessions, 12,003 zero-activity observations, official trading status/corporate actions/fills/costs/tax **NOT VERIFIED** |
| [#413 CI #38508247773](https://github.com/kims34/openpilot-opkr/actions/runs/38508247773) | 6/6 jobs PASS, frozen 34-case digest `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, serial 1.7650 s vs longest parallel 2.7079 s (0.652x) | **LIMITED PASS** test parity; slower in this regression phase; end-to-end CI/actual admitted backtest speed NOT VERIFIED |
| [#418 CI #39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) | Archived replay FAIL: `SourceDriftError` expected manifest `108f66714602a1bd3ae42c34dcca7c16e38f460b` vs observed `e0055c66c59398fd4a1158077446d886b54c4e37` | **FAIL-CLOSED**; no waiver or silent repin; separate [#39111405494](https://github.com/kims34/openpilot-opkr/actions/runs/39111405494) candidate proof and [#39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) offline one-runner success are not transitive safety approval |
| [Watchdog #41292056320](https://github.com/kims34/openpilot-opkr/actions/runs/41292056320) | 1/1 SUCCESS; original log: `M20 PIT admission: NOT ATTESTED; orders: DISABLED; holdout: NOT AUTHORIZED` | Guardrail confirmation, not M20 profit PASS |

Railway production project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`: `describe_environment` and `get_staged_changes` report staged=null and no changed resources; `get_status` and `environment_status` still report old `patch:e113dacb-6705-4416-9997-dc694539d382` as pending since 2026-10-29. **Cross-API inconsistency NOT VERIFIED; no accept-deploy.** Kiwoom real read-only service deployment `a77fb922-b679-4d88-92c4-03054ec579cd` reports SUCCESS while health lists 0 running / 1 crashed replica; do not infer service health from deployment SUCCESS. Index alert runtime latest log read 2026-11-01 13:18:44 UTC; read-only index/FX check, no economic admission.

## Final independent admission verdict and next permitted steps

**M20 after-tax annual risk-adjusted net profit / NetEV / PF / CAGR / MDD / ES95 / ES99 / return concentration / date-and-year robustness = NOT EVALUABLE; NO-GO.** Required original first-public 2021/2022 CFS three-month operating-income cell/period/public timestamp/correction lineage, issuer/security history, official KRX session/tradability/corporate action/executable fills/costs/taxes, and chronology receipt are NOT VERIFIED. No M20 performance run or new market-return experiment. H5 failed/consumed holdout is not independent reusable evidence.

Keep Frozen H5; M20 horizon20/purge20 and WF504/126/126, PIT/label/Purged/CPCV/independent Holdout, Champion/Top3/NO_TRADE, cost/tax/risk/promotion gates unchanged. Cache must match independently approved source/data/code/Frozen/runtime/admission-evidence SHA-256 and fail closed; parallelize independent read-only postprocessing only. `ORDERING=false`. No real orders, funds movement, account/credential permissions, Champion promotion, merge of #413/#414/#418, workflow changes or production deploy.

**Next source-owner-only evidence:** capture and independently verify `/anchor/latest` 404 response body and private anchor receipt existence/readability without manufacturing a timestamp; DART original 3-month CFS cell and exact public instant; KRX official calendar, security lineage and executable economics. Optimization owner must resolve #418 source drift and match #413 no-follow/fd/inode and strict receipt semantics under synthetic offline tests before considering any adoption. This audit changed no source code or runtime.
