"use client";

import type { StarShape } from "@/content/star-shapes";

import styles from "./constellation-art.module.css";

/**
 * The constellation line-art renderer shared by every screen that draws a
 * StarShape — the An sao reward and the Bản mệnh main card. Styling comes
 * from the `constel-*` classes in constellation-art.module.css; the parent
 * adds `styles.constelLit` to trigger the draw-in.
 *
 * Both consumers render inside their own `<svg>` with their own viewBox —
 * this module supplies the pieces, not the frame.
 */

/** Scattered-sky dots for the sleeping and vô chính diệu states. */
export const CONSTELLATION_SCATTER: readonly (readonly [number, number])[] = [
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

/** The accent gradient the strokes and nodes paint with. One per `<svg>`. */
export function ConstellationGradientDefs({ id }: { id: string }) {
  return (
    <defs>
      <linearGradient id={id} gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="320" y2="0">
        <stop offset="0" className={styles.constelStopA} />
        <stop offset="1" className={styles.constelStopB} />
      </linearGradient>
    </defs>
  );
}

/** One shape drawn into a box of the parent's viewBox: lines, then nodes. */
export function ConstellationShape({
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
            className={styles.constelLine}
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
            className={styles.constelNode}
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
