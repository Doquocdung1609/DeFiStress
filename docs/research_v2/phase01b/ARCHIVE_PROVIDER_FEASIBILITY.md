# Archive provider feasibility — targeted repair

**Result: ACCESS_BLOCKED / BACKEND_INDEPENDENCE_UNVERIFIED.** No eligible second historical-state source was established. This dossier reports a completed bounded investigation; it does not close the scientific gate.

Input integration: `2f850411613ddb6607ea3232f5637fd798156f6f` (PR #28 merged). Commander scoped acceptance: [6262030996](https://github.com/Doquocdung1609/DeFiStress/pull/28#issuecomment-6262030996). Frozen V1 annotated tag object `cdd9c3a80f4df21e7e054045cb93fdc5a7f731c7`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`. Scientific sources, Phase01-A and accepted tick/oracle/borrower reconstructions are unchanged.

Collection source: `dd32f7c19b2c899d95c77d83f6fa19a4769ab535`; [bounded run 39217670638](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39217670638); initial request-plan source `84ab944e35cfef521290732b79d6cf27118340d3`. The initial workflow was rejected before any job/RPC due to an unquoted YAML scalar containing a colon; corrected before collection. JSON-list/ABI-tuple comparison normalization was also corrected before collection. No actual result or numerical threshold was adjusted.

## Candidate selection and access evidence

Only two new public endpoints with provider-published archive claims were selected before collection. The earlier Llama, BlockPI and PublicNode failures were **not re-probed**. dRPC was read as the registered reference, not counted as a new independent source. No account, subscription, paid service, infrastructure or credentials were created.

| Provider | Official source / access intent | Actual observation in this run | Backend origin / independence |
|---|---|---|---|
| dRPC reference | [Routing overview](https://drpc.org/docs/howitworks/overview); existing `https://eth.drpc.org` | Complete 29-value core observation at each of 3 blocks, 2 matching reads; agrees with saved core values | Gateway to third-party/public nodes. Selected response headers show `x-drpc-provider-id=drpc-core-free` on30HTTP responses; this label is not attested concrete node ownership |
| SubQuery candidate | [Official Ethereum archive project](https://subquery.network/projects/ethereum-rpc---archive-node) publishes `https://ethereum.rpc.subquery.network/public`; [official manifest guidance](https://www.subquery.network/doc/indexer/build/manifest/chain-specific/ethereum.html) describes non-pruned archive endpoint | **DNS resolution failure from Windows runner**, `ConnectError: [Errno11001] getaddrinfo failed`, all6 identity-gated observations; no HTTP response was obtained | Public route is a decentralized RPC-operator gateway. Actual serving operator/node not identified; no inference of independence from branding |
| BlockReq candidate | [Official Ethereum page](https://blockreq.com/chains/ethereum) and [home page](https://blockreq.com/) publish public endpoint `https://ethereum-rpc.blockreq.com/v1/rpc/public` and archive capability | Chain ID1 returned. All6 target-header requests denied: RPC `-32601`, message **public endpoint only serves recent blocks (last1024); register for historical/archive access** | Exact serving upstream not attested. Public access does not establish entitlement for the three target blocks |
| Tenderly, desk review only | [Current pricing](https://tenderly.co/pricing), [official authenticated onboarding](https://tenderly.co/blog/getting-started-with-tenderly-web3-gateway/) | No project credential supplied/bound to this scoped workflow; **no RPC sent**. An older free-tier description is not used as a current access entitlement | Own-service description alone does not identify the backend serving any request, nor exclude dRPC upstream overlap |

Source pages reviewed2026-10-19UTC establish access intent, not operational archive success. SubQuery DNS failure is scoped to the actual runner, not proof of global outage or absence of archive storage. BlockReq's explicit runtime message takes precedence over treating its public/archive marketing as successful target-block access. The raw error class from reused V1 utilities is `PROVIDER_REQUEST_FAILURE`; manual interpretation is **ARCHIVE_ACCESS_REQUIRED**, based on the response message rather than assuming `-32601` means an ABI/software error.

## Historical method and query limits

Reuse unchanged `collector.core_observation`, `Rpc`, ABI decoder and identity validation from pinned integration. Same chain1, blocks26045352/26038152/26030952, hashes, contract addresses, functions, token ordering, fee tiers, raw units and decimals. All state calls use EIP-1898 blockHash + requireCanonical. No block-number/latest fallback was substituted.

New routes were tested twice at each target. Identity gates run before historical state: SubQuery never completed chain identity; BlockReq chain ID worked but target headers were denied. Therefore **no historical eth_call was issued to either new candidate**. Treat their core comparison values as unavailable, not zero and not agreeing. Reference dRPC core calls were read twice; tick ranges, oracle rounds and borrower discovery/reconstruction were not rerun.

Collector cap150logicalrequests/provider/block/pass, batch≤3, at most4concurrent batches and bounded transport retries; these are test limits, not vendor-advertised throughput guarantees. SubQuery public throughput was not established. BlockReq's observed public1024-block restriction is explicit, but no account-tier archive quota/entitlement was established. No further endpoint sweep or retry campaign is proposed.

## Exact missing conditions

1. Authorized, reachable archive endpoint for all3registered hashes with target header and exact EIP-1898 state-call support; for BlockReq this requires an account/endpoint with historical access, for SubQuery a resolvable operational endpoint/network route.
2. Request-linked serving operator, backend/upstream identity and evidence that the second data source does not share the dRPC serving backend. `drpc-core-free`, TLS hostname, clientVersion, matching values or different gateway brands are insufficient.
3. A verifiable mapping of dRPC's actual upstream for these requests, together with independent direct-source provenance (or another Commander-approved evidence design). Secret values should be provisioned through authorized runtime configuration, not committed to the dossier.

Without these conditions, further unauthenticated public-endpoint probing cannot be presented as progress on independent validation.
