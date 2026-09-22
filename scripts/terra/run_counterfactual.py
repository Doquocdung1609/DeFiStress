from __future__ import annotations

from _cli import common_replay_parser, experiment_from_args, load_dataset, write_json

from sim.terra.experiments import run_counterfactual


def main() -> None:
    parser = common_replay_parser("Run a clearly labelled Terra counterfactual experiment.")
    parser.add_argument("--liquidity-impact", type=float, default=0.18)
    parser.add_argument("--reaction-delay-hours", type=int, default=6)
    parser.add_argument("--redemption-friction", type=float, default=0.02)
    args = parser.parse_args()
    overrides = {
        "price_impact_coefficient": args.liquidity_impact,
        "reaction_delay_hours": args.reaction_delay_hours,
        "redemption_friction": args.redemption_friction,
    }
    write_json(args.output, run_counterfactual(load_dataset(args), experiment_from_args(args), overrides))


if __name__ == "__main__":
    main()
