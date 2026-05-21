'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useChartStore } from '@/store/chart-store';
import { CungCell } from './cung-cell';
import { CungDetailSheet } from './cung-detail-sheet';
import { PersonalInfo } from './personal-info';
import { CUNG_GRID } from '../types';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function FullChartDialog({ open, onOpenChange }: Props) {
  const current = useChartStore((s) => s.current);
  const lastInput = useChartStore((s) => s.lastInput);
  const saoLuuOverlay = useChartStore((s) => s.saoLuuOverlay);
  const selected = useChartStore((s) => s.selectedCungPosition);
  const selectCung = useChartStore((s) => s.selectCung);
  const [detailOpen, setDetailOpen] = useState(false);

  if (!current) return null;

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="flex max-h-[95vh] w-full max-w-[min(95vw,calc(95vh*2/3))] flex-col gap-3 overflow-hidden p-4">
          <DialogHeader>
            <DialogTitle>Lá số chi tiết</DialogTitle>
            <DialogDescription>
              Chạm vào một cung để xem mô tả đầy đủ.
            </DialogDescription>
          </DialogHeader>
          <div
            data-testid="full-chart-grid"
            className="grid aspect-[2/3] min-h-0 grid-cols-4 grid-rows-4 gap-px overflow-hidden rounded-md bg-border"
          >
            <PersonalInfo response={current} input={lastInput} />
            {CUNG_GRID.map(({ row, col, position }) => {
              const cung = current.cung_by_position[position];
              if (!cung) return null;
              const overlay = saoLuuOverlay?.cung_by_position[position]?.saoLuu;
              return (
                <CungCell
                  key={position}
                  cung={cung}
                  saoLuu={overlay}
                  selected={selected === position}
                  variant="full"
                  onClick={() => {
                    selectCung(position);
                    setDetailOpen(true);
                  }}
                  style={{ gridRow: row, gridColumn: col }}
                />
              );
            })}
          </div>
        </DialogContent>
      </Dialog>

      <CungDetailSheet
        open={detailOpen}
        onOpenChange={(v) => {
          setDetailOpen(v);
          if (!v) selectCung(null);
        }}
      />
    </>
  );
}
