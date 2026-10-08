from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class SnapshotCreate(BaseModel):
    mode: Literal["FIXTURE", "REAL_MAINNET", "CACHED_MAINNET"] = "FIXTURE"
    block_number: int | None = Field(default=None, ge=0)
    candidate_users: list[str] | None = Field(default=None, max_length=5_000)
    cached_snapshot_id: str | None = None


class ScenarioCreate(BaseModel):
    snapshot_id: str = "fixture-main-v1"
    name: str = Field(default="Professor Demo", min_length=1, max_length=100)
    shock_pct: Decimal = Field(default=Decimal("-20"), ge=-50, le=0)
    liquidity_haircut_pct: Decimal = Field(default=Decimal("40"), ge=0, le=95)
    gas_multiplier: Decimal = Field(default=Decimal("2"), gt=0, le=20)
    liquidator_capital_usdc: Decimal = Field(default=Decimal("10000000"), gt=0)
    liquidator_capacity_usdc: Decimal = Field(default=Decimal("2500000"), gt=0)
    liquidator_delay_steps: int = Field(default=0, ge=0, le=100)
    liquidator_min_profit_usdc: Decimal = Field(default=Decimal("0"), ge=0)
    arbitrage_capacity_pct: Decimal = Field(default=Decimal("50"), ge=0, le=100)
    arbitrage_delay_steps: int = Field(default=0, ge=0, le=100)
    horizon_steps: int = Field(default=12, ge=1, le=1000)
    timestep_seconds: int = Field(default=60, ge=1, le=86_400)
    monte_carlo_runs: int = Field(default=100, ge=1, le=10_000)
    seed: int = 20260914
    volatility_pct: Decimal = Field(default=Decimal("2"), ge=0, le=100)
    liquidation_bonus: Decimal = Field(default=Decimal("1.05"), ge=1, le=2)
    ltv_override: Decimal | None = Field(default=None, ge=0, le=1)
    liquidation_threshold_override: Decimal | None = Field(default=None, gt=0, le=1)
    liquidation_bonus_override: Decimal | None = Field(default=None, ge=1, le=2)
    max_waves: int = Field(default=12, ge=1, le=100)

    @field_validator("snapshot_id")
    @classmethod
    def nonempty_snapshot(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("snapshot_id is required")
        return value


class RunCreate(BaseModel):
    scenario_id: str
    mode: Literal["DETERMINISTIC", "MONTE_CARLO"] = "DETERMINISTIC"


class CompareRuns(BaseModel):
    run_ids: list[str] = Field(min_length=2, max_length=4)


class CascadeThresholdRequest(BaseModel):
    scenario_id: str


class ForkValidationRequest(BaseModel):
    snapshot_id: str | None = None
    borrower_hash: str | None = None


class ContagionNodeResponse(BaseModel):
    id: str
    label: str
    layer: str
    node_type: str
    evidence_status: str
    snapshot_id: str
    description: str
    raw_metrics: dict[str, float | int | str | None]
    provenance: dict[str, Any]


class ContagionEdgeResponse(BaseModel):
    id: str
    source: str
    target: str
    relation_type: str
    layer: str
    direction: str
    raw_value: dict[str, float | int | str | None]
    unit: str
    normalized_strength: float = Field(ge=0, le=1)
    evidence_status: str
    provenance: dict[str, Any]
    description: str
    formula: str
    active: bool
    step: int | None = None
    wave: int | None = None


class ContagionFrameResponse(BaseModel):
    index: int
    label: str
    wave: int
    step: int
    active_nodes: list[str]
    active_edge_ids: list[str]
    active_edges: list[ContagionEdgeResponse]
    price_state: dict[str, float | None]
    liquidation_volume_usd: float
    forced_weth: float
    liquidation_event_count: int
    cumulative_liquidated_debt_usd: float
    cascade_depth_so_far: int


class ContagionCentralityNodeResponse(BaseModel):
    in_degree_centrality: float
    out_degree_centrality: float
    betweenness_centrality: float
    eigenvector_centrality: float | None
    weighted_influence_strength: float


class ContagionCentralityResponse(BaseModel):
    aggregation_policy: str
    weighted_influence_interpretation: str
    nodes: dict[str, ContagionCentralityNodeResponse]
    structural_bridge_node: str | None
    eigenvector_unavailable_reason: str | None


class ContagionMatrixEdgeResponse(BaseModel):
    id: str
    relation_type: str
    raw_value: dict[str, float | int | str | None]
    unit: str
    evidence_status: str
    formula: str


class ContagionMatrixCellResponse(BaseModel):
    source: str
    target: str
    relation_types: list[str]
    raw_edges: list[ContagionMatrixEdgeResponse]
    max_normalized_strength: float = Field(ge=0, le=1)


class ContagionMatrixResponse(BaseModel):
    node_order: list[str]
    values: list[list[float]]
    cells: list[list[ContagionMatrixCellResponse]]
    metric: str
    aggregation_policy: str


class ContagionGraphResponse(BaseModel):
    graph_type: str
    graph_model_version: str
    simulation_model_version: str | None
    snapshot_id: str
    run_id: str | None
    scenario_id: str | None
    seed: int | None
    mode: str
    evidence_mode: str
    provenance: dict[str, Any]
    nodes: list[ContagionNodeResponse]
    edges: list[ContagionEdgeResponse]
    layers: list[str]
    relation_types: list[str]
    centrality: ContagionCentralityResponse
    contagion_matrix: ContagionMatrixResponse
    frames: list[ContagionFrameResponse]
    aggregate_summary: dict[str, Any] | None
    graph_metadata: dict[str, Any]
    claim_boundaries: list[str]


class TerraDatasetImportRequest(BaseModel):
    dataset_version: str = Field(min_length=1, max_length=96)
    status: Literal["REAL_HISTORICAL", "FIXTURE", "PARTIAL", "QUALITY_WARNING"]
    source_name: str = Field(min_length=1, max_length=160)
    source_type: str = Field(min_length=1, max_length=80)
    chain_id: str = "columbus-5"
    raw_reference: str = "api-import"
    observations: list[dict[str, Any]] = Field(min_length=1)


class TerraReplayRequest(BaseModel):
    dataset_version: str = "terra_fixture_v1"
    calibration_start: str = "2022-05-01T00:00:00Z"
    calibration_end: str = "2022-05-06T23:59:59Z"
    cutoff_timestamp: str = "2022-05-06T23:59:59Z"
    evaluation_start: str = "2022-05-07T00:00:00Z"
    evaluation_end: str = "2022-05-13T23:59:59Z"
    model_name: Literal["THRESHOLD", "HAZARD", "SYSTEM_DYNAMICS", "ABM"] = "ABM"
    mode: Literal["IN_SAMPLE_REPLAY", "OUT_OF_SAMPLE_REPLAY", "COUNTERFACTUAL_STRESS"] = "OUT_OF_SAMPLE_REPLAY"
    parameters: dict[str, Any] = Field(default_factory=dict)
    seed: int = 20220506


class TerraCounterfactualRequest(TerraReplayRequest):
    overrides: dict[str, Any] = Field(default_factory=lambda: {"price_impact_coefficient": 0.18})


class TerraSensitivityRequest(TerraReplayRequest):
    parameter: str = "reaction_delay_hours"
    values: list[float] = Field(default_factory=lambda: [0, 3, 6], min_length=1, max_length=20)


class TerraMonteCarloRequest(TerraReplayRequest):
    runs: int = Field(default=100, ge=1, le=10_000)


class TerraStressTestRequest(BaseModel):
    withdrawal_pressure: float = Field(default=1.0, ge=0.0, le=10.0)
    liquidity_capacity: float = Field(default=0.55, ge=0.0, le=5.0)
    arbitrage_capacity: float = Field(default=0.55, ge=0.0, le=5.0)
    confidence_sensitivity: float = Field(default=1.0, ge=0.0, le=10.0)
    outside_holder_exit: float = Field(default=0.004, ge=0.0, le=0.5)
    reserve_intervention: float = Field(default=0.0, ge=0.0, le=10.0)
    horizon_hours: int = Field(default=168, ge=1, le=720)
    initial_shock: float = Field(default=0.015, ge=0.0, le=0.9)
    redemption_friction: float = Field(default=0.02, ge=0.0, le=1.0)
    stress_start_timestamp: str = "2022-05-06T23:00:00Z"
    runs: int = Field(default=100, ge=1, le=1000)
    seed: int = 20220506
