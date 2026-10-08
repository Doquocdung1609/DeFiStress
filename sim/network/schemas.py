from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

GRAPH_MODEL_VERSION = "0.1.0-multilayer-contagion"


class NodeLayer(StrEnum):
    PROTOCOL = "PROTOCOL"
    ASSET = "ASSET"
    AGENT_ROLE = "AGENT_ROLE"
    REFERENCE_MARKET = "REFERENCE_MARKET"


class EvidenceStatus(StrEnum):
    OBSERVED_SNAPSHOT = "OBSERVED_SNAPSHOT"
    OBSERVED_ONCHAIN = "OBSERVED_ONCHAIN"
    SIMULATED_RUN = "SIMULATED_RUN"
    DERIVED_METRIC = "DERIVED_METRIC"
    SCENARIO_ASSUMPTION = "SCENARIO_ASSUMPTION"
    CONCEPTUAL_EXTENSION = "CONCEPTUAL_EXTENSION"


class RelationType(StrEnum):
    COLLATERAL_EXPOSURE = "COLLATERAL_EXPOSURE"
    DEBT_EXPOSURE = "DEBT_EXPOSURE"
    BORROWER_POSITION_EXPOSURE = "BORROWER_POSITION_EXPOSURE"
    LIQUIDATION_ROUTE = "LIQUIDATION_ROUTE"
    EXECUTION_PRICE_CHANNEL = "EXECUTION_PRICE_CHANNEL"
    REVALUATION_CHANNEL = "REVALUATION_CHANNEL"
    LIQUIDATION_FLOW = "LIQUIDATION_FLOW"
    EXECUTION_PRICE_IMPACT = "EXECUTION_PRICE_IMPACT"
    REVALUATION_FEEDBACK = "REVALUATION_FEEDBACK"
    ARBITRAGE_STABILIZATION = "ARBITRAGE_STABILIZATION"
    LIQUIDATION_EXECUTION = "LIQUIDATION_EXECUTION"
    REFERENCE_PRICE_LINK = "REFERENCE_PRICE_LINK"


@dataclass(frozen=True, slots=True)
class GraphNode:
    id: str
    label: str
    layer: NodeLayer
    node_type: str
    evidence_status: EvidenceStatus
    snapshot_id: str
    description: str
    raw_metrics: dict[str, float | int | str | None] = field(default_factory=dict)
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class GraphEdge:
    id: str
    source: str
    target: str
    relation_type: RelationType
    layer: str
    direction: str
    raw_value: dict[str, float | int | str | None]
    unit: str
    normalized_strength: float
    evidence_status: EvidenceStatus
    provenance: dict[str, Any]
    description: str
    formula: str
    active: bool = True
    step: int | None = None
    wave: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class GraphFrame:
    index: int
    label: str
    wave: int
    step: int
    active_nodes: list[str]
    active_edge_ids: list[str]
    active_edges: list[dict[str, Any]]
    price_state: dict[str, float | None]
    liquidation_volume_usd: float
    forced_weth: float
    liquidation_event_count: int
    cumulative_liquidated_debt_usd: float
    cascade_depth_so_far: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
