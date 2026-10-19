# Đề xuất GO/NO-GO dành cho Commander

**V2_GATE_B_PROTOCOL_READY_FOR_COMMANDER_REVIEW**  
**GATE_A_BLOCKED — GATE_B_SCOPED_PASS — PHASE02_NOT_AUTHORIZED**

Input: `cbcf8c451c9f2c83a2f07ae483ba6c3a25ecd815`; design authority: [Issue33](https://github.com/Doquocdung1609/DeFiStress/issues/33). Đây là **đề xuất quyết định**, không phải cấp phép triển khai. Gate B đã được Commander nghiệm thu như scoped state agreement tại PR30; Gate A vẫn theo tiêu chí độc lập hạ tầng ban đầu.

## Đề nghị theo mức triển khai

| Mức / đối tượng quyết định | Gate B đủ cho điều gì? | Điều kiện trước một lệnh mới | Đề nghị, không phải quyền hiện tại |
|---|---|---|---|
| L0 — governance/design | Review nguồn đã lưu, xác lập contracts/tests và phạm vi giả thuyết | Issue33 design scope; bảo toàn nguồn và V1 | **GO trong nhiệm vụ hiện tại**, chỉ hồ sơ |
| L1 — read-only ingestion / integrity | Có thể làm căn cứ cho pilot giới hạn trên registered core; không gọi độc lập backend hoặc toàn bộ dataset | Commander chỉ rõ sample, methods, budgets, missing/quarantine và retention. Dữ liệu mới cần provenance/coverage nghiệm thu riêng; không tự mở rộng PASS từ29 labels sang vectors | **Có thể xin phép riêng dưới Gate B**; chưa được phép chạy ở đây |
| L2 — isolated deterministic components với synthetic fixtures | Có thể kiểm tra units, rounding, missing guards, state transitions giả lập mà không cần giả định historical source độc lập | Scope chỉ pure isolated components, fixtures ghi SYNTHETIC, không historical calibration, không tích hợp engine/agents, không báo kết quả stress; Commander cấp lệnh riêng | **Có thể xin phép riêng dưới Gate B**; không gọi đây là Phase02 engine authorization |
| L3 — V2 simulation engine implementation/integration | Core agreement chưa đủ bảo đảm scientific input/execution contracts cho engine lịch sử | Đóng Gate A cho input campaign liên quan, coverage và protocol-version specs; test plan/local-fork strategy/budget controls; lệnh Phase02 riêng. Một ngoại lệ research prototype nếu Commander muốn phải có quyết định thay entry scope rõ, không tự đổi Gate A thành PASS | **NO-GO hiện tại**; chưa mở engine |
| L4 — full historical quantitative stress / execution findings | B-only không đủ | Gate A + use-specific complete ticks/portfolio/oracle timeline/freshness + validated local-fork receipts, conservation, agents/funding/gas/latency + registered controls/sample. A PASS một mình vẫn chưa đủ | **NO-GO** cho chạy/công bố findings này |
| L5 — causal Mainnet hoặc predictive claims | Không dùng agreement để chứng minh causal/forecast validity | Historical input gates theo scope; causal identification hoặc sealed OOS/cross-market design riêng, baselines, leakage controls và độc lập validation. V2 model interventions chỉ có causal meaning trong mô hình; Terra test riêng | **NO-GO** cho claims hiện tại; không cam kết kết quả dương |

Không có mức L1–L5 nào đang được cấp quyền bằng bảng này. Phân loại không phủ nhận khả năng nghiên cứu phương pháp bằng dữ liệu tổng hợp; nó ngăn kết quả synthetic bị trình bày như empirical validation. Chưa đủ lý do khoa học để đề nghị mở toàn Phase02 khi Gate A, execution validation và các use-specific coverage gaps còn mở.

## Phân biệt ba mức sẵn sàng

**Ready to design: YES**, dựa trên nguồn đã lưu và protocol proposal. **Ready to run Phase02 engine: NO**, thiếu lệnh riêng và các prerequisites. **Ready to publish V2 stress/causal/predictive findings: NO**. Có thể trình Commander xem scoped data-agreement finding với toàn bộ limitations hiện hành; việc nghiệm thu hồ sơ này không tự là publication approval hoặc Scientific Content Lock V2.

Gate A không bị hạ xuống hoặc đổi tên để phù hợp với dữ liệu đang có. Phương án hợp lý nhất là giữ cả hai cổng, tiếp tục chỉ những bounded tasks mà tính đúng không đòi giả định độc lập hạ tầng, và tách yêu cầu attestation khỏi engine readiness. Nhiều phép đọc khớp hơn từ cùng failure domain không khắc phục thiếu chứng cứ độc lập.

## Quy trình quyết định có thể bác bỏ

1. **Xác định task và claim**: L0–L5, input fields/band/cohort, observed vs reconstructed vs synthetic vs counterfactual; pin source/version và protocol. Không có mapping: NO-GO cho empirical use.
2. **Kiểm cổng phù hợp**: Gate B scoped hoặc Gate A strict theo bảng; đối chiếu [protocol](GATE_A_VS_B_PROTOCOL.md) và [risk matrix](PHASE02_DEPENDENCY_AND_RISK_MATRIX.md). Thiếu quyền/data/attestation: BLOCKED, không PASS nhờ CI xanh.
3. **Đánh giá failures**: identity/integrity/leakage hoặc unexplained numeric mismatch: FAIL và quarantine; provider/access gap: BLOCKED. Kết quả không có cascade, không arbitrage profit hoặc forecast không hơn baseline không tự gây FAIL nếu thiết kế và evidence đúng.
4. **Commander ban hành quyết định riêng**: task scope, inputs, gates chấp nhận, execution boundary, tests, output claim class và stop criteria. Không có quyết định này: `PHASE02_NOT_AUTHORIZED`.
5. **Sau thực thi được phép trong tương lai**: review observed test outcomes/negative cases và publication gate riêng. Không nâng successful ingestion thành execution validation hoặc independent research replication.

## Điều kiện cần xem xét lại đề xuất

Reopen affected gate khi có bằng chứng reference checksum sai, thay registration/ABI, mismatch chưa giải thích, data leakage, incomplete band/portfolio hoặc attribution trái với giả định. Không phải mọi thay đổi đều cần thu lại toàn bộ: triage scope trước, giữ outputs bị ảnh hưởng trong quarantine, chỉ recheck có mục tiêu khi được phép. Nếu chỉ tìm thêm tài liệu kiến trúc tổng quát, trạng thái Gate A không đổi.

Commander được đề nghị nghiệm thu **protocol và evidence boundaries**, giữ nguyên mandatory status, rồi lựa chọn: cấp riêng L1/L2 với hạn chế trên; hoặc ưu tiên một prospective attested archive campaign. Không tự chọn provider trả phí, liên hệ support, phát hành tag, merge hoặc mở Phase02 trong PR này.
