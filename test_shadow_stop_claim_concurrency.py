"""Deterministic synthetic stop/claim serialization; no broker or LIVE credit."""
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from threading import Barrier, Event
from unittest.mock import patch

from indexalert_automation_control import AutomationCapitalState, AutomationUserControls
from order_intent_journal import OrderIntentJournal, OrderJournalError
from shadow_capital_allocator import ShadowCapitalAllocator


class StopClaimConcurrencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'synthetic.sqlite'
        self.journal = OrderIntentJournal(self.path)
        self.allocator = ShadowCapitalAllocator(self.journal)
        self.allocator.configure(controls=AutomationUserControls(True, 100),
            baseline=AutomationCapitalState(0, 0), expected_revision=0)
        self.journal.register('synthetic', symbol='SYNTHETIC', side='BUY', quantity=10)

    def tearDown(self):
        self.journal.close()
        self.tmp.cleanup()

    @staticmethod
    def wait(event):
        if not event.wait(5):
            raise AssertionError('synthetic transaction synchronization timed out')

    def claim(self, journal, allocator, epoch):
        return allocator.reserve_and_claim_buy('synthetic', limit_price_krw=8,
            fee_buffer_krw=3, expected_epoch=epoch, expected_capital_revision=1)

    def race(self, *, kill_first, capital_change=False):
        ready, armed = Barrier(2, timeout=5), Barrier(2, timeout=5)
        locked, attempted = Event(), Event()
        shared = {}

        def worker(is_kill):
            journal = OrderIntentJournal(self.path)
            try:
                allocator = ShadowCapitalAllocator(journal)
                def stop():
                    if capital_change:
                        return allocator.configure(
                            controls=AutomationUserControls(False, 0),
                            baseline=AutomationCapitalState(0, 0), expected_revision=1)
                    return journal.trip_kill_switch()
                if ready.wait() == 0:
                    shared['epoch'] = journal.enable_shadow(
                        expected_epoch=journal.shadow_control()['epoch'])['epoch']
                armed.wait()
                if is_kill == kill_first:
                    # The first action holds the write lock until the other
                    # connection has reached its BEGIN IMMEDIATE boundary.
                    method = '_stop_shadow' if is_kill else '_claim_submission_locked'
                    original = getattr(journal, method)

                    def held(*args, **kwargs):
                        locked.set()
                        self.wait(attempted)
                        return original(*args, **kwargs)

                    with patch.object(journal, method, held):
                        return stop() if is_kill else self.claim(
                            journal, allocator, shared['epoch'])
                self.wait(locked)
                original_atomic = journal._atomic

                @contextmanager
                def competing_atomic():
                    attempted.set()
                    with original_atomic():
                        yield

                with patch.object(journal, '_atomic', competing_atomic):
                    if is_kill:
                        return stop()
                    try:
                        return self.claim(journal, allocator, shared['epoch'])
                    except OrderJournalError:
                        return 'CLAIM_DENIED'
            finally:
                journal.close()

        with patch('socket.socket', side_effect=AssertionError('network forbidden')):
            with ThreadPoolExecutor(max_workers=2) as pool:
                kill = pool.submit(worker, True)
                claim = pool.submit(worker, False)
                return kill.result(timeout=10), claim.result(timeout=10)

    def test_kill_commits_first_and_claim_reservation_rolls_back(self):
        kill, claim = self.race(kill_first=True)
        self.assertEqual(claim, 'CLAIM_DENIED')
        self.assertTrue(kill['killed'])
        self.assertEqual(self.journal.get('synthetic')['state'], 'INTENT_CREATED')
        self.assertEqual(self.allocator.state()['managed_reserve_krw'], 0)
        self.assertEqual(self.journal.shadow_control()['mode'], 'MASTER_OFF')

    def test_claim_commits_first_and_kill_preserves_uncertain_exposure(self):
        kill, claim = self.race(kill_first=False)
        self.assertEqual(claim['reservation_krw'], 83)
        self.assertFalse(claim['broker_request_sent'])
        self.assertFalse(claim['live_ordering_authorized'])
        self.assertTrue(kill['killed'])
        self.assertEqual(self.allocator.state()['managed_reserve_krw'], 83)
        self.assertEqual(self.journal.get('synthetic')['state'], 'SUBMITTING')
        self.assertEqual(self.journal.shadow_control()['mode'], 'MASTER_OFF')
        with self.assertRaises(OrderJournalError):
            self.journal.reset_kill_switch(expected_epoch=kill['epoch'])
        reopened = OrderIntentJournal(self.path)
        try:
            self.assertTrue(reopened.shadow_control()['killed'])
            self.assertEqual(reopened.get('synthetic')['state'], 'RECONCILIATION_REQUIRED')
            self.assertEqual(ShadowCapitalAllocator(reopened).state()['managed_reserve_krw'], 83)
            with self.assertRaises(OrderJournalError):
                self.claim(reopened, ShadowCapitalAllocator(reopened), kill['epoch'])
        finally:
            reopened.close()

    def test_reconnect_fences_an_old_connection_without_erasing_reservation(self):
        epoch = self.journal.enable_shadow(
            expected_epoch=self.journal.shadow_control()['epoch'])['epoch']
        self.claim(self.journal, self.allocator, epoch)
        reopened = OrderIntentJournal(self.path)
        try:
            self.assertEqual(self.journal.shadow_control()['mode'], 'MASTER_OFF')
            self.assertGreater(self.journal.shadow_control()['epoch'], epoch)
            self.assertEqual(self.journal.get('synthetic')['state'], 'RECONCILIATION_REQUIRED')
            self.assertEqual(self.allocator.state()['managed_reserve_krw'], 83)
            self.journal.register('next', symbol='SYNTHETIC_NEXT', side='BUY', quantity=1)
            with self.assertRaises(OrderJournalError):
                self.allocator.reserve_and_claim_buy('next', limit_price_krw=1,
                    fee_buffer_krw=0, expected_epoch=epoch, expected_capital_revision=1)
            self.assertEqual(self.journal.get('next')['state'], 'INTENT_CREATED')
            self.assertEqual(self.allocator.state()['managed_reserve_krw'], 83)
            with self.assertRaises(OrderJournalError):
                reopened.enable_shadow(expected_epoch=reopened.shadow_control()['epoch'])
        finally:
            reopened.close()

    def test_capital_disable_commits_first_and_stale_claim_cannot_reserve(self):
        configured, claim = self.race(kill_first=True, capital_change=True)
        self.assertEqual(claim, 'CLAIM_DENIED')
        self.assertEqual(configured['revision'], 2)
        self.assertFalse(configured['controls'].automation_enabled)
        self.assertEqual(configured['controls'].max_automation_capital_krw, 0)
        self.assertEqual(self.journal.get('synthetic')['state'], 'INTENT_CREATED')
        self.assertEqual(self.allocator.state()['managed_reserve_krw'], 0)
        self.assertEqual(self.journal.shadow_control()['mode'], 'MASTER_OFF')

    def test_claim_commits_first_then_capital_disable_preserves_reserve(self):
        configured, claim = self.race(kill_first=False, capital_change=True)
        self.assertEqual(claim['reservation_krw'], 83)
        self.assertFalse(claim['broker_request_sent'])
        self.assertFalse(claim['live_ordering_authorized'])
        state = self.allocator.state()
        self.assertEqual(state['revision'], 2)
        self.assertFalse(state['controls'].automation_enabled)
        self.assertEqual(state['controls'].max_automation_capital_krw, 0)
        self.assertEqual(state['managed_reserve_krw'], 83)
        self.assertEqual(self.journal.get('synthetic')['state'], 'SUBMITTING')
        self.assertEqual(self.journal.shadow_control()['mode'], 'MASTER_OFF')
        reopened = OrderIntentJournal(self.path)
        try:
            self.assertEqual(reopened.get('synthetic')['state'], 'RECONCILIATION_REQUIRED')
            restored = ShadowCapitalAllocator(reopened).state()
            self.assertEqual(restored['revision'], 2)
            self.assertEqual(restored['managed_reserve_krw'], 83)
            self.assertFalse(restored['controls'].automation_enabled)
            with self.assertRaises(OrderJournalError):
                reopened.enable_shadow(expected_epoch=reopened.shadow_control()['epoch'])
        finally:
            reopened.close()


if __name__ == '__main__':
    unittest.main()
