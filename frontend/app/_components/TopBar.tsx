import type { ReactNode } from "react";

interface TopBarProps {
  breadcrumb?: ReactNode;
  rightActions?: ReactNode;
}

export function TopBar({ breadcrumb, rightActions }: TopBarProps) {
  return (
    <div
      className="flex items-center justify-between px-7 py-4 border-b border-[rgba(26,22,17,0.14)]"
      style={{ background: "rgba(244,237,224,0.92)", backdropFilter: "blur(6px)" }}
    >
      <div className="flex items-center gap-6">
        <div className="font-serif text-[26px] font-semibold tracking-[1px] text-[var(--color-ink)]">
          tuvi<em className="italic text-[var(--color-crimson)] ml-px">.</em>ai
        </div>
        {breadcrumb && (
          <div className="flex items-center gap-3 text-[13px] text-[var(--color-ink-3)]">
            <span className="text-[var(--color-ink-4)]">/</span>
            {breadcrumb}
          </div>
        )}
      </div>
      <div className="flex items-center gap-2">{rightActions}</div>
    </div>
  );
}
