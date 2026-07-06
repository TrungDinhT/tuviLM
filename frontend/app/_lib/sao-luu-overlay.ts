import type {
  BuildLasoRequest,
  BuildLasoResponse,
  BuildSaoLuuResponse,
  UserProfile,
} from "./types";

export const VIEW_YEAR_MIN = 1900;
export const VIEW_YEAR_MAX = 2099;
export const DEFAULT_VIEW_YEAR = 2026;

const CAN = ["Canh", "Tân", "Nhâm", "Quý", "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ"] as const;
const CHI = ["Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi"] as const;

export function buildRequestFromProfile(profile: UserProfile): BuildLasoRequest {
  const { day, month, year, hour, gender } = profile;
  return { day, month, year, hour, gender };
}

export function canChiForYear(year: number): string {
  return `${CAN[mod(year, 10)]} ${CHI[mod(year, 12)]}`;
}

export function diaChiForYear(year: number): string {
  return CHI[mod(year, 12)];
}

export function formatViewYearLabel(year: number): string {
  return `${canChiForYear(year)} · ${year}`;
}

export function formatChartYearLabel(year: number): string {
  return `${year} ${canChiForYear(year)}`;
}

export function withSaoLuuOverlay(
  laso: BuildLasoResponse,
  overlay: BuildSaoLuuResponse,
): BuildLasoResponse {
  return {
    ...laso,
    cung_by_position: Object.fromEntries(
      Object.entries(laso.cung_by_position).map(([position, cung]) => [
        position,
        {
          ...cung,
          saoLuu: overlay.cung_by_position[position]?.saoLuu ?? [],
        },
      ]),
    ),
  };
}

function mod(value: number, divisor: number): number {
  return ((value % divisor) + divisor) % divisor;
}
