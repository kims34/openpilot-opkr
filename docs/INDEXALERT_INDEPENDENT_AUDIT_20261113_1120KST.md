# IndexAlert independent profitability and isolated runtime audit — 2026-11-13 11:20 KST

Scope: read-only GitHub/Railway evidence; synthetic offline software-only verification, no trading, deployment, merging, workflow edits, market backtests or policy changes. Prior audit commit e49d2d7e5ed1ba51cea367c65c6e63704b5fb764 is parent of this isolated branch.

## Exact refs and GitHub evidence
- Research index-alert-research-v1 HEAD df474df348f22aa38b1dedaa59fcff66e548b406; compare against pinned commit identical (ahead 0/behind 0).
- Development index-alert-position-regen-fix-v1 HEAD 1e6367d2863a86c3470da13d81a955d277eba485; compare identical.
- Draft OPEN/unmerged PR heads: #412 bf3d9514a87c53b1775e22ec9ba7711f6cecc49f; #413 f003ef6247e16fcc71bd3b1b20cd4904c4d984c0; #414 18c5418d9684d1717df58261ea27f28e514385b2; #418 2f98401cc50a6c6a25808a98516efd5bf0c944ee; KRX #420 fab3cbbd63a951a4e081f9e7f08c1391ca308581, #422 c14857620973531013799e44625d43080904fd5f, #423 0e38004363cac9fc4475556b3a1c445de9af407f. No newly observed PR head changes.
- Actions read directly (GitHub job conclusions): 38381997417 6/6 PASS; 38382214223 6/6 PASS; 38419111311 6/6 PASS; 38419649711 1/1 PASS; 38498552499 6/6 PASS; OpenDART 38419439742 2/2 PASS; PR #418 integrated archived-case 38486028854 1/1 FAIL.
- Last audit's direct job log isolated failure: research_v1_runtime_manifest.py archived Git blob expected SHA-1 108f66714602a1bd3ae42c34dcca7c16e38f460b, observed e428789e2e97ca7be3a4482e0df23b483a1ad69d, SourceDriftError. These are Git SHA-1 blob identifiers, not SHA-256 evidence. Preserve immutable gate; no re-pin/bypass.
- Prior fixed 34-case SHA-256 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34 remains independently NOT VERIFIED (not rehashed this run). #413/#418 code equivalence, overall CI/backtest acceleration NOT VERIFIED. Prior observed serial 1.7114s vs parallel 2.5776s in #413 regression slice is negative; do not generalize.

## Railway production read-only evidence
- Project d1c1a050-b7d6-41ce-b300-13c20f82a20a, production environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7.
- PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 1/1 running; runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 1/1 running.
- Kiwoom real-readonly deployment a77fb922-b679-4d88-92c4-03054ec579cd displayed online/SUCCESS but replica 0 running/1 crashed: operational FAIL. KRX worker deployment 16c93d7c-7cd0-4d84-a327-298d2805376c 0 running/0 crashed; no proof of current activity. Backend/push/db-query-readonly offline; db-query-readonly critical=1.
- Environment status pending staged patch e113dacb-6705-4416-9997-dc694539d382 with empty changes, not applied.
- Railway deploy log window 2026-11-13 01:20–02:21 UTC: PIT 0, KRX 0, Kiwoom 0 entries; runtime 161 entries returned (requested limit 160). At 02:20:44 UTC Investing USD/KRW HTTP errors and Yahoo fallback. Silence is not remediation. ORDERING runtime actual value NOT VERIFIED, required false.

## Gate verdict and next work
- Historical private KRX 2017–2022 raw-pair storage 1565/1565 weekday integrity PASS only as previously established; official calendar, market status, corporate actions, fills and fee/tax correctness NOT VERIFIED. Existing 27/803 bad OHLC remains unresolved FAIL by previous evidence (not rehashed here).
- OpenDART 15 candidate SGML rows/numeric-adjacency signature prior CI PASS at software signature level only; original-filing semantic identity, public available-at/PIT, 2021/2022 first 3-month consolidated operating profit period and correction lineage NOT VERIFIED.
- Historical entity/security mapping, NetEV/PF/CAGR/MDD/ES95/99, concentration and temporal robustness net of all transaction costs/taxes NOT VERIFIED; independent annual risk-adjusted profitability admission FAIL CLOSED / M20 NO-GO.
- Frozen H5, M20 horizon20/purge20, WF504/126/126, PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and all cost, tax, execution, risk, promotion thresholds unchanged. H5 consumed holdout and Dynamic cannot be reused independently. ORDERING=false required.
- Next: source owner supplies original DART filing/public timestamp and KRX official status/executability and exact private source SHA; offline independent comparison of archived manifest blob differences, fixed 34-case SHA-256 and cache fail-closed evidence. Do not modify other teams' code or workflows, run market profitability/M20, deploy, merge #413/#414/#418, trade, transfer funds, alter credentials or promote Champion without separate explicit approval.
