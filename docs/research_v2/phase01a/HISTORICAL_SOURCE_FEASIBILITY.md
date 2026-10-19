# Phase 01-A — Historical source feasibility

## Phạm vi và điểm neo

V1 đã phát hành tại annotated tag `v1.0.0-scientific-baseline`, target `2b505813d35d3cf6f4414585f9dd50f3b4281ac2`. V2 phân nhánh từ target đó. Scientific Lock `3f6e5302483681209e2408531eb5a15389f9fded`, Blueprint `8de52bebabef376be700836e6f93a92d7394d2c3` và manuscript anchor `ee9b372823e5c636238efe73a4268a5439cf1f80` không đổi. Receipt phát hành nằm trong `evidence/v1_release_verification.json`.

Đây là kiểm tra khả năng truy xuất và chất lượng đầu vào. Không chạy stress, Monte Carlo, liquidator, arbitrage hoặc mô hình contagion V2. Việc ingestion thành công không nghiệm thu một kết quả khoa học V2.

## Adapter V1 đã đọc và quyết định tái sử dụng

Tất cả đường dẫn sau được đọc tại release target, không dựa vào default branch.

| Thành phần V1 | Tái sử dụng trong pilot | Điều chỉnh chỉ ở lớp V2 |
|---|---|---|
| `backend/app/adapters/rpc.py` | `ReadOnlyRpcClient`, transport và allowlist đọc | Session chỉ cho chain/header/call/log; `eth_call` dùng registered block hash + `requireCanonical`; chặn latest và gửi giao dịch |
| `backend/app/adapters/uniswap/contracts.py` | Factory/pool ABI | Kiểm tra `getPool`, token ordering, fee, spacing, decimals tại cùng historical block |
| `backend/app/adapters/uniswap/ticks.py` | `bitmap_ticks` | Một bitmap word và tối đa 8 initialized ticks gần current tick; không dùng như full liquidity range |
| `backend/app/adapters/aave/contracts.py` | Pool/DataProvider ABIs | Tra historical addresses provider, oracle và data provider trước khi đọc reserve/account |
| `backend/app/adapters/aave/events.py` | LiquidationCall signature | Chỉ exact-block logs; giữ block hash và transaction/log locator |
| `backend/app/services/real_snapshot.py`, Aave `market.py`, `positions.py`, `oracle.py`, `address_book.py`; Uniswap `factory.py`, `pool.py`; `backend/app/schemas.py` | Đã đối chiếu cách pin block, đơn vị, dữ liệu vị thế và tick | Không gọi orchestration chọn pool theo depth hoặc address-book `latest`; không dùng phép quy đổi mặc định USDC/USD=1; không đòi Graph key cho ba sentinel addresses |

Giữ nguyên các file V1. V2 trả raw integers dưới dạng chuỗi, cùng decimals/base-unit đọc từ chain. HF danh mục là dữ liệu Pool; số dư token theo reserve là lớp dữ liệu riêng. Không áp đặt tuyến WETH/USDC cho mọi nghĩa vụ của danh mục.

## Nguồn trực tiếp và tài liệu kỹ thuật

| Nguồn | Vai trò | Phạm vi bằng chứng |
|---|---|---|
| [PublicNode Ethereum](https://ethereum.publicnode.com/), endpoint `https://ethereum-rpc.publicnode.com` | Header, historical state/log feasibility | Khả năng thực tế chỉ được nhận theo các request đã lưu; trang công bố endpoint không bảo đảm toàn bộ archive miễn phí |
| [dRPC Ethereum API](https://drpc.org/docs/ethereum-api), endpoint `https://eth.drpc.org` | Endpoint thứ hai cho cùng mẫu | Endpoint khác không mặc nhiên là independent consensus hoặc independent infrastructure |
| [Ethereum JSON-RPC](https://ethereum.org/developers/docs/apis/json-rpc/), [Geth eth namespace](https://geth.ethereum.org/docs/interacting-with-geth/rpc/ns-eth) | Ngữ nghĩa historical state và exact-block logs | Không dùng block tags động cho dữ liệu mẫu; finalized chỉ dùng kiểm tra điều kiện chấp nhận header |
| [Aave Oracles](https://www.aave.com/docs/aave-v3/smart-contracts/oracles) | Source address và effective asset price | `getSourceOfAsset`/`getAssetPrice` được đọc tại block mẫu; không đồng nhất source address với một Chainlink aggregator trực tiếp |
| [Uniswap pool data](https://developers.uniswap.org/docs/sdks/v3/guides/pool-data), [deployments](https://developers.uniswap.org/docs/protocols/v3/deployments) | Slot0, active liquidity, bitmap/tick, factory identity | Local tick sample không bao phủ toàn bộ initialized ticks hoặc dựng lại toàn bộ pool |

Các nguồn này phục vụ hợp đồng dữ liệu kỹ thuật, không thêm scholarly claims vào P2. Thời điểm kiểm tra: 2026-10-18 UTC. Từ workspace, request `eth_chainId` tới PublicNode trả HTTP 403; kiểm tra thực tế được thực hiện trên GitHub Actions Windows bằng lock V1, tách rõ khỏi mạng workspace.

## Preregistration và phương thức thu thập

Commit `79ca47ee5459bc602f24553d3eb519216bec10dd` khóa lựa chọn số block, hai pool và ba borrower sentinels. Run [39148862610](https://github.com/Doquocdung1609/DeFiStress/actions/runs/39148862610) lấy header: hai endpoint cùng trả hash cho ba block, gồm baseline khớp V1. Commit `85d35785ce759598bff8282e9c3619c49d22d9f9` gắn hash trước khi thực hiện state ingestion. Không có lựa chọn nào dựa trên cascade hay kết quả stress V2.

Ba block: 26045352; 26038152; 26030952. Đây là fixed block offsets 0/−7200/−14400, không mặc định ba thời điểm cách nhau chính xác một ngày. Hai pool là USDC/WETH fee 3000 và 500 millionths; baseline V1 dùng pool 3000. Ba địa chỉ người vay là ba raw addresses đầu tiên theo thứ tự từ điển trong V1 verified snapshot: chỉ dùng audit khả năng đọc, không phải cohort đại diện hoặc borrower census mới.

Mỗi endpoint đọc riêng từng block, hai pass độc lập. Không ghép thành một snapshot từ nhiều endpoint. Header kiểm tra đầu/cuối; `eth_call` dùng block hash; `eth_getLogs` dùng exact block hash. Snapshot canonical giữ chain, block, các component và giá trị đọc; provenance thời điểm/run/provider giữ riêng. Chỉ so hash lặp là PASS khi mọi component bắt buộc có dữ liệu; hai bản cùng thiếu không tạo PASS.

## Mức kiểm chứng và giới hạn

Kết quả thực tế theo từng nguồn/block/component, lỗi và missing-data quarantine nằm trong `PILOT_DATA_PROVENANCE.json`, `PHASE01A_VALIDATION_REPORT.md` và raw evidence. Không suy missing thành số 0; chỉ empty list trả về thật từ RPC mới biểu thị không có log trong exact block.

Run state ingestion39149158699 tại85d35785: **dRPC** đọc đầy đủ3/3 block, cả hai pool, Aave reserves/accounts/oracle và logs; mỗi snapshot được đọc hai lần với content hash trùng. **PublicNode** trả header/log nhưng historical `eth_call` thất bại với RPC code4444 `pruned history unavailable` (earliest available quan sát quanh262108xx). Ba state components ×3 blocks ×2 passes tạo18 quarantine records. Những record này tiếp tục là DATA_ACCESS_BLOCKED; không đổi endpoint hoặc lấy latest để biến chúng thành PASS. Như vậy có hai nguồn thực lấy được header/log, nhưng chỉ một nguồn cung cấp đủ historical state trong mẫu. Cross-endpoint state verification chưa đánh giá được, không gọi sự thiếu nguồn thứ hai là observed state mismatch.

Các historical Aave calls ở ba block cùng resolve provider `0x2f39d218133afab8f2b819b1066c7e434ad94e9e`, oracle `0x54586be62e3c3580375ae3723c145253060ca0c2`, data provider `0x0a16f2fcc0d44fae41cc54e079281d84a363becd`, base-unit100000000 và BASE_CURRENCY zero-address. Giá thực tế vẫn được lưu raw và chia đúng base unit; USDC token decimals6 và WETH18 được kiểm tra riêng. Đây là kết quả truy xuất cấu hình/đơn vị, chưa phải mô phỏng depeg hoặc validation tác động kinh tế.

Oracle trace dừng ở historical Pool → AddressesProvider → Aave oracle → source address và effective asset price/base unit. Lịch sử round/implementation bên trong proxy, adapter hoặc CAPO chưa được kiểm chứng; chưa phải hoàn tất Mainnet oracle fidelity cho V2. Timestamp của reserve phải không sau block; pilot không tự xác nhận độ mới của underlying aggregator rounds khi chưa đọc các rounds đó.

Tick scope là trạng thái slot0/active liquidity và sample tối đa 8 ticks trong một word tại block. Không dùng sample này để tính executable depth, stress hay swap ngoài cửa sổ. Log scope là ba exact blocks, không phải census toàn cửa sổ thị trường. Chưa kiểm chứng receipt/transfer paths hoặc thực thi giao dịch.

Public endpoints không có SLA archival hay bảo đảm truy xuất mọi epoch. Pilot chỉ khảo sát ba block cùng khoảng lịch sử; các thị trường khác, nhiều token, closed borrowers, full tick ranges và out-of-sample design thuộc các bước được Commander giao sau.
