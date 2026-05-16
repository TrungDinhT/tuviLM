"use client";

import { Eyebrow } from "./Eyebrow";
import { Btn } from "./Buttons";
import { MOCK_DAIVAN, MOCK_TIEUVAN } from "../_data/mock-daivan";

interface DaiVanModalProps {
  onClose: () => void;
}

export function DaiVanModal({ onClose }: DaiVanModalProps) {
  const daiVan = MOCK_DAIVAN;
  const tieuVan = MOCK_TIEUVAN;
  return (
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-[rgba(244,237,224,0.55)] anim-fade-in"
        style={{ backdropFilter: "blur(2px)" }}
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="daivan-title"
        className="absolute top-24 left-1/2 w-[1180px] max-w-[calc(100vw-48px)] bg-[rgba(255,252,245,0.99)] border-[1.5px] border-[var(--color-ink)] anim-scale-up"
        style={{ boxShadow: "0 24px 80px rgba(26,22,17,0.25)" }}
      >
        {/* Header */}
        <div className="px-8 py-6 border-b border-[rgba(26,22,17,0.14)] flex justify-between items-center">
          <div>
            <Eyebrow>Chọn năm xem · đại vận · tiểu vận</Eyebrow>
            <h2 id="daivan-title" className="font-serif text-[32px] font-medium mt-1 tracking-[-0.3px]">
              Đường đời con — <em className="italic text-[var(--color-crimson)]">10 đại vận</em>
            </h2>
            <div className="text-[13px] text-[var(--color-ink-3)] mt-1">
              Mỗi đại vận = 10 năm. Click để xem lá số tại đại vận đó.
            </div>
          </div>
          <Btn variant="ghost" className="text-[18px]" onClick={onClose} aria-label="Đóng">✕</Btn>
        </div>

        {/* Timeline */}
        <div className="px-12 pt-8 pb-5">
          <div className="relative h-[60px]">
            <div className="absolute top-[18px] left-0 right-0 h-px bg-[var(--color-ink-3)]" />
            <div className="absolute top-[18px] left-0 w-[22%] h-px bg-[var(--color-ink)]" />
            {daiVan.map((d, i) => (
              <div
                key={`tl-${d.range}`}
                className="absolute top-0 flex flex-col items-center cursor-pointer"
                style={{ left: `${(i / (daiVan.length - 1)) * 100}%`, transform: "translateX(-50%)" }}
              >
                <div className="text-[10px] text-[var(--color-ink-3)] mb-1 tracking-[0.4px]">{d.range}</div>
                <div
                  className="rounded-full border-[1.5px] border-[var(--color-ink)]"
                  style={{
                    width: d.current ? 22 : 14,
                    height: d.current ? 22 : 14,
                    background: d.current ? "var(--color-crimson)" : d.past ? "var(--color-ink)" : "var(--color-paper)",
                    boxShadow: d.current ? "0 0 0 6px rgba(139,42,31,0.15)" : "none",
                  }}
                />
                <div className={`font-serif italic text-[12px] mt-1.5 ${d.current ? "text-[var(--color-crimson)]" : "text-[var(--color-ink-3)]"}`}>{d.tenCan}</div>
              </div>
            ))}
          </div>
        </div>

        <hr className="border-t border-[rgba(26,22,17,0.14)] mx-8" />

        {/* Cards grid */}
        <div className="px-8 py-5 grid grid-cols-3 gap-3 max-h-[360px] overflow-auto">
          {daiVan.map((d) => (
            <div
              key={`card-${d.range}`}
              className="relative p-4 cursor-pointer transition-all"
              style={{
                border: d.current ? "1.5px solid var(--color-crimson)" : "1px solid rgba(26,22,17,0.14)",
                background: d.current ? "rgba(139,42,31,0.06)" : d.past ? "rgba(0,0,0,0.02)" : "rgba(255,252,245,0.6)",
                opacity: d.past ? 0.7 : 1,
              }}
            >
              {d.current && (
                <div className="absolute top-3 right-3 text-[9px] text-[var(--color-crimson)] font-bold tracking-[1px] uppercase">
                  ● đang xem
                </div>
              )}
              <div className="flex justify-between items-baseline">
                <div className={`font-serif text-[24px] font-semibold leading-none ${d.current ? "text-[var(--color-crimson)]" : "text-[var(--color-ink)]"}`}>
                  {d.range}
                </div>
                <div className="text-[11px] text-[var(--color-ink-3)]">tuổi</div>
              </div>
              <div className="font-serif italic text-[14px] text-[var(--color-ink-3)] mt-0.5">{d.tenCan}</div>
              <div className="text-[11px] text-[var(--color-ink-3)] uppercase tracking-[1px] mt-2 font-medium">{d.theme}</div>
              <div className="text-[13px] text-[var(--color-ink-2)] mt-1 leading-[1.45]">{d.main}</div>
            </div>
          ))}
        </div>

        {/* Tiểu vận row */}
        <div className="px-8 py-5 border-t border-[rgba(26,22,17,0.14)]" style={{ background: "var(--color-paper-2)" }}>
          <div className="flex items-baseline justify-between mb-2.5">
            <div>
              <Eyebrow style={{ fontSize: 10 }}>Trong đại vận 24–33, chọn năm cụ thể</Eyebrow>
              <div className="font-serif text-[18px] mt-0.5">Tiểu vận · 10 năm</div>
            </div>
            <span className="text-[11px] text-[var(--color-ink-3)]">← cuộn ngang →</span>
          </div>
          <div className="flex gap-1.5">
            {tieuVan.map((t) => (
              <div
                key={`tv-${t.y}`}
                className="flex-1 py-2 px-2 text-center cursor-pointer"
                style={{
                  border: t.current ? "1.5px solid var(--color-crimson)" : "1px solid rgba(26,22,17,0.14)",
                  background: t.current ? "var(--color-crimson)" : t.past ? "transparent" : "rgba(255,252,245,0.6)",
                  color: t.current ? "#f9efe0" : "var(--color-ink)",
                  opacity: t.past ? 0.45 : 1,
                }}
              >
                <div className="text-[14px] font-semibold">{t.y}</div>
                <div className={`font-serif italic text-[11px] mt-px ${t.current ? "text-[rgba(249,239,224,0.85)]" : "text-[var(--color-ink-3)]"}`}>{t.can}</div>
              </div>
            ))}
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <Btn variant="ghost" onClick={onClose}>Huỷ</Btn>
            <Btn variant="primary" onClick={onClose}>Xem lá số Bính Ngọ 2026</Btn>
          </div>
        </div>
      </div>
    </div>
  );
}
