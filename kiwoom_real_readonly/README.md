# Kiwoom REAL read-only isolated Railway context

This directory exists only to isolate the REAL read-only smoke from the repository root Railway configuration used by the KRX historical worker.

- no order/create/amend/cancel endpoint;
- no funds movement;
- no permission changes;
- source file must remain byte-identical to ../kiwoom_real_type00_readonly_smoke.py;
- Railway service rootDirectory should be /kiwoom_real_readonly and Dockerfile should be Dockerfile.
