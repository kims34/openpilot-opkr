"""Actual Chromium rendering checks using a temporary synthetic journal only."""
from pathlib import Path
import tempfile
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright, expect
from order_intent_journal import OrderIntentJournal
from shadow_operational_dashboard import create_dashboard_server
import test_native_settlement_review_cli as native_fixtures


class DashboardBrowserTests(unittest.TestCase):
    def test_native_file_balance_match_and_local_blockers_remain_distinct(self):
        fixture = native_fixtures.NativeReviewCLITests()
        fixture.setUp()
        server = create_dashboard_server(fixture.path, 0, settlement_input_path=fixture.input)
        worker = Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            before = fixture.journal.shadow_control(), fixture.journal.db.total_changes
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch()
                try:
                    page = browser.new_page()
                    page.goto(f"http://127.0.0.1:{server.server_port}")
                    expect(page.locator("#refresh")).to_be_enabled()

                    def value(label):
                        return page.locator("#settlement dt").filter(has_text=label).locator("+ dd").inner_text()

                    self.assertEqual(value("예수금 증감 대조"), "일치")
                    self.assertEqual(value("결제 필드 검증"), "미충족")
                    self.assertEqual(value("독립 계좌·결제 승인"), "미확인")
                    self.assertEqual(before, (fixture.journal.shadow_control(), fixture.journal.db.total_changes))
                    for private in ('a'*64, 'synthetic-review', str(fixture.input), str(fixture.path)):
                        self.assertNotIn(private, page.locator("body").inner_text())

                    fixture.payload['closing']['body']['entr'] = '9000'
                    fixture.write()
                    page.locator("#refresh").click()
                    expect(page.locator("#refresh")).to_be_enabled()
                    self.assertEqual(value("예수금 증감 대조"), "불일치")
                    self.assertEqual(value("결제 필드 검증"), "미충족")
                    self.assertEqual(before, (fixture.journal.shadow_control(), fixture.journal.db.total_changes))

                    fixture.journal.trip_kill_switch()
                    after_kill = fixture.journal.shadow_control(), fixture.journal.db.total_changes
                    page.locator("#refresh").click()
                    expect(page.locator("#refresh")).to_be_enabled()
                    self.assertIn("Kill Switch가 잠겨 있습니다", page.locator("#settlement").inner_text())
                    self.assertEqual(after_kill, (fixture.journal.shadow_control(), fixture.journal.db.total_changes))
                    self.assertIn("꺼짐", page.locator("#state").inner_text())
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
            worker.join()
            fixture.tearDown()

    def test_render_failure_clear_and_recovery_are_read_only(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "fixture.sqlite"
            journal = OrderIntentJournal(path)
            server = create_dashboard_server(path, 0)
            worker = Thread(target=server.serve_forever, daemon=True)
            worker.start()
            before = journal.shadow_control(), journal.db.total_changes
            try:
                with sync_playwright() as playwright:
                    browser = playwright.chromium.launch()
                    try:
                        page = browser.new_page()
                        page.goto(f"http://127.0.0.1:{server.server_port}")
                        expect(page.locator("#refresh")).to_be_enabled()
                        self.assertIn("조회 완료", page.locator("#state").inner_text())
                        self.assertIn("꺼짐", page.locator("#state").inner_text())
                        self.assertIn("연결되지 않았습니다", page.locator("#settlement").inner_text())
                        self.assertEqual(page.locator("#error").inner_text(), "")
                        page.route("**/api/settlement", lambda route: route.abort())
                        page.locator("#refresh").click()
                        expect(page.locator("#refresh")).to_be_enabled()
                        self.assertIn("가져오지 못했습니다", page.locator("#error").inner_text())
                        for selector in ("#state", "#blockers", "#capital", "#settlement"):
                            self.assertEqual(page.locator(selector).inner_text(), "")
                        page.unroute("**/api/settlement")
                        page.locator("#refresh").click()
                        expect(page.locator("#refresh")).to_be_enabled()
                        self.assertIn("조회 완료", page.locator("#state").inner_text())
                        self.assertEqual(page.locator("#error").inner_text(), "")
                        self.assertEqual(before, (journal.shadow_control(), journal.db.total_changes))
                    finally:
                        browser.close()
            finally:
                server.shutdown()
                server.server_close()
                worker.join()
                journal.close()


if __name__ == "__main__":
    unittest.main()
