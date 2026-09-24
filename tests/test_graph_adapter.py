from __future__ import annotations

from typing import Any

import httpx
import pytest

from backend.app.adapters.graph import GraphClient, GraphError


def test_graph_client_uses_bearer_auth_and_reads_indexed_block(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_post(url: str, **kwargs: Any) -> httpx.Response:
        captured.update({"url": url, **kwargs})
        return httpx.Response(200, json={"data": {"_meta": {"block": {"number": 123, "hash": "0xabc"}}}})

    monkeypatch.setattr(httpx, "post", fake_post)
    graph = GraphClient("secret-key", "subgraph-id")

    assert graph.indexed_block() == 123
    assert captured["url"] == "https://gateway.thegraph.com/api/subgraphs/id/subgraph-id"
    assert captured["headers"]["Authorization"] == "Bearer secret-key"
    assert "secret-key" not in captured["url"]
    assert "_meta" in captured["json"]["query"]


def test_graph_client_redacts_api_key_from_http_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args: Any, **kwargs: Any) -> httpx.Response:
        return httpx.Response(401, text="invalid token secret-key")

    monkeypatch.setattr(httpx, "post", fake_post)
    graph = GraphClient("secret-key", "subgraph-id")

    with pytest.raises(GraphError) as exc_info:
        graph.query("query { _meta { block { number } } }")

    assert "secret-key" not in str(exc_info.value)
    assert "[REDACTED]" in str(exc_info.value)


def test_graph_client_surfaces_graphql_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*args: Any, **kwargs: Any) -> httpx.Response:
        return httpx.Response(200, json={"errors": [{"message": "indexed block unavailable"}]})

    monkeypatch.setattr(httpx, "post", fake_post)

    with pytest.raises(GraphError, match="indexed block unavailable"):
        GraphClient("secret-key", "subgraph-id").query("query { broken }")
