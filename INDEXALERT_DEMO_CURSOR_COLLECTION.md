# Explicit bounded DEMO cursor collection

Collect only kt00007/ka10076 pages through the existing DEMO-only transport. Keep the same filters for each explicit continuation, reject repeated cursors and broker order identities, missing tables/IDs and invalid continuation headers. A capped Y page is blocked, never successful partial data or verified absence. The ten-page maximum is a workload bound from the reviewed official examples, not a source completeness pass rule. No automatic auth/refresh/retry.

Private in-memory snapshots deep-copy rows and expose only API/counts in safe reports. Cursor termination does not attest query scope completeness, account/day origin, freshness, fee settlement, genuine LIVE evidence or authority. No database/file mutation, actual request or deployment change was made for this collector.

Nine synthetic tests cover multi-page continuation, terminated empty pages, cap truncation, loops/duplicate orders, input/API limits, malformed tables/IDs/headers, provider failure sanitation and copy isolation. Full local218 offline tests passed. The current isolated Railway verifier remains exact pinned PR26 and first-page only; do not silently redeploy it to collect new scopes.
