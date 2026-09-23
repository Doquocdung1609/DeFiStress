from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from backend.app.adapters.terra.history import configured, historical, partial, unavailable
from backend.app.config import Settings, get_settings
from backend.app.db import Repository
from backend.app.schemas import (
    TerraCounterfactualRequest,
    TerraDatasetImportRequest,
    TerraMonteCarloRequest,
    TerraReplayRequest,
    TerraSensitivityRequest,
)
from backend.app.services.terra_datasets import dataset_from_rows
from backend.app.services.terra_export import build_terra_export
from sim.terra.experiments import run_ablation, run_benchmark, run_counterfactual, run_sensitivity
from sim.terra.fixtures import FIXTURE_VERSION, terra_fixture_dataset
from sim.terra.monte_carlo import run_terra_monte_carlo
from sim.terra.replay import HistoricalReplayExperiment, run_historical_replay
from sim.terra.schemas import DataStatus, ExperimentMode

router = APIRouter()


def terra_repository(settings: Settings = Depends(get_settings)) -> Repository:
    return Repository(settings.database_url)


def ensure_terra_fixture(repository: Repository) -> None:
    if repository.get_terra_dataset(FIXTURE_VERSION) is None:
        repository.save_terra_dataset(terra_fixture_dataset())


def _dataset_or_404(repository: Repository, dataset_version: str):
    ensure_terra_fixture(repository)
    dataset = repository.get_terra_dataset(dataset_version)
    if dataset is None:
        raise HTTPException(404, "Terra dataset not found")
    return dataset


def _preferred_historical_dataset(repository: Repository):
    """Return the strongest non-fixture Terra dataset currently stored."""

    manifests = repository.list_terra_datasets()
    priority = ("REAL_HISTORICAL", "PARTIAL", "QUALITY_WARNING")
    for wanted in priority:
        for manifest in manifests:
            if manifest.get("status") == wanted:
                dataset = repository.get_terra_dataset(str(manifest["dataset_version"]))
                if dataset is not None:
                    return dataset
    return None


def _historical_source_status(repository: Repository, settings: Settings) -> list[dict[str, Any]]:
    dataset = _preferred_historical_dataset(repository)
    dataset_status = dataset.manifest.status.value if dataset is not None else None
    dataset_version = dataset.manifest.dataset_version if dataset is not None else None
    source_manifest = dataset.manifest.source_manifest if dataset is not None else {}
    primary_source_type = str(source_manifest.get("primary", {}).get("source_type", "")).upper()

    if dataset is not None:
        reason = (
            f"Versioned dataset {dataset_version} is loaded with status {dataset_status}; "
            "use Data Provenance to inspect its manifest before citing it as evidence."
        )
        terra = (
            historical("Terra Classic historical data", reason)
            if dataset_status == "REAL_HISTORICAL"
            else partial("Terra Classic historical data", reason)
        )
    elif settings.terra_history_data_url or settings.terra_archive_lcd_url:
        terra = configured(
            "Terra Classic historical data",
            (
                "A Terra historical provider is configured. Ingest and validate a versioned dataset "
                "before treating it as evidence."
            ),
        )
    else:
        terra = unavailable(
            "Terra Classic historical data",
            "Set TERRA_HISTORY_DATA_URL or TERRA_ARCHIVE_LCD_URL, or import a verified CSV/JSON/Parquet dataset.",
        )

    has_curve = bool(
        dataset
        and ("curve" in source_manifest or "CURVE" in primary_source_type)
        and any(
            row.curve_ust_liquidity is not None
            or row.curve_pool_imbalance is not None
            or row.curve_ust_price is not None
            for row in dataset.observations
        )
    )
    if has_curve:
        reason = f"Curve fields are present in dataset {dataset_version} ({dataset_status})."
        curve = (
            historical("Ethereum archival RPC / Curve", reason)
            if dataset_status == "REAL_HISTORICAL"
            else partial("Ethereum archival RPC / Curve", reason)
        )
    elif settings.curve_history_data_url or settings.eth_archive_rpc_url:
        curve = configured(
            "Ethereum archival RPC / Curve",
            (
                "An Ethereum archive RPC or normalized Curve historical provider is configured; "
                "ingest Curve observations to attach historical evidence."
            ),
        )
    else:
        curve = unavailable(
            "Ethereum archival RPC / Curve",
            "Set ETH_ARCHIVE_RPC_URL or CURVE_HISTORY_DATA_URL if the Curve cross-chain channel is required.",
        )

    has_bridge = bool(
        dataset
        and ("bridge" in source_manifest or "BRIDGE" in primary_source_type)
        and any(
            row.bridge_outflow_terra_to_ethereum is not None or row.bridge_inflow_ethereum_to_terra is not None
            for row in dataset.observations
        )
    )
    if has_bridge:
        reason = f"Bridge-flow fields are present in dataset {dataset_version} ({dataset_status})."
        bridge = (
            historical("Bridge-flow indexer", reason)
            if dataset_status == "REAL_HISTORICAL"
            else partial("Bridge-flow indexer", reason)
        )
    elif settings.bridge_flow_data_url:
        bridge = configured(
            "Bridge-flow indexer",
            "A normalized bridge-flow provider is configured; ingest the observations before using them as evidence.",
        )
    else:
        bridge = unavailable(
            "Bridge-flow indexer",
            "Set BRIDGE_FLOW_DATA_URL or import a dataset containing bridge flow fields.",
        )

    return [terra.to_dict(), curve.to_dict(), bridge.to_dict()]


def _experiment(request: TerraReplayRequest) -> HistoricalReplayExperiment:
    return HistoricalReplayExperiment(
        dataset_version=request.dataset_version,
        ground_truth_version=request.dataset_version,
        calibration_start=request.calibration_start,
        calibration_end=request.calibration_end,
        cutoff_timestamp=request.cutoff_timestamp,
        evaluation_start=request.evaluation_start,
        evaluation_end=request.evaluation_end,
        model_name=request.model_name,
        parameters=request.parameters,
        seed=request.seed,
        mode=ExperimentMode(request.mode),
    )


@router.get("/case-studies")
def case_studies(repository: Repository = Depends(terra_repository)) -> list[dict[str, Any]]:
    return repository.list_case_studies()


@router.get("/terra/status")
def terra_status(
    repository: Repository = Depends(terra_repository),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    ensure_terra_fixture(repository)
    return {
        "case_study": "TERRA_2022",
        "default_cutoff": "2022-05-06T23:59:59Z",
        "default_evaluation": ["2022-05-07T00:00:00Z", "2022-05-13T23:59:59Z"],
        "datasets": repository.list_terra_datasets(),
        "historical_sources": _historical_source_status(repository, settings),
        "fixture_warning": "Synthetic fixture is available for software demonstration and is not historical evidence.",
    }


@router.post("/terra/datasets/import", status_code=status.HTTP_201_CREATED)
def import_terra_dataset(
    request: TerraDatasetImportRequest, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    try:
        dataset = dataset_from_rows(
            request.observations,
            request.dataset_version,
            DataStatus(request.status),
            request.source_name,
            request.source_type,
            request.chain_id,
            request.raw_reference,
        )
        return repository.save_terra_dataset(dataset)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.post("/terra/datasets/build")
def build_terra_dataset(
    repository: Repository = Depends(terra_repository),
    settings: Settings = Depends(get_settings),
) -> dict[str, Any]:
    ensure_terra_fixture(repository)
    existing = _preferred_historical_dataset(repository)
    if existing is not None:
        return {
            "status": existing.manifest.status.value,
            "reason": "A non-fixture historical dataset is already loaded.",
            "dataset_version": existing.manifest.dataset_version,
            "fixture_dataset": FIXTURE_VERSION,
            "import_formats": ["CSV", "Parquet", "JSON"],
        }

    if settings.terra_history_data_url:
        return {
            "status": "CONFIGURED",
            "reason": (
                "TERRA_HISTORY_DATA_URL is configured. Run scripts/terra/fetch_terra_history.py, "
                "validate the downloaded file, then import it."
            ),
            "fixture_dataset": FIXTURE_VERSION,
            "import_formats": ["CSV", "Parquet", "JSON"],
        }

    if settings.terra_archive_lcd_url:
        return {
            "status": "CONFIGURED",
            "reason": (
                "TERRA_ARCHIVE_LCD_URL is configured. Raw archival chain access is available, but a normalized "
                "research dataset must still be built/imported before replay."
            ),
            "fixture_dataset": FIXTURE_VERSION,
            "import_formats": ["CSV", "Parquet", "JSON"],
        }

    return {
        "status": "NEEDS_CONFIGURATION",
        "reason": "Configure TERRA_HISTORY_DATA_URL or TERRA_ARCHIVE_LCD_URL, or import a verified historical dataset.",
        "fixture_dataset": FIXTURE_VERSION,
        "import_formats": ["CSV", "Parquet", "JSON"],
    }


@router.get("/terra/datasets")
def terra_datasets(repository: Repository = Depends(terra_repository)) -> list[dict[str, Any]]:
    ensure_terra_fixture(repository)
    return repository.list_terra_datasets()


@router.get("/terra/timeseries")
def terra_timeseries(
    dataset_version: str = FIXTURE_VERSION,
    start: str | None = Query(default=None),
    end: str | None = Query(default=None),
    repository: Repository = Depends(terra_repository),
) -> dict[str, Any]:
    dataset = _dataset_or_404(repository, dataset_version)
    rows = dataset.observations
    if start and end:
        view = dataset.evaluation_view(start, end)
        allowed = set(view.timestamps)
        rows = tuple(row for row in rows if row.timestamp in allowed)
    return {"dataset": dataset.manifest.to_dict(), "observations": [row.to_dict() for row in rows]}


@router.get("/terra/wallet-cohorts")
def terra_wallet_cohorts(
    dataset_version: str = FIXTURE_VERSION, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    dataset = _dataset_or_404(repository, dataset_version)
    if dataset.manifest.status != DataStatus.FIXTURE:
        return {
            "status": "UNAVAILABLE",
            "reason": "Wallet-level/cohort source was not included in this dataset.",
            "cohorts": [],
        }
    latest = dataset.observations[-1]
    shares = {"WHALE": 0.23, "LARGE": 0.28, "MEDIUM": 0.31, "SMALL": 0.18}
    return {
        "status": "FIXTURE",
        "warning": "Synthetic cohort allocation for software demonstration only.",
        "cohorts": [
            {"cohort": name, "anchor_balance": float(latest.anchor_total_deposits) * share, "share": share}
            for name, share in shares.items()
        ],
    }


@router.post("/terra/replays", status_code=status.HTTP_201_CREATED)
def create_terra_replay(
    request: TerraReplayRequest, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    try:
        dataset = _dataset_or_404(repository, request.dataset_version)
        result = run_historical_replay(dataset, _experiment(request))
        replay_id = repository.save_terra_replay(request.dataset_version, result)
        return {"id": replay_id, "status": "COMPLETE", **result}
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


def _replay_or_404(repository: Repository, replay_id: str) -> dict[str, Any]:
    replay = repository.get_terra_replay(replay_id)
    if replay is None:
        raise HTTPException(404, "Terra replay not found")
    return replay


@router.get("/terra/replays/{replay_id}")
def get_terra_replay(replay_id: str, repository: Repository = Depends(terra_repository)) -> dict[str, Any]:
    return _replay_or_404(repository, replay_id)


@router.get("/terra/replays/{replay_id}/events")
def get_terra_replay_events(replay_id: str, repository: Repository = Depends(terra_repository)) -> list[dict[str, Any]]:
    return _replay_or_404(repository, replay_id).get("agent_events", [])


@router.get("/terra/replays/{replay_id}/timeseries")
def get_terra_replay_timeseries(replay_id: str, repository: Repository = Depends(terra_repository)) -> dict[str, Any]:
    replay = _replay_or_404(repository, replay_id)
    return {"simulated": replay["simulated_timeseries"], "ground_truth": replay["ground_truth_timeseries"]}


@router.get("/terra/replays/{replay_id}/metrics")
def get_terra_replay_metrics(replay_id: str, repository: Repository = Depends(terra_repository)) -> dict[str, Any]:
    return _replay_or_404(repository, replay_id)["validation_metrics"]


@router.post("/terra/benchmark", status_code=status.HTTP_201_CREATED)
def create_terra_benchmark(
    request: TerraReplayRequest, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    dataset = _dataset_or_404(repository, request.dataset_version)
    result = run_benchmark(dataset, _experiment(request))
    benchmark_id = repository.save_terra_benchmark(request.dataset_version, result)
    return {"id": benchmark_id, "status": "COMPLETE", **result}


@router.get("/terra/benchmark/{benchmark_id}")
def get_terra_benchmark(benchmark_id: str, repository: Repository = Depends(terra_repository)) -> dict[str, Any]:
    result = repository.get_terra_benchmark(benchmark_id)
    if result is None:
        raise HTTPException(404, "Terra benchmark not found")
    return result


@router.post("/terra/ablation", status_code=status.HTTP_201_CREATED)
def create_terra_ablation(
    request: TerraReplayRequest, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    dataset = _dataset_or_404(repository, request.dataset_version)
    result = run_ablation(dataset, _experiment(request))
    experiment_id = repository.save_terra_experiment(request.dataset_version, "ABLATION", result)
    return {"id": experiment_id, "status": "COMPLETE", **result}


@router.post("/terra/sensitivity", status_code=status.HTTP_201_CREATED)
def create_terra_sensitivity(
    request: TerraSensitivityRequest, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    dataset = _dataset_or_404(repository, request.dataset_version)
    result = run_sensitivity(dataset, _experiment(request), request.parameter, request.values)
    experiment_id = repository.save_terra_experiment(request.dataset_version, "SENSITIVITY", result)
    return {"id": experiment_id, "status": "COMPLETE", **result}


@router.post("/terra/counterfactual", status_code=status.HTTP_201_CREATED)
def create_terra_counterfactual(
    request: TerraCounterfactualRequest, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    dataset = _dataset_or_404(repository, request.dataset_version)
    result = run_counterfactual(dataset, _experiment(request), request.overrides)
    experiment_id = repository.save_terra_experiment(request.dataset_version, "COUNTERFACTUAL", result)
    return {"id": experiment_id, "status": "COMPLETE", **result}


@router.post("/terra/monte-carlo", status_code=status.HTTP_201_CREATED)
def create_terra_monte_carlo(
    request: TerraMonteCarloRequest, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    dataset = _dataset_or_404(repository, request.dataset_version)
    result = run_terra_monte_carlo(dataset, _experiment(request), request.runs)
    experiment_id = repository.save_terra_experiment(request.dataset_version, "MONTE_CARLO", result)
    return {"id": experiment_id, "status": "COMPLETE", **result}


@router.get("/terra/provenance")
def terra_provenance(
    dataset_version: str = FIXTURE_VERSION, repository: Repository = Depends(terra_repository)
) -> dict[str, Any]:
    dataset = _dataset_or_404(repository, dataset_version)
    return dataset.manifest.to_dict()


@router.get("/terra/export/{replay_id}")
def export_terra_replay(replay_id: str, repository: Repository = Depends(terra_repository)) -> Response:
    replay = _replay_or_404(repository, replay_id)
    payload = build_terra_export(replay)
    return Response(
        payload,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="terra-replay-{replay_id}.zip"'},
    )
