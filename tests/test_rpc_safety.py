import pytest

from backend.app.adapters.rpc import ReadOnlyRpcClient


def test_mainnet_write_method_is_rejected_before_network() -> None:
    client = ReadOnlyRpcClient("https://example.invalid")
    with pytest.raises(ValueError, match="not permitted"):
        client.call("eth_sendRawTransaction", ["0xdeadbeef"])


def test_block_tag_is_explicit() -> None:
    assert ReadOnlyRpcClient.block_tag(123) == "0x7b"
    assert ReadOnlyRpcClient.block_tag(None) == "finalized"
