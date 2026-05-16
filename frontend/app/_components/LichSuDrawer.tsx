"use client";

import { Eyebrow } from "./Eyebrow";
import { Btn, Chip } from "./Buttons";
import { MOCK_HISTORY } from "../_data/mock-history";

interface LichSuDrawerProps {
  onClose: () => void;
}

export function LichSuDrawer({ onClose }: LichSuDrawerProps) {
  return (
    <div className="fixed inset-0 z-50">
      <div className="absolute inset-0 bg-[rgba(244,237,224,0.55)] anim-fade-in" onClick={onClose} />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="lichsu-title"
        className="absolute top-0 left-0 bottom-0 w-[560px] max-w-[90vw] bg-[rgba(255,252,245,0.99)] border-r-[1.5px] border-[var(--color-ink)] flex flex-col anim-slide-left"
        style={{ boxShadow: "24px 0 64px rgba(26,22,17,0.18)" }}
      >
        {/* Header */}
        <div className="px-8 pt-6 pb-4 border-b border-[rgba(26,22,17,0.14)]">
          <div className="flex justify-between items-start">
            <div>
              <Eyebrow>Phiên đã hỏi</Eyebrow>
              <h2 id="lichsu-title" className="font-serif text-[32px] font-medium mt-1 tracking-[-0.3px]">
                Sổ tay trò chuyện
              </h2>
              <div className="text-[12px] text-[var(--color-ink-3)] mt-1">
                {MOCK_HISTORY.reduce((acc, g) => acc + g.items.length, 0)} phiên · {MOCK_HISTORY.reduce((acc, g) => acc + g.items.reduce((s, it) => s + it.count, 0), 0)} câu thầy đã trả lời
              </div>
            </div>
            <Btn variant="ghost" className="text-[16px]" onClick={onClose} aria-label="Đóng">✕</Btn>
          </div>

          <div className="flex items-center gap-3 mt-4">
            <span className="text-[11px] text-[var(--color-ink-3)] uppercase tracking-[1px]">Lá số</span>
            <div className="px-3.5 py-1.5 border border-[rgba(26,22,17,0.32)] bg-[var(--color-paper)] font-serif text-[16px] flex items-center gap-2 cursor-pointer">
              Vũ Duy Khanh <span className="text-[var(--color-ink-3)] text-[11px]">▾</span>
            </div>
            <Btn variant="ghost" className="text-[12px]">＋ thêm lá số</Btn>
          </div>

          <div className="mt-3.5">
            <div
              className="flex-1 px-3.5 py-2 border border-[rgba(26,22,17,0.14)] flex items-center gap-2 font-serif italic text-[15px] text-[var(--color-ink-3)]"
              style={{ background: "rgba(255,252,245,0.6)" }}
            >
              <span className="text-[12px]" aria-hidden="true">🔍</span>
              <span>Tìm câu hỏi, cung, sao…</span>
            </div>
          </div>
          <div className="flex gap-1.5 mt-2.5 flex-wrap">
            <Chip variant="active" className="text-[11px]">Tất cả</Chip>
            <Chip className="text-[11px]">Sự nghiệp</Chip>
            <Chip className="text-[11px]">Tình duyên</Chip>
            <Chip className="text-[11px]">Sức khoẻ</Chip>
            <Chip className="text-[11px]">★ Đã lưu</Chip>
          </div>
        </div>

        {/* Session list */}
        <div className="flex-1 py-2 overflow-auto">
          {MOCK_HISTORY.map((s) => (
            <div key={`day-${s.date}`}>
              <div className="px-8 pt-3.5 pb-1.5 text-[10px] text-[var(--color-ink-3)] font-semibold tracking-[1.5px] uppercase flex items-baseline gap-3">
                <span>{s.date}</span>
                <span className="flex-1 h-px bg-[var(--color-paper-3)]" />
              </div>
              {s.items.map((it) => (
                <button
                  key={`it-${s.date}-${it.time}-${it.q.slice(0,16)}`}
                  type="button"
                  className="w-full text-left px-8 py-3 cursor-pointer transition-colors"
                  style={{
                    borderLeft: it.current ? "3px solid var(--color-crimson)" : "3px solid transparent",
                    background: it.current ? "rgba(139,42,31,0.06)" : "transparent",
                  }}
                >
                  <div className="flex justify-between items-baseline gap-3">
                    <div className="flex-1">
                      <div className="font-serif text-[17px] leading-[1.3] text-[var(--color-ink)]">
                        {it.starred && <span className="text-[var(--color-gold)] mr-1.5">★</span>}
                        {it.q}
                      </div>
                    </div>
                    <span className="text-[11px] text-[var(--color-ink-3)] font-serif">{it.time}</span>
                  </div>
                  <div className="flex gap-2 mt-1.5 items-center text-[11.5px] text-[var(--color-ink-3)]">
                    <span
                      className="px-2 py-px border border-[rgba(26,22,17,0.14)] text-[10px] tracking-[0.3px] text-[var(--color-crimson)]"
                      style={{ background: "rgba(255,252,245,0.8)" }}
                    >
                      {it.cung}
                    </span>
                    <span className="font-serif italic text-[12px]">{it.mention}</span>
                    <span className="ml-auto">{it.count} tin</span>
                  </div>
                </button>
              ))}
            </div>
          ))}
        </div>

        {/* Footer */}
        <div
          className="px-8 py-4 border-t border-[rgba(26,22,17,0.14)] flex gap-2.5"
          style={{ background: "var(--color-paper-2)" }}
        >
          <Btn variant="crimson" className="flex-1 justify-center text-[13px]" onClick={onClose}>
            ＋ Bắt đầu phiên mới
          </Btn>
          <Btn variant="ghost" className="text-[16px]" aria-label="Mở liên kết">↗</Btn>
        </div>
      </div>
    </div>
  );
}
