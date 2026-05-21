'use client';

import { useEffect, useRef, useState } from 'react';
import { Send, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';
import { useChartStore } from '@/store/chart-store';
import { DEMO_CHAT, PLACEHOLDER_REPLY, QUICK_PROMPTS, type ChatMessage } from '../data';

export function ChatPanel() {
  const selected = useChartStore((s) => s.selectedCungPosition);
  const current = useChartStore((s) => s.current);
  const selectedRole = selected && current ? current.cung_by_position[selected]?.role : null;

  const [messages, setMessages] = useState<ChatMessage[]>(DEMO_CHAT);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (el) el.scrollTop = el.scrollHeight;
  }, [messages]);

  const send = () => {
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [
      ...prev,
      { role: 'user', text },
      { role: 'ai', text: PLACEHOLDER_REPLY },
    ]);
    setInput('');
  };

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
        <div className="flex items-center gap-1.5">
          {selected && (
            <Badge variant="secondary">
              {selected}
              {selectedRole && ` · ${selectedRole}`}
            </Badge>
          )}
          <Badge variant="outline">
            <Sparkles className="size-3" /> Demo
          </Badge>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4 lg:px-6 lg:py-5"
      >
        {messages.map((m, i) => (
          <Bubble key={i} {...m} />
        ))}
      </div>

      <div className="border-t border-border bg-background px-4 py-3 lg:px-6">
        <div className="mb-2 flex flex-wrap gap-1.5">
          {QUICK_PROMPTS.map((p) => (
            <Button key={p} type="button" variant="outline" size="sm" onClick={() => setInput(p)}>
              {p}
            </Button>
          ))}
        </div>
        <div className="flex items-end gap-2">
          <Textarea
            placeholder="Hỏi thầy điều gì..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                send();
              }
            }}
            className="max-h-40 min-h-10 py-2"
          />
          <Button size="icon" type="button" onClick={send} aria-label="Gửi">
            <Send className="size-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function Bubble({ role, text }: ChatMessage) {
  const isAi = role === 'ai';
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
          'rounded-xl px-3 py-2 text-sm leading-relaxed whitespace-pre-line',
          isAi ? 'bg-muted text-foreground' : 'bg-primary text-primary-foreground',
        )}
      >
        {isAi ? (
          <ReactMarkdown components={{ p: (p) => <span>{p.children}</span> }}>
            {text}
          </ReactMarkdown>
        ) : (
          text
        )}
      </div>
    </div>
  );
}
