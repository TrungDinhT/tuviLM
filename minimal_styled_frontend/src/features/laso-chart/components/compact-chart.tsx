'use client';

import { useState } from 'react';
import { useChartStore } from '@/store/chart-store';
import { CungCell } from './cung-cell';
import { CungDetailSheet } from './cung-detail-sheet';
import { PersonalInfo } from './personal-info';
import { CUNG_GRID } from '../types';

export function CompactChart() {
  const current = useChartStore((s) => s.current);
  const lastInput = useChartStore((s) => s.lastInput);
  const saoLuuOverlay = useChartStore((s) => s.saoLuuOverlay);
  const selected = useChartStore((s) => s.selectedCungPosition);
  const selectCung = useChartStore((s) => s.selectCung);
  const [open, setOpen] = useState(false);

  if (!current) return null;

  return (
    <>
      <div className="grid aspect-square grid-cols-4 grid-rows-4 gap-px overflow-hidden rounded-md bg-border">
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
              onClick={() => {
                selectCung(position);
                setOpen(true);
              }}
              style={{ gridRow: row, gridColumn: col }}
            />
          );
        })}
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
