"use client";

import Link from "next/link";
import { useState } from "react";

import { Pill } from "@/components/primitives/pill";
import { useIsHydrated } from "@/hooks/use-is-hydrated";
import { useLasoChart } from "@/lib/api/hooks";
import { useToastStore } from "@/store/toast-store";

import { AdviceCard } from "./advice-card";
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
  const [activeDot, setActiveDot] = useState(0);
  const showToast = useToastStore((state) => state.show);
  const hydrated = useIsHydrated();

  if (chart === undefined) return null;

  /**
   * Scroll-linked focus: each card's `--card-focus` is how close its centre
   * is to the rail's visible centre, normalised by the distance to its
   * nearest neighbour — so the leaving card shrinks and the incoming card
   * grows linearly through the swipe, meeting at 0.5 halfway. Written
   * imperatively per frame; React state only tracks the active dot.
   */
  const updateFocus = (rail: HTMLDivElement) => {
    const cards = [...rail.children] as HTMLElement[];
    const centers = cards.map((card) => card.offsetLeft + card.offsetWidth / 2);
    const viewCenter = rail.scrollLeft + rail.clientWidth / 2;

    let active = 0;
    let closest = Infinity;
    cards.forEach((card, index) => {
      const center = centers[index]!;
      const previous = centers[index - 1];
      const next = centers[index + 1];
      const spacing = Math.min(
        previous === undefined ? Infinity : center - previous,
        next === undefined ? Infinity : next - center,
      );
      const range = spacing === Infinity ? rail.clientWidth / 2 : spacing;
      const distance = Math.abs(center - viewCenter);
      card.style.setProperty(
        "--card-focus",
        Math.min(1, Math.max(0, 1 - distance / range)).toFixed(3),
      );
      if (distance < closest) {
        closest = distance;
        active = index;
      }
    });
    setActiveDot(active);
  };

  const stars = menhChinhTinh(chart).map(displayStarName);
  const badge = stars.length > 0 ? stars.join(" · ") : "Vô Chính Diệu";

  return (
    <div className="pb-[calc(56px+var(--tabbar-h))] lg:pb-14">
      <div className="px-[22px] pt-[calc(10px+var(--safe-t))] md:px-[30px] lg:px-10 lg:pt-[calc(18px+var(--safe-t))]">
        <div className="headline">
          <div>
            <div className="eyebrow">{hydrated ? greeting() : "Chào bạn"}</div>
            <h2>Bạn Sao Trẻ</h2>
            <p className="headsub">
              Lá Bài Bản Mệnh ở đầu — vuốt sang để lật hai lá bài phụ.
            </p>
          </div>
          <div className="head-aside">
            <span className="elbadge">
              <span className="dot" />
              {badge}
            </span>
          </div>
        </div>
      </div>

      <div className="deck" onScroll={(event) => updateFocus(event.currentTarget)}>
        <DestinyCard chart={chart} active={activeDot === 0} initialFocus={1} />
        <LuckCard chart={chart} active={activeDot === 1} initialFocus={0} />
        <AdviceCard chart={chart} active={activeDot === 2} initialFocus={0} />
      </div>
      <div className="deck-dots" aria-hidden="true">
        {[0, 1, 2].map((index) => (
          <i key={index} className={index === activeDot ? "on" : undefined} />
        ))}
      </div>

      <div className="px-[22px] pt-[10px] md:px-[30px] lg:px-10">
        <div className="share-row">
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

        <div className="shead">
          <h2>Khám phá thêm</h2>
        </div>
        <div className="shorts">
          <Link className="short glass" href="/van-han">
            <svg viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="9" />
              <path d="M12 3v3M12 18v3M3 12h3M18 12h3" />
              <circle cx="12" cy="12" r="2.5" />
            </svg>
            <div>
              <b>Vận hạn</b>
            </div>
            <span>Tình cảm, công danh, tiền tài</span>
          </Link>
          <Link className="short glass" href="/hoi-ai">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M4 6h16v10H9l-4 4V6z" />
              <path d="M9 11h6M9 8h4" />
            </svg>
            <div>
              <b>Hỏi AI</b>
            </div>
            <span>Trò chuyện cùng Nghê Sao</span>
          </Link>
        </div>
      </div>
    </div>
  );
}
