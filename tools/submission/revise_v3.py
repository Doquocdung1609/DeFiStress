"""Revise the current Drive master; preserve administrative source and old files."""

# ruff: noqa: E501
from pathlib import Path

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches

ROOT = Path('C:/Users/Admin/Desktop/NHOM_01_DEFISTRESS_BAO_CAO_BTL')
SOURCE = Path('C:/Users/Admin/Desktop/DeFiStress-BTL-V3/source/drive-current.docx')
REPO = Path(__file__).resolve().parents[2]


def insert(anchor, value, style='Normal'):
    return anchor.insert_paragraph_before(value, style)


def table_before(doc, anchor, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    for cell, value in zip(table.rows[0].cells, headers, strict=True):
        cell.text = str(value)
    for row in rows:
        for cell, value in zip(table.add_row().cells, row, strict=True):
            cell.text = str(value)
    anchor._p.addprevious(table._tbl)
    return table


def main():
    doc = Document(SOURCE)
    pars = list(doc.paragraphs)
    replacements = {
        131: 'Các đợt Monte Carlo ban đầu dùng 200 đường cho từng cấu hình. Bộ Severe mở rộng dùng cùng chuỗi seed để lưu các tiền tố 200, 1.000, 5.000 và 10.000 đường; các tiền tố chồng lấn và không phải bốn mẫu độc lập. Khoảng Wilson trong kết quả đã khóa mô tả bất định lấy mẫu có điều kiện theo phân phối stress. Thước đo đuôi tổng hợp phản ánh mức phơi nhiễm do mô hình tính, không phải tổn thất thị trường đã thực hiện.',
        133: 'Historical Fit dùng dữ liệu sự kiện để hiệu chỉnh khả năng tái dựng. Cảnh báo hồi cứu tách chế độ retrospective và cutoff-safe: mỗi mốc chỉ chọn quan sát có thời điểm được phép sử dụng không sau cutoff. Kiểm tra làm nhiễu tương lai đánh giá rò rỉ tính toán; thiết kế biến và trọng số vẫn chịu ảnh hưởng hiểu biết về sự kiện. Do đó, kết quả hồi cứu và kiểm tra leakage không thay thế một phép dự báo ngoài mẫu.',
        135: 'Các kết quả nghiên cứu được lưu cùng kịch bản, seed, mã nguồn và hash đầu vào/đầu ra. Bản demo có smoke API, kiểm thử Python, kiểm thử giao diện và kiểm tra trình duyệt riêng. Số lượng kiểm thử phải gắn với đúng phiên bản; không cộng các nhóm hồi quy chồng lấn thành một tổng mới.',
        148: 'Hai miền stress cho thấy sự xuất hiện vòng hai phụ thuộc điều kiện đầu vào. Miền 32 ô ban đầu có bán thế chấp nhưng chưa tạo thêm vòng; miền 60 ô mở rộng có bốn trường hợp vòng hai dưới Policy A. Đối chứng chính sách định giá giúp phân biệt tác động giá ở DEX với tác động được truyền vào HF.',
        150: 'Thanh khoản quyết định khả năng hấp thụ bán thế chấp. Với cùng lượng WETH bán ra, pool mỏng chịu thay đổi giá lớn hơn. Tuy nhiên, vị thế mới chỉ mất an toàn khi chính sách định giá truyền đủ mức giảm đó vào HF. Kết quả không đổi độ sâu trong miền gốc và bốn trường hợp vòng hai ở miền mở rộng phản ánh hai phạm vi khác nhau.',
        157: 'Trong thử độ trễ 0–4 bước, thời gian xử lý vị thế tăng từ 60 lên 300 giây trong cấu hình đã xét, còn nợ thanh lý và độ sâu không đổi. Đây là thời gian xử lý theo tiến trình mô hình. Thời gian phục hồi giá chỉ được diễn giải khi quỹ đạo thực sự vượt ngưỡng lệch giá rồi trở lại vùng phục hồi.',
        165: 'Tác động giá ngay sau bán là 0,0010879429953578185 theo tỷ lệ trong bảng nguồn RQ4. Khi tăng capacity arbitrage từ 0% lên 50% rồi 100%, độ lệch sau arbitrage giảm lần lượt từ 0,0010879429953578185 xuống 0,0005439714976789092 và gần 0. Vì vậy, arbitrage cải thiện giá còn lại ngay cả khi một số chỉ tiêu thanh lý giữ nguyên. Bước điều chỉnh này là price repositioning trong mô hình, chưa phải giao dịch arbitrage có vốn được thực thi trên Mainnet.',
    }
    for index, value in replacements.items():
        pars[index].text = value
    for p in doc.paragraphs:
        for old, new in [('Chi phí phí giao dịch','Chi phí giao dịch'),('sổ kết quả kết quả','sổ kết quả'),('giao dịch giao dịch hoán đổi','giao dịch hoán đổi'),('không biến mô hình thành công cụ tiên tri','và phạm vi diễn giải kết quả')]:
            if old in p.text:
                p.text = p.text.replace(old,new)
        if p.style.name == 'Heading 1':
            p.paragraph_format.page_break_before = True
    anchor = pars[116]
    insert(anchor, 'Phân loại dữ liệu và phạm vi mẫu', 'Heading 2')
    insert(anchor, 'The Graph tìm ứng viên theo nợ; RPC xác minh trạng thái tại cùng block. 109 vị thế tuyến WETH/USDC phục vụ mô phỏng thanh lý; 255 danh mục phục vụ phân tích LTV. Hai tập được chọn theo mục đích riêng, không giả định chúng lồng nhau. Sai số HF trung vị khoảng 0,00003031 và lớn nhất khoảng 0,603077 cần được đọc cùng phân tích gần ngưỡng thanh lý.')
    table_before(doc, anchor, ['Dữ liệu','Nguồn / mẫu','Vai trò'], [
        ['Ethereum snapshot','Chain 1; block 26045352; 454/500 xác minh','Trạng thái đầu vào cố định'],
        ['Tuyến WETH/USDC','109 vị thế','Thực thi tuyến thanh lý mô hình'],
        ['Phân tích LTV','255 danh mục','Khả năng vay phản thực'],
        ['Uniswap V3','Giá, tick, active liquidity, liquidity net tại block','Mô phỏng độ sâu theo khoảng giá'],
        ['Terra lịch sử','1.776 mốc giờ; 277.342 swaps','Tái dựng và kiểm tra hồi cứu'],
        ['Fixture / synthetic','Đầu vào thử nghiệm có nhãn','Demo và kiểm thử phần mềm'],
    ])
    anchor = pars[149]
    insert(anchor, 'Đối chứng chính sách định giá và thanh lý thực thi', 'Heading 2')
    insert(anchor, 'Bốn deterministic cases và mười đường Monte Carlo được chọn vì có vòng hai dưới A. Giữ đầu vào và thay policy cô lập vai trò của cơ chế truyền giá. Đây là tập đối chứng có chủ đích; mẫu số 10 không dùng để suy ra tần suất toàn thị trường.')
    table_before(doc, anchor, ['Policy','Depth ≥2 / 4 cases','Depth ≥2 / 10 paths','Mới đủ điều kiện','Thực thi vòng 2'], [
        ['A','4/4','10/10',35,14],['B','0/4','0/10',0,0],['C weak','0/4','0/10',6,0],['C moderate','0/4','2/10',11,2],
    ])
    insert(anchor, 'Đơn vị hai cột cuối là lượt người vay–kịch bản–chính sách. Trong tập đối chiếu mục tiêu, 36 lượt mới đủ điều kiện theo HF danh mục bị bỏ qua vì không có khoản nợ USDC thuộc tuyến WETH/USDC được mô hình hóa. Nhãn thô NOT_ELIGIBLE được giải thích bằng bằng chứng NO_MODELLED_USDC_DEBT; không suy ra các khoản nợ khác bằng không hoặc USDC đã được trả hết ở vòng trước.')
    insert(anchor, 'Nguồn: oracle_transmission_diagnostic_v1/comparison_matrix.csv; scientific_integration_v1/eligible_vs_executed_summary.csv.')
    anchor = pars[195]
    insert(anchor, 'Bằng chứng liên hệ lịch sử Ethereum', 'Heading 2')
    insert(anchor, 'Census RPC ghi nhận 28 LiquidationCall; 27 sự kiện được Graph ghép thành công. Trong 27 sự kiện, một tuyến WETH có thứ tự và lượng khớp được xác minh, hai trường hợp cùng giao dịch nhưng chưa chứng minh chuyển tài sản trực tiếp, 23 cùng block và một gần thời gian. Sự kiện chỉ có ở RPC được giữ riêng. Mức độ liên hệ này hỗ trợ truy vết giao thức, chưa xác lập chuỗi nhân quả lây lan lịch sử.')
    anchor = pars[245]
    insert(anchor, 'Công nghệ và luồng xử lý sản phẩm', 'Heading 2')
    insert(anchor, 'Frontend Next.js gửi tham số qua API FastAPI. Backend kiểm tra đầu vào, gọi engine phù hợp rồi lưu kết quả cùng run ID trong SQLite; frontend lấy JSON để trình bày và mở lại. Cơ sở dữ liệu phục vụ lưu trữ, không nằm giữa mọi phép tính nội bộ của engine. Python xử lý mô hình, NetworkX phân tích cấu trúc mạng và Playwright kiểm thử tương tác. Docker/PostgreSQL/Redis/Celery là phương án cấu hình tùy chọn, chưa được xác nhận vận hành trong bản local này.')
    table_before(doc, anchor, ['Module','Đường dẫn','Vai trò'], [
        ['Engine','sim/','Aave/Uniswap, Terra và chỉ tiêu'],['API','backend/app/','Kiểm tra request, gọi engine và lưu run'],['Giao diện','frontend/app/','Tham số, biểu đồ và xem kết quả'],['Kiểm thử','tests/; frontend/lib/*.test.ts','Hồi quy backend/giao diện'],['Vận hành','scripts/start_demo.ps1','Khởi động FastAPI và Next.js local'],
    ])
    insert(anchor, 'Hai luồng thao tác và kết quả', 'Heading 2')
    insert(anchor, 'Luồng Aave bắt đầu từ nhãn nguồn dữ liệu, chọn scenario, sửa tham số và chạy để xem HF, thanh lý và giá. Luồng Terra tách khám phá lịch sử khỏi B0–B3 synthetic. Kết quả synthetic đã lưu chuyển sang Exit Calculator với giá và thời điểm cảnh báo; người dùng khai báo khả năng khớp, giá thực thi, phí và độ trễ. Saved Runs và ZIP giữ kết quả để kiểm tra lại.')
    pictures = [('01-aave-fixture.png','Tổng quan Aave với nhãn fixture'),('06-terra-synthetic-warning.png','Bốn trạng thái cảnh báo synthetic'),('10-exit-capacity-partial.png','Kết quả thoát một phần vị thế')]
    for filename, caption in pictures:
        insert(anchor, f'Giao diện sau tích hợp PR #61 minh họa: {caption.lower()}.')
        p = insert(anchor,'')
        p.add_run().add_picture(str(REPO/'docs/demo/evidence/frontend-ui-improvements'/filename),width=Inches(6))
        insert(anchor,f'Hình 7: {caption} — nguồn: ảnh trình duyệt PR #61, fixture/synthetic.')
    insert(anchor, 'Kiểm thử và đóng góp thành viên', 'Heading 2')
    insert(anchor, 'Phiên bản có PR #61 đạt 32 frontend tests, lint và production build khi chạy lại local; smoke API đạt 9/9 và nhóm Python targeted đạt 18/18. Các nhóm có thể chồng lấn hồi quy, vì vậy không cộng thành một tổng kiểm thử độc lập. Real-RPC smoke phụ thuộc cấu hình và phải ghi trạng thái thực tế của CI.')
    table_before(doc,anchor,['Thành viên','Vai trò và bằng chứng'],[
        ['Đỗ Quốc Dũng','Nghiên cứu, mô hình hóa, dữ liệu và điều phối tích hợp; Doquocdung1609'],
        ['Đỗ Trung Hải','Backend/API, tích hợp demo và kiểm thử; Trunghai05, PR #58/#59'],
        ['Nguyễn Quang Minh','Frontend và trực quan hóa; Minh-1512, PR #61; ba commit được giữ khi merge. Phụ trách slide/thuyết trình; phần chỉnh lý hồ sơ bằng Codex được ghi là hỗ trợ chung.'],
    ])
    for section in doc.sections:
        footer = section.footer.paragraphs[0]
        footer.clear()
        field = OxmlElement('w:fldSimple')
        field.set(qn('w:instr'),'PAGE')
        footer._p.append(field)
    for table in doc.tables:
        for row in table.rows:
            prop = row._tr.get_or_add_trPr()
            prop.append(OxmlElement('w:cantSplit'))
    doc.save(ROOT/'01_BAO_CAO/DeFiStress_Bao_Cao_BTL_FINAL.docx')
    print('Saved current-source V3 revision')


if __name__ == '__main__':
    main()
