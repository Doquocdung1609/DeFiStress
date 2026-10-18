# V1 Release Blockers — Targeted Repair Evidence

**Scope:** infrastructure/provenance only; candidate source `ee9b372823e5c636238efe73a4268a5439cf1f80`; Phase 00 integration `45679b9e9abb4a7840db27482f9e757b85d8549b`.
**Status:** `REL-01_PATCH_PROPOSED — REL-02/03/04_OPEN — RELEASE_NOT_AUTHORIZED`.

## REL-01 — CI scheduling
- Original: `.github/workflows/ci.yml` used `if: ${{ secrets.ETH_RPC_URL != '' }}` at job level; GitHub refused job scheduling.
- Change in this branch: add `real-rpc-config` non-sensitive boolean output and gate `real-rpc-smoke` using `needs.real-rpc-config.outputs.configured`.
- Importantly, preserve the existing backend/frontend job contents from the baseline rather than introducing PR #19's unrelated Windows runner migration and nine test deselections.
- PR #19 previously demonstrated successful scheduling on its **different** head `b3b34f4a837a2854f5348a75d07fc66b55a1b232`, not on this branch. Scheduling and required job results on this PR must be read back from GitHub Actions before closing REL-01.
- Never log secret content.

## REL-02 — Environment lock: OPEN
- `pyproject.toml` specifies dependency ranges, not a complete frozen Python resolution. `docker-compose.yml` uses mutable images `postgres:17-alpine` and `redis:8-alpine`. `frontend/pnpm-lock.yaml` does not resolve Python/container requirements.
- Required evidence: source-attributed Python 3.12 resolved lock (including hashes and platform), tested clean install / smoke, and container image digest provenance. A new working lock cannot be represented as a recovered historical 2026 V1 environment without evidence.
- No guessed package hashes or Docker digests are committed here. **No environment validation executed.**

## REL-03 — Generator provenance: OPEN
- `data/processed/research_final/scientific_integration_v1/manifest.json` declares `implementation_hashes["scripts/research/build_scientific_integration_v1.py"] = 5a1bbd87ccf065763c3f82d921b977dadb21c520d073e5a2f69498f42ed094a2`.
- The Phase 00 audit observed current LF `9e88de4f4d17dc43f9c09183e9c93bce639ebdde4ea059eaa7bbed81788d5159` and CRLF `81e5d1dadaac1533b818409a0e0f0e13dc6c8b7ad9a3469033cf43243fa7e686`; neither matches. Historic commit `c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193` also did not match.
- Required: find exact historical generator byte object or write a Commander-reviewed **external** provenance erratum with clear unresolved generator identity. Do not update frozen manifest or claim numerical corruption without evidence.

## REL-04 — Large artifact coverage: OPEN
- Critical full-byte audits not yet established for `borrower_level_evidence.csv`, `eligible_vs_executed_audit.csv`, Severe 5000/10000 checkpoint files, and raw swap archives.
- Required: authorized complete clone/archive; exact SHA-256 for bytes (state LF/CRLF domain when relevant), file sizes and provenance; row-level scientific validation is a separate gate.
- Neither a Git blob ID nor a historical report is a newly observed SHA-256 check. **No large-byte audit executed here.**

## Preservation and release gate
- This PR only changes GitHub workflow scheduling and adds this audit note. It does **not** modify engine, results, frozen registries, or 7-chapter manuscript.
- PR #19 remains a distinct open proposal; do not merge both without reconciling histories.
- Canva/slides are not included in scientific release criteria.
- No Monte Carlo, science rerun, V2 Phase 01, merge, tag or release was authorized by this patch.
- Gate status: `G1_BLOCKED`. Close a blocker only using current observed test/verification evidence; scientific results being positive are never required.

## Next verification commands (not claimed executed)
1. Check scheduled jobs on this PR and classify scheduling versus test failures separately.
2. Generate an environment resolution in a clean isolated runtime and record full dependency hashes/versions.
3. Search historic Git blobs for the declared generator digest before preparing an erratum.
4. Read and SHA-256 hash complete critical large file bytes, with path, size and hash domain.
