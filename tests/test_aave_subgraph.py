from __future__ import annotations

from typing import Any

from backend.app.adapters.aave.subgraph import discover_borrowers_from_graph
from backend.app.adapters.graph import GraphError


class FakeGraph:
    def __init__(self) -> None:
        self.calls: list[dict[str, int]] = []

    def query(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        assert "block: { number: $block }" in query
        assert 'scaledVariableDebt_gt: "0"' in query
        assert 'principalStableDebt_gt: "0"' in query
        self.calls.append(variables)
        if variables["skip"] == 0:
            return {
                "variableDebt": [{"user": {"id": "0xAa"}}, {"user": {"id": "0xBb"}}],
                "stableDebt": [{"user": {"id": "0xaa"}}, {"user": {"id": "0xCc"}}],
            }
        return {"variableDebt": [], "stableDebt": []}


def test_graph_borrower_discovery_paginates_deduplicates_and_pins_block() -> None:
    graph = FakeGraph()

    users = discover_borrowers_from_graph(  # type: ignore[arg-type]
        graph,
        block_number=19_000_000,
        page_size=2,
        max_pages=5,
        max_users=10,
    )

    assert users == ["0xaa", "0xbb", "0xcc"]
    assert [call["skip"] for call in graph.calls] == [0, 2]
    assert {call["block"] for call in graph.calls} == {19_000_000}


def test_graph_borrower_discovery_stops_at_max_users() -> None:
    graph = FakeGraph()

    users = discover_borrowers_from_graph(  # type: ignore[arg-type]
        graph,
        block_number=19_000_000,
        page_size=2,
        max_pages=5,
        max_users=2,
    )

    assert users == ["0xaa", "0xbb"]
    assert len(graph.calls) == 1


class PositionSchemaGraph:
    def __init__(self) -> None:
        self.calls: list[dict[str, int]] = []

    def query(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(variables)
        if "userReserves" in query:
            raise GraphError("Type `Query` has no field `userReserves`")
        return {
            "positions": [
                {"account": {"id": "0xAa"}, "balance": "1", "type": "VARIABLE"},
                {"account": {"id": "0xaa"}, "balance": "2", "type": "STABLE"},
            ]
        }


def test_graph_borrower_discovery_supports_configured_position_schema() -> None:
    graph = PositionSchemaGraph()

    users = discover_borrowers_from_graph(  # type: ignore[arg-type]
        graph,
        block_number=19_000_000,
        page_size=100,
        max_pages=5,
        max_users=10,
    )

    assert users == ["0xaa"]
    assert {call["block"] for call in graph.calls} == {19_000_000}
