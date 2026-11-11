import type { PreviewLasoRequest } from "@/lib/api/schemas";

/**
 * The bridge between what the user picks and what the backend accepts.
 *
 * The time picker works in hour + AM/PM because that is how people know their
 * birth time. The backend wants an integer hour 0–23. Tử vi an sao theo canh
 * giờ (two-hour blocks), so the mapping sends the *midpoint* of the canh giờ —
 * always an even hour — which can never sit on a block boundary.
 *
 * There is no minute anywhere in here on purpose: canh-giờ boundaries fall on
 * odd hours, so the picked hour alone decides the block and a minute could
 * only ever suggest a precision the reading does not have.
 *
 * Giờ Tý (23:00–01:00) crosses midnight, and by convention belongs to the
 * coming day: an 11 PM pick is sent as hour 0 of the next calendar day, using
 * real date arithmetic (month and year roll over correctly).
 */

export const MERIDIEM = { AM: "AM", PM: "PM" } as const;
export type Meridiem = (typeof MERIDIEM)[keyof typeof MERIDIEM];

export interface CanhGio {
  readonly chi: string;
  readonly range: string;
}

/** Indexed by canh order, Tý first — the same order the clock face shows. */
const CANH_GIO_TABLE: readonly CanhGio[] = [
  { chi: "Tý", range: "23:00 – 01:00" },
  { chi: "Sửu", range: "01:00 – 03:00" },
  { chi: "Dần", range: "03:00 – 05:00" },
  { chi: "Mão", range: "05:00 – 07:00" },
  { chi: "Thìn", range: "07:00 – 09:00" },
  { chi: "Tỵ", range: "09:00 – 11:00" },
  { chi: "Ngọ", range: "11:00 – 13:00" },
  { chi: "Mùi", range: "13:00 – 15:00" },
  { chi: "Thân", range: "15:00 – 17:00" },
  { chi: "Dậu", range: "17:00 – 19:00" },
  { chi: "Tuất", range: "19:00 – 21:00" },
  { chi: "Hợi", range: "21:00 – 23:00" },
];

export interface BirthDateInput {
  readonly year: number;
  readonly month: number;
  readonly day: number;
}

export interface BirthTimeInput {
  /** 1–12, as shown on the clock face. */
  readonly hour12: number;
  readonly meridiem: Meridiem;
}

/** The year picker's ceiling; the backend rejects anything beyond 2099. */
export const MAX_BIRTH_YEAR = 2099;

export function toHour24(hour12: number, meridiem: Meridiem): number {
  if (meridiem === MERIDIEM.AM) return hour12 === 12 ? 0 : hour12;
  return hour12 === 12 ? 12 : hour12 + 12;
}

function canhIndex(hour24: number): number {
  // Tý covers 23 and 0, so shifting by one makes every block contiguous:
  // 23,0 → 0; 1,2 → 1; 3,4 → 2; …
  return Math.floor(((hour24 + 1) % 24) / 2);
}

/** The canh giờ a picked time falls in — for the readout and confirm dialog. */
export function canhGioOf(hour12: number, meridiem: Meridiem): CanhGio {
  const canh = CANH_GIO_TABLE[canhIndex(toHour24(hour12, meridiem))];
  if (canh === undefined) throw new RangeError("hour12 out of range");
  return canh;
}

export type ApiBirthTime =
  | { readonly ok: true; readonly value: Omit<PreviewLasoRequest, "calendar"> }
  | { readonly ok: false; readonly reason: "year-overflow" };

/**
 * Map a picked date + time to the API birth fields (minus `calendar`, which
 * callers add, and minus `gender`, which only the build call needs).
 *
 * The hour sent is the canh-giờ midpoint; a 23:xx pick rolls the date to the
 * next day with hour 0. Rolling 31/12/2099 forward exceeds the backend's year
 * ceiling, so that single edge fails closed instead of issuing a doomed call.
 */
export function toApiBirthTime(date: BirthDateInput, time: BirthTimeInput): ApiBirthTime {
  const hour24 = toHour24(time.hour12, time.meridiem);
  const apiHour = (canhIndex(hour24) * 2) % 24;

  let { year, month, day } = date;
  if (hour24 === 23) {
    // UTC keeps DST out of date arithmetic.
    const rolled = new Date(Date.UTC(year, month - 1, day));
    rolled.setUTCDate(rolled.getUTCDate() + 1);
    year = rolled.getUTCFullYear();
    month = rolled.getUTCMonth() + 1;
    day = rolled.getUTCDate();
  }

  if (year > MAX_BIRTH_YEAR) return { ok: false, reason: "year-overflow" };
  return { ok: true, value: { year, month, day, hour: apiHour } };
}
