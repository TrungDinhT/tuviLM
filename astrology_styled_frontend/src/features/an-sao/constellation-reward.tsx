"use client";

import { useId } from "react";

import { cn } from "@/lib/utils";

import { STAR_SHAPES, type StarShape } from "./star-shapes";

/** Scattered-sky dots for the sleeping and vô chính diệu states. */
const SCATTER: readonly (readonly [number, number])[] = [
  [26, 34],
  [66, 62],
  [108, 40],
  [150, 72],
  [192, 34],
  [232, 66],
  [272, 46],
  [300, 56],
  [90, 80],
  [210, 22],
];

interface ConstellationRewardProps {
  /**
   * Star keys of the previewed cung Mệnh, or null while no preview has
   * resolved — the sleeping state.
   */
  stars: readonly string[] | null;
  /** Backend display names, for the caption ("Thái Dương · …"). */
  names: readonly string[];
}

function ShapeLines({
  shape,
  box,
  gradientId,
}: {
  shape: StarShape;
  box: readonly [number, number, number, number];
  gradientId: string;
}) {
  const [x0, y0, w, h] = box;
  const point = (index: number) => {
    const p = shape.pts[index];
    return p === undefined ? ([0, 0] as const) : ([x0 + p[0] * w, y0 + p[1] * h] as const);
  };
  return (
    <>
      {shape.lines.map(([a, b]) => {
        const [x1, y1] = point(a);
        const [x2, y2] = point(b);
        return (
          <line
            key={`${a}-${b}`}
            className="reward-line"
            style={{ stroke: `url(#${gradientId})` }}
            x1={x1.toFixed(1)}
            y1={y1.toFixed(1)}
            x2={x2.toFixed(1)}
            y2={y2.toFixed(1)}
          />
        );
      })}
      {shape.pts.map((_, index) => {
        const [cx, cy] = point(index);
        return (
          <circle
            key={index}
            className="reward-node"
            style={{ fill: `url(#${gradientId})` }}
            cx={cx.toFixed(1)}
            cy={cy.toFixed(1)}
            r={index === 0 ? 3.4 : 2.8}
          />
        );
      })}
    </>
  );
}

/**
 * The constellation that wakes as the birth data completes.
 *
 * Fed by the preview endpoint — never by birth-date arithmetic. Stars with
 * authored line-art draw their constellation in the accent gradient; a star
 * without art, and vô chính diệu, get the neutral scattered sky. Portrait
 * art joins later through the content layer; until then the SVG treatment is
 * the only one, exactly as the prototype falls back.
 */
export function ConstellationReward({ stars, names }: ConstellationRewardProps) {
  // useId carries colons, which are awkward inside url(#…) — strip them.
  const gradientId = useId().replace(/:/g, "");
  const lit = stars !== null;
  const drawable = lit && stars.length > 0 && stars.every((key) => STAR_SHAPES[key] !== undefined);

  const caption = !lit
    ? "CHÒM SAO MỆNH ĐANG NGỦ"
    : stars.length === 0
      ? "MỆNH VÔ CHÍNH DIỆU · TRỜI RỘNG MỞ"
      : `CHÒM SAO ${names.join(" · ").toUpperCase()} ĐÃ THỨC`;

  // One centred constellation for a single star, two side by side for song tinh.
  const boxes: readonly (readonly [number, number, number, number])[] =
    stars !== null && stars.length === 2
      ? [
          [18, 14, 128, 70],
          [176, 14, 128, 70],
        ]
      : [[92, 16, 136, 66]];

  return (
    <div className={cn("relative mt-[6px] mb-[2px] h-[154px]", lit && "reward-lit")} aria-hidden="true">
      <svg
        viewBox="0 0 320 100"
        preserveAspectRatio="xMidYMid meet"
        className="absolute inset-0 h-[116px] w-full overflow-visible transition-opacity duration-[350ms]"
      >
        {drawable ? (
          <>
            <defs>
              <linearGradient id={gradientId} gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="320" y2="0">
                <stop offset="0" className="reward-stop-a" />
                <stop offset="1" className="reward-stop-b" />
              </linearGradient>
            </defs>
            {stars.map((key, index) => {
              const shape = STAR_SHAPES[key];
              const box = boxes[index];
              if (shape === undefined || box === undefined) return null;
              return <ShapeLines key={key} shape={shape} box={box} gradientId={gradientId} />;
            })}
          </>
        ) : (
          SCATTER.map(([cx, cy], index) => (
            <circle
              key={index}
              className={cn("reward-node", lit && stars.length === 0 && "reward-node-neutral")}
              cx={cx}
              cy={cy}
              r="2.4"
            />
          ))
        )}
      </svg>
      <div className="absolute right-0 bottom-[4px] left-0 z-2 text-center text-[12px] tracking-[0.2em] text-muted">
        {caption}
      </div>
    </div>
  );
}
