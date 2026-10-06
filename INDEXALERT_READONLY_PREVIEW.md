# Isolated Android readiness preview

This separate application uses com.indexalert.preview4.8-preview/code48 and the label IndexAlert 검증. It does not update com.indexalert.app or migrate its data. Its only network operation is the existing4.8 GET /automation/readiness contract. It contains no Firebase, registration/receipt/self-test sender, notifications, workers, broker requests, trading controls or data-sharing permissions. It cannot validate production notification E2E or original-package4.8 signing continuity.

The readiness implementation and four contract tests are exact copies of the canonical app files. CI checks byte equality before compilation, runs actual preview JUnit tests, builds a real debug APK and verifies package/version/signature, merged manifest permissions/components and absence of Firebase/WorkManager dependencies. Any source drift fails CI. Canonical app build stays explicitly scoped to :app tasks.

Debug signing is for isolated verification only. No stable release signing identity or future preview update continuity is claimed. Owner installed4.7 APK/hash/signer evidence and standard local debug-key absence are recorded in the development branch. Keep the existing app and private data. No APK installation, uninstall or data migration is performed by CI.

## Actual isolated preview build proof — 2026-10-06

PR53 merged to index-alert-build as 52377357c0c5260673fc823be3e8a0451abbea72. Workflow run 37402266619 completed successfully for source head 06e23a33def235fa7505d30fe1443267e13eb847.

Verified artifact:
- applicationId: com.indexalert.preview
- versionName/versionCode: 4.8-preview / 48
- APK SHA-256: c46bf10dc036bfaff5ab0b7d00938a66081cedac4ef2c20ce72d7bfa5e38564f
- size: 820613 bytes
- signer certificate SHA-256: 52083f68874f93989f232571fd811bb5b2e45f685a3980c33dcca02b89605bf4
- signature_verified: true
- unit tests: 4 passed, 0 failures/errors/skips
- readiness source byte-identical to canonical app: true
- permissions: android.permission.INTERNET only
- Firebase dependency: absent
- WorkManager dependency: absent
- production app updated: false
- broker request/order/live authority: false

The downloaded workflow artifact was independently hashed after extraction and matched the recorded APK SHA-256 exactly.

Owner may install this APK alongside4.7 and observe the readiness UI. Such an observation is only preview-device readiness UI evidence, never production4.8 push proof, source/PIT admission, empirical promotion or authorization for real orders. Original frozen gates and consumed failed holdout remain unchanged.
