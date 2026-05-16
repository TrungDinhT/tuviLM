"use client";

interface LichSuDrawerProps {
  onClose: () => void;
}

export function LichSuDrawer({ onClose }: LichSuDrawerProps) {
  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 bg-[rgba(26,22,17,0.35)] grid place-items-start"
    >
      <div className="bg-[var(--color-paper)] border-r border-[var(--color-ink)] h-full w-[560px] max-w-[90vw] px-8 py-6 font-serif italic">
        Lịch sử drawer — sắp ra mắt (Task 9)
      </div>
    </div>
  );
}
