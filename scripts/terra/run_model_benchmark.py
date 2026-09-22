from __future__ import annotations

from _cli import common_replay_parser, experiment_from_args, load_dataset, write_json

from sim.terra.experiments import run_benchmark


def main() -> None:
    parser = common_replay_parser("Run Threshold, Hazard, System Dynamics, and ABM benchmarks.")
    args = parser.parse_args()
    write_json(args.output, run_benchmark(load_dataset(args), experiment_from_args(args)))


if __name__ == "__main__":
    main()
