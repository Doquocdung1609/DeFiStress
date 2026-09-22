from dataclasses import replace
from decimal import Decimal

from sim.engine.run import run_simulation
from sim.schemas import BorrowerPosition, DexState, Scenario


def find_cascade_threshold(
    positions: list[BorrowerPosition],
    dex_state: DexState,
    initial_price: Decimal,
    base_scenario: Scenario,
    coarse_step_pct: Decimal = Decimal("1"),
    precision_pct: Decimal = Decimal("0.1"),
) -> Decimal | None:
    first: Decimal | None = None
    shock = Decimal(0)
    while shock <= Decimal(50):
        result = run_simulation(positions, dex_state, initial_price, replace(base_scenario, shock_pct=-shock))
        if int(result.metrics["cascade_depth"] or 0) >= 2:
            first = shock
            break
        shock += coarse_step_pct
    if first is None:
        return None
    low = max(Decimal(0), first - coarse_step_pct)
    high = first
    while high - low > precision_pct:
        midpoint = (low + high) / 2
        result = run_simulation(positions, dex_state, initial_price, replace(base_scenario, shock_pct=-midpoint))
        if int(result.metrics["cascade_depth"] or 0) >= 2:
            high = midpoint
        else:
            low = midpoint
    return high
