import { describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import { GenderControl } from '../gender-control';

describe('<GenderControl />', () => {
  it('renders both options with role=radio and the active one aria-checked', () => {
    render(<GenderControl value="M" onChange={() => {}} />);
    const nam = screen.getByRole('radio', { name: 'Nam' });
    const nu = screen.getByRole('radio', { name: 'Nữ' });
    expect(nam).toHaveAttribute('aria-checked', 'true');
    expect(nu).toHaveAttribute('aria-checked', 'false');
  });

  it('exposes role=radiogroup on the wrapper', () => {
    render(<GenderControl value="F" onChange={() => {}} />);
    expect(screen.getByRole('radiogroup')).toBeInTheDocument();
  });

  it('calls onChange when an inactive option is clicked', () => {
    const onChange = vi.fn();
    render(<GenderControl value="M" onChange={onChange} />);
    fireEvent.click(screen.getByRole('radio', { name: 'Nữ' }));
    expect(onChange).toHaveBeenCalledExactlyOnceWith('F');
  });

  it('moves selection with ArrowRight / ArrowLeft', () => {
    const onChange = vi.fn();
    render(<GenderControl value="M" onChange={onChange} />);
    const nam = screen.getByRole('radio', { name: 'Nam' });
    nam.focus();
    fireEvent.keyDown(nam, { key: 'ArrowRight' });
    expect(onChange).toHaveBeenLastCalledWith('F');

    onChange.mockClear();
    fireEvent.keyDown(nam, { key: 'ArrowLeft' });
    expect(onChange).toHaveBeenLastCalledWith('F');
  });

  it('only the active option is in the tab order', () => {
    render(<GenderControl value="F" onChange={() => {}} />);
    expect(screen.getByRole('radio', { name: 'Nữ' })).toHaveAttribute('tabindex', '0');
    expect(screen.getByRole('radio', { name: 'Nam' })).toHaveAttribute('tabindex', '-1');
  });
});
