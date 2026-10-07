import unittest
from unittest.mock import patch

from kiwoom_order_journal_bridge import KiwoomOrderJournalBridge, NativeBridgeError
from order_intent_journal import OrderIntentJournal, OrderJournalError
from shadow_capital_allocator import ShadowCapitalAllocator
import test_shadow_principal_release as fixtures
from test_kiwoom_order_journal_bridge import ACCOUNT, DAY, fill


class LateFillCapitalTests(unittest.TestCase):
    setUp = fixtures.PrincipalReleaseTests.setUp
    tearDown = fixtures.PrincipalReleaseTests.tearDown
    batch = fixtures.PrincipalReleaseTests.batch
    release = fixtures.PrincipalReleaseTests.release

    def released(self):
        self.assertTrue(self.batch()['matched'])
        self.release()

    def late(self, execution='late', quantity=1):
        return self.j.record_execution('d1',broker_order_id='o1',execution_id=execution,quantity=quantity)

    def assert_stopped(self):
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.assertEqual(self.j.get('d1')['state'],'RECONCILIATION_REQUIRED')
        self.assertEqual(self.j.db.execute('SELECT blocked FROM reconciliation_barrier').fetchone()[0],1)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM reconciled_snapshot_bindings').fetchone()[0],0)
        with self.assertRaises(OrderJournalError):
            self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])

    def test_lost_restoration_history_blocks_runtime_and_restart_without_recreation(self):
        self.released()
        self.late()
        self.assertEqual(self.j.db.execute("SELECT component FROM journal_component_history WHERE component='capital_restoration'").fetchall(), [('capital_restoration',)])
        self.j.db.execute('DROP TABLE shadow_capital_release_revocations')
        with self.assertRaisesRegex(OrderJournalError, 'component history missing'):
            self.late()
        self.assertEqual(self.j.get('d1')['filled_quantity'], 1)
        self.assertEqual(self.j.db.execute('SELECT reserve FROM shadow_capital_reservations WHERE key=?', ('d1',)).fetchone(), (83,))
        self.assertIsNone(self.j.db.execute("SELECT 1 FROM sqlite_master WHERE name='shadow_capital_release_revocations'").fetchone())
        self.j.close()
        with self.assertRaisesRegex(OrderJournalError, '^startup safety metadata missing$'):
            OrderIntentJournal(self.path)
        import sqlite3
        with sqlite3.connect(self.path) as db:
            self.assertEqual(db.execute('SELECT filled FROM intents WHERE key=?', ('d1',)).fetchone(), (1,))
            self.assertEqual(db.execute('SELECT reserve FROM shadow_capital_reservations WHERE key=?', ('d1',)).fetchone(), (83,))
            self.assertIsNone(db.execute("SELECT 1 FROM sqlite_master WHERE name='shadow_capital_release_revocations'").fetchone())

    def test_present_legacy_restoration_history_backfills_without_changing_facts(self):
        self.released()
        self.late()
        before=self.j.db.execute('SELECT * FROM shadow_capital_release_revocations').fetchall()
        self.j.db.execute('DROP TABLE journal_component_history')
        self.j.db.execute('PRAGMA user_version=0')
        self.j.close()
        self.j=OrderIntentJournal(self.path)
        self.a=ShadowCapitalAllocator(self.j)
        self.assertEqual(self.j.db.execute('SELECT * FROM shadow_capital_release_revocations').fetchall(), before)
        self.assertEqual(self.j.db.execute("SELECT component FROM journal_component_history WHERE component='capital_restoration'").fetchall(), [('capital_restoration',)])
        self.assertEqual(self.a.state()['managed_reserve_krw'], 83)
        self.assert_stopped()

    def test_filled_release_cannot_become_fee_only_when_restoration_row_is_lost(self):
        self.released()
        self.late()
        self.j.db.execute('DELETE FROM shadow_capital_release_revocations')
        self.j.db.execute('UPDATE shadow_capital_reservations SET reserve=fee_buffer')
        with self.assertRaisesRegex(OrderJournalError, 'filled principal release lacks restoration'):
            self.a.state()
        self.j.close()
        self.j = OrderIntentJournal(self.path)
        self.a = ShadowCapitalAllocator(self.j)
        with self.assertRaisesRegex(OrderJournalError, 'filled principal release lacks restoration'):
            self.a.state()
        self.assertEqual(self.j.get('d1')['filled_quantity'], 1)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone(), (1,))
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM shadow_capital_release_revocations').fetchone(), (0,))
        self.assertEqual(self.j.db.execute('SELECT reserve FROM shadow_capital_reservations').fetchone(), (3,))
        self.assert_stopped()

    def test_late_fill_after_released_principal_restores_reservation_and_stops(self):
        self.released()
        revision=self.a.state()['revision']
        with patch('socket.socket',side_effect=AssertionError('network forbidden')):
            self.late()
        self.assertEqual(self.j.get('d1')['filled_quantity'],1)
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)
        self.assertEqual(self.a.state()['revision'],revision+1)
        self.assertEqual(self.j.db.execute('SELECT released_principal FROM shadow_capital_releases').fetchone()[0],80)
        self.assertEqual(self.j.db.execute('SELECT restored_principal FROM shadow_capital_release_revocations').fetchone()[0],80)
        self.assert_stopped()

    def test_capital_reused_by_another_claim_restores_over_ceiling_exposure_without_dropping_fill(self):
        self.released()
        self.j.register('d2',symbol='OTHER',side='BUY',quantity=12)
        epoch=self.j.enable_shadow(expected_epoch=self.j.shadow_control()['epoch'])['epoch']
        self.a.reserve_and_claim_buy('d2',limit_price_krw=8,fee_buffer_krw=0,
            expected_epoch=epoch,expected_capital_revision=self.a.state()['revision'])
        self.late()
        self.assertEqual(self.a.state()['managed_reserve_krw'],179)
        self.assertEqual(self.j.get('d2')['state'],'SUBMITTING')
        self.assertEqual(self.j.get('d1')['filled_quantity'],1)
        self.assert_stopped()

    def test_duplicates_later_fills_and_restart_do_not_restore_principal_twice(self):
        self.released()
        self.late()
        revision=self.a.state()['revision']
        self.late()
        self.late('late-2',2)
        self.j.close()
        self.j=OrderIntentJournal(self.path)
        self.a=ShadowCapitalAllocator(self.j)
        self.late()
        self.assertEqual(self.a.state()['revision'],revision)
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)
        self.assertEqual(self.j.get('d1')['filled_quantity'],3)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM shadow_capital_release_revocations').fetchone()[0],1)
        self.assert_stopped()

    def test_full_late_fill_keeps_terminal_fact_but_requires_new_complete_batch(self):
        self.released()
        self.late(quantity=10)
        self.assertEqual(self.j.get('d1')['terminal_status'],'FILLED')
        self.assert_stopped()
        self.assertTrue(self.batch(status='FILLED',filled=10,revision=2)['matched'])
        with self.assertRaises(OrderJournalError):self.release(expected_snapshot_revision=2)
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)

    def test_restoration_failure_rolls_back_fill_and_retains_release_for_retry(self):
        self.released()
        self.j.db.execute("CREATE TRIGGER abort_restore BEFORE UPDATE OF reserve ON shadow_capital_reservations BEGIN SELECT RAISE(ABORT,'synthetic failure'); END")
        with self.assertRaises(OrderJournalError):self.late()
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)
        self.assertEqual(self.a.state()['managed_reserve_krw'],3)
        self.assertEqual(self.j.shadow_control()['mode'],'MASTER_OFF')
        self.j.db.execute('DROP TRIGGER abort_restore')
        self.late()
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)
        self.assert_stopped()

    def test_corrupt_release_principal_cannot_reduce_reserve_on_late_fill(self):
        self.released()
        for principal in (-80, 0, 79, 81, 80.5):
            with self.subTest(principal=principal):
                self.j.db.execute('UPDATE shadow_capital_releases SET released_principal=?', (principal,))
                with self.assertRaises(OrderJournalError):
                    self.late()
                self.assertEqual(self.j.get('d1')['filled_quantity'], 0)
                self.assertEqual(self.j.db.execute('SELECT reserve FROM shadow_capital_reservations').fetchone(), (3,))
                self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone(), (0,))
                self.assertEqual(self.j.shadow_control()['mode'], 'MASTER_OFF')
        self.j.db.execute('UPDATE shadow_capital_releases SET released_principal=80')
        self.late()
        self.assertEqual(self.j.get('d1')['filled_quantity'], 1)
        self.assertEqual(self.a.state()['managed_reserve_krw'], 83)
        self.assert_stopped()

    def test_corrupt_restoration_marker_cannot_accept_another_late_fill(self):
        self.released()
        self.late()
        self.j.db.execute("UPDATE shadow_capital_release_revocations SET execution_id='missing'")
        with self.assertRaises(OrderJournalError):
            self.late('later', 1)
        self.assertEqual(self.j.get('d1')['filled_quantity'], 1)
        self.assertEqual(self.j.db.execute('SELECT COUNT(*) FROM executions').fetchone(), (1,))
        self.assertEqual(self.j.db.execute('SELECT reserve FROM shadow_capital_reservations').fetchone(), (83,))
        self.j.db.execute("UPDATE shadow_capital_release_revocations SET execution_id='late'")
        self.late('later', 1)
        self.assertEqual(self.j.get('d1')['filled_quantity'], 2)
        self.assertEqual(self.a.state()['managed_reserve_krw'], 83)

    def test_native_bridge_binding_failure_rolls_back_restoration_and_fill_atomically(self):
        self.released()
        b=KiwoomOrderJournalBridge(self.j,account_fingerprint=ACCOUNT,trading_date=DAY)
        b.bind_order('d1',broker_order_id='o1',native_side='2')
        row=fill(qty=1,remaining=9);row.update(symbol='SYNTHETIC',broker_order_id='o1')
        self.j.db.execute("CREATE TRIGGER abort_native BEFORE INSERT ON native_fill_bindings BEGIN SELECT RAISE(ABORT,'synthetic failure'); END")
        with self.assertRaises(NativeBridgeError):b.apply_execution('d1',row,trading_date=DAY)
        self.assertEqual(self.j.get('d1')['filled_quantity'],0)
        self.assertEqual(self.a.state()['managed_reserve_krw'],3)
        self.j.db.execute('DROP TRIGGER abort_native')
        b.apply_execution('d1',row,trading_date=DAY)
        self.assertEqual(self.j.get('d1')['filled_quantity'],1)
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)
        self.assert_stopped()

    def test_cancel_late_fill_without_release_still_invalidates_batch_and_stops(self):
        self.batch()
        self.late()
        self.assertEqual(self.a.state()['managed_reserve_krw'],83)
        self.assert_stopped()

    def test_exhausted_safety_epoch_still_retains_late_fill_and_restored_capital(self):
        self.released()
        self.j.db.execute('UPDATE shadow_control SET epoch=?', (2**63-1,))
        self.late()
        self.assertEqual(self.j.get('d1')['filled_quantity'], 1)
        self.assertEqual(self.a.state()['managed_reserve_krw'], 83)
        self.assertEqual(self.j.shadow_control()['epoch'], 2**63-1)
        self.assert_stopped()

    def test_exhausted_capital_revision_preserves_late_fill_and_blocks_new_capacity(self):
        self.released()
        self.j.db.execute('UPDATE shadow_capital_config SET revision=?', (2**63-1,))
        self.late()
        state = self.a.state()
        self.assertEqual(state['revision'], 2**63-1)
        self.assertIs(type(state['revision']), int)
        self.assertEqual(state['managed_reserve_krw'], 83)
        self.assertEqual(self.j.get('d1')['filled_quantity'], 1)
        self.assert_stopped()
        self.j.register('d2',symbol='OTHER',side='BUY',quantity=1)
        with self.assertRaises(OrderJournalError):
            self.a.reserve_and_claim_buy('d2',limit_price_krw=1,fee_buffer_krw=0,
                expected_epoch=self.j.shadow_control()['epoch'],expected_capital_revision=2**63-1)
        self.assertEqual(self.j.get('d2')['state'], 'INTENT_CREATED')
        self.assertEqual(self.a.state()['managed_reserve_krw'], 83)

    def test_restored_total_above_sqlite_sum_range_remains_exact_and_unusable(self):
        self.released()
        # Fixture individual reservations are representable; total exceeds int64.
        self.j.register('other', symbol='OTHER', side='BUY', quantity=2**63-1)
        self.j.db.execute('INSERT INTO shadow_capital_reservations VALUES(?,?,?,?)',('other',1,0,2**63-1))
        self.late()
        self.assertEqual(self.a.state()['managed_reserve_krw'],2**63-1+83)
        self.assert_stopped()


if __name__=='__main__':unittest.main()
