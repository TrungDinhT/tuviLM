/**
 * Constellation line-art for all fourteen chính tinh, keyed by the
 * normalised star key (`starKeyFromName`). Points are normalised 0..1 inside
 * a bounding box; `lines` index into `pts`.
 *
 * The first eight shapes are ported from the design prototype (`SHAPES`) for
 * the An sao reward reveal; the remaining six are authored here, since the
 * Bản mệnh main card renders one at full size, where the scattered-sky
 * fallback would read as a placeholder.
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
  // --- The six shapes the prototype never authored --------------------------
  liemtrinh: {
    // Tia lửa: a hard lightning strike, kỷ luật và đam mê cùng cháy.
    pts: [
      [0.6, 0],
      [0.32, 0.42],
      [0.55, 0.48],
      [0.34, 1],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
    ],
  },
  thienco: {
    // Ngả rẽ: một đường đi rẽ nhánh, mưu trí nhìn trước con đường.
    pts: [
      [0.2, 0.02],
      [0.44, 0.34],
      [0.4, 0.6],
      [0.14, 0.96],
      [0.78, 0.86],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [2, 4],
    ],
  },
  thienluong: {
    // Mái che: roof and legs, the shelter that gives the star its name.
    pts: [
      [0.5, 0.04],
      [0.05, 0.46],
      [0.95, 0.46],
      [0.3, 0.98],
      [0.7, 0.98],
    ],
    lines: [
      [0, 1],
      [0, 2],
      [1, 3],
      [2, 4],
    ],
  },
  thientuong: {
    // Ấn: a seal — an outer stamp with its inner signet.
    pts: [
      [0.12, 0.08],
      [0.88, 0.08],
      [0.88, 0.92],
      [0.12, 0.92],
      [0.36, 0.34],
      [0.64, 0.34],
      [0.64, 0.66],
      [0.36, 0.66],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 0],
      [4, 5],
      [5, 6],
      [6, 7],
      [7, 4],
    ],
  },
  thiendong: {
    // Sóng hiền: a gentle rolling wave, phúc hưởng thụ êm như nước.
    pts: [
      [0, 0.6],
      [0.25, 0.32],
      [0.5, 0.56],
      [0.75, 0.3],
      [1, 0.52],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
      [3, 4],
    ],
  },
  cumon: {
    // Cánh cổng: two pillars and a lintel, with the speaker in the doorway.
    pts: [
      [0.2, 1],
      [0.2, 0.28],
      [0.8, 0.28],
      [0.8, 1],
      [0.5, 0.62],
    ],
    lines: [
      [0, 1],
      [1, 2],
      [2, 3],
    ],
  },
};
