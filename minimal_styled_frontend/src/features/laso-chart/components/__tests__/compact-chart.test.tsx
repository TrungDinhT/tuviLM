import { beforeEach, describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { useChartStore, type BirthInput } from '@/store/chart-store';
import type { BuildLasoResponse, Cung } from '@/lib/api/schemas';
import { CompactChart } from '../compact-chart';
import { CUNG_GRID } from '../../types';

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

function makeResponse(): BuildLasoResponse {
  return {
    id: 'test-1',
    summary: '',
    ban_menh_name: 'Đại Lâm Mộc',
    cuc_name: 'Thủy Nhị cục',
    menh_cuc_relation_label: 'Cục sinh mệnh',
    cung_by_position: Object.fromEntries(
      DIA_CHI.map((d) => [d, makeCung(d)]),
    ),
  };
}

const INPUT: BirthInput = { date: 3, month: 1, year: 1990, hour: 0, gender: 'F', name: 'Linh' };

beforeEach(() => {
  localStorage.clear();
  useChartStore.setState({
    lastInput: INPUT,
    current: makeResponse(),
    saoLuuOverlay: null,
    selectedCungPosition: null,
    history: [],
  });
});

describe('CompactChart', () => {
  it('renders all 12 địa chi cells when cung_by_position is keyed by địa chi', () => {
    render(<CompactChart />);
    const cells = screen.getAllByRole('button');
    expect(cells).toHaveLength(12);
  });

  it('renders the central personal-info block with chart metadata', () => {
    render(<CompactChart />);
    expect(screen.getByText('Lá số tử vi')).toBeInTheDocument();
    expect(screen.getByText('Linh')).toBeInTheDocument();
    expect(screen.getByText('Đại Lâm Mộc')).toBeInTheDocument();
    expect(screen.getByText('Thủy Nhị cục')).toBeInTheDocument();
    expect(screen.getByText('Cục sinh mệnh')).toBeInTheDocument();
  });

  it('places each địa chi cell at the canonical [row, col] coordinate', () => {
    render(<CompactChart />);
    const cells = screen.getAllByRole('button');
    const byPosition = new Map<string, HTMLElement>();
    for (const cell of cells) {
      const label = cell.textContent ?? '';
      const dc = DIA_CHI.find((d) => label.includes(d));
      if (dc) byPosition.set(dc, cell);
    }
    for (const { row, col, position } of CUNG_GRID) {
      const el = byPosition.get(position);
      expect(el, `cell for ${position}`).toBeDefined();
      expect(el!.style.gridRow).toBe(String(row));
      expect(el!.style.gridColumn).toBe(String(col));
    }
  });

  it('clicking a cell calls selectCung with that cell\'s địa chi name', () => {
    render(<CompactChart />);
    const cells = screen.getAllByRole('button');
    fireEvent.click(cells[0]!);
    const selected = useChartStore.getState().selectedCungPosition;
    expect(DIA_CHI).toContain(selected as (typeof DIA_CHI)[number]);
  });

  it('strips out tứ hóa / tuần / triệt / phụ tinh / trang sinh / age đại vận / sao lưu', () => {
    // Replace store with a cung that has every field populated.
    const noisyCung: Cung = makeCung('Tý', {
      chinh_tinh: ['Tử Vi (Miếu)'],
      phu_tinh: [{ name: 'Tả Phụ', display: 'Tả Phụ', element: 'Thổ' }],
      tuhoa: [{ name: 'hoa_loc', display: 'Hóa Lộc', element: 'Thổ' }],
      trang_sinh: 'Trường Sinh',
      is_tuan: true,
      is_triet: true,
      is_cung_than: true,
      age_daivan: 6,
      saoLuu: [{ name: 'Thiên Tướng', display: 'Thiên Tướng', element: 'Thủy' }],
    });
    useChartStore.setState({
      lastInput: INPUT,
      current: {
        id: 'noisy',
        summary: '',
        ban_menh_name: 'X',
        cuc_name: 'Y',
        menh_cuc_relation_label: 'Z',
        cung_by_position: Object.fromEntries(
          DIA_CHI.map((d) => [d, d === 'Tý' ? noisyCung : makeCung(d)]),
        ),
      },
      saoLuuOverlay: null,
      selectedCungPosition: null,
      history: [],
    });
    render(<CompactChart />);
    // Compact cell of Tý: chính tinh string visible.
    expect(screen.getByText('Tử Vi (M)')).toBeInTheDocument();
    // None of the stripped fields should appear.
    expect(screen.queryByText('Tả Phụ')).not.toBeInTheDocument();
    expect(screen.queryByText('Hóa Lộc')).not.toBeInTheDocument();
    expect(screen.queryByText('Trường Sinh')).not.toBeInTheDocument();
    expect(screen.queryByText('Thiên Tướng')).not.toBeInTheDocument();
    expect(screen.queryByText('T')).not.toBeInTheDocument(); // tuần marker
    expect(screen.queryByText('Tr')).not.toBeInTheDocument(); // triệt marker
    expect(screen.queryByText('6')).not.toBeInTheDocument(); // age đại vận
  });
});
