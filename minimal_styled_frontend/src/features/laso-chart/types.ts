import type { Cung } from '@/lib/api/schemas';

/**
 * Canonical 4×4 grid coordinates for the 12 cung. The order follows the
 * Tử Vi convention: counter-clockwise from Mệnh, with Mệnh at top-center-left
 * (row 1, col 2) per the design's CHART_LAYOUT in tuvi-v2.
 */
export const CUNG_GRID: Array<{
  row: 1 | 2 | 3 | 4;
  col: 1 | 2 | 3 | 4;
  position: string;
}> = [
  { row: 1, col: 1, position: 'Huynh Đệ' },
  { row: 1, col: 2, position: 'Mệnh' },
  { row: 1, col: 3, position: 'Phụ Mẫu' },
  { row: 1, col: 4, position: 'Phúc Đức' },
  { row: 2, col: 4, position: 'Điền Trạch' },
  { row: 3, col: 4, position: 'Quan Lộc' },
  { row: 4, col: 4, position: 'Nô Bộc' },
  { row: 4, col: 3, position: 'Thiên Di' },
  { row: 4, col: 2, position: 'Tật Ách' },
  { row: 4, col: 1, position: 'Tài Bạch' },
  { row: 3, col: 1, position: 'Tử Tức' },
  { row: 2, col: 1, position: 'Phu Thê' },
];

export interface CungCellData {
  cung: Cung;
  saoLuu: Cung['saoLuu'];
}
