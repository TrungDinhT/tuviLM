import type { ChatMessage, BuildLasoResponse } from "../_lib/types";

export function seedOpeningMessage(laso: BuildLasoResponse): ChatMessage[] {
  const menh = Object.values(laso.cung_by_position).find(c => c.role === "Mệnh");
  const menhStar = menh?.chinh_tinh[0]?.replace(/\s*\(.*\)\s*$/, "") ?? "vô chính diệu";
  const menhPos = menh?.position ?? "";
  return [
    {
      id: "ai-open",
      sender: "ai",
      body: `Chào con. Thầy vừa xem qua lá số của con — một lá số không tầm thường. Con muốn thầy nói sâu về điều gì trước?`,
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
