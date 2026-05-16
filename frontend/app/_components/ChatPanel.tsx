"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage as Msg } from "../_lib/types";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { Chip } from "./Buttons";
import { SUGGESTED_CHIPS } from "../_data/mock-chat";

interface ChatPanelProps {
  messages: Msg[];
  onSend: (body: string) => void;
  onRefClick: (kind: "ref" | "sao", value: string) => void;
  onChipClick: (chip: string) => void;
  pending?: boolean;
}

export function ChatPanel({ messages, onSend, onRefClick, onChipClick, pending = false }: ChatPanelProps) {
  const sentinelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    sentinelRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages.length, pending]);

  return (
    <div className="flex flex-col gap-4 h-full min-h-0">
      <div
        className="flex-1 flex flex-col gap-[18px] p-5 overflow-auto min-h-0 border border-[rgba(26,22,17,0.14)]"
        style={{ background: "rgba(255,252,245,0.55)", boxShadow: "inset 0 1px 0 rgba(255,255,255,0.5), 0 1px 0 rgba(26,22,17,0.06)" }}
      >
        <div className="flex items-center gap-3 text-[11px] tracking-[2px] text-[var(--color-ink-4)] uppercase">
          <span className="flex-1 h-px bg-[var(--color-ink-4)]" />
          <span>BẮT ĐẦU CUỘC NÓI CHUYỆN</span>
          <span className="flex-1 h-px bg-[var(--color-ink-4)]" />
        </div>
        {messages.map((m) => (
          <ChatMessage key={m.id} msg={m} onRefClick={onRefClick} />
        ))}
        {pending && (
          <div className="self-start font-serif italic text-[14px] text-[var(--color-ink-3)]">
            Thầy đang suy…
          </div>
        )}
        {messages.length <= 1 && (
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_CHIPS.map((c) => (
              <Chip key={`sug-${c}`} onClick={() => onChipClick(c)}>{c}</Chip>
            ))}
          </div>
        )}
        <div ref={sentinelRef} />
      </div>
      <ChatInput onSend={onSend} disabled={pending} />
    </div>
  );
}
