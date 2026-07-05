'use client';

import { useEffect, useRef, useState } from 'react';
import { Plus, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useChartStore } from '@/store/chart-store';
import { useChat, useSession } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import type { PersistedChatMessage } from '@/lib/api/schemas';
import { INITIAL_GREETING, QUICK_PROMPTS, type ChatMessage } from '../data';
import { MessageBubble } from './message-bubble';

function patchLastMessage(prev: ChatMessage[], update: Partial<ChatMessage>): ChatMessage[] {
  const next = [...prev];
  const last = next[next.length - 1];
  if (last && last.status === 'pending') {
    next[next.length - 1] = { ...last, ...update };
  }
  return next;
}

function fromPersistedMessages(messages: PersistedChatMessage[]): ChatMessage[] {
  if (messages.length === 0) return [INITIAL_GREETING];
  return messages.map((message) => ({
    role: message.role === 'assistant' ? 'ai' : 'user',
    text: message.content,
    status:
      message.status === 'confirmed'
        ? 'ok'
        : message.status === 'pending'
          ? 'pending'
          : 'error',
  }));
}

export function ChatPanel() {
  const ownerId = useChartStore((s) => s.ownerId);
  const chartProfileId = useChartStore((s) => s.chartProfileId);
  const sessionId = useChartStore((s) => s.sessionId);

  const [localMessages, setLocalMessages] = useState<{
    sessionId: string | null;
    messages: ChatMessage[];
  } | null>(null);
  const [draft, setDraft] = useState<{ sessionId: string | null; value: string }>({
    sessionId: null,
    value: '',
  });
  const scrollRef = useRef<HTMLDivElement>(null);
  const session = useSession(ownerId, sessionId);
  const chat = useChat();

  const hydratedMessages = session.isError
    ? [{ role: 'ai' as const, text: apiErrorMessage(session.error), status: 'error' as const }]
    : session.data
      ? fromPersistedMessages(session.data.session.messages)
      : [INITIAL_GREETING];
  const messages =
    localMessages?.sessionId === sessionId ? localMessages.messages : hydratedMessages;
  const input = draft.sessionId === sessionId ? draft.value : '';

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const sendMessage = (text: string) => {
    const message = text.trim();
    if (!message || chat.isPending || session.isPending) return;

    // Optimistic: user bubble + pending AI bubble.
    setLocalMessages({
      sessionId,
      messages: [
        ...messages,
        { role: 'user', text: message, status: 'ok' },
        { role: 'ai', text: '', status: 'pending' },
      ],
    });
    setDraft({ sessionId, value: '' });

    chat.mutate(
      {
        message,
        ownerId,
        chartProfileId,
        sessionId,
        onTextDelta: (delta) =>
          setLocalMessages((prev) => ({
            sessionId,
            messages: patchLastMessage(prev?.sessionId === sessionId ? prev.messages : messages, {
              role: 'ai',
              text: ((prev?.sessionId === sessionId ? prev.messages.at(-1)?.text : messages.at(-1)?.text) ?? '') + delta,
              status: 'pending',
            }),
          })),
      },
      {
        onSuccess: (resp) =>
          setLocalMessages((prev) => ({
            sessionId,
            messages: patchLastMessage(prev?.sessionId === sessionId ? prev.messages : messages, {
              role: 'ai',
              text: resp.answer,
              status: 'ok',
            }),
          })),
        onError: (err) => {
          const text = isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.';
          setLocalMessages((prev) => ({
            sessionId,
            messages: patchLastMessage(prev?.sessionId === sessionId ? prev.messages : messages, {
              role: 'ai',
              text,
              status: 'error',
            }),
          }));
        },
      },
    );
  };

  const isHydrating = Boolean(ownerId && sessionId) && session.isPending;
  const isBusy = chat.isPending || isHydrating;
  const showQuickPrompts = messages.length === 1 && !isHydrating;

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div
        ref={scrollRef}
        className="custom-scrollbar flex flex-1 flex-col overflow-y-auto"
      >
        <div className="mx-auto flex w-full max-w-[900px] flex-col gap-3 px-4 py-4 lg:px-6 lg:py-5">
          {messages.map((m, i) => (
            <MessageBubble
              key={i}
              message={m}
            />
          ))}
        </div>
      </div>

      <div className="mx-auto w-full max-w-[900px] px-4 py-3 lg:px-6">
        {showQuickPrompts && (
          <div className="mb-2 flex flex-wrap gap-1.5">
            {QUICK_PROMPTS.map((p) => (
              <Button
                key={p}
                type="button"
                variant="outline"
                size="sm"
                disabled={isBusy}
                onClick={() => sendMessage(p)}
              >
                {p}
              </Button>
            ))}
          </div>
        )}
        <div className="flex items-center gap-2 rounded-full border border-input bg-background px-4 py-2.5 shadow-sm">
          <Plus className="size-4 shrink-0 text-muted-foreground" />
          <input
            type="text"
            placeholder="Hỏi thầy điều gì..."
            value={input}
            disabled={isBusy}
            onChange={(e) => setDraft({ sessionId, value: e.target.value })}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage(input);
              }
            }}
            className="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground disabled:opacity-50"
          />
          <button
            type="button"
            onClick={() => sendMessage(input)}
            disabled={isBusy || !input.trim()}
            aria-label="Gửi"
            className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground disabled:opacity-50"
          >
            <Send className="size-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
