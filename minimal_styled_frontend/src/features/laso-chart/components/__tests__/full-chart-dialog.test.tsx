import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { useChartStore, type BirthInput } from '@/store/chart-store';
import type { BuildLasoResponse, Cung } from '@/lib/api/schemas';
import { FullChartDialog } from '../full-chart-dialog';

const DIA_CHI = [
  'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tị',
  'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi',
] as const;

function makeCung(position: string, overrides: Partial<Cung> = {}): Cung {
  return {
    position,
    role: 'Cung',
    chinh_tinh: [],
    phu_tinh: [],
    tuhoa: [],
    trang_sinh: null,
    is_tuan: false,
    is_triet: false,
    is_cung_than: false,
    age_daivan: null,
    saoLuu: [],
    ...overrides,
  };
}

function makeResponse(richTy = false): BuildLasoResponse {
  return {
    id: 'test-full',
    summary: '',
    ban_menh_name: 'Đại Lâm Mộc',
    cuc_name: 'Thủy Nhị cục',
    menh_cuc_relation_label: 'Cục sinh mệnh',
    cung_by_position: Object.fromEntries(
      DIA_CHI.map((d) => [
        d,
        d === 'Tý' && richTy
          ? makeCung(d, {
              chinh_tinh: ['Tử Vi (Miếu)'],
              phu_tinh: [{ name: 'Tả Phụ', display: 'Tả Phụ', element: 'Thổ' }],
              tuhoa: ['Hóa Lộc'],
              trang_sinh: 'Trường Sinh',
            })
          : makeCung(d),
      ]),
    ),
  };
}

const INPUT: BirthInput = { date: 3, month: 1, year: 1990, hour: 0, gender: 'F', name: 'Linh' };

beforeEach(() => {
  localStorage.clear();
  useChartStore.setState({
    lastInput: INPUT,
    current: makeResponse(true),
    saoLuuOverlay: null,
    selectedCungPosition: null,
    history: [],
  });
});

describe('FullChartDialog', () => {
  it('renders 12 cung cells inside an open dialog', () => {
    render(<FullChartDialog open={true} onOpenChange={() => {}} />);
    // Filter out the Dialog's "Close" button (accessible name = "Close").
    const cells = screen
      .getAllByRole('button')
      .filter((el) => el.textContent !== 'Close' && !el.querySelector('.sr-only'));
    expect(cells).toHaveLength(12);
  });

  it('renders phụ tinh, tứ hóa, and trang sinh inside the cells (variant=full)', () => {
    render(<FullChartDialog open={true} onOpenChange={() => {}} />);
    expect(screen.getByText('Tử Vi (Miếu)')).toBeInTheDocument();
    expect(screen.getByText('Tả Phụ')).toBeInTheDocument();
    expect(screen.getByText('Hóa Lộc')).toBeInTheDocument();
    expect(screen.getByText('Trường Sinh')).toBeInTheDocument();
  });

  it('grid container has aspect-[2/3] so each 4×4 cell is w:h = 2:3', () => {
    render(<FullChartDialog open={true} onOpenChange={() => {}} />);
    const grid = screen.getByTestId('full-chart-grid');
    expect(grid.className).toContain('aspect-[2/3]');
    expect(grid.className).toContain('grid-cols-4');
    expect(grid.className).toContain('grid-rows-4');
  });

  it('returns null when no chart is loaded', () => {
    useChartStore.setState({ current: null });
    const { container } = render(<FullChartDialog open={true} onOpenChange={() => {}} />);
    expect(container.firstChild).toBeNull();
  });
});
