# KRX origin and cross-audit binding review
Research issue: IA-20261006-ORIGIN-BINDING
Status: OPEN_REQUIRED_INDEPENDENT_EVIDENCE / REVIEW_ONLY_NOT_ADOPTED
Prepared: 2026-10-06 UTC
Authoritative code inspection ref: 93a51a5e666110dc42439b31c610a695cb232751
Scope: source governance engineering; no empirical Alpha trial.

## Findings from existing producers
All 122 root research_v1_*.py files listed in the actual GitHub tree were read at the pinned inspection ref. One transient missing-content fetch for research_v1_exit_policy_compare.py was retried successfully; that diagnostic was read only, not executed. The only literal source_contract_fingerprint_sha256 code references in this inspected set are in research_v1_krx_investor_flow_lineage.py. This is a scoped repository finding, not proof that no external materializer or alternate field spelling exists.

| Field | Established producer / meaning | Existing binding | Unresolved issue |
|---|---|---|---|
| record_fingerprint_sha256 | Authorization validator hashes normalized approval metadata including family, route, use scope, document SHA, capture and validity timestamps. | Historical worker _load_auth_record validates the record at evaluation_time and propagates its reference and record hash into acquisition receipts. | A valid metadata hash alone does not authenticate its issuer/document bytes or prove independent KRX origin. |
| receipt_fingerprint_sha256 | Acquisition receipt hashes its declared request/time/schema/content/current-public-evidence/authorization/authority body. | Acquisition batch verifies receipt bodies and forbids mixed authorization references/hashes/route/dataset/schema. | Verify real raw/object/receipt/approval-document lineage independently; no synthetic substitute. |
| batch_fingerprint_sha256 | Acquisition batch hashes the homogeneous receipt set and declared metadata/counts. | Admission revalidates batch body; PR120/121 additionally revalidate actual A-F entries and closure/authority summaries. | Does not define the investor-lineage source-contract hash or independent expected-scope identity. |
| source_contract_fingerprint_sha256 | Investor lineage accepts a supplied original SHA string and requires a single value; audit now reports that value. | Row chronology, publication floor and current public-evidence metadata are revalidated. | No generator/materializer of this fingerprint was found in the 122 inspected root research modules. Meaning and prospective external provenance remain unresolved. |
| scope_contract_fingerprint_sha256 | Expected-scope materializer bind_scope_contract_fingerprint accepts an externally frozen original SHA string and attaches it without changing keys. | Coverage requires a single expected-scope fingerprint and preserves its value. | The binder does not define what external object/version the hash identifies; do not assume expected-scope JSON/blob/task-set hash equality. |

Exact inspected blobs:
- authorization validator a8b5c40cfba32a92c1add0820f2f900e3823aec6 (pre-PR118/119 type-hardening baseline)
- acquisition receipt379ab054d968a02d8f966cc6ed1c73cc74edfaba
- acquisition batchc7ecce61a526d105ac0d5e088518baa1d3c36138
- historical workerad7a7ba279e298e5883473a8cfe97a397826c170
- investor lineage8668d033a05d85e3c6d59a0a6118236282be9e90
- investor coverage78a2dcb09949286faabd0d2f116b911904c64a71
- expected-scope materializer11491907f7653a8ef4b443fce52cd2dc573e05cc
- source admission8761ee5e3f0ccc2d372c9cf9d27aab57358890d1 (pre-PR120/121 summary-revalidation baseline)

## Prospective research review questions — not operational criteria
1. Identify the existing external frozen source-contract document/version used by investor lineage and the expected-scope binder, or formally specify a prospective review object if no previous definition exists. Do not silently repurpose batch, Git blob, public evidence, task-set or receipt fingerprints.
2. Establish independently verifiable links among approval-document bytes, validated approval metadata, actual request/raw objects/receipts, dataset lineage and independently attested scope. Preserve distinct hash domains and original time/identity semantics.
3. Locate contract-eligible historical event/publication/availability records. Retrieval/capture time cannot become historical availability. Preserve20:00KST investor publication floor and all exact chronology.
4. Preserve the distinction between internally consistent metadata, externally authenticated source evidence, source-governance review candidates and formal A-F closure. Even six PASS source results do not permit feature performance, sealed holdout, promotion or live trading.
5. Define review/attestation responsibility and prospective chronology under existing governance before any new binding object is adopted. This note supplies neither an external attestation nor an adopted Challenger.

## Authority
This review is not a contract replacement, ACCEPTED/CHALLENGER CANDIDATE, source gate PASS, trial preregistration or deployment instruction. No Champion/model/threshold/cutoff/PIT/labels/WF/Purged-CPCV/purge-embargo/cost/slippage/partial-fill/NetEV/Precision/PF/MDD/ES95-99/capacity/holdout-burn/promotion criterion changes. Performance, sealed-holdout and live-trading authorization remain false. Consumed failed invalid v1 holdout and its immutable lineage are never reused or repaired. No real order, fund movement or broker permission change.
