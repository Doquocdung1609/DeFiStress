"""Pure synthetic economic valuation; not native Aave bytecode or historical replay."""

from __future__ import annotations

from defistress_v2.contracts import Blocked, ExplicitBool, Ok, Quarantined, Rejected, SourceKind
from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.contracts.evidence import OriginKind
from defistress_v2.contracts.state import Missing, Unsupported
from defistress_v2.contracts.valuation import (
    WAD,
    EconomicPriceClass,
    HealthFactorStatus,
    PriceObservation,
    PriceSet,
    ReserveValuation,
    RoundStatus,
    SyntheticPortfolio,
    ValuationContext,
    ValuationProfile,
    ValuationResult,
)

ROUNDING_PROFILE = "SYNTHETIC_ECONOMIC_FLOOR_COLLATERAL_CEIL_DEBT_V1"


def _ceil_div(numerator: int, denominator: int) -> int:
    return (numerator + denominator - 1) // denominator


def validate_price_observation(
    observation: PriceObservation,
    decision_at_s: int,
    *,
    require_native_freshness: bool = False,
) -> Ok[PriceObservation] | Blocked | Rejected:
    """Validate identity/source/time without promoting synthetic evidence to native evidence."""

    if type(observation) is not PriceObservation or type(decision_at_s) is not int or decision_at_s < 0:
        raise TypeContractError("price validation requires typed observation and nonnegative exact decision time")
    if type(require_native_freshness) is not bool:
        raise TypeContractError("require_native_freshness must be an exact bool")
    source_kind = observation.evidence.source_kind
    permitted = {
        EconomicPriceClass.HISTORICAL_AAVE_ORACLE_OBSERVATION: {
            SourceKind.ORACLE_ADAPTER,
            SourceKind.SYNTHETIC_FIXTURE,
        },
        EconomicPriceClass.DEX_OBSERVATION: {SourceKind.DEX_SPOT, SourceKind.SYNTHETIC_FIXTURE},
        EconomicPriceClass.COUNTERFACTUAL_POLICY: {SourceKind.SYNTHETIC_FIXTURE},
    }[observation.economic_class]
    if source_kind not in permitted:
        return Rejected(
            "ORACLE_SOURCE_CONFUSION",
            f"{observation.economic_class.value} cannot use {source_kind.value}",
            (observation.evidence,),
        )
    if observation.effective_at_s > decision_at_s or observation.available_at_s > decision_at_s:
        return Rejected(
            "TIMESTAMP_LEAKAGE",
            "price was not effective and available by the valuation decision",
            (observation.evidence,),
        )
    if observation.block_ref is not None:
        if (
            observation.block_ref.timestamp_s > decision_at_s
            or observation.block_ref.canonicality_observed_at_s > decision_at_s
        ):
            return Rejected(
                "TIMESTAMP_LEAKAGE",
                "bound block or its canonicality was not observed by the valuation decision",
                (observation.evidence,),
            )
        source_block = observation.evidence.block_ref
        if source_block is not None and (
            source_block.identity_key != observation.block_ref.identity_key
            or source_block.timestamp_s != observation.block_ref.timestamp_s
        ):
            return Rejected(
                "INPUT_IDENTITY_MISMATCH",
                "price evidence and observation block identities differ",
                (observation.evidence,),
            )
    source_block = observation.evidence.block_ref
    if (observation.block_ref is None) != (source_block is None):
        return Rejected(
            "INPUT_IDENTITY_MISMATCH",
            "price observation and evidence must have the same block-binding presence",
            (observation.evidence,),
        )
    rounds = tuple(
        round_value
        for round_value in (observation.native_round, observation.upstream_round)
        if round_value.status is RoundStatus.AVAILABLE
    )
    if any(round_value.updated_at_s is not None and round_value.updated_at_s > decision_at_s for round_value in rounds):
        return Rejected("TIMESTAMP_LEAKAGE", "oracle round update is in the future", (observation.evidence,))
    if len(rounds) == 2 and rounds[0].phase_id != rounds[1].phase_id:
        return Rejected("ORACLE_ROUND_MISMATCH", "native and upstream round phases differ", (observation.evidence,))
    if require_native_freshness:
        if observation.native_round.status is not RoundStatus.AVAILABLE:
            return Blocked(
                "ORACLE_ROUND_UNSUPPORTED",
                "native round metadata is unavailable and upstream metadata is not a substitute",
                (observation.evidence,),
            )
        if observation.heartbeat_s is None:
            return Blocked(
                "ORACLE_FRESHNESS_UNSPECIFIED",
                "native-use freshness requires an explicit heartbeat profile",
                (observation.evidence,),
            )
        updated = observation.native_round.updated_at_s
        assert updated is not None
        if decision_at_s - updated > observation.heartbeat_s:
            return Blocked("ORACLE_STALE", "native round exceeds its declared heartbeat", (observation.evidence,))
    return Ok(observation)


def value_portfolio(
    portfolio: SyntheticPortfolio,
    prices: PriceSet,
    context: ValuationContext,
) -> Ok[ValuationResult] | Blocked | Rejected:
    """Apply the authorized economic profile to a complete synthetic portfolio."""

    if (
        type(portfolio) is not SyntheticPortfolio
        or type(prices) is not PriceSet
        or type(context) is not ValuationContext
    ):
        raise TypeContractError("valuation inputs must use P02-03-S typed contracts")
    if context.profile is not ValuationProfile.SYNTHETIC_ECONOMIC_REFERENCE:
        return Blocked(
            "PROTOCOL_PROFILE_UNVERIFIED",
            "P02-03-S implements only the synthetic economic reference profile",
            (portfolio.fixture_evidence,),
        )
    if portfolio.fixture_evidence.origin is not OriginKind.SYNTHETIC:
        return Blocked(
            "HISTORICAL_VALUATION_NOT_AUTHORIZED",
            "P02-03-S accepts synthetic portfolio fixtures only",
            (portfolio.fixture_evidence,),
        )
    if (
        prices.checkpoint_id != context.checkpoint_id
        or prices.policy_id != context.policy_id
        or prices.profile_version != context.profile_version
    ):
        return Rejected(
            "VALUATION_CONTEXT_MISMATCH",
            "price set and valuation context do not share checkpoint, policy and profile identity",
            (portfolio.fixture_evidence,),
        )
    positions = {position.asset.identity_key: position for position in portfolio.positions}
    slots = {slot.asset.identity_key: slot for slot in prices.slots}
    if set(positions) != set(slots):
        return Blocked(
            "MISSING_PARTICIPATING_ASSET",
            "full portfolio participation requires one price slot for every reserve and no route-only subset",
            (portfolio.fixture_evidence,),
        )
    for identity, position in positions.items():
        slot_asset = slots[identity].asset
        if position.asset.decimals != slot_asset.decimals:
            return Rejected(
                "INPUT_IDENTITY_MISMATCH",
                "portfolio and price slot disagree on token decimals",
                (portfolio.fixture_evidence,),
            )
    reserve_values: list[ReserveValuation] = []
    total_collateral = 0
    total_debt = 0
    weighted_lt = 0
    counterfactual = False
    for position in portfolio.positions:
        state = slots[position.asset.identity_key].state
        if isinstance(state, Quarantined):
            return Rejected("PRICE_QUARANTINED", state.reason, state.refs)
        if isinstance(state, Missing):
            return Blocked("MISSING_PRICE_SOURCE", state.reason, state.refs)
        if isinstance(state, Unsupported):
            return Blocked("UNSUPPORTED_PRICE_SOURCE", state.reason, state.refs)
        assert isinstance(state, PriceObservation)
        validation = validate_price_observation(state, context.as_of_s)
        if not isinstance(validation, Ok):
            return validation
        if state.evidence.origin is not OriginKind.SYNTHETIC:
            return Blocked(
                "HISTORICAL_VALUATION_NOT_AUTHORIZED",
                "P02-03-S cannot compute against historical observations",
                (state.evidence,),
            )
        counterfactual = counterfactual or state.economic_class is EconomicPriceClass.COUNTERFACTUAL_POLICY
        scale = 10**position.asset.decimals
        supplied = int(position.supplied.raw_amount)
        stable = int(position.stable_debt.raw_amount)
        variable = int(position.variable_debt.raw_amount)
        collateral = supplied * state.raw_price // scale if position.collateral_enabled else 0
        debt = _ceil_div((stable + variable) * state.raw_price, scale)
        total_collateral += collateral
        total_debt += debt
        weighted_lt += collateral * position.effective_lt_bps
        reserve_values.append(
            ReserveValuation(
                asset=position.asset,
                supplied_raw=position.supplied.raw_amount,
                stable_debt_raw=position.stable_debt.raw_amount,
                variable_debt_raw=position.variable_debt.raw_amount,
                price_raw=state.raw_base_per_whole_token,
                collateral_base_raw=str(collateral),
                debt_base_raw=str(debt),
                effective_lt_bps=position.effective_lt_bps,
            )
        )
    if total_debt == 0:
        status = HealthFactorStatus.NO_DEBT
        health_factor_wad = None
        below_one = None
    else:
        status = HealthFactorStatus.FINITE_WAD
        health_factor = WAD * weighted_lt // (10_000 * total_debt)
        health_factor_wad = str(health_factor)
        below_one = ExplicitBool(health_factor < WAD)
    return Ok(
        ValuationResult(
            portfolio_id=portfolio.portfolio_id,
            context_hash=context.content_hash,
            portfolio_hash=portfolio.content_hash,
            price_set_hash=prices.content_hash,
            reserves=tuple(reserve_values),
            total_collateral_base_raw=str(total_collateral),
            total_debt_base_raw=str(total_debt),
            weighted_lt_numerator_raw=str(weighted_lt),
            debt_denominator_raw=str(10_000 * total_debt),
            health_factor_status=status,
            health_factor_wad=health_factor_wad,
            below_one=below_one,
            rounding_profile=ROUNDING_PROFILE,
            origin=OriginKind.COUNTERFACTUAL if counterfactual else OriginKind.SYNTHETIC,
        )
    )
