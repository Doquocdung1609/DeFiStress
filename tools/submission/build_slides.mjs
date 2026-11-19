import fs from 'node:fs/promises';
import path from 'node:path';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const source = 'C:/Users/Admin/Desktop/DeFiStress-BTL-output/slide-hd';
const output = 'C:/Users/Admin/Desktop/NHOM_01_DEFISTRESS_BAO_CAO_BTL/02_SLIDE_THUYET_TRINH/DeFiStress_Nhom_1_FINAL.pptx';
const presentation = Presentation.create({ slideSize: { width: 1920, height: 1080 } });

function text(slide, content, left, top, width, height, size, bold = false, color = '#173259') {
  const box = slide.shapes.add({
    geometry: 'textbox',
    position: { left, top, width, height },
    fill: 'none',
    line: { style: 'solid', fill: 'none', width: 0 },
  });
  box.text = content;
  box.text.style = { fontFamily: 'Arial', fontSize: `${size}pt`, bold, color, wrap: true };
  return box;
}

async function sourceSlide(n) {
  const slide = presentation.slides.add();
  const file = path.join(source, `slide-${String(n).padStart(2, '0')}.jpg`);
  const bytes = await fs.readFile(file);
  slide.images.add({
    blob: bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength),
    contentType: 'image/jpeg',
    alt: `Trang ${n} của slide nghiên cứu DeFiStress Nhóm 1`,
    fit: 'contain',
    position: { left: 0, top: 0, width: 1920, height: 1080 },
  });
  slide.speakerNotes.text = `Nguồn: DefiStress - Nhóm 1.pdf, trang ${n}. Slide ảnh từ tài liệu nhóm; các kết quả được diễn giải trong báo cáo cuối với giới hạn mô hình.`;
}

function newSlide(title, kicker, lines, note) {
  const slide = presentation.slides.add();
  slide.background.fill = '#F7FAFE';
  slide.shapes.add({ geometry: 'rect', position: { left: 0, top: 0, width: 1920, height: 18 }, fill: '#0978C9', line: { fill: 'none', width: 0 } });
  text(slide, kicker.toUpperCase(), 100, 62, 1550, 58, 23, true, '#087BC7');
  text(slide, title, 100, 130, 1720, 135, 45, true, '#173259');
  let y = 325;
  for (const line of lines) {
    slide.shapes.add({ geometry: 'roundRect', position: { left: 100, top: y, width: 1720, height: 112 }, fill: '#FFFFFF', line: { style: 'solid', fill: '#D8E6F2', width: 2 } });
    text(slide, line, 140, y + 22, 1640, 75, 26, false, '#173259');
    y += 133;
  }
  text(slide, 'DeFiStress · Nhóm 1 · Ngành Công nghệ tài chính', 100, 1010, 1500, 35, 16, false, '#6B7D90');
  slide.speakerNotes.text = note;
}

for (let n = 1; n <= 42; n++) await sourceSlide(n);

newSlide('Sản phẩm chạy trên máy: từ dữ liệu đến kết quả', 'Kiến trúc phần mềm', [
  'Frontend Next.js → Backend FastAPI → engine mô phỏng và bộ phân tích Terra.',
  'SQLite lưu lượt chạy; API cho phép mở lại và xuất ZIP kết quả.',
  'Đầu vào có nhãn: fixture demo, dữ liệu lịch sử, snapshot Mainnet hoặc synthetic.',
  'Tính toán ngoài chuỗi; dữ liệu blockchain được đọc để dựng trạng thái đầu vào.',
], 'Slide sản phẩm mới. Demo chạy local tại localhost:3100 và API localhost:8100. Không tuyên bố đã triển khai smart contract hoặc gửi giao dịch Mainnet.');

newSlide('Terra: dữ liệu lịch sử và cảnh báo synthetic tách riêng', 'Trải nghiệm người dùng', [
  'Historical Data và Historical Fit trình bày chuỗi dữ liệu 2022 với chỗ thiếu được giữ nguyên.',
  'Early Warning hồi cứu có giới hạn về thời điểm có thể biết dữ liệu.',
  'Synthetic Warning B0–B3 là tình huống giả định để kiểm tra quy tắc, không là dự báo 2022.',
  'Thiếu hoặc đến muộn dữ liệu có thể dẫn đến ABSTAIN thay vì tự điền giá trị.',
], 'Khi trình bày, phân biệt quan sát lịch sử với đầu vào giả định và không gọi cảnh báo synthetic là dự báo được kiểm chứng ngoài mẫu.');

newSlide('Từ cảnh báo đến phương án thoát vị thế', 'Luồng minh họa', [
  'Chọn kết quả cảnh báo synthetic đã lưu → mở công cụ đánh giá thoát vốn.',
  'Giá và thời điểm cảnh báo được điền từ cùng run; người dùng xác định giá thoát, độ trễ, phí, trượt giá và khả năng khớp.',
  'Báo cáo riêng phần UST khớp, phần còn lại, tiền thu ròng và lỗ trên phần đã thoát.',
  'Kết quả là phản thực có điều kiện, không phải giao dịch hay mức giá thanh khoản thực của năm 2022.',
], 'Ví dụ kiểm thử: 1.000 UST, khớp 600 UST ở 0,8 USD/UST; phí 1%, trượt giá 2%, tiền thu ròng 465,6 USD.');

newSlide('Phương pháp và triển khai blockchain', 'Giải trình kỹ thuật', [
  'Agent-Based Modeling là phương pháp chính: borrower, một liquidator và một arbitrageur đại diện.',
  'Stress tất định và Monte Carlo đánh giá nhiều kịch bản; mạng quan hệ và Terra là các lớp phân tích bổ trợ.',
  'Aave V3 và Uniswap V3 cung cấp dữ liệu on-chain; engine, lưu kết quả và giao diện chạy ngoài chuỗi.',
  'Không triển khai hợp đồng giao dịch: mô phỏng phản thực cần nhiều phép tính nhưng không cần đổi trạng thái tài sản thật.',
], 'Nêu rõ dữ liệu on-chain không đồng nghĩa ứng dụng đã triển khai on-chain; không có giao dịch Mainnet từ bản demo.');

newSlide('Bằng chứng ứng dụng chạy thật', 'Demo và kiểm thử', [
  'Video MP4 ghi màn hình ứng dụng local: Aave fixture → scenario → kết quả → Terra.',
  'Cảnh báo synthetic liên kết sang công cụ thoát vốn; stress test có lượt chạy được lưu và mở lại.',
  'Smoke test kiểm tra nội dung tính toán; browser test kiểm tra thao tác và kết quả hoàn thành.',
  'Nguồn, giới hạn và hướng dẫn chạy được nêu trong README và phụ lục.',
], 'Mở video demo và chỉ ra run ID cùng nhãn nguồn. Không gọi lượt chạy fixture là kiểm chứng Mainnet.');

await sourceSlide(44);
await sourceSlide(45);

const pptx = await PresentationFile.exportPptx(presentation);
await fs.mkdir(path.dirname(output), { recursive: true });
await pptx.save(output);
console.log(JSON.stringify({ output, slides: presentation.slides.items.length }));
