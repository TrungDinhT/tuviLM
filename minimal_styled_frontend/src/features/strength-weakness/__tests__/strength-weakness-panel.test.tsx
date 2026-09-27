import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChartStore } from '@/store/chart-store';
import type { BuildLasoResponse, CapabilityProfile } from '@/lib/api/schemas';
import { StrengthWeaknessPanel } from '../strength-weakness-panel';

const chart: BuildLasoResponse = {
  id: 'test',
  summary: '',
  ban_menh_name: '',
  cuc_name: '',
  menh_cuc_relation_label: '',
  cung_by_position: {},
};
const birth = {
  calendar: 'solar' as const,
  year: 1990,
  month: 5,
  date: 15,
  hour: 10,
  gender: 'M' as const,
};
const profile: CapabilityProfile = {
  tong_quan: 'Hồ sơ năng lực của bạn',
  diem_manh: [
    {
      nang_luc_id: 'quyet_doan',
      nang_luc: 'Quyết đoán',
      mo_ta: 'Chủ động quyết định',
      giai_thich: 'Luận giải điểm mạnh',
    },
  ],
  diem_yeu: [
    {
      ten: 'Vội vàng',
      loai: 'qua_da',
      mo_ta: 'Đôi khi quyết định quá nhanh',
      giai_thich: 'Luận giải điểm yếu',
    },
  ],
};
const fetchMock = vi.fn();
let client: QueryClient;

function mount() {
  return render(
    <QueryClientProvider client={client}>
      <StrengthWeaknessPanel />
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  fetchMock.mockReset();
  vi.stubGlobal('fetch', fetchMock);
  useChartStore.setState({ current: chart, lastInput: birth, ownerId: 'owner-1' });
});
afterEach(() => {
  cleanup();
  client.clear();
  vi.unstubAllGlobals();
});

describe('strength and weakness analysis', () => {
  it('loads on demand, shows both findings, and reuses the chart report on remount', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify(profile)));
    const view = mount();
    expect(fetchMock).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole('button', { name: 'Khám phá năng lực' }));
    expect(await screen.findByText('Hồ sơ năng lực của bạn')).toBeInTheDocument();
    expect(screen.getByText('Quyết đoán')).toBeInTheDocument();
    expect(screen.getByText('Vội vàng')).toBeInTheDocument();
    expect(screen.getByText('Luận giải điểm mạnh')).toBeInTheDocument();
    const [url, options] = fetchMock.mock.calls[0]!;
    expect(url).toContain('/api/v1/laso/strength-weakness');
    expect(JSON.parse(options.body)).toEqual({
      calendar: 'solar',
      year: 1990,
      month: 5,
      day: 15,
      hour: 10,
      gender: 'M',
    });
    view.unmount();
    mount();
    expect(screen.getByText('Hồ sơ năng lực của bạn')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('preserves lunar hour and leap month and does not show the previous chart report', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify(profile)));
    mount();
    fireEvent.click(screen.getByRole('button', { name: 'Khám phá năng lực' }));
    await screen.findByText(profile.tong_quan);
    act(() =>
      useChartStore.setState({
        lastInput: {
          calendar: 'lunar',
          year: 1990,
          month: 5,
          date: 15,
          hour_in_dia_chi: 'ti',
          is_leap_month: true,
          gender: 'M',
        },
      }),
    );
    expect(screen.queryByText(profile.tong_quan)).not.toBeInTheDocument();
    fetchMock.mockResolvedValue(
      new Response(JSON.stringify({ ...profile, tong_quan: 'Hồ sơ âm lịch' })),
    );
    fireEvent.click(screen.getByRole('button', { name: 'Khám phá năng lực' }));
    await screen.findByText('Hồ sơ âm lịch');
    expect(JSON.parse(fetchMock.mock.calls[1]![1].body)).toEqual({
      calendar: 'lunar',
      year: 1990,
      month: 5,
      day: 15,
      hour_in_dia_chi: 'ti',
      is_leap_month: true,
      gender: 'M',
    });
  });

  it('shows loading, handles failure, and retries explicitly', async () => {
    let reject!: (error: Error) => void;
    fetchMock.mockImplementationOnce(
      () =>
        new Promise((_resolve, rejectRequest) => {
          reject = rejectRequest;
        }),
    );
    mount();
    fireEvent.click(screen.getByRole('button', { name: 'Khám phá năng lực' }));
    expect(await screen.findByRole('status')).toHaveTextContent('Đang phân tích');
    expect(screen.getByRole('button', { name: 'Đang phân tích…' })).toBeDisabled();
    await act(async () => reject(new Error('offline')));
    expect(await screen.findByRole('alert')).toHaveTextContent('Không kết nối');
    fetchMock.mockResolvedValue(new Response(JSON.stringify(profile)));
    fireEvent.click(screen.getByRole('button', { name: 'Thử lại' }));
    await screen.findByText(profile.tong_quan);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it('rejects malformed responses and hides the panel without a chart', async () => {
    fetchMock.mockResolvedValue(new Response(JSON.stringify({ tong_quan: 'Missing findings' })));
    mount();
    fireEvent.click(screen.getByRole('button', { name: 'Khám phá năng lực' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('không đúng định dạng');
    act(() => useChartStore.setState({ current: null, lastInput: null }));
    await waitFor(() =>
      expect(screen.queryByText('Điểm mạnh và điểm cần lưu ý')).not.toBeInTheDocument(),
    );
  });

  it('does not leak a late result into a newly selected chart', async () => {
    let resolve!: (value: Response) => void;
    fetchMock.mockImplementationOnce(
      () =>
        new Promise((complete) => {
          resolve = complete;
        }),
    );
    mount();
    fireEvent.click(screen.getByRole('button', { name: 'Khám phá năng lực' }));
    await screen.findByRole('status');
    act(() => useChartStore.setState({ lastInput: { ...birth, hour: 11 } }));
    await act(async () => resolve(new Response(JSON.stringify(profile))));
    expect(screen.queryByText(profile.tong_quan)).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Khám phá năng lực' })).toBeEnabled();
  });
});
