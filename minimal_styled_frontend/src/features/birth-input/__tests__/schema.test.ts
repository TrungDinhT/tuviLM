import { describe, expect, it } from 'vitest';
import { BirthFormSchema, toBirthInput, fromBirthInput } from '../schema';

const VALID = {
  name: 'Linh',
  dateOf: new Date(1991, 7, 14),
  hourOf: 6,
  minuteOf: 30,
  gender: 'F' as const,
};

describe('BirthFormSchema', () => {
  it('accepts a valid form', () => {
    expect(BirthFormSchema.safeParse(VALID).success).toBe(true);
  });

  it('rejects an out-of-range year (1800)', () => {
    const r = BirthFormSchema.safeParse({ ...VALID, dateOf: new Date(1800, 0, 1) });
    expect(r.success).toBe(false);
    expect(r.error?.issues[0]?.path).toEqual(['dateOf']);
  });

  it('rejects an out-of-range year (2200)', () => {
    expect(
      BirthFormSchema.safeParse({ ...VALID, dateOf: new Date(2200, 0, 1) }).success,
    ).toBe(false);
  });

  it('rejects an invalid gender', () => {
    const r = BirthFormSchema.safeParse({ ...VALID, gender: 'X' as unknown as 'F' });
    expect(r.success).toBe(false);
    expect(r.error?.issues[0]?.path).toEqual(['gender']);
  });

  it('rejects a missing date', () => {
    const r = BirthFormSchema.safeParse({ ...VALID, dateOf: undefined });
    expect(r.success).toBe(false);
    expect(r.error?.issues[0]?.path).toEqual(['dateOf']);
  });

  it('rejects an out-of-range hour', () => {
    expect(BirthFormSchema.safeParse({ ...VALID, hourOf: 24 }).success).toBe(false);
  });

  it('rejects a non-integer hour', () => {
    expect(BirthFormSchema.safeParse({ ...VALID, hourOf: 6.5 }).success).toBe(false);
  });

  it('rejects a missing minute', () => {
    const r = BirthFormSchema.safeParse({ ...VALID, minuteOf: undefined });
    expect(r.success).toBe(false);
    expect(r.error?.issues[0]?.path).toEqual(['minuteOf']);
  });

  it('rejects an out-of-range minute', () => {
    expect(BirthFormSchema.safeParse({ ...VALID, minuteOf: 60 }).success).toBe(false);
  });

  it('rejects an unknown place key (the field was removed)', () => {
    const parsed = BirthFormSchema.parse({ ...VALID, place: 'Hà Nội' } as never);
    expect(parsed).not.toHaveProperty('place');
  });
});

describe('toBirthInput / fromBirthInput', () => {
  it('round-trips date components and hour', () => {
    const input = toBirthInput(BirthFormSchema.parse(VALID));
    expect(input).toMatchObject({
      date: 14,
      month: 8,
      year: 1991,
      hour: 6,
      gender: 'F',
      name: 'Linh',
    });

    const back = fromBirthInput(input);
    expect(back.dateOf?.getDate()).toBe(14);
    expect(back.dateOf?.getMonth()).toBe(7);
    expect(back.dateOf?.getFullYear()).toBe(1991);
    expect(back.hourOf).toBe(6);
    expect(back.gender).toBe('F');
  });

  it('drops an empty name', () => {
    const input = toBirthInput(BirthFormSchema.parse({ ...VALID, name: '   ' }));
    expect(input.name).toBeUndefined();
  });
});
