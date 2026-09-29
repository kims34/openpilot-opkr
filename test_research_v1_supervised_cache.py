import tempfile
import unittest
from pathlib import Path

import pandas as pd

from research_v1_supervised_cache import (
    CACHE_VERSION,
    REQUIRED_FEATURE_RETURN_POLICY,
    StaleSupervisedCache,
    _source_fingerprint,
    _validate_meta,
)


class SupervisedCacheFingerprintTest(unittest.TestCase):
    def _raw(self):
        return pd.DataFrame(
            {
                "decision_date": pd.to_datetime(["2026-01-02", "2026-01-02", "2026-01-05"]),
                "symbol": ["000001", "000002", "000001"],
                "open": [100.0, 200.0, 101.0],
                "high": [102.0, 202.0, 103.0],
                "low": [99.0, 198.0, 100.0],
                "close": [101.0, 201.0, 102.0],
                "volume": [1000, 2000, 1100],
                "ChangesRatio": [1.0, 0.5, 0.99],
            }
        )

    def test_fingerprint_is_order_insensitive(self):
        raw = self._raw()
        shuffled = raw.sample(frac=1.0, random_state=7).reset_index(drop=True)
        self.assertEqual(_source_fingerprint(raw), _source_fingerprint(shuffled))

    def test_fingerprint_changes_when_market_content_changes(self):
        raw = self._raw()
        changed = raw.copy()
        changed.loc[0, "close"] = 999.0
        self.assertNotEqual(_source_fingerprint(raw), _source_fingerprint(changed))

    def test_validate_meta_rejects_different_source(self):
        raw = self._raw()
        fp = _source_fingerprint(raw)
        meta = {
            "version": CACHE_VERSION,
            "feature_return_policy": REQUIRED_FEATURE_RETURN_POLICY,
            "source_fingerprint": fp,
        }
        _validate_meta(meta, Path("dummy"), fp)
        changed = raw.copy()
        changed.loc[0, "symbol"] = "999999"
        with self.assertRaises(StaleSupervisedCache):
            _validate_meta(meta, Path("dummy"), _source_fingerprint(changed))


if __name__ == "__main__":
    unittest.main()
