# P02-02 — Read-only saved historical state adapter

This package exposes an immutable, block-bound view over the registered Phase 01-B Aave V3 and Uniswap V3 artifacts. It performs no network request, collection, Health Factor recomputation, AMM operation, liquidation, policy simulation, or Monte Carlo run.

The selection is explicit: block number, read pass, registered pools, full pack for pool/oracle state, and borrower-repair pack for borrower state. The blocked borrower component in the full pack is never used as an implicit fallback.

Validation order is bounded path resolution; raw byte size and SHA-256; single-member gzip decode; decoded size and SHA-256; strict duplicate-free JSON; typed schema/identity/unit checks; then immutable snapshot construction. Text control-file hashes accept either the registered LF byte domain or a CRLF checkout only after an explicit CRLF-to-LF verification. Binary component bytes are never normalized.

`SMOKE_REPORT.json` records all six registered block/read-pass views and dispositions all 46 Phase 02 test IDs. T02–T05 remain explicitly outside this work package.

Work repair adds pinned registration/provenance LF Git-blob anchors, actual identity/pass linkage, immutable typed DTOs, measured bitmap/portfolio/reserve coverage, explicit unsupported-round/freshness fields and structural source-schema guards. Composite views and normalized source-derived fields are RECONSTRUCTED; raw observation fields retain explicit OBSERVED pointers. Imported economic PASS is SOURCE_DECLARED, never a freshly executed HF/native check. Eight T01 specifications remain PARTIAL_SAVED_ADAPTER_SCOPE; partial-view loading and native execution are not implemented. Missing required components block even when a partial response would otherwise be acceptable; no fallback to the old blocked borrower component.

The committed smoke is STATIC_WORKTREE_EVIDENCE with exact code-byte hashes and no circular final adapter-commit assertion. Final-head CI smoke plus execution metadata/actual Git tree is acceptance evidence. Runtime artifact_git_ref is explicitly caller-declared; source content is independently anchored to the accepted Phase01B control blobs. Raw CRLF/LF/gzip/decoded/content hash domains remain distinct. See WORK_TECHNICAL_REVIEW.md for actual findings, tests and scientific boundaries.

Scientific status: `GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED`.
