from __future__ import annotations

import json

from sim import Scenario, run_simulation
from sim.fixtures import FIXTURE_PRICE, fixture_dex, fixture_positions
from sim.schemas import json_safe


def main() -> None:
    result = run_simulation(fixture_positions(), fixture_dex(), FIXTURE_PRICE, Scenario())
    print("MODE: FIXTURE - synthetic deterministic data, not Mainnet")
    print(json.dumps(json_safe(result.metrics), indent=2, sort_keys=True))
    waves = sorted({event.wave for event in result.events if event.event_type == "LIQUIDATION"})
    print(f"Liquidation waves: {waves or 'No endogenous cascade detected.'}")


if __name__ == "__main__":
    main()
