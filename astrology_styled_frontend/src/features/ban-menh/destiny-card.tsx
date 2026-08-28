"use client";

import { useId } from "react";

import {
  CONSTELLATION_SCATTER,
  ConstellationGradientDefs,
  ConstellationShape,
} from "@/components/shared/constellation-art";
import { destinyFor } from "@/content/destiny";
import { STAR_SHAPES } from "@/content/star-shapes";
import type { BuildLasoResponse } from "@/lib/api/schemas";
import { starKeyFromName } from "@/lib/theme";

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
    <article className="destiny reveal">
      <div className="card-back" aria-hidden="true">
        <span className="card-back-sigil">✦</span>
      </div>
      <div className="card-face">
        <div className="dtitle">TỬ VI CÁ NHÂN</div>
        <div className="dsub">
          {names.length > 0 ? (
            <>
              Chính tinh chiếu mệnh: <b>{label}</b>
              {songTinh ? " · sao đôi" : ""}
            </>
          ) : (
            <>
              Mệnh <b>vô chính diệu</b> — cả bầu trời soi chiếu
            </>
          )}
        </div>
        <div className="dchip">
          <i>✦</i> {entry.archetype}
        </div>
        <div className="dstage constel-lit" aria-hidden="true">
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
                <circle key={index} className="constel-node" cx={cx} cy={cy * 2.2} r="2.4" />
              ))
            )}
          </svg>
        </div>
        <div className="dmantra">{entry.mantra}</div>
      </div>
    </article>
  );
}
