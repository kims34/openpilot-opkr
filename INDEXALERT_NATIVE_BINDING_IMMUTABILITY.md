# Append-only local execution identities

Native account/day scope, order-side bindings, native fill bindings and journal executions now reject UPDATE and DELETE. Every journal connection enables SQLite recursive_triggers so INSERT OR REPLACE invokes DELETE guards rather than silently replacing committed rows. Existing append-only inbox receipts/conflicts/attempts gain the same REPLACE safeguard.

Idempotent INSERT OR IGNORE and exact duplicate replay remain supported. Mutable intent state, snapshot bindings and conservative capital accounting retain their existing operations. Existing rows are not rewritten or re-admitted. This protects ordinary application SQL mistakes, not a hostile database administrator who can remove triggers or change connection pragmas; there is no new external provenance attestation.

Three synthetic regression cases cover native scope/order/fill/execution replacement, reconnect pragmas and all inbox tables. Full local209 tests passed. No frozen artifacts, source admissions, account credentials, orders or funds changed.
