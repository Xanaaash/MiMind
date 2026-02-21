import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../stores/auth';
import { useThemeStore } from '../../stores/theme';
import SafetyDisclaimer from '../SafetyDisclaimer/SafetyDisclaimer';
import { useEffect, useState } from 'react';

const NAV_ITEMS = [
  { path: '/home', labelKey: 'nav.home', icon: '🏠' },
  { path: '/scales', labelKey: 'nav.scales', icon: '📋' },
  { path: '/tests', labelKey: 'nav.tests', icon: '🧩' },
  { path: '/neurodiversity', labelKey: 'nav.neuro', icon: '🧠' },
  { path: '/coach', labelKey: 'nav.coach', icon: '💬' },
  { path: '/tools', labelKey: 'nav.tools', icon: '🌿' },
  { path: '/journal', labelKey: 'nav.journal', icon: '📝' },
  { path: '/billing', labelKey: 'nav.billing', icon: '💎' },
];

export default function AppLayout() {
  const { t, i18n } = useTranslation();
  const { isAuthenticated, logout } = useAuthStore();
  const { theme, setTheme, resolved } = useThemeStore();
  const navigate = useNavigate();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const cycleTheme = () => {
    const order: Array<'light' | 'dark' | 'system'> = ['light', 'dark', 'system'];
    const next = order[(order.indexOf(theme) + 1) % order.length];
    setTheme(next);
  };
  const themeIcon = resolved === 'dark' ? '🌙' : theme === 'system' ? '💻' : '☀️';

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/auth');
    }
  }, [isAuthenticated, navigate]);

  const toggleLang = () => {
    const next = i18n.language === 'zh-CN' ? 'en-US' : 'zh-CN';
    i18n.changeLanguage(next);
  };

  if (!isAuthenticated) return null;

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top bar */}
      <header className="sticky top-0 z-30 bg-panel/80 backdrop-blur-md border-b border-line">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <NavLink to="/home" className="flex items-center gap-2">
            <span className="font-heading text-xl font-bold text-accent">MiMind</span>
            <span className="text-xs bg-accent-soft text-accent px-2 py-0.5 rounded-full font-semibold">AI</span>
          </NavLink>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1" aria-label="Primary navigation">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `px-3 py-2 rounded-xl text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-accent text-white'
                      : 'text-muted hover:bg-cream hover:text-ink'
                  }`
                }
              >
                <span className="mr-1">{item.icon}</span>
                {t(item.labelKey)}
              </NavLink>
            ))}
          </nav>

          <div className="flex items-center gap-1 sm:gap-2">
            <button
              onClick={cycleTheme}
              className="text-sm px-2 py-1 rounded-lg hover:bg-cream transition-colors"
              aria-label={t('layout.toggle_theme')}
              title={theme === 'system' ? t('layout.theme_system') : theme === 'dark' ? t('layout.theme_dark') : t('layout.theme_light')}
            >
              {themeIcon}
            </button>
            <button
              onClick={toggleLang}
              className="text-sm text-muted hover:text-ink px-2 py-1 rounded-lg hover:bg-cream transition-colors"
              aria-label={t('layout.switch_language')}
            >
              {i18n.language === 'zh-CN' ? 'EN' : '中文'}
            </button>
            <button
              onClick={() => { logout(); navigate('/'); }}
              className="text-sm text-muted hover:text-accent px-2 py-1 rounded-lg hover:bg-cream transition-colors"
              aria-label={t('auth.logout')}
            >
              {t('auth.logout')}
            </button>
            <button
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              className="md:hidden text-xl p-1"
              aria-label={t('layout.menu')}
              aria-expanded={mobileNavOpen}
              aria-controls="mobile-nav-menu"
            >
              ☰
            </button>
          </div>
        </div>

        {/* Mobile nav dropdown */}
        {mobileNavOpen && (
          <nav
            id="mobile-nav-menu"
            className="md:hidden border-t border-line bg-panel px-4 py-3 grid grid-cols-4 gap-2"
            aria-label="Mobile navigation"
          >
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={() => setMobileNavOpen(false)}
                className={({ isActive }) =>
                  `flex flex-col items-center gap-1 py-2 rounded-xl text-xs font-medium transition-colors ${
                    isActive ? 'bg-accent text-white' : 'text-muted hover:bg-cream'
                  }`
                }
              >
                <span className="text-lg">{item.icon}</span>
                {t(item.labelKey)}
              </NavLink>
            ))}
          </nav>
        )}
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-3 sm:px-4 py-4 sm:py-6">
        <Outlet />
      </main>

      <SafetyDisclaimer />
    </div>
  );
}
