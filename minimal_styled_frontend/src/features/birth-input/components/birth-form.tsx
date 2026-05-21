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
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useBuildLaso } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import { useChartStore, type HistoryEntry } from '@/store/chart-store';
import {
  BirthFormSchema,
  fromBirthInput,
  toApiRequest,
  toBirthInput,
  type BirthFormValues,
} from '../schema';

const EMPTY_VALUES: BirthFormValues = {
  name: '',
  place: '',
  dateOf: '',
  timeOf: '',
  gender: 'F',
};

type FieldErrors = Partial<Record<keyof BirthFormValues, string>>;

export function BirthForm() {
  const router = useRouter();
  const lastInput = useChartStore((s) => s.lastInput);
  const setCurrent = useChartStore((s) => s.setCurrent);
  const addToHistory = useChartStore((s) => s.addToHistory);

  const [values, setValues] = useState<BirthFormValues>(() =>
    lastInput ? fromBirthInput(lastInput) : EMPTY_VALUES,
  );
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);

  const mutation = useBuildLaso();

  const update = <K extends keyof BirthFormValues>(key: K, value: BirthFormValues[K]) => {
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
          next[key as keyof BirthFormValues] = issue.message;
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
          Cần ngày, giờ, nơi sinh chính xác để định cục mệnh.
        </CardDescription>
      </CardHeader>
      <form onSubmit={onSubmit} noValidate>
        <CardContent>
          <FieldGroup>
            <Field data-invalid={errors.name ? '' : undefined}>
              <FieldLabel htmlFor="b-name">Tên gọi</FieldLabel>
              <Input
                id="b-name"
                value={values.name ?? ''}
                onChange={(e) => update('name', e.target.value)}
                placeholder="Tên đầy đủ"
              />
            </Field>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field data-invalid={errors.dateOf ? '' : undefined}>
                <FieldLabel htmlFor="b-date">Ngày sinh (dương lịch)</FieldLabel>
                <Input
                  id="b-date"
                  type="date"
                  value={values.dateOf}
                  onChange={(e) => update('dateOf', e.target.value)}
                />
                {errors.dateOf && <FieldError>{errors.dateOf}</FieldError>}
              </Field>
              <Field data-invalid={errors.timeOf ? '' : undefined}>
                <FieldLabel htmlFor="b-time">Giờ sinh</FieldLabel>
                <Input
                  id="b-time"
                  type="time"
                  value={values.timeOf}
                  onChange={(e) => update('timeOf', e.target.value)}
                />
                {errors.timeOf && <FieldError>{errors.timeOf}</FieldError>}
              </Field>
            </div>

            <div className="grid gap-5 sm:grid-cols-2">
              <Field>
                <FieldLabel htmlFor="b-place">Nơi sinh</FieldLabel>
                <Input
                  id="b-place"
                  value={values.place ?? ''}
                  onChange={(e) => update('place', e.target.value)}
                  placeholder="Thành phố"
                />
              </Field>
              <Field data-invalid={errors.gender ? '' : undefined}>
                <FieldLabel htmlFor="b-gender">Giới tính</FieldLabel>
                <Select
                  value={values.gender}
                  onValueChange={(v) => update('gender', v as 'M' | 'F')}
                >
                  <SelectTrigger id="b-gender">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="F">Nữ</SelectItem>
                    <SelectItem value="M">Nam</SelectItem>
                  </SelectContent>
                </Select>
              </Field>
            </div>

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
