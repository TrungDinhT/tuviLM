import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { DemoBadge } from '@/components/shared/demo-badge';

const ASPECTS = [
  { key: 'tinh-than', label: 'Tinh thần', value: 82, note: 'Vững vàng' },
  { key: 'su-nghiep', label: 'Sự nghiệp', value: 67, note: 'Khởi sắc giữa năm' },
  { key: 'tai-loc', label: 'Tài lộc', value: 54, note: 'Cần kiên nhẫn' },
  { key: 'tinh-cam', label: 'Tình cảm', value: 71, note: 'Có biến chuyển' },
  { key: 'suc-khoe', label: 'Sức khỏe', value: 78, note: 'Ổn định' },
] as const;

export function AspectBars() {
  return (
    <Card size="sm">
      <CardHeader className="flex-row items-center justify-between">
        <CardTitle className="text-sm">Cát hung năm 2026</CardTitle>
        <DemoBadge />
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        {ASPECTS.map((a) => (
          <div key={a.key} className="flex flex-col gap-1.5">
            <div className="flex items-baseline justify-between gap-2 text-xs">
              <span className="whitespace-nowrap">{a.label}</span>
              <span className="font-mono tabular-nums text-muted-foreground">{a.value}</span>
            </div>
            <Progress value={a.value} />
            <div className="text-[11px] text-muted-foreground">{a.note}</div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
