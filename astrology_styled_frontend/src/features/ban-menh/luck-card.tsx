"use client";

import type { CSSProperties } from "react";

import { locRoleBlurb } from "@/content/loc-roles";
import { luckColourFor } from "@/content/luck-colour";
import { thangCatFor } from "@/content/thang-cat";
import type { BuildLasoResponse } from "@/lib/api/schemas";
import { cn } from "@/lib/utils";

import { cungRoleHolding } from "./selectors";

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
export function LuckCard({
  chart,
  active = true,
}: {
  chart: BuildLasoResponse;
  /** Whether this card is the rail's focused one — the rest rest face-down. */
  active?: boolean;
}) {
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
      className={cn("tarot glass luck-card", active && "is-active")}
      style={{ "--luck-hue": luck.hue } as CSSProperties}
    >
      <div className="top">
        <span className="g">
          <svg viewBox="0 0 24 24" fill="none">
            <path d="M12 3l2.4 5.3L20 9l-4 4 1 6-5-3-5 3 1-6-4-4 5.6-.7z" />
          </svg>
        </span>
        <span className="k">LÁ BÀI PHỤ</span>
      </div>
      <h3>Vận May</h3>
      <div className="key">
        {hoaLocRole !== null && hoaLocRole === locTonRole
          ? `Lộc tụ tại ${hoaLocRole}`
          : "Hai nguồn lộc"}
      </div>
      {locs.map((loc) => (
        <p key={loc.star}>
          <b>
            {loc.star} tại {loc.role}.
          </b>{" "}
          {locRoleBlurb(loc.role ?? "")}
        </p>
      ))}
      <div className="luck-row">
        <span className="luck-orb" aria-hidden="true" />
        Màu may mắn<b>{luck.name}</b>
      </div>
      <p>
        Theo nạp âm bản mệnh <b>{chart.ban_menh_name}</b>.
      </p>
      <span className="tag">✦ Tháng cát: {months.join(" · ")} (âm lịch)</span>
    </article>
  );
}
