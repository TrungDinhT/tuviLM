"use client";

import { useId } from "react";

import {
  CONSTELLATION_SCATTER,
  ConstellationGradientDefs,
  ConstellationShape,
} from "@/components/shared/constellation-art";
import constelStyles from "@/components/shared/constellation-art.module.css";
import { destinyFor } from "@/content/destiny";
import { STAR_SHAPES } from "@/content/star-shapes";
import type { BuildLasoResponse } from "@/lib/api/schemas";
import { starKeyFromName } from "@/lib/theme";

import deckStyles from "./deck.module.css";
import cardStyles from "./destiny-card.module.css";
import { displayStarName, menhChinhTinh, menhStarKey } from "./selectors";

/**
 * Lá Bài Bản Mệnh — the deck's main card.
 *
 * Everything on it resolves from the chính tinh of cung Mệnh through the
 * destiny table: archetype chip, mantra, and the constellation on the card
 * stage. Vô chính diệu gets its authored reading and the scattered sky —
 * a reading in its own right, never an empty stage.
 */
export function DestinyCard({ chart }: { chart: BuildLasoResponse }) {
  const gradientId = useId().replace(/:/g, "");

  const names = menhChinhTinh(chart);
  const keys = names.map(starKeyFromName);
  const entry = destinyFor(menhStarKey(chart));
  const songTinh = names.length === 2;
  const label = names.map(displayStarName).join(" · ");

  const boxes: readonly (readonly [number, number, number, number])[] = songTinh
    ? [
        [8, 40, 146, 140],
        [166, 40, 146, 140],
      ]
    : [[60, 26, 200, 168]];

  return (
    <article
      data-testid="destiny-card"
      className={`${cardStyles.destiny} ${cardStyles.reveal} relative flex aspect-[9/16] min-h-0 min-w-0 flex-[1_1_auto] flex-col overflow-hidden rounded-[22px] px-6 pt-[26px] pb-6 md:pt-[28px]`}
    >
      <div className={deckStyles.cardBack} aria-hidden="true">
        <span className={deckStyles.cardBackSigil}>✦</span>
      </div>
      <div className={deckStyles.cardFace}>
        <div className="font-display text-base font-semibold tracking-[0.06em] md:text-[20px]">
          TỬ VI CÁ NHÂN
        </div>
        <div className="mt-[5px] text-xs text-muted md:text-[14px]">
          {names.length > 0 ? (
            <>
              Chính tinh chiếu mệnh: <b className="font-semibold text-ink">{label}</b>
              {songTinh ? " · sao đôi" : ""}
            </>
          ) : (
            <>
              Mệnh <b className="font-semibold text-ink">vô chính diệu</b> — cả bầu trời soi chiếu
            </>
          )}
        </div>
        <div
          data-testid="destiny-chip"
          className={`${cardStyles.dchip} mt-[14px] inline-flex items-center gap-2 self-start rounded-full px-[14px] py-[7px] text-[12.5px] font-semibold text-ink`}
        >
          <i className="not-italic text-accent">✦</i> {entry.archetype}
        </div>
        <div className={`${constelStyles.constelLit} grid min-h-0 flex-[1_1_auto] place-items-center`} aria-hidden="true">
          <svg viewBox="0 0 320 220" preserveAspectRatio="xMidYMid meet" className="h-full w-full">
            {keys.every((key) => STAR_SHAPES[key] !== undefined) && keys.length > 0 ? (
              <>
                <ConstellationGradientDefs id={gradientId} />
                {keys.map((key, index) => {
                  const shape = STAR_SHAPES[key];
                  const box = boxes[index];
                  if (shape === undefined || box === undefined) return null;
                  return (
                    <ConstellationShape key={key} shape={shape} box={box} gradientId={gradientId} />
                  );
                })}
              </>
            ) : (
              // The scattered sky — the authored vô chính diệu treatment.
              CONSTELLATION_SCATTER.map(([cx, cy], index) => (
                <circle key={index} className={constelStyles.constelNode} cx={cx} cy={cy * 2.2} r="2.4" />
              ))
            )}
          </svg>
        </div>
        <div
          data-testid="destiny-mantra"
          className={`${cardStyles.dmantra} pt-[14px] font-display text-[15px] leading-[1.42] italic md:text-[17px]`}
        >
          {entry.mantra}
        </div>
      </div>
    </article>
  );
}
