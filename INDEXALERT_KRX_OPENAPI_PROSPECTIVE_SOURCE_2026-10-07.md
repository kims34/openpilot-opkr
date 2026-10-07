# KRX OpenAPI prospective source boundary — 2026-10-07

Status: NETWORK-FREE CURRENT-SESSION SOURCE NORMALIZATION — NOT SOURCE ADMISSION.

The currently available original KRX email does not establish unrestricted automated Data Marketplace web-session collection. That broader route remains blocked. This change therefore uses only the separately evidenced KRX OpenAPI service identities already proven by the project: `stk_bydd_trd` (KOSPI daily trade) and `stk_isu_base_info` (KOSPI security master). KRX's current official service pages list both services and state that stock daily-trade/basic-info data are available from 2010-01-04; this module itself performs no network request.

`research_v1_krx_openapi_prospective_source.py` consumes already-retrieved raw OpenAPI bytes, verifies the pinned connectivity-evidence contract and exact response fields, requires every daily row to match the requested session, joins the daily short issue code to the same-session official security master, and retains only rows whose official KRX identity is KOSPI common stock. It rejects incomplete mappings, duplicate identifiers, malformed rows and nonpositive common-stock OHLC instead of silently deleting names and changing cross-sectional ranks.

KRX `FLUC_RT` is normalized from percentage units into the decimal `krx_change_return` used by the frozen PIT feature engine. The receipt binds the raw daily/master SHA-256 values, normalized-panel SHA-256, exact connectivity-evidence fingerprint and retrieval timestamps.

Retrieval time is recorded only as **observed availability by retrieval time**, not as an official historical publication timestamp. The module explicitly keeps `current_session_finality_verified=false`, `complete_universe_verified=false` and `independent_source_admission_verified=false`. Therefore a structurally generated input/decision remains unadmitted Fresh Alpha evidence until independent current-session source/finality/chronology admission exists.

The prospective input snapshot now optionally binds an exact source-receipt SHA-256. A hash binds identity, not truth: this does not make source admission true.

No KRX request, credential access, Data Marketplace automation, historical replay, holdout access, broker action, funds movement or permission change occurs in this change. MASTER_OFF and live-order authority remain unchanged.
