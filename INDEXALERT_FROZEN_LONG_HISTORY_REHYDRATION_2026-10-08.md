# Frozen long-history source rehydration — 2026-10-08

Status: SOURCE RECONSTRUCTION CONTRACT ONLY — NO MODEL FIT, NO PERFORMANCE RERUN, NO HOLDOUT ACCESS, NO ALPHA/LIVE AUTHORITY.

PR #327 established that the existing Railway PIT volume begins in 2018 and therefore cannot be used directly for the frozen H5 anchored calendar, whose origin is 2015-06-15. The adopted policy-aligned calibration Action 36643183157 still has an unexpired result artifact (artifact 11067383547, digest `sha256:c8dd6a016103cf33d9219622f416fda25715c1cac19b371714d9308f2cb2c26f`). Its summary retains the exact source fingerprint used by the frozen supervised cache.

The recovered source identity is:

- date range actually observed by the run: 2015-06-15 through 2026-09-23;
- rows: 2,512,128;
- symbols: 1,089;
- columns: `decision_date, symbol, open, high, low, close, volume, value, krx_change_return`;
- pandas-hash XOR: `17836462952802001740`;
- pandas-hash uint64 sum: `17879387804724068608`.

The frozen Action ran Python 3.12.14, pandas 2.3.3, numpy 2.5.3 and pyarrow 21.0.0. The exact `research_v1_marcap.py` Git blob at the Action head `4df26b6f5d2d9e645cd2c0242c9ac8cefb747a9d` is `5b39887733473a6b4aff5a0fc097c0acc5f5d711`; the current PIT rebuild copy has the same blob identity.

`pit_rebuild/rehydrate_frozen_long_history.py` rebuilds the public marcap/derived-KRX panel into a separate attempt directory. It cannot replace the existing `/pit/marcap_kospi_pit` tree. It computes the same source-fingerprint semantics as `research_v1_supervised_cache._source_fingerprint` and publishes `/pit/marcap_kospi_pit_long_verified_36643183157` only if every recovered fingerprint field matches exactly. Any mismatch remains an unpromoted forensic attempt and fails closed.

The verified record explicitly keeps consumed-holdout access, performance evaluation, model fitting, retrospective decision backfill, Fresh Alpha admission, promotion and live-order authority false. This step recovers source identity only. A separate later step must build/verify the frozen supervised frame and model bundle before a prospective decision may be structurally committed.

No mismatch may be "fixed" by changing the frozen fingerprint, calendar, date range, H5 parameters or policy.
