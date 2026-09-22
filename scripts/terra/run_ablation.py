from __future__ import annotations

from _cli import common_replay_parser, experiment_from_args, load_dataset, write_json

from sim.terra.experiments import run_ablation


def main() -> None:
    parser = common_replay_parser("Run Terra ABM mechanism ablations.")
    args = parser.parse_args()
    write_json(args.output, run_ablation(load_dataset(args), experiment_from_args(args)))


if __name__ == "__main__":
    main()
