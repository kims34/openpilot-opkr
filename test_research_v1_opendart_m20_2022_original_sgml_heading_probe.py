"""Offline regression: original 2022 Q3 SGML context never creates PIT facts."""
import os
import unittest
from unittest.mock import patch

import research_v1_opendart_m20_2022_original_sgml_heading_probe as p


def table(label="영업이익", amount="12", preceding="", extra=""):
    return (preceding + "<table><tr><td>"+label+"</td><td>"+amount+
            "</td><td>11</td><td>10</td><td>9</td></tr>"+extra+"</table>")


class OriginalSGMLNeighborhoodTest(unittest.TestCase):
    def scan(self, text):
        x=p.Neighborhood()
        x.feed(text)
        x.close()
        return x

    def test_15_candidate_tables_strict_shape_not_facts(self):
        original = "".join(table(preceding="<p>2022년 3분기 연결손익계산서</p>") for _ in range(15))
        output = self.scan(original).finish()
        self.assertEqual(output["exact_label_operating_table_candidates"], 15)
        self.assertEqual(output["original_sgml_tables_examined"], 15)
        self.assertEqual(output["numeric_peers_at_least_four"], 15)
        self.assertEqual(output["prefix_12000_exact_cfs_title"], 15)
        self.assertFalse(output["heading_proximity_is_authoritative_statement_identity"])
        self.assertFalse(output["period_text_proximity_is_accounting_fact"])

    def test_extended_period_text_without_exact_cfs_not_bound(self):
        original = "".join(table(
            extra="<tr><td>2022.07.01~2022.09.30</td></tr>"
                  "<tr><td>2021.07.01~2021.09.30</td></tr>"
        ) for _ in range(15))
        out = self.scan(original).finish()
        self.assertEqual(out["table_contains_both_q3_full_windows"], 15)
        self.assertEqual(out["table_contains_exact_cfs_title"], 0)
        self.assertEqual(out["table_contains_cfs_and_3month_and_both_periods"], 0)

    def test_exact_CFS_terms_and_three_month_still_not_financial_values(self):
        original = "".join(table(
            label="영업손실", preceding="<p>연결포괄손익계산서</p>",
            extra="<tr><td>3개월</td><td>2022.07.01~2022.09.30</td>"
                  "<td>2021.07.01~2021.09.30</td></tr>"
                  "<tr><td>연결손익계산서</td></tr>"
        ) for _ in range(15))
        out = self.scan(original).finish()
        self.assertEqual(out["table_contains_cfs_and_3month_and_both_periods"],15)
        self.assertTrue(out["actual_q3_cfs_quarter_values_unverified"])
        self.assertNotIn("12",str(out))

    def test_only_14_operating_tables_fails_closed(self):
        with self.assertRaisesRegex(p.SGMLGap,"OPERATING_TABLE_CARDINALITY_CHANGED"):
            self.scan(table()*14).finish()

    def test_missing_end_table_fails_closed(self):
        scan=self.scan("<table><tr><td>영업이익</td><td>12</td></tr>")
        with self.assertRaisesRegex(p.SGMLGap,"TABLE_NESTING_INVALID"):
            scan.finish()

    def test_unsupported_or_oversized_input_is_guarded(self):
        with patch.object(p, "MAX_CELL", 2):
            with self.assertRaisesRegex(p.SGMLGap,"CELL_TEXT_BUDGET"):
                self.scan(table(amount="123456"))
        with patch.object(p, "MAX_NODES",1):
            with self.assertRaisesRegex(p.SGMLGap,"HTML_NODE_BUDGET"):
                self.scan(table())

    def test_sha_pinning_precedes_official_zip_parse(self):
        with patch.object(p,"inspect_official_original_document") as official:
            with self.assertRaisesRegex(p.SGMLGap,"FIRST_ORIGINAL_ZIP_SHA_DRIFT"):
                p.inspect(b"tampered")
        official.assert_not_called()

    def test_empty_key_makes_no_official_requests(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":""}), patch.object(
            p,"_official_get") as official:
            out=p.run(object())
        official.assert_not_called()
        self.assertEqual(out["source_status"],"AUTH_NOT_CONFIGURED")
        self.assertFalse(out["m20_performance_run_authorized"])

    def test_secret_provider_error_redacted_and_trading_disabled(self):
        with patch.dict(os.environ,{"OPENDART_API_KEY":"TOPSECRET"}), patch.object(
            p,"_official_get",side_effect=RuntimeError("TOPSECRET 12,345 20221114000001")):
            out=p.run(object())
        self.assertEqual(out["source_status"],"SOURCE_GAP_FAIL_CLOSED")
        self.assertNotIn("TOPSECRET",str(out))
        self.assertNotIn("12,345",str(out))
        self.assertFalse(out["m20_feature_pit_admitted"])
        self.assertFalse(out["real_orders_authorized"])
        self.assertEqual(out["ordering"],"DISABLED")


if __name__=="__main__":
    unittest.main()
