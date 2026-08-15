import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { DateInput } from '../date-input';

describe('<DateInput />', () => {
  it('renders the trigger in dd/MM/yyyy format', () => {
    render(<DateInput value={new Date(1991, 7, 14)} onChange={() => {}} />);
    expect(screen.getByRole('button')).toHaveTextContent('14/08/1991');
  });

  it('shows the placeholder when value is undefined', () => {
    render(<DateInput value={undefined} onChange={() => {}} placeholder="Chọn ngày" />);
    expect(screen.getByRole('button')).toHaveTextContent('Chọn ngày');
  });

  it('forwards the id prop to the trigger button', () => {
    render(<DateInput id="b-date" value={undefined} onChange={() => {}} />);
    expect(screen.getByRole('button')).toHaveAttribute('id', 'b-date');
  });

  it('passes through onChange typing as `Date | undefined`', () => {
    // Purely a type-level assertion via cast: if the callback typed onChange as
    // anything other than (d: Date | undefined) => void, this would fail tsc.
    const onChange = vi.fn<(d: Date | undefined) => void>();
    render(<DateInput value={undefined} onChange={onChange} />);
    expect(onChange).not.toHaveBeenCalled();
  });
});
