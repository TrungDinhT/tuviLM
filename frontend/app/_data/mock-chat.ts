import type { ChatMessage, BuildLasoResponse } from "../_lib/types";

export function seedOpeningMessage(laso: BuildLasoResponse): ChatMessage[] {
  const menh = Object.values(laso.cung_by_position).find(c => c.role === "Mệnh");
  const menhStar = menh?.chinh_tinh[0]?.replace(/\s*\(.*\)\s*$/, "") ?? "vô chính diệu";
  const menhPos = menh?.position ?? "";
  return [
    {
      id: "ai-open",
      sender: "ai",
      body: `Chào con. Thầy vừa xem qua lá số của con — một lá số không tầm thường. Mệnh con có [[sao:${menhStar}]] cư [[ref:${menh?.role ?? "Mệnh"}]] (${menhPos}). Con muốn thầy nói sâu về điều gì trước?`,
    },
  ];
}

export const SUGGESTED_CHIPS = [
  "Sự nghiệp đang vướng",
  "Tình duyên 2026",
  "Tài chính cuối năm",
  "Sức khoẻ",
  "Cha mẹ",
  "Tổng quan cả đời",
  "Hỏi điều khác…",
];

const CANNED_REPLIES = [
  "Để thầy xem… Tháng 7 âm con cần cẩn trọng văn từ, hợp đồng. Tháng 10 âm thì hanh thông hơn.",
  "Cung này có [[sao:Thiên Tướng]] — sao chủ phụ tá, ngay thẳng. Con hợp làm tham mưu, quản lý.",
  "Năm Bính Ngọ có [[sao:Kình Dương]] từ cung Thiên Di chiếu sang. Nửa đầu năm cứ làm tốt việc của mình.",
  "Có. [[sao:Thiên Khôi]] [[sao:Thiên Việt]] đồng cung — quý nhân nữ giới, hơn tuổi.",
  "Đại vận hiện tại rất thuận. Nửa cuối đại vận con sẽ có bước nhảy lớn.",
];

export function pickCannedReply(seed: number): ChatMessage {
  const body = CANNED_REPLIES[seed % CANNED_REPLIES.length];
  return { id: `ai-${Date.now()}`, sender: "ai", body };
}
