/**
 * Constellation line-art for the reward reveal, ported from the design
 * prototype (`SHAPES`). Points are normalised 0..1 inside a bounding box;
 * `lines` index into `pts`.
 *
 * Only eight of the fourteen chính tinh have authored art in the prototype.
 * A star without a shape falls back to the neutral scattered-sky treatment —
 * never a broken or placeholder render.
 */
export interface StarShape {
  readonly pts: readonly (readonly [number, number])[];
  readonly lines: readonly (readonly [number, number])[];
}

export const STAR_SHAPES: Record<string, StarShape> = {
  tuvi: {
    pts: [
      [0, 0.72],
      [0.26, 0.24],
      [0.5, 0.6],
      [0.74, 0.2],
      [1, 0.66],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
    ],
  },
  thienphu: {
    pts: [
      [0.5, 0],
      [1, 0.5],
      [0.5, 1],
      [0, 0.5],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 0],
    ],
  },
  thatsat: {
    pts: [
      [0, 0.2],
      [0.28, 0.36],
      [0.54, 0.3],
      [0.7, 0.56],
      [0.86, 0.82],
      [1, 0.56],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 5],
    ],
  },
  phaquan: {
    pts: [
      [0.5, 0.5],
      [0, 0.18],
      [0.92, 0],
      [1, 0.72],
      [0.28, 1],
    ],
    lines: [
      [0, 1],
      [0, 2],
      [0, 3],
      [0, 4],
    ],
  },
  thamlang: {
    pts: [
      [0.5, 0],
      [0.92, 0.36],
      [0.76, 0.92],
      [0.24, 0.92],
      [0.08, 0.36],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
      [4, 0],
    ],
  },
  thaiduong: {
    pts: [
      [0.5, 0.5],
      [0.5, 0],
      [1, 0.5],
      [0.5, 1],
      [0, 0.5],
    ],
    lines: [
      [0, 1],
      [0, 2],
      [0, 3],
      [0, 4],
    ],
  },
  thaiam: {
    pts: [
      [0, 0.5],
      [0.2, 0.16],
      [0.5, 0.06],
      [0.8, 0.16],
      [1, 0.5],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
    ],
  },
  vukhuc: {
    pts: [
      [0.5, 0],
      [1, 1],
      [0, 1],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 0],
    ],
  },
};
