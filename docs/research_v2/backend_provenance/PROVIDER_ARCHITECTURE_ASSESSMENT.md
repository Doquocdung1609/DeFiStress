# Backend provenance — official provider architecture assessment

**Review date:** 2026-10-19 (UTC). **Authorization:** [Issue #31](https://github.com/Doquocdung1609/DeFiStress/issues/31). **Pinned integration:** `b830d7d53ed9f2bbeac4e19e56afaf49ff8e4e29`.

## Definitions and boundaries

A *service brand* names a commercial API; an *endpoint/gateway* accepts requests; an *operator* runs infrastructure; the *serving backend* is the actual node or archival implementation that serviced a particular request. Distinct brands or URLs do not automatically imply distinct serving backends, and an archive node can respond without identifying its operator.

## Official documentation reviewed

| Claim ID | Provider | Verifiable official source | Classification | Supported conclusion and limitation |
|---|---|---|---|---|
| ARCH-DRPC-1 | dRPC | https://drpc.org/docs/howitworks/overview | PROVIDER_DOCUMENTED_ARCHITECTURE | dRPC's Dproxy/Dshackle architecture routes RPC requests among third-party/public data providers. Which provider actually handled our October 2026 requests is not identified by this overview. |
| ARCH-DRPC-2 | dRPC | https://drpc.org/docs/providers/setup | PROVIDER_DOCUMENTED_ARCHITECTURE | A provider-side Dshackle instance can front multiple nodes. A provider label alone is not a unique node ID or independently signed attribution. |
| ARCH-DRPC-3 | dRPC | https://drpc.org/docs/gettingstarted/verification | PROVIDER_DOCUMENTED_ARCHITECTURE | dRPC documents a quorum/provider-signature verification mechanism with configuration and method constraints. No such signatures or verified quorum proof were preserved for these registered requests; existence of a feature does not retroactively attest earlier requests. |
| ARCH-ALCH-1 | Alchemy | https://www.alchemy.com/docs/what-is-archive-data-on-ethereum | PROVIDER_DOCUMENTED_ARCHITECTURE | Alchemy describes archive Ethereum state and the RPC operations it enables; this establishes product capability, not the hardware/upstream for an individual query. |
| ARCH-ALCH-2 | Alchemy | https://www.alchemy.com/docs/ethereum-nodes | PROVIDER_DOCUMENTED_ARCHITECTURE | Alchemy describes Ethereum node types and archive-data access. This does not document a signed mapping from these six Alchemy reads to a concrete independently operated node. |
| ARCH-ALCH-3 | Alchemy | https://www.alchemy.com/docs/reference/ethereum-api-quickstart | PROVIDER_DOCUMENTED_ARCHITECTURE | Alchemy's Ethereum endpoint is a gateway into node-backed API data. Endpoint host identity is not an attestation of the serving archival instance. |

The cited source pages were consulted for this review on 2026-10-19; the contents are subject to subsequent provider changes. Statements are deliberately limited to what the documentation supplies, and do not assert that Alchemy uses dRPC, that dRPC uses Alchemy, or that their infrastructure necessarily overlaps.

## Request-level identity evidence

- **dRPC:** Prior evidence records the selected `x-drpc-provider-id=drpc-core-free` for 30 responses in an older bounded collection ([feasibility dossier](../phase01b/ARCHIVE_PROVIDER_FEASIBILITY.md)); it is an unauthenticated provider label, not a mapping to a legal operator or physical/archive-node identity. The PR #30 Alchemy comparison reused **saved dRPC core data** rather than capturing new dRPC requests.
- **Alchemy:** PR #30's sanitized output stores chain/block/field hashes and field comparison summaries, **not** provider-specific headers, signed upstream identity, request-level node instance IDs, or raw HTTP material. The absence of these data in persisted evidence prohibits retrospective authentication.
- **Joint finding:** The historical data are reproducibly consistent in the registered core scope; distinct **request-serving backends** remain unproven. The record offers no affirmative evidence of a shared backend either.

## Minimal useful follow-up

Request provider support documentation on whether operator-specific signed request attribution or timestamp-bound upstream/instance identifiers exist **for the cited run IDs and timestamps**. A generic assurance letter or endpoint hostname is only supplementary unless it verifiably links to actual served requests. If provider disclosures cannot be obtained, publish the scope limitation and let Commander consider Gate B separately. Do not purchase services or launch new RPC probes under this authorization.
