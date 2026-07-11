export interface SaoDetail {
  name: string;
  chinese?: string;
  epithet?: string;
  tags: string[];
  body: string;
  followUp: string[];
}

export const MOCK_STARS: Record<string, SaoDetail> = {
  "Kình Dương": {
    name: "Kình Dương",
    chinese: "羊刃",
    epithet: '"Lưỡi đao"',
    tags: ["Hung tinh", "Lục Sát", "Hành Kim"],
    body: "Sát tinh chủ về tranh chấp, thương tích, thị phi. Đắc địa ở Sửu Mùi Thìn Tuất.\n\nTại cung Thiên Di — dễ vướng kiện tụng, đặc biệt khi đi xa hoặc ký kết.",
    followUp: ["Cách hoá giải Kình Dương?", "Khi nào kích hoạt mạnh nhất?", "Tam phương tứ chính"],
  },
  "Thiên Tướng": {
    name: "Thiên Tướng",
    chinese: "天相",
    epithet: '"Tướng quân hỗ trợ"',
    tags: ["Cát tinh", "Hành Thuỷ"],
    body: "Sao chủ phụ tá, ngay thẳng, công minh. Hợp làm tham mưu, quản lý hơn là khởi nghiệp một mình.\n\nĐắc địa ở Tý Ngọ Sửu Mùi.",
    followUp: ["Hợp ngành nghề gì?", "Cách kết hợp với chính tinh khác"],
  },
  "Tử Vi": {
    name: "Tử Vi",
    chinese: "紫微",
    epithet: '"Đế tinh"',
    tags: ["Chính tinh", "Đế vương", "Hành Thổ"],
    body: "Vua của các sao. Chủ quyền uy, tôn quý, dẫn dắt. Cần cát tinh phù trợ mới phát huy hết. Tại Mệnh: chí lớn, khí phách đế vương, đôi khi cao ngạo.",
    followUp: ["Tử Vi cần cát tinh nào?", "Tử Vi cư Ngọ là cách gì?"],
  },
  "Phá Quân": {
    name: "Phá Quân",
    chinese: "破軍",
    epithet: '"Phá phách, khai mở"',
    tags: ["Chính tinh", "Hung", "Hành Thuỷ"],
    body: "Chủ phá cũ lập mới. Người Phá Quân làm thì làm lớn, nghỉ thì nghỉ hẳn. Đắc địa ở Tý Ngọ Thìn Tuất.",
    followUp: ["Phá Quân tại Mệnh nên làm gì?", "Cách kiềm chế tính phá"],
  },
};

export function getSaoDetail(name: string): SaoDetail {
  return MOCK_STARS[name] ?? {
    name,
    tags: ["Chưa có dữ liệu"],
    body: `Chi tiết về sao ${name} sẽ được bổ sung. Hỏi thầy để biết thêm.`,
    followUp: ["Hỏi thầy về sao này"],
  };
}
