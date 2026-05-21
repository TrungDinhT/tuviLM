'use client';

import { useEffect, useRef, useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Spinner } from '@/components/ui/spinner';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { useChartStore } from '@/store/chart-store';
import { useChat } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import type { BuildLasoResponse } from '@/lib/api/schemas';
import { INITIAL_GREETING, QUICK_PROMPTS, type ChatMessage } from '../data';

export function ChatPanel() {
  const selected = useChartStore((s) => s.selectedCungPosition);
  const current = useChartStore((s) => s.current);
  const lastInput = useChartStore((s) => s.lastInput);
  const setCurrent = useChartStore((s) => s.setCurrent);
  const selectedRole = selected && current ? current.cung_by_position[selected]?.role : null;

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
      <div className="flex items-center justify-between gap-3 border-b border-border bg-background px-4 py-3 lg:px-6 lg:py-4">
        <div className="flex items-center gap-3">
          <Avatar>
            <AvatarFallback>T</AvatarFallback>
          </Avatar>
          <div>
            <div className="text-sm font-medium">Tử Vi AI</div>
            <div className="text-xs text-muted-foreground">Phiên đọc lá số</div>
          </div>
        </div>
        {selected && (
          <Badge variant="secondary">
            {selected}
            {selectedRole && ` · ${selectedRole}`}
          </Badge>
        )}
      </div>

      <div
        ref={scrollRef}
        className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4 lg:px-6 lg:py-5"
      >
        {messages.map((m, i) => (
          <Bubble key={i} message={m} isResyncing={chat.isResyncing && m.status === 'pending'} />
        ))}
      </div>

      <div className="border-t border-border bg-background px-4 py-3 lg:px-6">
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
        <div className="flex items-end gap-2">
          <Textarea
            placeholder="Hỏi thầy điều gì..."
            value={input}
            disabled={chat.isPending}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage(input);
              }
            }}
            className="max-h-40 min-h-10 py-2"
          />
          <Button
            size="icon"
            type="button"
            onClick={() => sendMessage(input)}
            disabled={chat.isPending}
            aria-label="Gửi"
          >
            <Send className="size-4" />
          </Button>
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
          'rounded-xl px-3 py-2 text-base leading-relaxed',
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
          <div className="prose prose-base prose-neutral max-w-none prose-headings:font-semibold prose-headings:mt-3 prose-headings:mb-1 prose-p:my-2 first:prose-p:mt-0 last:prose-p:mb-0 prose-ul:my-2 prose-ol:my-2 prose-li:my-0.5 prose-pre:my-2 prose-pre:bg-background prose-pre:text-foreground prose-pre:rounded-md prose-pre:p-3 prose-code:before:hidden prose-code:after:hidden prose-code:bg-background prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:font-normal prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-hr:my-3">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
          </div>
        ) : (
          message.text
        )}
      </div>
    </div>
  );
}
