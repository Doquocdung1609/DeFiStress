"""Deterministic tests of data integrity boundaries, not simulated Mainnet data."""
import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "historical_pilot", Path(__file__).resolve().parents[1] / "docs/research_v2/phase01a/pilot.py"
)
assert SPEC is not None and SPEC.loader is not None
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)

HASH = "0x" + "a" * 64
BLOCK = {"number": 100, "expected_hash": HASH}
HEADER = {"number": "0x64", "hash": HASH, "timestamp": "0x3e8", "parentHash": "0x" + "b" * 64}
USDC = "0x" + "1" * 40
WETH = "0x" + "2" * 40
TOKENS = {"USDC": {"address": USDC, "decimals": 6}, "WETH": {"address": WETH, "decimals": 18}}


class FakeRpc:
    def __init__(self, chain="0x1", logs=None):
        self.chain = chain
        self.logs = logs
        self.calls = []

    def call(self, method, params):
        self.calls.append((method, params))
        return {"eth_chainId": self.chain, "eth_call": "0x01", "eth_getBlockByNumber": HEADER,
                "eth_getLogs": self.logs}.get(method)


class HistoricalIntegrityTests(unittest.TestCase):
    def test_registered_header(self):
        self.assertEqual(pilot.validate_header(HEADER, 100, HASH)["timestamp"], 1000)

    def test_missing_header_is_not_zero(self):
        with self.assertRaisesRegex(ValueError, "MISSING_BLOCK_HEADER"):
            pilot.validate_header(None, 100)

    def test_wrong_block_number(self):
        with self.assertRaisesRegex(ValueError, "BLOCK_NUMBER_MISMATCH"):
            pilot.validate_header(HEADER, 99)

    def test_wrong_block_hash(self):
        with self.assertRaisesRegex(ValueError, "BLOCK_HASH_MISMATCH"):
            pilot.validate_header(HEADER, 100, "0x" + "f" * 64)

    def test_wrong_chain(self):
        with self.assertRaisesRegex(ValueError, "CHAIN_ID_MISMATCH"):
            pilot.HistoricalSession("fixture", BLOCK, FakeRpc(chain="0xa"))

    def test_state_is_pinned_by_canonical_hash(self):
        rpc = FakeRpc()
        session = pilot.HistoricalSession("fixture", BLOCK, rpc)
        session.state_call([{"to": USDC, "data": "0x1234"}, "0x64"])
        self.assertEqual(rpc.calls[-1][1][1], {"blockHash": HASH, "requireCanonical": True})

    def test_latest_and_other_height_are_rejected(self):
        session = pilot.HistoricalSession("fixture", BLOCK, FakeRpc())
        for tag in ["latest", "pending", "0x65", {"blockHash": "wrong"}]:
            with self.subTest(tag=tag), self.assertRaisesRegex(ValueError, "UNPINNED_STATE_CALL"):
                session.state_call([{}, tag])

    def test_no_transaction_submission(self):
        session = pilot.HistoricalSession("fixture", BLOCK, FakeRpc())
        with self.assertRaisesRegex(ValueError, "METHOD_NOT_PERMITTED"):
            session.read("eth_sendRawTransaction", ["0x00"])

    def test_pool_metadata(self):
        pilot.validate_pool_metadata(USDC, WETH, 500, [6, 18], {"fee": 500}, TOKENS)

    def test_token_order(self):
        with self.assertRaisesRegex(ValueError, "TOKEN_ORDER"):
            pilot.validate_pool_metadata(WETH, USDC, 500, [18, 6], {"fee": 500}, TOKENS)

    def test_fee_mismatch(self):
        with self.assertRaisesRegex(ValueError, "FEE_MISMATCH"):
            pilot.validate_pool_metadata(USDC, WETH, 3000, [6, 18], {"fee": 500}, TOKENS)

    def test_decimals_mismatch(self):
        with self.assertRaisesRegex(ValueError, "DECIMALS_MISMATCH"):
            pilot.validate_pool_metadata(USDC, WETH, 500, [18, 18], {"fee": 500}, TOKENS)

    def test_repeat_content_hash(self):
        a = {"components": {"pool": {"status": "AVAILABLE", "data": {"liquidity": "42"}}}}
        self.assertEqual(pilot.repeat_verdict(a, a)["status"], "PASS")
        b = {"components": {"pool": {"status": "AVAILABLE", "data": {"liquidity": "43"}}}}
        self.assertEqual(pilot.repeat_verdict(a, b)["status"], "FAIL_CONTENT_MISMATCH")

    def test_two_missing_sweeps_do_not_pass_repeatability(self):
        a = {"components": {"pool": {"status": "QUARANTINED", "data": None}}}
        self.assertEqual(pilot.repeat_verdict(a, a)["status"], "NOT_EVALUABLE_INCOMPLETE")

    def test_canonical_key_order(self):
        self.assertEqual(pilot.digest({"a": 1, "b": 2}), pilot.digest({"b": 2, "a": 1}))

    def test_missing_is_quarantined_without_zero_fill(self):
        def failure():
            raise ValueError("archive missing")
        result = pilot.safe_component(failure)
        self.assertEqual(result["status"], "QUARANTINED")
        self.assertIsNone(result["data"])

    def test_empty_logs_are_an_observed_empty_list(self):
        session = pilot.HistoricalSession("fixture", BLOCK, FakeRpc(logs=[]))
        self.assertEqual(session.logs(USDC, HASH), [])
        self.assertEqual(session.rpc.calls[-1][1][0]["blockHash"], HASH)

    def test_missing_logs_are_not_an_empty_observation(self):
        session = pilot.HistoricalSession("fixture", BLOCK, FakeRpc(logs=None))
        with self.assertRaisesRegex(ValueError, "MISSING_RPC_RESULT"):
            session.logs(USDC, HASH)

    def test_logs_cannot_leak_another_block(self):
        row = {"blockNumber": "0x65", "blockHash": HASH, "address": USDC, "topics": [HASH]}
        session = pilot.HistoricalSession("fixture", BLOCK, FakeRpc(logs=[row]))
        with self.assertRaisesRegex(ValueError, "LEAKAGE"):
            session.logs(USDC, HASH)

    def test_oracle_config_resolved_at_requested_height(self):
        values = [USDC, WETH, USDC, WETH, USDC, 100000000]
        with patch.object(pilot, "read_contract", side_effect=values) as calls:
            result = pilot.historical_aave_config(None, {"aave_pool": WETH}, 100)
        self.assertEqual(result["oracle"], USDC)
        self.assertEqual(result["base_unit_raw"], "100000000")
        self.assertTrue(all(call.args[4] == 100 for call in calls.call_args_list))

    def test_historical_pool_address_mismatch(self):
        with patch.object(pilot, "read_contract", side_effect=[USDC, USDC]):
            with self.assertRaisesRegex(ValueError, "HISTORICAL_AAVE_POOL_MISMATCH"):
                pilot.historical_aave_config(None, {"aave_pool": WETH}, 100)


if __name__ == "__main__":
    unittest.main()
