undefined
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
