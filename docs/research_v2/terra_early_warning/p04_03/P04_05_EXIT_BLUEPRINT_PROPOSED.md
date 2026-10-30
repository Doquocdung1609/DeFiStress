# P04-05 exit-feasibility blueprint — PROPOSED / NOT RUN

A valid warning does not establish that an investor could withdraw or sell. No historical position, exit calculation, order, withdrawal or proceeds simulation is authorized in P04-03-S. This blueprint is conditional on a separately accepted alert/evaluation and explicit P04-05 execution scope.

Register intended account/venue/jurisdiction/access assumptions, custody/settlement asset, allowed routes and illustrative1,000/10,000/100,000UST positions before outcomes. Sizes are illustrative, not recovered investor holdings or recommended trades. The first admitted alert's issue time must be pinned with its input/config/profile lineage. Earliest potential order submission includes detection, communication, decision and transaction/withdrawal latency; execution additionally needs inclusion/queue/settlement and access constraints. Event/block time cannot substitute for actual observer or investor availability.

For CEX routes require timestamped executable bids/asks and depth, actual instrument identity, base/quote conversion, venue permissions, fees/spread, order-size limits, market/withdrawal halts, fill/partial-fill/cancel semantics and withdrawal delays. For DEX routes require historical canonical block/header/receipt/state, pool/token/ABI/code/decimals/amplification/fees, validated quote semantics, transaction ordering, gas/congestion, finality, route permissions and slippage limits. Liquidity depth and market impact must scale with the registered size; market volume, vendor VWAP and isolated swaps are not substitutes.

Future outputs should report per size/route action and execution intervals, executable/partial/unfilled quantities, net proceeds after fees/spread/gas/slippage/impact, quote age, assumptions and uncertainty bounds. Distinguish measured historical state from counterfactual access/latency assumptions. Sensitivity ranges must be registered and all infeasible/unknown cases retained, not tuned to produce an exit. Clock/availability/depth uncertainty must propagate; if defensible probability bounds do not exist, use explicit scenario bounds with no probability claim.

| State | Required future interpretation |
|---|---|
| `ALERT_DETECTED` | A valid admitted alert exists; no execution claim follows |
| `EXIT_FEASIBLE_UNDER_ASSUMPTIONS` | A separately validated route/depth/access/latency study supports the specified fill under the disclosed assumptions; no universal investor guarantee |
| `EXIT_NOT_FEASIBLE` | Verified restrictions or insufficient executable liquidity under the registered assumptions prevent the intended exit; partial fill/remainder disclosed |
| `NOT_VERIFIABLE` | Missing critical depth, access, state, delay or conversion evidence prevents a defensible conclusion; never replace it with an invented slippage estimate |

These are future study dispositions, not computed states in the warning package. Missing evidence takes precedence over a claim of feasibility. Independently reproduce input state, quote/receipt comparator, fee and latency handling, position units and uncertainty before accepting a result. Required current finding is **NOT_EXECUTED / NOT_VERIFIABLE**. Historical scoring and exit experiments remain unauthorized; source acquisition follows a separately bounded proposal. No promise is made that a real investor could have exited at a displayed price.
