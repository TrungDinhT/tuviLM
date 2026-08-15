import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  buildLaso,
  createAnonymous,
  createChartProfile,
  createSession,
  deleteChartProfile,
  deleteSession,
  getSession,
  listChartProfiles,
  listSessions,
  streamSessionChat,
} from '../client';
import fixture from '../__fixtures__/build-laso.json';

const REQ = { day: 14, month: 8, year: 1991, hour: 6, gender: 'F' as const };

function mockFetch(impl: typeof fetch) {
  vi.stubGlobal('fetch', vi.fn(impl));
}

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}

function sseResponse(events: Array<Record<string, unknown>>) {
  return new Response(events.map((event) => `data: ${JSON.stringify(event)}\n\n`).join(''), {
    status: 200,
    headers: { 'Content-Type': 'text/event-stream' },
  });
}

function firstFetchCall(fetchMock: ReturnType<typeof vi.fn<typeof fetch>>) {
  return fetchMock.mock.calls[0]!;
}

describe('buildLaso adapter', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('returns parsed data on 200 with valid body', async () => {
    mockFetch(async () => jsonResponse(fixture));
    const out = await buildLaso(REQ);
    expect(out.ban_menh_name).toBe(fixture.ban_menh_name);
  });

  it('normalises a 4xx into { kind: "http" }', async () => {
    mockFetch(async () => jsonResponse({ detail: 'bad year' }, 422));
    await expect(buildLaso(REQ)).rejects.toMatchObject({
      kind: 'http',
      status: 422,
      body: { detail: 'bad year' },
    });
  });

  it('normalises a 5xx into { kind: "http" }', async () => {
    mockFetch(async () => jsonResponse({ detail: 'boom' }, 500));
    await expect(buildLaso(REQ)).rejects.toMatchObject({
      kind: 'http',
      status: 500,
    });
  });

  it('normalises a network failure into { kind: "network" }', async () => {
    mockFetch(async () => {
      throw new TypeError('Failed to fetch');
    });
    await expect(buildLaso(REQ)).rejects.toEqual({ kind: 'network' });
  });

  it('normalises a malformed 200 body into { kind: "parse" }', async () => {
    mockFetch(async () => jsonResponse({ wrong: 'shape' }));
    await expect(buildLaso(REQ)).rejects.toMatchObject({
      kind: 'parse',
    });
  });
});

describe('new conversation adapters', () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('creates an anonymous owner without a JSON body', async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => jsonResponse({ owner_id: 'anon_123' }));
    mockFetch(fetchMock);

    await expect(createAnonymous()).resolves.toEqual({ owner_id: 'anon_123' });
    expect(firstFetchCall(fetchMock)[0]).toContain('/api/v1/anonymous');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({ method: 'POST' });
    expect(firstFetchCall(fetchMock)[1]).not.toHaveProperty('body');
  });

  it('creates a chart profile with owner and idempotency headers', async () => {
    const fetchMock = vi.fn<typeof fetch>(async () =>
      jsonResponse({
        chart_profile: {
          id: 'profile_1',
          display_name: 'Linh',
          birth_info: { calendar: 'solar', ...REQ },
          created_at: '2026-07-05T00:00:00Z',
          updated_at: '2026-07-05T00:00:00Z',
        },
      }),
    );
    mockFetch(fetchMock);

    const out = await createChartProfile(
      { display_name: 'Linh', birth_info: { calendar: 'solar', ...REQ } },
      'anon_123',
      'profile-key',
    );

    expect(out.chart_profile.id).toBe('profile_1');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({
      headers: {
        'Content-Type': 'application/json',
        'X-Anonymous-Owner-Id': 'anon_123',
        'Idempotency-Key': 'profile-key',
      },
    });
  });

  it('creates a session under a chart profile', async () => {
    const fetchMock = vi.fn<typeof fetch>(async () =>
      jsonResponse({
        session: {
          id: 'session_1',
          chart_profile_id: 'profile_1',
          title: 'Linh',
          messages: [],
          created_at: '2026-07-05T00:00:00Z',
          updated_at: '2026-07-05T00:00:00Z',
        },
      }),
    );
    mockFetch(fetchMock);

    const out = await createSession('profile_1', { title: 'Linh' }, 'anon_123', 'session-key');

    expect(out.session.id).toBe('session_1');
    expect(firstFetchCall(fetchMock)[0]).toContain('/api/v1/chart-profiles/profile_1/sessions');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({
      headers: {
        'Content-Type': 'application/json',
        'X-Anonymous-Owner-Id': 'anon_123',
        'Idempotency-Key': 'session-key',
      },
    });
  });

  it('lists chart profiles for the anonymous owner', async () => {
    const fetchMock = vi.fn<typeof fetch>(async () =>
      jsonResponse({
        chart_profiles: [
          {
            id: 'profile_1',
            display_name: 'Linh',
            birth_info: { calendar: 'solar', ...REQ },
            created_at: '2026-07-05T00:00:00Z',
            updated_at: '2026-07-05T00:00:00Z',
          },
        ],
      }),
    );
    mockFetch(fetchMock);

    const out = await listChartProfiles('anon_123');

    expect(out.chart_profiles[0]?.id).toBe('profile_1');
    expect(firstFetchCall(fetchMock)[0]).toContain('/api/v1/chart-profiles');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({
      headers: { 'X-Anonymous-Owner-Id': 'anon_123' },
    });
  });

  it('lists sessions under a chart profile', async () => {
    const fetchMock = vi.fn<typeof fetch>(async () =>
      jsonResponse({
        sessions: [
          {
            id: 'session_1',
            chart_profile_id: 'profile_1',
            title: 'Linh',
            message_count: 2,
            created_at: '2026-07-05T00:00:00Z',
            updated_at: '2026-07-05T00:00:00Z',
          },
        ],
      }),
    );
    mockFetch(fetchMock);

    const out = await listSessions('profile_1', 'anon_123');

    expect(out.sessions[0]?.id).toBe('session_1');
    expect(firstFetchCall(fetchMock)[0]).toContain('/api/v1/chart-profiles/profile_1/sessions');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({
      headers: { 'X-Anonymous-Owner-Id': 'anon_123' },
    });
  });

  it('loads a session with persisted messages', async () => {
    const fetchMock = vi.fn<typeof fetch>(async () =>
      jsonResponse({
        session: {
          id: 'session_1',
          chart_profile_id: 'profile_1',
          title: 'Linh',
          messages: [
            {
              id: 'msg_1',
              role: 'user',
              content: 'Hi',
              status: 'confirmed',
              created_at: '2026-07-05T00:00:00Z',
              updated_at: '2026-07-05T00:00:00Z',
            },
          ],
          created_at: '2026-07-05T00:00:00Z',
          updated_at: '2026-07-05T00:00:00Z',
        },
      }),
    );
    mockFetch(fetchMock);

    const out = await getSession('session_1', 'anon_123');

    expect(out.session.messages[0]?.content).toBe('Hi');
    expect(firstFetchCall(fetchMock)[0]).toContain('/api/v1/sessions/session_1');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({
      headers: { 'X-Anonymous-Owner-Id': 'anon_123' },
    });
  });

  it('deletes a chart profile for the anonymous owner', async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => new Response(null, { status: 204 }));
    mockFetch(fetchMock);

    await expect(deleteChartProfile('profile_1', 'anon_123')).resolves.toBeUndefined();

    expect(firstFetchCall(fetchMock)[0]).toContain('/api/v1/chart-profiles/profile_1');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({
      method: 'DELETE',
      headers: { 'X-Anonymous-Owner-Id': 'anon_123' },
    });
  });

  it('deletes a session for the anonymous owner', async () => {
    const fetchMock = vi.fn<typeof fetch>(async () => new Response(null, { status: 204 }));
    mockFetch(fetchMock);

    await expect(deleteSession('session_1', 'anon_123')).resolves.toBeUndefined();

    expect(firstFetchCall(fetchMock)[0]).toContain('/api/v1/sessions/session_1');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({
      method: 'DELETE',
      headers: { 'X-Anonymous-Owner-Id': 'anon_123' },
    });
  });

  it('streams session chat and joins text deltas', async () => {
    const onTextDelta = vi.fn();
    const onDebugEvent = vi.fn();
    const fetchMock = vi.fn<typeof fetch>(async () =>
      sseResponse([
        { type: 'ids', user_message_id: 'u1', assistant_message_id: 'a1' },
        { type: 'text', delta: 'Career ' },
        {
          type: 'tool_call',
          id: 'call_1',
          name: 'get_cung_by_position',
          arguments: { position: 'Mệnh' },
        },
        {
          type: 'tool_result',
          id: 'call_1',
          name: 'get_cung_by_position',
          content: { role: 'Mệnh' },
        },
        { type: 'text', delta: 'looks strong.' },
        { type: 'done', status: 'confirmed' },
      ]),
    );
    mockFetch(fetchMock);

    await expect(
      streamSessionChat(
        'session_1',
        { content: 'Career?' },
        'anon_123',
        'message-key',
        onTextDelta,
        onDebugEvent,
      ),
    ).resolves.toEqual({
      answer: 'Career looks strong.',
      tool_calls: [{ id: 'call_1', name: 'get_cung_by_position', arguments: { position: 'Mệnh' } }],
      debug_events: [
        {
          type: 'tool_call',
          id: 'call_1',
          name: 'get_cung_by_position',
          arguments: { position: 'Mệnh' },
        },
        {
          type: 'tool_result',
          id: 'call_1',
          name: 'get_cung_by_position',
          content: { role: 'Mệnh' },
        },
      ],
    });
    expect(onTextDelta.mock.calls.map(([delta]) => delta)).toEqual(['Career ', 'looks strong.']);
    expect(onDebugEvent).toHaveBeenCalledTimes(2);

    expect(firstFetchCall(fetchMock)[0]).toContain('/api/v1/sessions/session_1/chat/stream');
    expect(firstFetchCall(fetchMock)[1]).toMatchObject({
      headers: {
        'Content-Type': 'application/json',
        'X-Anonymous-Owner-Id': 'anon_123',
        'Idempotency-Key': 'message-key',
      },
      body: JSON.stringify({ content: 'Career?' }),
    });
  });

  it('turns stream error events into ApiError', async () => {
    mockFetch(async () => sseResponse([{ type: 'error', message: 'upstream 429 rate limit' }]));

    await expect(
      streamSessionChat('session_1', { content: 'Career?' }, 'anon_123', 'message-key'),
    ).rejects.toEqual({ kind: 'stream', message: 'upstream 429 rate limit' });
  });
});
