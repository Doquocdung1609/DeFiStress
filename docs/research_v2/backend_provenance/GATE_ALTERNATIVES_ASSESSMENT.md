# Scientific gate alternatives (proposal, not authorization)

| Property | Gate A — Strict Archive Independence | Gate B — Cross-Provider State Agreement |
|---|---|---|
| Claim under evaluation | Serving backend independence for historical readings | Numerical state agreement from two named RPC services |
| Required evidence | Verifiable request-linked distinct serving-backend identities | Identical registered chain/hash/ABI/method/state values, repeatability, retained provenance and discrepancies |
| Existing verdict | **BLOCKED** — no operator/node-level attestation | **PASS** for 3 registered blocks × 29 core labeled fields × 2 Alchemy reads against saved dRPC |
| What cannot be claimed | Independent archival serving infrastructure proven | Backend independence, full tick/oracle/borrower cross-provider replication, historical causality, economic liquidation execution |
| Decision rights | Commander only | Existing scoped data finding accepted; applying B to progression requires a **new explicit Commander decision** |

## Conservative bounded option if Commander considers Gate B

Potentially permit only reproducibility tooling, read-only data ingestion and noncausal validation inside precisely preregistered datasets, with independent-backend uncertainty prominently disclosed. **No automatic Phase02 authorization**, engine development or changed scientific claims flows from this dossier. Any future work package would require separate scientific scope, tests and explicit Commander authorization.

## Residual risks

- **Correlated infrastructure:** providers could use shared upstream nodes, software/client implementations, data sources, or overlapping incident domains.
- **Reference-time asymmetry:** Alchemy's 2026-10-19 run was compared with saved earlier dRPC observations, not simultaneous cross-provider reads.
- **Coverage limits:** only 29 core labels at each of three blocks; liquidity ticks, borrower reconstruction, oracle history and causal claims are not cross-validated by this comparison.
- **Provider disclosure limits:** the absence of cryptographic attribution cannot be fixed by comparing more matching state values alone.
- **Evidence retention:** the long-lived repository saves sanitized hash-linked summaries and originally linked CI artifact may expire.

## Decision tree

If reliable request-to-serving-node evidence becomes available for *both* providers, submit it for Gate A reconsideration. If it remains unavailable, do not rename Gate B as Gate A; Commander may separately approve bounded work under a revised protocol specifying residual uncertainty and avoiding causal or production-grade claims.

**Present decision:** Gate A BLOCKED; Gate B PASS_IN_REGISTERED_CORE_SCOPE; Phase02 NOT AUTHORIZED.
