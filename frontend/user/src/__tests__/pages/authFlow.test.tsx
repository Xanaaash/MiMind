import React from 'react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import Auth from '../../pages/Auth/Auth';
import { useAuthStore } from '../../stores/auth';
import { authLogin, authRegister, getEntitlements } from '../../api/auth';

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => key,
    i18n: { language: 'en-US' },
  }),
}));

vi.mock('../../api/auth', () => ({
  authLogin: vi.fn(),
  authRegister: vi.fn(),
  getEntitlements: vi.fn(),
}));

describe('Auth page password flow', () => {
  beforeEach(() => {
    localStorage.clear();
    useAuthStore.getState().logout();
    vi.mocked(authLogin).mockReset();
    vi.mocked(authRegister).mockReset();
    vi.mocked(getEntitlements).mockReset();
  });

  it('logs in with /api/auth/login and stores user session fields', async () => {
    vi.mocked(authLogin).mockResolvedValue({
      authenticated: true,
      user_id: 'u-auth-login',
      email: 'login@example.com',
      user: {
        user_id: 'u-auth-login',
        email: 'login@example.com',
        locale: 'en-US',
        created_at: new Date().toISOString(),
      },
    });
    vi.mocked(getEntitlements).mockResolvedValue({ channel: 'GREEN', entitlements: {} });

    render(
      <MemoryRouter>
        <Auth />
      </MemoryRouter>,
    );

    fireEvent.change(screen.getByPlaceholderText('auth.email_placeholder'), { target: { value: 'login@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('auth.password_placeholder'), { target: { value: 'Pass1234' } });
    fireEvent.click(screen.getByRole('button', { name: 'auth.login' }));

    await waitFor(() => expect(authLogin).toHaveBeenCalledWith('login@example.com', 'Pass1234'));
    await waitFor(() => expect(useAuthStore.getState().userId).toBe('u-auth-login'));
    expect(useAuthStore.getState().channel).toBe('GREEN');
  });

  it('switches to register mode and calls /api/auth/register', async () => {
    vi.mocked(authRegister).mockResolvedValue({
      authenticated: true,
      user_id: 'u-auth-register',
      email: 'signup@example.com',
      user: {
        user_id: 'u-auth-register',
        email: 'signup@example.com',
        locale: 'en-US',
        created_at: new Date().toISOString(),
      },
    });
    vi.mocked(getEntitlements).mockResolvedValue({ channel: 'GREEN', entitlements: {} });

    render(
      <MemoryRouter>
        <Auth />
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByRole('button', { name: 'auth.go_register' }));
    expect(screen.getByText('auth.password_hint')).toBeInTheDocument();

    fireEvent.change(screen.getByPlaceholderText('auth.email_placeholder'), { target: { value: 'signup@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('auth.password_placeholder'), { target: { value: 'Pass1234' } });
    fireEvent.click(screen.getByRole('button', { name: 'auth.submit_register' }));

    await waitFor(() =>
      expect(authRegister).toHaveBeenCalledWith('signup@example.com', 'Pass1234', 'en-US', '2026.02'),
    );
    await waitFor(() => expect(useAuthStore.getState().userId).toBe('u-auth-register'));
  });
});
