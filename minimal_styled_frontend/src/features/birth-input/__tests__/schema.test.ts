import { describe, expect, it } from 'vitest';
import { BirthFormSchema, toBirthInput, fromBirthInput } from '../schema';

const VALID = {
  name: 'Linh',
  place: 'Hà Nội',
  dateOf: '1991-08-14',
  timeOf: '06:30',
  gender: 'F' as const,
};

describe('BirthFormSchema', () => {
  it('accepts a valid form', () => {
    expect(BirthFormSchema.safeParse(VALID).success).toBe(true);
  });

  it('rejects an out-of-range year (1800)', () => {
    const r = BirthFormSchema.safeParse({ ...VALID, dateOf: '1800-08-14' });
    expect(r.success).toBe(false);
    expect(r.error?.issues[0]?.path).toEqual(['dateOf']);
  });

  it('rejects an out-of-range year (2200)', () => {
    expect(BirthFormSchema.safeParse({ ...VALID, dateOf: '2200-08-14' }).success).toBe(false);
  });

  it('rejects an invalid gender', () => {
    const r = BirthFormSchema.safeParse({ ...VALID, gender: 'X' as unknown as 'F' });
    expect(r.success).toBe(false);
    expect(r.error?.issues[0]?.path).toEqual(['gender']);
  });

  it('rejects a malformed date string', () => {
    expect(BirthFormSchema.safeParse({ ...VALID, dateOf: '14/08/1991' }).success).toBe(false);
  });

  it('rejects an impossible month', () => {
    expect(BirthFormSchema.safeParse({ ...VALID, dateOf: '1991-13-14' }).success).toBe(false);
  });
});

describe('toBirthInput / fromBirthInput', () => {
  it('round-trips date/time/gender (hour minutes truncated to :00)', () => {
    const input = toBirthInput(BirthFormSchema.parse(VALID));
    const back = fromBirthInput(input);
    expect(back.dateOf).toBe('1991-08-14');
    expect(back.timeOf).toBe('06:00');
    expect(back.gender).toBe('F');
  });

  it('drops empty optional name/place', () => {
    const input = toBirthInput(
      BirthFormSchema.parse({ ...VALID, name: '   ', place: '' }),
    );
    expect(input.name).toBeUndefined();
    expect(input.place).toBeUndefined();
  });
});
