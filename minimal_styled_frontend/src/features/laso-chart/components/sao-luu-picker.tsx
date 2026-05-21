'use client';

import { useState } from 'react';
import { Loader2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { DateInput } from '@/components/shared/date-input';
import { GenderControl } from '@/components/shared/gender-control';
import { HourSelect } from '@/components/shared/hour-select';
import { MinuteSelect } from '@/components/shared/minute-select';
import { useBuildSaoLuu } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import { useChartStore } from '@/store/chart-store';
import type { Gender } from '@/lib/api/schemas';

interface Draft {
  dateOf: Date | undefined;
  hourOf: number | undefined;
  minuteOf: number | undefined;
  gender: Gender;
}

export function SaoLuuPicker() {
  const setOverlay = useChartStore((s) => s.setSaoLuuOverlay);
  const clearOverlay = useChartStore((s) => s.clearSaoLuu);
  const overlay = useChartStore((s) => s.saoLuuOverlay);
  const lastInput = useChartStore((s) => s.lastInput);

  const [values, setValues] = useState<Draft>(() => ({
    dateOf: new Date(),
    hourOf: 8,
    minuteOf: 0,
    gender: lastInput?.gender ?? 'M',
  }));
  const [error, setError] = useState<string | null>(null);

  const mutation = useBuildSaoLuu();

  const onSubmit: React.FormEventHandler<HTMLFormElement> = (e) => {
    e.preventDefault();
    setError(null);
    if (!values.dateOf || values.hourOf === undefined) {
      setError('Vui lòng chọn ngày và giờ quan sát.');
      return;
    }
    mutation.mutate(
      {
        observation_time: {
          date: values.dateOf.getDate(),
          month: values.dateOf.getMonth() + 1,
          year: values.dateOf.getFullYear(),
          hour: values.hourOf,
          gender: values.gender,
        },
      },
      {
        onSuccess: (res) => setOverlay(res),
        onError: (err) => setError(isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.'),
      },
    );
  };

  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle className="text-sm">Sao lưu</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex flex-col gap-3" noValidate>
          <FieldGroup>
            <div className="grid grid-cols-2 gap-3">
              <Field>
                <FieldLabel htmlFor="sl-date">Ngày quan sát</FieldLabel>
                <DateInput
                  id="sl-date"
                  value={values.dateOf}
                  onChange={(d) => setValues((p) => ({ ...p, dateOf: d }))}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="sl-hour">Giờ : Phút</FieldLabel>
                <div className="grid grid-cols-2 gap-2">
                  <HourSelect
                    id="sl-hour"
                    value={values.hourOf}
                    onChange={(h) => setValues((p) => ({ ...p, hourOf: h }))}
                  />
                  <MinuteSelect
                    id="sl-minute"
                    value={values.minuteOf}
                    onChange={(m) => setValues((p) => ({ ...p, minuteOf: m }))}
                  />
                </div>
              </Field>
            </div>
            <Field>
              <FieldLabel htmlFor="sl-gender">Giới tính</FieldLabel>
              <GenderControl
                id="sl-gender"
                value={values.gender}
                onChange={(g) => setValues((p) => ({ ...p, gender: g }))}
              />
            </Field>
          </FieldGroup>

          {error && <div className="text-xs text-destructive">{error}</div>}

          <div className="flex items-center gap-2">
            <Button type="submit" size="sm" disabled={mutation.isPending}>
              {mutation.isPending ? (
                <>
                  <Loader2 className="size-3.5 animate-spin" /> Đang tính…
                </>
              ) : (
                'Áp dụng sao lưu'
              )}
            </Button>
            {overlay && (
              <Button type="button" size="sm" variant="ghost" onClick={clearOverlay}>
                <X className="size-3.5" /> Xóa sao lưu
              </Button>
            )}
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
