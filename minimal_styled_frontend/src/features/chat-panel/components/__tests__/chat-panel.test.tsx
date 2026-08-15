import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChartStore, type BirthInput } from '@/store/chart-store';
import type { BuildLasoResponse, Cung } from '@/lib/api/schemas';
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

function sessionResponse(messages: unknown[] = []) {
  return jsonResponse({
    session: {
      id: 'session_1',
      chart_profile_id: 'profile_1',
      title: 'Linh',
      messages,
      created_at: '2026-07-05T00:00:00Z',
      updated_at: '2026-07-05T00:00:00Z',
    },
  });
}

function sseResponse(events: Array<Record<string, unknown>>) {
  return new Response(events.map((event) => `data: ${JSON.stringify(event)}\n\n`).join(''), {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' },
  });
}

function mockChatFetch(chatImpl?: () => Response | Promise<Response>) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
    const url = String(input);
    if (url.includes('/chat/stream')) {
      if (!chatImpl) throw new TypeError('unexpected chat request');
      return chatImpl();
    }
    return sessionResponse();
  });
}

beforeEach(() => {
  localStorage.clear();
  useChartStore.setState({
    ownerId: 'anon_123',
    chartProfileId: 'profile_1',
    sessionId: 'session_1',
    lastInput: INPUT,
    current: RESPONSE,
    saoLuuOverlay: null,
    selectedCungPosition: null,
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('ChatPanel', () => {
  it('mounts with the initial greeting and quick-prompt row visible', async () => {
    mockChatFetch();
    renderPanel();
    expect(screen.getByText(/Chào bạn\. Mình đã đọc lá số của bạn/)).toBeInTheDocument();
    // Quick prompts are present.
    expect(await screen.findByRole('button', { name: /Năm nay sự nghiệp/ })).toBeInTheDocument();
    // Demo badge removed.
    expect(screen.queryByText('Demo')).toBeNull();
  });

  it('hydrates persisted session messages', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      sessionResponse([
        {
          id: 'msg_1',
          role: 'user',
          content: 'Cũ không?',
          status: 'confirmed',
          created_at: '2026-07-05T00:00:00Z',
          updated_at: '2026-07-05T00:00:00Z',
        },
        {
          id: 'msg_2',
          role: 'assistant',
          content: 'Cũ đây.',
          status: 'confirmed',
          created_at: '2026-07-05T00:00:00Z',
          updated_at: '2026-07-05T00:00:00Z',
        },
      ]),
    );

    renderPanel();

    await waitFor(() => {
      expect(screen.getByText('Cũ không?')).toBeInTheDocument();
      expect(screen.getByText('Cũ đây.')).toBeInTheDocument();
    });
    expect(screen.queryByText(/Chào bạn\. Mình đã đọc lá số của bạn/)).toBeNull();
  });

  it('quick-prompt click submits via session stream and removes the quick-prompt row', async () => {
    const fetchMock = mockChatFetch(() => sseResponse([{ type: 'text', delta: 'Câu trả lời' }]));

    renderPanel();
    const prompt = await screen.findByRole('button', { name: /Năm nay sự nghiệp/ });
    fireEvent.click(prompt);

    await waitFor(() => {
      expect(screen.getByText('Câu trả lời')).toBeInTheDocument();
    });

    // Quick-prompt buttons gone after first send.
    expect(screen.queryByRole('button', { name: /Năm nay sự nghiệp/ })).toBeNull();

    const streamCalls = fetchMock.mock.calls.filter(([url]) => String(url).includes('/chat/stream'));
    expect(streamCalls).toHaveLength(1);
    expect(streamCalls[0]![0]).toContain('/api/v1/sessions/session_1/chat/stream');
  });

  it('shows live tool debug events when Dev mode is enabled', async () => {
    mockChatFetch(() =>
      sseResponse([
        { type: 'tool_call', id: 'call_1', name: 'get_cung_by_position', arguments: { position: 'Mệnh' } },
        { type: 'tool_result', id: 'call_1', name: 'get_cung_by_position', content: { role: 'Mệnh' } },
        { type: 'text', delta: 'Câu trả lời' },
      ]),
    );

    renderPanel();
    fireEvent.click(await screen.findByRole('button', { name: 'Dev' }));
    fireEvent.click(await screen.findByRole('button', { name: /Năm nay sự nghiệp/ }));

    await waitFor(() => {
      expect(screen.getByText('Debug events (2)')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Debug events (2)'));
    expect(screen.getAllByText(/get_cung_by_position/)).toHaveLength(2);
  });

  it('manual send: textarea + Send disabled while pending, then answer replaces the pending bubble', async () => {
    let resolveChat: ((value: Response) => void) | undefined;
    const fetchMock = mockChatFetch(
      () =>
        new Promise<Response>((res) => {
          resolveChat = res;
        }),
    );

    renderPanel();
    const textarea = (await screen.findByPlaceholderText('Hỏi thầy điều gì...')) as HTMLTextAreaElement;
    await waitFor(() => expect(textarea).not.toBeDisabled());
    fireEvent.change(textarea, { target: { value: 'Hi' } });
    fireEvent.click(screen.getByRole('button', { name: 'Gửi' }));

    // Pending: button + textarea disabled.
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Gửi' })).toBeDisabled();
      expect(textarea).toBeDisabled();
    });

    await act(async () => {
      resolveChat!(sseResponse([{ type: 'text', delta: 'Reply' }]));
    });

    await waitFor(() => {
      expect(screen.getByText('Reply')).toBeInTheDocument();
      expect(textarea).not.toBeDisabled();
    });

    expect(fetchMock.mock.calls.filter(([url]) => String(url).includes('/chat/stream'))).toHaveLength(1);
  });

  it('shows streamed text while the request is still pending', async () => {
    let resolveChat: ((value: Response) => void) | undefined;
    mockChatFetch(
      () =>
        new Promise<Response>((res) => {
          resolveChat = res;
        }),
    );

    renderPanel();
    const input = await screen.findByPlaceholderText('Hỏi thầy điều gì...');
    await waitFor(() => expect(input).not.toBeDisabled());
    fireEvent.change(input, { target: { value: 'Hi' } });
    fireEvent.click(screen.getByRole('button', { name: 'Gửi' }));

    await waitFor(() => {
      expect(resolveChat).toBeTypeOf('function');
    });
    await act(async () => {
      resolveChat!(sseResponse([{ type: 'text', delta: 'Partial answer' }]));
    });

    expect(screen.getByText('Partial answer')).toBeInTheDocument();
  });

  it('network error renders an error bubble; conversation stays interactive', async () => {
    mockChatFetch(() => {
      throw new TypeError('network down');
    });

    renderPanel();
    const prompt = await screen.findByRole('button', { name: /Năm nay sự nghiệp/ });
    fireEvent.click(prompt);

    await waitFor(() => {
      expect(
        screen.getByText('Không kết nối được đến máy chủ. Vui lòng kiểm tra mạng.'),
      ).toBeInTheDocument();
    });

    // Textarea re-enabled after error.
    expect(screen.getByPlaceholderText('Hỏi thầy điều gì...')).not.toBeDisabled();
  });
});
