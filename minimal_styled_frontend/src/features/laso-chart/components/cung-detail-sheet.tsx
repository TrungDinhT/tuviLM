'use client';

import { Badge } from '@/components/ui/badge';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { abbreviateStarStatus } from '@/lib/utils';
import { useChartStore } from '@/store/chart-store';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function CungDetailSheet({ open, onOpenChange }: Props) {
  const current = useChartStore((s) => s.current);
  const position = useChartStore((s) => s.selectedCungPosition);
  const saoLuuOverlay = useChartStore((s) => s.saoLuuOverlay);

  const cung = position && current ? current.cung_by_position[position] : null;
  const saoLuu = position && saoLuuOverlay ? saoLuuOverlay.cung_by_position[position]?.saoLuu : [];

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="flex w-full max-w-md flex-col gap-4 overflow-y-auto p-6">
        <SheetHeader className="gap-1 p-0">
          <SheetTitle>{cung?.position ?? 'Cung'}</SheetTitle>
          <SheetDescription>
            {cung?.role ?? 'Chi tiết cung'}
          </SheetDescription>
        </SheetHeader>

        {!cung ? (
          <div className="text-sm text-muted-foreground">Chưa chọn cung nào.</div>
        ) : (
          <div className="flex flex-col gap-4 text-sm">
            <div className="flex flex-wrap gap-1.5">
              {cung.is_cung_than && <Badge variant="secondary">Cung Thân</Badge>}
              {cung.is_tuan && <Badge variant="destructive">Tuần</Badge>}
              {cung.is_triet && <Badge variant="destructive">Triệt</Badge>}
              {typeof cung.age_daivan === 'number' && (
                <Badge variant="outline">Đại vận tuổi {cung.age_daivan}</Badge>
              )}
              {cung.trang_sinh && <Badge variant="outline">{cung.trang_sinh}</Badge>}
            </div>

            <Section title="Chính tinh">
              {cung.chinh_tinh.length === 0 ? (
                <Empty />
              ) : (
                <ul className="flex flex-col gap-0.5">
                  {cung.chinh_tinh.map((s) => (
                    <li key={s} className="font-medium">{abbreviateStarStatus(s)}</li>
                  ))}
                </ul>
              )}
            </Section>

            <Section title="Phụ tinh">
              {cung.phu_tinh.length === 0 ? (
                <Empty />
              ) : (
                <ul className="flex flex-wrap gap-x-3 gap-y-1 text-muted-foreground">
                  {cung.phu_tinh.map((s) => (
                    <li key={s.name}>{abbreviateStarStatus(s.display)}</li>
                  ))}
                </ul>
              )}
            </Section>

            <Section title="Tứ hóa">
              {cung.tuhoa.length === 0 ? (
                <Empty />
              ) : (
                <ul className="flex flex-wrap gap-1.5">
                  {cung.tuhoa.map((t) => (
                    <Badge key={t.name} variant="secondary">{t.display}</Badge>
                  ))}
                </ul>
              )}
            </Section>

            {saoLuu && saoLuu.length > 0 && (
              <Section title="Sao lưu">
                <ul className="flex flex-wrap gap-x-3 gap-y-1 text-muted-foreground">
                  {saoLuu.map((s) => (
                    <li key={s.name}>{abbreviateStarStatus(s.display)}</li>
                  ))}
                </ul>
              </Section>
            )}
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="text-[10px] uppercase tracking-wide text-muted-foreground">{title}</div>
      {children}
    </div>
  );
}

function Empty() {
  return <div className="text-xs text-muted-foreground italic">—</div>;
}
