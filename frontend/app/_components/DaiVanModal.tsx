"use client";

interface DaiVanModalProps {
  onClose: () => void;
}

export function DaiVanModal({ onClose }: DaiVanModalProps) {
  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 bg-[rgba(26,22,17,0.35)] grid place-items-center"
    >
      <div className="bg-[var(--color-paper)] border border-[var(--color-ink)] px-8 py-6 font-serif italic">
        Đại vận picker — sắp ra mắt (Task 9)
      </div>
    </div>
  );
}
