"use client";

import { useState, type CSSProperties } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import type { ChatMessage as Msg, ChatToolEntry } from "../_lib/types";

interface ChatMessageProps {
  msg: Msg;
  onRefClick: (kind: "ref" | "sao", value: string) => void;
}

export function ChatMessage({ msg, onRefClick }: ChatMessageProps) {
  if (msg.sender === "user") {
    return (
      <div
        className="self-end px-4 py-2.5 max-w-[88%] text-[12px] sm:text-[13px] md:text-[14px] lg:text-[15px] xl:text-[16px] text-[var(--color-ink)] border border-[rgba(26,22,17,0.14)]"
        style={{ background: "var(--color-paper-2)", borderRadius: "14px 14px 4px 14px" }}
      >
        {msg.body}
      </div>
    );
  }

  const hasBody = msg.body.trim().length > 0;
  const showThinking = msg.status === "streaming" && !hasBody;

  return (
    <div className="self-start max-w-[88%] font-serif text-[14px] sm:text-[15px] md:text-[16px] lg:text-[17px] xl:text-[18px] text-[var(--color-ink)] leading-[1.5]">
      <span className="font-serif italic block mb-1 text-[14px] sm:text-[15px] md:text-[16px] lg:text-[17px] xl:text-[18px] tracking-[0.5px] uppercase font-medium text-[var(--color-crimson)]">
        Thầy Tuệ
      </span>
      {(msg.toolCalls?.length ?? 0) > 0 && (
        <ToolCallList tools={msg.toolCalls ?? []} />
      )}
      {hasBody && <MarkdownBody body={msg.body} onRefClick={onRefClick} />}
      {showThinking && <ThinkingDots />}
    </div>
  );
}

function preprocessTokens(body: string): string {
  return body.replace(
    /\[\[(ref|sao):([^\]]+)\]\]/g,
    (_match, kind: string, value: string) =>
      `[${value}](tuvi://${kind}/${encodeURIComponent(value)})`,
  );
}

function MarkdownBody({
  body,
  onRefClick,
}: {
  body: string;
  onRefClick: (kind: "ref" | "sao", value: string) => void;
}) {
  const source = preprocessTokens(body);
  const components: Components = {
    a: ({ href, children }) => {
      if (href && href.startsWith("tuvi://")) {
        const m = /^tuvi:\/\/(ref|sao)\/(.+)$/.exec(href);
        if (m) {
          const kind = m[1] as "ref" | "sao";
          const value = decodeURIComponent(m[2]);
          return (
            <button
              type="button"
              onClick={() => onRefClick(kind, value)}
              className={kind === "ref" ? "ref" : "ref-sao"}
              style={{
                background: "transparent",
                border: 0,
                padding: 0,
                font: "inherit",
                cursor: "pointer",
              }}
            >
              {children}
            </button>
          );
        }
      }
      return (
        <a href={href} target="_blank" rel="noopener noreferrer">
          {children}
        </a>
      );
    },
    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
    ul: ({ children }) => (
      <ul className="list-disc pl-5 mb-2 space-y-0.5">{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className="list-decimal pl-5 mb-2 space-y-0.5">{children}</ol>
    ),
    h1: ({ children }) => (
      <h1 className="font-serif text-[1.15em] font-medium mt-3 mb-1.5 text-[var(--color-crimson)]">
        {children}
      </h1>
    ),
    h2: ({ children }) => (
      <h2 className="font-serif text-[1.1em] font-medium mt-3 mb-1.5 text-[var(--color-crimson)]">
        {children}
      </h2>
    ),
    h3: ({ children }) => (
      <h3 className="font-serif text-[1.05em] font-medium mt-2.5 mb-1 text-[var(--color-crimson)]">
        {children}
      </h3>
    ),
    code: ({ children }) => (
      <code className="px-1 py-0.5 rounded bg-[rgba(26,22,17,0.06)] text-[0.92em]">
        {children}
      </code>
    ),
    pre: ({ children }) => (
      <pre className="p-2 rounded bg-[rgba(26,22,17,0.06)] overflow-x-auto text-[0.85em] mb-2">
        {children}
      </pre>
    ),
    blockquote: ({ children }) => (
      <blockquote className="border-l-2 border-[var(--color-crimson)] pl-3 italic text-[var(--color-ink-2)] my-2">
        {children}
      </blockquote>
    ),
    strong: ({ children }) => <strong className="font-medium">{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
    table: ({ children }) => (
      <div className="overflow-x-auto my-2">
        <table className="border-collapse text-[0.92em]">{children}</table>
      </div>
    ),
    th: ({ children }) => (
      <th className="border border-[rgba(26,22,17,0.18)] px-2 py-1 text-left bg-[rgba(26,22,17,0.04)]">
        {children}
      </th>
    ),
    td: ({ children }) => (
      <td className="border border-[rgba(26,22,17,0.14)] px-2 py-1">{children}</td>
    ),
  };
  return (
    <div className="markdown-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {source}
      </ReactMarkdown>
    </div>
  );
}

function ToolCallList({ tools }: { tools: ChatToolEntry[] }) {
  return (
    <div className="flex flex-col gap-1 mb-2">
      {tools.map((t) => (
        <ToolCallChip key={t.id} tool={t} />
      ))}
    </div>
  );
}

function ToolCallChip({ tool }: { tool: ChatToolEntry }) {
  const [open, setOpen] = useState(false);
  const running = tool.result === undefined;
  return (
    <div
      className="border border-[rgba(26,22,17,0.14)] rounded px-2 py-1 text-[12px] font-sans"
      style={{ background: "rgba(255,252,245,0.6)" }}
    >
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 w-full text-left bg-transparent border-0 p-0 cursor-pointer"
      >
        <span
          style={running ? runningDot : doneDot}
          className={running ? "anim-pulse-dot" : ""}
        />
        <span className="font-medium text-[var(--color-ink-2)]">{tool.name}</span>
        <span className="text-[var(--color-ink-3)] italic">
          {running ? "đang chạy…" : "xong"}
        </span>
        <span className="ml-auto text-[var(--color-ink-3)] text-[10px]">
          {open ? "▾" : "▸"}
        </span>
      </button>
      {open && (
        <div className="mt-1.5 space-y-1.5">
          <div>
            <div className="text-[10px] uppercase tracking-wider text-[var(--color-ink-3)] mb-0.5">
              Tham số
            </div>
            <pre className="text-[11px] leading-snug whitespace-pre-wrap break-words bg-[rgba(26,22,17,0.05)] p-1.5 rounded max-h-[160px] overflow-auto">
              {formatJson(tool.arguments)}
            </pre>
          </div>
          {!running && (
            <div>
              <div className="text-[10px] uppercase tracking-wider text-[var(--color-ink-3)] mb-0.5">
                Kết quả
              </div>
              <pre className="text-[11px] leading-snug whitespace-pre-wrap break-words bg-[rgba(26,22,17,0.05)] p-1.5 rounded max-h-[240px] overflow-auto">
                {formatJson(tool.result)}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function formatJson(v: unknown): string {
  if (v === undefined) return "";
  if (typeof v === "string") return v;
  try {
    return JSON.stringify(v, null, 2);
  } catch {
    return String(v);
  }
}

function ThinkingDots() {
  return (
    <div className="flex items-center gap-1 mt-1" aria-label="Thầy đang suy">
      <span className="anim-bounce-dot" style={dotStyle(0)} />
      <span className="anim-bounce-dot" style={dotStyle(160)} />
      <span className="anim-bounce-dot" style={dotStyle(320)} />
    </div>
  );
}

function dotStyle(delay: number): CSSProperties {
  return {
    display: "inline-block",
    width: 6,
    height: 6,
    borderRadius: "50%",
    background: "var(--color-crimson)",
    animationDelay: `${delay}ms`,
  };
}

const runningDot: CSSProperties = {
  display: "inline-block",
  width: 6,
  height: 6,
  borderRadius: "50%",
  background: "var(--color-crimson)",
};

const doneDot: CSSProperties = {
  display: "inline-block",
  width: 6,
  height: 6,
  borderRadius: "50%",
  background: "rgba(26,22,17,0.32)",
};
