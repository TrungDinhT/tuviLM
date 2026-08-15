'use client';

import { useState } from 'react';
import { useChartStore } from '@/store/chart-store';
import '@/styles/compact-chart.css';
import { CungCellCompact } from './cung-cell-compact';
import { CungDetailSheet } from './cung-detail-sheet';
import { PersonalInfo } from './personal-info';
import { CUNG_GRID } from '../types';

export function CompactChart() {
  const current = useChartStore((s) => s.current);
  const lastInput = useChartStore((s) => s.lastInput);
  const selected = useChartStore((s) => s.selectedCungPosition);
  const selectCung = useChartStore((s) => s.selectCung);
  const [open, setOpen] = useState(false);

  if (!current) return null;

  return (
    <>
      <div className="w-full overflow-auto">
        <div className="grid aspect-square min-w-[320px] grid-cols-4 grid-rows-4 gap-px overflow-hidden rounded-md bg-border">
          <PersonalInfo response={current} input={lastInput} />
          {CUNG_GRID.map(({ row, col, position }) => {
            const cung = current.cung_by_position[position];
            if (!cung) return null;
            return (
              <CungCellCompact
                key={position}
                cung={cung}
                selected={selected === position}
                onClick={() => {
                  selectCung(position);
                  setOpen(true);
                }}
                style={{ gridRow: row, gridColumn: col }}
              />
            );
          })}
        </div>
      </div>

      <CungDetailSheet
        open={open}
        onOpenChange={(v) => {
          setOpen(v);
          if (!v) selectCung(null);
        }}
      />
    </>
  );
}
