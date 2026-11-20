"""Create the reader-facing submission handoff from observed local evidence."""

# ruff: noqa: E501  -- long Vietnamese presentation passages are kept as full paragraphs.

from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.shared import Pt

ROOT = Path("C:/Users/Admin/Desktop/NHOM_01_DEFISTRESS_BAO_CAO_BTL")
SCRIPT_SOURCE = Path("C:/Users/Admin/Downloads/DeFiStress_Script_ThuyetTrinh_45_Slide.docx")
TIMELINE_SOURCE = Path("C:/Users/Admin/Desktop/DeFiStress-BTL-V3/recording/timeline.json")
REPO_URL = "https://github.com/Doquocdung1609/DeFiStress"
BRANCH = "submission/group01-btl-final"


def new_document(title: str) -> Document:
    document = Document()
    normal = document.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11)
    document.add_heading(title, 0)
    return document


def write_lines(document: Document, lines: list[str]) -> None:
    for item in lines:
        document.add_paragraph(item)


def script() -> None:
    source = Document(SCRIPT_SOURCE)
    document = new_document("KỊCH BẢN THUYẾT TRÌNH DEFISTRESS — NHÓM 1")
    write_lines(document, [
        "51 slide. Slide 1–42 kế thừa bộ trình bày nghiên cứu của nhóm; slide 43–47 bổ sung sản phẩm bài tập lớn; slide 48 khôi phục đóng góp nghiên cứu, slide 49 trình bày ba thành viên; slide 50–51 tương ứng slide 44–45 gốc.",
        "Khi trình bày các kết quả Aave, phải nêu chính sách định giá và phạm vi mô phỏng. Kết quả Terra synthetic không phải dự báo được kiểm chứng năm 2022.",
    ])
    for paragraph in source.paragraphs[:87]:
        if paragraph.text.strip():
            document.add_paragraph(paragraph.text, style="Normal")
    additions = [
        ("Slide 43 — Kiến trúc phần mềm", "Giới thiệu frontend Next.js, backend FastAPI, engine mô phỏng và SQLite lưu lượt chạy. Dữ liệu đầu vào có nhãn nguồn. Chỉ ra API cho phép mở lại và tải ZIP. Tất cả tính toán của demo chạy ngoài chuỗi."),
        ("Slide 44 — Terra: lịch sử và synthetic", "Phân biệt Historical Data, Historical Fit và Early Warning hồi cứu với Synthetic Warning B0–B3. Nêu rõ dữ liệu đến muộn hoặc thiếu có thể khiến hệ thống ABSTAIN. Không trình bày synthetic như tín hiệu đã dự báo thành công Terra 2022."),
        ("Slide 45 — Cảnh báo đến phương án thoát", "Mở video hoặc app: chọn một cảnh báo synthetic đã lưu, mở Exit Calculator với giá và thời điểm tự điền. Nhập giả định giá thoát, khả năng khớp, phí, trượt giá và độ trễ. Với ví dụ 1.000 UST, khả năng khớp 600 UST tại 0,8 USD/UST, phí 1% và trượt giá 2%, tiền thu ròng là 465,6 USD, còn 400 UST chưa thoát. Đây là phép tính minh họa có điều kiện."),
        ("Slide 46 — Phương pháp và blockchain", "ABM là phương pháp chính với borrower, một liquidator và một arbitrageur đại diện. Stress tất định, Monte Carlo, phân tích mạng và mô hình Terra là phần bổ trợ. Dữ liệu on-chain cung cấp trạng thái đầu vào; engine không gửi giao dịch và chưa triển khai smart contract."),
        ("Slide 47 — Bằng chứng sản phẩm", "Chỉ ra video MP4 quay ứng dụng thật trên localhost, smoke test và browser test. Đọc nhãn fixture trước khi giải thích kết quả Aave. Trình bày run ID, mở lại kết quả, tải ZIP và nêu các giới hạn của dữ liệu."),
    ]
    for heading, body in additions:
        document.add_heading(heading, level=1)
        document.add_paragraph(body)
    document.add_heading("Slide 48 — Đóng góp của DeFiStress", level=1)
    document.add_paragraph("Tổng hợp dữ liệu, ABM, đối chứng định giá, lưới mở rộng và công cụ tương tác. Chỉ kết luận theo kết quả đã khóa.")
    document.add_heading("Slide 49 — Ba thành viên", level=1)
    document.add_paragraph("Dũng phụ trách nghiên cứu và điều phối; Hải phụ trách phần mềm và demo; Minh đóng góp frontend, trực quan hóa, hướng dẫn người dùng qua PR #61. Slide và thuyết trình là trách nhiệm được giao; hồ sơ chỉnh lý bằng Codex là hỗ trợ chung.")
    for index, text_index in ((50, 89), (51, 91)):
        heading = source.paragraphs[text_index].text.replace(f"Slide {text_index // 2}", f"Slide {index}")
        document.add_heading(heading, level=1)
        document.add_paragraph(source.paragraphs[text_index + 1].text)
    for paragraph in list(document.paragraphs):
        if paragraph.text.startswith("Slide "):
            import re
            match = re.match(r"Slide (\d+)", paragraph.text)
            if match:
                number = int(match.group(1))
                speaker = "Đỗ Quốc Dũng" if number <= 27 else "Đỗ Trung Hải" if number <= 40 else "Nguyễn Quang Minh"
                role = paragraph.insert_paragraph_before(f"Người trình bày dự kiến: {speaker}.")
                paragraph._p.addnext(role._p)
    document.add_heading("Câu hỏi phản biện và trả lời", level=1)
    questions = [
        ("Vì sao chọn ABM?", "Cần mô tả hành vi khác nhau của người vay, liquidator và arbitrageur cùng vòng phản hồi qua thị trường."),
        ("Monte Carlo có thay ABM không?", "Monte Carlo tạo nhiều đường giả định; mỗi đường vẫn dùng quy tắc tương tác của mô hình."),
        ("Có triển khai blockchain không?", "Blockchain cung cấp đầu vào đọc; engine chạy ngoài chuỗi để thử phản thực với chi phí thấp."),
        ("HF dưới 1 đã là thanh lý thực thi chưa?", "Chưa. Cần tuyến nợ, vốn, công suất và kế hoạch có khoản hoàn trả dương."),
        ("Aave có dùng trực tiếp giá Uniswap trong mô hình không?", "Policy A là giả định của mô hình. Không gán đó là oracle thực tế của Aave."),
        ("Uniswap V3 khác mô hình x·y=k đơn giản thế nào?", "Thanh khoản hoạt động theo khoảng tick; vượt tick làm thay đổi lượng thanh khoản đang dùng."),
        ("280/10.000 nghĩa là gì?", "Tần suất depth ≥2 trong Severe Policy A của bộ đã khóa, không phải xác suất khủng hoảng thị trường."),
        ("Terra có cảnh báo trước mất neo đầu tiên không?", "HIGH đến muộn 45 giờ ở ngưỡng 0,995 nhưng sớm ba giờ ở ngưỡng sâu 0,90. Hai mốc khác nhau."),
        ("Exit Calculator bảo đảm khớp lệnh không?", "Không. Giá, phí và capacity là giả định; thiếu capacity thì chưa thể xác minh kết quả khớp."),
        ("Có kết nối ví hoặc giao dịch thật không?", "Bản demo là công cụ phân tích local, không gửi giao dịch tài sản thật."),
        ("Ai đóng góp phần nào?", "Dũng nghiên cứu và điều phối; Hải tích hợp phần mềm/demo; Minh frontend và trực quan hóa qua PR #61. Hồ sơ ghi nguồn commit và phần hỗ trợ chung."),
    ]
    for question, answer in questions:
        document.add_paragraph(question, style="Heading 2")
        document.add_paragraph(answer)
    target = ROOT / "02_SLIDE_THUYET_TRINH/Kich_Ban_Thuyet_Trinh_DeFiStress_FINAL.docx"
    target.parent.mkdir(parents=True, exist_ok=True)
    document.save(target)


def timeline() -> None:
    rows = json.loads(TIMELINE_SOURCE.read_text(encoding="utf-8"))
    seconds_total = 381.76
    descriptions = {
        "aave-fixture": "Tổng quan Aave và nhãn fixture",
        "aave-positions": "Danh mục người vay",
        "aave-baseline": "Baseline và kết quả",
        "aave-severe": "Severe và kết quả",
        "uniswap-feedback": "Thanh khoản/giá Uniswap trong kết quả",
        "terra-overview": "Tổng quan Terra",
        "terra-historical-crisis-week": "Dữ liệu Terra lịch sử",
        "terra-historical-fit": "Historical Fit",
        "terra-synthetic-warning": "Cảnh báo synthetic B0–B3",
        "warning-to-exit-prefill": "Liên kết cảnh báo sang công cụ thoát",
        "terra-missing-abstain": "Dữ liệu thiếu và ABSTAIN",
        "terra-high-warning": "Tình huống synthetic rủi ro cao",
        "terra-retrospective-cutoff-safe": "Cảnh báo hồi cứu và cutoff-safe",
        "terra-stress-adverse": "Terra stress test",
        "terra-data-sources": "Nguồn dữ liệu và giới hạn",
        "exit-capacity-partial": "Thoát vốn khi khớp một phần",
        "saved-run-readback": "Lượt chạy đã lưu và mở lại",
    }
    def stamp(value: float) -> str:
        whole = int(value)
        return f"{whole // 60:02}:{whole % 60:02}"
    lines = [
        "# VIDEO TIMELINE — DEFISTRESS FULL DEMO",
        "",
        "Video ghi bằng Playwright trên ứng dụng local sau PR #61. Mốc lấy từ phiên quay thật; mỗi cảnh kéo dài đến mốc tiếp theo. Thời lượng 06:22, gồm kiểm tra responsive cuối video.",
        "",
        "| Bắt đầu | Kết thúc | Cảnh |",
        "|---|---|---|",
    ]
    document = new_document("VIDEO TIMELINE — DEFISTRESS FULL DEMO")
    document.add_paragraph("Ứng dụng local sau PR #61, trình duyệt thật; thời lượng 06:22. Các mốc lấy từ timeline phiên quay.")
    table = document.add_table(rows=1, cols=3)
    for cell, value in zip(table.rows[0].cells, ("Bắt đầu", "Kết thúc", "Nội dung"), strict=True):
        cell.text = value
    for i, row in enumerate(rows):
        end = rows[i + 1]["seconds"] if i + 1 < len(rows) else seconds_total
        label = descriptions.get(row["scene"], row["scene"])
        lines.append(f"| {stamp(row['seconds'])} | {stamp(end)} | {label} |")
        cells = table.add_row().cells
        for cell, value in zip(cells, (stamp(row["seconds"]), stamp(end), label), strict=True):
            cell.text = value
    lines += ["", "Aave trong video dùng fixture synthetic được gắn nhãn. Cảnh báo B0–B3 và công cụ thoát vốn là minh họa phản thực, không phải giao dịch hoặc dự báo lịch sử."]
    document.add_paragraph(lines[-1])
    target = ROOT / "03_VIDEO_DEMO/VIDEO_TIMELINE"
    target.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    document.save(target.with_suffix(".docx"))


def readme() -> None:
    document = new_document("HƯỚNG DẪN NỘP BÀI — DEFISTRESS NHÓM 1")
    write_lines(document, [
        "Đề tài: Mô hình hóa và kiểm định sức chịu đựng rủi ro lây lan trong tài chính phi tập trung (DeFi).",
        "Thành viên theo tài liệu nhóm: Đỗ Quốc Dũng, Đỗ Trung Hải, Nguyễn Quang Minh. Học phần: Tiền số và công nghệ Blockchain. Giảng viên: TS Lâm Đức Dương.",
        "Phương pháp mô phỏng chính: Agent-Based Modeling. Stress tất định, Monte Carlo, phân tích mạng và tái dựng Terra là kỹ thuật bổ trợ theo từng câu hỏi nghiên cứu.",
        "Mở báo cáo tại 01_BAO_CAO; slide và kịch bản tại 02_SLIDE_THUYET_TRINH; video và timeline tại 03_VIDEO_DEMO; mã nguồn và hướng dẫn chạy tại 04_MA_NGUON_VA_HUONG_DAN; phương pháp, blockchain và bằng chứng tại 05_PHU_LUC_VA_MINH_CHUNG.",
        f"GitHub: {REPO_URL}; nhánh demo nộp bài: {BRANCH}. Nhánh này là bản demo phục vụ học phần, không thay thế bản nghiên cứu đã khóa.",
        "Khởi chạy trên Windows từ thư mục mã nguồn: cài Python 3.12, Node.js và pnpm; tạo .venv, cài backend theo pyproject.toml, chạy pnpm install trong frontend, sau đó chạy .\\scripts\\start_demo.ps1. Frontend localhost:3100; API localhost:8100.",
        "Mô hình chạy ngoài chuỗi và chỉ đọc dữ liệu blockchain để dựng trạng thái đầu vào. Bản nộp không có giao dịch Mainnet hoặc smart contract được triển khai.",
        "Giới hạn: Aave trong demo dùng fixture synthetic; Terra B0–B3 và Exit Calculator là minh họa theo giả định. Kết quả lịch sử hồi cứu không được gọi là dự báo ngoài mẫu.",
    ])
    document.save(ROOT / "README_NOP_BAI.docx")


def guide() -> None:
    (ROOT / "04_MA_NGUON_VA_HUONG_DAN").mkdir(parents=True, exist_ok=True)
    document = new_document("HƯỚNG DẪN CÀI ĐẶT VÀ KHỞI CHẠY DEFISTRESS")
    write_lines(document, [
        "Yêu cầu: Windows PowerShell, Python 3.12, Node.js và pnpm. Docker không bắt buộc cho demo local. Không cần RPC/API key trả phí.",
        "Giải nén DeFiStress_Submission_Source.zip. Trong thư mục gốc tạo virtual environment bằng `py -3.12 -m venv .venv`; kích hoạt hoặc gọi trực tiếp `.venv\\Scripts\\python.exe`.",
        "Cài backend: `.venv\\Scripts\\python.exe -m pip install -e .`; nếu cần phần test, cài thêm extras dev theo pyproject.toml.",
        "Cài frontend: `cd frontend; pnpm install --frozen-lockfile; cd ..`.",
        "Khởi chạy: `.\\scripts\\start_demo.ps1`; mở http://localhost:3100. FastAPI tại http://localhost:8100/docs. Dừng bằng `.\\scripts\\stop_demo.ps1`.",
        "Kiểm tra smoke: `.venv\\Scripts\\python.exe scripts\\demo_smoke.py`. Browser test: `cd frontend; node scripts/browser_demo.mjs` sau khi cài Chromium bằng `pnpm exec playwright install chromium`.",
        "Dùng Aave Fixture Dataset khi chưa cấu hình snapshot Mainnet. Mọi kết quả fixture phải giữ nhãn synthetic. Terra Historical và Synthetic B0–B3 là hai chế độ khác nhau.",
        "Xem README_BTL.md trong mã nguồn để biết provenance, giới hạn và đường dẫn chi tiết.",
    ])
    document.save(ROOT / "04_MA_NGUON_VA_HUONG_DAN/Huong_Dan_Cai_Dat_Va_Khoi_Chay.docx")


def main() -> None:
    script()
    timeline()
    readme()
    guide()
    (ROOT / "04_MA_NGUON_VA_HUONG_DAN/GitHub_Repository_Link.md").write_text(
        f"# DeFiStress Nhóm 1\n\nRepository: {REPO_URL}\n\nNhánh demo nộp bài: `{BRANCH}`.\n\nĐây là bản demo học phần; phiên bản nghiên cứu tích hợp là `feat/terra-model-v2`.\n",
        encoding="utf-8",
    )
    print("Built script, timeline, readme and setup guide")


if __name__ == "__main__":
    main()
