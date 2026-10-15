# P3_CHAPTER_ACCEPTANCE_RUBRIC

**Status: PROPOSED — AWAITING_COMMANDER_BLUEPRINT_APPROVAL.** Rubric áp dụng sau G0 approval, không tự cho phép viết Chương 1 hoặc cấp chapter lock. Scientific lock giữ nguyên tại `3f6e5302483681209e2408531eb5a15389f9fded`.

## Checkpoint và bằng chứng phải có

| Checkpoint | Tài liệu/kiểm tra | Người sở hữu | Điều kiện qua |
|---|---|---|---|
| CP1 Evidence Pack | CHAPTER_N_EVIDENCE_PACK: accepted IDs, RQ, source access, result/selector/commit, formulas, exhibits và limitations | Work tạo yêu cầu; Codex cung cấp numerical exhibit pack riêng | Không có excluded ID trong affirmative set; nguồn pin; exhibit chưa có được ghi request/pending |
| CP2 Academic Draft | Bản Markdown có version, luận điểm, bằng chứng, giải thích kinh tế và liên kết tiểu mục | Work | Đủ mục tiêu/luận điểm của chapter; đoạn quan trọng truy nguồn; không liệt kê code thay phương pháp |
| CP3 Technical Reconciliation | Finding log về số, denominator, units, formula semantics, policy/cohort, captions và locator | Codex, ghi trong codex/ | Không P0/P1; không sửa trực tiếp prose Work; kết quả test gắn executor/command/commit |
| CP4 Academic Self-review | Kiểm tính đúng, tổng hợp literature, logic, chiều sâu, ngôn ngữ, đóng góp và citation | Work, ghi rõ self-review | Đối thoại nguồn đúng mức; main point trước, scope sau; không nói self-review là independent external review |
| CP5 Targeted Repair | Finding ID → location → cause → repair → evidence → recheck | Owner của file | Chỉ sửa findings đã xác định; conflict scientific lock phải báo Commander, không tự unlock |
| CP6 Commander Chapter Lock | Version, exact SHA, accepted IDs, RQs, exhibit IDs, citation checks, reviews, limitations và remaining issues | Commander | Phê duyệt tường minh, không P0/P1; chỉ sau đó mới phát hành CHAPTER_N_LOCKED |

## Mức nghiêm trọng

P0: mâu thuẫn scientific lock, số liệu không được hỗ trợ, giả citation/ID, promotion excluded claim, causal Mainnet/actual-oracle claim trái bằng chứng, hoặc nâng mức xác minh nguồn. Dừng phần phụ thuộc và báo Commander; không sửa số để cứu prose.

P1: thiếu qualifier làm đổi nghĩa; nhầm eligible/executed hoặc mẫu số; formula/unit/timing sai; nguồn không resolve; không giữ negative findings; draft không trả lời đúng mục tiêu chương. Chưa được chapter lock.

P2: diễn đạt chưa rõ hoặc lặp nhưng không đổi scientific meaning; caption/cross-reference chưa thống nhất và sửa được. Chỉ để nonblocking khi Commander chấp thuận rõ với owner/điều kiện xử lý.

P3: lỗi hình thức nhỏ, chỉ chốt sau template verification. Không dùng điểm tổng hợp hoặc số test để bù P0/P1.

## Các tiêu chí chung

1. **Academic correctness:** khái niệm và quan hệ đúng nguồn; code facts dùng code/project evidence, không gắn thành scholarly empirical finding. Conceptual claim không phải có numerical result.
2. **Literature integration:** so sánh câu hỏi, thiết kế, horizon và phạm vi; phân biệt abstract/preview/full content. S17/S18 cùng nghiên cứu; U01–U08 chưa được promotion.
3. **Explanatory depth:** mỗi tiểu mục có câu hỏi trọng tâm, luận điểm, bằng chứng, cơ chế kinh tế và kết nối; đủ để độc giả hiểu vì sao có hoặc không có kết quả.
4. **Logical coherence:** dữ liệu quan sát, giả định, kiểm chứng và kết quả có vị trí riêng; không lấy kết quả để chứng minh lại giả định hoặc causal claim của bài nguồn.
5. **Measurement:** units, denominator, scenario/policy/cohort và thời điểm đo hiện cạnh kết quả; token USDC khác USD, ratio khác percent, delay khác recovery, impact khác residual.
6. **Style:** tiếng Việt tự nhiên, dùng thuật ngữ đã khóa; dẫn main point trước rồi scope/limits. Không lặp câu phủ định máy móc, không cường điệu để tăng độ mạnh và không thêm filler để tăng trang.
7. **Contribution:** chỉ ra phần tích hợp/đối chiếu/truy vết trong scope; không first-ever, superiority hoặc calibrated live-risk prescription nếu không có bằng chứng.
8. **Provenance:** exact commit/path/selector, result và exhibit IDs resolve; cite source theo chức năng; không equate CRLF/LF hashes hoặc reported tests với actual Work execution.
9. **Boundaries:** giữ mandatory limitations đúng nơi; tần suất MC có điều kiện, selected paths, one pool/cohort, representative agents, actual feed/fork chưa xác minh, USDC scope, noncausal history, aggregate network, Terra negative và hai CSV chưa đọc đủ.
10. **Completeness without repetition:** primary chapter phát triển claim, secondary dùng dẫn chiếu có chức năng khác; không nhồi44claims vào literature hoặc chép lại nguyên kết quả trong discussion.

## Tiêu chí riêng từng chương

| Chương | Câu hỏi nghiệm thu | Điều kiện bắt buộc |
|---|---|---|
| 1 | Vấn đề, khoảng trống và phạm vi có tạo thành một thiết kế nghiên cứu rõ? | 6/6 câu hỏi nguyên văn; khoảng trống giới hạn bộ literature; đóng góp dự kiến không vượt kết quả; bố cục bảy chương chỉ sau approval |
| 2 | Literature được tổng hợp và phản biện thay vì liệt kê? | S10/S11/S13 đúng thiết kế/horizon/access; phân biệt theory/code/project; các khái niệm được dùng tiếp ởCh3/Ch5 |
| 3 | Người đọc có thể hiểu giả định, phương trình và quá trình mô phỏng? | Policy A/B/C và timing rõ; gates, agents, units, Monte Carlo/prefix selection đúng; thiếu fidelity được công bố |
| 4 | Chất lượng dữ liệu đủ để đánh giá kết quả có điều kiện? | 454/109 tách; HF gần ngưỡng khác cực trị; source lineage; không full-market/full-protocol validation hoặc test run chưa làm |
| 5 | Sáu RQ có kết quả và giải thích cơ chế? | 4/0/0/0;10/0/0/2 đúng selected sets;280/10k Policy A;35/14 khác execution;36 no modeled USDC;impact/residual và3risk parameters riêng |
| 6 | Quan sát lịch sử và extensions có đúng cấp bằng chứng? | 28/27,1/2/23/1 không causal; negative Terra được giữ; graph gộp không full multilayer; không thay sáu RQ |
| 7 | Đóng góp và kết luận đủ sức bảo vệ mà không thêm claim? | 6 accepted answers nhất quán Ch5; contribution có giới hạn; đủ limitations; future work không biến thành kết quả hiện tại |

## Template và assembly

`TEMPLATE_VERIFICATION_PENDING` không chặn lập luận và nội dung G0. Các quy định font, margins, style/caption/equation numbering và bibliography của trường chỉ được áp dụng như yêu cầu chính thức khi có tài liệu xác minh. APA author–year là convention làm việc tạm thời.

Chỉ khi cả bảy chương được Commander khóa mới ghép, soát liên chương, chuẩn bibliography và dựng DOCX tự động Heading/Caption/Equation/Cross-reference/TOC/LOF/LOT theo template. G0 không tạo Word final.
