# IndexAlert independent audit — 2026-11-12 08:22 KST

## Scope and evidence provenance
Read-only GitHub API and Railway production connector observations, 2026-11-11 23:22 UTC (~2026-11-12 08:22 KST). This is a source/evidence and isolated offline-runtime audit, **not** a PIT admission, backtest, trading approval, or deployment. No other specialist branches or workflows were changed.

## Exact GitHub refs (fresh)
- research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`
- development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`
- PR #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f` OPEN/DRAFT
- PR #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0` OPEN/DRAFT
- PR #414 `18c5418d9684d1717df58261ea27f28e514385b2` OPEN/DRAFT; gate blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`
- PR #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee` OPEN/DRAFT
- KRX PR #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`; #422 `c14857620973531013799e44625d43080904fd5f`; #423 `0e38004363cac9fc4475556b3a1c445de9af407f`, all OPEN/DRAFT.
- Prior isolated audit branch HEAD before this document: `968c82fa6bc60f7fdc574f3702ce46314d0c736f`.

## GitHub Actions (fresh jobs API)
- `38381997417`: 6/6 success; `38382214223`: 6/6 success.
- `38419111311`: 6/6 success.
- `38419649711`: 1/1 success.
- `38419439742`: 2/2 success.
- Original 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` is **NOT VERIFIED** by independent byte recomputation this run. Previously reported 13 adversarial mocks, 28 synthetic checks, 2.9656s serial vs 2.6209s concurrent (1.1315x regression phase) are historical assertions, **NOT VERIFIED** as new measurements. End-to-end CI and official backtest speed **NOT VERIFIED**.

## Railway production (fresh)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`.
- PIT rebuild: running 1/1; Runtime: running 1/1.
- KRX worker: running 0/1 (online label alone is insufficient); Kiwoom real readonly: running 0/1, crashed 1/1 (**FAIL**). Backend and Push offline. db-query-readonly offline with one critical issue.
- Staged environment patch `e113dacb-6705-4416-9997-dc694539d382`, `changes=[]`; not applied.
- Latest listed Kiwoom readonly deployment 2026-10-29 06:21:36 UTC, commit `85bb6fd10bcc9ff2b14abe1c774f0d99f8eb84ab`; KRX worker listed 2026-10-12 13:07:31 UTC commit `1e6367d2863a86c3470da13d81a955d277eba485`.
- 2026-11-11 22:20–23:25 UTC deploy logs: PIT 0, KRX 0, Kiwoom 0; Runtime returned 121 entries (query limit 120, connector count observed), including USD/KRW investing provider failure/fallback and market quote checks. Runtime market quotes are **not** official KRX PIT evidence.

## Evidence gate
| Claim | Verdict | Basis |
|---|---|---|
| Historical KRX 1,565/1,565 weekday raw-pair storage integrity | **PASS, historical scope only** | Prior Railway SHA evidence summarized in PR #414 gate; no new raw-pair recomputation |
| Official KRX calendar, halts, corporate actions, tradeability and cost/tax | **NOT VERIFIED / FAIL-CLOSED** | Missing independent official market-state lineage and execution proof |
| OpenDART original-filing semantics, public available-at and 2021/2022 initial consolidated 3-month operating profit | **NOT VERIFIED / FAIL-CLOSED** | 15 candidate SGML rows and adjacent-number signature do not establish PIT or meaning |
| Historical company/security mappings | **NOT VERIFIED** | No approved PIT mapping lineage |
| H5 holdout and dynamic independence | **FAIL-CLOSED** | Consumed/failed holdout must not be reused |
| M20 economic run; net-of-tax NetEV, PF, CAGR, MDD, ES95/99, concentration, regime robustness | **NOT VERIFIED / NO-GO** | Official source PIT gate unapproved |
| Isolated offline software CI jobs | **PASS for listed job conclusions only** | GitHub Actions jobs API |
| SHA parity and complete backtest acceleration | **NOT VERIFIED** | No independent fixture hash recomputation or end-to-end timing |

## Frozen restrictions and next safe work
Keep H5 Frozen, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and all cost, tax, NetEV, fill, risk, promotion gates unchanged. ORDERING=false is a **required policy**, not independently confirmed as a live flag in this run. Cache only with complete independent approved source/data/code/Frozen/runtime/evidence SHA-256 matches; fail closed. Only read-only postprocessing may parallelize; no dependent retraining or capital transitions. Next: obtain original first-filing available-at and lineage proof, official KRX status/corporate-action mapping, and independently recompute offline fixture hashes using approved artifacts; do not initiate M20 economics or model search. No deployment, merge, workflow edits, orders, funding, credentials, account permissions, or Champion promotion.
