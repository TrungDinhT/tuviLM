"use client";

import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Markdown rendering for assistant chat text, styled to the twilight palette
 * through tokens — no raw colour literal, no external stylesheet.
 */
export function MarkdownBody({ body }: { body: string }) {
  const components: Components = {
    p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
    ul: ({ children }) => <ul className="mb-2 list-disc space-y-0.5 pl-5">{children}</ul>,
    ol: ({ children }) => <ol className="mb-2 list-decimal space-y-0.5 pl-5">{children}</ol>,
    h1: ({ children }) => (
      <h1 className="mt-3 mb-1.5 font-display text-[1.1em] font-semibold text-accent">{children}</h1>
    ),
    h2: ({ children }) => (
      <h2 className="mt-3 mb-1.5 font-display text-[1.05em] font-semibold text-accent">{children}</h2>
    ),
    h3: ({ children }) => (
      <h3 className="mt-2.5 mb-1 font-display text-[1em] font-semibold text-accent">{children}</h3>
    ),
    code: ({ children }) => (
      <code className="rounded bg-glass px-1 py-0.5 text-[0.92em]">{children}</code>
    ),
    pre: ({ children }) => (
      <pre className="mb-2 overflow-x-auto rounded-xl bg-glass p-2 text-[0.85em]">{children}</pre>
    ),
    blockquote: ({ children }) => (
      <blockquote className="my-2 border-l-2 border-accent pl-3 italic text-muted">{children}</blockquote>
    ),
    strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
    em: ({ children }) => <em className="italic">{children}</em>,
    a: ({ href, children }) => (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="underline decoration-accent underline-offset-2"
      >
        {children}
      </a>
    ),
    table: ({ children }) => (
      <div className="my-2 overflow-x-auto">
        <table className="border-collapse text-[0.92em]">{children}</table>
      </div>
    ),
    th: ({ children }) => (
      <th className="border border-glass-line bg-glass px-2 py-1 text-left">{children}</th>
    ),
    td: ({ children }) => <td className="border border-glass-line px-2 py-1">{children}</td>,
    hr: () => <hr className="my-3 border-glass-line" />,
  };

  return (
    <div className="markdown-body">
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {body}
      </ReactMarkdown>
    </div>
  );
}
