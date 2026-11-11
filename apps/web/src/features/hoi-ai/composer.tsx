"use client";

import { useState } from "react";

import { cn } from "@/lib/utils";

import styles from "./composer.module.css";

/**
 * The chat input, fixed to the bottom edge of the viewport like the design:
 * a frosted footer sitting just above the tab bar, with a gradient fade that
 * blends the top edge into the scrolling chat. Enter sends.
 */
export function Composer({
  disabled,
  onSend,
}: {
  disabled: boolean;
  onSend: (content: string) => void;
}) {
  const [value, setValue] = useState("");

  const submit = () => {
    if (disabled || value.trim() === "") return;
    onSend(value);
    setValue("");
  };

  return (
    <div
      className={cn(
        "fixed bottom-[var(--tabbar-h)] left-1/2 z-34 w-full max-w-[var(--col)] -translate-x-1/2",
        "px-[18px] pt-[14px] pb-[10px]",
        "lg:bottom-0 lg:left-[calc(var(--rail)+(100vw-var(--rail))/2)] lg:w-[min(780px,calc(100vw-var(--rail)-80px))] lg:max-w-none lg:px-0 lg:pb-[18px]",
        styles.composer,
      )}
    >
      <div
        className={`${styles.inputEnter} flex items-center gap-[10px] rounded-full border border-[rgba(243,239,250,0.18)] bg-[rgba(48,29,80,0.97)] py-2 pl-[18px] pr-2 shadow-[0_8px_24px_rgba(8,4,20,0.5),inset_0_1px_0_rgba(243,239,250,0.06)]`}
      >
        <input
          type="text"
          name="chat_message_input"
          autoComplete="off"
          autoCorrect="off"
          autoCapitalize="off"
          spellCheck={false}
          enterKeyHint="send"
          data-form-type="other"
          data-lpignore="true"
          data-1p-ignore="true"
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              submit();
            }
          }}
          disabled={disabled}
          placeholder="Hỏi Thiên Hạc điều gì đó…"
          className="min-w-0 flex-1 border-0 bg-transparent text-[15px] text-ink outline-none placeholder:text-muted"
        />
        <button
          type="button"
          aria-label="Gửi"
          onClick={submit}
          disabled={disabled}
          className="grid h-[42px] w-[42px] flex-none cursor-pointer place-items-center rounded-full border-0 bg-[linear-gradient(135deg,var(--accent-2),var(--accent))] disabled:cursor-not-allowed disabled:opacity-40"
        >
          <svg
            viewBox="0 0 24 24"
            className="h-5 w-5 fill-none [stroke:var(--color-bg-0)] [stroke-width:2]"
          >
            <path d="M4 12h15M13 6l6 6-6 6" />
          </svg>
        </button>
      </div>
    </div>
  );
}
