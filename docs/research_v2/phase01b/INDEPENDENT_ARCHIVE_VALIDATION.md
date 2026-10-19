# Independent archival validation — Phase01-B

Status: **INDEPENDENT_ARCHIVE_VALIDATION_BLOCKED**. This is a source-access and source-independence limitation, not evidence of agreeing archive state.

Integration input: `3c3928a9b71348648980de92fa80b31b6d2a647d`. V1 annotated tag `v1.0.0-scientific-baseline`, object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`. No V1/Phase01-A file is modified.

A/B/C source: `6e5285f04d1d5ab2900b51389cc3c025c9b64f42`; [actual collection run 39212923329](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39212923329). Local paths below are relative to this directory. Evidence is preserved at `evidence/full/`; D has its own source/run and separate `evidence/borrower_repair/`.

## Registered comparison

Chain 1, blocks 26045352 / 26038152 / 26030952; exact hashes/timestamps in `SAMPLE_REGISTRATION.json`. Every state call uses EIP-1898 blockHash + requireCanonical, the same address/method/ABI on each endpoint, two reads per endpoint/block. `evidence/full/cross_provider_comparison.json` contains field-level values, missing fields and mismatches. `core/` contains decoded results; `raw/core-*` retains request/response provenance and failures.

| Endpoint/operator | Three-block observation | Classification |
|---|---|---|
| `https://eth.drpc.org` / dRPC gateway | Complete core historical state, deterministic hashes match in 3/3 blocks | Single-gateway archive availability PASS |
| `https://eth.llamarpc.com` / LlamaNodes | HTTP 403 Cloudflare challenge; no usable identity/state | DATA_ACCESS_BLOCKED; no bypass attempted |
| `https://ethereum.public.blockpi.network/v1/rpc/public` / BlockPI | Chain/header available; historical state unavailable (-32000) | Historical archive access BLOCKED |
| `https://ethereum-rpc.publicnode.com` / PublicNode | Chain/header available; state pruned (4444) | Historical archive access BLOCKED |

For BlockPI and PublicNode, each same-block comparison has **4 agreeing identity fields, 26 missing fields and 0 observed mismatches**. Across six comparisons this is 24 identity agreements and 156 unavailable comparison fields; these counts are not 24 independent historical-state validations. Llama contributes no comparison values. Missing is null/explicit failure, never zero or agreement.

## Provider independence

Different URLs, operator names, `web3_clientVersion` and repeated content hashes do not establish a distinct serving backend. dRPC documents routing through third-party partners/public nodes. No signed request-level distinct-backend attestation was obtained. Its verification feature requiring additional credentials was not used. Even a newly accessible second URL must demonstrate independent serving infrastructure before this gate can PASS.

Public source references establish endpoint/interface intent only: [dRPC routing](https://drpc.org/docs/howitworks/overview), [dRPC verification](https://drpc.org/docs/gettingstarted/verification), [BlockPI Ethereum endpoint](https://blockpi.io/chain/ethereum/), [Llama proxy](https://github.com/llamanodes/web3-proxy). Runtime access is evidenced by saved RPC responses, not documentation.

## Transport limits and acceptance criterion

Probe run 39211695514 observed dRPC free-plan batch limit 3. The collector changed batch size, not blocks, pool sample, tick band, borrower ranking or scientific evidence. Four bounded concurrent batches; no paid endpoint/cloud provisioning. Log-range restriction and exact-hash fallback are recorded separately in borrower audit.

To resolve: obtain authorized independent archive access, pin the same block hashes, repeat the same state requests twice, compare every available field, retain mismatches and establish distinct backend provenance. Until then Phase01-B independent validation remains BLOCKED and Phase02 should not begin on a claim of independently validated inputs.
