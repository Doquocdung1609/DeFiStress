# REL-03 — External Generator Provenance Erratum

**Disposition:** `HISTORICAL_GENERATOR_HASH_IDENTIFIED`. Frozen manifests remain unchanged.

## Exact declaration and source object

`data/processed/research_final/scientific_integration_v1/manifest.json`, field `implementation_hashes["scripts/research/build_scientific_integration_v1.py"]`, declares:

`5a1bbd87ccf065763c3f82d921b977dadb21c520d073e5a2f69498f42ed094a2`

This is the **exact LF Git-byte SHA256** of the generator at:

- Commit: `a39337780f0e8d3807138a6048aaa1e1d7d9c8c8`.
- Path: `scripts/research/build_scientific_integration_v1.py`.
- Git blob: `ba55014f33a435b91fdd797eb08616e561b6cd02`.
- Exact bytes:72,333.
- [Pinned source](https://github.com/Doquocdung1609/DeFiStress/blob/a39337780f0e8d3807138a6048aaa1e1d7d9c8c8/scripts/research/build_scientific_integration_v1.py).

Work fetched all five versions in this path's reachable commit history through the GitHub connector and hashed their complete bytes. CI independently records the fetched-history scan in `generator-history.json`. This identifies the declaration's object; it is not proof of re-executing that generator or regenerating all outputs.

## Why the current generator differs

The subsequent commit `cebd23a4d1d245436a3520498059be86013da4cd` changes three typing locations:

1. Imports `cast` from `typing`.
2. Wraps the JSON load return in `cast(dict[str, Any], ...)`.
3. Annotates `table_figure_registry` as `dict[str, Any]`.

Its Git blob is `cd0c251aacd42b26556a8ab45e0f881ec0f9c1c2`,72,377 bytes. Its exact LF SHA256 is `9e88de4f4d17dc43f9c09183e9c93bce639ebdde4ea059eaa7bbed81788d5159`; its CRLF representation SHA256 is `81e5d1dadaac1533b818409a0e0f0e13dc6c8b7ad9a3469033cf43243fa7e686`. These are distinct byte hashes, not aliases for the declared SHA.

The diff contains typing changes rather than altered economic equations, parameters or result values. Static examination supports that scope; this erratum does not invent a new numerical replay verdict.

## Separate origin pointer

The manifest's `source_code_commit`/`artifact_bundle_commit` points to `c113fc1ec6dd98ffcc31241c1dbd1a93b20aa193`. That commit's generator is an earlier version: Git blob `ee06689a114c4e07eead7a320cb71dd8cdbb6157`,68,702 bytes, LF SHA256 `3b5feaeb4d85ea2d493a4d3c7b06df139a79d7f52eae9ee23db1883e1d471a7f`. It is an integration-origin pointer, **not** the object that matches the later implementation checksum. The checksum must be resolved using the exact object at `a3933778…` above.

## Release interpretation

The earlier “unidentified hash mismatch” is resolved as a version-scoped provenance discrepancy: the declaration matches a recorded generator, while the later checked-out generator has a typing-only patch. Current source identity and historical generation identity must remain separate. No Frozen/Oracle/Integration/accepted-claims manifest was edited, no result was retuned, and no builder replay was run for this erratum. Commander may review this external mapping as REL-03 evidence; it does not authorize a release tag or merge.
