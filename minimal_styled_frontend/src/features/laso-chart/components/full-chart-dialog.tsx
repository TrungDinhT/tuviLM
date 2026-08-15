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
import { CungCellFull } from './cung-cell-full';
import { CungDetailSheet } from './cung-detail-sheet';
import { PersonalInfo } from './personal-info';
import { CUNG_GRID } from '../types';
import '@/styles/full-chart.css';

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

type BadgePos = 'top-left' | 'top-center' | 'top-right' | 'bot-left' | 'bot-center' | 'bot-right';

interface TuanTrietPair {
  ids: [string, string];
  anchor: string;
  pos: BadgePos;
}

const TUAN_TRIET_PAIRS: TuanTrietPair[] = [
  { ids: ['Tý', 'Sửu'], anchor: 'Tý', pos: 'top-left' },
  { ids: ['Thìn', 'Tị'], anchor: 'Thìn', pos: 'top-center' },
  { ids: ['Dần', 'Mão'], anchor: 'Dần', pos: 'top-center' },
  { ids: ['Ngọ', 'Mùi'], anchor: 'Ngọ', pos: 'bot-right' },
  { ids: ['Thân', 'Dậu'], anchor: 'Thân', pos: 'bot-center' },
  { ids: ['Tuất', 'Hợi'], anchor: 'Tuất', pos: 'bot-center' },
];

const POSITION_TO_GRID = new Map(CUNG_GRID.map((g) => [g.position, { r: g.row - 1, c: g.col - 1 }]));

function badgeOffsetPercent(pos: BadgePos, anchorGrid: { r: number; c: number }) {
  const cellPct = 25;
  const xLeft = anchorGrid.c * cellPct;
  const xCenter = anchorGrid.c * cellPct + cellPct / 2;
  const xRight = (anchorGrid.c + 1) * cellPct;
  const yTop = anchorGrid.r * cellPct;
  const yBot = (anchorGrid.r + 1) * cellPct;
  switch (pos) {
    case 'top-left':
      return { left: `${xLeft}%`, top: `${yTop}%` };
    case 'top-center':
      return { left: `${xCenter}%`, top: `${yTop}%` };
    case 'top-right':
      return { left: `${xRight}%`, top: `${yTop}%` };
    case 'bot-left':
      return { left: `${xLeft}%`, top: `${yBot}%` };
    case 'bot-center':
      return { left: `${xCenter}%`, top: `${yBot}%` };
    case 'bot-right':
      return { left: `${xRight}%`, top: `${yBot}%` };
  }
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
        <DialogContent className="flex max-h-[95vh] w-full max-w-[max(520px,min(95vw,calc((95vh-120px)*2/3)))] flex-col gap-3 overflow-hidden p-4">
          <DialogHeader>
            <DialogTitle>Lá số chi tiết</DialogTitle>
            <DialogDescription>
              Chạm vào một cung để xem mô tả đầy đủ.
            </DialogDescription>
          </DialogHeader>
          <div className="flex-1 min-h-0 overflow-y-auto -mx-1 px-1">
            <div
              data-testid="full-chart-grid"
              className="fc-grid rounded-md"
            >
            <PersonalInfo response={current} input={lastInput} variant="full" className="fc-center" />
            {CUNG_GRID.map(({ row, col, position }) => {
              const cung = current.cung_by_position[position];
              if (!cung) return null;
              const overlay = saoLuuOverlay?.cung_by_position[position]?.saoLuu;
              return (
                <CungCellFull
                  key={position}
                  cung={cung}
                  saoLuu={overlay}
                  selected={selected === position}
                  onClick={() => {
                    selectCung(position);
                    setDetailOpen(true);
                  }}
                  style={{ gridRow: row, gridColumn: col }}
                />
              );
            })}
            {TUAN_TRIET_PAIRS.map((pair) => {
              const c1 = current.cung_by_position[pair.ids[0]];
              const c2 = current.cung_by_position[pair.ids[1]];
              const hasTuan = !!(c1?.is_tuan || c2?.is_tuan);
              const hasTriet = !!(c1?.is_triet || c2?.is_triet);
              if (!hasTuan && !hasTriet) return null;
              const label = hasTuan && hasTriet ? 'Tuần-Triệt' : hasTuan ? 'Tuần' : 'Triệt';
              const anchorGrid = POSITION_TO_GRID.get(pair.anchor);
              if (!anchorGrid) return null;
              const { left, top } = badgeOffsetPercent(pair.pos, anchorGrid);
              return (
                <div
                  key={`tt-${pair.anchor}`}
                  className="fc-badge-tuan-triet"
                  style={{ left, top }}
                >
                  {label}
                </div>
              );
            })}
          </div>
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
