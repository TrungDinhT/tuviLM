"use client";

import { useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";

import { Pill } from "@/components/primitives/pill";
import { useCreateSession, useGetSession, useListSessions } from "@/lib/api/hooks";
import { queryKeys } from "@/lib/api/queryKeys";
import type { ChatMessage } from "@/lib/api/schemas";
import { isRunTerminal } from "@/lib/api/runs";
import { useWorkflowRun } from "@/hooks/use-workflow-run";
import { describe, isApiError } from "@/lib/http/errors";
import { showToast } from "@/lib/toast";
import { useChartStore } from "@/store/chart-store";

import { ChatBubble, type BubbleStatus } from "./chat-bubble";
import { Composer } from "./composer";
import styles from "./hoi-ai-screen.module.css";
import { SessionHistory } from "./session-history";
import { toolStatusLabel } from "./tool-status";
import { useStickToBottom } from "./use-stick-to-bottom";

const GREETING =
  "Chào bạn, tôi là Thiên Hạc — tinh linh dẫn đường. Bạn muốn hỏi điều gì về lá số của mình?";

export function HoiAiScreen() {
  const hasChart = useChartStore((state) => state.hasChart);
  const chartProfileId = useChartStore((state) => state.chartProfileId);
  const queryClient = useQueryClient();

  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [historyOpen, setHistoryOpen] = useState(false);
  const autoCreatedFor = useRef<string | null>(null);
  const creatingSessionRef = useRef(false);

  const list = useListSessions(chartProfileId);
  const createSession = useCreateSession(chartProfileId);

  const sessions = useMemo(
    () => [...(list.data?.sessions ?? [])].sort((a, b) => b.updated_at.localeCompare(a.updated_at)),
    [list.data],
  );
  const activeSessionId = selectedId ?? sessions[0]?.id ?? null;

  const session = useGetSession(activeSessionId);

  const workflow = useWorkflowRun({
    workflow: "chat",
    resourceId: activeSessionId ? `session:${activeSessionId}` : null,
  });
  const run = workflow.run;
  const sessionMessages = session.data?.session.messages ?? [];
  const transcript: ChatMessage[] = sessionMessages.filter(
    (message) => message.status !== "pending",
  );
  const content = workflow.inputs?.content;
  const renderedDraft =
    typeof content === "string"
      ? {
          userContent: content,
          userMessageId: run?.state.metadata.user_message_id,
          assistantMessageId: run?.state.metadata.assistant_message_id,
          assistantText: run?.state.text ?? "",
          terminal:
            !run && workflow.error
              ? ("failed" as const)
              : run?.status === "succeeded"
                ? ("confirmed" as const)
                : run?.status === "failed" || run?.status === "cancelled"
                  ? run.status
                  : ("streaming" as const),
          activity: run?.state.progress ? toolStatusLabel(run.state.progress) : null,
        }
      : null;
  const refreshedRun = useRef<string | null>(null);
  useEffect(() => {
    if (!run || !isRunTerminal(run) || refreshedRun.current === run.id) return;
    refreshedRun.current = run.id;
    const sessionId = run.inputs.session_id;
    if (typeof sessionId === "string") {
      void queryClient.invalidateQueries({ queryKey: queryKeys.sessions.detail(sessionId) });
    }
    if (chartProfileId) {
      void queryClient.invalidateQueries({
        queryKey: queryKeys.sessions.byProfile(chartProfileId),
      });
    }
  }, [run, chartProfileId, queryClient]);

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
      <div className={`${styles.enterTranscript} flex flex-col items-start gap-4 py-10`}>
        <p className="max-w-[46ch] text-[13.5px] leading-relaxed text-muted">
          Lá số của bạn chưa được lưu để trò chuyện. Hãy an sao lại để Thiên Hạc có thể dẫn đường
          cho bạn.
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
    transcript.length === 0 &&
    renderedDraft === null &&
    !session.isPending &&
    activeSessionId !== null;

  const streaming = workflow.active || workflow.loading;

  // A fresh conversation (only the greeting, no real message) offers nothing to
  // fork from, so "Tạo mới" is disabled until the active session has a message.
  const createDisabled = activeSessionId === null || transcript.length === 0;

  const send = (content: string) => {
    if (!activeSessionId || streaming || !content.trim()) return;
    workflow.start({ session_id: activeSessionId, content: content.trim() });
    scrollToBottom();
  };

  const handleSelect = (id: string) => {
    setSelectedId(id);
    setHistoryOpen(false);
  };

  const handleCreateNew = async () => {
    if (chartProfileId === null || creatingSessionRef.current) return;
    creatingSessionRef.current = true;
    try {
      const result = await createSession.mutateAsync();
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
      <div className={`${styles.enterToolbar} flex items-center justify-between gap-2`}>
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

      <div className={`${styles.enterTranscript} flex flex-col gap-3`}>
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
            {!transcript.some((message) => message.id === renderedDraft.userMessageId) ? (
              <ChatBubble role="user" status="confirmed" content={renderedDraft.userContent} />
            ) : null}
            <ChatBubble
              role="assistant"
              status={renderedDraft.terminal}
              content={renderedDraft.assistantText}
              activity={renderedDraft.activity}
            />
          </>
        ) : null}
        {workflow.error ? (
          <div className="flex items-center gap-3">
            <p role="alert" className="text-[13px] text-muted">
              {isApiError(workflow.error)
                ? describe(workflow.error.error)
                : "Không tải được tiến trình. Bạn thử kết nối lại nhé."}
            </p>
            <Pill variant="ghost" onClick={workflow.retry}>
              Kết nối lại
            </Pill>
          </div>
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

      {workflow.active && run ? (
        <Pill
          variant="ghost"
          disabled={run.cancel_requested}
          onClick={() => void workflow.cancel()}
        >
          {run.cancel_requested ? "Đang dừng…" : "Dừng trả lời"}
        </Pill>
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
