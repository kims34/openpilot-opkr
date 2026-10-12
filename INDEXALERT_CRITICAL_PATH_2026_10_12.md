# Critical path decision — 2026-10-12 KST

Scope: bounded Astra review, not a strategy change or readiness approval.
Reviewed research HEAD 56dc0ceee2778362ccd9d7c996b1a7d4dadec923.

## Decision that changes the work order

H5 is DEVELOPMENTAL_NOT_CURRENTLY_PROMOTABLE. The existing
INDEXALERT_H5_PROFITABILITY_AUDIT_2026_10_09.md records a negative date-level
95% lower bound and best-five-date-excluded mean -0.36245729%, PF 0.83593211.
These are existing developmental results, not a new performance run.
Do not repeat this completed audit or treat source/broker repairs as an Alpha pass.

The Sep28 quarantine shadow is diagnostic only. Its 13 existing synthetic tests
passed locally during this review; canonical Action 38184726579 also completed
successfully at the reviewed HEAD. It requires a caller-provided frozen Top3,
does not generate that Top3, authenticate the source hash, repair warmup data,
or resolve affected-position economics. The source gate fails before prospective
decision generation. Therefore this downstream veto alone cannot unblock the
upstream producer. No remaining 776-stock tradability or PIT admission follows.
Do not wire it around the all-universe source gate, manufacture a Top3 from
filtered data, backfill ranks, remove held positions, or replay past decisions.

## Bounded critical sequence

1. Unblock genuinely new Alpha evidence: continue the already preregistered
   M20 source-lineage pilot; keep H5 future-only collection separate. Both retain
   their existing KRX/PIT/status/economics dependencies. M20 is not a shortcut
   around those requirements and has no numerical performance result yet.
2. Admit source/version/availability and fixed-policy evidence before any
   permitted empirical run. Reject failing candidates without rescue tuning.
   Existing consumed failed-invalid v1 holdout remains inaccessible for reuse.
3. Once an admissible candidate exists, complete its required independent
   validation/Shadow/confirmation plus native execution-readiness evidence.
   Kiwoom connectivity alone is not an investment approval.
4. Only after all existing Tiny Live gates and separately explicit real-order
   activation may the 100,000-KRW stage start. Final full-live evidence thresholds
   are separate; do not confuse them with permission to start capped validation.

## Concrete source diagnostic change

The M20 pilot previously emitted the same error for zero and multiple matches
of its single configured operating-profit account. This cannot distinguish a
missing taxonomy ID from duplicate statement lines. Preserve exact selection,
filing receipt/quarter checks, the same three official requests and all false
admission flags. Emit only fixed counts on cardinality failure, including the
count of dart_OperatingIncomeLoss as an unaccepted diagnostic hypothesis.
Never publish provider rows, monetary values, receipts or credentials.
The alternate ID is not admitted merely because it is present.

Eight local synthetic pilot tests pass, including missing vs duplicate lines,
unrelated issuer/year/statement filtering, no extra requests, privacy and no
admission. Remote PR safety and subsequent official source response remain
separate evidence. A workflow failure that retains SOURCE_GAP_FAIL_CLOSED is
not fixed by making CI green without source evidence.

Next source-dependent decision: use the newly distinguished failure and actual
aggregate candidate count to determine whether official taxonomy semantics need
verification or conflicting lines need reconciliation. Do not guess account
equivalence from a label, accept the first duplicate, or change the M20 signal.

This checkpoint changes no model, universe, cost, holdout, broker permission,
production runtime, deployment or automation schedule.

## Follow-up — official cardinality result and taxonomy-backed repair

PR379 merged at 8a1a58e2bd09f1fc9e4e6394571dc7b84396c2fe after PR
Action38192847909 SUCCESS. Postmerge Action38192883463/job114629257183
actually returned at 2026-10-12T01:45:50Z: configured account matches=0,
dart_OperatingIncomeLoss candidate count=1, SOURCE_GAP_FAIL_CLOSED.
This proves a missing configured ID in the fixed pilot, not duplicate lines.

The bounded correction selects only dart_OperatingIncomeLoss and requires
an additional official xbrlTaxonomy.json IS1 response to verify its exact
ID, operating-profit Korean label, monetary type and connected-statement scope.
Official schema: https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2020001
The existing statement API documents quarter fields here:
https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2019020
No free-text/fuzzy fallback or first-duplicate choice is permitted; conflicting
legacy accounts, wrong currency/label, malformed numeric grouping, unlinked
receipts and missing prior-quarter amounts still fail closed.

The request budget increases from three to four official GETs for this same
fixed issuer/report. No bulk collection, new issuer/period, KRX/broker route or
performance run. Taxonomy failure stops before financial retrieval. Current
taxonomy agreement is not historical version or PIT validation. Explicit
historical-taxonomy and quarter-comparability/restatement flags stay false.
Eleven local synthetic tests pass. Remote exact-head safety and the actual
postmerge official source response must be inspected separately.
