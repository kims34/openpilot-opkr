# IndexAlert independent audit — 2026-11-15 08:25 KST

Scope: read-only GitHub and Railway evidence review; this isolated document does not authorize PIT, economic replay, model search, deployment, order, account change, Champion promotion, or merge. Prior audit branch HEAD before write: `9e168c8b376bf4a3a14993931f53cafd6498601e`.

## Exact refs checked
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- Draft open unmerged PR HEADs: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`; #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`; #414 `18c5418d9684d1717df58261ea27f28e514385b2`; #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`; KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 integration gate file read at its HEAD: `docs/INDEXALERT_PROFITABILITY_INTEGRATION_GATE_2026-10-13.md`. The document explicitly preserves PIT NO-GO and non-reusable H5 holdout.
- GitHub Actions checked via actual job records: #38381997417 PASS 6/6; #38382214223 PASS 6/6; #38419111311 PASS 6/6; #38419439742 PASS 2/2; #38419649711 PASS 1/1; #38486028854 FAIL 1/1 (job 115599778959).
- #38486028854 job log directly shows `SourceDriftError: archived blob mismatch: research_v1_runtime_manifest.py expected=108f66714602a1bd3ae42c34dcca7c16e38f460b observed=e428789e2e97ca7be3a4482e0df23b483a1ad69d`. This is a Git blob SHA-1 provenance gate failure, **not** evidence of a 34-case SHA-256 parity failure. Archived 34-case SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` was not independently recomputed this run: NOT VERIFIED.
- PR #418 reported serial 2.9656s vs concurrent 2.6209s, regression-only ratio 1.1315x; full CI and real official backtest acceleration NOT VERIFIED.

## Railway production live read
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, 1/1 replica; Runtime SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, 1/1.
- KRX historical worker SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, 0/1 running; Kiwoom real-readonly-run SUCCESS, 0/1 running. Do not interpret deployment SUCCESS as continuously active worker.
- Backend/push offline with warnings; db-query-readonly offline with one critical warning.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382`, started 2026-10-29T06:20:53Z, unchanged/unapplied.
- Read-only log window 2026-11-14T22:15:00Z–23:30:00Z: PIT 0 entries, KRX 0 entries; Runtime returned 101 entries including 23:24:44Z Investing USD/KRW HTTPError with Yahoo fallback, market-state CLOSED, and ECOS prior-close alignment. None certifies original DART/KRX PIT.

## Independent gate decisions
- KRX 2017–2022 private 1,565/1,565 stored pairs: historical reported storage-integrity PASS only; official trading calendar/status, corporate actions, fillability, tax/cost: NOT VERIFIED.
- OpenDART original-vs-amended SGML candidate-row signature from #38419439742: offline CI PASS only; 2021/2022 exact first three-month consolidated operating profit, original-filing meaning, full correction lineage and precise public available-at/PIT: NOT VERIFIED.
- Historical issuer/security mapping and label PIT: NOT VERIFIED.
- H5/0–N consumed holdout: NO-GO, no retroactive tuning/reuse.
- M20 official PIT and after-fee/tax NetEV/PF/CAGR/MDD/ES95/ES99/concentration/temporal robustness: NOT VERIFIED; economic RUN prohibited.
- Optimization offline regression CI: designated older suites PASS; #418 subsequent integration FAIL on manifest source provenance; no performance certification.
- Frozen H5; M20 horizon20/purge20, WF504/126/126; independent Holdout, Champion, Top3, NO_TRADE; ORDERING=false: unchanged.

## Safe next actions
1. Source owners independently prove original-filing exact quarter/available-at and official KRX historical state/corporate actions with immutable raw hashes and times; do not infer approval from storage or CI success.
2. Optimization owner independently resolve archived manifest SHA-1 mismatch on its own isolated PR; preserve immutable baseline and rerun synthetic/offline-only tests, no workflow bypass.
3. Independently verify approved input, code, Frozen policy, runtime and evidence SHA-256 before enabling fail-closed cache; parallelize only independent read-only postprocessing.
4. Do not merge #413/#414/#418, deploy, activate ordering, use real capital, change account privileges or promote Champion without explicit separate approval.

No new PIT admission or profitability approval obtained.