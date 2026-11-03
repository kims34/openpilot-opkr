# IndexAlert independent profitability and isolated runtime audit — 2026-10-31 15:25 KST

Scope: read-only evidence reconciliation; no official market performance, M20 economic run, model search, Holdout, order, merge, deployment, permissions change or Champion promotion. This audit does not grant admission. Existing specialist code and workflows remain untouched.

## Verified source heads (GitHub direct)
- Research `index-alert-research-v1`: `3b8b7830612a6284d7c7a60628cb527cb741627a`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- KRX specialist `indexalert-krx-pit-source-audit-20261013`: `073d2d49e95f69fb10b943b93e51bb179fb3c698`.
- Draft PR #412 OpenDART: `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- Draft PR #413 optimization: `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- Draft PR #418 one-runner (base PR #413): `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- Draft PR #414 orchestration: `96aed82ab155e45a2bdf956505562e084cbbc747` at initial read; its core gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA-1 `984c933651f39f1ee9e26a1d7ac3893aaa5335be`.
- Draft KRX PR #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`. All observed unmerged. Related #416 `053de553646fc4765d2616544ca1e8d6bbdde35f`; #424 `a4ae98f40b3e6dcaf565cc402679497e42cdabb5`.

## Original Actions/CI evidence, independent read
- Official OpenDART [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742): two jobs SUCCESS; raw log of official-safe-candidate-row-diff reports first and corrected editions each 15 exact-label row candidates, numeric-peer candidate multiset identical; `original_cfs_q3_2022_2021_three_month_profit_verified=false`, `historical_publication_instant_pit_verified=false`, `m20_performance_run_authorized=false`, `ordering=DISABLED`. This is shape-only evidence, not 2021/2022 original standalone consolidated three-month fact/PIT approval. Original ZIP byte digest is not independently recomputed in this checkpoint.
- KRX [39714369327](https://github.com/kims34/openpilot-opkr/actions/runs/39714369327), [39714369438](https://github.com/kims34/openpilot-opkr/actions/runs/39714369438), [39001836000](https://github.com/kims34/openpilot-opkr/actions/runs/39001836000), [39714207925](https://github.com/kims34/openpilot-opkr/actions/runs/39714207925): relevant commit-associated offline synthetic/calendar candidate runs SUCCESS. These are **not** official historic trading-status or corporate-action admissions.
- KRX 2017–2022 private worker previously reported 1,565/1,565 weekday raw source pairs integrity PASS; 90 uncertain sessions and 12,003 zero-activity observations are not admitted as tradable. Current audit did not rehash private volume bytes, so retain this as earlier scope-limited evidence, not an independently repeated raw-byte PASS.
- PR #418 [39111405478](https://github.com/kims34/openpilot-opkr/actions/runs/39111405478) one job FAIL: `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e0055c66c59398fd4a1158077446d886b54c4e37`. Direct GitHub file reads confirm PR #413 manifest blob SHA-1 `e0055c66c59398fd4a1158077446d886b54c4e37` vs PR #418 `108f66714602a1bd3ae42c34dcca7c16e38f460b`.
- Direct source comparison: PR #413 demands literal False for `holdout_access_authorized` and `live_orders_authorized`, validates elevated receipt flags and uses no-follow component opening, fstat and identity recheck. PR #418 checks only literal True and uses `Path.is_file/is_symlink/open`; absence, non-boolean authority and path race are not equivalently fail-closed. **Optimization adoption FAIL / blocked**. Do not update pinned SHA merely to green CI.
- PR #418 [39111405562](https://github.com/kims34/openpilot-opkr/actions/runs/39111405562) one job SUCCESS; actual offline log: fixed 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`, identical outcomes; serial regression 2.3484 s vs parallel longest suite 2.0154 s (1.165x test-phase only), separate one-runner serial subprocess 2.3911 s vs parallel 2.0755 s (1.1521x). End-to-end CI speedup and official PIT backtest speedup **NOT VERIFIED**. Archived exact wheel hashes and native dependency identity also not verified in failed CI.
- Prior official watchdog [41151825793](https://github.com/kims34/openpilot-opkr/actions/runs/41151825793) SUCCESS does not grant M20 PIT, orders or Holdout.

## Railway production evidence (direct read, 2026-10-31)
- Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`. `describe_environment` and `get_staged_changes`: **staged=null**, no staged resources. No changes applied.
- `indexalert-pit-rebuild` deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` SUCCESS (deployed 2026-10-10); latest returned runtime event 2026-10-30 14:46:37 UTC = 23:46:37 KST, `COMMON_OHLC_NONPOSITIVE`, 27/803 common-stock rows, independent source/model/chronology admissions false, `ordering=DISABLED`, live orders false. Deployment SUCCESS does not imply fresh PIT data.
- `indexalert-runtime` deployment `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` SUCCESS; runtime monitoring log through 2026-10-31 06:25:43 UTC = 15:25:43 KST, not a PIT approval.
- `indexalert-kiwoom-real-readonly` deployment `a77fb922-b679-4d88-92c4-03054ec579cd` SUCCESS; health shows `state=online` while `running=0, crashed=1, total=1`, an unresolved status discrepancy. Its returned deploy log only records container startup 2026-10-29; no verified broker-authenticated success.
- `indexalert-backend`, `indexalert-push`, `db-query-readonly` health offline; `indexalert-pit-rebuild` and `indexalert-runtime` running 1/1. No operational repair authorized or attempted.

## Independent PASS / FAIL / NOT VERIFIED / NOT EVALUABLE
- PASS **only in bounded prior scope**: KRX 1,565 private weekday raw-pair storage integrity, frozen 34-case offline parity.
- FAIL: PR #418 archived manifest pinned blob consistency; PR #418 relative fail-closed security equivalence to PR #413.
- NOT VERIFIED: first-filed original 2021/2022 3-month consolidated operating profit, exact public available-at and correction/period lineage, issuer/security historic mapping, official KRX calendar/tradability/halts/corporate actions, executable prices/lot size/depth/fees/taxes, immutable PIT+runtime/source evidence admission, complete CI/backtest speedup.
- NOT EVALUABLE: post-cost/tax annual risk-adjusted NetEV, PF, CAGR, MDD, ES95/99, concentration, date-cluster robustness and tiny-capital capacity. No new returns computed.
- **M20 profitability NO-GO; ORDERING=false, Holdout unauthorized, no promotion or live orders.** Frozen H5/M20 horizon20-purge20, WF504/126/126, CPCV, Top3/NO_TRADE and all economic/risk thresholds unchanged.

## Next strictly separated work
1. OpenDART specialist independently prove first-filed original and public available-at/period/correction lineage, or attest exact missing original facts; never backfill from amended editions.
2. KRX specialist independently attest official historic session/status, issuer mapping, corporate actions, fillability and cost/tax schedule; do not reinterpret 1,565 stored pairs as market admission.
3. Optimization specialist reconcile PR #413 vs #418 fail-closed receipt and filesystem behavior, pinned source blob and archived environment identity in isolated synthetic-only tests; do not weaken expected SHA or safety flags to pass.
4. Orchestrator re-check raw source SHA/CI/Railway logs at next checkpoint. No M20 economic run until independent source/PIT/tradability/cost approvals; never recycle consumed Holdout or change frozen policy.

This commit adds **this audit document only** to the designated draft orchestration branch; no workflow, code, deployment, merge, account or trading state changes.
