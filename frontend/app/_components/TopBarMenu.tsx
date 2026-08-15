"use client";

import { useState, useEffect, useRef } from "react";
import { Btn } from "./Buttons";

interface TopBarMenuProps {
  onOpenLichSu: () => void;
  onOpenStrengthWeakness: () => void;
}

export function TopBarMenu({ onOpenLichSu, onOpenStrengthWeakness }: TopBarMenuProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function onClick(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <>
      <div className="hidden md:flex items-center gap-2">
        <Btn variant="crimson" onClick={onOpenStrengthWeakness}>✦ Điểm mạnh · yếu</Btn>
        <Btn variant="ghost" onClick={onOpenLichSu}>Lịch sử</Btn>
        <Btn variant="ghost">↗ chia sẻ</Btn>
        <Btn>⬇ tải lá số</Btn>
      </div>

      <div ref={ref} className="md:hidden relative">
        <Btn
          variant="ghost"
          onClick={() => setOpen((v) => !v)}
          className="text-[18px] px-3"
          aria-expanded={open}
          aria-haspopup="true"
          aria-label="Menu"
        >
          ≡
        </Btn>
        {open && (
          <div
            className="absolute right-0 top-full mt-1 z-40 bg-[var(--color-paper)] border border-[var(--color-ink)] min-w-[180px] flex flex-col"
            style={{ boxShadow: "0 8px 24px rgba(26,22,17,0.18)" }}
          >
            <Btn variant="ghost" className="justify-start rounded-none" onClick={() => { setOpen(false); onOpenStrengthWeakness(); }}>✦ Điểm mạnh · yếu</Btn>
            <Btn variant="ghost" className="justify-start rounded-none" onClick={() => { setOpen(false); onOpenLichSu(); }}>Lịch sử</Btn>
            <Btn variant="ghost" className="justify-start rounded-none">Chia sẻ</Btn>
            <Btn variant="ghost" className="justify-start rounded-none">Tải lá số</Btn>
          </div>
        )}
      </div>
    </>
  );
}
