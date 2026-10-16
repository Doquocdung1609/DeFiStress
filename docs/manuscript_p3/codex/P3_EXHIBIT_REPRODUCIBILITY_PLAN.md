# P3 Exhibit Reproducibility Plan

Status: `P3-G0 — NO FULL EXHIBIT RENDERING`

Scientific source lock: `3f6e5302483681209e2408531eb5a15389f9fded`
Transformation version: `p3-g0-builder-v1`

## Boundary

This plan authorizes deterministic extraction and display transformation only. It does not authorize new simulation runs, interpolation, retuning, synthetic borrowers, new oracle assumptions, cohort changes or new statistical findings.

## Proposed pipeline after blueprint approval

1. Pin checkout to `3f6e5302483681209e2408531eb5a15389f9fded` and verify the Frozen, Oracle, Integration, P2 and Final Registry objects.
2. Resolve the approved exhibit's accepted claim IDs, result IDs and source paths through `P3_LOCKED_EVIDENCE_INVENTORY.json`.
3. Extract only declared rows/fields. Record filters, grouping and ordering as the exhibit transformation specification.
4. Independently recompute counts, units, denominators, cohort, scenario and policy from the locked source without reusing the renderer's aggregation function.
5. Render deterministically to CSV/Markdown and SVG; derive PNG/PDF only from the verified vector source where practical.
6. Attach a per-exhibit manifest with input commit/hash, transformation version, output checksum, units, policy, denominator and limitations.
7. Obtain Codex technical review, Work academic interpretation review and Commander approval before `CHAPTER_LOCKED`.

## Hash semantics

- Git blob IDs and SHA-256 of Git blob bytes identify committed LF-normalized content.
- Checkout SHA-256 is recorded separately; Windows text may be CRLF.
- A CRLF/LF difference is not a scientific change when normalized content and Git provenance match.
- JSON outputs in G0 include a canonical-content SHA-256 with the checksum field omitted. Markdown outputs include a checksum of UTF-8 bytes preceding the checksum line. No self-referential hash is claimed.

## Deterministic rendering constraints

- Stable row ordering by explicit keys; stable legend/category order from the approved spec.
- No timestamps, random IDs, ambient locale or filesystem paths in output bytes.
- Fixed decimal display rules; raw locked values remain available in CSV/JSON provenance.
- Accessible, grayscale-safe palette; no 3D or truncated axes; schematic diagrams labeled as schematic.
- Caption must state evidence type, population/denominator, units, policy/scenario, permitted conclusion and prohibited inference.
- Existing PNGs are not silently modified. A display-only rerender receives a new P3 exhibit ID and manifest.

## Static scientific invariants

- Registry: 35 scholarly + 13 Integration records; 44 affirmative; 4 disallowed; six RQs.
- Oracle counts: A 35/14, B 0/0, C weak 6/0, C moderate 11/2; 36 skipped are route-ineligible due to absent modeled USDC debt.
- Severe: 280/10,000 depth≥2 is Policy A only; ten targeted paths are selected, not a population estimator.
- Haircuts 90/95% are extreme counterfactuals.
- Historical: 28 Pool, 27 Graph-matched, tiers 1/2/23/1; no causal historical contagion.
- Bad debt is modeled uncovered debt, not realized loss. USDC token quantity and USD-equivalent remain distinct.
- Terra negative cutoff-safe/OOS finding is preserved. Network output is a typed graph extension, not full multilayer contagion or DebtRank.
- Arbitrage price repositioning is not a funded executable swap.

## G0 coverage and tests

- Evidence inventory records: 67.
- Proposed catalog entries: 11.
- All catalog source paths must resolve to a P3 evidence ID and all catalog claims must be affirmative.
- Tests verify source-lock identity, locked tree/blob preservation, claim/result/table/figure resolution, exact six-RQ order, numerical invariants and deterministic regeneration.

## Change control

If an exhibit requires an unregistered statistic, source-tier elevation, strengthened causal statement or data not present in the locked inventory, create `EVIDENCE_CHANGE_REQUEST` and stop. G0 ends at `AWAITING_COMMANDER_BLUEPRINT_APPROVAL`.

Content SHA-256 (UTF-8, excluding this checksum line): `27783d45f8cf542f070dcdf7a23af1a56a582b49a11f53d64b38f82de5020334`
