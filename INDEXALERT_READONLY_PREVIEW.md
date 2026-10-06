# Isolated Android readiness preview

This separate application uses com.indexalert.preview4.8-preview/code48 and the label IndexAlert 검증. It does not update com.indexalert.app or migrate its data. Its only network operation is the existing4.8 GET /automation/readiness contract. It contains no Firebase, registration/receipt/self-test sender, notifications, workers, broker requests, trading controls or data-sharing permissions. It cannot validate production notification E2E or original-package4.8 signing continuity.

The readiness implementation and four contract tests are exact copies of the canonical app files. CI checks byte equality before compilation, runs actual preview JUnit tests, builds a real debug APK and verifies package/version/signature, merged manifest permissions/components and absence of Firebase/WorkManager dependencies. Any source drift fails CI. Canonical app build stays explicitly scoped to :app tasks.

Debug signing is for isolated verification only. No stable release signing identity or future preview update continuity is claimed. Owner installed4.7 APK/hash/signer evidence and standard local debug-key absence are recorded in the development branch. Keep the existing app and private data. No APK installation, uninstall or data migration is performed by CI.

After actual CI succeeds, retrieve the exact preview APK and verification artifact from the recorded run. Owner may install alongside4.7 and observe the unavailable status. Such an observation is only preview-device readiness UI evidence, never production4.8 push proof, source/PIT admission, empirical promotion or authorization for real orders. Original frozen gates and consumed failed holdout remain unchanged.
