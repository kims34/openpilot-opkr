import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import audit_retired_validation as audit
import validation_stage_gate as gate


class RetiredGateTests(unittest.TestCase):
    def test_all_downstream_stages_block_before_outcome_or_self_authority_read(self):
        with patch.object(gate,'load_json',side_effect=AssertionError('outcome read forbidden')):
            for stage in ('shadow_s1','fresh_confirmation_s2','live'):
                with self.subTest(stage=stage), self.assertRaisesRegex(SystemExit,'RETIRED_VALIDATION_LINEAGE'):
                    gate.check(stage)

    def test_forged_passed_flags_cannot_resurrect_retired_stages(self):
        forged={'passed':True,'policy_changed_after_unseal':False,
                'real_orders_sent':False,'fresh_data':True}
        with patch.object(gate,'load_json',return_value=forged) as read:
            for stage in ('shadow_s1','fresh_confirmation_s2','live'):
                with self.assertRaises(SystemExit): gate.check(stage)
            read.assert_not_called()

    def test_absent_result_does_not_authorize_another_window(self):
        with tempfile.TemporaryDirectory() as root:
            with patch.object(gate,'SEALED_RESULT',Path(root)/'absent.json'):
                with self.assertRaisesRegex(SystemExit,'RETIRED_VALIDATION_LINEAGE'):
                    gate.check('sealed_holdout')

    def test_consumed_result_blocks_without_parsing_even_invalid_json(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'result.json'
            p.write_bytes(b'preserved invalid content')
            with patch.object(gate,'SEALED_RESULT',p), patch.object(gate,'load_json',side_effect=AssertionError('read')):
                with self.assertRaisesRegex(SystemExit,'window is consumed'):
                    gate.check('sealed_holdout')
            self.assertEqual(p.read_bytes(),b'preserved invalid content')

    def test_unknown_stage_fails_closed(self):
        with self.assertRaisesRegex(SystemExit,'unknown stage'): gate.check('forged')

    def test_deployment_audit_hashes_bytes_without_outcome_parse_or_write(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'result.json'
            raw=b'no json parsing allowed here'
            p.write_bytes(raw)
            expected={'result.json':hashlib.sha256(raw).hexdigest()}
            with patch.object(audit,'ROOT',Path(root)), patch.object(audit,'EXPECTED',expected), patch.object(gate,'SEALED_RESULT',p), patch.object(gate,'load_json',side_effect=AssertionError('read')):
                out=audit.audit()
            self.assertTrue(out['validation_boundary_preserved'])
            self.assertFalse(out['outcome_metrics_parsed'])
            self.assertEqual(p.read_bytes(),raw)

    def test_missing_or_changed_artifact_is_not_preserved(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/'changed.json'
            p.write_bytes(b'changed')
            with patch.object(audit,'ROOT',Path(root)), patch.object(audit,'EXPECTED',{'changed.json':'0'*64,'missing.json':'1'*64}):
                self.assertFalse(audit.audit()['validation_boundary_preserved'])


if __name__=='__main__': unittest.main()
