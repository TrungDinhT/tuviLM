// Traditional Tử Vi layout: 12 địa chi around perimeter of a 4x4 grid,
// counter-clockwise from Tị (top-left). Center 2x2 holds the info card.

export const DIA_CHI_GRID: Record<string, { r: number; c: number }> = {
  "Tị":   { r: 0, c: 0 },
  "Ngọ":  { r: 0, c: 1 },
  "Mùi":  { r: 0, c: 2 },
  "Thân": { r: 0, c: 3 },
  "Dậu":  { r: 1, c: 3 },
  "Tuất": { r: 2, c: 3 },
  "Hợi":  { r: 3, c: 3 },
  "Tý":   { r: 3, c: 2 },
  "Sửu":  { r: 3, c: 1 },
  "Dần":  { r: 3, c: 0 },
  "Mão":  { r: 2, c: 0 },
  "Thìn": { r: 1, c: 0 },
};

export const DIA_CHI_ORDER = [
  "Tị", "Ngọ", "Mùi", "Thân",
  "Dậu", "Tuất",
  "Hợi", "Tý", "Sửu", "Dần",
  "Mão", "Thìn",
] as const;
