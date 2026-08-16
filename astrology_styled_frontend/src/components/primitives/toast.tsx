"use client";

import { useEffect } from "react";

import { useToastStore } from "@/store/toast-store";

const VISIBLE_MS = 2200;

/**
 * The single transient message slot.
 *
 * Positioned above `--tabbar-h`, which is `0px` at the desktop tier. The
 * offset is `max(--tabbar-h, --safe-b)` rather than a sum: `--tabbar-h`
 * already folds in `--safe-b`, so adding both would double-count the inset,
 * while taking the larger still clears a home indicator on a desktop-width
 * touch device where the tab bar is gone.
 *
 * `role="status"` with `aria-live="polite"` so a screen reader announces the
 * message without stealing focus.
 */
export function Toast() {
  const message = useToastStore((state) => state.message);
  const dismiss = useToastStore((state) => state.dismiss);

  useEffect(() => {
    if (message === null) return;
    const timer = setTimeout(dismiss, VISIBLE_MS);
    return () => clearTimeout(timer);
  }, [message, dismiss]);

  return (
    <div
      role="status"
      aria-live="polite"
      className={[
        "toast-surface pointer-events-none fixed left-1/2 z-60",
        "bottom-[calc(22px+max(var(--tabbar-h),var(--safe-b)))] lg:left-[calc(50%+var(--rail)/2)]",
        "rounded-full px-5 py-3 text-[13.5px] font-medium whitespace-nowrap text-ink",
        "transition-[opacity,transform] duration-300",
        message === null
          ? "-translate-x-1/2 translate-y-5 opacity-0"
          : "-translate-x-1/2 translate-y-0 opacity-100",
      ].join(" ")}
    >
      {message}
    </div>
  );
}
