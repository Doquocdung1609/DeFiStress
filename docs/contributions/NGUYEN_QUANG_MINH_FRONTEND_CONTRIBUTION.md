# Nguyễn Quang Minh — đóng góp frontend DeFiStress

## Trạng thái

Đã hoàn thiện và push đóng góp frontend trên nhánh `feat/quang-minh-frontend-visualization`, tạo từ `origin/submission/group01-btl-final` (`2d075da`). Pull Request #61 đang mở để nhóm review; chưa merge.

| Trường | Giá trị đã xác minh |
|---|---|
| Họ tên | Nguyễn Quang Minh (theo phân công trong prompt) |
| Vai trò | Frontend development, UI/UX và trực quan hóa dữ liệu |
| GitHub username | [`Minh-1512`](https://github.com/Minh-1512) |
| Nhánh làm việc | `feat/quang-minh-frontend-visualization` |
| Pull Request | [#61 — feat(frontend): enhance DeFiStress visualization and user experience](https://github.com/Doquocdung1609/DeFiStress/pull/61) |
| Commit code | [`8faa6b75e00adba9229ace2aa0a666aa725f9d57`](https://github.com/Doquocdung1609/DeFiStress/commit/8faa6b75e00adba9229ace2aa0a666aa725f9d57) |
| Commit hướng dẫn và ảnh | [`63e25410bb6f068450438a8801b26fcf45d0eb18`](https://github.com/Doquocdung1609/DeFiStress/commit/63e25410bb6f068450438a8801b26fcf45d0eb18) |
| Tác giả trên GitHub | GitHub liên kết hai commit với `Minh-1512`; author hiển thị Nguyễn Quang Minh. |

## Công việc đã hoàn thành ở local

| Nhiệm vụ | File/component | Commit | Kết quả |
|---|---|---|---|
| Hiển thị Health Factor | `frontend/app/components/Dashboard.tsx`, `frontend/lib/visualization.ts` | [`8faa6b7`](https://github.com/Doquocdung1609/DeFiStress/commit/8faa6b75e00adba9229ace2aa0a666aa725f9d57) | HF dưới 1 không còn bị làm tròn thành 1.000; thêm nhãn đủ điều kiện xem xét thanh lý, tại ngưỡng và mức đệm tương đối. |
| Trạng thái cảnh báo B0–B3 | `frontend/app/components/terra/DemoControls.tsx`, `frontend/lib/visualization.ts` | [`8faa6b7`](https://github.com/Doquocdung1609/DeFiStress/commit/8faa6b75e00adba9229ace2aa0a666aa725f9d57) | Nhãn NORMAL/WATCH/HIGH/ABSTAIN có mô tả chữ; score và số tín hiệu lấy từ API; ABSTAIN không bị đổi thành NORMAL. |
| Trực quan hóa Exit Calculator | `frontend/app/components/terra/DemoControls.tsx`, `frontend/app/globals.css` | [`8faa6b7`](https://github.com/Doquocdung1609/DeFiStress/commit/8faa6b75e00adba9229ace2aa0a666aa725f9d57) | Tách cảnh báo/giả định/kết quả; hiển thị thanh khớp một phần, bảng chi phí và NOT_VERIFIABLE khi thiếu capacity. |
| Regression helpers | `frontend/lib/visualization.test.ts`, `frontend/scripts/browser_demo.mjs` | [`8faa6b7`](https://github.com/Doquocdung1609/DeFiStress/commit/8faa6b75e00adba9229ace2aa0a666aa725f9d57) | Thêm kiểm thử formatter/trạng thái/khớp và cập nhật browser smoke selectors, responsive checks. |
| Hướng dẫn và ảnh minh chứng | `docs/demo/FRONTEND_USER_GUIDE_VI.md`, `docs/demo/evidence/frontend-ui-improvements/` | [`63e2541`](https://github.com/Doquocdung1609/DeFiStress/commit/63e25410bb6f068450438a8801b26fcf45d0eb18) | Hướng dẫn tiếng Việt và 17 ảnh ứng dụng thật, gồm so sánh trước/sau và kích thước responsive. |

## Kiểm thử và ảnh minh chứng

- `pnpm test`: 32 kiểm thử đạt.
- `pnpm lint`: đạt.
- `pnpm exec tsc --noEmit`: đạt.
- `pnpm build`: đạt.
- `python scripts/demo_smoke.py`: 9 bước API đạt, gồm Aave, dữ liệu Terra, warning, stress, bản lưu và ZIP.
- `pnpm exec node scripts/browser_demo.mjs`: 17 ảnh browser được chụp; luồng saved run/tải ZIP và kiểm tra tràn ngang ở 1920×1080, 1366×768, 1024×768, 390×844 đạt.
- Ví dụ API Exit: 1.000 UST, capacity 600, giá 0,8 USD, phí 1%, trượt giá 2% → 600/400 UST, net 465,6 USD và modeled loss 134,4 USD.

Ảnh so sánh trước/sau và ảnh browser sau cải thiện nằm trong `docs/demo/evidence/`. Đây là ảnh chụp ứng dụng local thật.

## Hạn chế cần handoff

API local ban đầu không khởi động vì `sim/network/build.py` import `networkx`, nhưng gói này chưa được khai báo trong `pyproject.toml`. Đã cài `networkx` chỉ trong virtual environment để QA tiếp tục; không sửa backend/dependency trong nhánh frontend này. Nhóm phụ trách backend nên khai báo dependency để lần bootstrap sau chạy được ngay.

## Tái hiện thay đổi

```powershell
.\scripts\start_demo.ps1
Set-Location frontend
pnpm test
pnpm lint
pnpm exec tsc --noEmit
pnpm build
$env:DEMO_WEB_URL = "http://localhost:3100"
$env:DEMO_BROWSER_OUTPUT = "..\docs\demo\evidence\frontend-ui-improvements"
pnpm exec node scripts\browser_demo.mjs
Set-Location ..
.\.venv\Scripts\python.exe scripts\demo_smoke.py
.\scripts\stop_demo.ps1
```

## Handoff

Pull Request #61 đã được tạo từ nhánh làm việc sang `submission/group01-btl-final`. Chờ nhóm trưởng review và chấp thuận trước khi merge.
