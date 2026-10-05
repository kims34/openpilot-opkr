# Isolated DEMO deployment config precedence

Actual first isolated deployment18870bde-7a8a-4bb9-8e69-a07f8dfd00e9 built Dockerfile.krx-historical-worker because root railway.json selects it. The live service UI config alone was insufficient evidence of the image actually built. Root railway.json is intentionally preserved for its existing worker.

Use service-specific railwayConfigFile=railway-kiwoom-demo-readonly.json with exact pinned source. This file explicitly selects the lean DEMO Dockerfile, python -S -B verifier and NEVER restart. No volume or provider permission change. Verify actual build log COPY of the three Kiwoom modules and actual safe runtime JSON before claiming DEMO verification. Existing public/PIT/KRX services are not repinned or reconfigured.

The wrong build has no verifier module and its configured -S startup cannot execute it; inspect actual exit/logs rather than inferring network activity or success. Do not count that deployment as provider evidence. The corrective redeployment fixes observed config precedence, not an attempt to bypass a queue or failed strategy gate.
