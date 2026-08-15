import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useChartStore } from '@/store/chart-store';
import { Sidebar } from '../sidebar';

vi.mock('next/navigation', () => ({
  usePathname: () => '/chat',
  useRouter: () => ({ push: vi.fn() }),
}));

function renderSidebar() {
  const client = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={client}>
      <Sidebar collapsed={false} />
    </QueryClientProvider>,
  );
}

function jsonResponse(body: unknown) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}

beforeEach(() => {
  localStorage.clear();
  useChartStore.setState({
    ownerId: 'anon_123',
    chartProfileId: 'profile_1',
    sessionId: 'session_1',
    lastInput: null,
    current: null,
    saoLuuOverlay: null,
    selectedCungPosition: null,
  });

  vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const url = String(input);
    if (init?.method === 'DELETE') {
      return new Response(null, { status: 204 });
    }
    if (url.endsWith('/api/v1/chart-profiles')) {
      return jsonResponse({
        chart_profiles: [
          {
            id: 'profile_1',
            display_name: 'Linh',
            birth_info: { calendar: 'solar', day: 3, month: 1, year: 1990, hour: 0, gender: 'F' },
            created_at: '2026-07-05T00:00:00Z',
            updated_at: '2026-07-05T10:00:00Z',
          },
        ],
      });
    }
    if (url.includes('/api/v1/chart-profiles/profile_1/sessions')) {
      return jsonResponse({
        sessions: [
          {
            id: 'session_1',
            chart_profile_id: 'profile_1',
            title: 'Hỏi gần đây',
            message_count: 4,
            created_at: '2026-07-05T10:00:00Z',
            updated_at: '2026-07-05T10:00:00Z',
          },
        ],
      });
    }
    throw new TypeError(`unexpected fetch: ${url}`);
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

describe('Sidebar', () => {
  it('shows the profile/session library instead of a history nav item', async () => {
    renderSidebar();

    expect(screen.queryByRole('link', { name: /Lịch sử/ })).toBeNull();
    expect(screen.getByRole('link', { name: /Đọc lá số/ })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /^Lá số$/ })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /^Linh/ })).toBeInTheDocument();
    expect(await screen.findByRole('button', { name: /^Hỏi gần đây/ })).toBeInTheDocument();
  });

  it('confirms and deletes a session from the tree', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    renderSidebar();
    await screen.findByRole('button', { name: /^Hỏi gần đây/ });
    fireEvent.click(screen.getByRole('button', { name: /Xóa phiên Hỏi gần đây/ }));

    expect(window.confirm).toHaveBeenCalledWith('Xóa phiên trò chuyện này?');
    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/sessions/session_1'),
        expect.objectContaining({ method: 'DELETE' }),
      );
    });
  });

  it('confirms and deletes a whole profile from the tree', async () => {
    vi.spyOn(window, 'confirm').mockReturnValue(true);

    renderSidebar();
    await screen.findByRole('button', { name: /^Linh/ });
    fireEvent.click(screen.getByRole('button', { name: /Xóa hồ sơ Linh/ }));

    expect(window.confirm).toHaveBeenCalledWith('Xóa toàn bộ hồ sơ "Linh" và các phiên trò chuyện?');
    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/chart-profiles/profile_1'),
        expect.objectContaining({ method: 'DELETE' }),
      );
    });
  });
});
