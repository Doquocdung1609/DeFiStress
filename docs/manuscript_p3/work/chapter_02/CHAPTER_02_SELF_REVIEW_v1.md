# CHAPTER_02_SELF_REVIEW_v1

**Trạng thái đề nghị:** `CHAPTER_02_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW`.

Đây là **Work self-review** kết hợp đọc nội dung và kiểm tra tĩnh bằng công cụ; không phải external peer review, Codex technical sign-off hoặc một lượt kiểm toán lại P2/G0. Commander quyết định nghiệm thu và Chapter Lock.

## 1. Source anchors và phạm vi thực hiện

- Scientific Lock: `3f6e5302483681209e2408531eb5a15389f9fded`.
- Blueprint Lock: `8de52bebabef376be700836e6f93a92d7394d2c3`.
- Ch1 Lock / starting integration: `88dbc4234378b5bbcc61b73700a0c5298f66225f`.
- Đọc [Commander Chapter 01 Lock](https://github.com/Doquocdung1609/DeFiStress/issues/3#issuecomment-6208965565): đã cấp `CHAPTER_02_FULL_DRAFT_AUTHORIZED` cho nhánh Work mới, giữ Ch1 và sources bất biến. Đã đọc directive đính kèm hiện tại, không xin gate Evidence Pack riêng.
- Đọc toàn văn Ch1 tại lock và các phần liên quan của bộ P2/registry/Blueprint; đọc code vừa đủ để xác nhận portfolio, liquidation gates, token units, tick/reposition, policies và graph. Không mở engine audit hoặc research search mới.
- Output chỉ ba file dưới `docs/manuscript_p3/work/chapter_02/`; output SHA được ghi ở PR/handoff, không tự chèn vào file.

## 2. Cấu trúc và chức năng học thuật

Năm mục chính và14tiểu mục dùng nguyên văn titles Blueprint. Các nhóm nội dung trong directive được đặt vào headings này, không tạo một outline mới theo chín nhóm chủ đề. T2.1 ở2.5.1, không tạo thêm figure hoặc equation display.

| Mục | Lập luận được phát triển | Phạm vi review |
|---|---|---|
| 2.1 | HF là quan hệ giá trị; LTV/LT/bonus có ba cơ chế; động cơ và các ràng buộc xử lý | Phân biệt portfolio/route/execution; reference protocol khác project rules; không bot-market calibration. |
| 2.2 | Range/tick tạo độ sâu có hướng; giá bình quân/slippage khác giá biên; oracle và arbitrage là hai mắt xích riêng | Token order/decimals, reference price, A/B/C giả định và price repositioning được đặt rõ. |
| 2.3 | Stablecoin có vai trò khác theo phía bảng cân đối; định giá nợ khác quy đổi/thanh toán | USDC quantity khác USD-equivalent; S15 tác giả cá nhân, S16 issuer, S17/S18 cùng nghiên cứu. |
| 2.4 | Phương pháp được chọn theo đối tượng: static/scenario/ABM/MC; network biểu diễn cấu trúc khác distress | ODD không tự chứng nhận; conditional uncertainty, selected/prefix mẫu; betweenness khác DebtRank. |
| 2.5 | So sánh estimand, thiết kế, horizon và access; rút ra yêu cầu cho mô hình | T2.1 tổng hợp phản biện; không dùng Policy-A Wave2 bác empirical S13, không causal history hoặc gap toàn ngành. |

## 3. Academic và scientific consistency review

**Scientific accuracy — PASS_CONTENT_SELF_REVIEW.** Các luận điểm nhân quả mạnh được đọc lại theo chuỗi điều kiện. Giảm giá tài sản chỉ làm HF thay đổi theo quy tắc định giá; HF mất an toàn không đồng nghĩa thực thi. Các yếu tố vốn/công suất/chi phí/thời gian được tách, không quy mọi skip về profitability. Price impact ở DEX không tự là giá oracle và không xác nhận lây lan Mainnet. Các đồng nhất thức định giá được giải thích bằng lời, không gán chúng thành đặc tả đầy đủ của Aave V3.

**Academic argument — PASS_CONTENT_SELF_REVIEW.** Mỗi phần phát triển biến trung gian và điều kiện: từ giá trị bảo đảm đến khả năng xử lý; từ khoảng thanh khoản đến thực thi; từ điều chỉnh giá đến transmission; từ cấu trúc mô hình đến phạm vi suy luận. Literature được đối thoại theo vấn đề, không xếp thành các đoạn tóm tắt tác giả nối tiếp. Phần cuối rút ra nhóm biến và yêu cầu kiểm chứng, không lặp ba đóng góp hoặc toàn bộ bố cục Ch1.

**Citation — PASS_WITH_DECLARED_ACCESS_LIMITS.**29 source records từ P2 được dùng theo vai trò, không gọi29nghiên cứu peer-reviewed độc lập. Abstract/preview/code/documentation/forum/issuer sources được tách trong audit vàT2.1. Không thêm hệ số, sample size hoặc định lý chưa đọc; không nâng nguồn thành fulltext. S13 giữ phát hiện không tìm tác động giá kéo dài có ý nghĩa theo thiết kế, khác với modeled Wave2 ở các stress cases Policy A. S17/S18 vẫn một công trình với hai phiên bản.

**Language và chapter boundary — PASS_CONTENT_SELF_REVIEW.** Thân chương dùng đoạn văn có cơ chế, điều kiện và hàm ý; không danh sách code/module. Không lặp sáu RQ nguyên văn hoặc454/109, không chuyển số liệu Wave2/MC/historical/Terra/network vào phần lý thuyết. Inline HF/tên biến phục vụ giải thích; equations/timing/algorithm thuộc Ch3. Không viết Ch3 trong lần này.

## 4. Targeted repairs thực tế

| Finding | Loại và vị trí | Hành động đã thực hiện | Recheck |
|---|---|---|---|
| CH02-R01 | Legacy Ch2 chỉ định nghĩa ngắn và dễ đồng nhất HF với giao dịch xử lý | Viết lại2.1 theo danh mục, tuyến, planning/execution; không chép đoạn legacy | C03 và schema/planner/Addendum; đọc nội dung và kiểm accepted scope. |
| CH02-R02 | Legacy viện dẫn CPMI và mô tả mạng nhiều lớp/ABM rộng hơn implementation | Dùng Kosse et al.; giới hạn graph gộp, representative agents và DebtRank chưa triển khai | P2 APA/Matrix, C14/C19/C26/C28, source code đã đọc. |
| CH02-R03 | Bản soạn đầu2.5.2 lặp cách giải thích horizon đã có ở2.2.2 | Thay đoạn đầu bằng tiêu chí so sánh đại lượng/độ phân giải/nơi đo và cảnh báo ghép bằng chứng khác cấp | Đọc lại vai trò hai mục; không thay kết quả S13 hoặc model. |
| CH02-R04 | Bản soạn đầu dùng NIST trước khi giới thiệu tên tổ chức | Viết đầy đủ National Institute of Standards and Technology ở lần đầu, giữ NIST cho bảng | Đối chiếu S24; method không đổi thành Agresti–Coull theo tên trang. |
| CH02-R05 | Audit draft rút gọn một số locators thành1.3/1.2 gây mơ hồ | Sửa về2.1.3/2.1.2 đúng tiểu mục | Kiểm bảng audit và headings. |

R01–R02 là sửa khi kế thừa legacy; R03–R05 là sửa bản soạn trong cùng lượt. Không dựng một scientific FAIL giả để tạo repair log. Không có numerical/source change.

## 5. Kiểm tra tĩnh thực tế

Lệnh **`python verify_chapter02.py` — PASS** kiểm:

- 5/5 headings và14/14subheadings khớp nguyên văn Blueprint; các tiểu mục có nội dung, không placeholder.
- T2.1 đúng12nhánh/7cột, caption/provenance và textual synthesis; không thêm statistics.
- 31 accepted P2 records được dùng ở mức nền tảng/giới hạn, bao phủ12/12primary Ch2; primary/secondary destinations trong audit khớp JSON gốc. Không dùng bốn disallowed IDs làm affirmative.
- 29 bibliography entries khớp nguyên mục P2, không URL/DOI mới; chưa dùng S30 hoặc U records.
- 36 source blobs được tải/đối chiếu tại đúng ba source anchors, gồm nguyên Ch1. Source cache chỉ tái dùng khi bytes khớp Git object đã fetch; không dùng default branch để nâng version.
- Không RQ gốc bị lặp/viết lại; không equation display mới hoặc số liệu dành cho Ch5/6.
- Không có đoạn văn dài chép nguyên từ Ch1 theo phép so normalized paragraphs; đây là chỉ báo sao chép chính xác, không phải đo đầy đủ trùng ý. Mức phát triển khái niệm mới được Work tự đọc đánh giá.

Không chạy simulation/Monte Carlo, replay, RPC/fork, statistical estimation hoặc tính khoảng tin cậy mới. Không chạy lại bộ pytest khoa học hoặc nhận test Codex trước đây là independent Work run. Kiểm tra chữ/nguồn không tự chứng minh external validity của mô hình.

## 6. Hạn chế và Commander review

`TEMPLATE_VERIFICATION_PENDING` còn hiệu lực cho bản DOCX cuối và chuẩn trường; author–year là working convention kế thừa Ch1. Source-access của P2 và hai raw borrower CSV lớn chưa đọc đầy đủ/cell-by-cell được giữ. Hash LF Git blob và Windows CRLF checkout là hai miền bytes khác nhau.

Các contextual references từ claims có primary ởCh3/6/7 được dùng để định nghĩa hoặc công bố giới hạn theo narrative Blueprint Ch2, không chuyển primary destination. Đóng góp/numerical findings vẫn ở chương được phân bổ. Đây là cách dùng nhất quán nonblocking note của Commander khi khóa Ch1; audit chép nguyên destinations để người review kiểm tra.

Commander cần xem chiều sâu so sánh, sự vừa đủ của phần2.4network/MC, cách trình bày T2.1 với số cột lớn khi chuyển định dạng, và mức phát triển so với Ch1. Markdown chưa thực hiện layout DOCX hoặc visual QA. Bảng nguồn dài không phải một phát hiện mới; việc chọn references được đánh giá theo chức năng trong lập luận.

**Scientific blockers phát hiện: không có.** Chưa có external academic review hoặc Codex chapter review được thực hiện trong vòng này. Không kích hoạt Codex vì chưa phát hiện bất nhất công thức/đơn vị/provenance cần xử lý riêng.

**CHAPTER_02_FULL_DRAFT_READY_FOR_COMMANDER_REVIEW — STOP, AWAIT COMMANDER CHAPTER 02 REVIEW.**
