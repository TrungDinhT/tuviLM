import { z } from 'zod';
import { GenderSchema, type BuildLasoRequest } from '@/lib/api/schemas';
import type { BirthInput } from '@/store/chart-store';

export const BirthFormSchema = z
  .object({
    name: z.string().optional(),
    place: z.string().optional(),
    dateOf: z.string().regex(/^\d{4}-\d{2}-\d{2}$/, 'Ngày sinh không hợp lệ.'),
    timeOf: z.string().regex(/^\d{2}:\d{2}$/, 'Giờ sinh không hợp lệ.'),
    gender: GenderSchema,
  })
  .superRefine((value, ctx) => {
    const [y, m, d] = value.dateOf.split('-').map(Number) as [number, number, number];
    if (y < 1900 || y > 2099) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['dateOf'],
        message: 'Năm sinh phải nằm trong khoảng 1900–2099.',
      });
    }
    if (m < 1 || m > 12 || d < 1 || d > 31) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['dateOf'],
        message: 'Ngày sinh không hợp lệ.',
      });
    }
  });

export type BirthFormValues = z.infer<typeof BirthFormSchema>;

export function toBirthInput(values: BirthFormValues): BirthInput {
  const [y, m, d] = values.dateOf.split('-').map(Number) as [number, number, number];
  const [hh] = values.timeOf.split(':').map(Number) as [number, number];
  return {
    date: d,
    month: m,
    year: y,
    hour: hh,
    gender: values.gender,
    name: values.name?.trim() || undefined,
    place: values.place?.trim() || undefined,
  };
}

export function toApiRequest(input: BirthInput): BuildLasoRequest {
  return {
    date: input.date,
    month: input.month,
    year: input.year,
    hour: input.hour,
    gender: input.gender,
  };
}

export function fromBirthInput(input: BirthInput): BirthFormValues {
  const dateOf = `${input.year.toString().padStart(4, '0')}-${input.month.toString().padStart(2, '0')}-${input.date.toString().padStart(2, '0')}`;
  const timeOf = `${input.hour.toString().padStart(2, '0')}:00`;
  return {
    name: input.name,
    place: input.place,
    dateOf,
    timeOf,
    gender: input.gender,
  };
}
