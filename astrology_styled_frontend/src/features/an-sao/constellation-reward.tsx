"use client";

import { useId } from "react";

import {
  CONSTELLATION_SCATTER,
  ConstellationGradientDefs,
  ConstellationShape,
} from "@/components/shared/constellation-art";
import { STAR_SHAPES } from "@/content/star-shapes";
import { cn } from "@/lib/utils";

interface ConstellationRewardProps {
  /**
   * Star keys of the previewed cung Mệnh, or null while no preview has
   * resolved — the sleeping state.
   */
  stars: readonly string[] | null;
  /** Backend display names, for the caption ("Thái Dương · …"). */
  names: readonly string[];
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
    <div className={cn("relative mt-[6px] mb-[2px] h-[154px]", lit && "constel-lit")} aria-hidden="true">
      <svg
        viewBox="0 0 320 100"
        preserveAspectRatio="xMidYMid meet"
        className="absolute inset-0 h-[116px] w-full overflow-visible transition-opacity duration-[350ms]"
      >
        {drawable ? (
          <>
            <ConstellationGradientDefs id={gradientId} />
            {stars.map((key, index) => {
              const shape = STAR_SHAPES[key];
              const box = boxes[index];
              if (shape === undefined || box === undefined) return null;
              return <ConstellationShape key={key} shape={shape} box={box} gradientId={gradientId} />;
            })}
          </>
        ) : (
          CONSTELLATION_SCATTER.map(([cx, cy], index) => (
            <circle
              key={index}
              className={cn("constel-node", lit && stars.length === 0 && "constel-node-neutral")}
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
