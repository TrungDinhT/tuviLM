'use client';

import { useQuery } from '@tanstack/react-query';
import { Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { analyzeStrengthWeakness } from '@/lib/api/client';
import { BuildLasoRequestSchema, type CapabilityProfile } from '@/lib/api/schemas';
import { apiErrorMessage, isApiError } from '@/lib/http/errors';
import { useChartStore } from '@/store/chart-store';

const weaknessLabels = {
  han_che_truc_tiep: 'Hạn chế trực tiếp',
  qua_da: 'Biểu hiện quá đà',
  xung_dot: 'Xung đột khuynh hướng',
};

export function StrengthWeaknessPanel() {
  const input = useChartStore((state) => state.lastInput);
  const current = useChartStore((state) => state.current);
  const ownerId = useChartStore((state) => state.ownerId);
  const parsed = BuildLasoRequestSchema.safeParse(
    input && {
      calendar: input.calendar ?? 'solar',
      day: input.date,
      month: input.month,
      year: input.year,
      gender: input.gender,
      ...(input.calendar === 'lunar'
        ? { hour_in_dia_chi: input.hour_in_dia_chi, is_leap_month: input.is_leap_month ?? false }
        : { hour: input.hour }),
    },
  );
  const birth = parsed.success ? parsed.data : null;
  const report = useQuery({
    queryKey: ['strength-weakness', ownerId, birth],
    queryFn: () => {
      if (!birth) throw new Error('Thiếu thông tin ngày giờ sinh');
      return analyzeStrengthWeakness(birth);
    },
    // Analysis is requested explicitly; mounting either panel never spends a model call.
    enabled: false,
    staleTime: Infinity,
    gcTime: 30 * 60 * 1000,
    retry: false,
  });

  if (!current || !birth) return null;

  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Sparkles className="size-4" aria-hidden="true" />
          Điểm mạnh và điểm cần lưu ý
        </CardTitle>
        <CardDescription>Khám phá năng lực từ lá số của bạn.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {report.data ? (
          <CapabilityReport report={report.data} />
        ) : (
          <>
            {report.isFetching && (
              <p role="status" className="text-muted-foreground text-sm">
                Đang phân tích năng lực. Quá trình này có thể mất một chút thời gian…
              </p>
            )}
            {report.isError && !report.isFetching && (
              <p role="alert" className="text-destructive text-sm">
                {isApiError(report.error)
                  ? apiErrorMessage(report.error)
                  : 'Chưa thể phân tích năng lực. Vui lòng thử lại.'}
              </p>
            )}
            <Button
              type="button"
              variant="outline"
              className="w-full"
              disabled={report.isFetching}
              onClick={() => void report.refetch({ cancelRefetch: false })}
            >
              {report.isFetching
                ? 'Đang phân tích…'
                : report.isError
                  ? 'Thử lại'
                  : 'Khám phá năng lực'}
            </Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}

function CapabilityReport({ report }: { report: CapabilityProfile }) {
  return (
    <div className="space-y-5">
      <p className="text-sm leading-relaxed whitespace-pre-line">{report.tong_quan}</p>
      <section className="space-y-2" aria-label="Điểm mạnh">
        <h3 className="text-sm font-semibold">Điểm mạnh</h3>
        {report.diem_manh.length === 0 && (
          <p className="text-muted-foreground text-sm">
            Chưa có đủ căn cứ để chọn điểm mạnh nổi bật.
          </p>
        )}
        {report.diem_manh.map((finding) => (
          <Finding key={finding.nang_luc_id} title={finding.nang_luc} {...finding} />
        ))}
      </section>
      <section className="space-y-2" aria-label="Điểm cần lưu ý">
        <h3 className="text-sm font-semibold">Điểm cần lưu ý</h3>
        {report.diem_yeu.length === 0 && (
          <p className="text-muted-foreground text-sm">
            Chưa có đủ căn cứ để chọn hạn chế nổi bật.
          </p>
        )}
        {report.diem_yeu.map((finding, index) => (
          <Finding
            key={`${finding.ten}:${index}`}
            title={finding.ten}
            label={weaknessLabels[finding.loai]}
            {...finding}
          />
        ))}
      </section>
    </div>
  );
}

function Finding({
  title,
  label,
  mo_ta,
  giai_thich,
}: {
  title: string;
  label?: string;
  mo_ta: string;
  giai_thich: string;
}) {
  return (
    <article className="border-border space-y-2 rounded-lg border p-3">
      <h4 className="text-sm font-medium">{title}</h4>
      {label && <p className="text-muted-foreground text-xs">{label}</p>}
      <p className="text-sm leading-relaxed whitespace-pre-line">{mo_ta}</p>
      <details className="text-sm">
        <summary className="text-primary focus-visible:outline-ring cursor-pointer rounded-sm font-medium focus-visible:outline-2">
          Xem luận giải
        </summary>
        <p className="text-muted-foreground mt-2 leading-relaxed whitespace-pre-line">
          {giai_thich}
        </p>
      </details>
    </article>
  );
}
