"use client";

import type { ChatMessage as Msg } from "../_lib/types";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { Chip } from "./Buttons";
import { SUGGESTED_CHIPS } from "../_data/chat-suggestions";
import { StickToBottom, useStickToBottomContext } from "use-stick-to-bottom";

interface ChatPanelProps {
  messages: Msg[];
  onSend: (body: string) => void;
  onRefClick: (kind: "ref" | "sao", value: string) => void;
  onChipClick: (chip: string) => void;
  pending?: boolean;
}

export function ChatPanel({ messages, onSend, onRefClick, onChipClick, pending = false }: ChatPanelProps) {
  return (
    <div className="flex flex-col gap-4 h-full min-h-0">
      <StickToBottom
        className="flex-1 min-h-0 relative"
        resize="smooth"
        initial="instant"
      >
        <StickToBottom.Content
          className="flex flex-col gap-[18px] py-5 pr-3 pl-1"
          scrollClassName="chat-scroll"
        >
          <div className="flex items-center gap-3 text-[11px] tracking-[2px] text-[var(--color-ink-4)] uppercase">
            <span className="flex-1 h-px bg-[var(--color-ink-4)]" />
            <span>BẮT ĐẦU CUỘC NÓI CHUYỆN</span>
            <span className="flex-1 h-px bg-[var(--color-ink-4)]" />
          </div>
          {messages.map((m) => (
            <ChatMessage key={m.id} msg={m} onRefClick={onRefClick} />
          ))}
          {messages.length <= 1 && (
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_CHIPS.map((c) => (
                <Chip key={`sug-${c}`} onClick={() => onChipClick(c)}>{c}</Chip>
              ))}
            </div>
          )}
        </StickToBottom.Content>
        <ScrollToBottomButton />
      </StickToBottom>
      <ChatInput onSend={onSend} disabled={pending} />
    </div>
  );
}

function ScrollToBottomButton() {
  const { isAtBottom, scrollToBottom } = useStickToBottomContext();
  if (isAtBottom) return null;
  return (
    <button
      type="button"
      onClick={() => scrollToBottom()}
      className="absolute left-1/2 -translate-x-1/2 bottom-3 z-10 w-9 h-9 rounded-full grid place-items-center text-[18px] text-[var(--color-paper)] border-0 cursor-pointer"
      style={{ background: "var(--color-crimson)", boxShadow: "0 4px 12px rgba(139,42,31,0.4)" }}
      aria-label="Cuộn xuống dưới"
    >
      ↓
    </button>
  );
}
