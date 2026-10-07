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


## Owner-supplied email scope comparison (2026-10-07)

# Owner-supplied KRX email text — 2026-10-07 21:52 KST

Owner supplied a copied email header/body in this chat. Display name: KRX Data Marketplace Team; displayed date: Oct2,2026,3:30PM (email display timezone not specified). Body identifies the KRX data business department. The copied text states personal research may download/query full historical periods, use programmatic low/high-frequency collection without separate advance approval, and prohibits external leakage/sale/third-party distribution.

Scope comparison: consistent with the previously recorded HIST_ACQ_v3 personal/internal research, full-history, automated/high-frequency, no-redistribution scope. Existing permission/scope disposition is not reset; no repeat permission request is necessary. This email text does not separately authorize real orders, account permission changes, data resale or public distribution.

Evidence limits: owner-supplied transcription is now available; actual sender email address, full message authentication headers, original message bytes and timezone are not supplied. Do not treat linked tracking images as sender authentication or fetch them. No original approval-document SHA256 was generated from pasted/normalized text. Original-document authentication and its exact linkage to existing authorization metadata/raw/receipts/source/scope contract identities remain independently open. Historical availability/PIT lineage and economics admission are not supplied by this usage statement.

Next minimal owner input: expand email sender details and supply only the actual sender address; do not forward passwords/API keys or unrelated mail. Existing private-store audit and no-holdout/no-order boundaries remain unchanged.



## Owner email header screenshot — 2026-10-07 21:53 KST

Read the owner-attached sender-details screenshot directly. Visible From: KRX Data Marketplace Team <krxdata@krx.co.kr>; Reply-To:krxdata@krx.co.kr; mailed-by:krx.co.kr; date:Oct2,2026,3:30PM (display timezone not specified). Subject concerns KRX Data Marketplace statistics automated-query permission and official delivery route. Recipient personal name/address omitted from this record.

This supplies the previously missing displayed sender address and Gmail mailed-by domain, consistent with the copied body and KRX domain. It is owner-presented header evidence, not a raw-message DKIM/DMARC verification; original .eml bytes/full authentication headers and document-to-receipt/source/scope fingerprint linkage remain unverified. No synthetic approval-document hash created. No additional owner email/header request is required for the present scope comparison. HIST_ACQ_v3 recorded scope remains unchanged; no approval reset, data admission or real-trading authorization follows.


## Exact v3 identity comparison — 2026-10-07 22:00 KST

New independent code inspection: research194da5016ad3aecc2ceb25944666daa74f038083, INDEXALERT_KRX_PERMISSION_REPLY_EVIDENCE.json/.md and research_v1_krx_authorization_evidence.py. The validator's evidence_document_sha256 is an externally supplied document identity; validating64hex and normalized record hash does not authenticate document bytes.

The existing v3 evidence preserves original screenshotSHA1983036114310ea42dd60ad49fc52c19a7378f7f1d3f1c1a65dabc7b4d1cf1e1 and redacted normalized email-recordSHA7361065e06599f947216233fc84e97126b1675de5af41068114cf6ef9577e304. These are distinct from a raw .eml hash and cannot be replaced with one.

The owner-presented header has a different displayed subject (“RE: [이용문의] KRX Data Marketplace 통계 데이터의 자동 조회 허용 여부 및 공식 제공 경로 문의”) from the existing v3 subject (“[KRX Data Marketplace] 데이터 이용 문의에 대한 답변의 건”). Existing v3 observation is15:06KST on Oct2 with exactlatestreplytime unknown; newly shown message display says Oct2,15:30 with displaytimezone unspecified. Therefore scope agreement is established, but exact same-message identity/timestamp cannot be asserted or overwritten. This is an identity ambiguity, not a finding of invalid rights or forged mail.

Minimum next original input: the specific KRX reply .eml from Gmail Show original > Download original, supplied privately by the owner. Parse only that message, retain original bytes identity separately from existing screenshot/redacted-record hashes, inspect its actual Date/From/authentication headers and whether the earlier thread is present. Do not replace existing metadata or backdate any capture. Even a verified .eml alone does not close raw/receipt/source/scope/PIT links.

Earlier “no additional owner email/header request required” applied to scope comparison. Exact original-document binding now requires original bytes. No repeat approval is requested and GateFscopePASS remains recorded. No acquisition/performance/holdout/live authorization changed.
