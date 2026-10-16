# CHAPTER_03_SELF_REVIEW_v1

**Đề nghị:** `CHAPTER_03_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.

Đây là tự rà soát của Work và kiểm tra nội dung/nguồn tĩnh bằng công cụ. Không phải phản biện ngoài độc lập hoặc một đợt chạy lại numerical validation. Bản thảo hoàn chỉnh để Commander nghiệm thu học thuật và kiểm tra kỹ thuật có mục tiêu; Work chưa cấp `CHAPTER_03_LOCKED`.

## 1. Mốc và phạm vi

| Vai trò | Phiên bản |
|---|---|
| Scientific Lock | `3f6e5302483681209e2408531eb5a15389f9fded` |
| Blueprint Lock | `8de52bebabef376be700836e6f93a92d7394d2c3` |
| Starting integration / hai chương đã khóa | `cba9c58e36f269aa717bda20ac66ffc63acc77a5` |
| Nhánh bàn giao | `research/p3-ch03-full-manuscript-work` |
| Final commit | Ghi bằng exact SHA trong PR/Git handoff, không tự nhúng SHA của chính file |

Đã đọc toàn văn Chương 1–2 tại starting integration; giữ nguyên cả hai. Đã đọc Blueprint, registry, P2 và implementation đúng ref; danh sách 55 file và Git blob nằm trong audit. Không nghiên cứu literature mới, không nâng source access, không chạy simulation/Monte Carlo/RPC. Chỉ bàn giao ba file thuộc Work/chapter_03; các script kiểm nội dung cục bộ không trở thành thay đổi repository.

## 2. Mức hoàn thiện theo Blueprint

Blueprint thực tế có **6 mục cấp 2 và 15 tiểu mục cấp 3**. Đối chiếu nguyên văn từng heading cho thấy đủ và đúng thứ tự; không dùng số 16 từ ghi chú sơ bộ thay cho cấu trúc nguồn.

| Mục | Nội dung đã hoàn thành | Tự đánh giá |
|---|---|---|
| 3.1 | Lớp quan sát/tái dựng/mô phỏng; mô hình trạng thái; shock alignment; lịch đầu wave, trong wave và cuối wave; điều kiện dừng | Đủ để theo dõi cơ chế; F3.1 thể hiện cả vòng xét vị thế và vòng wave |
| 3.2 | Người vay thụ động; HF danh mục; close factor/dust; tuyến WETH/USDC; vốn/công suất/lợi nhuận; lý do skip; arbitrage đại diện | Đối chiếu từng cổng với code; không gán tối ưu hóa hay cơ chế bot chưa có |
| 3.3 | HF và dạng aggregate triển khai; USDC/USD; V3 token order/fee/tick; metrics/depth/recovery/composite tail | Định nghĩa trước kết quả, rõ units/thời điểm đo |
| 3.4 | A/B/C, cấu hình weak/moderate, completed-wave history và min-cap | Đúng hypothetical policy; không actual Aave/Chainlink |
| 3.5 | Lưới 32/60, sensitivity, targeted 4/4/10, distributions/clipping, batch/prefix, Wilson | Chỉ thiết kế và mẫu số; không đưa kết quả Chương 5 vào |
| 3.6 | Verification, tái dựng, reproducibility, historical comparison, external validity và provenance | Phân biệt phạm vi; không đổi inherited checks thành Work execution |

Các tiểu mục phát triển bằng văn xuôi phương pháp; không tổ chức thành API guide. Không chép nguyên đoạn dài từ Chương 1–2. Chương 4 chỉ được nhắc như bước tiếp theo, chưa được viết.

## 3. Công thức và exhibits

| Nhóm | Kết quả thực tế |
|---|---|
| E3.1/E3.4/E3.5/E3.6/E3.8 | 5/5 trong thân bài, nguyên LaTeX Work đã khóa |
| E3.2/E3.3/E3.7 | 3/3 ở phụ lục A.1–A.3 trong cùng file; không ép vào thân bài |
| T3.1 | Bảng đầy đủ tác nhân/thông tin/cổng/trạng thái/giới hạn, tổng hợp trực tiếp từ code |
| T3.2 | Bảng đầy đủ thiết kế, đơn vị mẫu, policy và RQ; không có success counts |
| T3.3 | Từ điển biến/chỉ tiêu có units, cấp phân tích, locator và RQ |
| F3.1 | Mermaid `SCHEMATIC_FROM_LOCKED_MODEL_SPEC`; có nội dung và caption, chưa là Codex-rendered publication figure |

Không thay mapping template đã duyệt; trạng thái văn bản/schematic của lượt này không biến `CODEX_SPEC_REQUIRED` thành `RENDERED`. Final figure rendering/typesetting là việc sản xuất sau, không phải thiếu nội dung phương pháp.

## 4. Những điểm phát hiện và sửa có mục tiêu

| Finding | Vị trí | Sai khác/rủi ro phát hiện | Sửa trong bản cuối | Đối chiếu lại |
|---|---|---|---|---|
| CH03-R01 | 3.1.2 / F3.1 | Flow khái niệm có thể khiến người đọc tưởng HF/tập eligible cập nhật sau từng sale | Nêu tập và valuation chốt đầu wave; quote thay đổi theo pool; tách intrawave HF reporting | Engine các dòng 97–118, 163–201, 222–226; schematic theo đúng hai tầng lặp |
| CH03-R02 | F3.1 | Schematic nháp gộp delay vào nút được lặp và chưa vẽ vòng ứng viên | Tách bước chờ ban đầu; thêm kiểm còn vị thế trong danh sách trước arbitrage | So thứ tự engine; không có lặp delay mỗi wave |
| CH03-R03 | 3.2.1 / 3.3.1 / E3.1 | HF tổng quát dễ bị đọc thành định giá từng reserve, hoặc LT override áp toàn danh mục | Giải thích WETH override riêng; other collateral giữ recorded LT/tổng USD | `BorrowerPosition.health_factor` |
| CH03-R04 | 3.2.2 / E3.5 | Đồng nhất eligible/route/attempted/executed; tưởng mọi skip được xét lại | Tách ba chỉ báo, cổng xét và tập loại khỏi xét; capacity skip có ngoại lệ; zero-positive wave dừng | `plan_liquidation`, `Liquidator.evaluate`, engine 120–142, 256 |
| CH03-R05 | 3.2.2 / 3.3.1 / E3.8 | Dust/seize/profit dễ bị mô tả như full USD repricing | Nêu dust nợ dùng token USDC; E3.8 chỉ thành phần nợ; seize/profit còn danh nghĩa | Liquidation planner, schema debt_value; C35 |
| CH03-R06 | 3.3.2 / A.1–A.2 | Nhầm chiều token, giá nghịch đảo, fee hoặc formula tick | Giữ token0 USDC/6, token1 WETH/18; raw net amounts; không chép floor tick làm identity code | `spot_price`, `sell_weth`, `tick_from_sqrt_price_x96` |
| CH03-R07 | 3.2.3 / 3.3.3 | Nhầm ngưỡng arbitrage với recovery; nhầm funded swap | Tách 0,05% trigger và 0,5% recovery; tái định vị có cập nhật L, không capital execution | `Arbitrageur.act`, engine `RECOVERY_TOLERANCE`, `arbitrage_toward` |
| CH03-R08 | 3.5 / T3.2 | Có thể gộp prefix/P0v2/Level3 hoặc diagnostic với preset Severe | Tách từng version và unit; diagnostic common parameters lấy selection manifest; targeted không probability sample | Frozen tables, selection, MC batches/checkpoint và scripts |
| CH03-R09 | A.3 / audit | Tên helper và dòng số kế thừa không luôn đúng source đang đọc; 1,96 là xấp xỉ | Dùng `_wilson` thực tế, chỉ rõ normal quantile 0,975; sửa locator E3.6 sang runner:90 | Đọc source có số dòng, không tính CI mới |
| CH03-R10 | Tham khảo | Sao mục tác giả Grimm thủ công có thể lặp tên | Thay toàn bộ 15 entries bằng nguyên mục APA P2 đã khóa | Kiểm chuỗi từng entry và URL; không nguồn mới |

Các sửa trên là làm rõ bản thảo theo nguồn hiện có, không sửa code/registry/numerical evidence. Chưa thấy scientific blocker mới; các giới hạn đơn vị depeg và arbitrage đều là giới hạn đã khóa được công bố, không được che bằng công thức mới.

## 5. Kiểm tra đã thực hiện

Lệnh chạy cục bộ: `python build_chapter03_audit.py` và `python verify_chapter03.py`. Lệnh thứ nhất tổng hợp sidecar từ các nguồn đã truy xuất; lệnh thứ hai kiểm nội dung và provenance tĩnh. Không import hoặc gọi engine để chạy kịch bản. Các lỗi ban đầu của bộ kiểm (đếm sơ bộ 16 thay vì 15 heading, đếm cả dấu đóng display math, tên trường JSON) đã được sửa theo schema/Blueprint rồi chạy lại; không sửa tài liệu khoa học để chiều theo bộ kiểm.

| Nội dung kiểm bằng công cụ | Kết quả |
|---|---|
| Headings nguyên văn Blueprint | PASS — 6/6 + 15/15 |
| LaTeX và placement Work | PASS — 8/8, 5 thân bài + 3 phụ lục |
| Primary allocation Chương 3 | PASS — 13/13; giữ nguyên primary/secondary |
| Accepted components dùng thực tế | PASS — 21 records: 18 P2 + 3 Integration, đều affirmative; không phát triển số liệu kết quả của C23 tại đây |
| Bốn disallowed | PASS — có safeguard trong audit, không trong manuscript như affirmative premise |
| Sáu RQ | PASS — nguyên văn trong bảng kiểm sidecar, giữ phạm vi; không viết lại hay lặp câu hỏi đầy đủ trong chương |
| Trích dẫn | PASS — 15 entries đúng P2, URL không phát sinh, access labels kế thừa |
| Source integrity | PASS — 55 Git blob checks với ref đúng; không đồng nhất CRLF/LF hoặc SHA1/SHA256 |
| Thứ tự engine | PASS — đối chiếu tĩnh thứ tự haircut → align → eligible → quote/sale → arbitrage → history/valuation → stop |
| Mẫu số đọc trực tiếp | PASS — selection 4 mục tiêu/4 đối chứng/10 targeted × 4 policies; 72 summary rows; MC prefixes/batches riêng |
| Lặp nguyên văn Chương 1–2 | Không có đoạn văn dài trùng theo kiểm tra chuỗi; các khái niệm cần thiết được đặc tả bằng chức năng phương pháp |
| Phạm vi sản phẩm | Ba file Work; không chương mới tiếp theo, không final DOCX |

Đánh giá độ sâu, độ tự nhiên tiếng Việt và độ rõ của lập luận là self-review nội dung, không phải kết quả tự động suy ra từ độ dài hay số test. Lượt này không nhận một đánh giá Codex độc lập mới; Commander là cổng nghiệm thu.

## 6. Giới hạn còn lại và điểm Commander cần xem

Hai CSV borrower lớn vẫn chưa được đọc trực tiếp toàn bộ: Oracle `borrower_level_evidence.csv` và Integration `eligible_vs_executed_audit.csv`. Work đã đọc code, manifests và summary, không tuyên đối chiếu từng raw cell hoặc replay mới. Nhãn `WORK_INDEPENDENT_STATIC_RECONSTRUCTION` của P2, `CODEX_REPLAY_VERIFICATION` và `CODEX_PREMERGE_AUDIT` được giữ đúng vai trò thừa kế.

Commander nên kiểm có mục tiêu ba chỗ nhạy: HF aggregate/other LT; lịch valuation và danh sách wave; quy ước USDC danh nghĩa trong seize/profit khi thảo luận RQ5. Văn bản đã nêu rõ các giới hạn, không mở rộng chúng thành lỗi thực nghiệm mới hoặc lén sửa implementation. Depth sau wave đầu có thể gồm backlog nên không được dùng một mình để quy nguyên nhân cho phản hồi nội sinh.

Nguồn abstract/preview chưa nâng fulltext; các hàng kiểm chưa có quyền đại diện toàn Mainnet. Arbitrage chưa funded executable swap, local-fork execution chưa được xác nhận độc lập, chính sách giá chưa hiệu chỉnh với Aave oracle lịch sử, và haircuts 90%/95% vẫn là extreme counterfactual tails. Các giới hạn này được đặt ở đúng phần phương pháp thay vì lặp phủ định ở mọi đoạn.

`TEMPLATE_VERIFICATION_PENDING` còn chặn final DOCX formatting khi chưa có quy định trường được xác minh; không chặn review nội dung chương Markdown. F3.1 cần bước rendering sản xuất về sau, các bảng đã có nội dung đầy đủ trong bản thảo.

**Scientific blockers phát hiện trong lượt này: không có.** Đề nghị Commander review bản đầy đủ và thực hiện technical spot-check theo các điểm trên. Dừng tại `AWAIT_COMMANDER_CHAPTER_03_REVIEW`; không tự cấp chapter lock, không viết Chương 4.
