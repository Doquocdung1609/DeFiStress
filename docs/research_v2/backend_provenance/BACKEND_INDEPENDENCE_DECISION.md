# Serving-backend independence: evidence decision

**Current disposition: CASE 2 — PLAUSIBLE BUT UNPROVEN**, with *plausible* meaning merely that different servicing arrangements are possible, **not** a positive probability estimate. Gate A remains **BLOCKED**. No evidence establishes backend overlap or independence for the six Alchemy reads and the saved dRPC baseline.

## Three-case adjudication

| Case | Required evidence | Finding |
|---|---|---|
| 1 — Distinct backend demonstrated | Request-linked verifiable concrete upstream identities for both serving paths and adequate evidence of separation | **NOT DEMONSTRATED** |
| 2 — Distinct plausible but unproven | Two distinct API services, agreeing saved-state data, but incomplete request-specific origins | **CURRENT CLASSIFICATION** |
| 3 — Overlap contradicted / access unavailable | Verified shared serving instance/operator, or failure to access required identity data | **Identity evidence unavailable; shared backend NOT established** |

Service name, TLS endpoint, `clientVersion`, content hashes, and generic response header `drpc-core-free` are not signed node-instance attribution. Official dRPC routing [documentation](https://drpc.org/docs/howitworks/overview) makes dRPC's actual upstream variable. [Verification documentation](https://drpc.org/docs/gettingstarted/verification) describes a provider-signature/quorum facility, but the relevant requests were not captured using it. Alchemy's [archive documentation](https://www.alchemy.com/docs/what-is-archive-data-on-ethereum) describes data access rather than request-level operator attestation.

### Evidence gaps and feasibility

1. **Retrospective trace for saved dRPC baseline:** obtain provider-held mapping of original request time/ID to upstream operator and serving node, if retained. Existing saved data may lack a stable provider correlation identifier. Effort: provider-support exchange, no project infrastructure; availability unknown.
2. **Alchemy execution attribution:** ask if any signed or auditably timestamped request-to-operator attribution exists for the PR #30 CI time window, and whether it is disclosed to nonenterprise projects. Effort: support inquiry; access/plan restrictions unknown.
3. **Cross-source verification:** only if *both* respond with strong, comparable request-level attribution can distinctness be established. A future verification service would validate **future** requests, not retroactively attribute older unlogged ones.

Costs and attainable attestations are not verified; do not promise zero-cost provider support, purchased tiers, or public headers sufficient for this Gate A. Under current authorization there is no new RPC call, subscription, paid resource or infrastructure provision.

**Recommendation to Commander:** accept this bounded provenance audit as completed, retain **Gate A BLOCKED**, and evaluate **Gate B separately** if scientific governance permits bounded forward work. Neither acceptance of this dossier nor Gate B's current PASS silently authorizes Phase02.
