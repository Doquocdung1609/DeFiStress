from __future__ import annotations

import json
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any

from backend.app.db import Repository
from backend.app.services.terra_datasets import import_research_dataset
from sim.terra.fixtures import FIXTURE_VERSION, terra_fixture_dataset
from sim.terra.replay import HistoricalReplayExperiment
from sim.terra.schemas import DataStatus, ExperimentMode


def common_replay_parser(description: str) -> ArgumentParser:
    parser = ArgumentParser(description=description)
    parser.add_argument("--dataset-version", default=FIXTURE_VERSION)
    parser.add_argument("--calibration-start", default="2022-05-01T00:00:00Z")
    parser.add_argument("--cutoff", default="2022-05-06T23:59:59Z")
    parser.add_argument("--evaluation-start", default="2022-05-07T00:00:00Z")
    parser.add_argument("--evaluation-end", default="2022-05-13T23:59:59Z")
    parser.add_argument("--seed", type=int, default=20220506)
    parser.add_argument("--database-url", default="sqlite:///./data/defi_stress.db")
    parser.add_argument("--output", type=Path)
    return parser


def experiment_from_args(args: Namespace, model_name: str = "ABM") -> HistoricalReplayExperiment:
    return HistoricalReplayExperiment(
        dataset_version=args.dataset_version,
        ground_truth_version=args.dataset_version,
        calibration_start=args.calibration_start,
        calibration_end=args.cutoff,
        cutoff_timestamp=args.cutoff,
        evaluation_start=args.evaluation_start,
        evaluation_end=args.evaluation_end,
        model_name=model_name,
        seed=args.seed,
        mode=ExperimentMode.OUT_OF_SAMPLE_REPLAY,
    )


def load_dataset(args: Namespace):
    if args.dataset_version == FIXTURE_VERSION:
        return terra_fixture_dataset()
    repository = Repository(args.database_url)
    dataset = repository.get_terra_dataset(args.dataset_version)
    if dataset is None:
        raise SystemExit(f"Dataset {args.dataset_version!r} was not found in {args.database_url}")
    return dataset


def write_json(path: Path | None, payload: dict[str, Any]) -> None:
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    if path is None:
        print(rendered)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {path}")
    path.write_text(rendered, encoding="utf-8")
    print(path)


def import_file(args: Namespace) -> dict[str, Any]:
    dataset = import_research_dataset(
        args.input,
        args.dataset_version,
        DataStatus(args.status),
        args.source_name,
        args.source_type,
        args.chain_id,
        args.raw_reference,
    )
    repository = Repository(args.database_url)
    repository.save_terra_dataset(dataset)
    return dataset.manifest.to_dict()
