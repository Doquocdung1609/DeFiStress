"""Deterministic, schema-versioned JSON for derived V2 contract content."""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from typing import Protocol, runtime_checkable

from defistress_v2.contracts.errors import CanonicalJsonError, TypeContractError

CONTRACT_SCHEMA_VERSION = "defistress-v2-contracts/0.1"
_UNSIGNED_INTEGER = re.compile(r"0|[1-9][0-9]*")
_SIGNED_INTEGER = re.compile(r"0|-?[1-9][0-9]*")


@runtime_checkable
class CanonicalSerializable(Protocol):
    """A type that declares its own schema-aware canonical representation."""

    def to_canonical(self) -> object: ...


@dataclass(frozen=True, slots=True)
class ExplicitBool:
    """Marks a boolean as an explicitly boolean schema field."""

    value: bool

    def __post_init__(self) -> None:
        if type(self.value) is not bool:
            raise TypeContractError("explicit boolean value must be bool")


@dataclass(frozen=True, slots=True)
class FrozenMap(Mapping[str, object]):
    """Hashable, recursively immutable mapping with deterministic key order."""

    _items: tuple[tuple[str, object], ...]

    def __post_init__(self) -> None:
        if type(self._items) is not tuple:
            raise TypeContractError("FrozenMap items must be an exact tuple")
        normalized: list[tuple[str, object]] = []
        for item in self._items:
            if type(item) is not tuple or len(item) != 2 or type(item[0]) is not str:
                raise TypeContractError("FrozenMap entries must be (str, value) tuples")
            normalized.append((item[0], deep_freeze(item[1])))
        keys = [key for key, _ in normalized]
        if keys != sorted(keys) or len(keys) != len(set(keys)):
            raise TypeContractError("FrozenMap keys must be unique and sorted")
        object.__setattr__(self, "_items", tuple(normalized))

    @classmethod
    def from_mapping(cls, value: Mapping[str, object]) -> FrozenMap:
        if any(type(key) is not str for key in value):
            raise TypeContractError("mapping keys must be strings")
        return cls(tuple((key, deep_freeze(value[key])) for key in sorted(value)))

    def __getitem__(self, key: str) -> object:
        for candidate, value in self._items:
            if candidate == key:
                return value
        raise KeyError(key)

    def __iter__(self) -> Iterator[str]:
        return (key for key, _ in self._items)

    def __len__(self) -> int:
        return len(self._items)


def _assert_deeply_immutable(value: object) -> None:
    """Do not retain caller-owned mutable serializer state inside frozen values."""

    if type(value) in (str, bytes, int, type(None), ExplicitBool):
        return
    if isinstance(value, Enum) and type(value.value) is str:
        return
    if type(value) is FrozenMap:
        for _, item in value._items:
            _assert_deeply_immutable(item)
        return
    if type(value) is tuple:
        for item in value:
            _assert_deeply_immutable(item)
        return
    if (
        isinstance(value, CanonicalSerializable)
        and is_dataclass(value)
        and not isinstance(value, type)
        and getattr(getattr(type(value), "__dataclass_params__", None), "frozen", False)
        and not hasattr(value, "__dict__")
    ):
        for member in fields(value):
            _assert_deeply_immutable(getattr(value, member.name))
        return
    raise TypeContractError("serializer payload must be a deeply immutable slotted frozen value object")


def deep_freeze(value: object) -> object:
    """Freeze nested payload data without coercing scalar types."""

    if isinstance(value, FrozenMap):
        return value
    if isinstance(value, Mapping):
        return FrozenMap.from_mapping(value)
    if isinstance(value, (list, tuple)):
        return tuple(deep_freeze(item) for item in value)
    if type(value) is bool or type(value) is float:
        raise TypeContractError(f"{type(value).__name__} requires an explicit typed contract")
    if type(value) in (str, bytes, int, type(None), ExplicitBool):
        return value
    if isinstance(value, Enum) and type(value.value) is str:
        return value
    if isinstance(value, CanonicalSerializable):
        _assert_deeply_immutable(value)
        return value
    raise TypeContractError(f"unsupported immutable payload type: {type(value).__name__}")


def normalize_integer_string(value: int | str, *, signed: bool) -> str:
    """Return a canonical base-10 integer string without bool coercion."""

    if type(value) is int:
        normalized = str(value)
    elif type(value) is str:
        normalized = value
    else:
        raise TypeContractError("integer must be an exact int or canonical base-10 string")
    pattern = _SIGNED_INTEGER if signed else _UNSIGNED_INTEGER
    if pattern.fullmatch(normalized) is None:
        raise TypeContractError("integer string is not canonical for its signedness")
    return normalized


def _canonicalize(value: object) -> object:
    if isinstance(value, CanonicalSerializable):
        return _canonicalize(value.to_canonical())
    if isinstance(value, ExplicitBool):
        return value.value
    if isinstance(value, Enum):
        if type(value.value) is not str:
            raise CanonicalJsonError("enum values must be strings")
        return value.value
    if isinstance(value, FrozenMap):
        return {key: _canonicalize(item) for key, item in value._items}
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise CanonicalJsonError("canonical JSON keys must be strings")
        return {key: _canonicalize(value[key]) for key in sorted(value)}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_canonicalize(item) for item in value]
    if value is None or type(value) is str:
        return value
    if type(value) is bool:
        raise CanonicalJsonError("raw bool requires ExplicitBool schema marker")
    if type(value) is int:
        raise CanonicalJsonError("integers must be emitted as canonical schema strings")
    if isinstance(value, (float, bytes, bytearray, set, frozenset)):
        raise CanonicalJsonError(f"unsupported canonical JSON type: {type(value).__name__}")
    raise CanonicalJsonError(f"unsupported canonical JSON value: {type(value).__name__}")


def _dump_ready(value: object) -> bytes:
    try:
        text = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"), sort_keys=True)
        return text.encode("utf-8", errors="strict")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise CanonicalJsonError("canonical JSON encoding failed") from exc


def canonical_json_bytes(payload: object, *, schema_version: str = CONTRACT_SCHEMA_VERSION) -> bytes:
    """Encode deterministic derived content; source bytes are never normalized here."""

    if type(schema_version) is not str or not schema_version:
        raise CanonicalJsonError("schema_version must be a nonempty string")
    document = {"payload": _canonicalize(payload), "schema_version": schema_version}
    return _dump_ready(document)


def parse_canonical_json(raw: bytes, *, schema_version: str = CONTRACT_SCHEMA_VERSION) -> object:
    """Strictly parse bytes produced by :func:`canonical_json_bytes`."""

    if type(raw) is not bytes:
        raise CanonicalJsonError("canonical input must be bytes")

    def pairs_hook(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise CanonicalJsonError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    def reject_number(_value: str) -> object:
        raise CanonicalJsonError("JSON numeric literals are forbidden")

    try:
        text = raw.decode("utf-8", errors="strict")
        document = json.loads(
            text,
            object_pairs_hook=pairs_hook,
            parse_int=reject_number,
            parse_float=reject_number,
            parse_constant=reject_number,
        )
    except CanonicalJsonError:
        raise
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise CanonicalJsonError("invalid canonical JSON") from exc
    if not isinstance(document, dict) or set(document) != {"payload", "schema_version"}:
        raise CanonicalJsonError("canonical document has an invalid envelope")
    if document["schema_version"] != schema_version:
        raise CanonicalJsonError("canonical schema version mismatch")
    if _dump_ready(document) != raw:
        raise CanonicalJsonError("JSON bytes are valid but not canonical")

    def restore_explicit_booleans(value: object) -> object:
        if type(value) is bool:
            return ExplicitBool(value)
        if isinstance(value, dict):
            return {key: restore_explicit_booleans(item) for key, item in value.items()}
        if isinstance(value, list):
            return [restore_explicit_booleans(item) for item in value]
        return value

    return deep_freeze(restore_explicit_booleans(document["payload"]))
