export interface HistoryItem {
  time: string;
  q: string;
  cung: string;
  mention: string;
  count: number;
  current?: boolean;
  starred?: boolean;
}

export interface HistoryGroup {
  date: string;
  items: HistoryItem[];
}

export const MOCK_HISTORY: HistoryGroup[] = [
  {
    date: "Hôm nay · 12 May",
    items: [
      { time: "14:18", q: "Sự nghiệp 2026 con có nên nhảy việc?", cung: "Quan Lộc", mention: "Thiên Tướng, Kình Dương", count: 8, current: true },
      { time: "13:30", q: "Cung Tật Ách giải nghĩa thế nào?", cung: "Tật Ách", mention: "Cự Môn, Thiên Đồng", count: 3 },
    ],
  },
  {
    date: "Hôm qua · 11 May",
    items: [
      { time: "21:14", q: "Năm Mùi cưới được không thầy?", cung: "Phu Thê", mention: "Phá Quân, Hồng Loan", count: 12, starred: true },
    ],
  },
  {
    date: "8 May",
    items: [
      { time: "09:02", q: "Tổng quan cả đời con", cung: "Mệnh", mention: "Tử Vi cư Ngọ", count: 24 },
      { time: "08:30", q: "Mẹ con năm nay sức khoẻ thế nào?", cung: "Phụ Mẫu", mention: "Thái Âm hãm", count: 5 },
    ],
  },
  {
    date: "3 May",
    items: [
      { time: "22:40", q: "Có nên đổi công ty cuối năm?", cung: "Quan Lộc", mention: "—", count: 6 },
    ],
  },
];
