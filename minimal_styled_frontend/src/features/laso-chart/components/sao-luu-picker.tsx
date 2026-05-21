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
  const [error, setError] = useState<string | null>(null);

  const mutation = useBuildSaoLuu();
  const { mutate } = mutation;

  useEffect(() => {
    const parsed = Number(year);
    if (!Number.isInteger(parsed) || parsed < 1900 || parsed > 2099) {
      setError(year === '' ? null : 'Vui lòng nhập năm hợp lệ (1900–2099).');
      return;
    }
    setError(null);
    const handle = setTimeout(() => {
      mutate(
        {
          observation_time: {
            date: 1,
            month: 1,
            year: parsed,
            hour: 0,
            gender: lastInput?.gender ?? 'M',
          },
        },
        {
          onSuccess: (res) => setOverlay(res),
          onError: (err) =>
            setError(isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.'),
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
              onChange={(e) => setYear(e.target.value)}
            />
          </Field>
        </FieldGroup>

        {error && <div className="mt-3 text-xs text-destructive">{error}</div>}
      </CardContent>
    </Card>
  );
}
