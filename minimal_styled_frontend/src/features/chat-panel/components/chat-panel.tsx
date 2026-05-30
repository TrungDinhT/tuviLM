'use client';

import { useEffect, useRef, useState } from 'react';
import { Plus, Send, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { cn } from '@/lib/utils';
import { useChartStore } from '@/store/chart-store';
import { useChat } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import type { BuildLasoResponse } from '@/lib/api/schemas';
import { INITIAL_GREETING, QUICK_PROMPTS, type ChatMessage } from '../data';

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

    const applyBuildResponse = (resp: BuildLasoResponse) => {
      if (lastInput) setCurrent(lastInput, resp);
    };

    chat.mutate(
      { message, lastInput, applyBuildResponse },
      {
        onSuccess: (resp) => {
          setMessages((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last && last.status === 'pending') {
              next[next.length - 1] = { role: 'ai', text: resp.answer, status: 'ok' };
            }
            return next;
          });
        },
        onError: (err) => {
          const text = isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.';
          setMessages((prev) => {
            const next = [...prev];
            const last = next[next.length - 1];
            if (last && last.status === 'pending') {
              next[next.length - 1] = { role: 'ai', text, status: 'error' };
            }
            return next;
          });
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
            <Bubble key={i} message={m} isResyncing={chat.isResyncing && m.status === 'pending'} />
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

function Bubble({ message, isResyncing }: { message: ChatMessage; isResyncing: boolean }) {
  const isAi = message.role === 'ai';
  const isPending = message.status === 'pending';
  const isError = message.status === 'error';
  return (
    <div
      className={cn(
        'flex max-w-[90%] gap-2',
        isAi ? 'items-start self-start' : 'items-start self-end justify-end',
      )}
    >
      {isAi && (
        <Avatar className="mt-0.5 size-7">
          <AvatarFallback className="bg-foreground text-background">
            <Sparkles className="size-3" />
          </AvatarFallback>
        </Avatar>
      )}
      <div
        className={cn(
          'rounded-xl px-3 py-2 text-sm leading-relaxed',
          isAi
            ? isError
              ? 'bg-destructive/10 text-destructive whitespace-pre-line'
              : 'bg-muted text-foreground'
            : 'bg-primary text-primary-foreground whitespace-pre-line',
        )}
      >
        {isPending ? (
          <div className="flex flex-col gap-1">
            <Spinner className="size-4" />
            {isResyncing && (
              <span className="text-xs text-muted-foreground">
                (đang đồng bộ lại lá số…)
              </span>
            )}
          </div>
        ) : isAi ? (
          <div className="prose prose-sm prose-neutral max-w-none prose-headings:font-semibold prose-headings:mt-3 prose-headings:mb-1 prose-p:my-2 first:prose-p:mt-0 last:prose-p:mb-0 prose-ul:my-2 prose-ol:my-2 prose-li:my-0.5 prose-pre:my-2 prose-pre:bg-background prose-pre:text-foreground prose-pre:rounded-md prose-pre:p-3 prose-code:before:hidden prose-code:after:hidden prose-code:bg-background prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:font-normal prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-hr:my-3">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
          </div>
        ) : (
          message.text
        )}
      </div>
    </div>
  );
}
