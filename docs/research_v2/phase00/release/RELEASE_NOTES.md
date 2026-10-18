# DeFiStress V1 — Scientific Baseline

This release preserves the Commander-approved scientific baseline. It is a research release with explicit scientific and reproduction limits, not a production risk-management or market-forecasting certification.

## Immutable anchors

- Annotated tag: `v1.0.0-scientific-baseline`.
- Release source: `2b505813d35d3cf6f4414585f9dd50f3b4281ac2` (merged PR #26; PR #25 also merged).
- Scientific Content Lock: `3f6e5302483681209e2408531eb5a15389f9fded`.
- Seven-chapter Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Final manuscript source anchor: `ee9b372823e5c636238efe73a4268a5439cf1f80`.

## Included scientific scope

Versioned lending–DEX–liquidation research code, canonical snapshot and historical inputs, Frozen v3 outputs, Oracle Transmission Diagnostic, Scientific Integration Addendum, and Final Accepted Claims Registry v1.1 (48 records: 44 affirmative candidates and four excluded audit records, with mandatory qualifiers).

The official Vietnamese **seven-chapter** report is available as editable DOCX and controlled Markdown under [`docs/manuscript_p3/work/final_assembly/`](https://github.com/Doquocdung1609/DeFiStress/tree/2b505813d35d3cf6f4414585f9dd50f3b4281ac2/docs/manuscript_p3/work/final_assembly). Older five-chapter DOCX files are historical inputs only. No Canva, slide image or PowerPoint assets are attached to this release. School-specific formatting remains `TEMPLATE_VERIFICATION_PENDING`.

## Exact post-merge CI and reproduction evidence

[Run 39147469533](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39147469533) at the exact release source completed **SUCCESS**: backend 226 PASS / 0 FAIL / 0 ERROR / 0 SKIP; frontend 21 PASS; Ruff, mypy and source-preservation checks passed. Tests and assertions were retained without deselection. The RPC smoke job was **skipped because configuration is absent**; live Mainnet RPC validation is not claimed.

Python 3.12.10 on native Windows Server 2025 x64 was installed and smoke-tested with 105 version-pinned, actual wheel-SHA-256-locked distributions. Fresh isolated installation, pip check, version matching and five existing smoke tests passed (the five are a subset of the 226 tests). Lock SHA-256: `edc53ad79a7b9924bd8a9c889e053547dc620a9b1482a3551b150fcd1e08f4ff`.

The tested target is a **new native Windows source-execution environment**, not a recovered original historical environment or certification of Linux, Docker, packaged deployment or offline dependency availability. No container was used; no Docker digest is claimed.

The complete-byte collector verified 91 scoped records / 309,463,168 bytes (90 existing V1 files plus one supplied historical DOCX fixture), recording each size and actual SHA-256; zero scoped records were UNVERIFIED. This is byte identity, not independent scientific row reconstruction or full historical replay. Exact post-merge evidence artifact `v1-g1-evidence-39147469533` (ID 12143897506) has ZIP SHA-256 `9ea08fa155237bb460054bd28fc63ef0cca8a6bf1041fd3d0b19aba40cbade04`; downloaded digest, CRC and JUnit were verified. Actions artifacts have retention limits; persistent scoped checksum evidence is also committed under `docs/research_v2/phase00/g1/`.

The external generator provenance erratum identifies the historical source matching the declared generator checksum at commit `a39337780f0e8d3807138a6048aaa1e1d7d9c8c8`. Current generator LF/CRLF representations have different hashes after typing-only edits; these identities are not conflated. Frozen manifests were not rewritten. Earlier release dossiers retain their historical PENDING/not-released fields; this published release and its exact tag/CI are the later release decision, not a retroactive edit to those records.

## Mandatory scientific limitations

- One canonical snapshot, one modeled DEX venue and a frozen research cohort do not represent all DeFi. Portfolio HF eligibility and route-specific executed liquidation are distinct.
- Oracle A/B/C are hypothetical valuation-transmission policies, not verified Aave/Chainlink Mainnet oracle behavior. Cascade outcomes depend on policy and scenario.
- Severe stress tails are counterfactual. Conditional Monte Carlo frequencies and purposively selected replay paths are not market crisis probabilities.
- Representative agents, non-recycled liquidator capital, unsplit plans and arbitrage price repositioning limit execution realism. Funded on-chain arbitrage and independent local-fork execution are not validated.
- Historical event associations, including same-block/time-window links, do not establish causal Mainnet contagion. Modeled bad debt is not realized financial loss.
- Terra V1 retains negative strict out-of-sample early-warning findings; successful prediction of the initial depeg is not claimed.
- The network extension is structural/run-weighted evidence, not independently validated complete dynamic multilayer causal loss propagation.
- RQ6 retains the corrected LTV scope of 255 WETH-collateral indebted portfolios, distinct from the 109 WETH/USDC route cohort; LT outputs are portfolio-debt USD valuations at USDC/USD = 1, not USDC token quantities.

No new Monte Carlo, retuning, full historical replay or V2 scientific result was produced for this release. V2 work must branch from this immutable V1 source and retain separate provenance.
