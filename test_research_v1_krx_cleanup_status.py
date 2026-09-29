import unittest

import pandas as pd

from research_v1_krx_cleanup_status import (
    KRXCleanupStatusError,
    cleanup_mask_for_dates,
    normalise_cleanup_trading,
    planned_delisting_mask_for_dates,
)


class TestKRXCleanupStatus(unittest.TestCase):
    def _raw(self):
        return pd.DataFrame({
            "종목코드": ["300"],
            "종목명": ["테스트보통주"],
            "시장구분": ["KOSPI"],
            "증권구분": ["주권"],
            "정리매매 시작일": ["2026/09/10"],
            "정리매매 종료일": ["2026/09/16"],
            "상장폐지 예정일": ["2026/09/17"],
            "상장폐지사유": ["테스트 사유"],
        })

    def test_normalise_and_lineage(self):
        out = normalise_cleanup_trading(
            self._raw(), available_at="2026-09-09 20:00:00+09:00"
        )
        self.assertEqual(out.loc[0, "symbol"], "000300")
        self.assertEqual(str(out.loc[0, "cleanup_start"].date()), "2026-09-10")
        self.assertEqual(str(out.loc[0, "cleanup_end"].date()), "2026-09-16")
        self.assertEqual(str(out.loc[0, "planned_delisting_date"].date()), "2026-09-17")
        self.assertIn("MDCSTAT237", out.loc[0, "source"])
        self.assertTrue(pd.notna(out.loc[0, "available_at"]))

    def test_cleanup_interval_is_inclusive(self):
        cleanup = normalise_cleanup_trading(
            self._raw(), available_at="2026-09-09 20:00:00+09:00"
        )
        rows = pd.DataFrame({
            "decision_date": pd.to_datetime([
                "2026-09-09", "2026-09-10", "2026-09-16", "2026-09-17"
            ]),
            "symbol": ["000300"] * 4,
        })
        self.assertEqual(
            cleanup_mask_for_dates(rows, cleanup).tolist(),
            [False, True, True, False],
        )
        self.assertEqual(
            planned_delisting_mask_for_dates(rows, cleanup).tolist(),
            [False, False, False, True],
        )

    def test_missing_lineage_fails_closed(self):
        with self.assertRaises(KRXCleanupStatusError):
            normalise_cleanup_trading(self._raw(), available_at=None)

    def test_bad_source_fails_closed(self):
        with self.assertRaises(KRXCleanupStatusError):
            normalise_cleanup_trading(
                self._raw(),
                available_at="2026-09-09 20:00:00+09:00",
                source="UNOFFICIAL_PROXY",
            )

    def test_invalid_interval_fails_closed(self):
        raw = self._raw()
        raw.loc[0, "정리매매 종료일"] = "2026/09/09"
        with self.assertRaises(KRXCleanupStatusError):
            normalise_cleanup_trading(
                raw, available_at="2026-09-09 20:00:00+09:00"
            )

    def test_planned_delisting_must_follow_cleanup_end(self):
        raw = self._raw()
        raw.loc[0, "상장폐지 예정일"] = "2026/09/16"
        with self.assertRaises(KRXCleanupStatusError):
            normalise_cleanup_trading(
                raw, available_at="2026-09-09 20:00:00+09:00"
            )


if __name__ == "__main__":
    unittest.main()
