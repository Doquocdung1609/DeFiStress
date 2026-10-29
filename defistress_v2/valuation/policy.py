"""Exact-rational, causal A/B/C counterfactual policy controls for synthetic fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction

from defistress_v2.contracts import Blocked, DeterministicContentSha256, EvidenceRef, Ok, Rejected
from defistress_v2.contracts.canonical import normalize_integer_string
from defistress_v2.contracts.errors import IdentityContractError, TypeContractError
from defistress_v2.contracts.evidence import OriginKind
from defistress_v2.contracts.identity import AssetId
from defistress_v2.contracts.units import UINT256_MAX
from defistress_v2.contracts.valuation import BaseUnit

ELIGIBILITY_CONTEXT_PROFILE = "P02_03_ELIGIBILITY_CONTEXT_V2"
REPORTING_CONTEXT_PROFILE = "P02_03_REPORTING_CONTEXT_V1"


def _identifier(value: object, field: str) -> str:
    if type(value) is not str or not value.strip():
        raise TypeContractError(f"{field} must be a nonempty string")
    return value


def _uint(value: object, field: str, *, positive: bool = False) -> int:
    if type(value) is not int or value < 0 or value > UINT256_MAX or (positive and value == 0):
        raise TypeContractError(f"{field} must be an exact uint256" + (" greater than zero" if positive else ""))
    return value


def _uint_text(value: object, field: str, *, positive: bool = False) -> str:
    if type(value) is not str:
        raise TypeContractError(f"{field} must be a canonical integer string")
    normalized = normalize_integer_string(value, signed=False)
    _uint(int(normalized), field, positive=positive)
    return normalized


class PolicyKind(StrEnum):
    A_ADVERSE_PASS_THROUGH = "A_ADVERSE_PASS_THROUGH"
    B_REFERENCE_ONLY = "B_REFERENCE_ONLY"
    C_LAGGED_SMOOTHED_PROXY = "C_LAGGED_SMOOTHED_PROXY"


class InitializationLabel(StrEnum):
    COMPLETED_HISTORY = "COMPLETED_HISTORY"
    MODEL_DEFINED_INITIALIZATION = "MODEL_DEFINED_INITIALIZATION"


@dataclass(frozen=True, slots=True)
class Rational:
    numerator: str
    denominator: str

    def __post_init__(self) -> None:
        numerator = _uint_text(self.numerator, "numerator")
        denominator = _uint_text(self.denominator, "denominator", positive=True)
        reduced = Fraction(int(numerator), int(denominator))
        if reduced.numerator != int(numerator) or reduced.denominator != int(denominator):
            raise TypeContractError("rational values must be reduced to canonical form")

    @classmethod
    def from_fraction(cls, value: Fraction) -> Rational:
        if type(value) is not Fraction or value < 0:
            raise TypeContractError("rational source must be an exact nonnegative Fraction")
        return cls(str(value.numerator), str(value.denominator))

    @property
    def fraction(self) -> Fraction:
        return Fraction(int(self.numerator), int(self.denominator))

    def to_canonical(self) -> object:
        return {"denominator": self.denominator, "numerator": self.numerator}


@dataclass(frozen=True, slots=True)
class RationalPrice:
    asset: AssetId
    base_unit: BaseUnit
    value: Rational

    def __post_init__(self) -> None:
        if type(self.asset) is not AssetId or type(self.base_unit) is not BaseUnit or type(self.value) is not Rational:
            raise TypeContractError("rational price identity, unit and value must be typed")
        if self.value.fraction <= 0:
            raise TypeContractError("policy price must be positive")

    @classmethod
    def from_int(cls, asset: AssetId, base_unit: BaseUnit, value: int) -> RationalPrice:
        _uint(value, "price", positive=True)
        return cls(asset, base_unit, Rational(str(value), "1"))

    def to_canonical(self) -> object:
        return {"asset": self.asset, "base_unit": self.base_unit, "value": self.value}


@dataclass(frozen=True, slots=True)
class PolicyConfig:
    policy_id: str
    kind: PolicyKind
    alpha: Rational
    lag_steps: int
    smoothing_window: int
    version: str = "P02_03_SYNTHETIC_POLICY_V1"

    def __post_init__(self) -> None:
        _identifier(self.policy_id, "policy_id")
        _identifier(self.version, "version")
        if type(self.kind) is not PolicyKind or type(self.alpha) is not Rational:
            raise TypeContractError("policy kind and alpha must be typed")
        if self.alpha.fraction > 1:
            raise TypeContractError("policy alpha must be in [0,1]")
        _uint(self.lag_steps, "lag_steps", positive=True)
        _uint(self.smoothing_window, "smoothing_window", positive=True)
        if self.kind is not PolicyKind.C_LAGGED_SMOOTHED_PROXY and self.alpha.fraction != 0:
            raise TypeContractError("A/B policies do not accept a transmission alpha")

    def to_canonical(self) -> object:
        return {
            "alpha": self.alpha,
            "kind": self.kind,
            "lag_steps": normalize_integer_string(self.lag_steps, signed=False),
            "policy_id": self.policy_id,
            "smoothing_window": normalize_integer_string(self.smoothing_window, signed=False),
            "version": self.version,
        }


@dataclass(frozen=True, slots=True)
class CompletedDexObservation:
    sequence: int
    completed_at_s: int
    available_at_s: int
    price: RationalPrice
    evidence: EvidenceRef

    def __post_init__(self) -> None:
        _uint(self.sequence, "sequence")
        _uint(self.completed_at_s, "completed_at_s")
        _uint(self.available_at_s, "available_at_s")
        if self.available_at_s < self.completed_at_s:
            raise TypeContractError("DEX observation cannot be available before completion")
        if type(self.price) is not RationalPrice or type(self.evidence) is not EvidenceRef:
            raise TypeContractError("completed DEX observation requires typed price and evidence")
        if self.evidence.origin is not OriginKind.SYNTHETIC:
            raise TypeContractError("P02-03-S policy history accepts synthetic evidence only")

    def to_canonical(self) -> object:
        return {
            "available_at_s": normalize_integer_string(self.available_at_s, signed=False),
            "completed_at_s": normalize_integer_string(self.completed_at_s, signed=False),
            "evidence": self.evidence,
            "price": self.price,
            "sequence": normalize_integer_string(self.sequence, signed=False),
        }


@dataclass(frozen=True, slots=True)
class CounterfactualPolicyState:
    state_id: str
    checkpoint_id: str
    config: PolicyConfig
    reference_price: RationalPrice
    history: tuple[CompletedDexObservation, ...]
    frozen_eligibility_price: RationalPrice
    eligibility_context_hash: DeterministicContentSha256
    fixture_evidence: EvidenceRef
    eligibility_as_of_s: int

    def __post_init__(self) -> None:
        _identifier(self.state_id, "state_id")
        _identifier(self.checkpoint_id, "checkpoint_id")
        if type(self.config) is not PolicyConfig:
            raise TypeContractError("policy config must be typed")
        if type(self.reference_price) is not RationalPrice or type(self.frozen_eligibility_price) is not RationalPrice:
            raise TypeContractError("policy prices must be typed")
        if type(self.history) is not tuple or any(type(value) is not CompletedDexObservation for value in self.history):
            raise TypeContractError("policy history must be an immutable typed tuple")
        if type(self.eligibility_context_hash) is not DeterministicContentSha256:
            raise TypeContractError("eligibility hash must use deterministic-content domain")
        if type(self.fixture_evidence) is not EvidenceRef or self.fixture_evidence.origin is not OriginKind.SYNTHETIC:
            raise TypeContractError("policy state requires synthetic fixture evidence")
        _uint(self.eligibility_as_of_s, "eligibility_as_of_s")
        _assert_compatible_price(self.reference_price, self.frozen_eligibility_price)
        _validate_history(self.history, self.reference_price)
        if any(
            item.completed_at_s > self.eligibility_as_of_s or item.available_at_s > self.eligibility_as_of_s
            for item in self.history
        ):
            raise TypeContractError("frozen policy state contains look-ahead history")

    @property
    def content_hash(self) -> DeterministicContentSha256:
        return DeterministicContentSha256.from_payload(self)

    def to_canonical(self) -> object:
        return {
            "checkpoint_id": self.checkpoint_id,
            "config": self.config,
            "eligibility_context_hash": self.eligibility_context_hash,
            "frozen_eligibility_price": self.frozen_eligibility_price,
            "fixture_evidence": self.fixture_evidence,
            "history": self.history,
            "eligibility_as_of_s": normalize_integer_string(self.eligibility_as_of_s, signed=False),
            "reference_price": self.reference_price,
            "state_id": self.state_id,
        }


@dataclass(frozen=True, slots=True)
class PolicyUpdate:
    state: CounterfactualPolicyState
    valuation_price: RationalPrice
    initialization: InitializationLabel
    parent_state_hash: DeterministicContentSha256

    def __post_init__(self) -> None:
        if (
            type(self.state) is not CounterfactualPolicyState
            or type(self.valuation_price) is not RationalPrice
            or type(self.initialization) is not InitializationLabel
            or type(self.parent_state_hash) is not DeterministicContentSha256
        ):
            raise TypeContractError("policy update fields must be typed")

    def to_canonical(self) -> object:
        return {
            "initialization": self.initialization,
            "parent_state_hash": self.parent_state_hash,
            "state": self.state,
            "valuation_price": self.valuation_price,
        }


@dataclass(frozen=True, slots=True)
class ReportingPrice:
    price: RationalPrice
    policy_id: str
    eligibility_context_hash: DeterministicContentSha256
    reporting_context_hash: DeterministicContentSha256
    reporting_at_s: int

    def __post_init__(self) -> None:
        if type(self.price) is not RationalPrice:
            raise TypeContractError("reporting price must be typed")
        _identifier(self.policy_id, "policy_id")
        if type(self.eligibility_context_hash) is not DeterministicContentSha256:
            raise TypeContractError("reporting result must retain typed eligibility hash")
        if type(self.reporting_context_hash) is not DeterministicContentSha256:
            raise TypeContractError("reporting result must retain typed selected-input lineage")
        _uint(self.reporting_at_s, "reporting_at_s")

    def to_canonical(self) -> object:
        return {
            "eligibility_context_hash": self.eligibility_context_hash,
            "policy_id": self.policy_id,
            "price": self.price,
            "reporting_context_hash": self.reporting_context_hash,
            "reporting_at_s": normalize_integer_string(self.reporting_at_s, signed=False),
        }


def _assert_compatible_price(left: RationalPrice, right: RationalPrice) -> None:
    left_asset = (*left.asset.identity_key, left.asset.decimals)
    right_asset = (*right.asset.identity_key, right.asset.decimals)
    if left_asset != right_asset or left.base_unit != right.base_unit:
        raise IdentityContractError("policy prices must share asset and explicit base unit")


def _validate_history(history: tuple[CompletedDexObservation, ...], reference: RationalPrice) -> None:
    if history and history[0].sequence != 0:
        raise IdentityContractError("policy history must begin with seeded baseline sequence zero")
    previous_sequence: int | None = None
    previous_completed: int | None = None
    for observation in history:
        _assert_compatible_price(reference, observation.price)
        if previous_sequence is not None and observation.sequence != previous_sequence + 1:
            raise IdentityContractError("policy observation sequences must be contiguous and ordered")
        if previous_completed is not None and observation.completed_at_s < previous_completed:
            raise IdentityContractError("policy observations must be time ordered")
        previous_sequence = observation.sequence
        previous_completed = observation.completed_at_s


def policy_a() -> PolicyConfig:
    return PolicyConfig("A_ADVERSE_PASS_THROUGH", PolicyKind.A_ADVERSE_PASS_THROUGH, Rational("0", "1"), 1, 1)


def policy_b() -> PolicyConfig:
    return PolicyConfig("B_REFERENCE_ONLY", PolicyKind.B_REFERENCE_ONLY, Rational("0", "1"), 1, 1)


def policy_c_weak() -> PolicyConfig:
    return PolicyConfig("C_WEAK", PolicyKind.C_LAGGED_SMOOTHED_PROXY, Rational("1", "4"), 1, 3)


def policy_c_moderate() -> PolicyConfig:
    return PolicyConfig("C_MODERATE", PolicyKind.C_LAGGED_SMOOTHED_PROXY, Rational("1", "2"), 1, 2)


def advance_policy(
    state: CounterfactualPolicyState,
    reference_price: RationalPrice,
    completed: tuple[CompletedDexObservation, ...],
    *,
    checkpoint_id: str,
    decision_at_s: int,
) -> Ok[PolicyUpdate] | Blocked | Rejected:
    """Advance from completed, available history only and return a new immutable state."""

    if type(state) is not CounterfactualPolicyState or type(reference_price) is not RationalPrice:
        raise TypeContractError("advance_policy requires typed state and reference price")
    if type(completed) is not tuple or any(type(value) is not CompletedDexObservation for value in completed):
        raise TypeContractError("completed observations must be an immutable typed tuple")
    _identifier(checkpoint_id, "checkpoint_id")
    _uint(decision_at_s, "decision_at_s")
    if decision_at_s < state.eligibility_as_of_s:
        return Rejected(
            "TIMESTAMP_LEAKAGE",
            "policy decision cannot precede its parent eligibility checkpoint",
            (state.fixture_evidence,),
        )
    try:
        _assert_compatible_price(state.reference_price, reference_price)
        combined = state.history + completed
        _validate_history(combined, reference_price)
    except (IdentityContractError, TypeContractError) as exc:
        refs = tuple(item.evidence for item in completed) or (
            state.history[-1].evidence if state.history else state.fixture_evidence,
        )
        affected = tuple(item for item in refs if item is not None)
        return Rejected("POLICY_INPUT_INVALID", str(exc), affected)
    future = tuple(
        item for item in combined if item.completed_at_s > decision_at_s or item.available_at_s > decision_at_s
    )
    if future:
        return Rejected(
            "TIMESTAMP_LEAKAGE",
            "policy update contains an incomplete or unavailable observation",
            tuple(item.evidence for item in future),
        )
    kind = state.config.kind
    initialization = InitializationLabel.COMPLETED_HISTORY
    selected_observations: tuple[CompletedDexObservation, ...] = ()
    if kind is PolicyKind.A_ADVERSE_PASS_THROUGH:
        if not combined:
            return Blocked(
                "POLICY_HISTORY_REQUIRED",
                "Policy A requires a seeded or completed DEX observation",
                (state.fixture_evidence,),
            )
        selected_observations = (combined[-1],)
        result_value = min(reference_price.value.fraction, selected_observations[0].price.value.fraction)
    elif kind is PolicyKind.B_REFERENCE_ONLY:
        result_value = reference_price.value.fraction
    else:
        end = len(combined) - (state.config.lag_steps - 1)
        if end <= 0:
            result_value = reference_price.value.fraction
            initialization = InitializationLabel.MODEL_DEFINED_INITIALIZATION
        else:
            start = max(0, end - state.config.smoothing_window)
            selected_observations = combined[start:end]
            values = tuple(item.price.value.fraction for item in selected_observations)
            mean = sum(values, Fraction(0, 1)) / len(values)
            reference_value = reference_price.value.fraction
            proxy = reference_value + state.config.alpha.fraction * (mean - reference_value)
            result_value = min(reference_value, proxy)
    valuation_price = RationalPrice(
        reference_price.asset,
        reference_price.base_unit,
        Rational.from_fraction(result_value),
    )
    parent_hash = state.content_hash
    next_state = CounterfactualPolicyState(
        state_id=f"{state.state_id}:{checkpoint_id}",
        checkpoint_id=checkpoint_id,
        config=state.config,
        reference_price=reference_price,
        history=combined,
        frozen_eligibility_price=valuation_price,
        eligibility_context_hash=DeterministicContentSha256.from_payload(
            {
                "context_profile": ELIGIBILITY_CONTEXT_PROFILE,
                "checkpoint_id": checkpoint_id,
                "decision_at_s": normalize_integer_string(decision_at_s, signed=False),
                "initialization": initialization,
                "parent_eligibility_context_hash": state.eligibility_context_hash,
                "policy": state.config,
                "reference_price": reference_price,
                "selected_observations": selected_observations,
                "price": valuation_price,
            }
        ),
        fixture_evidence=state.fixture_evidence,
        eligibility_as_of_s=decision_at_s,
    )
    return Ok(PolicyUpdate(next_state, valuation_price, initialization, parent_hash))


def reporting_price(
    state: CounterfactualPolicyState,
    reference_price: RationalPrice,
    current_dex: CompletedDexObservation,
    *,
    reporting_at_s: int,
) -> Ok[ReportingPrice] | Rejected:
    """Return a reporting-only price while retaining the frozen eligibility hash."""

    if type(state) is not CounterfactualPolicyState or type(current_dex) is not CompletedDexObservation:
        raise TypeContractError("reporting_price requires typed policy state and DEX observation")
    _uint(reporting_at_s, "reporting_at_s")
    if reporting_at_s < state.eligibility_as_of_s:
        return Rejected(
            "TIMESTAMP_LEAKAGE",
            "reporting time cannot precede the frozen eligibility checkpoint",
            (current_dex.evidence,),
        )
    try:
        _assert_compatible_price(state.reference_price, reference_price)
        _assert_compatible_price(reference_price, current_dex.price)
    except (IdentityContractError, TypeContractError) as exc:
        return Rejected("POLICY_INPUT_INVALID", str(exc), (current_dex.evidence,))
    if current_dex.completed_at_s > reporting_at_s or current_dex.available_at_s > reporting_at_s:
        return Rejected(
            "TIMESTAMP_LEAKAGE",
            "reporting price cannot use an incomplete or unavailable DEX observation",
            (current_dex.evidence,),
        )
    if state.config.kind is PolicyKind.A_ADVERSE_PASS_THROUGH:
        value = min(reference_price.value.fraction, current_dex.price.value.fraction)
        selected = RationalPrice(reference_price.asset, reference_price.base_unit, Rational.from_fraction(value))
        selected_inputs: tuple[object, ...] = (reference_price, current_dex)
    elif state.config.kind is PolicyKind.B_REFERENCE_ONLY:
        selected = reference_price
        selected_inputs = (reference_price,)
    else:
        selected = state.frozen_eligibility_price
        selected_inputs = (state.frozen_eligibility_price,)
    reporting_context_hash = DeterministicContentSha256.from_payload(
        {
            "context_profile": REPORTING_CONTEXT_PROFILE,
            "eligibility_context_hash": state.eligibility_context_hash,
            "policy": state.config,
            "reporting_at_s": normalize_integer_string(reporting_at_s, signed=False),
            "selected_inputs": selected_inputs,
        }
    )
    return Ok(
        ReportingPrice(
            selected,
            state.config.policy_id,
            state.eligibility_context_hash,
            reporting_context_hash,
            reporting_at_s,
        )
    )
