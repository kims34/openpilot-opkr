# IndexAlert independent profitability and isolated runtime audit — 2026-11-11 21:17 KST

Read-only GitHub/Railway inspection; no model, workflow, data, trading, deployment or PR modifications. Existing frozen gates remain binding.

## Exact source references
- Research index-alert-research-v1: `df474df348f22aa38b1dedaa59fcff66e548b406` (GitHub compare identical 0/0).
- Development index-alert-position-regen-fix-v1: `1e6367d2863a86c3470da13d81a955d277eba485` (compare identical 0/0).
- OPEN/Draft/unmerged PR heads: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- #414 gate `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md` blob SHA `984c933651f39f1ee9e26a1d7ac3893aaa5335be`; gate on PR head, not necessarily frozen base.
- GitHub Actions [38381997417](https://github.com/kims34/openpilot-opkr/actions/runs/38381997417), [38382214223](https://github.com/kims34/openpilot-opkr/actions/runs/38382214223), [38419111311](https://github.com/kims34/openpilot-opkr/actions/runs/38419111311), [38419649711](https://github.com/kims34/openpilot-opkr/actions/runs/38419649711), [38419439742](https://github.com/kims34/openpilot-opkr/actions/runs/38419439742), [38498552499](https://github.com/kims34/openpilot-opkr/actions/runs/38498552499): respectively 6/6, 6/6, 6/6, 1/1, 2/2, 6/6 jobs success. Job completion is not independent artifact byte rehash.
- Previous reported 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: **NOT VERIFIED independently this run**. Offline-only regression PASS at job level; synthetic 13 adversarial / 28 extra cases are historical assertions, not fresh replay. Single runner serial 2.9656s vs concurrent 2.6209s => regression-phase 1.1315x; full CI and real official backtest speed **NOT VERIFIED**.

## Railway production evidence (2026-11-11 10:00–12:20 UTC)
- Environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`; PIT rebuild deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5` running 1/1; runtime `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00` running 1/1.
- KRX worker deployment `16c93d7c-7cd0-4d84-a327-298d2805376c` running 0/1; cannot treat successful deployment as live source validation. Kiwoom real readonly `a77fb922-b679-4d88-92c4-03054ec579cd` running 0/1, crashed 1/1: **FAIL runtime** despite service-level online label. Backend/push/db-query-readonly offline; latter critical 1.
- PIT logs: 10 observed errors `KRXProspectiveOpenAPISourceError / COMMON_OHLC_NONPOSITIVE` from 10:00:54 to 12:16:18 UTC. Explicit `fresh_alpha_observation_admitted=false`, `funds_movement_authorized=false`. This is a live fail-closed **PASS for observed block behavior**, **FAIL for prospective source validity**, not PIT approval. KRX and Kiwoom service deploy logs 0 entries in selected window.
- Runtime log shows Investing USD/KRW HTTP errors and Yahoo fallback at 12:11 UTC; not an official source.
- Staged Railway patch `e113dacb-6705-4416-9997-dc694539d382` with zero changes: untouched.

## Admission decision
| Check | Decision | Basis |
|---|---|---|
| KRX 2017–22 private 1565/1565 weekday pairs | PASS **prior storage integrity only** | Historical evidence, no new private volume byte rehash |
| OpenDART 2021/2022 first original 3-month consolidated operating profit, period/correction lineage, exact public available-at | NOT VERIFIED | Original ZIP/SGML candidate matches do not prove account semantic, 3-month CFS cell or first public instant |
| Historical issuer/security as-of mapping | NOT VERIFIED | No complete source-backed lineage |
| Official KRX session/calendar/halt/delist/actions, realistic fills, taxes and costs | NOT VERIFIED | 90 uncertain days, 12003 zero-activity and 27 suspect nonpositive OHLC blocked |
| Prospective KRX input acceptance | FAIL | Repeated COMMON_OHLC_NONPOSITIVE; deny admission |
| Offline CI regression jobs | PASS (job status only) | Six named runs successful; 34-case SHA independently NOT VERIFIED |
| Official net annual risk-adjusted profitability, NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness | NOT VERIFIED | No authorized M20 PIT economic run |
| Whole-backtest optimization | NOT VERIFIED | Only synthetic regression phase timing reported |

## Immutable constraints and next gates
- Frozen H5 and M20 horizon20/purge20, WF504/126/126, PIT/Purged/CPCV/independent Holdout/Champion/Top3/NO_TRADE, costs/taxes/NetEV/execution/risk/promotion unchanged. H5 failed/consumed holdout and Dynamic outputs cannot be recycled. M20 **NO-GO**.
- Cache only on matching independently approved source/data/calculation/Frozen/runtime/approval SHA-256 evidence; fail closed. Parallelize only independent read-only postprocessing, never dependent retraining or capital transitions.
- Next: independent original-filing CFS cell+public timestamp proof from OpenDART owner; KRX official calendar/status/actions/feasibility proof from owner; independently reproduce offline fixed SHA and whole-CI wall time only if safe; then gate review, **not** an automatic M20 run.
- `ORDERING=false`; no real orders, funds transfers, credentials/permissions, Champion promotion, PR merges, auto-deploy or workflow edits. All require appropriate separate approval. No changes to other Work rooms.
