export interface CalendarDate {
  readonly year: number;
  /** 1–12. */
  readonly month: number;
  readonly day: number;
}

export function daysInMonth(year: number, month: number): number {
  // Day 0 of the next month is the last day of this one.
  return new Date(Date.UTC(year, month, 0)).getUTCDate();
}

export function isRealDate({ year, month, day }: CalendarDate): boolean {
  return month >= 1 && month <= 12 && day >= 1 && day <= daysInMonth(year, month);
}
