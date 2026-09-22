from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class DataSnapshot(Base):
    __tablename__ = "data_snapshots"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    mode: Mapped[str] = mapped_column(String(32), index=True)
    chain_id: Mapped[int] = mapped_column(Integer)
    block_number: Mapped[int] = mapped_column(Integer, index=True)
    block_hash: Mapped[str] = mapped_column(String(80))
    block_timestamp: Mapped[str] = mapped_column(String(64))
    retrieved_at: Mapped[str] = mapped_column(String(64))
    source_manifest: Mapped[dict] = mapped_column(JSON)
    payload: Mapped[dict] = mapped_column(JSON)
    immutable: Mapped[bool] = mapped_column(Boolean, default=True)


class AaveReserve(Base):
    __tablename__ = "aave_reserves"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("data_snapshots.id"), index=True)
    asset: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (Index("ix_reserve_snapshot_asset", "snapshot_id", "asset", unique=True),)


class BorrowerPositionRecord(Base):
    __tablename__ = "borrower_positions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("data_snapshots.id"), index=True)
    user_hash: Mapped[str] = mapped_column(String(80), index=True)
    health_factor: Mapped[float] = mapped_column(Float)
    payload: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (Index("ix_position_snapshot_user", "snapshot_id", "user_hash", unique=True),)


class DexPoolRecord(Base):
    __tablename__ = "dex_pools"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("data_snapshots.id"), index=True)
    pool_address: Mapped[str] = mapped_column(String(80))
    fee: Mapped[int] = mapped_column(Integer)
    payload: Mapped[dict] = mapped_column(JSON)


class DexTickRecord(Base):
    __tablename__ = "dex_ticks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("data_snapshots.id"), index=True)
    pool_address: Mapped[str] = mapped_column(String(80))
    tick_idx: Mapped[int] = mapped_column(Integer)
    liquidity_net: Mapped[str] = mapped_column(String(96))
    liquidity_gross: Mapped[str] = mapped_column(String(96))


class PriceSeries(Base):
    __tablename__ = "price_series"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str | None] = mapped_column(ForeignKey("data_snapshots.id"), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(64))
    asset: Mapped[str] = mapped_column(String(32))
    timestamp: Mapped[str] = mapped_column(String(64))
    price: Mapped[str] = mapped_column(String(96))
    block_number: Mapped[int | None] = mapped_column(Integer, nullable=True)


class ScenarioRecord(Base):
    __tablename__ = "scenarios"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("data_snapshots.id"), index=True)
    config_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)


class SimulationRunRecord(Base):
    __tablename__ = "simulation_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    scenario_id: Mapped[str] = mapped_column(ForeignKey("scenarios.id"), index=True)
    seed: Mapped[int] = mapped_column(Integer)
    model_version: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(24), index=True)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    result_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class SimulationEventRecord(Base):
    __tablename__ = "simulation_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("simulation_runs.id"), index=True)
    step: Mapped[int] = mapped_column(Integer)
    wave: Mapped[int] = mapped_column(Integer)
    event_type: Mapped[str] = mapped_column(String(40), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON)


class SimulationMetricRecord(Base):
    __tablename__ = "simulation_metrics"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    run_id: Mapped[str] = mapped_column(ForeignKey("simulation_runs.id"), index=True)
    metric: Mapped[str] = mapped_column(String(80))
    value: Mapped[float | None] = mapped_column(Float, nullable=True)
    quantile: Mapped[str | None] = mapped_column(String(16), nullable=True)
    __table_args__ = (Index("ix_metric_run_name_quantile", "run_id", "metric", "quantile", unique=True),)


class ValidationRun(Base):
    __tablename__ = "validation_runs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    snapshot_id: Mapped[str | None] = mapped_column(ForeignKey("data_snapshots.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(40))
    report_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class DataQualityFlag(Base):
    __tablename__ = "data_quality_flags"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[str] = mapped_column(ForeignKey("data_snapshots.id"), index=True)
    code: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16))
    message: Mapped[str] = mapped_column(Text)


class ResearchCaseStudyRecord(Base):
    __tablename__ = "research_case_studies"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    case_type: Mapped[str] = mapped_column(String(48), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON)


class ResearchDatasetVersionRecord(Base):
    __tablename__ = "research_dataset_versions"
    dataset_version: Mapped[str] = mapped_column(String(96), primary_key=True)
    case_study_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    dataset_hash: Mapped[str] = mapped_column(String(80), unique=True)
    row_count: Mapped[int] = mapped_column(Integer)
    start_timestamp: Mapped[str] = mapped_column(String(64))
    end_timestamp: Mapped[str] = mapped_column(String(64))
    manifest_json: Mapped[dict] = mapped_column(JSON)
    quality_report_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class DatasetSourceRecord(Base):
    __tablename__ = "dataset_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version: Mapped[str] = mapped_column(ForeignKey("research_dataset_versions.dataset_version"), index=True)
    source_name: Mapped[str] = mapped_column(String(160))
    source_type: Mapped[str] = mapped_column(String(64))
    chain_id: Mapped[str] = mapped_column(String(64))
    quality_flag: Mapped[str] = mapped_column(String(32))
    payload_json: Mapped[dict] = mapped_column(JSON)


class TerraHourlyStateRecord(Base):
    __tablename__ = "terra_hourly_state"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version: Mapped[str] = mapped_column(ForeignKey("research_dataset_versions.dataset_version"), index=True)
    timestamp: Mapped[str] = mapped_column(String(64), index=True)
    block_height: Mapped[int] = mapped_column(Integer, index=True)
    payload_json: Mapped[dict] = mapped_column(JSON)
    __table_args__ = (Index("ix_terra_dataset_timestamp", "dataset_version", "timestamp", unique=True),)


class TerraWalletCohortRecord(Base):
    __tablename__ = "terra_wallet_cohorts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_version: Mapped[str] = mapped_column(ForeignKey("research_dataset_versions.dataset_version"), index=True)
    wallet_id_hash: Mapped[str] = mapped_column(String(96), index=True)
    cohort: Mapped[str] = mapped_column(String(24), index=True)
    payload_json: Mapped[dict] = mapped_column(JSON)


class HistoricalReplayRecord(Base):
    __tablename__ = "historical_replays"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_version: Mapped[str] = mapped_column(ForeignKey("research_dataset_versions.dataset_version"), index=True)
    model_name: Mapped[str] = mapped_column(String(64), index=True)
    experiment_mode: Mapped[str] = mapped_column(String(48), index=True)
    status: Mapped[str] = mapped_column(String(24), index=True)
    metadata_json: Mapped[dict] = mapped_column(JSON)
    result_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class ModelBenchmarkRecord(Base):
    __tablename__ = "model_benchmarks"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_version: Mapped[str] = mapped_column(ForeignKey("research_dataset_versions.dataset_version"), index=True)
    status: Mapped[str] = mapped_column(String(24), index=True)
    result_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class TerraExperimentRecord(Base):
    __tablename__ = "terra_experiments"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    dataset_version: Mapped[str] = mapped_column(ForeignKey("research_dataset_versions.dataset_version"), index=True)
    experiment_type: Mapped[str] = mapped_column(String(48), index=True)
    status: Mapped[str] = mapped_column(String(24), index=True)
    result_json: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
