"""Synthetic KRX OpenAPI prospective-source tests; no network access."""
import copy
import json
import unittest
from pathlib import Path

import pandas as pd

from research_v1_krx_openapi_prospective_source import (
    AVAILABILITY_SEMANTICS,
    KRXProspectiveOpenAPISourceError,
    build_current_session_openapi_source,
    validate_source_receipt,
)
from research_v1_prospective_inputs import (
    build_current_session_inputs,
    input_snapshot_sha256,
)


ROOT = Path(__file__).parent
EVIDENCE = json.loads(
    (ROOT / "INDEXALERT_KRX_OPENAPI_CONNECTIVITY_EVIDENCE.json").read_text(
        encoding="utf-8"
    )
)


def _raw(rows):
    return json.dumps({"OutBlock_1": rows}, ensure_ascii=False).encode("utf-8")


def _master_rows():
    return [
        {
            "ISU_CD": "KR7005930003", "ISU_SRT_CD": "005930",
            "ISU_NM": "삼성전자", "ISU_ABBRV": "삼성전자",
            "ISU_ENG_NM": "SAMSUNG", "LIST_DD": "19750611",
            "MKT_TP_NM": "KOSPI", "SECUGRP_NM": "주권",
            "SECT_TP_NM": "", "KIND_STKCERT_TP_NM": "보통주",
            "PARVAL": "100", "LIST_SHRS": "1000",
        },
        {
            "ISU_CD": "KR7005931001", "ISU_SRT_CD": "005935",
            "ISU_NM": "삼성전자우", "ISU_ABBRV": "삼성전자우",
            "ISU_ENG_NM": "SAMSUNG PREF", "LIST_DD": "19890313",
            "MKT_TP_NM": "유가증권", "SECUGRP_NM": "주권",
            "SECT_TP_NM": "", "KIND_STKCERT_TP_NM": "우선주",
            "PARVAL": "100", "LIST_SHRS": "100",
        },
    ]


def _daily_rows():
    base = {
        "BAS_DD": "20261007", "MKT_NM": "KOSPI", "SECT_TP_NM": "",
        "CMPPREVDD_PRC": "100", "MKTCAP": "1000000", "LIST_SHRS": "1000",
    }
    return [
        {
            **base, "ISU_CD": "005930", "ISU_NM": "삼성전자",
            "TDD_CLSPRC": "70,000", "FLUC_RT": "1.25",
            "TDD_OPNPRC": "69,500", "TDD_HGPRC": "70,500",
            "TDD_LWPRC": "69,000", "ACC_TRDVOL": "1,000",
            "ACC_TRDVAL": "70,000,000",
        },
        {
            **base, "ISU_CD": "005935", "ISU_NM": "삼성전자우",
            "TDD_CLSPRC": "60,000", "FLUC_RT": "-0.50",
            "TDD_OPNPRC": "60,100", "TDD_HGPRC": "60,200",
            "TDD_LWPRC": "59,900", "ACC_TRDVOL": "100",
            "ACC_TRDVAL": "6,000,000",
        },
    ]


def build(daily=None, master=None):
    return build_current_session_openapi_source(
        daily_raw=_raw(_daily_rows() if daily is None else daily),
        master_raw=_raw(_master_rows() if master is None else master),
        expected_session="2026-10-07",
        daily_retrieved_at="2026-10-07T18:10:05+09:00",
        master_retrieved_at="2026-10-07T18:10:06+09:00",
        connectivity_evidence=EVIDENCE,
    )


class KRXOpenAPIProspectiveSourceTest(unittest.TestCase):
    def test_exact_openapi_rows_normalize_to_common_stock_panel_without_admission(self):
        out = build()
        self.assertTrue(validate_source_receipt(out)["valid"])
        panel = out["panel"]
        self.assertEqual(panel["symbol"].tolist(), ["005930"])
        self.assertEqual(panel["standard_code"].tolist(), ["KR7005930003"])
        self.assertEqual(float(panel.iloc[0]["krx_change_return"]), 0.0125)
        self.assertEqual(float(panel.iloc[0]["open"]), 69500.0)
        self.assertEqual(
            out["availability_semantics"], AVAILABILITY_SEMANTICS
        )
        self.assertFalse(out["current_session_finality_verified"])
        self.assertFalse(out["complete_universe_verified"])
        self.assertFalse(out["independent_source_admission_verified"])
        self.assertFalse(out["fresh_alpha_observation_admitted"])
        self.assertFalse(out["live_order_authorized"])

    def test_source_receipt_can_be_bound_into_label_free_input_snapshot(self):
        out = build()
        # Add enough prior days solely to exercise the warmup path. The exact
        # current-session row remains sourced from the official OpenAPI adapter.
        row = out["panel"].iloc[0]
        dates = pd.bdate_range("2026-09-01", periods=27)
        history = []
        for i, day in enumerate(dates[:-1]):
            history.append({
                "decision_date": day, "symbol": row.symbol,
                "open": 60000+i*10, "high": 60100+i*10,
                "low": 59900+i*10, "close": 60050+i*10,
                "volume": 1000+i, "value": 60000000+i*1000,
                "krx_change_return": 0.001,
                "available_at": day.strftime("%Y-%m-%d")+"T18:10:00+09:00",
            })
        current = out["panel"][[
            "decision_date","symbol","open","high","low","close","volume",
            "value","krx_change_return","available_at"
        ]].copy()
        raw = pd.concat([pd.DataFrame(history), current], ignore_index=True)
        snapshot = build_current_session_inputs(
            raw,
            decision_at="2026-10-07T18:15:00+09:00",
            source_receipt_sha256=out["source_receipt_sha256"],
        )
        self.assertTrue(snapshot["source_receipt_bound"])
        self.assertEqual(
            snapshot["source_receipt_sha256"], out["source_receipt_sha256"]
        )
        self.assertFalse(snapshot["independent_source_admission_verified"])
        digest = input_snapshot_sha256(snapshot)
        changed = dict(snapshot)
        changed["source_receipt_sha256"] = "0"*64
        self.assertNotEqual(input_snapshot_sha256(changed), digest)

    def test_session_schema_mapping_and_raw_tamper_fail_closed(self):
        wrong_day = _daily_rows()
        wrong_day[0] = dict(wrong_day[0], BAS_DD="20261006")
        with self.assertRaisesRegex(KRXProspectiveOpenAPISourceError, "session"):
            build(daily=wrong_day)
        missing = _daily_rows()
        missing[0] = dict(missing[0])
        del missing[0]["FLUC_RT"]
        with self.assertRaisesRegex(KRXProspectiveOpenAPISourceError, "FLUC_RT"):
            build(daily=missing)
        out = build()
        changed = copy.copy(out)
        changed["daily_raw_sha256"] = "0"*64
        with self.assertRaisesRegex(KRXProspectiveOpenAPISourceError, "fingerprint"):
            validate_source_receipt(changed)

    def test_missing_master_mapping_or_zero_ohlc_is_not_silently_dropped(self):
        with self.assertRaisesRegex(KRXProspectiveOpenAPISourceError, "missing from"):
            build(master=_master_rows()[:1], daily=_daily_rows()+[{
                **_daily_rows()[0], "ISU_CD":"123456", "ISU_NM":"미매핑"
            }])
        bad = _daily_rows()
        bad[0] = dict(bad[0], TDD_OPNPRC="0")
        with self.assertRaisesRegex(KRXProspectiveOpenAPISourceError, "nonpositive"):
            build(daily=bad)


    def test_nonpositive_ohlc_rejection_attaches_safe_activity_counts(self):
        for all_zero, expected_no_activity in ((False, 0), (True, 1)):
            rows = _daily_rows()
            bad_prices = {
                "TDD_OPNPRC": "0", "TDD_HGPRC": "0",
                "TDD_LWPRC": "0", "TDD_CLSPRC": "0",
                "ACC_TRDVOL": "0", "ACC_TRDVAL": "0",
            } if all_zero else {"TDD_OPNPRC": "0"}
            rows[0] = dict(rows[0], **bad_prices)
            rows[0]["ISU_NM"] = "DO_NOT_LEAK"
            with self.assertRaisesRegex(
                KRXProspectiveOpenAPISourceError, "nonpositive"
            ) as caught:
                build(daily=rows)
            counts = caught.exception.safe_ohlc_counts
            self.assertEqual(counts["common_stock_rows"], 1)
            self.assertEqual(counts["nonpositive_ohlc_rows"], 1)
            self.assertEqual(counts["zero_volume_value_rows"], expected_no_activity)
            self.assertEqual(counts["other_activity_rows"], 1 - expected_no_activity)
            self.assertEqual(counts["all_zero_ohlc_rows"], int(all_zero))
            self.assertNotIn("DO_NOT_LEAK", str(counts))


    def test_reproduced_zero_activity_27_of_28_does_not_become_safe_universe(self):
        # Synthetic reproduction of the shape of the real 2026-09-28
        # anomaly, not of any KRX security row or private market payload.
        # 27 zero-volume/value common stocks have zero intraday OHLC and a
        # positive close; none has all four prices zero. Their identifiers
        # and prices below are fabricated; frozen ranks must not backfill.
        daily = [_daily_rows()[0]]
        master = [_master_rows()[0]]
        for i in range(27):
            code = f"{800000 + i:06d}"
            daily.append({
                **_daily_rows()[0],
                "ISU_CD": code,
                "ISU_NM": "synthetic",
                "TDD_OPNPRC": "0",
                "TDD_HGPRC": "0",
                "TDD_LWPRC": "0",
                "TDD_CLSPRC": "1000",
                "ACC_TRDVOL": "0",
                "ACC_TRDVAL": "0",
            })
            master.append({
                **_master_rows()[0],
                "ISU_CD": f"KR7{code}000",
                "ISU_SRT_CD": code,
                "ISU_NM": "synthetic",
            })
        with self.assertRaisesRegex(
            KRXProspectiveOpenAPISourceError, "nonpositive"
        ) as caught:
            build(daily=daily, master=master)
        observed = caught.exception.safe_ohlc_counts
        self.assertEqual(observed["common_stock_rows"], 28)
        self.assertEqual(observed["nonpositive_ohlc_rows"], 27)
        self.assertEqual(observed["zero_volume_value_rows"], 27)
        self.assertEqual(observed["other_activity_rows"], 0)
        self.assertEqual(observed["all_zero_ohlc_rows"], 0)
        self.assertNotIn("synthetic", str(caught.exception))
        # Source validation cannot silently treat no-trade rows as officially
        # halted, drop 27 names, or record an admitted decision panel.

    def test_retrieval_time_is_observed_availability_not_backdated_publication(self):
        out = build()
        self.assertEqual(
            out["observed_available_by"], "2026-10-07T09:10:06+00:00"
        )
        self.assertEqual(
            out["panel"]["available_at"].unique().tolist(),
            ["2026-10-07T09:10:06+00:00"],
        )
        self.assertFalse(out["current_session_finality_verified"])


if __name__ == "__main__":
    unittest.main()
