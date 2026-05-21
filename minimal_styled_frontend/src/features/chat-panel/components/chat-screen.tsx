'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet';
import { Empty, EmptyContent, EmptyDescription, EmptyMedia, EmptyTitle } from '@/components/ui/empty';
import { useChartStore } from '@/store/chart-store';
import { AspectBars } from '@/features/laso-chart/components/aspect-bars';
import { CompactChart } from '@/features/laso-chart/components/compact-chart';
import { SaoLuuPicker } from '@/features/laso-chart/components/sao-luu-picker';
import { ChatPanel } from './chat-panel';

export function ChatScreen() {
  const current = useChartStore((s) => s.current);
  const [mobileChartOpen, setMobileChartOpen] = useState(false);

  if (!current) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <Empty className="max-w-sm">
          <EmptyMedia variant="icon">
            <Sparkles className="size-5" />
          </EmptyMedia>
          <EmptyTitle>Chưa có lá số nào</EmptyTitle>
          <EmptyDescription>An lá số trước để bắt đầu trò chuyện.</EmptyDescription>
          <EmptyContent>
            <Button asChild>
              <Link href="/">
                Nhập thông tin <ArrowRight className="size-4" />
              </Link>
            </Button>
          </EmptyContent>
        </Empty>
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-0 w-full">
      {/* Chat column (always visible) */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Mobile-only: open chart in a sheet */}
        <div className="border-b border-border bg-background px-4 py-3 lg:hidden">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="w-full justify-between"
            onClick={() => setMobileChartOpen(true)}
          >
            Xem chi tiết lá số <ArrowRight className="size-4" />
          </Button>
        </div>
        <div className="min-h-0 flex-1">
          <ChatPanel />
        </div>
      </div>

      {/* Desktop chart side panel */}
      <aside className="hidden w-[420px] shrink-0 flex-col gap-4 overflow-y-auto border-l border-border bg-background p-4 lg:flex">
        <Card size="sm">
          <CardHeader>
            <CardTitle className="text-sm">Lá số</CardTitle>
          </CardHeader>
          <CardContent>
            <CompactChart />
          </CardContent>
        </Card>
        <SaoLuuPicker />
        <AspectBars />
      </aside>

      {/* Mobile chart sheet */}
      <Sheet open={mobileChartOpen} onOpenChange={setMobileChartOpen}>
        <SheetContent side="right" className="flex w-full flex-col gap-4 overflow-y-auto p-4">
          <SheetHeader className="gap-1 p-0">
            <SheetTitle>Lá số</SheetTitle>
            <SheetDescription>Chạm vào một cung để xem chi tiết.</SheetDescription>
          </SheetHeader>
          <CompactChart />
          <SaoLuuPicker />
          <AspectBars />
        </SheetContent>
      </Sheet>
    </div>
  );
}
