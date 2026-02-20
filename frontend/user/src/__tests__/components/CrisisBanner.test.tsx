import React from "react";
import { describe, expect, it, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import CrisisBanner from '../../components/CrisisBanner/CrisisBanner';

const mockNavigate = vi.fn();

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
  }),
}));

vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

describe('CrisisBanner', () => {
  beforeEach(() => {
    mockNavigate.mockReset();
  });

  it('renders nothing when visible is false', () => {
    const { container } = render(<CrisisBanner visible={false} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders alert content and hotline links when visible is true', () => {
    render(<CrisisBanner visible message="Need immediate support" />);

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('Need immediate support')).toBeInTheDocument();

    const telLinks = screen.getAllByRole('link');
    expect(telLinks.length).toBeGreaterThanOrEqual(2);
    expect(telLinks[0]).toHaveAttribute('href', expect.stringContaining('tel:'));
  });

  it('navigates to safety page from action button', () => {
    render(<CrisisBanner visible />);
    fireEvent.click(screen.getByRole('button', { name: 'safety.subtitle' }));
    expect(mockNavigate).toHaveBeenCalledWith('/safety');
  });
});
