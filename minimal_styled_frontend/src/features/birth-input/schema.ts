import { z } from 'zod';
import {
  DiaChiSchema,
  GenderSchema,
  type BuildLasoRequest,
  type DiaChiId,
} from '@/lib/api/schemas';
import type { BirthInput } from '@/store/chart-store';

export const DIA_CHI_HOURS: { value: DiaChiId; label: string; range: string }[] = [
  { value: 'ty', label: 'Tý', range: '23:00-00:59' },
  { value: 'suu', label: 'Sửu', range: '01:00-02:59' },
  { value: 'dan', label: 'Dần', range: '03:00-04:59' },
  { value: 'meo', label: 'Mão', range: '05:00-06:59' },
  { value: 'thin', label: 'Thìn', range: '07:00-08:59' },
  { value: 'ti', label: 'Tỵ', range: '09:00-10:59' },
  { value: 'ngo', label: 'Ngọ', range: '11:00-12:59' },
  { value: 'mui', label: 'Mùi', range: '13:00-14:59' },
  { value: 'than', label: 'Thân', range: '15:00-16:59' },
  { value: 'dau', label: 'Dậu', range: '17:00-18:59' },
  { value: 'tuat', label: 'Tuất', range: '19:00-20:59' },
  { value: 'hoi', label: 'Hợi', range: '21:00-22:59' },
];

export const BirthFormSchema = z
  .object({
    calendar: z.enum(['solar', 'lunar']).default('solar'),
    name: z.string().optional(),
    dateOf: z
      .date({
        required_error: 'Vui lòng chọn ngày sinh.',
        invalid_type_error: 'Vui lòng chọn ngày sinh.',
      })
      .optional(),
    lunarDay: z.number().int().min(1).max(31).default(1),
    lunarMonth: z.number().int().min(1).max(12).default(1),
    lunarYear: z.number().int().min(1900).max(2099).default(1990),
    hourInDiaChi: DiaChiSchema.default('ty'),
    isLeapMonth: z.boolean().default(false),
    hourOf: z
      .number({
        required_error: 'Vui lòng chọn giờ sinh.',
        invalid_type_error: 'Vui lòng chọn giờ sinh.',
      })
      .int()
      .min(0)
      .max(23),
    minuteOf: z
      .number({
        required_error: 'Vui lòng chọn phút sinh.',
        invalid_type_error: 'Vui lòng chọn phút sinh.',
      })
      .int()
      .min(0)
      .max(59),
    gender: GenderSchema,
  })
  .superRefine((values, ctx) => {
    if (values.calendar !== 'solar') return;
    if (!values.dateOf) {
      ctx.addIssue({
        code: 'custom',
        path: ['dateOf'],
        message: 'Vui lòng chọn ngày sinh.',
      });
      return;
    }
    if (values.dateOf.getFullYear() < 1900 || values.dateOf.getFullYear() > 2099) {
      ctx.addIssue({
        code: 'custom',
        path: ['dateOf'],
        message: 'Năm sinh phải nằm trong khoảng 1900–2099.',
      });
    }
  });

export type BirthFormValues = z.infer<typeof BirthFormSchema>;

export function toBirthInput(values: BirthFormValues): BirthInput {
  if (values.calendar === 'lunar') {
    return {
      calendar: 'lunar',
      date: values.lunarDay,
      month: values.lunarMonth,
      year: values.lunarYear,
      hour_in_dia_chi: values.hourInDiaChi,
      is_leap_month: values.isLeapMonth,
      gender: values.gender,
      name: values.name?.trim() || undefined,
    };
  }

  if (!values.dateOf) {
    throw new Error('Solar birth date is required');
  }
  return {
    calendar: 'solar',
    date: values.dateOf.getDate(),
    month: values.dateOf.getMonth() + 1,
    year: values.dateOf.getFullYear(),
    hour: values.hourOf,
    // Note: minute is collected for UX precision but not sent — the backend's
    // BuildLasoRequest only carries hour, and Tử Vi giờ boundaries fall on
    // odd hours (e.g. 14:59 = Mùi, 15:00 = Thân) so the hour value already
    // determines the canh giờ correctly.
    gender: values.gender,
    name: values.name?.trim() || undefined,
  };
}

export function toApiRequest(input: BirthInput): BuildLasoRequest {
  if (input.calendar === 'lunar') {
    return {
      calendar: 'lunar',
      day: input.date,
      month: input.month,
      year: input.year,
      hour_in_dia_chi: input.hour_in_dia_chi ?? 'ty',
      is_leap_month: input.is_leap_month ?? false,
      gender: input.gender,
    };
  }
  return {
    calendar: 'solar',
    day: input.date,
    month: input.month,
    year: input.year,
    hour: input.hour ?? 0,
    gender: input.gender,
  };
}

export function fromBirthInput(input: BirthInput): Partial<BirthFormValues> {
  if (input.calendar === 'lunar') {
    return {
      name: input.name,
      calendar: 'lunar',
      lunarDay: input.date,
      lunarMonth: input.month,
      lunarYear: input.year,
      hourInDiaChi: input.hour_in_dia_chi ?? 'ty',
      isLeapMonth: input.is_leap_month ?? false,
      hourOf: 0,
      minuteOf: 0,
      gender: input.gender,
    };
  }
  return {
    name: input.name,
    calendar: 'solar',
    dateOf: new Date(input.year, input.month - 1, input.date),
    hourOf: input.hour ?? 0,
    // We don't persist the minute (backend doesn't carry it), so the form
    // defaults to `0` on prefill.
    minuteOf: 0,
    gender: input.gender,
  };
}

export function canChiForYear(year: number): string {
  const can = ['Canh', 'Tân', 'Nhâm', 'Quý', 'Giáp', 'Ất', 'Bính', 'Đinh', 'Mậu', 'Kỷ'];
  const chi = ['Thân', 'Dậu', 'Tuất', 'Hợi', 'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tỵ', 'Ngọ', 'Mùi'];
  return `${can[mod(year, 10)]} ${chi[mod(year, 12)]}`;
}

export function diaChiHourLabel(value: DiaChiId | undefined): string {
  return DIA_CHI_HOURS.find((option) => option.value === value)?.label ?? '';
}

function mod(value: number, divisor: number): number {
  return ((value % divisor) + divisor) % divisor;
}
