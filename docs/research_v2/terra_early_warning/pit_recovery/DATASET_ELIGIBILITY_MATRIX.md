# Terra — ma trận điều kiện point-in-time

Nguồn kiểm toán: PR #51, HEAD `8ec1eb2c49c1d4c3088b2bb0550b38fb6a05bde5`, đã tích hợp tại `053e94cb722f15eed689814c5a7771fa8f881be8`. Quyền: `V2_TERRA_P04_01_REVIEW_AND_PIT_EVIDENCE_RESEARCH_AUTHORIZED`. Ngày rà soát: 21/10/2026. Các quyết định dưới đây dành cho nghiên cứu V2, không sửa dữ liệu hay diễn giải V1 đã khóa.

## Quy tắc quyết định

Một giá trị quan sát, một thời điểm hiển thị và một thời điểm người quan sát nhận được dữ liệu là ba đối tượng khác nhau. `POINT_IN_TIME_ELIGIBLE` đòi hỏi ánh xạ nguồn–asset–đơn vị–phiên bản, khoảng thời gian quan sát, bằng chứng khả dụng, kiểm soát sửa đổi và quy tắc quyết định được duyệt. `BLOCKED_INSUFFICIENT_AVAILABILITY_EVIDENCE` nghĩa là còn thiếu bằng chứng; không có nghĩa dữ liệu chắc chắn chưa tồn tại trong lịch sử. `REJECTED` được gắn với **mục đích sử dụng cụ thể**, không xóa bản ghi gốc.

Ledger máy đọc được: [PUBLICATION_TIME_EVIDENCE_LEDGER.json](PUBLICATION_TIME_EVIDENCE_LEDGER.json). Nó chứa SHA-256/Git blob của bốn tài liệu Git ngoài dự án và ba tệp repository đọc bổ sung; hash của trang web chưa tải bytes nguyên bản để `null`. Những trang lỗi truy cập không được coi là đã xác minh nội dung.

## 14 trường của bảng mở rộng

Tất cả cùng tham chiếu `data/processed/terra_extended/terra_state_hourly_20220301_20220513.csv` tại integration nêu trên và các mục `core_fields` trong registry P04-01. Có 12 trường kinh tế và hai tọa độ; không gọi cả 14 là 14 chỉ báo dự báo độc lập. Trạng thái của **từng dòng** hiện là `BLOCKED_INSUFFICIENT_AVAILABILITY_EVIDENCE`.

| Trường | Đơn vị / vai trò | Bằng chứng mới hoặc điều kiện còn thiếu |
|---|---|---|
| `timestamp` | Nhãn giờ UTC; tọa độ | Nhãn đầu giờ không chứng minh dữ liệu đã hoàn tất tại đầu giờ. Không phải tín hiệu kinh tế tự thân. |
| `block_height` | Chiều cao Terra; định danh hỗ trợ | Cần header/hash/chain `columbus-5`, height thực của state query và thời điểm khả dụng; không chỉ chiều cao được lấy mẫu. |
| `ust_price` | USD/UST theo nhãn nguồn | Đã xác minh khác biệt hourly-last và backward-as-of ở hai giờ tranh chấp; ngữ nghĩa minute bar và vintage Kaiko vẫn thiếu. |
| `luna_price` | USD/LUNA theo nhãn nguồn | Cùng khác biệt thời gian; không chuyển mặc định hợp đồng Binance sang giá tổng hợp nhiều sàn. |
| `ust_supply` | UST | Mã hình nguồn dùng tổng balance/1e9 để biểu diễn tỷ UST; cần đối chiếu schema/đơn vị raw pack trước bất kỳ rebuild nào. |
| `luna_supply` | LUNA | State theo giờ cần effective time/header và vintage; không dùng thời điểm file hiện tại làm thời điểm lịch sử. |
| `anchor_total_deposits` | UST suy dẫn | Hợp đồng phân biệt `prev_*` và epoch state. Cần code ID triển khai, state height thật, aUST scaling và kỳ tính lãi. |
| `anchor_deposit_flow` | UST trên khoảng một giờ | Tổng sự kiện `[h,h+1h)` chỉ hoàn chỉnh sau cuối khoảng và độ trễ; cần chứng minh đủ sự kiện và đúng chiều. |
| `anchor_withdrawal_flow` | UST trên khoảng một giờ | Điều kiện như dòng trên; thiếu không phải zero. |
| `ust_native_redemption_volume` | UST trên khoảng một giờ | Cần raw transaction/action, completeness, interval closure và thời điểm phát hành. |
| `gross_luna_issuance_from_native_swaps` | LUNA trên khoảng một giờ | Cần xác minh output/fee semantics và thời điểm khả dụng của mọi thành phần. |
| `backing_ratio` | Tỷ số suy dẫn | Thời điểm khả dụng là max của các đầu vào cộng xử lý; đây không phải tỷ lệ bảo chứng tài sản theo nghĩa đen. |
| `top10_anchor_share` | Phân số | Effective time của daily holder snapshot, cohort và publication chưa xác minh; không ngoại suy sau 06/05. |
| `top100_anchor_share` | Phân số | Cùng điều kiện; kéo giá trị ngày sang lưới giờ không tạo quan sát độc lập mới. |

Kết quả: **0/14 bản ghi được thông qua cho forecasting ở checkpoint này**. Tính toàn vẹn bytes của 35 tệp vẫn PASS. Hai kết luận đo các thuộc tính khác nhau.

## Những cách dùng bị loại

| Trường legacy / mục đích | Quyết định | Căn cứ |
|---|---|---|
| `curve_ust_price` như giá quan sát riêng của Curve | `REJECTED` | Manifest legacy trỏ về cùng Parquet giá UST tổng hợp; tên cột không tạo nguồn giá Curve độc lập. |
| `terra_dex_liquidity` như thanh khoản thực thi lịch sử | `REJECTED` | Nguồn ghi rõ proxy từ volume thị trường 24 giờ chia 24. |
| `terra_dex_depth` như độ sâu lịch sử có thể khớp lệnh | `REJECTED` | Quantile volume cố định không phải sổ lệnh hay pool reserves. |

Ba dòng là ba quyết định về **use case**, không cộng vào mẫu số 14 trường để tạo “17 dataset”. Có thể giữ proxy trong một giả thuyết phản thực có nhãn rõ sau khi được duyệt; không dùng nó xác nhận thoát vị thế lịch sử.

## Nguồn ứng viên mới và khả năng thu hồi

| Ứng viên | Đã xác minh | Chưa xác minh / trạng thái dùng làm predictor |
|---|---|---|
| Binance websocket trước sự kiện, PIT-R01 | Phiên bản Git 09/03/2022 có `T`, `E`, `t`, `x` và quote asset | Chưa có capture UST/LUNA, receipt time, vintage equivalence hay symbol/window coverage: `BLOCKED_INSUFFICIENT_AVAILABILITY_EVIDENCE`. |
| Binance daily/monthly archive, PIT-R02/R03 | Tài liệu trước sự kiện mô tả tải ngày kế tiếp; tài liệu hiện tại công bố việc thay thế archive và checksum cũ/mới | Chưa đọc tập checksum revision, file thị trường hoặc chứng cứ upload đầu tiên. Không mặc định archive khả dụng cùng lúc giao dịch. |
| Anchor/columbus-5, PIT-R04–R06 | Schema query trước sự kiện và tài liệu phân biệt state lưu / state cộng dồn lãi | Chưa xác minh code triển khai, header/receipt và quyền archive thực tế. Tham số `block_height` không đủ pin lịch sử. |
| Curve Ethereum, PIT-R08/R10 | Báo cáo có candidate block/hash và mô tả chuỗi sự kiện | Explorer từ chối truy cập; chưa readback receipt/state/ABI. Không xác nhận reserves hay execution. |
| BTC/ETH và stablecoin đối chứng | Đã đặc tả yêu cầu chung nguồn/clock/vintage | Chưa có panel point-in-time được nghiệm thu; không lấy dữ liệu Ethereum hiện tại thay bối cảnh năm 2022. |

Không có nguồn số liệu mới được nâng trạng thái dự báo chỉ nhờ tìm được tài liệu. Gói thu thập/verification đề xuất nằm trong [ACQUISITION_VERIFICATION_PACKAGE_PROPOSED.md](ACQUISITION_VERIFICATION_PACKAGE_PROPOSED.md).
