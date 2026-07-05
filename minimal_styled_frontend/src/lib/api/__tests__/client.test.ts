import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { buildLaso, createAnonymous, createChartProfile, createSession } from '../client';
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
});
