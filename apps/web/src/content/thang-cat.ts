import type { DiaChi } from "@/lib/api/schemas";

/**
 * Tháng cát — the auspicious lunar months for a natal year địa chi.
 *
 * A precomputed 12-row table, not runtime arithmetic. Each row holds the
 * chi's partners, mapped to lunar months (tháng Giêng = Dần):
 *
 * - tam hợp: the two chi at `index ± 4` (e.g. Dần – Ngọ – Tuất)
 * - lục hợp: the chi at `13 − index`, wrapped mod 12 (e.g. Tý – Sửu,
 *   Dần – Hợi), over the 0-based index of the enum order
 *   Tý Sửu Dần Mão Thìn Tỵ Ngọ Mùi Thân Dậu Tuất Hợi
 *
 * The frontend deliberately does not reimplement the transforms
 * (`src/refactored/placement/transforms.py`); the test in this module
 * re-derives every row from these definitions, so a mis-keyed entry fails
 * loudly instead of rendering a wrong month.
 *
 * Months are always presented as âm lịch — see the card.
 */

export interface ThangCatRow {
  /** The tam hợp partners' lunar months, ascending. */
  readonly tamHop: readonly [number, number];
  /** The lục hợp partner's lunar month. */
  readonly lucHop: number;
}

export const THANG_CAT: Record<DiaChi, ThangCatRow> = {
  ty: { tamHop: [3, 7], lucHop: 12 }, // Tý: tam hợp Thìn·Thân, lục hợp Sửu
  suu: { tamHop: [4, 8], lucHop: 11 }, // Sửu: Tỵ·Dậu, Tý
  dan: { tamHop: [5, 9], lucHop: 10 }, // Dần: Ngọ·Tuất, Hợi
  meo: { tamHop: [6, 10], lucHop: 9 }, // Mão: Mùi·Hợi, Tuất
  thin: { tamHop: [7, 11], lucHop: 8 }, // Thìn: Thân·Tý, Dậu
  ti: { tamHop: [8, 12], lucHop: 7 }, // Tỵ: Dậu·Sửu, Thân
  ngo: { tamHop: [1, 9], lucHop: 6 }, // Ngọ: Dần·Tuất, Mùi
  mui: { tamHop: [2, 10], lucHop: 5 }, // Mùi: Mão·Hợi, Ngọ
  than: { tamHop: [3, 11], lucHop: 4 }, // Thân: Thìn·Tý, Tỵ
  dau: { tamHop: [4, 12], lucHop: 3 }, // Dậu: Tỵ·Sửu, Thìn
  tuat: { tamHop: [1, 5], lucHop: 2 }, // Tuất: Dần·Ngọ, Mão
  hoi: { tamHop: [2, 6], lucHop: 1 }, // Hợi: Mão·Mùi, Dần
};

export function thangCatFor(diaChi: DiaChi): ThangCatRow {
  return THANG_CAT[diaChi];
}
