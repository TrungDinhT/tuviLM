"use client";

import { useState, type FormEvent } from "react";

interface ChatInputProps {
  onSend: (body: string) => void;
  placeholder?: string;
  disabled?: boolean;
}

export function ChatInput({ onSend, placeholder = "Con hỏi thầy điều gì đó…", disabled = false }: ChatInputProps) {
  const [val, setVal] = useState("");

  function submit(e: FormEvent) {
    e.preventDefault();
    const t = val.trim();
    if (!t || disabled) return;
    onSend(t);
    setVal("");
  }

  return (
    <form
      onSubmit={submit}
      className="flex items-center gap-3 px-4 py-3.5 border border-[rgba(26,22,17,0.32)] rounded-sm"
      style={{ background: "rgba(255,252,245,0.9)" }}
    >
      <span className="text-[var(--color-ink-3)] text-[14px]" aria-hidden="true">✎</span>
      <input
        value={val}
        onChange={(e) => setVal(e.target.value)}
        placeholder={placeholder}
        aria-label="Tin nhắn cho thầy"
        disabled={disabled}
        className="flex-1 bg-transparent outline-none font-serif italic text-[17px] text-[var(--color-ink)] placeholder:text-[var(--color-ink-3)] disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || val.trim().length === 0}
        className="w-9 h-9 grid place-items-center rounded-full bg-[var(--color-ink)] text-[var(--color-paper)] cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
        aria-label="Gửi"
      >
        →
      </button>
    </form>
  );
}
