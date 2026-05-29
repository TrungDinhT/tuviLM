'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { useBuildSaoLuu } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import { useChartStore } from '@/store/chart-store';

export function SaoLuuPicker() {
  const setOverlay = useChartStore((s) => s.setSaoLuuOverlay);
  const lastInput = useChartStore((s) => s.lastInput);

  const [year, setYear] = useState<string>(() => new Date().getFullYear().toString());
  const [apiError, setApiError] = useState<string | null>(null);

  const mutation = useBuildSaoLuu();
  const { mutate } = mutation;

  const parsed = Number(year);
  const validationError =
    !Number.isInteger(parsed) || parsed < 1900 || parsed > 2099
      ? year === ''
        ? null
        : 'Vui lòng nhập năm hợp lệ (1900–2099).'
      : null;

  const displayError = validationError || apiError;

  useEffect(() => {
    const parsedYear = Number(year);
    if (!Number.isInteger(parsedYear) || parsedYear < 1900 || parsedYear > 2099) {
      return;
    }
    const handle = setTimeout(() => {
      setApiError(null);
      mutate(
        {
          observation_time: {
            date: 1,
            month: 1,
            year: parsedYear,
            hour: 0,
            gender: lastInput?.gender ?? 'M',
          },
        },
        {
          onSuccess: (res) => setOverlay(res),
          onError: (err) =>
            setApiError(isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.'),
        },
      );
    }, 300);
    return () => clearTimeout(handle);
  }, [year, lastInput?.gender, mutate, setOverlay]);

  return (
    <Card size="sm">
      <CardHeader></CardHeader>
      <CardContent>
        <FieldGroup>
          <Field className="flex-row">
            <FieldLabel htmlFor="sl-year">Xem năm</FieldLabel>
            <Input
              id="sl-year"
              type="number"
              inputMode="numeric"
              min={1800}
              max={2200}
              value={year}
              onChange={(e) => {
                setYear(e.target.value);
                setApiError(null);
              }}
            />
          </Field>
        </FieldGroup>

        {displayError && <div className="mt-3 text-xs text-destructive">{displayError}</div>}
      </CardContent>
    </Card>
  );
}
