import { create } from 'zustand';

type Theme = 'light' | 'dark' | 'system';

interface ThemeState {
  theme: Theme;
  resolved: 'light' | 'dark';
  setTheme: (theme: Theme) => void;
}

function getSystemPreference(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'light';
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function resolve(theme: Theme): 'light' | 'dark' {
  return theme === 'system' ? getSystemPreference() : theme;
}

function applyToDOM(resolved: 'light' | 'dark') {
  const root = document.documentElement;
  if (resolved === 'dark') {
    root.classList.add('dark');
  } else {
    root.classList.remove('dark');
  }
}

const stored = (localStorage.getItem('mc_theme') as Theme) ?? 'system';
const initialResolved = resolve(stored);
applyToDOM(initialResolved);

export const useThemeStore = create<ThemeState>((set) => ({
  theme: stored,
  resolved: initialResolved,

  setTheme: (theme) => {
    localStorage.setItem('mc_theme', theme);
    const r = resolve(theme);
    applyToDOM(r);
    set({ theme, resolved: r });
  },
}));

if (typeof window !== 'undefined') {
  const mq = window.matchMedia('(prefers-color-scheme: dark)');
  mq.addEventListener('change', () => {
    const state = useThemeStore.getState();
    if (state.theme === 'system') {
      const r = getSystemPreference();
      applyToDOM(r);
      useThemeStore.setState({ resolved: r });
    }
  });
}
