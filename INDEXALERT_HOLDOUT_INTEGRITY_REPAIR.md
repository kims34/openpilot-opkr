# Holdout integrity repair — synthetic evidence only

Verified source base: 4811ed3115af4674aea024f54cf49d05f7379430.
The current sealed-holdout-v1 window is consumed and its existing failed result is immutable.
This change grants no evaluation, promotion or live-order authority.

## Reproduction and corrections
A synthetic 100-session history was run through the actual v2 engineer() function.
Holding pre-cutoff features constant and changing only future-session returns changed
pre-cutoff ret1/ret5 labels under the original evaluator split. This reproduces
boundary leakage without accessing private market data or reading actual outcomes.

holdout_training_boundary.training_rows enforces the existing horizon, training length,
purge, contiguous calendar and exact decision-date/index binding. For all four original
horizons, future-return changes leave eligible training features and labels identical.
This helper is tested infrastructure, not an admitted successor evaluator.

The consumed v1 evaluator is retired at main() entry before any private reads or model
execution. The standalone sealed_holdout gate rejects an existing result even if a
manifest still asserts unopened state. No old evaluator/result is repaired and rerun.

## Validation
Nine synthetic unit tests pass locally (Python 3.12.14; pandas 2.2.3, NumPy 2.3.5,
scikit-learn 1.8.0). The dedicated GitHub workflow validates on Python 3.12 and the
production pandas 2.3.3 / scikit-learn 1.7.2 versions. Local success is not a claim
of remote CI success; check the workflow for the exact repair commit.

## Unchanged
Frozen Core/model/threshold/cost/Top3 criteria, rejected-candidate dispositions,
cutoff and pass-rule historical record, baseline fingerprints, private data/volumes,
consumed result, server revision and brokerage authority are unchanged.
Railway remains pinned to the existing implementation with the already verified
read-only result audit and restart NEVER. Repair-branch tests are not performance
or real-account evidence.

## Still required
Independent freeze/acquisition/access lineage reconciliation; all source/PIT,
status-economics and broker execution admissions; a genuinely separate prospective
protocol before any new untouched window. Reuse of the consumed namespace is forbidden.
