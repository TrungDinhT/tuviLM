'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { DateInput } from '@/components/shared/date-input';
import { GenderControl } from '@/components/shared/gender-control';
import { HourSelect } from '@/components/shared/hour-select';
import { MinuteSelect } from '@/components/shared/minute-select';
import { useBuildLaso } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import { useChartStore, type HistoryEntry } from '@/store/chart-store';
import type { Gender } from '@/lib/api/schemas';
import { BirthFormSchema, toApiRequest, toBirthInput } from '../schema';

interface DraftValues {
  name: string;
  dateOf: Date | undefined;
  hourOf: number | undefined;
  minuteOf: number | undefined;
  gender: Gender;
}

type FieldErrors = Partial<Record<keyof DraftValues, string>>;

export function BirthForm() {
  const router = useRouter();
  const setCurrent = useChartStore((s) => s.setCurrent);
  const addToHistory = useChartStore((s) => s.addToHistory);

  // Landing form always renders in default state — no prefill from the store,
  // even when a previous chart exists. Submitting still writes to the store
  // and to history; this is read-side only.
  const [values, setValues] = useState<DraftValues>(() => ({
    name: '',
    dateOf: undefined,
    hourOf: 0,
    minuteOf: 0,
    gender: 'M',
  }));
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);

  const mutation = useBuildLaso();

  const update = <K extends keyof DraftValues>(key: K, value: DraftValues[K]) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    if (errors[key]) setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const onSubmit: React.FormEventHandler<HTMLFormElement> = (e) => {
    e.preventDefault();
    setSubmitError(null);
    const parsed = BirthFormSchema.safeParse(values);
    if (!parsed.success) {
      const next: FieldErrors = {};
      for (const issue of parsed.error.issues) {
        const key = issue.path[0];
        if (typeof key === 'string' && !(key in next)) {
          next[key as keyof DraftValues] = issue.message;
        }
      }
      setErrors(next);
      return;
    }
    const input = toBirthInput(parsed.data);
    mutation.mutate(toApiRequest(input), {
      onSuccess: (response) => {
        setCurrent(input, response);
        const entry: HistoryEntry = {
          id: response.id,
          builtAt: Date.now(),
          input,
          response,
        };
        addToHistory(entry);
        router.push('/chat');
      },
      onError: (err) => {
        setSubmitError(isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.');
      },
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Thông tin để an lá số</CardTitle>
        <CardDescription>
          Cần ngày, giờ sinh chính xác để định cục mệnh.
        </CardDescription>
      </CardHeader>
      <form onSubmit={onSubmit} noValidate>
        <CardContent>
          <FieldGroup>
            <Field>
              <FieldLabel htmlFor="b-name">Tên gọi</FieldLabel>
              <Input
                id="b-name"
                value={values.name}
                onChange={(e) => update('name', e.target.value)}
                placeholder="Tên đầy đủ"
              />
            </Field>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field data-invalid={errors.dateOf ? '' : undefined}>
                <FieldLabel htmlFor="b-date">Ngày sinh (dương lịch)</FieldLabel>
                <DateInput
                  id="b-date"
                  value={values.dateOf}
                  onChange={(d) => update('dateOf', d)}
                />
                {errors.dateOf && <FieldError>{errors.dateOf}</FieldError>}
              </Field>
              <Field data-invalid={errors.hourOf || errors.minuteOf ? '' : undefined}>
                <FieldLabel htmlFor="b-hour">Giờ sinh</FieldLabel>
                <div className="grid grid-cols-2 gap-2">
                  <HourSelect
                    id="b-hour"
                    value={values.hourOf}
                    onChange={(h) => update('hourOf', h)}
                  />
                  <MinuteSelect
                    id="b-minute"
                    value={values.minuteOf}
                    onChange={(m) => update('minuteOf', m)}
                  />
                </div>
                {(errors.hourOf || errors.minuteOf) && (
                  <FieldError>{errors.hourOf ?? errors.minuteOf}</FieldError>
                )}
              </Field>
            </div>

            <Field>
              <FieldLabel htmlFor="b-gender">Giới tính</FieldLabel>
              <GenderControl
                id="b-gender"
                value={values.gender}
                onChange={(g) => update('gender', g)}
              />
            </Field>

            <FieldDescription className="text-xs">
              Giờ sinh càng chính xác, lá số càng đúng. Sai số ±15 phút có thể đổi cục.
            </FieldDescription>

            {submitError && (
              <div className="rounded-md border border-destructive/40 bg-destructive/5 px-3 py-2 text-xs text-destructive">
                {submitError}
              </div>
            )}
          </FieldGroup>
        </CardContent>
        <CardFooter className="justify-between gap-3">
          <span className="text-xs text-muted-foreground">
            Thông tin chỉ dùng để an lá số cho bạn.
          </span>
          <Button type="submit" size="lg" disabled={mutation.isPending}>
            {mutation.isPending ? (
              <>
                <Loader2 className="size-4 animate-spin" />
                Đang an lá số…
              </>
            ) : (
              <>
                An lá số <ArrowRight className="size-4" />
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
