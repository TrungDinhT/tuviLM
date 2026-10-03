"use client";

import {
  createContext,
  useContext,
  useId,
  useState,
  type CSSProperties,
  type ReactNode,
} from "react";

import { cn } from "@/lib/utils";

/**
 * Carousel — a composition primitive in the shadcn shape
 * (Carousel → CarouselContent → CarouselItem, plus CarouselDots in place of
 * the prev/next buttons our design doesn't use), but with no carousel
 * library: the browser's own scroll-snap drives the gesture, and CSS
 * scroll-driven animations drive any scroll-linked visuals. JavaScript only
 * tracks the active item (dots, z-index) and writes the `--card-focus`
 * fallback variable for browsers without `animation-timeline: view()`.
 *
 * The primitive ships structure and mechanics (inline scroll-snap utilities);
 * skins like `.deck` supply sizing and effects.
 */

/**
 * Browsers with scroll-driven animations get the focus visuals from CSS;
 * the rest get imperative `--card-focus` writes on scroll — main-thread
 * per-frame style writes are the fallback, not the default. Evaluated once:
 * support never flips at runtime.
 */
const HAS_SCROLL_TIMELINES =
  typeof CSS !== "undefined" && CSS.supports("animation-timeline: view()");

const CarouselContext = createContext<{ active: number; setActive: (index: number) => void }>({
  active: 0,
  setActive: () => {},
});

export function Carousel({ children }: { children: ReactNode }) {
  const [active, setActive] = useState(0);
  return (
    <CarouselContext.Provider value={{ active, setActive }}>
      {children}
    </CarouselContext.Provider>
  );
}

export function CarouselContent({
  className,
  children,
}: {
  className?: string;
  children: ReactNode;
}) {
  const { setActive } = useContext(CarouselContext);

  /** Closest-to-centre tracking: drives the dots and the focused item's
      z-index. Writes `--card-focus` only on the fallback path. */
  const trackActive = (rail: HTMLDivElement) => {
    const items = [...rail.children] as HTMLElement[];
    const centers = items.map((item) => item.offsetLeft + item.offsetWidth / 2);
    const viewCenter = rail.scrollLeft + rail.clientWidth / 2;

    let active = 0;
    let closest = Infinity;
    items.forEach((item, index) => {
      const center = centers[index]!;
      const previous = centers[index - 1];
      const next = centers[index + 1];
      const spacing = Math.min(
        previous === undefined ? Infinity : center - previous,
        next === undefined ? Infinity : next - center,
      );
      const range = spacing === Infinity ? rail.clientWidth / 2 : spacing;
      const distance = Math.abs(center - viewCenter);
      if (!HAS_SCROLL_TIMELINES) {
        item.style.setProperty(
          "--card-focus",
          Math.min(1, Math.max(0, 1 - distance / range)).toFixed(3),
        );
      }
      if (distance < closest) {
        closest = distance;
        active = index;
      }
    });
    setActive(active);
  };

  return (
    <div
      className={cn("flex snap-x snap-mandatory overflow-x-auto", className)}
      onScroll={(event) => trackActive(event.currentTarget)}
    >
      {children}
    </div>
  );
}

export function CarouselItem({
  index,
  initialFocus = 0,
  className,
  children,
}: {
  /** Zero-based position — compared against the active index for `is-active`. */
  index: number;
  /** The `--card-focus` rendered before the first scroll frame (fallback path). */
  initialFocus?: number;
  className?: string;
  children: ReactNode;
}) {
  const { active } = useContext(CarouselContext);
  // Each item publishes its traversal through the rail as a named inline
  // view timeline; descendants subscribe via --card-tl (their own view()
  // would resolve against an overflow:hidden child, not the rail).
  const timeline = `--tl-${useId().replace(/:/g, "")}`;

  return (
    <div
      role="group"
      aria-roledescription="slide"
      className={cn("shrink-0 snap-center", index === active && "is-active", className)}
      style={
        {
          "--card-focus": initialFocus,
          "--card-tl": timeline,
          viewTimelineName: timeline,
          viewTimelineAxis: "inline",
        } as CSSProperties
      }
    >
      {children}
    </div>
  );
}

export function CarouselDots({
  count,
  className,
}: {
  count: number;
  className?: string;
}) {
  const { active } = useContext(CarouselContext);
  return (
    <div className={className} aria-hidden="true">
      {Array.from({ length: count }, (_, index) => (
        <i key={index} className={index === active ? "on" : undefined} />
      ))}
    </div>
  );
}
