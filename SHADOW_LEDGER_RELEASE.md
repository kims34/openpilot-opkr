# IndexAlert prospective shadow ledger

This release keeps model `3.1-causal-adaptive-close` as the served probability model.

It adds a prospective-only shadow ledger for frozen calibration challengers. Shadow forecasts are recorded before the target market open, stored separately from production forecasts, and scored only after the target close is available. They never replace or alter the probability returned to the app.

The ledger uses `INDEXALERT_DB`; production is configured to persist it on the Railway `/data` volume.
