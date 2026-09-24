from __future__ import annotations

import shutil
from copy import deepcopy
from dataclasses import asdict
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status

from backend.app.adapters.rpc import ReadOnlyRpcClient
from backend.app.config import Settings, get_settings
from backend.app.db import Repository
from backend.app.schemas import (
    CascadeThresholdRequest,
    CompareRuns,
    ForkValidationRequest,
    RunCreate,
    ScenarioCreate,
    SnapshotCreate,
)
from backend.app.services.export import build_experiment_zip
from backend.app.services.real_snapshot import create_real_snapshot
from backend.app.services.runs import execute_run, scenario_from_dict
from backend.app.services.snapshots import ensure_fixture_snapshot, simulation_inputs
from backend.app.terra_api import router as terra_router
from sim.dex import V3Pool
from sim.engine import MODEL_VERSION, find_cascade_threshold
from sim.presets import scenario_presets
from sim.schemas import json_safe

router = APIRouter(prefix="/api/v1")
router.include_router(terra_router)


def get_repository(settings: Settings = Depends(get_settings)) -> Repository:
    return Repository(settings.database_url)


@router.get("/health")
def health(settings: Settings = Depends(get_settings)) -> dict[str, Any]:
    if settings.eth_rpc_url:
        rpc = ReadOnlyRpcClient(settings.eth_rpc_url).health()
        ethereum = asdict(rpc)
    else:
        ethereum = {
            "connected": False,
            "chain_id": None,
            "current_block": None,
            "finalized_block": None,
            "block_lag": None,
            "latency_ms": None,
            "error": "ETH_RPC_URL is not configured; Fixture mode remains available.",
        }
    return {
        "service": "healthy",
        "mode": settings.app_mode,
        "safety_banner": "Research Simulation — Mainnet Read-Only",
        "ethereum_rpc": ethereum,
        "aave": "HEALTHY" if ethereum["connected"] else "UNAVAILABLE",
        "uniswap": "HEALTHY" if ethereum["connected"] else "UNAVAILABLE",
        "subgraph": "CONFIGURED" if settings.graph_api_key and settings.aave_v3_subgraph_id else "UNAVAILABLE",
        "can_create_real_snapshot": bool(
            ethereum["connected"]
            and ethereum["chain_id"] == 1
            and settings.graph_api_key
            and settings.aave_v3_subgraph_id
        ),
    }


@router.post("/snapshots", status_code=status.HTTP_201_CREATED)
def create_snapshot(
    request: SnapshotCreate,
    repository: Repository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    try:
        if request.mode == "FIXTURE":
            return ensure_fixture_snapshot(repository)
        if request.mode == "CACHED_MAINNET":
            if not request.cached_snapshot_id:
                raise ValueError("cached_snapshot_id is required for CACHED_MAINNET")
            cached = repository.get_snapshot(request.cached_snapshot_id)
            if not cached or cached.get("mode") not in {"REAL_MAINNET", "CACHED_MAINNET"}:
                raise ValueError("A cached real Mainnet snapshot was not found")
            cached_copy = deepcopy(cached)
            cached_copy["id"] = f"cached-{cached['id']}"
            cached_copy["mode"] = "CACHED_MAINNET"
            cached_copy["label"] = "Cached Mainnet Snapshot"
            cached_copy["source_manifest"].setdefault("application", {})["cached_from_snapshot_id"] = cached["id"]
            return repository.save_snapshot(cached_copy)
        snapshot = create_real_snapshot(settings, request.block_number, request.candidate_users)
        return repository.save_snapshot(snapshot)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/snapshots")
def list_snapshots(repository: Repository = Depends(get_repository)) -> list[dict[str, Any]]:
    ensure_fixture_snapshot(repository)
    return repository.list_snapshots()


def _snapshot_or_404(repository: Repository, snapshot_id: str) -> dict[str, Any]:
    snapshot = repository.get_snapshot(snapshot_id)
    if not snapshot:
        raise HTTPException(404, "Snapshot not found")
    return snapshot


@router.get("/snapshots/{snapshot_id}")
def get_snapshot(snapshot_id: str, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    return _snapshot_or_404(repository, snapshot_id)


@router.get("/snapshots/{snapshot_id}/market")
def get_market(snapshot_id: str, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    snapshot = _snapshot_or_404(repository, snapshot_id)
    return {
        "aave_market": snapshot["aave_market"],
        "reserves": snapshot["aave_reserves"],
        "oracle_prices": snapshot["oracle_prices"],
        "external_prices": snapshot["external_prices"],
        "stablecoin_state": snapshot["stablecoin_state"],
    }


@router.get("/snapshots/{snapshot_id}/positions")
def get_positions(snapshot_id: str, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    snapshot = _snapshot_or_404(repository, snapshot_id)
    positions, _, price = simulation_inputs(snapshot)
    debt_total = sum((position.debt_value() for position in positions), Decimal(0))
    rows = []
    for position in positions:
        hf = position.health_factor(price)
        rows.append(
            {
                **json_safe(position),
                "health_factor": float(hf),
                "liquidation_price": float(position.liquidation_price() or 0),
                "distance_to_liquidation": float(hf - 1) if hf.is_finite() else None,
                "total_debt": float(position.debt_value()),
                "debt_share": 0 if debt_total == 0 else float(position.debt_value() / debt_total),
            }
        )
    return {"positions": rows, "coverage": snapshot["coverage"]}


@router.get("/snapshots/{snapshot_id}/liquidity")
def get_liquidity(snapshot_id: str, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    snapshot = _snapshot_or_404(repository, snapshot_id)
    _, dex_state, _ = simulation_inputs(snapshot)
    pool = V3Pool(dex_state)
    return {
        "pool": snapshot["dex_pool"],
        "pools": snapshot.get("dex_pools", [snapshot["dex_pool"]]),
        "spot_price": float(pool.spot_price),
        "depth_usdc": {str(pct): float(pool.depth_to_price_drop_usdc(Decimal(pct))) for pct in ("1", "2", "5")},
        "quality_flags": [
            flag for flag in snapshot["data_quality_flags"] if "TICK" in flag["code"] or "POOL" in flag["code"]
        ],
    }


@router.post("/scenarios", status_code=status.HTTP_201_CREATED)
def create_scenario(request: ScenarioCreate, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    ensure_fixture_snapshot(repository)
    payload = request.model_dump(exclude={"snapshot_id"})
    scenario_from_dict(payload).validate()
    try:
        return repository.save_scenario(request.snapshot_id, payload)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc


@router.get("/scenarios")
def list_scenarios(repository: Repository = Depends(get_repository)) -> list[dict[str, Any]]:
    return repository.list_scenarios()


@router.get("/scenario-presets")
def list_scenario_presets() -> dict[str, Any]:
    return {name: json_safe(preset) for name, preset in scenario_presets().items()}


@router.post("/runs", status_code=status.HTTP_201_CREATED)
def create_run(
    request: RunCreate,
    background_tasks: BackgroundTasks,
    repository: Repository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    scenario = repository.get_scenario(request.scenario_id)
    if not scenario:
        raise HTTPException(404, "Scenario not found")
    config = scenario_from_dict(scenario["config"])
    run_id = repository.create_run(
        request.scenario_id,
        config.seed,
        MODEL_VERSION,
        status="PENDING" if request.mode == "MONTE_CARLO" else "RUNNING",
    )
    if request.mode == "MONTE_CARLO":
        if settings.async_backend.upper() == "CELERY":
            from backend.app.worker import execute_run_task

            execute_run_task.delay(run_id, request.mode)
        else:
            background_tasks.add_task(execute_run, repository, run_id, request.mode)
        return repository.get_run(run_id) or {}
    execute_run(repository, run_id, request.mode)
    return repository.get_run(run_id) or {}


def _run_or_404(repository: Repository, run_id: str) -> dict[str, Any]:
    run = repository.get_run(run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return run


@router.get("/runs/{run_id}")
def get_run(run_id: str, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    return _run_or_404(repository, run_id)


@router.get("/runs/{run_id}/events")
def get_events(run_id: str, repository: Repository = Depends(get_repository)) -> list[dict[str, Any]]:
    _run_or_404(repository, run_id)
    return repository.get_events(run_id)


@router.get("/runs/{run_id}/metrics")
def get_metrics(run_id: str, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    run = _run_or_404(repository, run_id)
    return (run.get("result") or {}).get("metrics", {})


@router.post("/runs/compare")
def compare_runs(request: CompareRuns, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    runs = [_run_or_404(repository, run_id) for run_id in request.run_ids]
    if any(run["status"] != "COMPLETE" for run in runs):
        raise HTTPException(409, "All compared runs must be COMPLETE")
    scenario_ids = [run["scenario_id"] for run in runs]
    scenarios = [repository.get_scenario(item) for item in scenario_ids]
    snapshots = {item["snapshot_id"] for item in scenarios if item}
    if len(snapshots) != 1:
        raise HTTPException(422, "Scenario comparison requires the same snapshot")
    baseline = runs[0]["result"]["metrics"]
    compared = []
    for run in runs:
        metrics = run["result"]["metrics"]
        delta = {
            key: None if value is None or baseline.get(key) is None else value - baseline[key]
            for key, value in metrics.items()
            if isinstance(value, (int, float))
        }
        compared.append(
            {
                "run_id": run["id"],
                "metrics": metrics,
                "delta_vs_first": delta,
                "timeseries": run["result"].get("timeseries", []),
            }
        )
    return {"snapshot_id": next(iter(snapshots)), "runs": compared}


@router.post("/analysis/cascade-threshold")
def cascade_threshold(
    request: CascadeThresholdRequest, repository: Repository = Depends(get_repository)
) -> dict[str, Any]:
    scenario_row = repository.get_scenario(request.scenario_id)
    if not scenario_row:
        raise HTTPException(404, "Scenario not found")
    snapshot = _snapshot_or_404(repository, scenario_row["snapshot_id"])
    positions, dex, price = simulation_inputs(snapshot)
    threshold = find_cascade_threshold(positions, dex, price, scenario_from_dict(scenario_row["config"]))
    return {
        "critical_shock_pct": None if threshold is None else float(-threshold),
        "cascade_definition": "cascade_depth >= 2",
    }


@router.post("/validate/fork")
def validate_fork(
    request: ForkValidationRequest,
    repository: Repository = Depends(get_repository),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    if request.snapshot_id:
        snapshot = _snapshot_or_404(repository, request.snapshot_id)
        if snapshot["mode"] == "FIXTURE":
            return repository.save_validation(
                request.snapshot_id, "UNAVAILABLE", {"reason": "Fork validation requires a real Mainnet snapshot."}
            )
    if not settings.eth_archive_rpc_url:
        return repository.save_validation(
            request.snapshot_id, "NOT_RUN_MISSING_ARCHIVE_RPC", {"reason": "ETH_ARCHIVE_RPC_URL is not configured."}
        )
    if not shutil.which("forge") or not shutil.which("anvil"):
        return repository.save_validation(
            request.snapshot_id, "NOT_RUN_MISSING_FOUNDRY", {"reason": "Foundry/Anvil executables are unavailable."}
        )
    return repository.save_validation(
        request.snapshot_id,
        "READY_LOCAL_ONLY",
        {"reason": "Harness prerequisites are present; run contracts/validation locally with an explicit sample."},
    )


@router.get("/runs/{run_id}/export")
def export_run(run_id: str, repository: Repository = Depends(get_repository)) -> Response:
    try:
        payload = build_experiment_zip(repository, run_id)
    except KeyError as exc:
        raise HTTPException(404, str(exc)) from exc
    return Response(
        payload,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="defi-stress-{run_id}.zip"'},
    )


@router.get("/provenance/{snapshot_id}")
def provenance(snapshot_id: str, repository: Repository = Depends(get_repository)) -> dict[str, Any]:
    snapshot = _snapshot_or_404(repository, snapshot_id)
    return {
        "snapshot_id": snapshot_id,
        "mode": snapshot["mode"],
        "block_number": snapshot["block_number"],
        "block_hash": snapshot["block_hash"],
        "sources": snapshot["source_manifest"],
        "quality_flags": snapshot["data_quality_flags"],
        "formulas": {
            "health_factor": "sum(collateral * price * liquidation_threshold) / sum(debt * price)",
            "cascade_amplification": "total liquidated debt / direct-shock liquidated debt",
            "bad_debt": "sum(max(remaining debt value - recoverable collateral value, 0))",
        },
    }
