import { describe, expect, it } from 'vitest';
import {
  BuildLasoRequestSchema,
  BuildLasoResponseSchema,
  BuildSaoLuuRequestSchema,
  BuildSaoLuuResponseSchema,
  CungSchema,
} from '../schemas';
import fixture from '../__fixtures__/build-laso.json';

describe('BuildLasoRequestSchema', () => {
  it('accepts a valid request', () => {
    const r = BuildLasoRequestSchema.safeParse({
      date: 14,
      month: 8,
      year: 1991,
      hour: 6,
      gender: 'F',
    });
    expect(r.success).toBe(true);
  });

  it.each([
    { field: 'date', value: 0 },
    { field: 'date', value: 32 },
    { field: 'month', value: 13 },
    { field: 'year', value: 1800 },
    { field: 'year', value: 2200 },
    { field: 'hour', value: 24 },
    { field: 'gender', value: 'X' },
  ])('rejects out-of-range $field=$value', ({ field, value }) => {
    const base = { date: 14, month: 8, year: 1991, hour: 6, gender: 'F' as const };
    const r = BuildLasoRequestSchema.safeParse({ ...base, [field]: value });
    expect(r.success).toBe(false);
  });
});

describe('BuildSaoLuuRequestSchema', () => {
  it('accepts a valid wrapped observation_time', () => {
    const r = BuildSaoLuuRequestSchema.safeParse({
      observation_time: { date: 1, month: 1, year: 2026, hour: 8, gender: 'M' },
    });
    expect(r.success).toBe(true);
  });

  it('rejects an unwrapped time', () => {
    const r = BuildSaoLuuRequestSchema.safeParse({
      date: 1, month: 1, year: 2026, hour: 8, gender: 'M',
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
