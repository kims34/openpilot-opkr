# IndexAlert KRX Coverage/PIT Audit Contract v1

Updated: 2026-10-02 KST  
Contract: `INDEXALERT-KRX-COVERAGE-PIT-AUDIT-v1`  
Phase: `COVERAGE_PIT_AUDIT`  
Status: **NETWORK-FREE REVIEW COMPOSER — CANNOT SET A-F PASS**

This phase consumes only already-acquired private evidence and independently
attested expected scopes. It makes no KRX request.

## Required predecessors

The audit cannot initialize until all of these are complete and verified:

- IDENTITY_SEED
- IDENTITY_STANDARD_CODE_BINDING
- PER_SECURITY_HISTORY
- STATUS_ECONOMICS phase
- independent expected-scope attestation
- private raw-object verification
- request-receipt verification
- row-within-preregistered-request-window verification

## Gate C review candidate — security/status

A candidate may be emitted only when:
- exact historical identity coverage matches the independent expected scope;
- official halt/cleanup/delisting/delisted-price evidence is structurally
  consistent;
- all preregistered status-history requests completed;
- the expected-scope contract fingerprint matches exactly.

This still does not make Gate C PASS automatically.

## Gate D review candidate — security/status

Retrospective download time must never be rewritten as historical availability.

Status Gate D therefore remains blocked unless a separate audit supplies explicit
official historical availability lineage. Event dates or retrieval timestamps
alone are insufficient.

## Gate C review candidate — investor flow

The validated investor-flow key set must exactly equal the independently
attested expected `(event_date, symbol, isu_cd)` set. The system may not insert
missing rows or create zero-flow observations.

## Gate D review candidate — investor flow

Every row must carry validated:
`event_time <= published_at <= available_at <= ingested_at`

and the frozen official publication-floor rule must hold.

## Authority boundary

This composer may return **review candidates only**.

It may never:
- write A-F PASS;
- close the source contract;
- authorize a feature-performance experiment;
- authorize sealed holdout;
- authorize live trading.

Separate source-gate review and later source-data admission remain mandatory.
