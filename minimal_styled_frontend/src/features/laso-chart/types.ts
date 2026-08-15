import type { Cung } from '@/lib/api/schemas';

/**
 * Canonical 4×4 grid coordinates for the 12 cung, keyed by địa chi name.
 *
 * Each `position` matches a key in `BuildLasoResponse.cung_by_position`
 * (see `api/_parse.py::to_cung_payload_map`, which keys by
 * `dia_chi_entity.name`). Roles like Mệnh/Huynh Đệ rotate per chart and
 * are NOT used as grid keys.
 *
 *   row 1: Tị   Ngọ  Mùi  Thân
 *   row 2: Thìn  ·    ·   Dậu
 *   row 3: Mão   ·    ·   Tuất
 *   row 4: Dần  Sửu  Tý   Hợi
 *
 * The central 2×2 (rows 2–3, cols 2–3) is occupied by `PersonalInfo`.
 */
export const CUNG_GRID: Array<{
  row: 1 | 2 | 3 | 4;
  col: 1 | 2 | 3 | 4;
  position: string;
}> = [
  { row: 1, col: 1, position: 'Tị' },
  { row: 1, col: 2, position: 'Ngọ' },
  { row: 1, col: 3, position: 'Mùi' },
  { row: 1, col: 4, position: 'Thân' },
  { row: 2, col: 4, position: 'Dậu' },
  { row: 3, col: 4, position: 'Tuất' },
  { row: 4, col: 4, position: 'Hợi' },
  { row: 4, col: 3, position: 'Tý' },
  { row: 4, col: 2, position: 'Sửu' },
  { row: 4, col: 1, position: 'Dần' },
  { row: 3, col: 1, position: 'Mão' },
  { row: 2, col: 1, position: 'Thìn' },
];

export interface CungCellData {
  cung: Cung;
  saoLuu: Cung['saoLuu'];
}
