"use client";

import type { CSSProperties } from "react";

import { locRoleBlurb } from "@/content/loc-roles";
import { luckColourFor } from "@/content/luck-colour";
import { thangCatFor } from "@/content/thang-cat";
import type { BuildLasoResponse } from "@/lib/api/schemas";

import deckStyles from "./deck.module.css";
import { cungRoleHolding } from "./selectors";
import tarotStyles from "./tarot.module.css";

/**
 * Lá bài phụ 1 — Vận May.
 *
 * Three facts from the chart: where Hóa Lộc and Lộc Tồn sit (blurb per cung
 * role), the lucky colour from the nạp âm bản mệnh's ngũ hành (labelled with
 * the nạp âm it came from), and the auspicious lunar months from the natal
 * year địa chi's tam hợp / lục hợp partners.
 *
 * The lucky colour is written to the scoped `--luck-hue` on this card alone;
 * CSS folds it into `--t-hue`. The global accent is never touched.
 */
export function LuckCard({ chart }: { chart: BuildLasoResponse }) {
  const hoaLocRole = cungRoleHolding(chart, "Hóa Lộc");
  const locTonRole = cungRoleHolding(chart, "Lộc Tồn");
  const luck = luckColourFor(chart.ban_menh_ngu_hanh);
  const thangCat = thangCatFor(chart.dia_chi_natal_year);
  const months = [...thangCat.tamHop, thangCat.lucHop].sort((a, b) => a - b);

  const locs = [
    { star: "Hóa Lộc", role: hoaLocRole },
    { star: "Lộc Tồn", role: locTonRole },
  ].filter((loc) => loc.role !== null);

  return (
    <article
      data-testid="luck-card"
      className={`${tarotStyles.tarot} glass relative flex min-h-0 min-w-0 flex-[1_1_auto] flex-col overflow-hidden px-5 py-[22px] [--t-hue:var(--luck-hue)]`}
      style={{ "--luck-hue": luck.hue } as CSSProperties}
    >
      <div className={deckStyles.cardBack} aria-hidden="true">
        <span className={deckStyles.cardBackSigil}>✦</span>
      </div>
      <div className={deckStyles.cardFace}>
        <div className="relative z-1 flex items-center gap-[10px]">
          <span className="grid h-8 w-8 place-items-center rounded-[10px] border bg-[color-mix(in_srgb,var(--t-hue)_18%,transparent)] [border-color:color-mix(in_srgb,var(--t-hue)_45%,transparent)]">
            <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 fill-none [stroke:var(--t-hue)] [stroke-width:1.6]">
              <path d="M12 3l2.4 5.3L20 9l-4 4 1 6-5-3-5 3 1-6-4-4 5.6-.7z" />
            </svg>
          </span>
          <span className="text-[10px] font-semibold tracking-[0.34em] text-muted">LÁ BÀI PHỤ</span>
        </div>
        <h3 className="mt-[13px] font-display text-[13.5px] font-medium tracking-[0.02em] text-muted">
          Vận May
        </h3>
        <div className="relative z-1 mt-1 font-display text-[20px] leading-[1.06] font-semibold text-ink [text-shadow:0_0_18px_var(--t-hue-glow)]">
          {hoaLocRole !== null && hoaLocRole === locTonRole
            ? `Lộc tụ tại ${hoaLocRole}`
            : "Hai nguồn lộc"}
        </div>
        {locs.map((loc) => (
          <p
            key={loc.star}
            className="relative z-1 mt-[10px] text-xs leading-[1.55] font-light text-muted lg:max-w-[64ch]"
          >
            <b className="font-semibold text-ink">
              {loc.star} tại {loc.role}.
            </b>{" "}
            {locRoleBlurb(loc.role ?? "")}
          </p>
        ))}
        <div className="relative z-1 mt-3 flex items-center gap-[11px] rounded-full border border-glass-line bg-[rgba(255,255,255,0.055)] py-2 pl-[9px] pr-[14px] text-[13px] text-muted">
          <span
            data-testid="luck-orb"
            className="h-[26px] w-[26px] shrink-0 rounded-full bg-[radial-gradient(circle_at_34%_28%,#ffffff,color-mix(in_srgb,var(--luck-hue)_55%,#ffffff)_26%,var(--luck-hue)_70%,color-mix(in_srgb,var(--luck-hue)_60%,#000000)_100%)] shadow-[0_0_14px_color-mix(in_srgb,var(--luck-hue)_55%,transparent),inset_0_-2px_5px_rgba(0,0,0,0.35)]"
            aria-hidden="true"
          />
          Màu may mắn<b className="ml-auto text-[14px] font-semibold text-ink">{luck.name}</b>
        </div>
        <p className="relative z-1 mt-[10px] text-xs leading-[1.55] font-light text-muted lg:max-w-[64ch]">
          Theo nạp âm bản mệnh <b className="font-semibold text-ink">{chart.ban_menh_name}</b>.
        </p>
        <span className="relative z-1 mt-auto self-start rounded-full border bg-[color-mix(in_srgb,var(--t-hue)_10%,transparent)] px-3 py-[6px] text-[11px] font-medium [border-color:color-mix(in_srgb,var(--t-hue)_40%,transparent)] [color:var(--t-hue)] lg:mt-[14px]">
          ✦ Tháng cát: {months.join(" · ")} (âm lịch)
        </span>
      </div>
    </article>
  );
}
