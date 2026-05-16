import { useMutation } from "@tanstack/react-query";
import { API_URL } from "@/constants/env";

export type StreamEvent =
  | { type: "text"; delta: string }
  | { type: "tool_call"; id: string; name: string; arguments: unknown }
  | { type: "tool_result"; id: string; name: string | null; content: unknown }
  | { type: "result"; output: string | null }
  | { type: "error"; message: string }
  | { type: "done" };

export interface StreamHandlers {
  onEvent: (event: StreamEvent) => void;
  signal?: AbortSignal;
}

export interface StreamChatVars {
  message: string;
  onEvent: (event: StreamEvent) => void;
  signal?: AbortSignal;
}

export async function streamChat(
  message: string,
  { onEvent, signal }: StreamHandlers,
): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ message }),
    signal,
  });
  if (!res.ok || !res.body) {
    throw new Error(`Stream chat failed (HTTP ${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) !== -1) {
      const raw = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      const line = raw.trim();
      if (!line.startsWith("data:")) continue;
      const json = line.slice(5).trim();
      if (!json) continue;
      try {
        const event = JSON.parse(json) as StreamEvent;
        onEvent(event);
        if (event.type === "done") return;
      } catch {
        // skip malformed lines
      }
    }
  }
}

export function useStreamChat() {
  return useMutation({
    mutationFn: ({ message, onEvent, signal }: StreamChatVars) =>
      streamChat(message, { onEvent, signal }),
  });
}
