"use client";

import { useState } from "react";

import { ThemeProvider } from "@/components/providers/theme-provider";
import type { ChartOutcome } from "@/lib/theme";

/**
 * Scaffolding, not product. This page exists so the token set, the runtime
 * accent, and the scoped-accent pattern can be seen working before any screen
 * is built. Delete it once the An sao screen lands.
 */

const OUTCOMES: ReadonlyArray<{ label: string; outcome: ChartOutcome | null }> = [
  { label: "Chưa an sao (mặc định Kim)", outcome: null },
  { label: "Đơn tinh · Tử Vi", outcome: { stars: ["tuvi"] } },
  { label: "Song tinh · Vũ Khúc + Tham Lang", outcome: { stars: ["vukhuc", "thamlang"] } },
  { label: "Vô chính diệu", outcome: { stars: [] } },
  { label: "Sao chưa có màu · Liêm Trinh", outcome: { stars: ["liemtrinh"] } },
];

/**
 * Worked example of the scoped-accent pattern: each card sets its own
 * `--t-hue` inline, and uses it for border, glow and tag. The surrounding
 * accent is untouched, which is why the two cards can disagree while the
 * heading above them still follows the chart.
 */
function TopicCard({ hue, title, body }: { hue: string; title: string; body: string }) {
  return (
    <article
      className="hue-surface flex flex-col rounded-card border bg-glass p-5 backdrop-blur-2xl"
      style={{ "--t-hue": hue } as React.CSSProperties}
    >
      <span className="text-[10px] font-semibold tracking-[0.34em] text-muted uppercase">
        Lá bài phụ
      </span>
      <h3 className="mt-3 font-display text-2xl font-semibold" style={{ color: "var(--t-hue)" }}>
        {title}
      </h3>
      <p className="mt-2 text-[13px] leading-relaxed font-light text-muted">{body}</p>
    </article>
  );
}

export function AccentDemo() {
  const [index, setIndex] = useState(0);
  const current = OUTCOMES[index] ?? OUTCOMES[0]!;

  return (
    <ThemeProvider outcome={current.outcome}>
      <section className="mt-8">
        <h2 className="font-display text-xl font-semibold">Accent theo lá số</h2>
        <p className="mt-1 text-[13px] text-muted">
          Đổi kết quả để thấy toàn bộ quầng sáng và gradient đổi theo, không tải lại trang.
        </p>

        <div className="mt-4 flex flex-wrap gap-2">
          {OUTCOMES.map((option, i) => (
            <button
              key={option.label}
              type="button"
              onClick={() => setIndex(i)}
              aria-pressed={i === index}
              className="cursor-pointer rounded-full border border-glass-line px-3 py-2 text-[11px] transition-colors aria-pressed:border-transparent aria-pressed:bg-accent aria-pressed:text-bg-0"
            >
              {option.label}
            </button>
          ))}
        </div>

        <div
          className="accent-gradient mt-5 flex items-center gap-3 rounded-card border p-4"
          style={{ borderColor: "var(--accent-glow)" }}
        >
          <span className="font-display text-lg font-semibold text-bg-0">
            Gradient accent-2 → accent
          </span>
        </div>

        <h2 className="mt-8 font-display text-xl font-semibold">Accent lồng nhau</h2>
        <p className="mt-1 text-[13px] text-muted">
          Hai thẻ dưới đây tự đặt <code className="text-ink">--t-hue</code> riêng. Accent toàn cục ở
          trên vẫn không đổi.
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <TopicCard
            hue="var(--star-thamlang)"
            title="Tình Duyên"
            body="Thẻ này dùng hue riêng, không đụng tới --accent."
          />
          <TopicCard
            hue="var(--star-phaquan)"
            title="Học Đường"
            body="Thẻ bên cạnh dùng hue khác hẳn, hai bên không ảnh hưởng nhau."
          />
        </div>
      </section>
    </ThemeProvider>
  );
}
