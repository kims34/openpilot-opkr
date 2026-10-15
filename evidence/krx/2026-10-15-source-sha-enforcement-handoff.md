# KRX private source SHA requirement — 2026-10-15

## Tested implementation
Updated the read-only source-day comparator so a real mounted-volume comparison must have a valid pinned 64-character SHA-256 original snapshot digest. Missing, malformed or ambiguous pins cause a fail-closed result before any production source file is read. A missing reference day set or invalid expected empty count also fails. Existing tests for incorrect worker identity keep their original refusal behavior.

[GitHub Actions #38678519906](https://github.com/kims34/openpilot-opkr/actions/runs/38678519906): 142/142 tests passed. The branch change was isolated and not deployed to Railway. Synthetic tests do not authenticate KRX source data.

## Outstanding
The original 184 ambiguous KRX dates have not been checked against a complete, independently authenticated historical official trading calendar. The 27 quarantined securities remain excluded. Source PIT admission, M20 profitability, holdout and live trading remain blocked. No orders or external KRX API calls were made. `ORDERING=false` unchanged.
