import { beforeEach, describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChartStore, type BirthInput } from '@/store/chart-store';
import type { BuildLasoResponse, Cung } from '@/lib/api/schemas';
import { ChatScreen } from '../chat-screen';

function renderWithProviders(ui: React.ReactElement) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(<QueryClientProvider client={client}>{ui}</QueryClientProvider>);
}

const DIA_CHI = [
  'Tý', 'Sửu', 'Dần', 'Mão', 'Thìn', 'Tị',
  'Ngọ', 'Mùi', 'Thân', 'Dậu', 'Tuất', 'Hợi',
] as const;

function makeCung(position: string): Cung {
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
  };
}

const INPUT: BirthInput = { date: 3, month: 1, year: 1990, hour: 0, gender: 'F', name: 'Linh' };

const RESPONSE: BuildLasoResponse = {
  id: 'screen-test',
  summary: '',
  ban_menh_name: 'X',
  cuc_name: 'Y',
  menh_cuc_relation_label: 'Z',
  cung_by_position: Object.fromEntries(DIA_CHI.map((d) => [d, makeCung(d)])),
};

beforeEach(() => {
  localStorage.clear();
  useChartStore.setState({
    lastInput: null,
    current: null,
    saoLuuOverlay: null,
    selectedCungPosition: null,
    history: [],
  });
});

describe('ChatScreen full-chart trigger', () => {
  it('renders the "Xem chi tiết" trigger button when a chart is loaded', () => {
    useChartStore.setState({ lastInput: INPUT, current: RESPONSE });
    renderWithProviders(<ChatScreen />);
    const triggers = screen.getAllByRole('button', { name: 'Xem chi tiết' });
    expect(triggers.length).toBeGreaterThan(0);
  });

  it('does not render the trigger button when no chart is loaded', () => {
    renderWithProviders(<ChatScreen />);
    expect(screen.queryByRole('button', { name: 'Xem chi tiết' })).toBeNull();
  });
});
