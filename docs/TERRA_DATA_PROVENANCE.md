# Terra Data Provenance

## Priority

- P0: Terra Classic archival chain/state/events; Ethereum archival state for secondary Curve/bridge components.
- P1: reputable indexed blockchain/protocol datasets.
- P2: market/reference providers used for cross-checking only.

Each imported observation can carry source name/type, chain ID, block height/hash, transaction/event/contract references, retrieval time, dataset version, raw reference, and quality flag. Each dataset manifest stores the time range, row count, hash, transformation version, git commit, missing intervals, and source manifest.

## Current connectivity

No authenticated historical source is bundled. Acquisition scripts therefore write an explicit `UNAVAILABLE` manifest and exit; they never synthesize historical rows. CSV/Parquet/JSON import is operational. `terra_fixture_v1` is deterministic and always labelled `FIXTURE`.

Raw inputs belong in `data/raw` and are never overwritten. Processed versions point back to the raw reference and hash.
