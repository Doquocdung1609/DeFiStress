"""P02-01 pure contract checks using only visibly SYNTHETIC fixtures."""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import json
from pathlib import Path

import pytest

from defistress_v2.contracts import (
    CONTRACT_SCHEMA_VERSION,
    ArtifactBytesSha256,
    AsOfContext,
    AssetId,
    Available,
    Blocked,
    BlockRef,
    DecodedBytesSha256,
    DeterministicContentSha256,
    EvidenceEnvelope,
    EvidenceRef,
    ExplicitBool,
    FrozenMap,
    FutureStateRef,
    GitBlobSha1,
    Missing,
    ObservationContext,
    Ok,
    OriginKind,
    QuantityKind,
    Quarantined,
    Rejected,
    SignedDelta,
    SourceKind,
    UnsignedAmount,
    Unsupported,
    canonical_json_bytes,
    guard_canonicality_evidence,
    guard_same_block_and_time,
    guard_source_kind,
    normalize_integer_string,
    parse_canonical_json,
    verify_artifact_bytes,
    verify_decoded_bytes,
)
from defistress_v2.contracts.errors import (
    CanonicalJsonError,
    ContractError,
    DigestMismatchError,
    IdentityContractError,
    LineageContractError,
    TypeContractError,
)
from defistress_v2.contracts.units import INT256_MAX, INT256_MIN, UINT256_MAX

BLOCK_HASH = "0x" + "12" * 32
OTHER_BLOCK_HASH = "0x" + "34" * 32
USDC_ADDRESS = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
SOURCE_COMMIT = "1" * 40


@pytest.fixture
def block() -> BlockRef:
    return BlockRef(
        chain_id=1,
        number=100,
        hash=BLOCK_HASH,
        timestamp_s=900,
        canonicality_evidence_id="observed:block-canonicality",
        canonicality_observed_at_s=1000,
    )


@pytest.fixture
def usdc() -> AssetId:
    return AssetId(1, USDC_ADDRESS, 6, "synthetic:usdc-decimals", "USDC")


@pytest.fixture
def observed_ref(block: BlockRef) -> EvidenceRef:
    return EvidenceRef(
        evidence_id="observed:block-canonicality",
        origin=OriginKind.OBSERVED,
        source_kind=SourceKind.ONCHAIN_CONTRACT,
        source_commit=SOURCE_COMMIT,
        artifact_path="synthetic/observed-block.json",
        locator="/block",
        source_schema="synthetic-observed-shape/1",
        verification_scope="SYNTHETIC_SHAPE_ONLY_NOT_MAINNET_VALIDATION",
        retrieved_at_s=1000,
        raw_sha256=ArtifactBytesSha256.from_bytes(b"SYNTHETIC observed block"),
        block_ref=block,
    )


def synthetic_ref(fixture_id: str = "P02-01") -> EvidenceRef:
    return EvidenceRef.synthetic(fixture_id, f"SYNTHETIC:{fixture_id}".encode())


@pytest.mark.parametrize(
    ("kwargs", "error"),
    [
        pytest.param({"chain_id": True}, TypeContractError, id="P02-T01-02:SYNTHETIC-bool-chain"),
        pytest.param({"chain_id": 0}, TypeContractError, id="P02-T01-02:SYNTHETIC-zero-chain"),
        pytest.param({"number": -1}, TypeContractError, id="P02-T01-02:SYNTHETIC-negative-block"),
        pytest.param({"hash": "0x12"}, IdentityContractError, id="P02-T01-02:SYNTHETIC-short-hash"),
        pytest.param({"hash": "12" * 32}, IdentityContractError, id="P02-T01-02:SYNTHETIC-unprefixed-hash"),
        pytest.param({"timestamp_s": 1001}, IdentityContractError, id="P02-T01-06:SYNTHETIC-future-canonicality"),
    ],
)
def test_block_ref_rejects_invalid_identity(kwargs: dict[str, object], error: type[ContractError]) -> None:
    values: dict[str, object] = {
        "chain_id": 1,
        "number": 100,
        "hash": BLOCK_HASH,
        "timestamp_s": 900,
        "canonicality_evidence_id": "synthetic:block",
        "canonicality_observed_at_s": 1000,
    }
    values.update(kwargs)
    with pytest.raises(error):
        BlockRef(**values)  # type: ignore[arg-type]


def test_block_ref_normalizes_hex_case_and_serializes_integers_as_strings(block: BlockRef) -> None:
    assert block.hash == BLOCK_HASH.lower()
    canonical = block.to_canonical()
    assert isinstance(canonical, dict)
    assert canonical["chain_id"] == "1" and canonical["number"] == "100"


@pytest.mark.parametrize(
    ("decimals", "address"),
    [
        pytest.param(True, USDC_ADDRESS, id="P02-T01-03:SYNTHETIC-bool-decimals"),
        pytest.param(-1, USDC_ADDRESS, id="P02-T01-03:SYNTHETIC-negative-decimals"),
        pytest.param(256, USDC_ADDRESS, id="P02-T01-03:SYNTHETIC-overflow-decimals"),
        pytest.param(6, "0x1234", id="P02-T01-02:SYNTHETIC-short-address"),
    ],
)
def test_asset_rejects_invalid_decimals_or_address(decimals: object, address: str) -> None:
    with pytest.raises(ContractError):
        AssetId(1, address, decimals, "synthetic:decimals")  # type: ignore[arg-type]


@pytest.mark.parametrize("decimals", [0, 255], ids=["SYNTHETIC-decimals-min", "SYNTHETIC-decimals-max"])
def test_asset_accepts_exact_decimal_boundaries(decimals: int) -> None:
    asset = AssetId(1, USDC_ADDRESS, decimals, "synthetic:decimals")
    assert asset.decimals == decimals and asset.address == USDC_ADDRESS.lower()


def test_asset_unit_is_bound_to_identity_not_symbol(usdc: AssetId) -> None:
    impostor = AssetId(10, USDC_ADDRESS, 6, "synthetic:other-chain", "USDC")
    assert usdc.identity_key != impostor.identity_key
    assert UnsignedAmount.from_int(usdc, 1, QuantityKind.DEBT) != UnsignedAmount.from_int(
        impostor, 1, QuantityKind.DEBT
    )


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(0, id="P02-T01-03:SYNTHETIC-uint-zero"),
        pytest.param(UINT256_MAX, id="P02-T01-03:SYNTHETIC-uint-max"),
    ],
)
def test_unsigned_amount_accepts_exact_boundaries(usdc: AssetId, raw: int) -> None:
    amount = UnsignedAmount.from_int(usdc, raw, QuantityKind.DEBT)
    assert amount.raw_amount == str(raw)


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(True, id="P02-T01-03:SYNTHETIC-bool-amount"),
        pytest.param(1.5, id="P02-T01-03:SYNTHETIC-float-amount"),
        pytest.param(-1, id="P02-T01-03:SYNTHETIC-negative-uint"),
        pytest.param(UINT256_MAX + 1, id="P02-T01-03:SYNTHETIC-uint-overflow"),
    ],
)
def test_unsigned_amount_rejects_non_exact_or_out_of_range(usdc: AssetId, raw: object) -> None:
    with pytest.raises(TypeContractError):
        UnsignedAmount.from_int(usdc, raw, QuantityKind.DEBT)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(INT256_MIN, id="P02-T01-03:SYNTHETIC-int-min"),
        pytest.param(-1, id="P02-T01-03:SYNTHETIC-negative-delta"),
        pytest.param(0, id="P02-T01-03:SYNTHETIC-zero-delta"),
        pytest.param(INT256_MAX, id="P02-T01-03:SYNTHETIC-int-max"),
    ],
)
def test_signed_delta_accepts_declared_domain(usdc: AssetId, raw: int) -> None:
    assert SignedDelta.from_int(usdc, raw, QuantityKind.DELTA).raw_delta == str(raw)


@pytest.mark.parametrize("raw", [INT256_MIN - 1, INT256_MAX + 1])
def test_signed_delta_rejects_overflow(usdc: AssetId, raw: int) -> None:
    with pytest.raises(TypeContractError):
        SignedDelta.from_int(usdc, raw, QuantityKind.DELTA)


def test_amount_signedness_and_kind_cannot_be_confused(usdc: AssetId) -> None:
    with pytest.raises(TypeContractError):
        UnsignedAmount.from_int(usdc, 1, QuantityKind.DELTA)
    with pytest.raises(TypeContractError):
        SignedDelta.from_int(usdc, 1, QuantityKind.BALANCE)
    with pytest.raises(TypeContractError):
        UnsignedAmount(usdc, "1", "DEBT")  # type: ignore[arg-type]
    with pytest.raises(TypeContractError):
        UnsignedAmount("USDC", "1", QuantityKind.DEBT)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", ["00", "01", "+1", "-0", "-1"])
def test_unsigned_integer_strings_require_canonical_form(value: str) -> None:
    with pytest.raises(TypeContractError):
        normalize_integer_string(value, signed=False)


def test_available_zero_is_not_missing(observed_ref: EvidenceRef) -> None:
    available = Available(0, (observed_ref,))
    missing = Missing("source field absent", (observed_ref,))
    assert available.value == 0
    assert available.status.value == "AVAILABLE"
    assert missing.status.value == "MISSING"
    assert available != missing


def test_available_none_and_unreferenced_unavailable_are_rejected(observed_ref: EvidenceRef) -> None:
    with pytest.raises(TypeContractError):
        Available(None, (observed_ref,))
    with pytest.raises(TypeContractError):
        Missing("absent", ())
    with pytest.raises(TypeContractError):
        Unsupported("nativeRound", "not exposed", ())
    with pytest.raises(TypeContractError):
        Quarantined("digest mismatch", ())
    with pytest.raises(TypeContractError):
        Available(1.5, (observed_ref,))
    with pytest.raises(TypeContractError):
        Missing("absent", ("not-evidence",))  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        Available(0, (observed_ref,), status="MISSING")  # type: ignore[call-arg]


def test_missing_unsupported_and_quarantined_are_distinct(observed_ref: EvidenceRef) -> None:
    values = (
        Missing("not returned", (observed_ref,)),
        Unsupported("nativeRound", "adapter has no native round", (observed_ref,)),
        Quarantined("source hash mismatch", (observed_ref,)),
    )
    assert [value.status.value for value in values] == ["MISSING", "UNSUPPORTED", "QUARANTINED"]


def test_result_statuses_keep_blocked_and_rejected_separate(observed_ref: EvidenceRef) -> None:
    ok = Ok({"fixture": "SYNTHETIC"})
    blocked = Blocked("CAPABILITY_INCOMPLETE", "native profile unavailable", (observed_ref,))
    rejected = Rejected("DIGEST_MISMATCH", "supplied bytes do not match", (observed_ref,))
    assert [ok.status.value, blocked.status.value, rejected.status.value] == ["OK", "BLOCKED", "REJECTED"]


def test_nested_payloads_are_deeply_immutable(observed_ref: EvidenceRef) -> None:
    source = {"nested": ["SYNTHETIC", {"zero": 0}]}
    available = Available(source, (observed_ref,))
    source["nested"].append("MUTATION")
    assert isinstance(available.value, FrozenMap)
    assert len(available.value["nested"]) == 2
    with pytest.raises(TypeError):
        available.value["new"] = "forbidden"  # type: ignore[index]


def test_raw_hash_domains_preserve_lf_and_crlf_bytes() -> None:
    lf = b"SYNTHETIC\n"
    crlf = b"SYNTHETIC\r\n"
    assert ArtifactBytesSha256.from_bytes(lf) != ArtifactBytesSha256.from_bytes(crlf)
    verify_artifact_bytes(lf, ArtifactBytesSha256.from_bytes(lf))
    with pytest.raises(DigestMismatchError):
        verify_artifact_bytes(crlf, ArtifactBytesSha256.from_bytes(lf))


def test_decoded_hash_verification_cannot_be_substituted_with_raw_domain() -> None:
    decoded = b"SYNTHETIC decoded payload"
    verify_decoded_bytes(decoded, DecodedBytesSha256.from_bytes(decoded))
    with pytest.raises(DigestMismatchError):
        verify_decoded_bytes(decoded + b"!", DecodedBytesSha256.from_bytes(decoded))


def test_hash_domains_are_nominally_distinct() -> None:
    digest = hashlib.sha256(b"SYNTHETIC").hexdigest()
    assert ArtifactBytesSha256(digest) != DecodedBytesSha256(digest)
    assert ArtifactBytesSha256(digest) != DeterministicContentSha256(digest)
    assert GitBlobSha1.from_bytes(b"what is up, doc?").value == "bd9dbf5aae1a3862dd1526723246b20206e5fc37"
    with pytest.raises(TypeContractError):
        ArtifactBytesSha256("A" * 64)
    with pytest.raises(TypeContractError):
        ArtifactBytesSha256.from_bytes(bytearray(b"not exact bytes"))  # type: ignore[arg-type]


def test_frozen_map_direct_construction_cannot_bypass_key_invariants() -> None:
    with pytest.raises(TypeContractError):
        FrozenMap((("z", "1"), ("a", "2")))
    with pytest.raises(TypeContractError):
        FrozenMap((("a", "1"), ("a", "2")))


def test_canonical_json_is_sorted_compact_utf8_and_has_no_final_lf() -> None:
    raw = canonical_json_bytes({"z": "শেষ", "a": "1", "flag": ExplicitBool(False)})
    assert raw == (
        b'{"payload":{"a":"1","flag":false,"z":"\xe0\xa6\xb6\xe0\xa7\x87\xe0\xa6\xb7"},'
        b'"schema_version":"defistress-v2-contracts/0.1"}'
    )
    assert not raw.endswith(b"\n")
    parsed = parse_canonical_json(raw)
    assert canonical_json_bytes(parsed) == raw


def test_canonical_ordered_vector_accepts_tuple_and_list_with_same_bytes() -> None:
    assert canonical_json_bytes({"vector": ("0", "1")}) == canonical_json_bytes({"vector": ["0", "1"]})


def test_ordinary_text_and_null_are_not_reinterpreted_as_numeric_or_missing() -> None:
    raw = canonical_json_bytes({"display_label": "001", "optional_note": None})
    parsed = parse_canonical_json(raw)
    assert parsed["display_label"] == "001"
    assert parsed["optional_note"] is None


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"n": 1}, id="P02-T01-05:SYNTHETIC-raw-int"),
        pytest.param({"b": True}, id="P02-T01-05:SYNTHETIC-unmarked-bool"),
        pytest.param({"f": 1.0}, id="P02-T01-05:SYNTHETIC-float"),
        pytest.param({"binary": b"x"}, id="P02-T01-05:SYNTHETIC-binary"),
        pytest.param({"unordered": {"x"}}, id="P02-T01-05:SYNTHETIC-set"),
    ],
)
def test_canonical_json_rejects_ambiguous_scalar_or_container_types(payload: object) -> None:
    with pytest.raises(CanonicalJsonError):
        canonical_json_bytes(payload)


def test_strict_parser_rejects_duplicate_keys_numbers_and_noncanonical_whitespace() -> None:
    duplicate = (
        b'{"payload":{"x":"1","x":"2"},"schema_version":"defistress-v2-contracts/0.1"}'
    )
    numeric = b'{"payload":{"x":1},"schema_version":"defistress-v2-contracts/0.1"}'
    spaced = b'{"payload": {}, "schema_version":"defistress-v2-contracts/0.1"}'
    for raw in (duplicate, numeric, spaced):
        with pytest.raises(CanonicalJsonError):
            parse_canonical_json(raw)


def test_unicode_is_preserved_without_normalization_and_surrogates_reject() -> None:
    composed = canonical_json_bytes({"text": "é"})
    decomposed = canonical_json_bytes({"text": "e\u0301"})
    assert composed != decomposed
    with pytest.raises(CanonicalJsonError):
        canonical_json_bytes({"text": "\ud800"})


def test_evidence_ref_rejects_invalid_commit_path_time_and_secret(block: BlockRef) -> None:
    base: dict[str, object] = {
        "evidence_id": "observed:fixture",
        "origin": OriginKind.OBSERVED,
        "source_kind": SourceKind.SAVED_ARTIFACT,
        "source_commit": SOURCE_COMMIT,
        "artifact_path": "synthetic/fixture.json",
        "locator": "/",
        "source_schema": "fixture/1",
        "verification_scope": "SYNTHETIC_SHAPE_ONLY",
        "retrieved_at_s": 1000,
        "raw_sha256": ArtifactBytesSha256.from_bytes(b"fixture"),
        "block_ref": block,
    }
    for mutation in (
        {"source_commit": "short"},
        {"artifact_path": "../escape"},
        {"retrieved_at_s": 899},
        {"locator": "https://user:secret@example.test/data"},
    ):
        values = {**base, **mutation}
        with pytest.raises(ContractError):
            EvidenceRef(**values)  # type: ignore[arg-type]

    with pytest.raises(TypeContractError):
        EvidenceRef(**{**base, "origin": "OBSERVED"})  # type: ignore[arg-type]
    with pytest.raises(TypeContractError):
        EvidenceRef(**{**base, "raw_sha256": hashlib.sha256(b"fixture").hexdigest()})  # type: ignore[arg-type]


def test_synthetic_evidence_identity_is_visible() -> None:
    reference = synthetic_ref("P02-T01-08")
    assert reference.evidence_id == "synthetic:P02-T01-08"
    assert reference.origin is OriginKind.SYNTHETIC
    with pytest.raises(LineageContractError):
        dataclasses.replace(reference, evidence_id="hidden-fixture")


def test_observed_envelope_cannot_promote_synthetic_parent(block: BlockRef) -> None:
    reference = synthetic_ref("P02-T01-08-promotion")
    with pytest.raises(LineageContractError):
        EvidenceEnvelope(
            payload={"value": "0"},
            block_ref=block,
            origin=OriginKind.OBSERVED,
            sources=(reference,),
        )


def test_observed_envelope_accepts_only_direct_observed_source(block: BlockRef, observed_ref: EvidenceRef) -> None:
    envelope = EvidenceEnvelope(
        payload={"raw_balance": "0"},
        block_ref=block,
        origin=OriginKind.OBSERVED,
        sources=(observed_ref,),
    )
    assert envelope.origin is OriginKind.OBSERVED
    with pytest.raises(TypeContractError):
        EvidenceEnvelope(
            payload={"raw_balance": "0"},
            block_ref=block,
            origin=OriginKind.OBSERVED,
            sources=("not-evidence",),  # type: ignore[arg-type]
        )


def test_derived_envelope_requires_derivation_and_parents(block: BlockRef, observed_ref: EvidenceRef) -> None:
    parent_hash = DeterministicContentSha256.from_payload({"parent": "SYNTHETIC_DECLARED"})
    reconstructed = EvidenceEnvelope(
        payload={"value": "0"},
        block_ref=block,
        origin=OriginKind.RECONSTRUCTED,
        sources=(observed_ref,),
        derivation_id="synthetic:reconstruction-method",
        parent_content_hashes=(parent_hash,),
        parent_origins=(OriginKind.OBSERVED,),
    )
    # Full provenance includes acquisition time; stable state content deliberately does not.
    assert reconstructed.content_sha256 != DeterministicContentSha256.from_payload(reconstructed.to_canonical())
    with pytest.raises(LineageContractError):
        dataclasses.replace(reconstructed, parent_origins=())


def test_synthetic_envelope_round_trip_is_deterministic(block: BlockRef) -> None:
    envelope = EvidenceEnvelope(
        payload={"fixture_id": "SYNTHETIC-P02-01", "zero": "0"},
        block_ref=block,
        origin=OriginKind.SYNTHETIC,
        sources=(synthetic_ref("P02-01-envelope"),),
    )
    raw = canonical_json_bytes(envelope)
    assert canonical_json_bytes(parse_canonical_json(raw)) == raw


def test_envelope_rejects_untyped_numeric_payload(block: BlockRef) -> None:
    with pytest.raises(CanonicalJsonError):
        EvidenceEnvelope(
            payload={"raw_amount": 1},
            block_ref=block,
            origin=OriginKind.SYNTHETIC,
            sources=(synthetic_ref("P02-01-untyped-number"),),
        )


def test_same_block_guard_accepts_consistent_observation(block: BlockRef, observed_ref: EvidenceRef) -> None:
    observation = ObservationContext(block, effective_at_s=900, available_at_s=990, evidence_ref=observed_ref)
    result = guard_same_block_and_time(AsOfContext(block, 1000), (observation,))
    assert isinstance(result, Ok)


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param({"chain_id": 10}, id="P02-T01-06:SYNTHETIC-cross-chain"),
        pytest.param({"number": 101}, id="P02-T01-06:SYNTHETIC-cross-number"),
        pytest.param({"hash": OTHER_BLOCK_HASH}, id="P02-T01-06:SYNTHETIC-cross-hash"),
    ],
)
def test_same_block_guard_rejects_identity_mismatch(
    block: BlockRef, observed_ref: EvidenceRef, mutation: dict[str, object]
) -> None:
    other = dataclasses.replace(block, **mutation)
    other_ref = dataclasses.replace(
        observed_ref,
        evidence_id="observed:other",
        block_ref=other,
        retrieved_at_s=other.canonicality_observed_at_s,
    )
    observation = ObservationContext(other, 900, 990, other_ref)
    result = guard_same_block_and_time(AsOfContext(block, 1000), (observation,))
    assert isinstance(result, Rejected) and result.code == "TIMESTAMP_OR_BLOCK_LEAKAGE"


@pytest.mark.parametrize(
    ("effective", "available"),
    [
        pytest.param(1001, 990, id="P02-T01-06:SYNTHETIC-future-effective"),
        pytest.param(900, 1001, id="P02-T01-06:SYNTHETIC-future-available"),
    ],
)
def test_same_block_guard_rejects_lookahead(
    block: BlockRef, observed_ref: EvidenceRef, effective: int, available: int
) -> None:
    observation = ObservationContext(block, effective, available, observed_ref)
    result = guard_same_block_and_time(AsOfContext(block, 1000), (observation,))
    assert isinstance(result, Rejected) and result.code == "TIMESTAMP_OR_BLOCK_LEAKAGE"


def test_canonicality_guard_binds_evidence_id_time_and_block(block: BlockRef, observed_ref: EvidenceRef) -> None:
    assert isinstance(guard_canonicality_evidence(block, observed_ref), Ok)
    wrong_id = dataclasses.replace(observed_ref, evidence_id="observed:wrong")
    assert isinstance(guard_canonicality_evidence(block, wrong_id), Rejected)
    wrong_time = dataclasses.replace(observed_ref, retrieved_at_s=1001)
    assert isinstance(guard_canonicality_evidence(block, wrong_time), Rejected)


def test_source_kind_guard_rejects_dex_spot_as_oracle(block: BlockRef, observed_ref: EvidenceRef) -> None:
    dex = dataclasses.replace(observed_ref, source_kind=SourceKind.DEX_SPOT, evidence_id="observed:dex")
    result = guard_source_kind(dex, SourceKind.ORACLE_ADAPTER)
    assert isinstance(result, Rejected) and result.code == "ORACLE_SOURCE_CONFUSION"
    assert isinstance(guard_source_kind(observed_ref, SourceKind.ONCHAIN_CONTRACT), Ok)


def test_future_state_ref_is_type_only_and_strict(block: BlockRef) -> None:
    state_hash = DeterministicContentSha256.from_payload({"state": "SYNTHETIC"})
    state = FutureStateRef(block, 0, state_hash)
    assert state.state_version == 0
    with pytest.raises(TypeContractError):
        FutureStateRef(block, True, state_hash)


def test_contract_package_has_no_v1_runtime_imports() -> None:
    forbidden: list[tuple[Path, str]] = []
    package = Path("defistress_v2/contracts")
    for path in package.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                roots = [alias.name.split(".", 1)[0] for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module is not None:
                roots = [node.module.split(".", 1)[0]]
            else:
                continue
            forbidden.extend((path, root) for root in roots if root in {"sim", "backend"})
    assert not forbidden


def test_schema_version_is_stable() -> None:
    assert CONTRACT_SCHEMA_VERSION == "defistress-v2-contracts/0.1"


def test_spec_coverage_declares_bounded_implemented_and_future_scope() -> None:
    path = Path("docs/research_v2/p02_01/P02_01_SPEC_COVERAGE.json")
    coverage = json.loads(path.read_text(encoding="utf-8"))
    assert set(coverage["implemented_contract_portions"]) == {
        "P02-T01-02",
        "P02-T01-03",
        "P02-T01-04",
        "P02-T01-05",
        "P02-T01-06",
        "P02-T01-08",
    }
    assert {"P02-T01-01", "P02-T01-07"}.issubset(coverage["not_implemented"])
    assert coverage["specification_total"] == 46
    assert coverage["historical_execution"] == "NOT_AUTHORIZED"


def test_review_mutable_serializer_cannot_escape_deep_freeze(observed_ref: EvidenceRef) -> None:
    class MutableSerializer:
        def __init__(self) -> None:
            self.values = ["SYNTHETIC"]

        def to_canonical(self) -> object:
            return {"values": self.values}

    with pytest.raises(TypeContractError):
        Available(MutableSerializer(), (observed_ref,))
    with pytest.raises(TypeContractError):
        FrozenMap.from_mapping({"nested": MutableSerializer()})


def test_review_frozen_shell_with_mutable_field_is_rejected(observed_ref: EvidenceRef) -> None:
    @dataclasses.dataclass(frozen=True, slots=True)
    class MutableChild:
        values: list[str]

        def to_canonical(self) -> object:
            return {"values": self.values}

    with pytest.raises(TypeContractError):
        Available(MutableChild(["SYNTHETIC"]), (observed_ref,))


def test_review_native_immutable_contract_keeps_nominal_type(block: BlockRef, observed_ref: EvidenceRef) -> None:
    value = Available(block, (observed_ref,))
    assert value.value is block
    assert isinstance(value.value, BlockRef)


def test_review_same_block_guard_checks_source_identity(block: BlockRef, observed_ref: EvidenceRef) -> None:
    wrong = dataclasses.replace(block, number=101, hash=OTHER_BLOCK_HASH)
    reference = dataclasses.replace(observed_ref, block_ref=wrong)
    result = guard_same_block_and_time(AsOfContext(block, 1000), (ObservationContext(block, 900, 990, reference),))
    assert isinstance(result, Rejected) and result.code == "TIMESTAMP_OR_BLOCK_LEAKAGE"


def test_review_missing_source_block_is_blocked(block: BlockRef, observed_ref: EvidenceRef) -> None:
    reference = dataclasses.replace(observed_ref, block_ref=None)
    result = guard_same_block_and_time(AsOfContext(block, 1000), (ObservationContext(block, 900, 990, reference),))
    assert isinstance(result, Blocked) and result.code == "MISSING_BLOCK_REFERENCE"


@pytest.mark.parametrize("source_block", [None, OTHER_BLOCK_HASH])
def test_review_observed_envelope_requires_matching_source_block(
    block: BlockRef, observed_ref: EvidenceRef, source_block: str | None
) -> None:
    reference = dataclasses.replace(
        observed_ref, block_ref=None if source_block is None else dataclasses.replace(block, hash=source_block)
    )
    with pytest.raises(LineageContractError):
        EvidenceEnvelope({"fixture": "SYNTHETIC"}, block, OriginKind.OBSERVED, (reference,))


@pytest.mark.parametrize("mutate_source", [False, True])
def test_review_same_hash_cannot_hide_timestamp_mismatch(
    block: BlockRef, observed_ref: EvidenceRef, mutate_source: bool
) -> None:
    inconsistent = dataclasses.replace(block, timestamp_s=901)
    observation = ObservationContext(
        block if mutate_source else inconsistent,
        900,
        990,
        dataclasses.replace(observed_ref, block_ref=inconsistent) if mutate_source else observed_ref,
    )
    result = guard_same_block_and_time(AsOfContext(block, 1000), (observation,))
    assert isinstance(result, Rejected)


@pytest.mark.parametrize(("effective", "available"), [(950, 990), (900, 899)])
def test_review_observation_clock_is_valid_for_its_block(
    block: BlockRef, observed_ref: EvidenceRef, effective: int, available: int
) -> None:
    result = guard_same_block_and_time(
        AsOfContext(block, 1000), (ObservationContext(block, effective, available, observed_ref),)
    )
    assert isinstance(result, Rejected) and result.code == "TIMESTAMP_OR_BLOCK_LEAKAGE"


def test_review_retrieval_time_is_provenance_not_content(block: BlockRef, observed_ref: EvidenceRef) -> None:
    original = EvidenceEnvelope({"raw_balance": "0"}, block, OriginKind.OBSERVED, (observed_ref,))
    fetched_again = dataclasses.replace(
        original, sources=(dataclasses.replace(observed_ref, retrieved_at_s=1001),)
    )
    assert canonical_json_bytes(original) != canonical_json_bytes(fetched_again)
    assert original.content_sha256 == fetched_again.content_sha256
    assert original.content_sha256 != dataclasses.replace(original, payload={"raw_balance": "1"}).content_sha256


def test_review_nested_reference_also_uses_content_projection(block: BlockRef, observed_ref: EvidenceRef) -> None:
    first = EvidenceEnvelope({"reference": observed_ref}, block, OriginKind.OBSERVED, (observed_ref,))
    later = dataclasses.replace(observed_ref, retrieved_at_s=1001)
    second = dataclasses.replace(first, payload={"reference": later}, sources=(later,))
    assert first.content_sha256 == second.content_sha256


def test_review_projection_keeps_payload_and_economic_clocks(block: BlockRef, observed_ref: EvidenceRef) -> None:
    first = EvidenceEnvelope({"retrieved_at_s": "1000"}, block, OriginKind.OBSERVED, (observed_ref,))
    assert first.content_sha256 != dataclasses.replace(first, payload={"retrieved_at_s": "1001"}).content_sha256
    observation = ObservationContext(block, 900, 990, observed_ref)
    with_clock = dataclasses.replace(first, payload={"observation": observation})
    assert with_clock.content_sha256 != dataclasses.replace(
        with_clock, payload={"observation": dataclasses.replace(observation, available_at_s=991)}
    ).content_sha256


def test_review_iterator_cannot_bypass_nonempty_source_validation(block: BlockRef, observed_ref: EvidenceRef) -> None:
    with pytest.raises(TypeContractError):
        EvidenceEnvelope({"fixture": "SYNTHETIC"}, block, OriginKind.OBSERVED, iter([observed_ref]))  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ["parent_content_hashes", "parent_origins"])
def test_review_parent_vectors_reject_single_use_iterators(
    block: BlockRef, observed_ref: EvidenceRef, field: str
) -> None:
    values = {
        "parent_content_hashes": (DeterministicContentSha256.from_payload({"parent": "SYNTHETIC"}),),
        "parent_origins": (OriginKind.OBSERVED,),
    }
    values[field] = iter(values[field])  # type: ignore[assignment]
    with pytest.raises(TypeContractError):
        EvidenceEnvelope(
            {"fixture": "SYNTHETIC"}, block, OriginKind.RECONSTRUCTED, (observed_ref,),
            derivation_id="synthetic:method", **values,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize("field", ["refs", "warnings"])
def test_review_reference_and_warning_containers_are_explicit(field: str, observed_ref: EvidenceRef) -> None:
    with pytest.raises(TypeContractError):
        if field == "refs":
            Available(0, iter([observed_ref]))  # type: ignore[arg-type]
        else:
            Ok("SYNTHETIC", warnings="warning")  # type: ignore[arg-type]


@pytest.mark.parametrize("signed", [False, True])
def test_review_oversized_decimal_strings_raise_typed_error(usdc: AssetId, signed: bool) -> None:
    with pytest.raises(TypeContractError):
        if signed:
            SignedDelta(usdc, "-" + "9" * 5000, QuantityKind.DELTA)
        else:
            UnsignedAmount(usdc, "9" * 5000, QuantityKind.DEBT)


@pytest.mark.parametrize("signed", [False, True])
def test_review_oversized_integer_convenience_is_range_checked(usdc: AssetId, signed: bool) -> None:
    with pytest.raises(TypeContractError):
        if signed:
            SignedDelta.from_int(usdc, -(10**5000), QuantityKind.DELTA)
        else:
            UnsignedAmount.from_int(usdc, 10**5000, QuantityKind.DEBT)


@pytest.mark.parametrize("raw", [1, True])
def test_review_raw_quantity_constructor_does_not_coerce_non_string(usdc: AssetId, raw: object) -> None:
    with pytest.raises(TypeContractError):
        UnsignedAmount(usdc, raw, QuantityKind.DEBT)  # type: ignore[arg-type]
    with pytest.raises(TypeContractError):
        SignedDelta(usdc, raw, QuantityKind.DELTA)  # type: ignore[arg-type]


def test_review_pool_liquidity_is_not_an_asset_token_delta(usdc: AssetId) -> None:
    with pytest.raises(TypeContractError):
        SignedDelta.from_int(usdc, 1, QuantityKind.NET_LIQUIDITY)


def test_review_canonicality_guard_rejects_inconsistent_header_time(block: BlockRef, observed_ref: EvidenceRef) -> None:
    reference = dataclasses.replace(observed_ref, block_ref=dataclasses.replace(block, timestamp_s=901))
    result = guard_canonicality_evidence(block, reference)
    assert isinstance(result, Rejected) and result.code == "INPUT_IDENTITY_MISMATCH"
