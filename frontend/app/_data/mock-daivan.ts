export interface DaiVan {
  range: string;
  tenCan: string;
  theme: string;
  main: string;
  past?: boolean;
  current?: boolean;
}

export interface TieuVan {
  y: number;
  can: string;
  past?: boolean;
  current?: boolean;
}

export const MOCK_DAIVAN: DaiVan[] = [
  { range: "4–13",   tenCan: "Canh Thìn", theme: "Thiếu niên",   main: "Học hành sáng láng, được cha mẹ yêu mến", past: true },
  { range: "14–23",  tenCan: "Tân Tỵ",    theme: "Trưởng thành", main: "Ly hương du học, gặp thầy tốt", past: true },
  { range: "24–33",  tenCan: "Nhâm Ngọ",  theme: "Khởi nghiệp",  main: "Sự nghiệp khởi sắc, quý nhân tương trợ", current: true },
  { range: "34–43",  tenCan: "Quý Mùi",   theme: "Đỉnh cao",     main: "Danh vọng cực thịnh, gặp đối tác lớn" },
  { range: "44–53",  tenCan: "Giáp Thân", theme: "Củng cố",      main: "Gia đạo viên mãn, tài sản ổn định" },
  { range: "54–63",  tenCan: "Ất Dậu",    theme: "Lưu ý",        main: "Sức khoẻ chú ý, tu tâm dưỡng tính" },
  { range: "64–73",  tenCan: "Bính Tuất", theme: "An hưởng",     main: "Tuổi già hạnh phúc, con cháu hiếu thuận" },
  { range: "74–83",  tenCan: "Đinh Hợi",  theme: "Cẩn trọng",    main: "Cẩn thận tật ách, dưỡng thân" },
  { range: "84+",    tenCan: "Mậu Tý",    theme: "Trường thọ",   main: "Đắc hậu phúc, sống lâu" },
];

export const MOCK_TIEUVAN: TieuVan[] = [
  { y: 2024, can: "Giáp Thìn", past: true },
  { y: 2025, can: "Ất Tỵ",    past: true },
  { y: 2026, can: "Bính Ngọ", current: true },
  { y: 2027, can: "Đinh Mùi" },
  { y: 2028, can: "Mậu Thân" },
  { y: 2029, can: "Kỷ Dậu" },
  { y: 2030, can: "Canh Tuất" },
  { y: 2031, can: "Tân Hợi" },
  { y: 2032, can: "Nhâm Tý" },
  { y: 2033, can: "Quý Sửu" },
];
