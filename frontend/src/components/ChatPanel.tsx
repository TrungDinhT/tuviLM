import { useState } from "react";
import type { ChatMessage } from "../types";

type Props = {
  messages: ChatMessage[];
  onSend: (text: string) => Promise<void>;
  busy: boolean;
};

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
            <p>{m.content}</p>
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
