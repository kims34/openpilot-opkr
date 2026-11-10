# IndexAlert independent audit — 2026-11-11 02:19 KST

Scope: read-only verification; no market experiment, merge, deployment, ordering or promotion.

## GitHub
Research HEAD (compare API): df474df348f22aa38b1dedaa59fcff66e548b406. Development ref index-alert-position-regen-fix-v1: diverged, 1148 ahead / 281 behind; exact development HEAD NOT VERIFIED because compare response lacks head commit SHA. Merge base c490974ff6619bb978dc6f83f9c24f2c46622f85. PR search for requested PR numbers returned empty; PR status/HEAD NOT VERIFIED, not assumed closed. Gate document fetch on research ref returned 404; document SHA NOT VERIFIED.

Actions job conclusions directly checked: 38381997417 6/6 success, 38382214223 6/6 success, 38419111311 6/6 success, 38419649711 1/1 success, 38419439742 2/2 success. Case-level SHA 5d957eb8b89242d3ba7aa4966a7b81f8db5500aee8a82ca223dd121a7b23cc34, 13 adversarial and 28 synthetic cases NOT independently recalculated. 2.9656s/2.6209s=1.1315x prior claimed regression-phase comparison, not full CI or market acceleration.

## Railway production
Project d1c1a050-b7d6-41ce-b300-13c20f82a20a; environment 83d5840b-270e-4d3f-a941-a37fd4a55ff7. PIT rebuild deployment 8b354fc1-cfb2-4ef0-863e-67f7f5dda2b5 SUCCESS running 1/1; runtime eaaa9f67-b9f2-41d2-832c-7d6fad9b9b00 SUCCESS running 1/1. KRX historical worker 16c93d7c-7cd0-4d84-a327-298d2805376c SUCCESS running 0/1; runtime availability NOT VERIFIED. Kiwoom real readonly a77fb922-b679-4d88-92c4-03054ec579cd deployment SUCCESS but running 0/1 crashed 1/1: runtime FAIL. Backend, push, db-query-readonly offline; db-query-readonly critical issue 1. Pending staged patch e113dacb-6705-4416-9997-dc694539d382 changes [] untouched. Deploy log query since 2026-11-10T16:00Z for PIT/KRX/Kiwoom returned zero entries, not a proof of healthy operation.

## Evidence gates
Historical reported OpenDART 15 SGML candidates and adjacent numeric signatures: candidate extraction only; original-filing meaning/public available-at/PIT NOT VERIFIED. Historical reported KRX 1565/1565 weekday original-pair storage integrity PASS only in earlier scope; official calendar, trade state, corporate actions, execution, cost/tax NOT VERIFIED. 2021/2022 initial three-month consolidated operating profit period/correction lineage, issuer/security history mapping NOT VERIFIED. NetEV, PF, CAGR, MDD, ES95/99, return concentration and temporal robustness after transaction costs and tax NOT VERIFIED. M20 economic run NO-GO. H5 consumed holdout not reusable.

Frozen H5; M20 horizon20/purge20; WF504/126/126; PIT/label/Purged/CPCV/independent holdout/Champion/Top3/NO_TRADE and all economic gates unchanged. ORDERING=false required, actual environment value NOT VERIFIED. Fail-closed cache only on approved source/data/code/Frozen/runtime/approval SHA256 match. Parallelism restricted to independent read-only postprocessing. No workflow changes, retraining parallelization, market performance experiment, merge, deployment or trades.

Next: obtain authoritative original filing/PIT evidence and exact period/correction lineage; KRX calendar/tradability reconciliation; independently hash CI fixture artifacts; investigate crashed readonly replica through logs/owner without deployment. Do not release M20 until independent evidence gate passes.
