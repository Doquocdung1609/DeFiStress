"""Finish the retained V3 master using locked tables and explicit model definitions."""

# ruff: noqa: E501
from __future__ import annotations

import csv
import re
import shutil
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt
from docx.text.paragraph import Paragraph
from revise_v3 import insert, table_before

ROOT = Path('C:/Users/Admin/Desktop/NHOM_01_DEFISTRESS_BAO_CAO_BTL')
QA = Path('C:/Users/Admin/Desktop/DeFiStress-BTL-V3')
REPO = Path(__file__).resolve().parents[2]
TARGET = ROOT/'01_BAO_CAO/DeFiStress_Bao_Cao_BTL_FINAL.docx'


def eq(anchor, expression, explanation):
    p = insert(anchor, '')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    math = OxmlElement('m:oMathPara')
    formula = OxmlElement('m:oMath')
    def append_math(parent, value):
        for token in re.split(r'([A-Za-zΣ]+_[A-Za-z]+)',value):
            if not token:
                continue
            if re.fullmatch(r'[A-Za-zΣ]+_[A-Za-z]+',token):
                base,index=token.split('_',1)
                sub=OxmlElement('m:sSub')
                for tag,text in [('m:e',base),('m:sub',index)]:
                    element=OxmlElement(tag)
                    run=OxmlElement('m:r')
                    value_node=OxmlElement('m:t')
                    value_node.text=text
                    run.append(value_node)
                    element.append(run)
                    sub.append(element)
                parent.append(sub)
            else:
                run=OxmlElement('m:r')
                value_node=OxmlElement('m:t')
                value_node.text=token
                run.append(value_node)
                parent.append(run)
    if expression.startswith('HF =') or expression=='p̂ = k / n':
        lhs,rhs=expression.split(' = ',1)
        numerator,denominator=rhs.rsplit(' / ',1)
        append_math(formula,lhs+' = ')
        fraction=OxmlElement('m:f')
        for tag,value in [('m:num',numerator),('m:den',denominator)]:
            element=OxmlElement(tag)
            append_math(element,value)
            fraction.append(element)
        formula.append(fraction)
    else:
        append_math(formula,expression)
    math.append(formula)
    p._p.append(math)
    insert(anchor, explanation)


def heading(doc, name):
    return next(p for p in doc.paragraphs if p.text == name)


def field(p, instruction):
    item = OxmlElement('w:fldSimple')
    item.set(qn('w:instr'), instruction)
    p._p.append(item)


def main():
    retained = QA/'source/v3-editorial-master.docx'
    if not retained.exists():
        shutil.copy2(TARGET, retained)
    doc = Document(retained)
    for p in doc.paragraphs:
        replacements = {
            'giá trị khởi tạo ngẫu nhiên cố định': 'seed cố định',
            'giá trị khởi tạo ngẫu nhiên': 'seed',
            'hiện tại. tài liệu': 'hiện tại. Tài liệu',
            '(CPMI, 2023)': '(Kosse et al., 2023)',
            'Chi phí phí giao dịch': 'Chi phí giao dịch',
            'sổ kết quả kết quả': 'sổ kết quả',
            'giao dịch giao dịch hoán đổi': 'giao dịch hoán đổi',
            'Terra cung cấp kiểm chứng lịch sử nhưng và phạm vi diễn giải kết quả': 'Terra: kiểm chứng lịch sử và phạm vi diễn giải',
            'Việc giữ lại kết quả âm này giúp báo cáo có tính phòng thủ khoa học tốt hơn và tránh nhầm lẫn giữa tái dựng lịch sử với dự báo ngoài mẫu.': 'Kết quả âm xác định rõ tín hiệu phản ánh giai đoạn căng thẳng sâu hơn là dự báo mất neo ban đầu.',
        }
        for old, new in replacements.items():
            if old in p.text:
                p.text = p.text.replace(old, new)
        if p.text.startswith('Nghiên cứu đã xây dựng một quy trình mô phỏng'):
            p.text = 'Nhóm xây dựng DeFiStress Lab gồm mô hình tác tử Aave–Uniswap, lớp phân tích Terra và ứng dụng tương tác có lưu/xuất kết quả. Lưới gốc 32 tổ hợp ghi nhận độ sâu 0/1/2 lần lượt 12/20/0; lưới mở rộng 60 tổ hợp ghi nhận 18/38/4 dưới Policy A. Đối chứng B loại vòng hai trong tập mục tiêu, còn C moderate giữ 2/10 đường Monte Carlo đã chọn. Kết quả chỉ ra chính sách định giá và điều kiện thực thi là hai mắt xích quyết định phản hồi. Arbitrage thu hẹp độ lệch giá còn lại, trong khi tác động tới thanh lý phụ thuộc cấu hình. RQ5 cô lập kênh định giá nợ USDC; RQ6 phân biệt khả năng vay ban đầu, ranh giới HF và động lực thanh lý.'
        if p.text.startswith('Đóng góp chính của nghiên cứu là một quy trình'):
            p.text='DeFiStress Lab kết hợp dữ liệu có provenance, ABM, đối chứng định giá và dashboard tương tác. Người dùng chạy kịch bản, xem cảnh báo, đánh giá phương án thoát theo giả định rồi lưu và xuất kết quả. Các kết luận gắn với đúng mẫu, policy và phạm vi kiểm chứng.'
        if p.text.startswith('Committee on Payments and Market Infrastructures.'):
            p.text = 'Kosse, A., Glowka, M., Mattei, I., & Rice, T. (2023). Will the real stablecoin please stand up? (BIS Papers No. 141). Bank for International Settlements. https://www.bis.org/publ/bppdf/bispap141.htm'
        if p.text.startswith('Lehar, A., & Parlour, C. A.') and 'http' not in p.text:
            p.add_run(' https://www.bis.org/publ/work1062.htm')
        if p.text.startswith('Aave. (2026'):
            p.text = p.text.replace('(2026a)', '(n.d.-a)').replace('(2026b)', '(n.d.-b)')
        if p.text.startswith('HF = (Tổng'):
            p.text = 'HF sử dụng cùng đồng tiền định giá cho tài sản và nợ; công thức danh mục được trình bày tại Chương 4.'
    for p in doc.paragraphs:
        if 'Aave, 2026' in p.text:
            p.text = p.text.replace('Aave, 2026a', 'Aave, n.d.-a').replace('Aave, 2026b', 'Aave, n.d.-b')
        if p.text.startswith('Gas, năng lực kinh doanh chênh lệch giá và năng lực tác nhân'):
            p.text = 'Trong miền thử gốc, gas và công suất tác nhân chưa tạo khác biệt rõ về thanh lý; vốn giảm xuống 25%–50% nhu cầu tham chiếu thì trở thành ràng buộc. Arbitrage có tác động rõ tới độ lệch giá sau điều chỉnh ngay cả khi độ sâu chuỗi và tổng nợ thanh lý không đổi. Vì vậy, phải chọn chỉ tiêu phù hợp với cơ chế của từng tham số.'
        if p.text.startswith('Commit nghiên cứu cuối:'):
            p.text='Nguồn khoa học đã khóa: 3f6e5302483681209e2408531eb5a15389f9fded. Bản phần mềm có PR #61: 25e757adf698f47029565d7b276af856374c698f. Commit hồ sơ và hash từng file được ghi riêng trong manifest nộp bài.'

    anchor = heading(doc, 'Câu hỏi nghiên cứu')
    insert(anchor, 'Bên cạnh sáu câu hỏi mô hình, nhóm xây dựng ứng dụng để người dùng thay tham số, chạy kịch bản, xem kết quả, lưu lượt chạy và xuất dữ liệu. B0–B3 và công cụ thoát vị thế chuyển các giả định thành thao tác có thể kiểm tra, đồng thời giữ nhãn dữ liệu giả lập riêng với lịch sử Terra.')
    anchor = heading(doc, 'Thanh khoản, AMM và Uniswap V3')
    insert(anchor, 'LTV là giới hạn vay ban đầu; LT dùng để xác định mức an toàn của khoản vay đang tồn tại. Ví dụ minh họa, tài sản trị giá 10.000 USD, LTV 75% và LT 80% cho phép vay tối đa 7.500 USD ở lúc mở vị thế. Nếu nợ 6.000 USD thì HF = 1,3333; tài sản giảm còn 7.000 USD làm HF = 0,9333. Ví dụ dùng để giải thích cơ chế, không phải kết quả Mainnet. Close factor giới hạn phần nợ được xử lý trong một lần; planner dùng 50% khi HF trên 0,95 và hai phía đạt 2.000 USD, chuyển tới 100% khi điều kiện tương ứng không còn thỏa. Các nhánh xử lý phần dư vẫn theo planner đã pin.')
    anchor = heading(doc, 'Khoảng trống nghiên cứu và hướng tiếp cận')
    insert(anchor, 'Ba nhóm tài liệu đóng vai trò bổ sung: nghiên cứu giao thức giải thích động lực thanh lý và nhu cầu thanh khoản; ABM cung cấp cách biểu diễn hành vi và phản hồi; lý thuyết mạng mô tả quan hệ giữa các thành phần. Nhóm kế thừa các cơ chế này để nối trạng thái cùng block với thí nghiệm phản thực. Khác biệt giữa kết quả lịch sử và kết quả mô hình được giữ khi so sánh. Tài liệu Bergmeir et al. (2018) bàn về điều kiện áp dụng cross-validation cho mô hình tự hồi quy; nghiên cứu này dùng nó để nhấn mạnh yêu cầu thiết kế đánh giá chuỗi thời gian, không coi đó là chứng minh tính hợp lệ dự báo của Terra.')

    anchor = heading(doc, 'Thiết kế kịch bản và phân tích độ nhạy')
    insert(anchor, 'Công thức và quy tắc tính toán', 'Heading 2')
    equations = [
        ('V_C = Σ_i e_i q_i P_i ; V_D = Σ_j d_j P_j', 'q_i và d_j là lượng token; P là USD/token; e_i bằng 1 khi tài sản được phép làm thế chấp. V_C và V_D có đơn vị USD. Tài sản cung cấp nhưng tắt cờ thế chấp không tham gia tử số HF.'),
        ('HF = (Σ_i e_i q_i P_i LT_i) / V_D', 'LT_i là tỷ lệ không thứ nguyên. Chỉ xét điều kiện thanh lý khi HF < 1 và V_D > 0; trường hợp không nợ được xử lý riêng.'),
        ('BorrowCapacity = Σ_i e_i q_i P_i LTV_i', 'Khả năng vay phản thực có đơn vị USD; không phải dư nợ thực tế của tập 255 danh mục.'),
        ('Repay₀ = f_close × D_USDC ; Seize₀ = Repay₀ × b / P_WETH', 'Đây là bước đầu planner của tuyến USDC/WETH, b là hệ số bonus (1,05 tương ứng 5%). Planner tiếp tục chặn theo tài sản còn lại và xử lý phần dư. Công thức seize dùng xấp xỉ USDC=1 trong tuyến đã triển khai; không là đẳng thức thực thi depeg tổng quát.'),
        ('Impact = |P_after_sale / P_reference − 1| ; Residual = |P_after_arb / P_reference − 1|', 'Hai chỉ tiêu là tỷ lệ, nhân 100 để hiển thị %. Giá ngay sau bán và giá sau arbitrage thuộc hai thời điểm khác nhau trong wave.'),
        ('BadDebt = Σ_k max(0, V_D,k − V_C,k)', 'Phần nợ không được bảo đảm đủ theo giá mô hình, đơn vị USD tương đương. Đây là ước lượng mô hình, không phải khoản lỗ thị trường đã thực hiện.'),
        ('Amplification = TotalLiquidated / DirectLiquidated', 'Thước đo không thứ nguyên; mẫu số là nợ thanh lý trực tiếp. Trường hợp mẫu số bằng 0 tuân theo nhánh bảo vệ của engine, không gán tỷ số vô hạn.'),
        ('p̂ = k / n', 'k là số đường có depth ≥2 và n là số đường của cùng scenario/seed/policy. Khoảng Wilson và các giá trị báo cáo lấy từ bảng khóa, không tính thống kê mới.'),
        ('Wilson = [p̂ + z²/(2n) ± z√(p̂(1−p̂)/n + z²/(4n²))] / [1 + z²/n]', 'z ≈ 1,96 ở mức 95%; p̂ và khoảng đều không thứ nguyên. Công thức mô tả bất định lấy mẫu mô phỏng có điều kiện (Wilson, 1927; Agresti & Coull, 1998).'),
        ('P_A = min(P_ref, P_DEX) ; P_B = P_ref', 'Sau wave hoàn tất, A truyền biến động bất lợi của DEX vào định giá; B chỉ dùng tham chiếu.'),
        ('P_C,t = min(P_ref, P_ref + α(MeanPastDEX_t − P_ref))', 'C weak: α=0,25, lag=1 wave, cửa sổ=3; C moderate: α=0,50, lag=1, cửa sổ=2. Chỉ dùng giá của các wave đã hoàn tất; min_periods=1. Đây là proxy giả định, không là oracle Aave/Chainlink.'),
    ]
    for expression, explanation in equations:
        eq(anchor, expression, explanation)
    insert(anchor, 'Thanh khoản V3 sử dụng căn giá s=√P. Trong một khoảng có L cố định, Δx = L(1/s_b − 1/s_a) và Δy = L(s_a − s_b) khi giá giảm từ s_a xuống s_b. Lượng token được quy đổi theo decimals của pool. Khi vượt tick đã khởi tạo, active liquidity đổi theo liquidity net với chiều crossing; không nối toàn miền bằng một L cố định (Adams et al., 2021).')
    anchor = heading(doc, 'Kết quả mô phỏng Monte Carlo')
    insert(anchor, 'Bốn trường hợp vòng hai trong lưới mở rộng có cú sốc −40% hoặc −50%, kết hợp haircut 90% hoặc 95%, dưới Policy A. Các haircut này là phản thực cực đoan. Kết quả khác miền 32 ô là do thay đổi miền stress; không cộng hai lưới thành 92 trường hợp độc lập.')
    table_before(doc,anchor,['Số đường Severe','Depth ≥2','Tần suất','Seed'],[(r['actual_runs'],r['depth_ge_2_successes'],f"{float(r['depth_ge_2_frequency'])*100:.2f}%",r['seed']) for r in csv.DictReader((REPO/'data/processed/research_final/frozen_v3/tables/rq1_monte_carlo.csv').open()) if r['label']=='Severe'])
    insert(anchor, 'Với seed 20260914, tần suất của các tiền tố lần lượt 4,00%, 3,10%, 2,78% và 2,80%. Mẫu lớn làm tần suất ổn định hơn trong phân phối giả định; các tiền tố vẫn phụ thuộc nhau. Hai seed kiểm tra ở 1.000 đường ghi nhận 2,3% và 3,7%. Khoảng Wilson đã lưu cho 280/10.000 xấp xỉ 2,49%–3,14%, chỉ thuộc Severe Policy A.')

    anchor = heading(doc, 'Phân tích mạng lưới rủi ro nhiều lớp')
    insert(anchor, 'Cảnh báo giả lập B0–B3 và phương án hành động', 'Heading 2')
    insert(anchor, 'B0 là đối chứng không phát cảnh báo khi dữ liệu hợp lệ. B1 xét mức mất neo giảm của UST bền qua cửa sổ quan sát, d = min_t max(0,1−P_UST,t/P_neo). B2 xét mức giảm hiện tại của LUNA, l = max(0,−r_t). B1 có ngưỡng WATCH/HIGH 0,5%/1%; B2 dùng 5%/10%. Hệ thống kiểm tra thời điểm sẵn có trước khi tính; dữ liệu thiếu hoặc đến muộn có thể khiến ABSTAIN, kể cả đối chứng B0.')
    eq(anchor,'S_B3 = 0,5 min(1,d/0,02) + 0,5 min(1,l/0,20)','Điểm B3 từ 0 đến 1; WATCH từ 0,5 và HIGH từ 0,75. Tín hiệu mean/variance LUNA được xuất để giải thích, không tự thêm vào điểm composite. Nguồn: defistress_v2/terra_warning/engine.py.')
    insert(anchor, 'Ví dụ API đã kiểm tra: UST=0,99; LUNA từ 100 xuống 90 cho B0 NORMAL, B1 HIGH, B2 HIGH và B3 WATCH. UST=0,96 và LUNA còn 50 cho B3 HIGH. Đây là vector giả lập dùng để kiểm tra quy tắc, khác dữ liệu lịch sử 2022.')
    eq(anchor,'Q_fill = min(Q, Capacity) ; Gross = Q_fill × P_exit','Q và Capacity tính bằng UST, P_exit tính bằng USD/UST. Khi capacity không có bằng chứng, đầu ra NOT_VERIFIABLE giữ số lượng khớp chưa xác định.')
    eq(anchor,'Net = Gross × (1 − fee − slippage) ; Q_left = Q − Q_fill','Phí và trượt giá là tỷ lệ; backend chặn tổng lớn hơn 100%. Với Q=1.000 UST, capacity=600 UST, P_exit=0,8 USD/UST, fee=1%, slippage=2%, gross=480 USD và net=465,6 USD.')
    eq(anchor,'Loss_filled = Q_fill × P_warning − Net','Ở ví dụ P_warning=1 USD/UST, lỗ trên phần 600 UST đã thoát là 134,4 USD; còn 400 UST chưa thoát, không được gộp vào khoản lỗ đã thực hiện theo giả định này. Giá thực thi do người dùng nhập, chưa tự suy ra từ thanh khoản lịch sử.')
    anchor = heading(doc,'Công nghệ và luồng xử lý sản phẩm')
    table_before(doc,anchor,['API dưới /api/v1','Method','Đầu vào → đầu ra'],[
        ['/terra/demo/warnings','POST','Giá/timestamp synthetic → trạng thái B0–B3, lineage và run ID'],
        ['/terra/demo/exits','POST','Số lượng, giá, capacity, chi phí → net và phần chưa thoát'],
        ['/terra/demo/runs/{run_id}','GET','Run ID → kết quả đã lưu'],
        ['/terra/demo/runs/{run_id}/export','GET','Run ID → ZIP kết quả'],
        ['/terra/demo/historical-data','GET','Phạm vi hiển thị → dữ liệu lịch sử có nhãn nguồn'],
        ['/terra/stress-test','POST','Scenario/seed → quỹ đạo phản thực'],
    ])
    for p in doc.paragraphs:
        if p.text.startswith('Nguồn:'):
            p.paragraph_format.keep_with_next = False
        if p.style.name.startswith('Heading'):
            p.paragraph_format.keep_with_next = True
    chapter_cursor=0
    for node in list(doc.element.body):
        if node.tag==qn('w:p'):
            p=Paragraph(node,doc)
            if p.style.name=='Heading 1':
                chapter_cursor+=1
        elif node.tag==qn('w:tbl') and 1<=chapter_cursor<=7:
            previous=node.getprevious()
            previous_text=''.join(previous.itertext()) if previous is not None else ''
            if not re.match(r'^Bảng\s+\d',previous_text):
                element=OxmlElement('w:p')
                node.addprevious(element)
                caption=Paragraph(element,doc)
                first_text=''.join(node.itertext())[:180]
                title='Phạm vi nguồn và mẫu nghiên cứu' if chapter_cursor==3 else 'Đối chiếu theo phạm vi mục'
                for key,value in [('Policy','Đối chứng policy và eligible/executed'),('Số đường Severe','Các tiền tố Severe Monte Carlo'),('API dưới','API và kết quả trả về'),('Module','Các module phần mềm'),('Thành viên','Ba thành viên và minh chứng'),('RQ','Ma trận kết luận theo câu hỏi nghiên cứu')]:
                    if key in first_text:
                        title=value
                        break
                caption.text=f'Bảng {chapter_cursor}.99: {title}'
    for name in ['Figure Caption', 'Table Caption']:
        if name not in doc.styles:
            style=doc.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
            style.base_style=doc.styles['Caption']
    # Rebuild captions and automatic lists from the actual final document order.
    chapter = 0
    counts = {}
    caption_rows = []
    for p in list(doc.paragraphs):
        if p.style.name == 'Heading 1':
            chapter += 1
        match = re.match(r'^(Hình|Bảng)\s+\d+(?:\.\d+)?\s*:\s*(.*)',p.text)
        if match:
            label,title=match.groups()
            key=(chapter,label)
            counts[key]=counts.get(key,0)+1
            number=f'{chapter}.{counts[key]}'
            p.clear()
            p.add_run(f'{label} {chapter}.')
            field(p,f'SEQ {"Figure" if label=="Hình" else "Table"}{chapter} \\* ARABIC')
            p.add_run(': '+title)
            p.style='Figure Caption' if label=='Hình' else 'Table Caption'
            p.paragraph_format.keep_with_next=False
            caption_rows.append((label,number,title))
    # Remove inherited manually maintained lists; replace with real TOC fields.
    for label, title in [('Hình','DANH MỤC HÌNH ẢNH'),('Bảng','DANH MỤC BẢNG BIỂU')]:
        p=next((x for x in doc.paragraphs if x.text==title),None)
        if p is not None:
            nxt=p._p.getnext()
            if nxt is not None and nxt.tag==qn('w:tbl'):
                nxt.getparent().remove(nxt)
            listing=p.insert_paragraph_before('')
            p._p.addnext(listing._p)
            style_name='Figure Caption' if label=='Hình' else 'Table Caption'
            field(listing,f'TOC \\t "{style_name},1" \\h \\z')
    # Preserve existing sections, suppress both cover footers.
    for section in doc.sections:
        section.different_first_page_header_footer=True
        for p in section.first_page_footer.paragraphs:
            p.clear()
    doc.sections[0].footer.paragraphs[0].clear()
    for index,section in enumerate(doc.sections):
        if index==0:
            continue
        section.footer.is_linked_to_previous=False
        section.different_first_page_header_footer=False
        footer=section.footer.paragraphs[0]
        footer.clear()
        field(footer,'PAGE')
        page_type=section._sectPr.find(qn('w:pgNumType'))
        if page_type is not None and index==1:
            page_type.set(qn('w:fmt'),'lowerRoman')
    for table in doc.tables:
        for row_index,row in enumerate(table.rows):
            trpr=row._tr.get_or_add_trPr()
            if trpr.find(qn('w:cantSplit')) is None:
                trpr.append(OxmlElement('w:cantSplit'))
            for cell in row.cells:
                for p in cell.paragraphs:
                    if 'Năng lực kinh doanh chênh lệch giá không tạo phản ứng' in p.text or 'năng lực kinh doanh chênh lệch giá không tạo phản ứng' in p.text:
                        p.text='Arbitrage thu hẹp độ lệch giá còn lại; chỉ tiêu thanh lý không nhất thiết thay đổi cùng mức.'
                    if p.text=='KẾT QUẢ ÂM' and row.cells[0].text=='RQ4':
                        p.text='CÓ ĐIỀU KIỆN'
                    p.paragraph_format.keep_with_next=row_index<len(table.rows)-1
                    if p.text.strip() == 'Thời gian phục hồi':
                        p.text = 'Thời gian xử lý vị thế'
                    if p.text.strip() == 'giá trị khởi tạo ngẫu nhiên':
                        p.text = 'Seed'
                    for run in p.runs:
                        run.font.size=Pt(10)
    in_chapters=False
    for p in doc.paragraphs:
        if p.style.name=='Heading 1':
            in_chapters=True
        if in_chapters and p.style.name!='Heading 1':
            for br in list(p._p.iter(qn('w:br'))):
                if br.get(qn('w:type'))=='page':
                    br.getparent().remove(br)
        if p.style.name=='Table Caption':
            p.paragraph_format.keep_with_next=True
        if p._p.xpath('.//w:drawing'):
            p.paragraph_format.keep_with_next=True
    for paragraph in doc.paragraphs:
        if paragraph.text.startswith('Các kết quả nghiên cứu được lưu cùng kịch bản'):
            paragraph.text = 'Đầu vào, kịch bản, seed và hash được lưu để tái lập. Kiểm thử API, Python và trình duyệt gắn với đúng phiên bản; các bộ hồi quy chồng lấn không được cộng thành một tổng độc lập.'
        if paragraph.text.startswith('Lệnh chuẩn để tái lập toàn bộ package nghiên cứu'):
            paragraph.text = 'Lệnh chạy bản demo nộp bài (khác với quy trình tái lập bộ nghiên cứu đã khóa):'
        if paragraph.text.startswith('Nguồn: Nhóm nghiên cứu xây dựng từ cơ chế Aave và Uniswap V3'):
            paragraph.text = 'Nguồn: Sơ đồ cơ chế của mô hình. Liên kết giá DEX → HF đi qua Policy A/C giả định; đây không phải sơ đồ oracle Aave Mainnet đã được xác minh.'
        if paragraph.style.name == 'Table Caption' and '7.5' in paragraph.text:
            # Keep field-based numbering while correcting only the caption description.
            for run in paragraph.runs:
                if 'Đối chứng policy và eligible/executed' in run.text:
                    run.text = run.text.replace('Đối chứng policy và eligible/executed', 'Ma trận kết luận và giới hạn sáu RQ')
    for table in doc.tables:
        for row in table.rows:
            if len(row.cells) >= 3 and row.cells[0].text.strip() == 'Thời gian xử lý vị thế':
                row.cells[2].text = 'Thời gian xử lý tập vị thế theo lịch engine; khác thời gian phục hồi giá.'
            if len(row.cells) >= 3 and row.cells[0].text.strip() == 'Nợ xấu' and row.cells[1].text.strip() == 'USDC':
                row.cells[1].text = 'USD tương đương'
            for cell in row.cells:
                if 'Không che giấu việc chưa xuất hiện vòng thanh lý thứ hai' in cell.text:
                    cell.text = 'Lưới gốc không có vòng hai; lưới mở rộng có bốn trường hợp dưới Policy A. Cảnh báo Terra bỏ lỡ mất neo ban đầu.'
    # Avoid an overflowed explicit page-break paragraph after the abstract.
    for index, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip() == 'MỤC LỤC':
            paragraph.paragraph_format.page_break_before = True
            if index:
                previous = doc.paragraphs[index - 1]
                for br in list(previous._p.iter(qn('w:br'))):
                    if br.get(qn('w:type')) == 'page':
                        br.getparent().remove(br)
                if not previous.text.strip() and previous._p.find('.//' + qn('w:sectPr')) is None:
                    previous._p.getparent().remove(previous._p)
    for style in doc.styles:
        if style.name.lower().startswith('toc'):
            style.paragraph_format.keep_with_next = False
            style.paragraph_format.keep_together = False
            style.paragraph_format.page_break_before = False
    doc.save(TARGET)
    with (QA/'FORMULA_AND_CAPTION_INVENTORY.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f)
        w.writerow(['type','number','title'])
        w.writerows(caption_rows)
    print(f'Final editorial pass: {chapter} chapters; {len(caption_rows)} caption records')


if __name__=='__main__':
    main()
