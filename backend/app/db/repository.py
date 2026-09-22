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
    DataSnapshot,
    DexPoolRecord,
    DexTickRecord,
    ScenarioRecord,
    SimulationEventRecord,
    SimulationMetricRecord,
    SimulationRunRecord,
    ValidationRun,
)
from sim.schemas import json_safe


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
            rows = session.scalars(select(DataSnapshot).order_by(DataSnapshot.block_number.desc())).all()
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


def _position_hf(position: dict[str, Any], price: float) -> float:
    debt = float(position.get("debt_usdc", 0)) + float(position.get("other_debt_usd", 0))
    if debt <= 0:
        return 1e18
    collateral = float(position.get("collateral_weth", 0)) * price
    collateral += float(position.get("other_collateral_usd", 0))
    return collateral * float(position.get("liquidation_threshold", 0)) / debt
