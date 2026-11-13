import { canhGioOf, MERIDIEM } from "@/features/an-sao/birth-time";
import type { BirthInfo, ChartProfile } from "@/lib/api/schemas";

/** Lower-case, without Vietnamese marks, so "me mai" finds "Mẹ Mai". */
export const normalize = (value: string): string =>
  value
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .replace(/đ/g, "d");

export const birthDetail = (birth: BirthInfo): string => {
  const canh = canhGioOf(birth.hour % 12 || 12, birth.hour < 12 ? MERIDIEM.AM : MERIDIEM.PM);
  return `Giờ ${canh.chi} · ${birth.gender === "M" ? "Nam" : "Nữ"}`;
};

const sameBirth = (a: BirthInfo, b: BirthInfo): boolean =>
  a.year === b.year &&
  a.month === b.month &&
  a.day === b.day &&
  a.hour === b.hour &&
  a.gender === b.gender;

/**
 * The saved profile of the chart on screen: by id when the chart was opened
 * from a profile, else by birth data (a chart cast before it was saved).
 */
export const findCurrentProfile = (
  saved: ChartProfile[],
  profileId: string | null,
  birth: BirthInfo,
): ChartProfile | undefined =>
  saved.find((profile) => profile.id === profileId) ??
  saved.find((profile) => sameBirth(profile.birth_info, birth));
