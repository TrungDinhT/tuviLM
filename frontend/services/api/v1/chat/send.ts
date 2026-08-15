import { useMutation } from "@tanstack/react-query";
import { API_URL } from "@/constants/env";

export type StreamEvent =
  | { type: "ids"; user_message_id: string; assistant_message_id: string }
  | { type: "text"; delta: string }
  | { type: "tool_call"; id: string; name: string; arguments: unknown }
  | { type: "tool_result"; id: string; name: string | null; content: unknown }
  | { type: "result"; output: string | null }
  | { type: "error"; message: string }
  | {
      type: "duplicate_in_progress";
      user_message_id: string;
      assistant_message_id: string;
      status: string;
    }
  | { type: "done"; status?: string };

export interface StreamHandlers {
  onEvent: (event: StreamEvent) => void;
  signal?: AbortSignal;
}

export interface StreamChatVars {
  message: string;
  ownerId: string;
  sessionId: string;
  onEvent: (event: StreamEvent) => void;
  signal?: AbortSignal;
}

export async function streamChat(
  message: string,
  {
    onEvent,
    ownerId,
    sessionId,
    signal,
  }: StreamHandlers & { ownerId: string; sessionId: string },
): Promise<void> {
  if (!ownerId || !sessionId) {
    throw new Error("Missing conversation session.");
  }

  const res = await fetch(
    `${API_URL}/api/v1/sessions/${sessionId}/chat/stream`,
    {
      method: "POST",
      headers: {
        "content-type": "application/json",
        "X-Anonymous-Owner-Id": ownerId,
        "Idempotency-Key": randomId(),
      },
      body: JSON.stringify({ content: message }),
      signal,
    },
  );
  if (!res.ok || !res.body) {
    throw new Error(`Stream chat failed (HTTP ${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  const emit = (raw: string): boolean => {
    const data = raw
      .split("\n")
      .filter((line) => line.trimStart().startsWith("data:"))
      .map((line) => line.slice(line.indexOf("data:") + 5).trim())
      .join("\n");
    if (!data) return false;

    let event: StreamEvent;
    try {
      event = JSON.parse(data) as StreamEvent;
    } catch {
      throw new Error("Không đọc được phản hồi trò chuyện.");
    }
    onEvent(event);
    if (event.type === "error") {
      throw new Error(event.message || "Luồng trò chuyện gặp lỗi.");
    }
    return event.type === "done";
  };

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const raw = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      if (emit(raw)) return;
    }
  }
  if (buffer.trim()) emit(buffer);
}

export function useStreamChat() {
  return useMutation({
    mutationFn: ({ message, ownerId, sessionId, onEvent, signal }: StreamChatVars) =>
      streamChat(message, { ownerId, sessionId, onEvent, signal }),
  });
}

function randomId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
