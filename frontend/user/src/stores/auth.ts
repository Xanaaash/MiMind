import { create } from 'zustand';
import type { TriageChannel } from '../types';

interface AuthState {
  userId: string | null;
  email: string | null;
  locale: string;
  channel: TriageChannel | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;

  setUser: (userId: string, email: string, locale: string) => void;
  setChannel: (channel: TriageChannel) => void;
  setLoading: (loading: boolean) => void;
  setInitialized: (initialized: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  userId: localStorage.getItem('mc_user_id'),
  email: localStorage.getItem('mc_email'),
  locale: localStorage.getItem('mc_locale') ?? 'zh-CN',
  channel: (localStorage.getItem('mc_channel') as TriageChannel) ?? null,
  isAuthenticated: !!localStorage.getItem('mc_user_id'),
  isLoading: false,
  isInitialized: false,

  setUser: (userId, email, locale) => {
    localStorage.setItem('mc_user_id', userId);
    localStorage.setItem('mc_email', email);
    localStorage.setItem('mc_locale', locale);
    set({ userId, email, locale, isAuthenticated: true });
  },

  setChannel: (channel) => {
    localStorage.setItem('mc_channel', channel);
    set({ channel });
  },

  setLoading: (isLoading) => set({ isLoading }),

  setInitialized: (isInitialized) => set({ isInitialized }),

  logout: () => {
    localStorage.removeItem('mc_user_id');
    localStorage.removeItem('mc_email');
    localStorage.removeItem('mc_locale');
    localStorage.removeItem('mc_channel');
    set({
      userId: null,
      email: null,
      locale: 'zh-CN',
      channel: null,
      isAuthenticated: false,
      isInitialized: true,
    });
  },
}));
