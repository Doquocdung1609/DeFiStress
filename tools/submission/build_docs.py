"""Build course-submission Word documents from the preserved research report."""

# ruff: noqa: E501  -- long Vietnamese manuscript passages are kept as full paragraphs.

from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

TITLE = "Mô hình hóa và kiểm định sức chịu đựng rủi ro lây lan trong tài chính phi tập trung"
STUDENTS = ["Đỗ Quốc Dũng", "Đỗ Trung Hải", "Nguyễn Quang Minh"]


def style(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2.5)
    section.left_margin, section.right_margin = Cm(3), Cm(2.2)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = "Times New Roman", Pt(13)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(6)
    for name, size in (("Heading 1", 16), ("Heading 2", 14), ("Heading 3", 13)):
        heading = doc.styles[name]
        heading.font.name, heading.font.size = "Times New Roman", Pt(size)
        heading.font.bold = True
        heading.paragraph_format.space_before = Pt(12)
        heading.paragraph_format.space_after = Pt(6)


def body_before(anchor, text: str, heading: str | None = None):
    paragraph = anchor.insert_paragraph_before(text, style=heading or "Normal")
    if heading is None:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return paragraph


def find_heading(doc: Document, text: str):
    for paragraph in doc.paragraphs:
        if paragraph.text == text:
            return paragraph
    raise ValueError(f"Missing source heading: {text}")


def set_field(paragraph, instruction: str) -> None:
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    run._r.append(begin)
    instruction_run = paragraph.add_run()
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    instruction_run._r.append(instr)
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    paragraph.add_run()._r.append(separate)
    paragraph.add_run("Mục lục sẽ được cập nhật khi mở trong Word")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    paragraph.add_run()._r.append(end)


def make_main(source: Path, destination: Path, course: str, lecturer: str) -> None:
    doc = Document(source)
    style(doc)
    original = list(doc.paragraphs)
    for paragraph in original:
        if paragraph.text == "BÁO CÁO TỔNG KẾT":
            paragraph.text = "BÁO CÁO BÀI TẬP LỚN"
        elif paragraph.text == "ĐỀ TÀI NGHIÊN CỨU KHOA HỌC CỦA SINH VIÊN":
            paragraph.text = f"Học phần: {course}" if course else "Học phần: chờ nhóm xác nhận"
        elif paragraph.text.startswith("Người hướng dẫn:"):
            paragraph.text = f"Giảng viên phụ trách: {lecturer}" if lecturer else "Giảng viên phụ trách: chờ nhóm xác nhận"
        elif paragraph.text.startswith("Nhóm nghiên cứu xin trân trọng cảm ơn"):
            paragraph.text = (
                "Nhóm 1 trân trọng cảm ơn Học viện Công nghệ Bưu chính Viễn thông, "
                "Khoa Tài chính Kế toán 1 và các thầy cô đã hướng dẫn nhóm trong quá trình thực hiện bài tập lớn. "
                "Những góp ý về dữ liệu, mô hình và phạm vi kết luận giúp nhóm kiểm tra sản phẩm chặt chẽ hơn."
            )
        elif paragraph.text.startswith("Sáu câu hỏi nghiên cứu được kiểm tra"):
            paragraph.text = (
                "Sáu câu hỏi nghiên cứu được kiểm tra qua cú sốc giá WETH, suy giảm thanh khoản, "
                "giới hạn tác nhân thanh lý, năng lực kinh doanh chênh lệch giá, định giá USDC và các tham số rủi ro. "
                "Trong lưới gốc 32 tổ hợp không xuất hiện độ sâu từ hai vòng; lưới mở rộng 60 tổ hợp có bốn trường hợp "
                "độ sâu hai vòng dưới Policy A. Kiểm tra đối chứng cho thấy kết quả vòng hai phụ thuộc chính sách "
                "truyền giá DEX vào định giá vị thế. Đây là kết quả mô phỏng phản thực, không phải tần suất khủng hoảng ngoài thị trường."
            )
        elif paragraph.text.startswith("Lưới kiểm tra gồm cú sốc ETH"):
            paragraph.text = (
                "Lưới gốc 32 tổ hợp gồm cú sốc ETH từ −5% đến −40% và các mức suy giảm thanh khoản 0%, 25%, 50%, 75%: "
                "12 tổ hợp có độ sâu 0, 20 có độ sâu 1, không tổ hợp nào có độ sâu 2. "
                "Lưới mở rộng 60 tổ hợp ghi nhận 18/38/4 tương ứng độ sâu 0/1/2. "
                "Các trường hợp độ sâu 2 dưới Policy A là kết quả có điều kiện theo miền stress và chính sách định giá, "
                "không xác lập một ngưỡng lây lan độc lập với oracle."
            )
        elif paragraph.text.startswith("Không kịch bản nào trong năm nhóm Monte Carlo chính"):
            paragraph.text = (
                "Trong 10.000 đường Severe theo Policy A ở bộ Level-3 đã khóa, 280 đường đạt độ sâu từ hai vòng. "
                "Không đường nào trong bộ được báo cáo đạt độ sâu từ ba vòng. Tần suất 280/10.000 chỉ phản ánh "
                "phân phối stress và cơ chế truyền giá của mô hình, không phải xác suất khủng hoảng thực tế."
            )
        elif paragraph.text.startswith("Nguồn: Table_06_aave_monte_carlo.csv"):
            paragraph.text = "Nguồn: frozen_v3/tables/rq1_monte_carlo.csv và manifest Level-3 đã khóa."
        elif paragraph.text.startswith("Kết quả cho thấy khả năng xuất hiện cascade"):
            paragraph.text = (
                "Khả năng xuất hiện thanh lý vòng hai phụ thuộc cú sốc, thanh khoản và chính sách định giá. "
                "Miền 32 tổ hợp ban đầu không có vòng hai; miền 60 tổ hợp mở rộng có bốn trường hợp độ sâu 2 dưới Policy A. "
                "Khi giữ nguyên các trường hợp được chọn nhưng dùng giá tham chiếu cho HF (Policy B), "
                "không trường hợp nào giữ độ sâu 2. Kết quả mô hình không chứng minh Aave Mainnet dùng giá spot Uniswap làm oracle."
            )
        elif "run_full_research_quy trình.py" in paragraph.text:
            paragraph.text = (
                "Tái lập bản demo: .\\scripts\\start_demo.ps1; .\\.venv\\Scripts\\python.exe scripts\\demo_smoke.py; "
                "cd frontend; node scripts\\browser_demo.mjs. Các gói nghiên cứu đã khóa có manifest và lệnh tái lập riêng trong repository."
            )
    find_heading(doc, "GIỚI THIỆU").text = "GIỚI THIỆU ĐỀ TÀI"
    find_heading(doc, "CƠ SỞ LÝ THUYẾT VÀ TỔNG QUAN NGHIÊN CỨU").text = "CƠ SỞ LÝ THUYẾT"
    find_heading(doc, "PHƯƠNG PHÁP NGHIÊN CỨU").text = "DỮ LIỆU VÀ TRẠNG THÁI HỆ THỐNG"
    find_heading(doc, "KẾT QUẢ NGHIÊN CỨU").text = "KẾT QUẢ MÔ PHỎNG AAVE VÀ UNISWAP"
    find_heading(doc, "THẢO LUẬN, KẾT LUẬN VÀ KIẾN NGHỊ").text = "PHẦN MỀM, TRIỂN KHAI VÀ KẾT LUẬN"

    # The source's early Monte Carlo summary and tail figure were superseded by
    # the locked extended run. Keep the old DOCX untouched, remove those items
    # only from this submission copy.
    mc_table = doc.tables[13]
    while len(mc_table.rows) > 2:
        row = mc_table.rows[-1]._tr
        row.getparent().remove(row)
    for cell, value in zip(mc_table.rows[0].cells, ("Mẫu", "Số path", "Depth ≥ 2", "Chính sách", "Diễn giải"), strict=True):
        cell.text = value
    for cell, value in zip(mc_table.rows[1].cells, ("Severe Level-3", "10.000", "280", "Policy A", "Tần suất trong mô hình"), strict=True):
        cell.text = value
    for paragraph in original:
        if paragraph.text.startswith("Hình 4.12: Rủi ro đuôi") or paragraph.text.startswith("Nguồn: tổn thất kỳ vọng ở phần đuôi 95% trên 200") or paragraph._p.xpath(".//w:drawing") and original.index(paragraph) == 249:
            paragraph._p.getparent().remove(paragraph._p)
    figure_list = doc.tables[2]
    for row in list(figure_list.rows):
        if row.cells[0].text == "Hình 4.12":
            row._tr.getparent().remove(row._tr)
    for row_index, conclusion, status in (
        (1, "Lưới 32 ô không có depth 2; lưới 60 ô có 4 depth 2 dưới Policy A. Kết quả phụ thuộc chính sách định giá.", "CÓ ĐIỀU KIỆN"),
        (2, "Thanh khoản DEX thay đổi khả năng hấp thụ bán bắt buộc và tác động giá; HF chỉ phản hồi qua policy định giá.", "CÓ ĐIỀU KIỆN"),
    ):
        doc.tables[19].rows[row_index].cells[1].text = conclusion
        doc.tables[19].rows[row_index].cells[2].text = status
    doc.tables[21].rows[1].cells[1].text = "32 ô: 0 depth 2; 60 ô: 4 depth 2 dưới Policy A."
    doc.tables[21].rows[1].cells[2].text = "Không suy ra ngưỡng độc lập với oracle hay xác suất thị trường."
    doc.tables[21].rows[2].cells[1].text = "Thanh khoản mỏng tăng tác động giá; vòng mới cần kênh định giá HF và giao dịch thực thi."
    doc.tables[21].rows[2].cells[2].text = "Một pool và chính sách định giá phản thực."

    def revised_label(text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            kind, chapter, number = match.groups()
            index = int(number)
            if kind == "Bảng" and chapter == "3" and index in {2, 3}:
                return f"Bảng 4.{index-1}"
            if kind == "Bảng" and chapter == "4":
                return f"Bảng {5 if index <= 6 else 6}.{index if index <= 6 else index-6}"
            if kind == "Bảng" and chapter == "5" and index == 1:
                return "Bảng 7.1"
            if kind == "Hình" and chapter == "4":
                return f"Hình {5 if index <= 7 else 6}.{index if index <= 7 else index-7}"
            return match.group(0)

        return re.sub(r"\b(Bảng|Hình) ([345])\.(\d+)\b", replace, text)

    for paragraph in doc.paragraphs:
        revised = revised_label(paragraph.text)
        if revised != paragraph.text:
            paragraph.text = revised
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                revised = revised_label(cell.text)
                if revised != cell.text:
                    cell.text = revised

    method = find_heading(doc, "Mô hình tác tử và vòng phản hồi")
    body_before(method, "PHƯƠNG PHÁP MÔ PHỎNG VÀ THIẾT KẾ MÔ HÌNH", "Heading 1")
    body_before(method, "Phương pháp chính là mô phỏng dựa trên tác tử (Agent-Based Modeling, ABM). Nhiều người vay có danh mục khác nhau tương tác với một liquidator đại diện, một arbitrageur đại diện và pool Uniswap V3. Pool là môi trường giao dịch; chính sách định giá là quy tắc hệ thống, không phải tác nhân độc lập.")
    body_before(method, "Trình tự tính theo mã: áp cú sốc WETH, định giá danh mục, chốt tập đủ điều kiện đầu wave, lập kế hoạch thanh lý, kiểm tra tuyến tài sản cùng vốn, công suất, gas và lợi nhuận, thực thi bán WETH qua pool, điều chỉnh giá sau bán, rồi cập nhật giá định giá cho wave kế tiếp. HF không được tính lại cho toàn bộ danh mục sau từng giao dịch trong cùng wave.")
    body_before(method, "Policy A dùng giá thấp hơn giữa giá tham chiếu và DEX cho vòng sau. Policy B chỉ dùng giá tham chiếu. Policy C weak và moderate là giả định truyền giá có trễ và làm trơn. Không chính sách nào được tự nhận là oracle Aave hoặc Chainlink thực tế.")

    terra = find_heading(doc, "Kiểm chứng lịch sử mở rộng - Terra 2022")
    body_before(terra, "TERRA 2022 VÀ CẢNH BÁO RỦI RO", "Heading 1")
    body_before(terra, "Phần Terra tách tái dựng lịch sử 2022, cảnh báo hồi cứu và mô hình cảnh báo B0–B3 trên dữ liệu tổng hợp. 1.776 quan sát theo giờ và 277.342 swap lịch sử thuộc nguồn nghiên cứu đã lưu; các giá nhập trong B0–B3 của bản demo là synthetic, không phải đầu vào hợp lệ để tuyên bố dự báo trước sụp đổ Terra.")
    body_before(terra, "Công cụ Exit Calculator chỉ tính kết quả theo giá, dung lượng khớp, phí, trượt giá và độ trễ do người dùng giả định. Khi thiếu dung lượng thị trường, hệ thống trả NOT_VERIFIABLE. Tiền ròng và tổn thất trên phần đã bán được báo riêng với số UST chưa khớp. Không có bằng chứng nhà đầu tư năm 2022 thực sự có thể khớp lệnh theo các giả định demo.")

    discussion = find_heading(doc, "Thảo luận kết quả")
    body_before(discussion, "Kiến trúc và chức năng ứng dụng", "Heading 2")
    body_before(discussion, "DeFiStress chạy dưới dạng FastAPI backend, Next.js frontend và SQLite cho chế độ local. Adapter đọc nguồn blockchain hoặc dữ liệu đã lưu; engine xử lý mô phỏng ngoài chuỗi; dashboard hiển thị danh mục, kịch bản, cảnh báo, kết quả và file xuất. Các API demo lưu run và cho phép đọc lại cùng run ID và tải ZIP.")
    body_before(discussion, "Bản nộp minh họa các luồng Aave–Uniswap fixture, Terra Historical Data, Historical Fit, Early Warning hồi cứu, Synthetic B0–B3, Stress Test và Exit Calculator. Trang cảnh báo synthetic có thể chuyển sang Exit Calculator; giá và thời điểm được đọc lại từ run cảnh báo đã lưu, còn giá thoát, dung lượng và chi phí vẫn phải do người dùng đặt giả định.")
    body_before(discussion, "Triển khai và phạm vi blockchain", "Heading 2")
    body_before(discussion, "Dữ liệu Mainnet tại block 26.045.352 được dùng để tái dựng trạng thái Aave V3 và Uniswap V3. Việc đọc trạng thái hợp đồng thông minh là read-only; kết quả stress và cảnh báo chạy ngoài chuỗi. Nhóm không triển khai engine trên Ethereum Mainnet và không gửi giao dịch dùng tài sản thật. Cách tổ chức này giảm chi phí gas và cho phép thử nhiều kịch bản mà không thay đổi trạng thái blockchain.")
    body_before(discussion, "Cài đặt và kiểm thử bản demo", "Heading 2")
    body_before(discussion, "Trên Windows, chạy scripts\\start_demo.ps1 từ thư mục repository. Backend ở http://localhost:8100, giao diện ở http://localhost:3100. Chạy .venv\\Scripts\\python.exe scripts\\demo_smoke.py để kiểm tra các luồng chính; dừng bằng scripts\\stop_demo.ps1. Chế độ fixture không cần RPC key. Docker Compose là tùy chọn và chỉ nên dùng khi Docker Engine có sẵn.")
    body_before(discussion, "Kiểm thử tự động xác nhận trạng thái API, nội dung kết quả Aave, 1.776 quan sát Terra, B0–B3, stress, phép tính thoát, lưu lại và ZIP. Video demo ghi ứng dụng đang chạy thật, không dùng giao dịch on-chain hoặc dữ liệu giả mạo làm bằng chứng lịch sử.")

    for paragraph in list(doc.paragraphs):
        if paragraph.text.startswith("Báo cáo gồm năm chương"):
            paragraph.text = "Báo cáo gồm bảy chương: giới thiệu; cơ sở lý thuyết; dữ liệu; phương pháp mô phỏng; kết quả Aave–Uniswap; Terra; phần mềm, triển khai và kết luận."
    # Replace obsolete printed five-chapter contents with a Word TOC field.
    toc = find_heading(doc, "MỤC LỤC")
    next_front = find_heading(doc, "DANH MỤC TỪ VIẾT TẮT")
    cursor = toc._p.getnext()
    while cursor is not None and cursor is not next_front._p:
        following = cursor.getnext()
        cursor.getparent().remove(cursor)
        cursor = following
    set_field(next_front.insert_paragraph_before(), 'TOC \\o "1-3" \\h \\z \\u')

    destination.parent.mkdir(parents=True, exist_ok=True)
    doc.save(destination)


def create_document(path: Path, title: str, sections: list[tuple[str, list[str]]], table=None) -> None:
    doc = Document()
    style(doc)
    heading = doc.add_paragraph(title, style="Title")
    heading.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph("Nhóm 1 · Học viện Công nghệ Bưu chính Viễn thông · Ngành Công nghệ tài chính")
    for section_title, paragraphs in sections:
        doc.add_heading(section_title, level=1)
        for content in paragraphs:
            p = doc.add_paragraph(content)
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if table:
        rows = doc.add_table(rows=1, cols=len(table[0]))
        rows.style = "Table Grid"
        for cell, value in zip(rows.rows[0].cells, table[0], strict=True):
            cell.text = value
        for row in table[1:]:
            cells = rows.add_row().cells
            for cell, value in zip(cells, row, strict=True):
                cell.text = value
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--course", default="")
    parser.add_argument("--lecturer", default="")
    args = parser.parse_args()
    root = args.output
    make_main(args.source, root / "01_BAO_CAO/DeFiStress_Bao_Cao_BTL_FINAL.docx", args.course, args.lecturer)
    create_document(root / "05_PHU_LUC_VA_MINH_CHUNG/Phuong_Phap_Mo_Phong_DeFiStress.docx", "Phương pháp mô phỏng DeFiStress", [
        ("Phương pháp chủ đạo", ["DeFiStress dùng Agent-Based Modeling (ABM). Danh mục người vay không đồng nhất; một liquidator đại diện quyết định theo vốn, công suất, gas và lợi nhuận; một arbitrageur đại diện điều chỉnh chênh lệch giá. Pool Uniswap V3 và chính sách định giá là môi trường và quy tắc của hệ thống."]),
        ("Trình tự một vòng", ["Khởi tạo danh mục và pool → cú sốc WETH → định giá HF → chốt tập vị thế đủ điều kiện ở đầu wave → lập kế hoạch và kiểm tra ràng buộc → thanh lý có hoàn trả nợ dương → bán WETH qua các tick → điều chỉnh giá → cập nhật giá định giá cho wave sau. Wave dừng khi không còn vị thế, không có nợ được hoàn trả hoặc hết horizon/max waves."]),
        ("Công thức và đơn vị", ["Health Factor = giá trị tài sản thế chấp có điều chỉnh ngưỡng thanh lý / giá trị nợ. Giá trị hai vế dùng cùng đơn vị định giá. USDC token quantity phải tách khỏi giá trị nợ quy USD. Price impact tức thời đo thay đổi sau bán thanh lý; độ lệch còn lại đo sau bước điều chỉnh arbitrage. Bad debt là nợ thiếu bảo đảm theo mô hình, không phải tổn thất tài chính đã thực hiện."]),
        ("Tính danh mục và điều kiện thanh lý", ["Với mỗi tài sản i, giá trị thế chấp là số lượng token nhân với giá USD và chỉ tham gia HF nếu trạng thái sử dụng làm thế chấp được bật. Ngưỡng thanh lý có trọng số được áp trên giá trị tài sản thế chấp. Mẫu số HF là tổng giá trị nợ theo USD. HF dưới 1 là điều kiện danh mục có thể được xét; thanh lý thực thi cần thêm tuyến nợ USDC/WETH, kế hoạch hợp lệ và khoản hoàn trả nợ dương.", "LTV chi phối khoản vay tối đa ở thời điểm khởi tạo. Liquidation threshold chi phối ranh giới HF. Liquidation bonus ảnh hưởng lượng tài sản liquidator nhận khi hoàn trả nợ. Ba tham số có tác dụng khác nhau và không thể gộp thành một biến rủi ro chung."]),
        ("Thanh khoản tập trung Uniswap V3", ["Pool được mô tả theo giá căn bậc hai, tick hiện tại, các tick khởi tạo và thanh khoản đang hoạt động. Khi bán WETH, giá đi qua từng đoạn thanh khoản; vượt tick thì lượng thanh khoản hoạt động thay đổi theo liquidity net của tick. Mô hình không dùng công thức x·y=k của AMM V2 để thay thế toàn bộ hành vi V3.", "Tác động giá tức thời là độ lệch giá sau forced sale trước điều chỉnh giá. Độ lệch còn lại đo sau hành động arbitrage trong wave. Cơ chế arbitrage_toward là tái định vị giá trong mô hình, không phải bằng chứng đã có giao dịch arbitrage on-chain được cấp vốn."]),
        ("Chỉ tiêu đầu ra", ["Cascade depth đếm số wave có hoàn trả nợ dương, không phải max_waves được cấu hình. Total liquidated debt là tổng nợ đã hoàn trả trong mô hình; unliquidated debt là nợ của các vị thế còn dưới ngưỡng HF sau xử lý. Bad debt ước lượng phần nợ không được tài sản thế chấp bảo đảm đủ theo mô hình. Time to recovery chỉ có nghĩa sau khi độ lệch giá thực sự vượt ngưỡng phục hồi.", "Các đơn vị phải ghi rõ: WETH và USDC là lượng token; USD là giá trị quy đổi; tỷ lệ phần trăm áp dụng cho cú sốc, tác động giá, LTV và haircut; thời gian là bước mô phỏng nhân với số giây mỗi bước."]),
        ("Kỹ thuật bổ trợ", ["Lưới tất định quét các tổ hợp tham số đã định. Monte Carlo tạo nhiều đường stress theo phân phối giả định, không thay thế ABM. Phân tích mạng mô tả liên kết cấu trúc, chưa phải lan truyền tổn thất động. Terra dùng tái dựng lịch sử, stress phản thực và cảnh báo theo quy tắc; kết quả B0–B3 hiện chỉ là synthetic."]),
        ("Giới hạn suy luận", ["Policy A truyền giá DEX bất lợi vào HF; B dùng giá tham chiếu; C là proxy có trễ/làm trơn. Đây là chính sách nghiên cứu, không xác nhận oracle Aave thực tế. 280/10.000 là tần suất mô phỏng Severe theo Policy A, không phải xác suất khủng hoảng Mainnet."]),
    ], table=[("Phương pháp", "Chức năng", "Đầu vào", "Đầu ra"), ("ABM", "Tương tác borrower–liquidator–pool", "Danh mục, giá, thanh khoản", "Wave, nợ thanh lý, tác động giá"), ("Lưới tất định", "So sánh tham số", "Shock, haircut, policy", "Phân loại độ sâu"), ("Monte Carlo", "Đánh giá phân phối giả định", "Seed và phân phối stress", "Tần suất trong mô hình"), ("Historical replay", "Tái dựng Terra", "Dữ liệu lịch sử đã lưu", "Sai số và giới hạn cảnh báo")])
    create_document(root / "05_PHU_LUC_VA_MINH_CHUNG/Giai_Trinh_Trien_Khai_Blockchain_DeFiStress.docx", "Giải trình triển khai blockchain DeFiStress", [
        ("Blockchain được dùng ở đâu", ["Ứng dụng đọc dữ liệu Ethereum Mainnet, trạng thái Aave V3/Uniswap V3 và lịch sử Terra từ nguồn đã lưu. Một snapshot Mainnet được neo ở block 26.045.352. Việc đọc dữ liệu on-chain và tái dựng trạng thái không đồng nghĩa phần mềm đã được triển khai dưới dạng smart contract."]),
        ("Kiến trúc chạy", ["Blockchain và dữ liệu đã lưu → read-only adapter → engine mô phỏng ngoài chuỗi → FastAPI → Next.js dashboard và báo cáo. SQLite lưu kết quả demo cục bộ; không có giao dịch Mainnet dùng tài sản thật."]),
        ("Lý do chọn tính toán ngoài chuỗi", ["ABM, Monte Carlo và xử lý dữ liệu lịch sử cần nhiều vòng lặp, nhiều kịch bản và các bảng/biểu đồ lớn. Đưa các phép tính đó vào hợp đồng thông minh sẽ tăng gas, giới hạn tài nguyên thực thi, gây độ trễ và không mang lại lợi ích thay đổi trạng thái tài sản. Phương án ngoài chuỗi cho phép thử phản thực với chi phí thấp, còn snapshot đầu vào vẫn truy vết được."]),
        ("Khả năng mở rộng", ["Một proof of concept local chain có thể lưu run ID và hash kết quả để kiểm tra toàn vẹn sau này. Bản nộp hiện không kèm receipt local-chain đã thực thi, vì vậy không tuyên bố đã triển khai hợp đồng thông minh."]),
    ])
    create_document(root / "05_PHU_LUC_VA_MINH_CHUNG/Phan_Cong_Va_Dong_Gop_Thanh_Vien.docx", "Phân công và đóng góp thành viên", [
        ("Phạm vi ghi nhận", ["Nhóm 1 gồm đúng ba thành viên. Minh phụ trách frontend và trực quan hóa trong PR #61; ba commit 8faa6b7, 63e2541, 03b3eba được giữ khi merge. Trách nhiệm slide và thuyết trình được giao cho Minh; chỉnh lý cuối bằng Codex là hỗ trợ chung của nhóm."]),
    ], table=[("Thành viên", "GitHub", "Công việc", "Bằng chứng"), (STUDENTS[0], "Doquocdung1609", "Nghiên cứu, dữ liệu, mô hình hóa và điều phối", "Lịch sử nguồn và tích hợp"), (STUDENTS[1], "Trunghai05", "Phần mềm, API và demo", "PR #58, #59"), (STUDENTS[2], "Minh-1512", "Frontend, trực quan hóa và kiểm thử", "PR #61, merge 25e757a")])


if __name__ == "__main__":
    main()
