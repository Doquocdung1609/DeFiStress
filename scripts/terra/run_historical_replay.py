from __future__ import annotations

from _cli import common_replay_parser, experiment_from_args, load_dataset, write_json

from sim.terra.replay import run_historical_replay


def main() -> None:
    parser = common_replay_parser("Run a cutoff-safe Terra historical replay.")
    parser.add_argument("--model", default="ABM", choices=["THRESHOLD", "HAZARD", "SYSTEM_DYNAMICS", "ABM"])
    args = parser.parse_args()
    result = run_historical_replay(load_dataset(args), experiment_from_args(args, args.model))
    write_json(args.output, result)


if __name__ == "__main__":
    main()
