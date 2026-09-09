"use client";

import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { Pill } from "@/components/primitives/pill";
import { newIdempotencyKey } from "@/lib/api/client";
import { useCreateSession, useGetSession, useListSessions } from "@/lib/api/hooks";
import { queryKeys } from "@/lib/api/queryKeys";
import type { ChatMessage, SseChatEvent } from "@/lib/api/schemas";
import { streamChat } from "@/lib/api/stream";
import { describe, isApiError } from "@/lib/http/errors";
import { useChartStore } from "@/store/chart-store";
import { useToastStore } from "@/store/toast-store";

import { ChatBubble, type BubbleStatus } from "./chat-bubble";
import { Composer } from "./composer";
import { SessionHistory } from "./session-history";
import { toolStatusLabel } from "./tool-status";
import { useStickToBottom } from "./use-stick-to-bottom";

type Terminal = "streaming" | "confirmed" | "failed" | "cancelled";

/** The in-flight exchange that has not yet been read back from the backend. */
interface Draft {
  userContent: string;
  assistantText: string;
  assistantMessageId: string | null;
  terminal: Terminal;
  idempotencyKey: string;
  duplicateInProgress: boolean;
  /** The current tool activity label, shown while the assistant is thinking. */
  activity: string | null;
}

interface ActiveStream {
  controller: AbortController;
  sessionId: string;
  idempotencyKey: string;
}

const GREETING =
  "Chào bạn, tôi là Thiên Hạc — tinh linh dẫn đường. Bạn muốn hỏi điều gì về lá số của mình?";

function doneTerminal(status: string): Terminal {
  switch (status) {
    case "confirmed":
      return "confirmed";
    case "failed":
      return "failed";
    case "cancelled":
      return "cancelled";
    default:
      return "streaming";
  }
}

/**
 * The Hỏi AI screen — a chat with Thiên Hạc.
 *
 * Opens on the most recent session by default, with a browsable history and a
 * "Tạo mới" action. Replies stream token-by-token from the real SSE endpoint.
 * The transcript is the backend's `GET /sessions/{id}`; the in-flight turn is
 * local state that reconciles away once the backend confirms it.
 */
export function HoiAiScreen() {
  const hasChart = useChartStore((state) => state.hasChart);
  const chartProfileId = useChartStore((state) => state.chartProfileId);
  const showToast = useToastStore((state) => state.show);
  const queryClient = useQueryClient();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const autoCreatedFor = useRef<string | null>(null);
  const activeStreamRef = useRef<ActiveStream | null>(null);
  const creatingSessionRef = useRef(false);

  const abortActiveStream = useCallback(() => {
    const active = activeStreamRef.current;
    if (active === null) return;
    activeStreamRef.current = null;
    active.controller.abort();
  }, []);

  useEffect(() => () => abortActiveStream(), [abortActiveStream]);

  const list = useListSessions(chartProfileId);
  const createSession = useCreateSession(chartProfileId);

  const sessions = useMemo(
    () => [...(list.data?.sessions ?? [])].sort((a, b) => b.updated_at.localeCompare(a.updated_at)),
    [list.data],
  );
  const activeSessionId = selectedId ?? sessions[0]?.id ?? null;

  const session = useGetSession(activeSessionId);

  const sessionMessages = session.data?.session.messages ?? [];
  const transcript: ChatMessage[] = sessionMessages.filter(
    (message) => message.status !== "pending",
  );

  const duplicateMessage = draft?.duplicateInProgress
    ? sessionMessages.find((message) => message.id === draft.assistantMessageId)
    : undefined;
  const duplicateStillPending =
    draft?.duplicateInProgress === true &&
    (duplicateMessage === undefined || duplicateMessage.status === "pending");
  const renderedDraft =
    draft?.duplicateInProgress === true &&
    duplicateMessage !== undefined &&
    duplicateMessage.status !== "pending"
      ? {
          ...draft,
          assistantText: duplicateMessage.content,
          terminal: doneTerminal(duplicateMessage.status),
          duplicateInProgress: false,
        }
      : draft;
  const refetchSession = session.refetch;

  useEffect(() => {
    if (!duplicateStillPending) return;
    const timer = window.setInterval(() => {
      void refetchSession();
    }, 1_000);
    return () => window.clearInterval(timer);
  }, [duplicateStillPending, refetchSession]);

  const contentKey = `${transcript.length}:${renderedDraft?.assistantText.length ?? 0}:${renderedDraft?.activity ?? ""}:${renderedDraft?.userContent.length ?? 0}`;
  const { isAtBottom, scrollToBottom } = useStickToBottom(contentKey);

  // Ensure the profile has at least one session so the chat opens on something.
  const needsSession = chartProfileId !== null && list.isSuccess && sessions.length === 0;
  useEffect(() => {
    if (!needsSession || autoCreatedFor.current === chartProfileId) return;
    autoCreatedFor.current = chartProfileId;
    createSession.mutate();
  }, [needsSession, createSession, chartProfileId]);

  if (!hasChart) return null;

  if (chartProfileId === null) {
    return (
      <div className="flex flex-col items-start gap-4 py-10">
        <p className="max-w-[46ch] text-[13.5px] leading-relaxed text-muted">
          Lá số của bạn chưa được lưu để trò chuyện. Hãy an sao lại để Thiên Hạc có thể dẫn đường cho
          bạn.
        </p>
        <Link
          href="/"
          className="rounded-full border border-glass-line bg-glass px-6 py-3 text-[14px] font-semibold no-underline"
        >
          An sao lại
        </Link>
      </div>
    );
  }

  const draftReconciled =
    renderedDraft !== null &&
    renderedDraft.assistantMessageId !== null &&
    transcript.some((message) => message.id === renderedDraft.assistantMessageId);

  const showGreeting =
    transcript.length === 0 && draft === null && !session.isPending && activeSessionId !== null;

  const streaming = renderedDraft !== null && renderedDraft.terminal === "streaming";

  // A fresh conversation (only the greeting, no real message) offers nothing to
  // fork from, so "Tạo mới" is disabled until the active session has a message.
  const createDisabled = activeSessionId === null || transcript.length === 0;

  const updateTurnDraft = (turn: ActiveStream, update: (current: Draft) => Draft) => {
    setDraft((current) =>
      current?.idempotencyKey === turn.idempotencyKey ? update(current) : current,
    );
  };

  const invalidateSession = (sessionId: string) => {
    void queryClient.invalidateQueries({ queryKey: queryKeys.sessions.detail(sessionId) });
    if (chartProfileId !== null) {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.sessions.byProfile(chartProfileId),
      });
    }
  };

  const applyEvent = (event: SseChatEvent, turn: ActiveStream) => {
    if (activeStreamRef.current !== turn) return;
    switch (event.type) {
      case "ids":
        updateTurnDraft(turn, (current) => ({
          ...current,
          assistantMessageId: event.assistant_message_id,
        }));
        break;
      case "tool_call":
        updateTurnDraft(turn, (current) => ({ ...current, activity: toolStatusLabel(event.name) }));
        break;
      case "text":
        updateTurnDraft(turn, (current) => ({
          ...current,
          activity: null,
          assistantText: current.assistantText + event.delta,
        }));
        break;
      case "error":
        updateTurnDraft(turn, (current) => ({ ...current, terminal: "failed", activity: null }));
        showToast("Thiên Hạc chưa thể trả lời trọn vẹn. Bạn thử lại nhé.");
        break;
      case "done":
        updateTurnDraft(turn, (current) => ({
          ...current,
          terminal: doneTerminal(event.status),
          duplicateInProgress: event.status === "duplicate_in_progress",
        }));
        invalidateSession(turn.sessionId);
        break;
      case "duplicate_in_progress":
        updateTurnDraft(turn, (current) => ({
          ...current,
          assistantMessageId: event.assistant_message_id,
          duplicateInProgress: true,
        }));
        invalidateSession(turn.sessionId);
        break;
      default:
        break;
    }
  };

  const send = async (content: string) => {
    if (activeSessionId === null || streaming || activeStreamRef.current !== null) return;
    const trimmed = content.trim();
    if (trimmed === "") return;

    const turn: ActiveStream = {
      controller: new AbortController(),
      sessionId: activeSessionId,
      idempotencyKey: newIdempotencyKey(),
    };
    activeStreamRef.current = turn;
    setDraft({
      userContent: trimmed,
      assistantText: "",
      assistantMessageId: null,
      terminal: "streaming",
      idempotencyKey: turn.idempotencyKey,
      duplicateInProgress: false,
      activity: null,
    });
    scrollToBottom();
    try {
      for await (const event of streamChat(turn.sessionId, trimmed, {
        idempotencyKey: turn.idempotencyKey,
        signal: turn.controller.signal,
      })) {
        applyEvent(event, turn);
      }
    } catch (error) {
      if (activeStreamRef.current !== turn) return;
      if (error instanceof DOMException && error.name === "AbortError") {
        updateTurnDraft(turn, (current) => ({ ...current, terminal: "cancelled" }));
        return;
      }
      updateTurnDraft(turn, (current) => ({ ...current, terminal: "failed" }));
      showToast(
        isApiError(error)
          ? describe(error.error)
          : "Có lỗi xảy ra khi trò chuyện. Bạn thử lại nhé.",
      );
    } finally {
      if (activeStreamRef.current === turn) activeStreamRef.current = null;
    }
  };

  const handleSelect = (id: string) => {
    abortActiveStream();
    setSelectedId(id);
    setDraft(null);
    setHistoryOpen(false);
  };

  const handleCreateNew = async () => {
    if (chartProfileId === null || creatingSessionRef.current) return;
    abortActiveStream();
    creatingSessionRef.current = true;
    try {
      const result = await createSession.mutateAsync();
      setDraft(null);
      setSelectedId(result.session.id);
      setHistoryOpen(false);
    } catch (error) {
      showToast(isApiError(error) ? describe(error.error) : "Không tạo được cuộc trò chuyện.");
    } finally {
      creatingSessionRef.current = false;
    }
  };

  return (
    <div className="flex flex-col gap-4 pb-10">
      <div className="flex items-center justify-between gap-2">
        <span className="min-w-0 flex-1 truncate text-[13px] font-semibold text-accent">
          Khám phá vận mệnh
        </span>
        <div className="flex flex-none items-center gap-2">
          <Pill
            variant="ghost"
            className="px-4 py-2 text-[13px]"
            onClick={() => setHistoryOpen(true)}
          >
            Lịch sử
          </Pill>
          <Pill
            variant="ghost"
            className="px-4 py-2 text-[13px]"
            disabled={createDisabled || createSession.isPending}
            onClick={() => void handleCreateNew()}
          >
            Tạo mới
          </Pill>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        {list.isError || createSession.isError ? (
          <div className="flex items-center gap-3">
            <p className="text-[13.5px] text-muted">
              {createSession.isError
                ? "Không tạo được cuộc trò chuyện."
                : "Không tải được cuộc trò chuyện."}
            </p>
            <Pill
              variant="ghost"
              className="px-4 py-2 text-[13px]"
              onClick={() => {
                if (createSession.isError) {
                  autoCreatedFor.current = null;
                  createSession.mutate();
                } else {
                  void list.refetch();
                }
              }}
            >
              Thử lại
            </Pill>
          </div>
        ) : activeSessionId === null ? (
          <p className="text-[13.5px] text-muted">Đang chuẩn bị cuộc trò chuyện…</p>
        ) : null}

        {showGreeting ? (
          <ChatBubble role="assistant" status="confirmed" content={GREETING} />
        ) : null}

        {transcript.map((message) => (
          <ChatBubble
            key={message.id}
            role={message.role}
            status={message.role === "assistant" ? (message.status as BubbleStatus) : "confirmed"}
            content={message.content}
          />
        ))}

        {renderedDraft !== null && !draftReconciled ? (
          <>
            <ChatBubble role="user" status="confirmed" content={renderedDraft.userContent} />
            {renderedDraft.terminal === "streaming" || renderedDraft.assistantText !== "" ? (
              <ChatBubble
                role="assistant"
                status={renderedDraft.terminal}
                content={renderedDraft.assistantText}
                activity={renderedDraft.activity}
              />
            ) : null}
          </>
        ) : null}
      </div>

      {!isAtBottom ? (
        <button
          type="button"
          aria-label="Cuộn xuống dưới"
          onClick={scrollToBottom}
          className="fixed bottom-[calc(var(--tabbar-h)+104px)] left-1/2 z-34 grid h-9 w-9 -translate-x-1/2 cursor-pointer place-items-center rounded-full border-0 bg-[linear-gradient(135deg,var(--accent-2),var(--accent))] shadow-[0_4px_12px_var(--accent-glow)] lg:left-[calc(var(--rail)+(100vw-var(--rail))/2)]"
        >
          <svg
            viewBox="0 0 24 24"
            className="h-5 w-5 fill-none [stroke:var(--color-bg-0)] [stroke-width:2]"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </button>
      ) : null}

      <Composer
        disabled={activeSessionId === null || streaming}
        onSend={(content) => void send(content)}
      />

      <SessionHistory
        open={historyOpen}
        onOpenChange={setHistoryOpen}
        sessions={sessions}
        activeSessionId={activeSessionId}
        creating={createSession.isPending}
        createDisabled={createDisabled}
        onSelect={handleSelect}
        onCreateNew={() => void handleCreateNew()}
      />
    </div>
  );
}
