"use client";

import type { CSSProperties } from "react";

import Link from "next/link";

import { Pill } from "@/components/primitives/pill";
import {
  Carousel,
  CarouselContent,
  CarouselDots,
  CarouselItem,
} from "@/components/primitives/carousel";
import { useIsHydrated } from "@/hooks/use-is-hydrated";
import { useLasoChart } from "@/lib/api/hooks";
import { nguHanhOf, starKeyFromName } from "@/lib/theme";
import { showToast } from "@/lib/toast";

import { AdviceCard } from "./advice-card";
import deckStyles from "./deck.module.css";
import { DestinyCard } from "./destiny-card";
import { LuckCard } from "./luck-card";
import { displayStarName, menhChinhTinh } from "./selectors";

const COMING_SOON = "Tính năng sẽ sớm được cập nhật ✦";

/** The greeting follows the clock, so it is gated on hydration. */
function greeting(): string {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 11) return "Chào buổi sáng";
  if (hour < 13) return "Chào buổi trưa";
  if (hour < 18) return "Chào buổi chiều";
  if (hour < 23) return "Chào buổi tối";
  return "Chào đêm khuya";
}

/**
 * The Bản mệnh screen — the deck every cast lands on.
 *
 * A pure derivation of the cached chart: no request, no loading state, no
 * persisted state of its own. Without a chart the established navigation
 * lock owns the route — the screen renders nothing rather than an empty deck.
 */
export function BanMenhScreen() {
  const { data: chart } = useLasoChart();
  const hydrated = useIsHydrated();

  if (chart === undefined) return null;

  const names = menhChinhTinh(chart).map(displayStarName);
  const keys = menhChinhTinh(chart).map(starKeyFromName);
  // Song tinh whose two chính tinh carry two different ngũ hành: each star is
  // shown in its own element colour and the badge itself becomes a gradient.
  const twoTone = (() => {
    if (keys.length !== 2) return null;
    const [a, b] = keys.map(nguHanhOf);
    if (a == null || b == null || a === b) return null;
    return [a, b] as const;
  })();

  return (
    <div className="pb-[calc(56px+var(--tabbar-h))] lg:pb-14">
      <div className="px-[22px] pt-[calc(10px+var(--safe-t))] md:px-[30px] lg:px-10 lg:pt-[calc(18px+var(--safe-t))]">
        <div className="flex items-center justify-between gap-[14px]">
          <div className="text-[10px] font-bold tracking-[0.26em] text-accent uppercase">
            {hydrated ? greeting() : "Chào bạn"}
          </div>
          <div className="flex flex-none flex-col items-end gap-[9px]">
            {twoTone ? (
              <span
                className="inline-flex items-center gap-2 rounded-full border bg-[linear-gradient(135deg,color-mix(in_srgb,var(--badge-a)_14%,transparent),color-mix(in_srgb,var(--badge-b)_14%,transparent))] px-[14px] py-[6px] text-[13px] font-semibold [border-color:color-mix(in_srgb,var(--badge-a),var(--badge-b))]"
                style={
                  {
                    "--badge-a": `var(--element-${twoTone[0]})`,
                    "--badge-b": `var(--element-${twoTone[1]})`,
                  } as CSSProperties
                }
              >
                <span className="h-[9px] w-[9px] rounded-full bg-[linear-gradient(135deg,var(--badge-a),var(--badge-b))] shadow-[0_0_10px_color-mix(in_srgb,var(--badge-a)_50%,transparent)]" />
                <span className="[color:var(--badge-a)]">{names[0]}</span>
                <span className="text-muted">·</span>
                <span className="[color:var(--badge-b)]">{names[1]}</span>
              </span>
            ) : (
              <span className="inline-flex items-center gap-2 rounded-full border border-accent-glow bg-[color-mix(in_srgb,var(--accent)_12%,transparent)] px-[14px] py-[6px] text-[13px] font-semibold text-accent">
                <span className="h-[9px] w-[9px] rounded-full bg-accent shadow-[0_0_10px_var(--accent-glow)]" />
                {names.length > 0 ? names.join(" · ") : "Vô Chính Diệu"}
              </span>
            )}
          </div>
        </div>
        <h2 className="mt-[10px] font-display text-[26px] leading-[1.06] font-semibold tracking-[-0.01em]">
          Bạn Sao Trẻ
        </h2>
        <p className="mt-[7px] max-w-[54ch] text-[13.5px] leading-[1.5] text-muted">
          Lá Bài Bản Mệnh ở đầu — vuốt sang để lật hai lá bài phụ.
        </p>
      </div>

      <Carousel>
        <CarouselContent className={deckStyles.deck}>
          <CarouselItem index={0} initialFocus={1} className={deckStyles.deckItem}>
            <DestinyCard chart={chart} />
          </CarouselItem>
          <CarouselItem index={1} className={deckStyles.deckItem}>
            <LuckCard chart={chart} />
          </CarouselItem>
          <CarouselItem index={2} className={deckStyles.deckItem}>
            <AdviceCard chart={chart} />
          </CarouselItem>
        </CarouselContent>
        <CarouselDots count={3} className={deckStyles.deckDots} />
      </Carousel>

      <div className="px-[22px] pt-[10px] md:px-[30px] lg:px-10">
        <div className="mx-auto mt-[18px] flex w-[min(340px,86%)] gap-[10px] md:w-[min(560px,92%)]">
          <Pill
            variant="ghost"
            className="flex-1 px-[10px] py-[13px] text-[14px]"
            onClick={() => showToast(COMING_SOON)}
          >
            ⇪ Lưu ảnh
          </Pill>
          <Pill
            className="flex-1 px-[10px] py-[13px] text-[14px]"
            onClick={() => showToast(COMING_SOON)}
          >
            Chia sẻ
          </Pill>
        </div>

        <div className="mx-[2px] mt-[26px] mb-[12px] flex items-baseline justify-between">
          <h2 className="text-[22px] font-semibold">Khám phá thêm</h2>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <Link
            className="glass flex cursor-pointer flex-col gap-[10px] border-0 p-[18px] text-left text-ink no-underline"
            href="/van-han"
          >
            <svg viewBox="0 0 24 24" fill="none" className="h-[30px] w-[30px] fill-none [stroke:var(--accent)] [stroke-width:1.4]">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 3v3M12 18v3M3 12h3M18 12h3" />
              <circle cx="12" cy="12" r="2.5" />
            </svg>
            <div>
              <b className="text-base font-semibold">Vận hạn</b>
            </div>
            <span className="text-[12.5px] text-muted">Tình cảm, công danh, tiền tài</span>
          </Link>
          <Link
            className="glass flex cursor-pointer flex-col gap-[10px] border-0 p-[18px] text-left text-ink no-underline"
            href="/hoi-ai"
          >
            <svg viewBox="0 0 24 24" fill="none" className="h-[30px] w-[30px] fill-none [stroke:var(--accent)] [stroke-width:1.4]">
              <path d="M4 6h16v10H9l-4 4V6z" />
              <path d="M9 11h6M9 8h4" />
            </svg>
            <div>
              <b className="text-base font-semibold">Hỏi AI</b>
            </div>
            <span className="text-[12.5px] text-muted">Trò chuyện cùng Thiên Hạc</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
