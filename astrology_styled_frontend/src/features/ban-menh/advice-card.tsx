"use client";

import type { CSSProperties } from "react";

import { adviceFor } from "@/content/advice";
import type { BuildLasoResponse } from "@/lib/api/schemas";

import deckStyles from "./deck.module.css";
import tarotStyles from "./tarot.module.css";

/**
 * Lá bài phụ 2 — Lời Khuyên.
 *
 * The entry is keyed by (Mệnh–Cục relation, âm dương polarity) — the stable
 * enums, never the display labels. The tag shows its provenance: the relation
 * label and the polarity, so the advice reads as about *this* chart.
 *
 * Its hue is the accent's own second shade: close to the deck's chrome, and
 * deliberately not the lucky colour — that one belongs to Vận May alone.
 */
export function AdviceCard({ chart }: { chart: BuildLasoResponse }) {
  const entry = adviceFor(chart.menh_cuc_relation, chart.am_duong_relation);
  const polarityLabel = chart.am_duong_relation === "thuan_ly" ? "Thuận lý" : "Nghịch lý";

  return (
    <article
      data-testid="advice-card"
      className={`${tarotStyles.tarot} glass relative flex min-h-0 min-w-0 flex-[1_1_auto] flex-col overflow-hidden px-5 py-[22px]`}
      style={{ "--t-hue": "var(--accent-2)" } as CSSProperties}
    >
      <div className={deckStyles.cardBack} aria-hidden="true">
        <span className={deckStyles.cardBackSigil}>✦</span>
      </div>
      <div className={deckStyles.cardFace}>
        <div className="relative z-1 flex items-center gap-[10px]">
          <span className={`${tarotStyles.g} grid h-8 w-8 place-items-center rounded-[10px]`}>
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 fill-none [stroke:var(--t-hue)] [stroke-width:1.6]">
              <path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v15H5.5A1.5 1.5 0 0 0 4 20.5zM20 5.5A1.5 1.5 0 0 0 18.5 4H13v15h5.5a1.5 1.5 0 0 1 1.5 1.5z" />
            </svg>
          </span>
          <span className="text-[10px] font-semibold tracking-[0.34em] text-muted">LÁ BÀI PHỤ</span>
        </div>
        <h3 className="mt-[13px] font-display text-[13.5px] font-medium tracking-[0.02em] text-muted">
          Lời Khuyên
        </h3>
        <div
          data-testid="advice-key"
          className="relative z-1 mt-1 font-display text-[20px] leading-[1.06] font-semibold text-ink [text-shadow:0_0_18px_var(--t-hue-glow)]"
        >
          {entry.phrase}
        </div>
        <p className="relative z-1 mt-[10px] text-xs leading-[1.55] font-light text-muted lg:max-w-[64ch]">
          {entry.advice}
        </p>
        <span
          className={`${tarotStyles.tag} relative z-1 mt-auto self-start rounded-full px-3 py-[6px] text-[11px] font-medium [color:var(--t-hue)] lg:mt-[14px]`}
        >
          ✦ {chart.menh_cuc_relation_label} · {polarityLabel}
        </span>
      </div>
    </article>
  );
}
