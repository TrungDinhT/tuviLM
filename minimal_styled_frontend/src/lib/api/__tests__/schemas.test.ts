import { describe, expect, it } from 'vitest';
import {
  BuildLasoRequestSchema,
  BuildLasoResponseSchema,
  BuildSaoLuuRequestSchema,
  BuildSaoLuuResponseSchema,
  ChatResponseSchema,
  CungSchema,
  CreateAnonymousResponseSchema,
  CreateChartProfileRequestSchema,
  CreateChartProfileResponseSchema,
  CreateSessionRequestSchema,
  CreateSessionResponseSchema,
  SessionChatStreamRequestSchema,
} from '../schemas';
import fixture from '../__fixtures__/build-laso.json';

describe('BuildLasoRequestSchema', () => {
  it('accepts a valid request', () => {
    const r = BuildLasoRequestSchema.safeParse({
      day: 14,
      month: 8,
      year: 1991,
      hour: 6,
      gender: 'F',
    });
    expect(r.success).toBe(true);
  });

  it.each([
    { field: 'day', value: 0 },
    { field: 'day', value: 32 },
    { field: 'month', value: 13 },
    { field: 'year', value: 1800 },
    { field: 'year', value: 2200 },
    { field: 'hour', value: 24 },
    { field: 'gender', value: 'X' },
  ])('rejects out-of-range $field=$value', ({ field, value }) => {
    const base = { day: 14, month: 8, year: 1991, hour: 6, gender: 'F' as const };
    const r = BuildLasoRequestSchema.safeParse({ ...base, [field]: value });
    expect(r.success).toBe(false);
  });
});

describe('BuildSaoLuuRequestSchema', () => {
  it('accepts a valid wrapped observation_time', () => {
    const r = BuildSaoLuuRequestSchema.safeParse({
      observation_time: { day: 1, month: 1, year: 2026, hour: 8, gender: 'M' },
    });
    expect(r.success).toBe(true);
  });

  it('rejects an unwrapped time', () => {
    const r = BuildSaoLuuRequestSchema.safeParse({
      day: 1, month: 1, year: 2026, hour: 8, gender: 'M',
    });
    expect(r.success).toBe(false);
  });
});

describe('BuildLasoResponseSchema', () => {
  it('round-trips the synthetic fixture', () => {
    const r = BuildLasoResponseSchema.safeParse(fixture);
    expect(r.success).toBe(true);
  });

  it('includes all 12 standard cung positions', () => {
    const r = BuildLasoResponseSchema.parse(fixture);
    const expected = [
      'Mệnh', 'Phụ Mẫu', 'Phúc Đức', 'Điền Trạch',
      'Quan Lộc', 'Nô Bộc', 'Thiên Di', 'Tật Ách',
      'Tài Bạch', 'Tử Tức', 'Phu Thê', 'Huynh Đệ',
    ];
    for (const pos of expected) {
      expect(r.cung_by_position[pos]).toBeDefined();
    }
  });

  it('rejects a response missing a required field', () => {
    const broken = { ...fixture };
    // @ts-expect-error: intentionally remove a required field
    delete broken.cuc_name;
    const r = BuildLasoResponseSchema.safeParse(broken);
    expect(r.success).toBe(false);
  });
});

describe('BuildSaoLuuResponseSchema', () => {
  it('accepts the same cung_by_position shape', () => {
    const r = BuildSaoLuuResponseSchema.safeParse({
      cung_by_position: fixture.cung_by_position,
    });
    expect(r.success).toBe(true);
  });
});

describe('new conversation schemas', () => {
  it('accepts an anonymous owner response', () => {
    expect(CreateAnonymousResponseSchema.safeParse({ owner_id: 'anon_123' }).success).toBe(true);
  });

  it('accepts a chart profile create request', () => {
    const r = CreateChartProfileRequestSchema.safeParse({
      display_name: 'Linh',
      birth_info: {
        calendar: 'solar',
        day: 14,
        month: 8,
        year: 1991,
        hour: 6,
        gender: 'F',
      },
    });
    expect(r.success).toBe(true);
  });

  it('accepts chart profile and session responses', () => {
    const chartProfile = {
      id: 'profile_1',
      display_name: 'Linh',
      birth_info: {
        calendar: 'solar',
        day: 14,
        month: 8,
        year: 1991,
        hour: 6,
        gender: 'F',
      },
      created_at: '2026-07-05T00:00:00Z',
      updated_at: '2026-07-05T00:00:00Z',
    };
    expect(CreateChartProfileResponseSchema.safeParse({ chart_profile: chartProfile }).success).toBe(true);
    expect(CreateSessionRequestSchema.safeParse({ title: 'Linh' }).success).toBe(true);
    expect(
      CreateSessionResponseSchema.safeParse({
        session: {
          id: 'session_1',
          chart_profile_id: 'profile_1',
          title: 'Linh',
          messages: [],
          created_at: '2026-07-05T00:00:00Z',
          updated_at: '2026-07-05T00:00:00Z',
        },
      }).success,
    ).toBe(true);
  });

  it('accepts a session chat stream request', () => {
    expect(SessionChatStreamRequestSchema.safeParse({ content: 'Hello' }).success).toBe(true);
    expect(SessionChatStreamRequestSchema.safeParse({ content: '' }).success).toBe(false);
  });
});

describe('ChatResponseSchema', () => {
  it('round-trips a minimal response with empty tool_calls', () => {
    const r = ChatResponseSchema.safeParse({ answer: 'Xin chào.', tool_calls: [] });
    expect(r.success).toBe(true);
    expect(r.data?.debug_events).toEqual([]);
  });

  it('requires tool_calls (backend always emits the field)', () => {
    expect(ChatResponseSchema.safeParse({ answer: 'Hi' }).success).toBe(false);
  });

  it('accepts populated tool_calls with arbitrary arguments', () => {
    const r = ChatResponseSchema.safeParse({
      answer: 'See cung Mệnh',
      tool_calls: [{ id: 'c1', name: 'get_cung_by_position', arguments: { position: 'Tý' } }],
      debug_events: [
        { type: 'tool_call', id: 'c1', name: 'get_cung_by_position', arguments: { position: 'Tý' } },
        { type: 'tool_result', id: 'c1', name: 'get_cung_by_position', content: { role: 'Mệnh' } },
      ],
    });
    expect(r.success).toBe(true);
  });

  it('rejects a response missing answer', () => {
    expect(ChatResponseSchema.safeParse({ tool_calls: [] }).success).toBe(false);
  });
});

describe('CungSchema', () => {
  it('treats role and trang_sinh as optional / nullable', () => {
    const r = CungSchema.safeParse({
      position: 'Mệnh',
      chinh_tinh: [],
      phu_tinh: [],
      tuhoa: [],
      is_tuan: false,
      is_triet: false,
      is_cung_than: false,
      saoLuu: [],
    });
    expect(r.success).toBe(true);
  });
});
