# IndexAlert independent audit — 2026-11-12 14:20 KST

Scope: read-only GitHub/Railway verification; no economic backtest, source changes, workflow edits, merge, deploy, ordering, or trading. Independent audit branch starting HEAD: `2c7ed106bb6d9ef581cd4120b605fd21324807a5`.

## Verified GitHub source refs
- Research `index-alert-research-v1`: `df474df348f22aa38b1dedaa59fcff66e548b406`.
- Development `index-alert-position-regen-fix-v1`: `1e6367d2863a86c3470da13d81a955d277eba485`.
- PRs OPEN/Draft/unmerged: #412 `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`, #413 `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`, #414 `18c5418d9684d1717df58261ea27f28e514385b2`, #418 `2f98401cc50a6c6a25808a98516efd5bf0c944ee`, #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`.
- PR #414 frozen gate document at PR HEAD: blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be`. Its explicit economic decision is NO-GO.
- GitHub Actions runs `38381997417`, `38382214223`, `38419111311`: each 6/6 jobs SUCCESS; `38419649711` 1/1 SUCCESS; `38419439742` 2/2 SUCCESS. Run commit SHAs respectively `55e7fe2b3fe322e39f817914ff1ed5b589bbe0da`, `05d73661bcc879fe0dd66ffcea5fe1f5ee6fbd56`, `b22e4f39517c2bc38e173e63e8fd52f29a535dad`, `8f363b8683d34a48754916b34810a5a8bb958896`, `39af5b0043e122bc0e42935d8813759ff6c1a6e7`. Jobs succeeded, not independent recomputation of artifacts.
- 34-case expected SHA-256 `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34`: independent artifact-byte recalculation NOT VERIFIED. Historical synthetic 28 cases, adversarial 13 mocks and serial 2.9656s / concurrent 2.6209s (1.1315x regression phase) are historical claims, not end-to-end speed verification.

## Railway production read-only evidence (2026-11-12 04:20–05:25 UTC)
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`, environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild SUCCESS deployment `8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5`, running 1/1; runtime SUCCESS `eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00`, running 1/1.
- KRX worker SUCCESS deployment `16c93d7c-7cd0-4d84-a327-298d2805376c`, running 0/1, crashed 0/1: current active processing NOT VERIFIED (could be idle job).
- Kiwoom real read-only SUCCESS deployment `a77fb922-b679-4d88-92c4-03054ec579cd`, running 0/1 and crashed 1/1: runtime FAIL despite service state online.
- Backend, push and db-query-readonly offline; db-query-readonly critical notification 1.
- PIT, KRX and Kiwoom deployment log query returned zero entries in the specified window; absence of logs is not a healthy-state proof.
- Runtime 31 log entries: 05:19 UTC USD/KRW Investing HTTPError and Yahoo fallback; no independent market-data accuracy approval.
- Staged patch `e113dacb-6705-4416-9997-dc694539d382` has zero changes, left untouched.

## Economic and provenance gates
- PASS (historical limited scope only): 2017–2022 private KRX weekday 1565/1565 stored raw pairs integrity; original/correction DART candidate-row byte/signature checks; offline software CI jobs listed above.
- NOT VERIFIED / fail-closed: official original-filing semantics and exact public available-at PIT, 2021/2022 first 3-month consolidated operating-income period and correction lineage, historic entity/security mapping, official KRX calendar/trading status/corporate actions/executability, costs/taxes, NetEV/PF/CAGR/MDD/ES95/ES99/concentration/temporal robustness, 34-case independent SHA recomputation, full CI/backtest acceleration, live ORDERING flag.
- FAIL (operational): Kiwoom read-only replica crashed, offline backend/push/db-query-readonly; does not imply a strategy profitability failure.
- M20 PIT and economic run NO-GO; H5 consumed holdout and Dynamic results not reusable as independent holdout. Keep Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and existing risk/tax/cost/execution criteria unchanged. ORDERING=false remains required, not independently observed live.
- Cache only on independently approved source/data/code/frozen-policy/runtime/evidence SHA-256 exact match (fail closed). Parallelize read-only post-processing only; never dependent retraining or capital transition.
- Next: obtain independent source timestamp/lineage and official KRX status evidence through authorized read-only channels; verify artifacts' bytes and CI wall-clock using reproducible offline synthetic inputs only. Do not run new official-market performance tests or M20 economics before PIT approval. No merges, production deployments, real orders, capital movements, credential changes or Champion promotion without separate explicit approval.
