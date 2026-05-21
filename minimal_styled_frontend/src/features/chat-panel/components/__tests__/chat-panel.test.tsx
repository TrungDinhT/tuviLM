import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChartStore, type BirthInput } from '@/store/chart-store';
import type { BuildLasoResponse, Cung } from '@/lib/api/schemas';
import { NO_LASO_SENTINEL } from '@/lib/api/schemas';
import { ChatPanel } from '../chat-panel';

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
  id: 'panel-test',
  summary: '',
  ban_menh_name: 'X',
  cuc_name: 'Y',
  menh_cuc_relation_label: 'Z',
  cung_by_position: Object.fromEntries(DIA_CHI.map((d) => [d, makeCung(d)])),
};

function renderPanel() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <ChatPanel />
    </QueryClientProvider>,
  );
}

function jsonResponse(body: unknown, init: ResponseInit = {}) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
}

beforeEach(() => {
  localStorage.clear();
  useChartStore.setState({
    lastInput: INPUT,
    current: RESPONSE,
    saoLuuOverlay: null,
    selectedCungPosition: null,
    history: [],
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('ChatPanel', () => {
  it('mounts with the initial greeting and quick-prompt row visible', () => {
    renderPanel();
    expect(screen.getByText(/Chào bạn\. Mình đã đọc lá số của bạn/)).toBeInTheDocument();
    // Quick prompts are present.
    expect(screen.getByRole('button', { name: /Năm nay sự nghiệp/ })).toBeInTheDocument();
    // Demo badge removed.
    expect(screen.queryByText('Demo')).toBeNull();
  });

  it('quick-prompt click submits via real /chat call and removes the quick-prompt row', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ answer: 'Câu trả lời', tool_calls: [] }));

    renderPanel();
    fireEvent.click(screen.getByRole('button', { name: /Năm nay sự nghiệp/ }));

    await waitFor(() => {
      expect(screen.getByText('Câu trả lời')).toBeInTheDocument();
    });

    // Quick-prompt buttons gone after first send.
    expect(screen.queryByRole('button', { name: /Năm nay sự nghiệp/ })).toBeNull();

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]![0]).toContain('/api/v1/chat');
  });

  it('manual send: textarea + Send disabled while pending, then answer replaces the pending bubble', async () => {
    let resolveChat: ((value: Response) => void) | undefined;
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementationOnce(
      () => new Promise<Response>((res) => { resolveChat = res; }),
    );

    renderPanel();
    const textarea = screen.getByPlaceholderText('Hỏi thầy điều gì...') as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: 'Hi' } });
    fireEvent.click(screen.getByRole('button', { name: 'Gửi' }));

    // Pending: button + textarea disabled.
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Gửi' })).toBeDisabled();
      expect(textarea).toBeDisabled();
    });

    await act(async () => {
      resolveChat!(jsonResponse({ answer: 'Reply', tool_calls: [] }));
    });

    await waitFor(() => {
      expect(screen.getByText('Reply')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Gửi' })).not.toBeDisabled();
    });

    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('sentinel triggers /laso/build + retry /chat and shows resync caption', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      // First /chat returns the sentinel.
      .mockResolvedValueOnce(jsonResponse({ answer: NO_LASO_SENTINEL, tool_calls: [] }))
      // /laso/build succeeds.
      .mockResolvedValueOnce(jsonResponse(RESPONSE))
      // Second /chat returns the real answer.
      .mockResolvedValueOnce(jsonResponse({ answer: 'After resync', tool_calls: [] }));

    renderPanel();
    fireEvent.click(screen.getByRole('button', { name: /Năm nay sự nghiệp/ }));

    // The resync caption appears between the first and second /chat calls.
    await waitFor(() => {
      expect(screen.getByText(/đang đồng bộ lại lá số/)).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('After resync')).toBeInTheDocument();
    });

    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(fetchMock.mock.calls[0]![0]).toContain('/api/v1/chat');
    expect(fetchMock.mock.calls[1]![0]).toContain('/api/v1/laso/build');
    expect(fetchMock.mock.calls[2]![0]).toContain('/api/v1/chat');
  });

  it('sentinel after resync renders an error bubble and does not loop', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(jsonResponse({ answer: NO_LASO_SENTINEL, tool_calls: [] }))
      .mockResolvedValueOnce(jsonResponse(RESPONSE))
      .mockResolvedValueOnce(jsonResponse({ answer: NO_LASO_SENTINEL, tool_calls: [] }));

    renderPanel();
    fireEvent.click(screen.getByRole('button', { name: /Năm nay sự nghiệp/ }));

    await waitFor(() => {
      expect(
        screen.getByText('Không khôi phục được phiên lá số. Vui lòng thử lại.'),
      ).toBeInTheDocument();
    });

    // No fourth call.
    expect(fetchMock).toHaveBeenCalledTimes(3);
  });

  it('network error renders an error bubble; conversation stays interactive', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new TypeError('network down'));

    renderPanel();
    fireEvent.click(screen.getByRole('button', { name: /Năm nay sự nghiệp/ }));

    await waitFor(() => {
      expect(
        screen.getByText('Không kết nối được đến máy chủ. Vui lòng kiểm tra mạng.'),
      ).toBeInTheDocument();
    });

    // Textarea re-enabled after error.
    expect(screen.getByPlaceholderText('Hỏi thầy điều gì...')).not.toBeDisabled();
  });
});
