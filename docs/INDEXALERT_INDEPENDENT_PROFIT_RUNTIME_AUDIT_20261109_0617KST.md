# IndexAlert independent profitability/runtime audit — 2026-11-09 06:17 KST

Scope: read-only GitHub and Railway production inspection; this audit document is the only intended write. No model, workflow, market backtest, trading, deployment or merge.

## GitHub immutable evidence
- PR #414: OPEN Draft HEAD `18c5418d9684d1717df58261ea27f28e514385b2`; base SHA `3b8b7830612a6284d7c7a60628cb527cb741627a`. Gate file blob `984c933651f39f1ee9e26a1d7ac3893aaa5335be` on PR branch (not research base).
- PR #412: OPEN Draft HEAD `bf3d9514a87c53b1775e22ec9ba7711f6cecc49f`.
- PR #413: OPEN Draft HEAD `f003ef6247e16fcc71bd3b1b20cd4904c4d984c0`.
- PR #418: OPEN Draft HEAD `2f98401cc50a6c6a25808a98516efd5bf0c944ee`.
- KRX #420 `fab3cbbd63a951a4e081f9e7f08c1391ca308581`, #422 `c14857620973531013799e44625d43080904fd5f`, #423 `0e38004363cac9fc4475556b3a1c445de9af407f`, all OPEN Draft.
- Branch names research `index-alert-research-v1` and development `index-alert-position-regen-fix-v1` exist; current branch tip SHAs not independently resolved by branch search. PR #414 base SHA is not proof of current branch tip.
- Original Actions 38381997417, 38382214223, 38419111311: each 6/6 jobs SUCCESS. 38419649711: 1/1 SUCCESS. OpenDART 38419439742: 2/2 SUCCESS. Chronology Anchor 41515392296: auto-anchor FAILURE, validation SKIPPED. Historical fixed 34-case SHA `5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34` and synthetic 28 cases / 1.1315x regression phase are prior claims, not independently recomputed this run.

## Railway production
Project `d1c1a050-b7d6-41ce-b300-13c20f82a20a`; environment `83d5840b-270e-4d3f-a941-a37fd4a55ff7`.
- PIT rebuild and runtime each 1 running / 0 crashed replica.
- Real readonly service reports online/SUCCESS but replica 0 running / 1 crashed: runtime health FAIL.
- db-query-readonly offline, 1 critical; backend offline 4 warnings, push offline 1 warning.
- Pending staged patch `e113dacb-6705-4416-9997-dc694539d382` with empty changes []; not applied.
- Service deploy-log query for PIT, KRX worker, real readonly in 2026-11-08 20:00–21:30 UTC returned 0 entries each. Absence of entries does not certify normal operations.

## Admission matrix
- Historical offline CI regression job status: PASS (jobs only; software synthetic).
- KRX 2017–2022 private 1565/1565 stored weekday SHA pairs: PASS solely as earlier reported storage integrity, not independently re-read today.
- Official first original 2021/2022 CFS 3-month operating-profit cell/period and corrected lineage, public available-at PIT: NOT VERIFIED.
- Historical issuer/security mapping; official KRX session/status/corporate action/fillability, tax and execution costs: NOT VERIFIED.
- 90 unresolved days, 27 invalid OHLC and 12003 zero-activity quarantines: prior blocking evidence; no admission.
- NetEV/PF/CAGR/MDD/ES95/99/concentration/temporal robustness: NOT VERIFIED, M20 NO-GO.
- Overall CI or actual backtest speedup: NOT VERIFIED. Only independent read-only postprocessing can be parallel; dependent retraining and capital transitions remain serial.
- Chronology Anchor: FAIL. Real readonly runtime replica health: FAIL.
- Frozen H5 / M20 horizon20 purge20 / WF504-126-126, PIT/purged/CPCV/independent holdout/Champion/Top3/NO_TRADE unchanged. Consumed H5 holdout/Dynamic not reusable. ORDERING=false policy required; this run did not read live environment variable value.

## Next evidence
1. Obtain original-provider ZIP/SGML/XBRL and exact publication timestamps with immutable SHA, correct 2021/2022 original 3-month consolidated operating-income period/lineage.
2. Independently reconcile KRX official calendar, issuer-security mapping, corporate actions, tradability and private bad OHLC; keep fail-closed.
3. Diagnose chronology anchor and readonly replica without production changes; confirm actual ORDERING setting through authorized read-only evidence.
4. Only after PIT admission and separate explicit authorization evaluate one frozen M20 economics run; never use consumed holdout.
