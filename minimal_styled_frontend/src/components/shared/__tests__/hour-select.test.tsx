import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { HourSelect } from '../hour-select';

describe('<HourSelect />', () => {
  it('renders the trigger as the plain hour number', () => {
    render(<HourSelect value={6} onChange={() => {}} />);
    expect(screen.getByRole('combobox')).toHaveTextContent('6');
  });

  it('shows the placeholder when value is undefined', () => {
    render(<HourSelect value={undefined} onChange={() => {}} placeholder="--" />);
    expect(screen.getByRole('combobox')).toHaveTextContent('--');
  });

  it('formats hour 23 as plain "23" (largest option)', () => {
    render(<HourSelect value={23} onChange={() => {}} />);
    expect(screen.getByRole('combobox')).toHaveTextContent('23');
  });

  it('passes through onChange typing as (h: number) => void', () => {
    const onChange = vi.fn<(h: number) => void>();
    render(<HourSelect value={0} onChange={onChange} />);
    expect(onChange).not.toHaveBeenCalled();
  });
});
