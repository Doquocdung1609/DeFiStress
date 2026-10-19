"""Archive gate fixtures are synthetic, not independent historical observations."""
import importlib.util
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('archive_repair', Path(__file__).resolve().parents[1] /
       'docs/research_v2/phase01b/archive_independence/collect.py')
assert spec is not None and spec.loader is not None
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ArchiveIndependenceTests(unittest.TestCase):
    def test_agreeing_data_without_backend_evidence_is_blocked(self):
        self.assertEqual(module.gate([{'status': 'AGREES'}], True, False), 'BLOCKED')

    def test_missing_is_not_zero_or_agreement(self):
        expected = {'data': {'fields': {'liquidity': 0}}}
        row = module.field_comparison(expected, {'data': None})[0]
        self.assertIsNone(row['observed'])
        self.assertEqual(row['status'], 'BLOCKED_MISSING_DATA')

    def test_mismatch_cannot_be_hidden_by_missing_independence(self):
        self.assertEqual(module.gate([{'status': 'MISMATCH'}], True, False), 'FAIL')

    def test_repeat_read_required_even_if_independence_were_proven(self):
        self.assertEqual(module.gate([{'status': 'AGREES'}], False, True), 'BLOCKED')

    def test_abi_tuples_and_saved_json_arrays_compare_by_value(self):
        expected = {'data': {'fields': {'slot0': [1, 2, True]}}}
        observed = {'data': {'fields': {'slot0': (1, 2, True)}, 'unavailable': {}}}
        self.assertEqual(module.field_comparison(expected, observed)[0]['status'], 'AGREES')
        self.assertEqual(module.field_comparison(observed, expected)[0]['status'], 'AGREES')

    def test_empty_comparison_is_never_pass(self):
        self.assertEqual(module.gate([], True, True), 'BLOCKED')

    def test_pass_requires_all_three_conditions(self):
        self.assertEqual(module.gate([{'status': 'AGREES'}], True, True), 'PASS')


if __name__ == '__main__':
    unittest.main()
