from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from backend.app.db.models import (
    AaveReserve,
    Base,
    BorrowerPositionRecord,
    DataQualityFlag,
    DatasetSourceRecord,
    DataSnapshot,
    DexPoolRecord,
    DexTickRecord,
    HistoricalReplayRecord,
    ModelBenchmarkRecord,
    ResearchCaseStudyRecord,
    ResearchDatasetVersionRecord,
    ScenarioRecord,
    SimulationEventRecord,
    SimulationMetricRecord,
    SimulationRunRecord,
    TerraExperimentRecord,
    TerraHourlyStateRecord,
    ValidationRun,
)
from sim.schemas import json_safe
from sim.terra.datasets import DatasetManifest, ResearchDataset
from sim.terra.schemas import DataStatus, TerraObservation, parse_utc


class Repository:
    def __init__(self, database_url: str):
        connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
        self.engine = create_engine(database_url, future=True, connect_args=connect_args)
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    def save_snapshot(self, snapshot: dict[str, Any]) -> dict[str, Any]:
        payload = json_safe(snapshot)
        with self.sessions.begin() as session:
            existing = session.get(DataSnapshot, str(payload["id"]))
            if existing:
                return existing.payload
            record = DataSnapshot(
                id=str(payload["id"]),
                mode=str(payload["mode"]),
                chain_id=int(payload["chain_id"]),
                block_number=int(payload["block_number"]),
                block_hash=str(payload["block_hash"]),
                block_timestamp=str(payload["block_timestamp"]),
                retrieved_at=str(payload["retrieved_at"]),
                source_manifest=payload["source_manifest"],
                payload=payload,
                immutable=True,
            )
            session.add(record)
            for reserve in payload.get("aave_reserves", []):
                session.add(AaveReserve(snapshot_id=record.id, asset=reserve["symbol"], payload=reserve))
            price = float(payload.get("oracle_prices", {}).get("WETH", 0))
            for position in payload.get("borrowers", []):
                hf = float(position.get("health_factor") or _position_hf(position, price))
                session.add(
                    BorrowerPositionRecord(
                        snapshot_id=record.id,
                        user_hash=position["borrower_hash"],
                        health_factor=hf,
                        payload=position,
                    )
                )
            pool = payload.get("dex_pool")
            pools = payload.get("dex_pools") or ([pool] if pool else [])
            for pool_row in pools:
                session.add(
                    DexPoolRecord(
                        snapshot_id=record.id,
                        pool_address=pool_row["pool_address"],
                        fee=int(pool_row["fee"]),
                        payload=pool_row,
                    )
                )
            for tick in payload.get("dex_ticks", []):
                session.add(
                    DexTickRecord(
                        snapshot_id=record.id,
                        pool_address=pool["pool_address"] if pool else "",
                        tick_idx=int(tick["tick"]),
                        liquidity_net=str(tick["liquidity_net"]),
                        liquidity_gross=str(tick["liquidity_gross"]),
                    )
                )
            for flag in payload.get("data_quality_flags", []):
                session.add(DataQualityFlag(snapshot_id=record.id, **flag))
        return payload

    def get_snapshot(self, snapshot_id: str) -> dict[str, Any] | None:
        with self.sessions() as session:
            record = session.get(DataSnapshot, snapshot_id)
            return record.payload if record else None

    def list_snapshots(self) -> list[dict[str, Any]]:
        with self.sessions() as session:
            rows = session.scalars(
                select(DataSnapshot).order_by(DataSnapshot.block_number.desc(), DataSnapshot.retrieved_at.desc())
            ).all()
            return [row.payload for row in rows]

    def save_scenario(self, snapshot_id: str, config: dict[str, Any]) -> dict[str, Any]:
        scenario_id = str(uuid4())
        payload = json_safe(config)
        with self.sessions.begin() as session:
            if session.get(DataSnapshot, snapshot_id) is None:
                raise KeyError("snapshot not found")
            session.add(ScenarioRecord(id=scenario_id, snapshot_id=snapshot_id, config_json=payload))
        return {"id": scenario_id, "snapshot_id": snapshot_id, "config": payload, "locked": False}

    def get_scenario(self, scenario_id: str) -> dict[str, Any] | None:
        with self.sessions() as session:
            row = session.get(ScenarioRecord, scenario_id)
            if not row:
                return None
            return {"id": row.id, "snapshot_id": row.snapshot_id, "config": row.config_json, "locked": row.locked}

    def list_scenarios(self) -> list[dict[str, Any]]:
        with self.sessions() as session:
            rows = session.scalars(select(ScenarioRecord).order_by(ScenarioRecord.created_at.desc())).all()
            return [
                {"id": r.id, "snapshot_id": r.snapshot_id, "config": r.config_json, "locked": r.locked} for r in rows
            ]

    def create_run(self, scenario_id: str, seed: int, model_version: str, status: str = "RUNNING") -> str:
        run_id = str(uuid4())
        with self.sessions.begin() as session:
            scenario = session.get(ScenarioRecord, scenario_id)
            if not scenario:
                raise KeyError("scenario not found")
            scenario.locked = True
            session.add(
                SimulationRunRecord(
                    id=run_id,
                    scenario_id=scenario_id,
                    seed=seed,
                    model_version=model_version,
                    status=status,
                    progress_percent=0 if status == "PENDING" else 10,
                )
            )
        return run_id

    def complete_run(self, run_id: str, result: dict[str, Any]) -> None:
        result = json_safe(result)
        with self.sessions.begin() as session:
            run = session.get(SimulationRunRecord, run_id)
            if not run or run.status == "COMPLETE":
                if run and run.status == "COMPLETE":
                    raise ValueError("completed runs are immutable")
                raise KeyError("run not found")
            run.status = "COMPLETE"
            run.progress_percent = 100
            run.ended_at = datetime.now(UTC).replace(tzinfo=None)
            run.result_json = result
            for event in result.get("events", []):
                session.add(
                    SimulationEventRecord(
                        run_id=run_id,
                        step=int(event["step"]),
                        wave=int(event["wave"]),
                        event_type=event["event_type"],
                        payload_json=event,
                    )
                )
            for metric, value in result.get("metrics", {}).items():
                session.add(
                    SimulationMetricRecord(
                        run_id=run_id,
                        metric=metric,
                        value=float(value) if isinstance(value, (int, float)) else None,
                    )
                )

    def update_run_progress(self, run_id: str, progress_percent: int) -> None:
        with self.sessions.begin() as session:
            run = session.get(SimulationRunRecord, run_id)
            if run and run.status in {"PENDING", "RUNNING"}:
                run.status = "RUNNING"
                run.progress_percent = max(0, min(99, progress_percent))

    def fail_run(self, run_id: str, message: str) -> None:
        with self.sessions.begin() as session:
            run = session.get(SimulationRunRecord, run_id)
            if run:
                run.status = "FAILED"
                run.error = message
                run.ended_at = datetime.now(UTC).replace(tzinfo=None)

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with self.sessions() as session:
            run = session.get(SimulationRunRecord, run_id)
            if not run:
                return None
            return {
                "id": run.id,
                "scenario_id": run.scenario_id,
                "seed": run.seed,
                "model_version": run.model_version,
                "status": run.status,
                "progress_percent": run.progress_percent,
                "result": run.result_json,
                "error": run.error,
            }

    def get_events(self, run_id: str) -> list[dict[str, Any]]:
        with self.sessions() as session:
            rows = session.scalars(
                select(SimulationEventRecord)
                .where(SimulationEventRecord.run_id == run_id)
                .order_by(SimulationEventRecord.step, SimulationEventRecord.id)
            ).all()
            return [row.payload_json for row in rows]

    def save_validation(self, snapshot_id: str | None, status: str, report: dict[str, Any]) -> dict[str, Any]:
        validation_id = str(uuid4())
        with self.sessions.begin() as session:
            session.add(ValidationRun(id=validation_id, snapshot_id=snapshot_id, status=status, report_json=report))
        return {"id": validation_id, "status": status, "report": report}

    def ensure_case_studies(self) -> None:
        cases = (
            (
                "terra-2022",
                "TerraUSD / LUNA — May 2022",
                "HISTORICAL_VALIDATION",
                {"chain": "Terra Classic", "purpose": "Out-of-sample historical replay and model benchmark"},
            ),
            (
                "aave-v3",
                "Aave V3 + Uniswap V3",
                "CONTEMPORARY_STRESS",
                {"chain": "Ethereum Mainnet", "purpose": "Contemporary counterfactual stress testing"},
            ),
        )
        with self.sessions.begin() as session:
            for case_id, name, case_type, payload in cases:
                if session.get(ResearchCaseStudyRecord, case_id) is None:
                    session.add(
                        ResearchCaseStudyRecord(id=case_id, name=name, case_type=case_type, payload_json=payload)
                    )

    def list_case_studies(self) -> list[dict[str, Any]]:
        self.ensure_case_studies()
        with self.sessions() as session:
            rows = session.scalars(select(ResearchCaseStudyRecord).order_by(ResearchCaseStudyRecord.id)).all()
            return [{"id": row.id, "name": row.name, "case_type": row.case_type, **row.payload_json} for row in rows]

    def save_terra_dataset(self, dataset: ResearchDataset) -> dict[str, Any]:
        manifest = dataset.manifest
        payload = manifest.to_dict()
        with self.sessions.begin() as session:
            existing = session.get(ResearchDatasetVersionRecord, manifest.dataset_version)
            if existing:
                if existing.dataset_hash != manifest.dataset_hash:
                    raise ValueError("dataset_version already exists with a different hash")
                return existing.manifest_json
            session.add(
                ResearchDatasetVersionRecord(
                    dataset_version=manifest.dataset_version,
                    case_study_id="terra-2022",
                    status=manifest.status.value,
                    dataset_hash=manifest.dataset_hash,
                    row_count=manifest.row_count,
                    start_timestamp=payload["start_timestamp"],
                    end_timestamp=payload["end_timestamp"],
                    manifest_json=payload,
                    quality_report_json=manifest.quality_report,
                )
            )
            primary = manifest.source_manifest.get("primary", {})
            session.add(
                DatasetSourceRecord(
                    dataset_version=manifest.dataset_version,
                    source_name=str(primary.get("source", "UNAVAILABLE")),
                    source_type=str(primary.get("priority", "UNAVAILABLE")),
                    chain_id=str(primary.get("chain", "columbus-5")),
                    quality_flag=manifest.status.value,
                    payload_json=manifest.source_manifest,
                )
            )
            for row in dataset.observations:
                row_payload = row.to_dict()
                session.add(
                    TerraHourlyStateRecord(
                        dataset_version=manifest.dataset_version,
                        timestamp=str(row_payload["timestamp"]),
                        block_height=row.block_height,
                        payload_json=row_payload,
                    )
                )
        return payload

    def get_terra_dataset(self, dataset_version: str) -> ResearchDataset | None:
        with self.sessions() as session:
            manifest_row = session.get(ResearchDatasetVersionRecord, dataset_version)
            if not manifest_row:
                return None
            rows = session.scalars(
                select(TerraHourlyStateRecord)
                .where(TerraHourlyStateRecord.dataset_version == dataset_version)
                .order_by(TerraHourlyStateRecord.timestamp)
            ).all()
            payload = manifest_row.manifest_json
            manifest = DatasetManifest(
                dataset_version=dataset_version,
                status=DataStatus(payload["status"]),
                row_count=int(payload["row_count"]),
                start_timestamp=parse_utc(payload["start_timestamp"]),
                end_timestamp=parse_utc(payload["end_timestamp"]),
                dataset_hash=str(payload["dataset_hash"]),
                source_manifest=dict(payload["source_manifest"]),
                quality_report=dict(payload["quality_report"]),
                transformation_version=str(payload["transformation_version"]),
                git_commit=str(payload["git_commit"]),
            )
            return ResearchDataset(manifest, tuple(TerraObservation.from_mapping(row.payload_json) for row in rows))

    def list_terra_datasets(self) -> list[dict[str, Any]]:
        with self.sessions() as session:
            rows = session.scalars(
                select(ResearchDatasetVersionRecord).order_by(ResearchDatasetVersionRecord.created_at.desc())
            ).all()
            return [row.manifest_json for row in rows]

    def save_terra_replay(self, dataset_version: str, result: dict[str, Any]) -> str:
        replay_id = str(uuid4())
        metadata = result["metadata"]
        with self.sessions.begin() as session:
            session.add(
                HistoricalReplayRecord(
                    id=replay_id,
                    dataset_version=dataset_version,
                    model_name=str(result["model"]["name"]),
                    experiment_mode=str(metadata["mode"]),
                    status="COMPLETE",
                    metadata_json=metadata,
                    result_json=json_safe(result),
                )
            )
        return replay_id

    def get_terra_replay(self, replay_id: str) -> dict[str, Any] | None:
        with self.sessions() as session:
            row = session.get(HistoricalReplayRecord, replay_id)
            if not row:
                return None
            return {"id": row.id, "status": row.status, **row.result_json}

    def save_terra_benchmark(self, dataset_version: str, result: dict[str, Any]) -> str:
        benchmark_id = str(uuid4())
        with self.sessions.begin() as session:
            session.add(
                ModelBenchmarkRecord(
                    id=benchmark_id, dataset_version=dataset_version, status="COMPLETE", result_json=json_safe(result)
                )
            )
        return benchmark_id

    def get_terra_benchmark(self, benchmark_id: str) -> dict[str, Any] | None:
        with self.sessions() as session:
            row = session.get(ModelBenchmarkRecord, benchmark_id)
            return None if not row else {"id": row.id, "status": row.status, **row.result_json}

    def save_terra_experiment(self, dataset_version: str, experiment_type: str, result: dict[str, Any]) -> str:
        experiment_id = str(uuid4())
        with self.sessions.begin() as session:
            session.add(
                TerraExperimentRecord(
                    id=experiment_id,
                    dataset_version=dataset_version,
                    experiment_type=experiment_type,
                    status="COMPLETE",
                    result_json=json_safe(result),
                )
            )
        return experiment_id

    def get_terra_experiment(self, experiment_id: str) -> dict[str, Any] | None:
        with self.sessions() as session:
            row = session.get(TerraExperimentRecord, experiment_id)
            if row is None:
                return None
            return {"id": row.id, "status": row.status, **row.result_json}

    def list_terra_experiments(
        self, limit: int = 30, experiment_types: tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        with self.sessions() as session:
            query = select(TerraExperimentRecord)
            if experiment_types is not None:
                query = query.where(TerraExperimentRecord.experiment_type.in_(experiment_types))
            rows = session.scalars(query.order_by(TerraExperimentRecord.created_at.desc()).limit(limit)).all()
            return [
                {"id": row.id, "status": row.status, "experiment_type": row.experiment_type,
                 "dataset_version": row.dataset_version, "created_at": row.created_at.isoformat() + "Z"}
                for row in rows
            ]


def _position_hf(position: dict[str, Any], price: float) -> float:
    debt = float(position.get("debt_usdc", 0)) + float(position.get("other_debt_usd", 0))
    if debt <= 0:
        return 1e18
    collateral = float(position.get("collateral_weth", 0)) * price
    collateral += float(position.get("other_collateral_usd", 0))
    return collateral * float(position.get("liquidation_threshold", 0)) / debt
