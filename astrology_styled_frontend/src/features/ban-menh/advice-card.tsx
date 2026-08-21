"use client";

import type { CSSProperties } from "react";

import { adviceFor } from "@/content/advice";
import type { BuildLasoResponse } from "@/lib/api/schemas";
import { cn } from "@/lib/utils";

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
export function AdviceCard({
  chart,
  active = true,
  initialFocus = 0,
}: {
  chart: BuildLasoResponse;
  /** Whether this card opens focused — it paints above its neighbours. */
  active?: boolean;
  /** The `--card-focus` before the first scroll frame; see DestinyCard. */
  initialFocus?: number;
}) {
  const entry = adviceFor(chart.menh_cuc_relation, chart.am_duong_relation);
  const polarityLabel = chart.am_duong_relation === "thuan_ly" ? "Thuận lý" : "Nghịch lý";

  return (
    <article
      className={cn("tarot glass", active && "is-active")}
      style={{ "--t-hue": "var(--accent-2)", "--card-focus": initialFocus } as CSSProperties}
    >
      <div className="card-back" aria-hidden="true">
        <span className="card-back-sigil">✦</span>
      </div>
      <div className="card-face">
        <div className="top">
          <span className="g">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M4 5.5A1.5 1.5 0 0 1 5.5 4H11v15H5.5A1.5 1.5 0 0 0 4 20.5zM20 5.5A1.5 1.5 0 0 0 18.5 4H13v15h5.5a1.5 1.5 0 0 1 1.5 1.5z" />
            </svg>
          </span>
          <span className="k">LÁ BÀI PHỤ</span>
        </div>
        <h3>Lời Khuyên</h3>
        <div className="key">{entry.phrase}</div>
        <p>{entry.advice}</p>
        <span className="tag">
          ✦ {chart.menh_cuc_relation_label} · {polarityLabel}
        </span>
      </div>
    </article>
  );
}
