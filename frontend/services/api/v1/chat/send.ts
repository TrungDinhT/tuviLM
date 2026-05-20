import { useMutation } from "@tanstack/react-query";
import { API_URL } from "@/constants/env";

export type StreamEvent =
  | { type: "ids"; user_message_id: string; assistant_message_id: string }
  | { type: "text"; delta: string }
  | { type: "tool_call"; id: string; name: string; arguments: unknown }
  | { type: "tool_result"; id: string; name: string | null; content: unknown }
  | { type: "failed"; assistant_message_id: string; status: "failed"; message: string }
  | { type: "done"; status: "confirmed" };

export interface StreamHandlers {
  onEvent: (event: StreamEvent) => void;
  signal?: AbortSignal;
}

export interface StreamChatVars {
  clientId: string;
  sessionId: string;
  parentId: string;
  content: string;
  onEvent: (event: StreamEvent) => void;
  signal?: AbortSignal;
}

export async function streamChat(
  req: { clientId: string; sessionId: string; parentId: string; content: string },
  { onEvent, signal }: StreamHandlers,
): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/chat/stream`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      client_id: req.clientId,
      session_id: req.sessionId,
      parent_id: req.parentId,
      content: req.content,
    }),
    signal,
  });
  if (!res.ok || !res.body) {
    let detail = "";
    try {
      const body = await res.json();
      detail = typeof body?.detail === "string" ? body.detail : "";
    } catch {
      detail = "";
    }
    throw new Error(detail || `Stream chat failed (HTTP ${res.status})`);
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
    mutationFn: ({ clientId, sessionId, parentId, content, onEvent, signal }: StreamChatVars) =>
      streamChat({ clientId, sessionId, parentId, content }, { onEvent, signal }),
  });
}
