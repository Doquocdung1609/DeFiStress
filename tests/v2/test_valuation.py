"""P02-03-S synthetic oracle/valuation vectors; no historical portfolio execution."""

from __future__ import annotations

import dataclasses

import pytest

from defistress_v2.contracts import (
    ArtifactBytesSha256,
    AssetId,
    Blocked,
    DeterministicContentSha256,
    EvidenceRef,
    Missing,
    Ok,
    OriginKind,
    QuantityKind,
    Quarantined,
    Rejected,
    SourceKind,
    UnsignedAmount,
    Unsupported,
)
from defistress_v2.contracts.errors import ContractError
from defistress_v2.contracts.valuation import (
    WAD,
    BaseUnit,
    BlockRef,
    EconomicPriceClass,
    HealthFactorStatus,
    PriceObservation,
    PriceSet,
    PriceSlot,
    ReservePosition,
    RoundMetadata,
    RoundStatus,
    SyntheticPortfolio,
    ValuationContext,
    ValuationProfile,
    ValuationPurpose,
)
from defistress_v2.valuation import (
    CompletedDexObservation,
    CounterfactualPolicyState,
    InitializationLabel,
    PolicyConfig,
    PolicyKind,
    Rational,
    RationalPrice,
    advance_policy,
    policy_a,
    policy_b,
    policy_c_moderate,
    policy_c_weak,
    reporting_price,
    validate_price_observation,
    value_portfolio,
)

WETH = AssetId(1, "0x" + "11" * 20, 18, "synthetic:weth-decimals", "WETH")
USDC = AssetId(1, "0x" + "22" * 20, 6, "synthetic:usdc-decimals", "USDC")
TOY_COLLATERAL = AssetId(1, "0x" + "33" * 20, 0, "synthetic:collateral-decimals", "COLL")
TOY_DEBT = AssetId(1, "0x" + "44" * 20, 0, "synthetic:debt-decimals", "DEBT")
USD8 = BaseUnit("USD", 8, "USD_1E8", "synthetic:usd-scale")
FIXTURE = EvidenceRef.synthetic("p02-03", b"p02-03-synthetic-fixture", retrieved_at_s=1)
UNSUPPORTED_ROUND = RoundMetadata(RoundStatus.UNSUPPORTED, reason="synthetic interface does not expose round data")
MISSING_ROUND = RoundMetadata(RoundStatus.MISSING, reason="synthetic round evidence absent")
AVAILABLE_ROUND = RoundMetadata(RoundStatus.AVAILABLE, 1, 10, 90, 10)


def amount(asset: AssetId, raw: int, kind: QuantityKind) -> UnsignedAmount:
    return UnsignedAmount.from_int(asset, raw, kind)


def position(
    asset: AssetId,
    *,
    supplied: int = 0,
    debt: int = 0,
    enabled: bool = False,
    lt: int = 0,
    ltv: int = 0,
    bonus: int = 10_000,
) -> ReservePosition:
    return ReservePosition(
        asset,
        amount(asset, supplied, QuantityKind.COLLATERAL),
        amount(asset, 0, QuantityKind.DEBT),
        amount(asset, debt, QuantityKind.DEBT),
        enabled,
        lt,
        ltv,
        bonus,
    )


def price(
    asset: AssetId,
    raw: int,
    *,
    economic_class: EconomicPriceClass = EconomicPriceClass.HISTORICAL_AAVE_ORACLE_OBSERVATION,
    evidence: EvidenceRef = FIXTURE,
    effective: int = 90,
    available: int = 90,
    native_round: RoundMetadata = UNSUPPORTED_ROUND,
    upstream_round: RoundMetadata = AVAILABLE_ROUND,
    heartbeat: int | None = None,
    base: BaseUnit = USD8,
    block_ref: BlockRef | None = None,
) -> PriceObservation:
    return PriceObservation(
        f"synthetic:{asset.symbol}:{raw}",
        asset,
        base,
        str(raw),
        economic_class,
        evidence,
        effective,
        available,
        block_ref,
        "synthetic:config",
        "synthetic:adapter",
        native_round,
        upstream_round,
        heartbeat,
    )


def price_set(*observations: PriceObservation, policy_id: str = "A") -> PriceSet:
    return PriceSet(
        "synthetic:prices",
        "checkpoint-1",
        USD8,
        tuple(PriceSlot(item.asset, item) for item in observations),
        policy_id,
        "SYNTHETIC_ECONOMIC_REFERENCE_V1",
    )


def context(
    policy_id: str = "A", *, purpose: ValuationPurpose = ValuationPurpose.ELIGIBILITY_CHECKPOINT
) -> ValuationContext:
    return ValuationContext(
        "synthetic:context",
        "checkpoint-1",
        100,
        purpose,
        ValuationProfile.SYNTHETIC_ECONOMIC_REFERENCE,
        "SYNTHETIC_ECONOMIC_REFERENCE_V1",
        policy_id,
        ("economic floor/ceil profile", "resolved LT is explicit synthetic input"),
    )


def portfolio(*positions: ReservePosition) -> SyntheticPortfolio:
    return SyntheticPortfolio("synthetic:portfolio", tuple(positions), FIXTURE)


def unwrap(result: object) -> object:
    assert isinstance(result, Ok)
    return result.payload


def test_v03_01_unit_consistent_economic_hf() -> None:
    result = unwrap(
        value_portfolio(
            portfolio(
                position(WETH, supplied=2 * 10**18, enabled=True, lt=8000, ltv=7500),
                position(USDC, debt=1000 * 10**6),
            ),
            price_set(price(WETH, 2000 * USD8.scale), price(USDC, USD8.scale)),
            context(),
        )
    )
    assert result.total_collateral_base_raw == str(4000 * USD8.scale)
    assert result.total_debt_base_raw == str(1000 * USD8.scale)
    assert result.health_factor_wad == str(3_200_000_000_000_000_000)
    assert result.below_one.value is False


def test_v03_02_usdc_price_changes_valuation_not_token_quantity() -> None:
    positions = portfolio(
        position(WETH, supplied=2 * 10**18, enabled=True, lt=8000),
        position(USDC, debt=1000 * 10**6),
    )
    depeg = price(
        USDC,
        80_000_000,
        economic_class=EconomicPriceClass.COUNTERFACTUAL_POLICY,
    )
    result = unwrap(value_portfolio(positions, price_set(price(WETH, 2000 * USD8.scale), depeg), context()))
    usdc_row = next(row for row in result.reserves if row.asset.identity_key == USDC.identity_key)
    assert usdc_row.variable_debt_raw == str(1000 * 10**6)
    assert usdc_row.debt_base_raw == str(800 * USD8.scale)
    assert result.health_factor_wad == str(4 * WAD)
    assert result.origin is OriginKind.COUNTERFACTUAL


@pytest.mark.parametrize(("debt", "expected_relation"), [(79, 1), (80, 0), (81, -1)])
def test_v03_03_hf_threshold_uses_exact_wad_boundary(debt: int, expected_relation: int) -> None:
    result = unwrap(
        value_portfolio(
            portfolio(
                position(TOY_COLLATERAL, supplied=100, enabled=True, lt=8000),
                position(TOY_DEBT, debt=debt),
            ),
            price_set(price(TOY_COLLATERAL, USD8.scale), price(TOY_DEBT, USD8.scale)),
            context(),
        )
    )
    hf = int(result.health_factor_wad)
    assert (hf > WAD) - (hf < WAD) == expected_relation
    assert result.below_one.value is (expected_relation < 0)


def test_v03_04_zero_debt_is_tagged_without_infinity_or_eligibility() -> None:
    result = unwrap(
        value_portfolio(
            portfolio(position(WETH, supplied=10**18, enabled=True, lt=8000)),
            price_set(price(WETH, 2000 * USD8.scale)),
            context(),
        )
    )
    assert result.health_factor_status is HealthFactorStatus.NO_DEBT
    assert result.health_factor_wad is None
    assert result.below_one is None


def test_v03_04_missing_debt_asset_price_blocks_instead_of_inferring_zero() -> None:
    missing = Missing("required liability price absent", (FIXTURE,))
    prices = PriceSet(
        "synthetic:missing",
        "checkpoint-1",
        USD8,
        (PriceSlot(WETH, price(WETH, 2000 * USD8.scale)), PriceSlot(USDC, missing)),
        "A",
        "SYNTHETIC_ECONOMIC_REFERENCE_V1",
    )
    result = value_portfolio(
        portfolio(position(WETH, supplied=10**18, enabled=True, lt=8000), position(USDC, debt=1)),
        prices,
        context(),
    )
    assert isinstance(result, Blocked)
    assert result.code == "MISSING_PRICE_SOURCE"


def test_unsupported_price_state_remains_distinct_from_missing() -> None:
    unsupported = Unsupported("price", "source semantics not supported", (FIXTURE,))
    prices = PriceSet(
        "synthetic:unsupported",
        "checkpoint-1",
        USD8,
        (PriceSlot(WETH, unsupported),),
        "A",
        "SYNTHETIC_ECONOMIC_REFERENCE_V1",
    )

    result = value_portfolio(portfolio(position(WETH, debt=1)), prices, context())

    assert isinstance(result, Blocked)
    assert result.code == "UNSUPPORTED_PRICE_SOURCE"


def test_v03_05_declared_floor_and_ceil_rounding() -> None:
    toy = AssetId(1, "0x" + "55" * 20, 2, "synthetic:toy-decimals", "TOY")
    result = unwrap(
        value_portfolio(
            portfolio(position(toy, supplied=1, debt=1, enabled=True, lt=8000)),
            price_set(price(toy, 33)),
            context(),
        )
    )
    assert result.reserves[0].collateral_base_raw == "0"
    assert result.reserves[0].debt_base_raw == "1"
    assert result.health_factor_wad == "0"


def test_v03_06_ltv_and_bonus_do_not_enter_hf_formula() -> None:
    base = position(WETH, supplied=10**18, enabled=True, lt=8000, ltv=5000, bonus=10_500)
    changed = dataclasses.replace(base, ltv_bps=1000, liquidation_bonus_bps=12_000)
    debt = position(USDC, debt=1000 * 10**6)
    prices = price_set(price(WETH, 2000 * USD8.scale), price(USDC, USD8.scale))
    first = unwrap(value_portfolio(portfolio(base, debt), prices, context()))
    second = unwrap(value_portfolio(portfolio(changed, debt), prices, context()))
    assert first.health_factor_wad == second.health_factor_wad


def rational_price(value: int) -> RationalPrice:
    return RationalPrice.from_int(WETH, USD8, value)


def dex(
    sequence: int, value: int, *, completed: int | None = None, available: int | None = None
) -> CompletedDexObservation:
    completed_at = 10 + sequence if completed is None else completed
    available_at = completed_at if available is None else available
    return CompletedDexObservation(sequence, completed_at, available_at, rational_price(value), FIXTURE)


def policy_state(config: PolicyConfig, history: tuple[CompletedDexObservation, ...] = ()) -> CounterfactualPolicyState:
    ref = rational_price(100)
    return CounterfactualPolicyState(
        "synthetic:state",
        "checkpoint-0",
        config,
        ref,
        history,
        ref,
        DeterministicContentSha256.from_payload({"checkpoint": "0"}),
        FIXTURE,
        20,
    )


@pytest.mark.parametrize(
    ("config", "expected"),
    [(policy_a(), 60), (policy_b(), 100), (policy_c_weak(), 95), (policy_c_moderate(), 85)],
)
def test_v03_07_counterfactual_policy_reference_vectors(config: PolicyConfig, expected: int) -> None:
    state = policy_state(config, (dex(0, 100), dex(1, 80), dex(2, 60)))
    update = unwrap(advance_policy(state, rational_price(100), (), checkpoint_id="checkpoint-1", decision_at_s=20))
    assert update.valuation_price.value.fraction == expected
    assert state.checkpoint_id == "checkpoint-0"
    assert update.state is not state


@pytest.mark.parametrize(
    ("lag", "expected", "label"),
    [(3, 100, InitializationLabel.COMPLETED_HISTORY), (4, 100, InitializationLabel.MODEL_DEFINED_INITIALIZATION)],
)
def test_v03_08_lag_and_initialization_are_explicit(lag: int, expected: int, label: InitializationLabel) -> None:
    config = PolicyConfig("C_CUSTOM", PolicyKind.C_LAGGED_SMOOTHED_PROXY, Rational("1", "2"), lag, 3)
    state = policy_state(config, (dex(0, 100), dex(1, 80), dex(2, 60)))
    update = unwrap(advance_policy(state, rational_price(100), (), checkpoint_id="checkpoint-1", decision_at_s=20))
    assert update.valuation_price.value.fraction == expected
    assert update.initialization is label


@pytest.mark.parametrize(("config", "expected"), [(policy_a(), 70), (policy_b(), 100), (policy_c_weak(), 95)])
def test_v03_09_reporting_price_preserves_frozen_eligibility_context(config: PolicyConfig, expected: int) -> None:
    state = dataclasses.replace(policy_state(config), frozen_eligibility_price=rational_price(95))
    before = state.eligibility_context_hash
    result = unwrap(reporting_price(state, rational_price(100), dex(0, 70), reporting_at_s=20))
    assert result.price.value.fraction == expected
    assert result.eligibility_context_hash == before == state.eligibility_context_hash


def test_v03_10_dex_evidence_cannot_masquerade_as_aave_oracle() -> None:
    observed_dex = EvidenceRef(
        "dex:evidence",
        OriginKind.OBSERVED,
        SourceKind.DEX_SPOT,
        "1" * 40,
        "synthetic/dex.json",
        "/price",
        "synthetic/1",
        "TEST_ONLY",
        100,
        ArtifactBytesSha256.from_bytes(b"dex"),
    )
    result = validate_price_observation(price(WETH, 100, evidence=observed_dex), 100)
    assert isinstance(result, Rejected)
    assert result.code == "ORACLE_SOURCE_CONFUSION"


def test_price_evidence_and_observation_block_must_match() -> None:
    first = BlockRef(1, 1, "0x" + "aa" * 32, 80, "canonical:1", 90)
    second = BlockRef(1, 2, "0x" + "bb" * 32, 81, "canonical:2", 90)
    oracle_evidence = EvidenceRef(
        "oracle:evidence",
        OriginKind.OBSERVED,
        SourceKind.ORACLE_ADAPTER,
        "1" * 40,
        "synthetic/oracle.json",
        "/price",
        "synthetic/1",
        "TEST_ONLY",
        100,
        ArtifactBytesSha256.from_bytes(b"oracle"),
        block_ref=first,
    )
    result = validate_price_observation(price(WETH, 100, evidence=oracle_evidence, block_ref=second), 100)
    assert isinstance(result, Rejected)
    assert result.code == "INPUT_IDENTITY_MISMATCH"


def test_v03_10_future_price_is_rejected_without_lookahead() -> None:
    result = validate_price_observation(price(WETH, 100, effective=101, available=102), 100)
    assert isinstance(result, Rejected)
    assert result.code == "TIMESTAMP_LEAKAGE"


def test_v03_10_upstream_round_does_not_replace_unsupported_native_round() -> None:
    result = validate_price_observation(price(WETH, 100), 100, require_native_freshness=True)
    assert isinstance(result, Blocked)
    assert result.code == "ORACLE_ROUND_UNSUPPORTED"


def test_native_freshness_requires_heartbeat_and_enforces_staleness() -> None:
    unknown = validate_price_observation(
        price(WETH, 100, native_round=AVAILABLE_ROUND), 100, require_native_freshness=True
    )
    assert isinstance(unknown, Blocked)
    assert unknown.code == "ORACLE_FRESHNESS_UNSPECIFIED"
    stale = validate_price_observation(
        price(WETH, 100, native_round=AVAILABLE_ROUND, heartbeat=5),
        100,
        require_native_freshness=True,
    )
    assert isinstance(stale, Blocked)
    assert stale.code == "ORACLE_STALE"


def test_native_and_upstream_round_phase_mismatch_is_rejected() -> None:
    native = RoundMetadata(RoundStatus.AVAILABLE, 2, 10, 90, 10)
    result = validate_price_observation(price(WETH, 100, native_round=native), 100)
    assert isinstance(result, Rejected)
    assert result.code == "ORACLE_ROUND_MISMATCH"


def test_quarantined_price_rejects_dependent_valuation() -> None:
    prices = PriceSet(
        "synthetic:quarantine",
        "checkpoint-1",
        USD8,
        (PriceSlot(WETH, Quarantined("digest mismatch", (FIXTURE,))),),
        "A",
        "SYNTHETIC_ECONOMIC_REFERENCE_V1",
    )
    result = value_portfolio(portfolio(position(WETH, debt=1)), prices, context())
    assert isinstance(result, Rejected)
    assert result.code == "PRICE_QUARANTINED"


def test_route_only_price_set_is_blocked_by_full_participation_guard() -> None:
    result = value_portfolio(
        portfolio(position(WETH, supplied=1, enabled=True, lt=8000), position(USDC, debt=1)),
        price_set(price(WETH, 100)),
        context(),
    )
    assert isinstance(result, Blocked)
    assert result.code == "MISSING_PARTICIPATING_ASSET"


def test_historical_evidence_is_structurally_checked_but_not_valued_by_s_slice() -> None:
    observed_oracle = EvidenceRef(
        "oracle:historical",
        OriginKind.OBSERVED,
        SourceKind.ORACLE_ADAPTER,
        "1" * 40,
        "synthetic/oracle.json",
        "/price",
        "synthetic/1",
        "STRUCTURAL_TEST_ONLY",
        100,
        ArtifactBytesSha256.from_bytes(b"historical-oracle"),
    )
    result = value_portfolio(
        portfolio(position(WETH, debt=1)),
        price_set(price(WETH, 100, evidence=observed_oracle)),
        context(),
    )
    assert isinstance(result, Blocked)
    assert result.code == "HISTORICAL_VALUATION_NOT_AUTHORIZED"


def test_policy_future_observation_is_rejected_and_parent_state_is_unchanged() -> None:
    state = policy_state(policy_a(), (dex(0, 100),))
    parent_hash = state.content_hash
    result = advance_policy(
        state,
        rational_price(100),
        (dex(1, 80, completed=21, available=22),),
        checkpoint_id="checkpoint-1",
        decision_at_s=20,
    )
    assert isinstance(result, Rejected)
    assert result.code == "TIMESTAMP_LEAKAGE"
    assert state.content_hash == parent_hash


def test_frozen_policy_state_rejects_future_or_unseeded_history() -> None:
    with pytest.raises(ContractError, match="look-ahead"):
        dataclasses.replace(policy_state(policy_a(), (dex(0, 100),)), eligibility_as_of_s=9)
    with pytest.raises(ContractError, match="sequence zero"):
        policy_state(policy_a(), (dex(1, 100),))


def test_reporting_cannot_precede_frozen_checkpoint() -> None:
    state = policy_state(policy_b())
    result = reporting_price(state, rational_price(100), dex(0, 70), reporting_at_s=19)
    assert isinstance(result, Rejected)
    assert result.code == "TIMESTAMP_LEAKAGE"


def test_policy_a_without_seeded_or_completed_history_blocks() -> None:
    result = advance_policy(
        policy_state(policy_a()), rational_price(100), (), checkpoint_id="checkpoint-1", decision_at_s=20
    )
    assert isinstance(result, Blocked)
    assert result.code == "POLICY_HISTORY_REQUIRED"


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Rational("2", "2"),
        lambda: Rational("-1", "1"),
        lambda: Rational("1", "0"),
        lambda: RationalPrice.from_int(WETH, USD8, 0),
        lambda: PolicyConfig("bad", PolicyKind.C_LAGGED_SMOOTHED_PROXY, Rational("2", "1"), 1, 1),
        lambda: PolicyConfig("bad", PolicyKind.C_LAGGED_SMOOTHED_PROXY, Rational("1", "2"), 0, 1),
        lambda: PolicyConfig("bad", PolicyKind.C_LAGGED_SMOOTHED_PROXY, Rational("1", "2"), 1, 0),
    ],
)
def test_invalid_rational_and_policy_parameters_are_rejected(factory: object) -> None:
    with pytest.raises(ContractError):
        factory()  # type: ignore[operator]


@pytest.mark.parametrize(
    "factory",
    [
        lambda: RoundMetadata(RoundStatus.AVAILABLE, 0, 1, 1, 1),
        lambda: RoundMetadata(RoundStatus.UNSUPPORTED, 0, 0, 0, 0, "not supported"),
        lambda: PriceObservation(
            "bad",
            WETH,
            USD8,
            "0",
            EconomicPriceClass.COUNTERFACTUAL_POLICY,
            FIXTURE,
            0,
            0,
            None,
            "config",
            None,
            MISSING_ROUND,
            MISSING_ROUND,
            None,
        ),
        lambda: ReservePosition(
            WETH,
            amount(WETH, 1, QuantityKind.COLLATERAL),
            amount(USDC, 0, QuantityKind.DEBT),
            amount(WETH, 0, QuantityKind.DEBT),
            True,
            8000,
            7000,
            10_500,
        ),
    ],
)
def test_malformed_round_price_or_asset_units_are_rejected(factory: object) -> None:
    with pytest.raises(ContractError):
        factory()  # type: ignore[operator]


def test_duplicate_assets_and_wrong_base_unit_are_rejected() -> None:
    with pytest.raises(ContractError, match="duplicate"):
        PriceSet(
            "duplicate",
            "checkpoint-1",
            USD8,
            (PriceSlot(WETH, price(WETH, 1)), PriceSlot(WETH, price(WETH, 2))),
            "A",
            "v1",
        )
    eur = BaseUnit("EUR", 8, "EUR_1E8", "synthetic:eur-scale")
    with pytest.raises(ContractError, match="base unit"):
        PriceSet("wrong-base", "checkpoint-1", USD8, (PriceSlot(WETH, price(WETH, 1, base=eur)),), "A", "v1")


def test_price_set_rejects_duplicate_observation_ids_and_partial_block_binding() -> None:
    usdc_with_duplicate_id = dataclasses.replace(price(USDC, 1), observation_id=price(WETH, 1).observation_id)
    with pytest.raises(ContractError, match="duplicate observation"):
        price_set(price(WETH, 1), usdc_with_duplicate_id)

    block = BlockRef(1, 10, "0x" + "ab" * 32, 90, "synthetic:canonicality", 90)
    bound = price(WETH, 1, block_ref=block)
    with pytest.raises(ContractError, match="block-bound and unbound"):
        price_set(bound, price(USDC, 1))


def test_price_observation_rejects_cross_chain_block_and_partial_evidence_binding() -> None:
    other_chain = BlockRef(10, 10, "0x" + "cd" * 32, 90, "synthetic:canonicality", 90)
    with pytest.raises(ContractError, match="share chain"):
        price(WETH, 1, block_ref=other_chain)

    bound_evidence = dataclasses.replace(
        FIXTURE,
        block_ref=BlockRef(1, 10, "0x" + "ef" * 32, 90, "x", 90),
        retrieved_at_s=90,
    )
    result = validate_price_observation(price(WETH, 1, evidence=bound_evidence), 100)
    assert isinstance(result, Rejected)
    assert result.code == "INPUT_IDENTITY_MISMATCH"


def test_valuation_rejects_profile_version_mismatch() -> None:
    prices = dataclasses.replace(price_set(price(WETH, 1)), profile_version="OTHER_PROFILE")

    result = value_portfolio(portfolio(position(WETH, debt=1)), prices, context())

    assert isinstance(result, Rejected)
    assert result.code == "VALUATION_CONTEXT_MISMATCH"


def test_cross_chain_price_set_and_portfolio_are_rejected() -> None:
    other = AssetId(10, "0x" + "66" * 20, 18, "synthetic:other-decimals", "OTHER")
    with pytest.raises(ContractError, match="different chains"):
        PriceSet(
            "cross-chain",
            "checkpoint-1",
            USD8,
            (PriceSlot(WETH, price(WETH, 1)), PriceSlot(other, price(other, 1))),
            "A",
            "v1",
        )
    with pytest.raises(ContractError, match="different chains"):
        portfolio(position(WETH), position(other))


def test_deterministic_hashes_change_with_policy_or_quantity_and_replay_exactly() -> None:
    original = portfolio(position(WETH, supplied=1, enabled=True, lt=8000))
    replay = portfolio(position(WETH, supplied=1, enabled=True, lt=8000))
    changed = portfolio(position(WETH, supplied=2, enabled=True, lt=8000))
    assert original.content_hash == replay.content_hash
    assert original.content_hash != changed.content_hash
    assert context("A").content_hash != context("B").content_hash


def test_contracts_are_immutable() -> None:
    observed = price(WETH, 100)
    with pytest.raises(dataclasses.FrozenInstanceError):
        observed.available_at_s = 200  # type: ignore[misc]
