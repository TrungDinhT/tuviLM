import type { ChatMessage, BuildLasoResponse } from "../_lib/types";

export function seedOpeningMessage(_laso: BuildLasoResponse): ChatMessage[] {
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
