import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { buildLaso } from '../client';
import fixture from '../__fixtures__/build-laso.json';

const REQ = { date: 14, month: 8, year: 1991, hour: 6, gender: 'F' as const };

function mockFetch(impl: typeof fetch) {
  vi.stubGlobal('fetch', vi.fn(impl));
}

function jsonResponse(body: unknown, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
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
