"use client";

import { Pill } from "@/components/primitives/pill";
import { BalanceBadge } from "@/components/shell/balance-badge";
import {
  Carousel,
  CarouselContent,
  CarouselDots,
  CarouselItem,
} from "@/components/primitives/carousel";
import { useIsHydrated } from "@/hooks/use-is-hydrated";
import { useLasoChart } from "@/lib/api/hooks";
import { showToast } from "@/lib/toast";

import { AdviceCard } from "./advice-card";
import deckStyles from "./deck.module.css";
import { DestinyCard } from "./destiny-card";
import { LuckCard } from "./luck-card";

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
 * The deck is derived from the cached chart; only the header reads account
 * balance. Without a chart the established navigation
 * lock owns the route — the screen renders nothing rather than an empty deck.
 */
export function BanMenhScreen() {
  const { data: chart } = useLasoChart();
  const hydrated = useIsHydrated();

  if (chart === undefined) return null;

  return (
    <div className="pb-[calc(56px+var(--tabbar-h))] lg:pb-14">
      <div className="px-[22px] pt-[calc(10px+var(--safe-t))] md:px-[30px] lg:px-10 lg:pt-[calc(18px+var(--safe-t))]">
        <div className="flex items-center justify-between gap-[14px]">
          <div className="text-[10px] font-bold tracking-[0.26em] text-accent uppercase">
            {hydrated ? greeting() : "Chào bạn"}
          </div>
          <div className="flex flex-none flex-col items-end gap-[9px] lg:hidden">
            <BalanceBadge />
          </div>
        </div>
        <h2 className="mt-[10px] font-display text-[26px] leading-[1.06] font-semibold tracking-[-0.01em]">
          Bạn Sao Trẻ
        </h2>
        <p className="mt-[7px] max-w-[54ch] text-[13.5px] leading-[1.5] text-muted">
          Lá Bài Bản Mệnh ở đầu — vuốt sang để lật hai lá bài phụ.
        </p>
      </div>

      <div className="mt-8">
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
      </div>

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
      </div>
    </div>
  );
}
