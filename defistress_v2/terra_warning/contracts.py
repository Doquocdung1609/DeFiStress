"""P04-03-S immutable, synthetic-only warning contracts and exact arithmetic."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, fields
from datetime import timedelta
from enum import StrEnum
from fractions import Fraction

from defistress_v2.contracts import canonical_json_bytes
from defistress_v2.contracts.errors import TypeContractError
from defistress_v2.terra_pit import (
    TERRA_PIT_SCHEMA_VERSION,
    AdmissionPolicy,
    AssetUnit,
    TemporalObservation,
    TerraChainId,
    UtcInstant,
)

SCHEMA = "defistress-terra-synthetic-warning/1"
MODEL_VERSION = "synthetic-toy/1"
MAX_OBSERVATIONS = 512
MAX_WINDOW = 16
MAX_RATIO_BITS = 12000
PROFILES = (
    "reduced-rational-no-rounding/1",
    "completed-hour-grid-linear-revisions-no-fallback/1",
    "consecutive-peg-minimum/1",
    "signed-simple-return-population-variance/1",
    TERRA_PIT_SCHEMA_VERSION,
)


def digest(domain: str, payload: object) -> str:
    return hashlib.sha256(canonical_json_bytes({"domain": domain, "value": payload}, schema_version=SCHEMA)).hexdigest()


def record(value: object) -> object:
    """Dataclass payload, with integers emitted explicitly by individual contracts."""
    return {field.name: getattr(value, field.name) for field in fields(value)}  # type: ignore[arg-type]


@dataclass(frozen=True, slots=True)
class ExactRatio:
    numerator: int
    denominator: int = 1

    def __post_init__(self) -> None:
        if type(self.numerator) is not int or type(self.denominator) is not int or self.denominator <= 0:
            raise TypeContractError("ratio requires exact integers and positive denominator")
        if max(abs(self.numerator).bit_length(), self.denominator.bit_length()) > MAX_RATIO_BITS:
            raise TypeContractError("RATIONAL_SIZE_BOUND")
        ratio = Fraction(self.numerator, self.denominator)
        object.__setattr__(self, "numerator", ratio.numerator)
        object.__setattr__(self, "denominator", ratio.denominator)

    @classmethod
    def from_fraction(cls, value: Fraction) -> ExactRatio:
        if type(value) is not Fraction:
            raise TypeContractError("value must be an exact Fraction")
        return cls(value.numerator, value.denominator)

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.numerator, self.denominator)

    def to_canonical(self) -> object:
        return {"numerator": str(self.numerator), "denominator": str(self.denominator)}


class ModelId(StrEnum):
    B0 = "B0_NEVER_ALERT"
    B1 = "B1_UST_PEG_STRESS"
    B2 = "B2_LUNA_MARKET_STRESS"
    B3 = "B3_TRANSPARENT_COMPOSITE"


class RiskLevel(StrEnum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    HIGH = "HIGH"
    ABSTAIN = "ABSTAIN"


@dataclass(frozen=True, slots=True)
class DecisionContext:
    decision_at: UtcInstant
    information_cutoff: UtcInstant
    issued_at: UtcInstant

    def __post_init__(self) -> None:
        if any(type(value) is not UtcInstant for value in (self.decision_at, self.information_cutoff, self.issued_at)):
            raise TypeContractError("decision clocks must be typed UTC instants")
        if not self.information_cutoff <= self.decision_at <= self.issued_at:
            raise TypeContractError("require information_cutoff <= decision_at <= issued_at")

    def to_canonical(self) -> object:
        return record(self)


@dataclass(frozen=True, slots=True)
class SeriesSpec:
    source_id: str
    unit: AssetUnit
    policy: AdmissionPolicy
    chain: TerraChainId = TerraChainId("columbus-5")

    def __post_init__(self) -> None:
        if type(self.source_id) is not str or not self.source_id or len(self.source_id) > 128:
            raise TypeContractError("source_id must be a bounded nonempty string")
        if type(self.unit) is not AssetUnit or type(self.policy) is not AdmissionPolicy:
            raise TypeContractError("series unit/policy must be typed")
        if type(self.chain) is not TerraChainId or self.policy.max_source_age is None:
            raise TypeContractError("series requires Terra identity and explicit source-age policy")

    def to_canonical(self) -> object:
        return record(self)


@dataclass(frozen=True, slots=True)
class WarningConfig:
    ust: SeriesSpec
    luna: SeriesSpec
    reference_price: ExactRatio = ExactRatio(1)
    peg_persistence: int = 1
    luna_return_window: int = 1
    profile_id: str = "issue56-synthetic-hourly/1"

    def __post_init__(self) -> None:
        if type(self.ust) is not SeriesSpec or type(self.luna) is not SeriesSpec:
            raise TypeContractError("configuration requires immutable typed series")
        if type(self.reference_price) is not ExactRatio or self.reference_price.numerator <= 0:
            raise TypeContractError("reference price must be positive exact ratio")
        for size in (self.peg_persistence, self.luna_return_window):
            if type(size) is not int or not 1 <= size <= MAX_WINDOW:
                raise TypeContractError("window must be exact integer within 1..16")
        if self.profile_id != "issue56-synthetic-hourly/1":
            raise TypeContractError("unknown model profile")
        for series, asset in ((self.ust, "UST"), (self.luna, "LUNA")):
            unit = series.unit
            if unit.base_asset != asset or unit.quote_asset is None or unit.unit != f"{unit.quote_asset}/{asset}":
                raise TypeContractError("exact declared price unit required")
        if self.ust.unit.quote_asset != self.luna.unit.quote_asset or self.ust.chain != self.luna.chain:
            raise TypeContractError("implicit quote/chain conversion is forbidden")
        if self.ust.source_id == self.luna.source_id:
            raise TypeContractError("toy price streams require distinct source identifiers")

    @property
    def config_hash(self) -> str:
        return digest("configuration", self)

    @property
    def profile_hash(self) -> str:
        return digest("profiles", {"profiles": PROFILES, "id": self.profile_id, "thresholds": THRESHOLDS})

    def to_canonical(self) -> object:
        return {
            "ust": self.ust,
            "luna": self.luna,
            "reference_price": self.reference_price,
            "peg_persistence": str(self.peg_persistence),
            "luna_return_window": str(self.luna_return_window),
            "profile_id": self.profile_id,
            "sample_period_us": "3600000000",
            "thresholds": THRESHOLDS,
        }


# Toy constants from Issue56; never fitted, probabilities, or historical safety levels.
THRESHOLDS = (
    ("B1_WATCH", ExactRatio(1, 200)),
    ("B1_HIGH", ExactRatio(1, 100)),
    ("B2_WATCH", ExactRatio(1, 20)),
    ("B2_HIGH", ExactRatio(1, 10)),
    ("B3_WATCH", ExactRatio(1, 2)),
    ("B3_HIGH", ExactRatio(3, 4)),
    ("UST_SATURATION", ExactRatio(1, 50)),
    ("LUNA_SATURATION", ExactRatio(1, 5)),
)


def toy_config() -> WarningConfig:
    policy = AdmissionPolicy(timedelta(0), timedelta(hours=24))
    return WarningConfig(
        SeriesSpec("synthetic-ust", AssetUnit("UST", "USD", "USD/UST"), policy),
        SeriesSpec("synthetic-luna", AssetUnit("LUNA", "USD", "USD/LUNA"), policy),
    )


@dataclass(frozen=True, slots=True)
class WarningInputs:
    ust: tuple[TemporalObservation, ...]
    luna: tuple[TemporalObservation, ...]

    def __post_init__(self) -> None:
        for series in (self.ust, self.luna):
            if type(series) is not tuple or len(series) > MAX_OBSERVATIONS:
                raise TypeContractError("inputs must be bounded immutable tuples")
            if any(type(item) is not TemporalObservation for item in series):
                raise TypeContractError("inputs must contain TemporalObservation records")


@dataclass(frozen=True, slots=True)
class InputSlot:
    component: str
    expected_at: UtcInstant
    ancestry: tuple[TemporalObservation, ...]
    selected: TemporalObservation | None
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.component not in {"UST", "LUNA"} or type(self.expected_at) is not UtcInstant:
            raise TypeContractError("invalid slot identity/time")
        if type(self.ancestry) is not tuple or any(type(x) is not TemporalObservation for x in self.ancestry):
            raise TypeContractError("slot ancestry must be immutable typed records")
        if type(self.reasons) is not tuple or any(type(x) is not str or not x for x in self.reasons):
            raise TypeContractError("slot reasons must be immutable strings")
        if self.selected is None:
            if not self.reasons:
                raise TypeContractError("unavailable slot requires reasons")
        elif type(self.selected) is not TemporalObservation or not self.ancestry or self.ancestry[-1] != self.selected:
            raise TypeContractError("selected slot must retain exact revision ancestry")
        elif self.reasons:
            raise TypeContractError("selected slot cannot have rejection reasons")

    def to_canonical(self) -> object:
        return record(self)


@dataclass(frozen=True, slots=True)
class SignalContribution:
    signal_id: str
    value: ExactRatio
    role: str

    def __post_init__(self) -> None:
        if type(self.signal_id) is not str or not self.signal_id or type(self.value) is not ExactRatio:
            raise TypeContractError("invalid exact signal")
        if self.role not in {"DERIVED_FEATURE", "SCORE_CONTRIBUTION"}:
            raise TypeContractError("signal is model-derived, never a native observation")

    def to_canonical(self) -> object:
        return record(self)


@dataclass(frozen=True, slots=True)
class WarningResult:
    model_id: ModelId
    context: DecisionContext
    config: WarningConfig
    slots: tuple[InputSlot, ...]
    signals: tuple[SignalContribution, ...]
    score: ExactRatio | None
    level: RiskLevel
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        if type(self.model_id) is not ModelId or type(self.level) is not RiskLevel:
            raise TypeContractError("result model/risk level must be typed enums")
        if type(self.context) is not DecisionContext or type(self.config) is not WarningConfig:
            raise TypeContractError("result requires frozen typed context/configuration")
        for items, expected in ((self.slots, InputSlot), (self.signals, SignalContribution)):
            if type(items) is not tuple or any(type(item) is not expected for item in items):
                raise TypeContractError("result members must be immutable typed tuples")
        if type(self.reasons) is not tuple or any(type(x) is not str or not x for x in self.reasons):
            raise TypeContractError("result reasons must be immutable strings")
        if self.level is RiskLevel.ABSTAIN:
            if self.score is not None or not self.reasons or self.signals:
                raise TypeContractError("abstention requires reasons, no score or partial signals")
        elif type(self.score) is not ExactRatio or self.score.numerator < 0 or self.reasons:
            raise TypeContractError("scored decision requires nonnegative exact score, no abstention reasons")
        if self.level is not RiskLevel.ABSTAIN and (not self.slots or any(s.selected is None for s in self.slots)):
            raise TypeContractError("scored output requires complete admitted support")
        # Public dataclass construction and dataclasses.replace must obey the same
        # synthetic admission and model rules as evaluate().  Recompute from the
        # retained causal ancestry, without consulting any future or external data.
        from defistress_v2.terra_warning.engine import _compute_result_fields

        inputs = WarningInputs(
            tuple(item for slot in self.slots if slot.component == "UST" for item in slot.ancestry),
            tuple(item for slot in self.slots if slot.component == "LUNA" for item in slot.ancestry),
        )
        recomputed = _compute_result_fields(self.model_id, inputs, self.context, self.config)
        # A future-only bar is deliberately absent from causal ancestry.  Once
        # omitted, recomputation cannot distinguish it from an absent bar;
        # both reasons are safe abstentions with identical empty support.
        comparable_slots = tuple(
            InputSlot(slot.component, slot.expected_at, (), None, ("REQUIRED_OBSERVATION_MISSING",))
            if not slot.ancestry and slot.selected is None and slot.reasons == ("NOT_YET_AVAILABLE",)
            else slot
            for slot in self.slots
        )
        comparable_reasons = tuple(sorted({
            f"{slot.component}:{reason}" for slot in comparable_slots for reason in slot.reasons
        })) if self.level is RiskLevel.ABSTAIN else self.reasons
        if (comparable_slots, self.signals, self.score, self.level, comparable_reasons) != recomputed:
            raise TypeContractError("WARNING_RESULT_SEMANTIC_MISMATCH")

    @property
    def input_lineage_hash(self) -> str:
        return digest("selected-causal-inputs", {
            "model_id": self.model_id, "model_version": MODEL_VERSION,
            "context": self.context, "config": self.config,
            "profile_hash": self.config.profile_hash, "slots": self.slots,
        })

    @property
    def output_hash(self) -> str:
        return digest("warning-output", self)

    def to_canonical(self) -> object:
        return {
            "record_kind": "SYNTHETIC_MODEL_WARNING_NOT_NATIVE_OBSERVATION",
            "origin": "SYNTHETIC", "validation_status": "SYNTHETIC_CONTROLS_ONLY",
            "model_id": self.model_id, "model_version": MODEL_VERSION,
            "context": self.context, "configuration": self.config,
            "config_hash": self.config.config_hash, "profile_hash": self.config.profile_hash,
            "input_lineage_hash": self.input_lineage_hash,
            "required_observations": str(len(self.slots)),
            "available_observations": str(sum(slot.selected is not None for slot in self.slots)),
            "slots": self.slots, "signals": self.signals,
            "score": self.score, "level": self.level, "reasons": self.reasons,
        }
