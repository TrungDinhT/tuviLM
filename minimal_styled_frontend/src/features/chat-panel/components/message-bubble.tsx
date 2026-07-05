'use client';

import { Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Spinner } from '@/components/ui/spinner';
import { cn } from '@/lib/utils';
import type { ChatMessage } from '../data';

const MARKDOWN_CLASSES =
  'prose prose-sm prose-neutral max-w-none ' +
  'prose-headings:font-semibold prose-headings:mt-3 prose-headings:mb-1 ' +
  'prose-p:my-2 first:prose-p:mt-0 last:prose-p:mb-0 ' +
  'prose-ul:my-2 prose-ol:my-2 prose-li:my-0.5 ' +
  'prose-pre:my-2 prose-pre:bg-background prose-pre:text-foreground prose-pre:rounded-md prose-pre:p-3 ' +
  'prose-code:before:hidden prose-code:after:hidden prose-code:bg-background prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:font-normal ' +
  'prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-hr:my-3';

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
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
        {isPending && !message.text ? (
          <Spinner className="size-4" />
        ) : isAi ? (
          <div className={MARKDOWN_CLASSES}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.text}</ReactMarkdown>
          </div>
        ) : (
          message.text
        )}
      </div>
    </div>
  );
}
