import { describe, it, expect, beforeEach } from 'vitest';
import { useAuthStore } from '../../stores/auth';

describe('useAuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      userId: null,
      email: null,
      locale: 'zh-CN',
      channel: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,
    });
  });

  it('starts unauthenticated when localStorage is empty', () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.userId).toBeNull();
  });

  it('setUser persists to localStorage and updates state', () => {
    useAuthStore.getState().setUser('u-123', 'a@b.com', 'en-US');

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.userId).toBe('u-123');
    expect(state.email).toBe('a@b.com');
    expect(state.locale).toBe('en-US');

    expect(localStorage.getItem('mc_user_id')).toBe('u-123');
    expect(localStorage.getItem('mc_email')).toBe('a@b.com');
    expect(localStorage.getItem('mc_locale')).toBe('en-US');
  });

  it('setChannel persists non-null channel and removes null', () => {
    useAuthStore.getState().setChannel('GREEN');
    expect(useAuthStore.getState().channel).toBe('GREEN');
    expect(localStorage.getItem('mc_channel')).toBe('GREEN');

    useAuthStore.getState().setChannel(null);
    expect(useAuthStore.getState().channel).toBeNull();
    expect(localStorage.getItem('mc_channel')).toBeNull();
  });

  it('setLoading and setInitialized update booleans', () => {
    useAuthStore.getState().setLoading(true);
    expect(useAuthStore.getState().isLoading).toBe(true);

    useAuthStore.getState().setInitialized(true);
    expect(useAuthStore.getState().isInitialized).toBe(true);
  });

  it('logout clears state and localStorage', () => {
    useAuthStore.getState().setUser('u-1', 'x@x.com', 'zh-CN');
    useAuthStore.getState().setChannel('YELLOW');

    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.userId).toBeNull();
    expect(state.email).toBeNull();
    expect(state.channel).toBeNull();
    expect(state.isInitialized).toBe(true);

    expect(localStorage.getItem('mc_user_id')).toBeNull();
    expect(localStorage.getItem('mc_email')).toBeNull();
    expect(localStorage.getItem('mc_channel')).toBeNull();
  });
});
