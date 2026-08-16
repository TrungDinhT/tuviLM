"use client";

import { usePathname } from "next/navigation";

import { screenFor } from "@/config/site";

/**
 * Desktop-only top bar.
 *
 * Below `lg` each screen carries its own sticky header instead, and there is
 * no room for this. The band spans the full working area while its text is
 * locked to the `--shell` column, matching the content beneath it.
 *
 * Its outer height is pinned to `--topbar-h`, border included (`border-box`).
 * Everything sticky below offsets by that same variable, so the two only meet
 * flush if this element is exactly that tall. A `min-height` plus padding lets
 * font metrics push it a couple of pixels taller, and those pixels show up as
 * the sticky header jumping the moment it pins.
 */
export function TopBar() {
  const pathname = usePathname();
  const screen = screenFor(pathname);
  if (screen === null) return null;

  return (
    <header className="topbar-surface sticky top-0 z-30 hidden h-[var(--topbar-h)] lg:block">
      <div className="mx-auto flex h-full w-full max-w-[var(--shell)] items-center gap-[18px] px-10">
        <div>
          <div className="text-[10px] font-bold tracking-[0.24em] text-muted uppercase">
            {screen.group}
          </div>
          <h1 className="mt-[3px] text-[22px] leading-tight font-semibold">{screen.title}</h1>
        </div>
      </div>
    </header>
  );
}
