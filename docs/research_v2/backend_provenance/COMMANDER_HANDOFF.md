# Commander handoff — V2 backend provenance assessment

**Authorization:** `V2_BACKEND_PROVENANCE_ASSESSMENT_AUTHORIZED` ([Issue #31](https://github.com/Doquocdung1609/DeFiStress/issues/31)).
**Start:** `b830d7d53ed9f2bbeac4e19e56afaf49ff8e4e29`.
**Review date:** 2026-10-19.

## Findings

1. Official [dRPC routing architecture](https://drpc.org/docs/howitworks/overview) documents third-party node/provider selection. Official [Alchemy archive guidance](https://www.alchemy.com/docs/what-is-archive-data-on-ethereum) establishes availability of historical Ethereum state, **not** independently audited per-request node identity.
2. Registered Alchemy vs saved dRPC: **174/174 field-pass comparisons agree**, 0 mismatches/missing, 3 blocks × 29 labels, two Alchemy reads each. Source [run #39223539524](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39223539524); SHA-256 and block hashes preserved in [source evidence](../phase01b/alchemy_crosscheck/VERIFIED_CI_EVIDENCE.json). Not 174 statistically independent observations.
3. The stored `drpc-core-free` routing label comes from an earlier dRPC run and does **not** prove the specific upstream of the saved baseline or the later Alchemy run.
4. No direct backend attestation, paired request-specific serving instance IDs or signed cross-provider identity evidence were found **in the reviewed preserved records**. This does not prove shared backend.
5. No new RPC reads, credentials, infrastructure, subscription or historical reconstruction were used.

## Decision requested (do not assume approval)

- **Gate A:** BLOCKED / `BACKEND_INDEPENDENCE_UNVERIFIED`.
- **Gate B:** PASS only for registered historical **core state agreement**.
- **Phase02:** NOT AUTHORIZED. Strict scientific baseline unchanged.
- **Recommendation:** accept the provenance dossier as an honest report of evidence limits. Commander may seek targeted provider attestation for Gate A; or open a *separately authorized*, bounded Gate B-based research track whose claims and methodology expressly disclaim backend independence.

## Deliverable index

- `PROVIDER_ARCHITECTURE_ASSESSMENT.md` — official links, architecture, hierarchy of evidence.
- `REQUEST_PROVENANCE_EVIDENCE.json` — source IDs/hashes, blocks and evidence types.
- `BACKEND_INDEPENDENCE_DECISION.md` — three-case adjudication, attestation gaps.
- `GATE_ALTERNATIVES_ASSESSMENT.md` — Gate A/B conditions, residual risks.
- `COMMANDER_HANDOFF.md` — decisions requested and project guardrails.

**Mandatory final status:** `ARCHIVE_INDEPENDENCE_BLOCKED — PHASE02_NOT_AUTHORIZED`.
