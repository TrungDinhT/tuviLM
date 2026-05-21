'use client';

import { useState } from 'react';
import { Loader2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useBuildSaoLuu } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import { useChartStore } from '@/store/chart-store';
import {
  BirthFormSchema,
  toBirthInput,
  type BirthFormValues,
} from '@/features/birth-input/schema';

const DEFAULT_TIME: BirthFormValues = {
  dateOf: new Date().toISOString().slice(0, 10),
  timeOf: '08:00',
  gender: 'F',
};

export function SaoLuuPicker() {
  const setOverlay = useChartStore((s) => s.setSaoLuuOverlay);
  const clearOverlay = useChartStore((s) => s.clearSaoLuu);
  const overlay = useChartStore((s) => s.saoLuuOverlay);
  const lastInput = useChartStore((s) => s.lastInput);

  const [values, setValues] = useState<BirthFormValues>(() => ({
    ...DEFAULT_TIME,
    gender: lastInput?.gender ?? 'F',
  }));
  const [error, setError] = useState<string | null>(null);

  const mutation = useBuildSaoLuu();

  const update = <K extends keyof BirthFormValues>(key: K, value: BirthFormValues[K]) => {
    setValues((prev) => ({ ...prev, [key]: value }));
  };

  const onSubmit: React.FormEventHandler<HTMLFormElement> = (e) => {
    e.preventDefault();
    setError(null);
    const parsed = BirthFormSchema.safeParse(values);
    if (!parsed.success) {
      setError(parsed.error.issues[0]?.message ?? 'Dữ liệu không hợp lệ.');
      return;
    }
    const input = toBirthInput(parsed.data);
    mutation.mutate(
      {
        observation_time: {
          date: input.date,
          month: input.month,
          year: input.year,
          hour: input.hour,
          gender: input.gender,
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
                <Input
                  id="sl-date"
                  type="date"
                  value={values.dateOf}
                  onChange={(e) => update('dateOf', e.target.value)}
                />
              </Field>
              <Field>
                <FieldLabel htmlFor="sl-time">Giờ</FieldLabel>
                <Input
                  id="sl-time"
                  type="time"
                  value={values.timeOf}
                  onChange={(e) => update('timeOf', e.target.value)}
                />
              </Field>
            </div>
            <Field>
              <FieldLabel htmlFor="sl-gender">Giới tính</FieldLabel>
              <Select
                value={values.gender}
                onValueChange={(v) => update('gender', v as 'M' | 'F')}
              >
                <SelectTrigger id="sl-gender">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="F">Nữ</SelectItem>
                  <SelectItem value="M">Nam</SelectItem>
                </SelectContent>
              </Select>
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
