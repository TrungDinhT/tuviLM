"use client";

import { cn } from "@/lib/utils";

import styles from "./chat-bubble.module.css";
import { MarkdownBody } from "./markdown";

export type BubbleStatus = "confirmed" | "failed" | "cancelled" | "streaming";

/**
 * One chat message. User messages carry the runtime accent; assistant messages
 * sit on frosted glass and render their body as markdown. While the assistant
 * is still thinking (streaming, no text yet) it shows the current activity —
 * e.g. "Đang tra cứu…" — with a pulsing dot.
 */
export function ChatBubble({
  role,
  status,
  content,
  activity,
}: {
  role: "user" | "assistant";
  status: BubbleStatus;
  content: string;
  /** The current tool activity, shown while the assistant is still thinking. */
  activity?: string | null;
}) {
  const isUser = role === "user";
  const thinking = !isUser && status === "streaming" && content.trim() === "";

  return (
    <div className={cn("flex flex-col", isUser ? "items-end" : "items-start")}>
      <div
        className={cn(
          "max-w-[82%] rounded-[20px] px-4 py-[13px] text-[14.5px] leading-[1.5]",
          isUser
            ? "rounded-br-[6px] bg-[linear-gradient(135deg,var(--accent-2),var(--accent))] font-medium text-bg-0"
            : "rounded-bl-[6px] border border-glass-line bg-glass text-ink",
        )}
      >
        {isUser ? (
          <span className="whitespace-pre-wrap">{content}</span>
        ) : thinking ? (
          <Thinking activity={activity} />
        ) : (
          <MarkdownBody body={content} />
        )}
      </div>
      {!isUser && (status === "failed" || status === "cancelled") ? (
        <span className="mt-1 text-[11px] text-muted">
          {status === "failed" ? "Tin nhắn chưa gửi trọn vẹn." : "Đã dừng trả lời."}
        </span>
      ) : null}
    </div>
  );
}

function Thinking({ activity }: { activity?: string | null }) {
  return (
    <span className="flex items-center gap-2 text-muted">
      <span className={styles.dot} />
      <span>{activity ? `${activity}…` : "Thiên Hạc đang suy nghĩ…"}</span>
    </span>
  );
}
