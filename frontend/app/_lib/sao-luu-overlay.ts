import type {
  BuildLasoRequest,
  BuildLasoResponse,
  BuildSaoLuuResponse,
  DiaChiId,
  UserProfile,
} from "./types";

export const VIEW_YEAR_MIN = 1900;
export const VIEW_YEAR_MAX = 2099;
export const DEFAULT_VIEW_YEAR = 2026;

const CAN = ["Canh", "Tân", "Nhâm", "Quý", "Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ"] as const;
const CHI = ["Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi"] as const;

export const DIA_CHI_HOURS: { value: DiaChiId; label: string; range: string }[] = [
  { value: "ty", label: "Tý", range: "23:00 hôm trước - 00:59" },
  { value: "suu", label: "Sửu", range: "01:00 - 02:59" },
  { value: "dan", label: "Dần", range: "03:00 - 04:59" },
  { value: "meo", label: "Mão", range: "05:00 - 06:59" },
  { value: "thin", label: "Thìn", range: "07:00 - 08:59" },
  { value: "ti", label: "Tỵ", range: "09:00 - 10:59" },
  { value: "ngo", label: "Ngọ", range: "11:00 - 12:59" },
  { value: "mui", label: "Mùi", range: "13:00 - 14:59" },
  { value: "than", label: "Thân", range: "15:00 - 16:59" },
  { value: "dau", label: "Dậu", range: "17:00 - 18:59" },
  { value: "tuat", label: "Tuất", range: "19:00 - 20:59" },
  { value: "hoi", label: "Hợi", range: "21:00 - 22:59" },
];

export function buildRequestFromProfile(profile: UserProfile): BuildLasoRequest {
  const { day, month, year, gender } = profile;
  if (profile.calendar === "am") {
    return {
      calendar: "lunar",
      day,
      month,
      year,
      hour_in_dia_chi: profile.hour_in_dia_chi ?? "ty",
      is_leap_month: profile.is_leap_month ?? false,
      gender,
    };
  }
  return { calendar: "solar", day, month, year, hour: profile.hour ?? 0, gender };
}

export function canChiForYear(year: number): string {
  return `${CAN[mod(year, 10)]} ${CHI[mod(year, 12)]}`;
}

export function diaChiForYear(year: number): string {
  return CHI[mod(year, 12)];
}

export function diaChiHourLabel(value: DiaChiId | undefined): string {
  return DIA_CHI_HOURS.find((option) => option.value === value)?.label ?? "";
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
