"""Phase01-B data validation tests; fixtures are never labeled Mainnet evidence."""
import gzip
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "historical_validation", Path(__file__).resolve().parents[1] / "docs/research_v2/phase01b/collector.py"
)
assert SPEC is not None and SPEC.loader is not None
b = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(b)


def reserve(supplied=0, debt=0, decimals=6, price=100000000, lt=8500, enabled=False, index=0):
    return {"status": "AVAILABLE", "data": [supplied, 0, debt, 0, 0, 0, 0, 0, enabled],
            "decimals": decimals, "price": price, "lt": lt, "reserve_id": index}


class Phase01BValidationTests(unittest.TestCase):
    def test_negative_tick_words_are_contiguous(self):
        low, high, words = b.tick_bounds(-3, 10)
        self.assertEqual((low % 10, high % 10), (0, 0))
        self.assertEqual(words, list(range(words[0], words[-1] + 1)))
        self.assertLessEqual(low, -3)
        self.assertGreaterEqual(high, -3)

    def test_tick_bounds_clamp_legal_domain(self):
        low, high, _ = b.tick_bounds(887270, 60)
        self.assertLessEqual(high, 887272)
        self.assertGreaterEqual(low, -887272)

    def test_duplicate_ticks_fail(self):
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            b.liquidity_audit([{"tick": 0}, {"tick": 0}], 0, 1)

    def test_gross_net_inconsistency_fails(self):
        with self.assertRaisesRegex(ValueError, "GROSS_NET"):
            b.liquidity_audit([{"tick": 0, "gross": "1", "net": "2"}], 0, 3)

    def test_negative_anchored_liquidity_fails(self):
        with self.assertRaisesRegex(ValueError, "NEGATIVE"):
            b.liquidity_audit([{"tick": -10, "gross": "20", "net": "20"}], 0, 10)

    def test_valid_liquidity_is_anchored_not_independent(self):
        result = b.liquidity_audit([{"tick": -10, "gross": "20", "net": "5"}], 0, 10)
        self.assertEqual(result["status"], "PASS")
        self.assertIn("NOT_INDEPENDENT", result["boundary_status"])

    def test_valid_historical_round(self):
        self.assertEqual(b.validate_round([3, 100, 90, 95, 3], 100)["age_seconds_at_block"], 5)

    def test_future_round_rejected(self):
        with self.assertRaisesRegex(ValueError, "TIMESTAMP"):
            b.validate_round([3, 100, 90, 101, 3], 100)

    def test_incomplete_round_rejected(self):
        with self.assertRaisesRegex(ValueError, "INVALID_ROUND"):
            b.validate_round([3, 100, 90, 95, 2], 100)

    def test_proxy_phase_bits_are_not_raw_aggregator_round_ids(self):
        wrapped = (7 << 64) | 42
        b.compare_proxy_round([wrapped, 100, 90, 95, wrapped], [42, 100, 90, 95, 42])
        with self.assertRaisesRegex(ValueError, "ROUND_MISMATCH"):
            b.compare_proxy_round([wrapped, 100, 90, 95, wrapped], [42, 101, 90, 95, 42])

    def test_agreement_is_not_independence(self):
        state = {"fields": {"x": 1}, "unavailable": {}}
        result = b.compare_fields(state, state)
        self.assertEqual(result["agreeing_fields"], 1)
        self.assertEqual(result["independent_validation_status"], "INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED")

    def test_missing_is_not_a_mismatch_or_zero(self):
        result = b.compare_fields({"fields": {"x": 1}, "unavailable": {}},
                                  {"fields": {}, "unavailable": {"x": {}}})
        self.assertEqual((result["mismatches"], result["missing_fields"]), (0, 1))
        self.assertIsNone(result["fields"][0]["comparison"])

    def test_field_mismatch_is_explicit(self):
        result = b.compare_fields({"fields": {"x": 1}, "unavailable": {}},
                                  {"fields": {"x": 2}, "unavailable": {}})
        self.assertEqual(result["mismatches"], 1)

    def test_full_portfolio_hf_uses_both_assets_and_decimals(self):
        rows = [reserve(2 * 10**18, 0, 18, 2000 * 10**8, 8000, True, 0),
                reserve(1000 * 10**6, 2000 * 10**6, enabled=True, index=1)]
        account = [5000 * 10**8, 2000 * 10**8, 0, 0, 0, 2025000000000000000]
        result = b.reconstruct_account(rows, account, None, 0)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["hf_raw"], "2025000000000000000")

    def test_emode_bitmap_override_is_asset_specific(self):
        rows = [reserve(2 * 10**18, 0, 18, 2000 * 10**8, 8000, True, 0),
                reserve(1000 * 10**6, 2000 * 10**6, enabled=True, index=1)]
        account = [5000 * 10**8, 2000 * 10**8, 0, 0, 0, 2325000000000000000]
        mode = {"status": "AVAILABLE", "lt": 9500, "collateral_bitmap": "1"}
        self.assertEqual(b.reconstruct_account(rows, account, mode, 0)["status"], "PASS")

    def test_missing_reserve_blocks_hf(self):
        result = b.reconstruct_account([{"status": "BLOCKED", "data": None}], [0] * 6, None, 0)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIsNone(result["hf_raw"])

    def test_zero_price_is_missing_valuation_not_zero_debt(self):
        result = b.reconstruct_account([reserve(debt=1, price=0)], [0] * 6, None, 0)
        self.assertEqual(result["status"], "BLOCKED")

    def test_zero_debt_sentinel_is_preserved(self):
        maximum = (1 << 256) - 1
        result = b.reconstruct_account([reserve()], [0, 0, 0, 0, 0, maximum], None, 0)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["hf_raw"], str(maximum))

    def test_discovery_has_no_future_logs(self):
        log = {"blockNumber": "0x401", "address": "pool", "topics": ["sig", "0x00", "0x" + "1" * 64],
               "blockHash": "0x" + "2" * 64}
        with self.assertRaisesRegex(ValueError, "LEAKAGE"):
            b.choose_borrowers([log], {"number": 1024}, "pool", "sig", 8)

    def test_historical_selector_never_latest(self):
        rpc = b.Rpc.__new__(b.Rpc)
        rpc.block = {"number": 100, "expected_hash": "hash"}
        with self.assertRaises(b.DataIssue):
            rpc.check("eth_call", [{}, "latest"])
        rpc.check("eth_call", [{}, {"blockHash": "hash", "requireCanonical": True}])

    def test_provider_limit_is_not_a_data_mismatch(self):
        self.assertEqual(b.issue_kind("Batch of more than 3 requests not allowed on free plan"),
                         "PROVIDER_CAPABILITY_LIMIT")

    def test_gzip_and_uncompressed_hash_domains(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json.gz"
            metadata = b.dump_gzip(path, {"x": 123})
            self.assertNotEqual(metadata["sha256_gzip_bytes"], metadata["sha256_canonical_json_bytes"])
            self.assertEqual(json.loads(gzip.decompress(path.read_bytes())), {"x": 123})

    def test_exact_log_fallback_requires_the_whole_registered_window(self):
        with self.assertRaises(b.DataIssue):
            b.validate_discovery_headers([], {"number": 1024})

    def test_discovery_headers_must_be_contiguous(self):
        def h(n):
            return "0x" + f"{n:064x}"
        rows = [{"number": hex(n), "hash": h(n), "parentHash": h(n - 1), "timestamp": hex(n)}
                for n in range(1, 1025)]
        block = {"number": 1024, "expected_hash": h(1024), "timestamp_unix": 1024}
        self.assertEqual(len(b.validate_discovery_headers(rows, block)), 1024)
        rows[100]["parentHash"] = h(9999)
        with self.assertRaisesRegex(ValueError, "DISCONTINUOUS"):
            b.validate_discovery_headers(rows, block)

    def test_discovery_header_timestamp_cannot_exceed_snapshot(self):
        def h(n):
            return "0x" + f"{n:064x}"
        rows = [{"number": hex(n), "hash": h(n), "parentHash": h(n - 1), "timestamp": hex(n)}
                for n in range(1, 1025)]
        rows[-1]["timestamp"] = hex(1025)
        with self.assertRaisesRegex(ValueError, "TIMESTAMP_LEAKAGE"):
            b.validate_discovery_headers(rows, {"number": 1024, "expected_hash": h(1024), "timestamp_unix": 1024})


if __name__ == "__main__":
    unittest.main()
