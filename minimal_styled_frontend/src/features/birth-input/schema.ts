import { z } from 'zod';
import { GenderSchema, type BuildLasoRequest } from '@/lib/api/schemas';
import type { BirthInput } from '@/store/chart-store';

export const BirthFormSchema = z
  .object({
    name: z.string().optional(),
    dateOf: z
      .date({
        required_error: 'Vui lòng chọn ngày sinh.',
        invalid_type_error: 'Vui lòng chọn ngày sinh.',
      })
      .refine(
        (d) => d.getFullYear() >= 1900 && d.getFullYear() <= 2099,
        'Năm sinh phải nằm trong khoảng 1900–2099.',
      ),
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
  });

export type BirthFormValues = z.infer<typeof BirthFormSchema>;

export function toBirthInput(values: BirthFormValues): BirthInput {
  return {
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
  return {
    date: input.date,
    month: input.month,
    year: input.year,
    hour: input.hour,
    gender: input.gender,
  };
}

export function fromBirthInput(input: BirthInput): Partial<BirthFormValues> {
  return {
    name: input.name,
    dateOf: new Date(input.year, input.month - 1, input.date),
    hourOf: input.hour,
    // We don't persist the minute (backend doesn't carry it), so the form
    // defaults to `0` on prefill.
    minuteOf: 0,
    gender: input.gender,
  };
}
