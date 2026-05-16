import { useMutation } from "@tanstack/react-query";
import type { ChatRequest, ChatResponse } from "@/app/_lib/types";
import { API_URL } from "@/constants/env";

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    throw new Error(`Gửi tin nhắn thất bại (HTTP ${res.status})`);
  }
  const data = await res.json();
  if (!data || typeof data.answer !== "string") {
    throw new Error("Phản hồi chat không hợp lệ");
  }
  return data as ChatResponse;
}

export function useSendChat() {
  return useMutation({
    mutationFn: sendChat,
  });
}
