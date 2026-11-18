# DeFiStress V2 functional demo design

## Intent

Build an academic demonstration where a user can run Aave–Uniswap and Terra computations, inspect their assumptions and mechanisms, reload saved results, and export them. The user has explicitly requested autonomous implementation. Product function and historical scientific eligibility remain separate.

## Existing system and decisions

- Reuse the Next.js 16 frontend, FastAPI backend, SQLAlchemy repository, Aave simulation engine, Terra V1 retrospective and stress engines, and P04-03-S synthetic B0–B3 engine.
- Assemble PR #53/#55/#57/#58 exact reviewed candidate blobs on `demo/e2e-preview` from accepted integration `c51d4d06d8b560a149e32ade922f8ed62da1a589`; leave the four Draft PRs untouched. This is a preview, not formal integration or independent acceptance.
- Use small synchronous synthetic B0–B3 and exit calculations. Existing Aave deterministic runs use their current persisted run service. Existing Terra replay and counterfactual endpoints remain available. Small Terra stress runs can remain synchronous; large work stays on existing background mechanisms.
- Persist new synthetic warning and exit records in the existing `terra_experiments` table with explicit experiment types and fixture dataset version, then add retrieval/list/export endpoints. This avoids a new database schema for the demo.
- Run the normal local demo with SQLite and local background tasks, without paid APIs. Repair Docker Compose packaging and provide a one-command Windows path. PostgreSQL/Redis/worker remain available for the full stack.

## Product surface

1. Landing page links to Aave workspace, Terra historical timeline, retrospective warning, synthetic warning, stress, exit planner, results and source status.
2. Aave fixture presets and scenario execution retain separate oracle and DEX prices, eligibility and executed liquidations. The existing run ID, result, comparison and ZIP export stay authoritative.
3. Terra historical timeline reads preserved March–May 2022 data. It shows source/quality labels and gaps. V1 warning remains explicitly retrospective, including its cutoff-safe *reconstruction* variant.
4. Synthetic warning editor accepts exact decimal UST and two LUNA prices or missing values, generates synthetic hourly observations at an explicit UTC cutoff, invokes B0–B3, and displays each immutable result, risk level, score, signals, slots, lineage and assumptions. No historical data enter the scorer.
5. Illustrative exit editor accepts position, warning clock, delay, price movement, fee, slippage and optional execution capacity. It calculates finite gross/net proceeds and unfilled amount under user assumptions. No wallet, order book, trade or historical P04-05 experiment is involved.
6. Result history includes existing Aave runs plus persisted demo warning/exit records with retrieval and export.

## Failure and evidence rules

- Validate finite, bounded inputs; meaningful 422 errors for invalid values. Missing source price yields ABSTAIN, not NORMAL. Unknown actual liquidity yields NOT_VERIFIABLE; a user-declared capacity only supports an illustrative estimate.
- Preserve exact selected model output and origin. No success badge before COMPLETE. No null historical observation becomes zero in charts.
- All new endpoints return JSON-safe finite values. Fixed synthetic fixture timestamps and request/source hashes make repeated runs reproducible. Saved run responses include mode, origin, assumptions, source, execution status and engine version.
- No V1/frozen scientific source edits, 14-field eligibility promotion, P04-04 backtest, prospective forecast claim, live trade or investor exit claim.

## Approaches considered

- **Extend existing Next/FastAPI stack (chosen):** smallest functional addition, preserves present routes, engines and visual language. It needs focused adapter and UI work.
- Separate dashboard/service: simpler isolation but duplicates startup, history and export and weakens the actual integrated demo.
- Reuse V1 warning scorer for synthetic editor: would blur historical and synthetic origins and bypass P04-03-S controls.

## Acceptance

Run all nine requested presentation paths through the real backend and browser. Verify persistence/readback and export, error handling, no paid dependencies, reproducible startup/shutdown, strict scientific labels, existing regression suites, lint/type checks, and protected-source hashes. Record actual logs, screenshots or real video, and a Vietnamese runbook. Declare PRODUCT_DEMO_COMPLETE only if the definition in the user prompt is observed end to end.
