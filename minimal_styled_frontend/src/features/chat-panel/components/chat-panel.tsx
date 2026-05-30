'use client';

import { useEffect, useRef, useState } from 'react';
import { Plus, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useChartStore } from '@/store/chart-store';
import { useChat } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
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

export function ChatPanel() {
  const lastInput = useChartStore((s) => s.lastInput);
  const setCurrent = useChartStore((s) => s.setCurrent);

  const [messages, setMessages] = useState<ChatMessage[]>([INITIAL_GREETING]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const chat = useChat();

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const sendMessage = (text: string) => {
    const message = text.trim();
    if (!message || chat.isPending) return;

    // Optimistic: user bubble + pending AI bubble.
    setMessages((prev) => [
      ...prev,
      { role: 'user', text: message, status: 'ok' },
      { role: 'ai', text: '', status: 'pending' },
    ]);
    setInput('');

    chat.mutate(
      {
        message,
        lastInput,
        applyBuildResponse: (resp) => {
          if (lastInput) setCurrent(lastInput, resp);
        },
      },
      {
        onSuccess: (resp) =>
          setMessages((prev) => patchLastMessage(prev, { role: 'ai', text: resp.answer, status: 'ok' })),
        onError: (err) => {
          const text = isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.';
          setMessages((prev) => patchLastMessage(prev, { role: 'ai', text, status: 'error' }));
        },
      },
    );
  };

  const showQuickPrompts = messages.length === 1;

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
              isResyncing={chat.isResyncing && m.status === 'pending'}
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
                disabled={chat.isPending}
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
            disabled={chat.isPending}
            onChange={(e) => setInput(e.target.value)}
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
            disabled={chat.isPending || !input.trim()}
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
