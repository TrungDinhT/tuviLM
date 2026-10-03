"use client";

import { Dialog } from "@/components/primitives/dialog";
import { Pill } from "@/components/primitives/pill";
import type { ChatSessionSummary } from "@/lib/api/schemas";
import { cn } from "@/lib/utils";

import { sessionLabel } from "./session-label";

/**
 * The session history — a panel overlay listing the profile's conversations.
 * Selecting one switches the chat; "Tạo mới" starts a fresh conversation.
 */
export function SessionHistory({
  open,
  onOpenChange,
  sessions,
  activeSessionId,
  creating,
  createDisabled,
  onSelect,
  onCreateNew,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  sessions: ChatSessionSummary[];
  activeSessionId: string | null;
  creating: boolean;
  createDisabled: boolean;
  onSelect: (id: string) => void;
  onCreateNew: () => void;
}) {
  return (
    <Dialog
      open={open}
      onOpenChange={onOpenChange}
      variant="panel"
      title="Lịch sử trò chuyện"
      description="Chọn một cuộc trò chuyện để xem lại."
      footer={
        <Pill
          type="button"
          className="w-full py-[13px] text-[14px]"
          disabled={creating || createDisabled}
          onClick={onCreateNew}
        >
          Tạo cuộc trò chuyện mới
        </Pill>
      }
    >
      <div className="flex flex-col gap-2">
        {sessions.map((session) => (
          <button
            key={session.id}
            type="button"
            onClick={() => onSelect(session.id)}
            className={cn(
              "flex w-full items-center justify-between gap-3 rounded-2xl border px-4 py-3 text-left",
              session.id === activeSessionId
                ? "border-accent-glow bg-glass"
                : "border-glass-line bg-glass",
            )}
          >
            <span className="min-w-0 flex-1 truncate text-[13.5px] font-medium">
              {sessionLabel(session)}
            </span>
            {session.id === activeSessionId ? (
              <span className="flex-none text-[11px] font-semibold text-accent">Hiện tại</span>
            ) : null}
          </button>
        ))}
        {sessions.length === 0 ? (
          <p className="text-[13.5px] text-muted">Chưa có cuộc trò chuyện nào.</p>
        ) : null}
      </div>
    </Dialog>
  );
}
