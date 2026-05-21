'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { ArrowRight, History as HistoryIcon, Trash2 } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Empty, EmptyContent, EmptyDescription, EmptyMedia, EmptyTitle } from '@/components/ui/empty';
import { useChartStore, type HistoryEntry } from '@/store/chart-store';

function formatBirth(input: HistoryEntry['input']): string {
  const dd = input.date.toString().padStart(2, '0');
  const mm = input.month.toString().padStart(2, '0');
  const hh = input.hour.toString().padStart(2, '0');
  return `${dd}.${mm}.${input.year} · ${hh}:00`;
}

function formatRelative(ms: number, now: number): string {
  const diff = Math.max(0, now - ms);
  const min = Math.floor(diff / 60_000);
  if (min < 1) return 'Vừa xong';
  if (min < 60) return `${min} phút trước`;
  const hr = Math.floor(min / 60);
  if (hr < 24) return `${hr} giờ trước`;
  const day = Math.floor(hr / 24);
  if (day < 30) return `${day} ngày trước`;
  const mo = Math.floor(day / 30);
  return `${mo} tháng trước`;
}

export function HistoryList() {
  const router = useRouter();
  const history = useChartStore((s) => s.history);
  const loadFromHistory = useChartStore((s) => s.loadFromHistory);
  const removeFromHistory = useChartStore((s) => s.removeFromHistory);
  const [now] = useState(() => Date.now());

  if (history.length === 0) {
    return (
      <Empty className="mx-auto max-w-sm">
        <EmptyMedia variant="icon">
          <HistoryIcon className="size-5" />
        </EmptyMedia>
        <EmptyTitle>Chưa có lá số nào</EmptyTitle>
        <EmptyDescription>
          Mỗi lá số bạn an sẽ được lưu lại ở đây để xem lại nhanh chóng.
        </EmptyDescription>
        <EmptyContent>
          <Button asChild>
            <Link href="/">
              Nhập thông tin <ArrowRight className="size-4" />
            </Link>
          </Button>
        </EmptyContent>
      </Empty>
    );
  }

  return (
    <ul className="grid gap-3 sm:grid-cols-2">
      {history.map((entry) => (
        <li key={entry.id}>
          <Card size="sm" className="cursor-pointer transition-colors hover:bg-accent/50">
            <CardHeader>
              <div className="flex items-center justify-between gap-2">
                <Badge variant="outline" className="text-[10px]">
                  {entry.input.gender === 'M' ? 'Nam' : 'Nữ'}
                </Badge>
                <span className="text-[11px] text-muted-foreground tabular-nums">
                  {formatRelative(entry.builtAt, now)}
                </span>
              </div>
              <CardTitle className="text-sm leading-snug">
                {entry.input.name?.trim() || 'Không tên'}
              </CardTitle>
              <div className="text-xs text-muted-foreground">{formatBirth(entry.input)}</div>
              <div className="text-xs text-muted-foreground">
                Bản mệnh: <span className="text-foreground">{entry.response.ban_menh_name}</span>
              </div>
            </CardHeader>
            <CardContent className="flex items-center justify-between gap-2 pt-0">
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={() => {
                  loadFromHistory(entry.id);
                  router.push('/chat');
                }}
              >
                Mở lá số <ArrowRight className="size-3.5" />
              </Button>
              <Button
                type="button"
                variant="ghost"
                size="icon-sm"
                aria-label="Xóa"
                onClick={() => removeFromHistory(entry.id)}
              >
                <Trash2 className="size-3.5" />
              </Button>
            </CardContent>
          </Card>
        </li>
      ))}
    </ul>
  );
}
