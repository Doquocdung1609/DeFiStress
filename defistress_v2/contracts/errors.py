"""Typed failures raised when constructing invalid offline contracts."""

from __future__ import annotations


class ContractError(ValueError):
    """Base class for caller-supplied contract violations."""

    code = "CONTRACT_ERROR"


class TypeContractError(ContractError):
    code = "TYPE_OR_UNIT_MISMATCH"


class IdentityContractError(ContractError):
    code = "INPUT_IDENTITY_MISMATCH"


class CanonicalJsonError(ContractError):
    code = "CANONICAL_JSON_INVALID"


class DigestMismatchError(ContractError):
    code = "DIGEST_MISMATCH"


class LineageContractError(ContractError):
    code = "EVIDENCE_LINEAGE_INVALID"
