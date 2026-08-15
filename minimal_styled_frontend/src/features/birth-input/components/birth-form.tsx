'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowRight, Info, Loader2 } from 'lucide-react';
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
import { useBuildLaso, useCreateChartSession } from '@/lib/api/hooks';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import { useChartStore } from '@/store/chart-store';
import type { BuildLasoResponse, DiaChiId, Gender } from '@/lib/api/schemas';
import {
  BirthFormSchema,
  canChiForYear,
  DIA_CHI_HOURS,
  toApiRequest,
  toBirthInput,
} from '../schema';

interface DraftValues {
  calendar: 'solar' | 'lunar';
  name: string;
  dateOf: Date | undefined;
  lunarDay: number;
  lunarMonth: number;
  lunarYear: number;
  hourInDiaChi: DiaChiId;
  isLeapMonth: boolean;
  hourOf: number | undefined;
  minuteOf: number | undefined;
  gender: Gender;
}

type FieldErrors = Partial<Record<keyof DraftValues, string>>;

export function BirthForm() {
  const router = useRouter();
  const ownerId = useChartStore((s) => s.ownerId);
  const setConversationContext = useChartStore((s) => s.setConversationContext);
  const setCurrent = useChartStore((s) => s.setCurrent);

  // Landing form always renders in default state — no prefill from the store,
  // even when a previous chart exists.
  const [values, setValues] = useState<DraftValues>(() => ({
    calendar: 'solar',
    name: '',
    dateOf: undefined,
    lunarDay: 1,
    lunarMonth: 1,
    lunarYear: 1990,
    hourInDiaChi: 'ty',
    isLeapMonth: false,
    hourOf: 0,
    minuteOf: 0,
    gender: 'M',
  }));
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitError, setSubmitError] = useState<string | null>(null);

  const mutation = useBuildLaso();
  const sessionMutation = useCreateChartSession();

  const update = <K extends keyof DraftValues>(key: K, value: DraftValues[K]) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    if (errors[key]) setErrors((prev) => ({ ...prev, [key]: undefined }));
  };

  const handleBuildSuccess = (input: ReturnType<typeof toBirthInput>, response: BuildLasoResponse) => {
    setCurrent(input, response);
    router.push('/chat');
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
    const apiInput = toApiRequest(input);
    const displayName = input.name ?? 'Không tên';
    sessionMutation.mutate(
      { ownerId, displayName, birthInfo: apiInput },
      {
        onSuccess: ({ ownerId, chartProfileId, sessionId }) => {
          setConversationContext(ownerId, chartProfileId, sessionId);
          mutation.mutate(apiInput, {
            onSuccess: (response) => handleBuildSuccess(input, response),
            onError: (err) => {
              setSubmitError(isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.');
            },
          });
        },
        onError: (err) => {
          setSubmitError(isApiError(err) ? apiErrorMessage(err) : 'Đã có lỗi xảy ra.');
        },
      },
    );
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
          <FieldGroup className='pb-4'>
            <Field>
              <FieldLabel htmlFor="b-name">Tên gọi</FieldLabel>
              <Input
                id="b-name"
                value={values.name}
                onChange={(e) => update('name', e.target.value)}
                placeholder="Tên đầy đủ"
              />
            </Field>

            <Field>
              <FieldLabel>Lịch sinh</FieldLabel>
              <div className="grid grid-cols-2 gap-2">
                <Button
                  type="button"
                  variant={values.calendar === 'solar' ? 'default' : 'outline'}
                  onClick={() => update('calendar', 'solar')}
                >
                  Dương lịch
                </Button>
                <Button
                  type="button"
                  variant={values.calendar === 'lunar' ? 'default' : 'outline'}
                  onClick={() => update('calendar', 'lunar')}
                >
                  Âm lịch
                </Button>
              </div>
              {values.calendar === 'lunar' && <LunarInfo />}
            </Field>

            <div className="grid gap-5 sm:grid-cols-2">
              {values.calendar === 'solar' ? (
                <Field data-invalid={errors.dateOf ? '' : undefined}>
                  <FieldLabel htmlFor="b-date">Ngày sinh (dương lịch)</FieldLabel>
                  <DateInput
                    id="b-date"
                    value={values.dateOf}
                    onChange={(d) => update('dateOf', d)}
                  />
                  {errors.dateOf && <FieldError>{errors.dateOf}</FieldError>}
                </Field>
              ) : (
                <Field>
                  <FieldLabel>Ngày sinh âm lịch</FieldLabel>
                  <div className="grid grid-cols-[1fr_1fr_1.4fr] gap-2">
                    <NumberInput
                      label="Ngày âm"
                      value={values.lunarDay}
                      min={1}
                      max={31}
                      onChange={(v) => update('lunarDay', v)}
                    />
                    <NumberInput
                      label="Tháng âm"
                      value={values.lunarMonth}
                      min={1}
                      max={12}
                      onChange={(v) => update('lunarMonth', v)}
                    />
                    <NumberInput
                      label="Năm âm"
                      value={values.lunarYear}
                      min={1900}
                      max={2099}
                      onChange={(v) => update('lunarYear', v)}
                    />
                  </div>
                  <div className="mt-2 flex items-center justify-between gap-3 text-xs text-muted-foreground">
                    <span>
                      Năm âm:{' '}
                      <span className="font-medium text-foreground">
                        {canChiForYear(values.lunarYear)}
                      </span>
                    </span>
                    <label className="flex items-center gap-1.5">
                      <input
                        type="checkbox"
                        checked={values.isLeapMonth}
                        onChange={(e) => update('isLeapMonth', e.target.checked)}
                      />
                      Tháng nhuận
                    </label>
                  </div>
                </Field>
              )}
              <Field data-invalid={errors.hourOf || errors.minuteOf ? '' : undefined}>
                <FieldLabel htmlFor="b-hour">Giờ sinh</FieldLabel>
                {values.calendar === 'lunar' ? (
                  <DiaChiHourSelect
                    id="b-hour"
                    value={values.hourInDiaChi}
                    onChange={(v) => update('hourInDiaChi', v)}
                  />
                ) : (
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
                )}
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
          <Button
            type="submit"
            size="lg"
            disabled={sessionMutation.isPending || mutation.isPending}
          >
            {sessionMutation.isPending || mutation.isPending ? (
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

function LunarInfo() {
  return (
    <details className="text-xs text-muted-foreground">
      <summary className="flex cursor-pointer items-center gap-1">
        <Info className="size-3.5" />
        Năm âm có thể khác năm dương
      </summary>
      <p className="mt-1 leading-relaxed">
        Âm lịch cần đúng năm âm. Ví dụ 01/01/1990 dương lịch có thể vẫn thuộc
        tháng 12 năm Kỷ Tị 1989 âm lịch.
      </p>
    </details>
  );
}

function NumberInput({
  label,
  value,
  min,
  max,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  onChange: (value: number) => void;
}) {
  return (
    <Input
      aria-label={label}
      type="number"
      min={min}
      max={max}
      value={value}
      onChange={(e) => onChange(Number(e.target.value))}
    />
  );
}

function DiaChiHourSelect({
  id,
  value,
  onChange,
}: {
  id: string;
  value: DiaChiId;
  onChange: (value: DiaChiId) => void;
}) {
  return (
    <select
      id={id}
      value={value}
      onChange={(e) => onChange(e.target.value as DiaChiId)}
      className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50"
    >
      {DIA_CHI_HOURS.map((option) => (
        <option key={option.value} value={option.value}>
          {option.label} ({option.range})
        </option>
      ))}
    </select>
  );
}
