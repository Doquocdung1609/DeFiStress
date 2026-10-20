# P02-02 — Read-only saved historical state adapter

This package exposes an immutable, block-bound view over the registered Phase 01-B Aave V3 and Uniswap V3 artifacts. It performs no network request, collection, Health Factor recomputation, AMM operation, liquidation, policy simulation, or Monte Carlo run.

The selection is explicit: block number, read pass, registered pools, full pack for pool/oracle state, and borrower-repair pack for borrower state. The blocked borrower component in the full pack is never used as an implicit fallback.

Validation order is bounded path resolution; raw byte size and SHA-256; single-member gzip decode; decoded size and SHA-256; strict duplicate-free JSON; typed schema/identity/unit checks; then immutable snapshot construction. Text control-file hashes accept either the registered LF byte domain or a CRLF checkout only after an explicit CRLF-to-LF verification. Binary component bytes are never normalized.

`SMOKE_REPORT.json` records all six registered block/read-pass views and dispositions all 46 Phase 02 test IDs. T02–T05 remain explicitly outside this work package.

Scientific status: `GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_HISTORICAL_EXECUTION_NOT_AUTHORIZED`.
