import { useState } from "react";
import ReactMarkdown from "react-markdown";
import type { ChatMessage, ChatToolCall } from "../types";

type Props = {
  messages: ChatMessage[];
  onSend: (text: string) => Promise<void>;
  busy: boolean;
};

function formatToolCallLabel(toolCall: ChatToolCall): string {
  const args = toolCall.arguments;
  if (args === null || args === undefined) return `${toolCall.name}()`;

  if (typeof args === "string") {
    try {
      return formatToolCallLabel({ ...toolCall, arguments: JSON.parse(args) });
    } catch {
      return `${toolCall.name}(${args})`;
    }
  }

  if (Array.isArray(args)) {
    return `${toolCall.name}(${args.map(String).join(", ")})`;
  }

  if (typeof args === "object") {
    const values = Object.values(args as Record<string, unknown>)
      .filter((value) => value !== null && value !== undefined)
      .map(String);
    return `${toolCall.name}(${values.join(", ")})`;
  }

  return `${toolCall.name}(${String(args)})`;
}

function formatToolResult(result: unknown): string {
  if (result === null || result === undefined) return "";
  if (typeof result === "string") return result;
  try {
    return JSON.stringify(result, null, 2);
  } catch {
    return String(result);
  }
}

export default function ChatPanel({ messages, onSend, busy }: Props) {
  const [text, setText] = useState("");

  const submit = async () => {
    const value = text.trim();
    if (!value || busy) return;
    setText("");
    await onSend(value);
  };

  return (
    <section className="panel chat-panel">
      <div className="section-head">
        <h2>Chat</h2>
        <span className="summary">{busy ? "Streaming..." : "Ready"}</span>
      </div>

      <div className="chat-log">
        {messages.map((m) => (
          <article key={m.id} className={`msg ${m.role}`}>
            <header>{m.role === "user" ? "Bạn" : "Trợ lý"}</header>
            {m.toolCalls?.length ? (
              <div className="tool-call-list">
                {m.toolCalls.map((toolCall, index) => {
                  const resultText = formatToolResult(toolCall.result);
                  const key = toolCall.id ?? `${toolCall.name}-${index}`;
                  if (!resultText) {
                    return (
                      <span className="tool-call" key={key}>
                        {formatToolCallLabel(toolCall)}
                      </span>
                    );
                  }
                  return (
                    <details className="tool-call tool-call-detail" key={key}>
                      <summary>{formatToolCallLabel(toolCall)}</summary>
                      <pre className="tool-call-result">{resultText}</pre>
                    </details>
                  );
                })}
              </div>
            ) : null}
            {m.role === "assistant" ? (
              <div className="msg-markdown">
                <ReactMarkdown>{m.content}</ReactMarkdown>
              </div>
            ) : (
              <p>{m.content}</p>
            )}
          </article>
        ))}
      </div>

      <div className="chat-input-row">
        <textarea
          rows={2}
          placeholder="Nhập câu hỏi về lá số..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              void submit();
            }
          }}
        />
        <button className="primary-btn" onClick={() => void submit()} disabled={busy || !text.trim()}>
          Gửi
        </button>
      </div>
    </section>
  );
}
