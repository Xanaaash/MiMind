import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../stores/auth';
import SafetyDisclaimer from '../SafetyDisclaimer/SafetyDisclaimer';
import { useEffect, useState } from 'react';

const NAV_ITEMS = [
  { path: '/home', labelKey: 'nav.home', icon: '🏠' },
  { path: '/scales', labelKey: 'nav.scales', icon: '📋' },
  { path: '/tests', labelKey: 'nav.tests', icon: '🧩' },
  { path: '/coach', labelKey: 'nav.coach', icon: '💬' },
  { path: '/tools', labelKey: 'nav.tools', icon: '🌿' },
  { path: '/journal', labelKey: 'nav.journal', icon: '📝' },
  { path: '/billing', labelKey: 'nav.billing', icon: '💎' },
];

export default function AppLayout() {
  const { t, i18n } = useTranslation();
  const { isAuthenticated, channel, logout } = useAuthStore();
  const navigate = useNavigate();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/auth');
      return;
    }
    if (!channel) {
      navigate('/onboarding');
    }
  }, [isAuthenticated, channel, navigate]);

  const toggleLang = () => {
    const next = i18n.language === 'zh-CN' ? 'en-US' : 'zh-CN';
    i18n.changeLanguage(next);
  };

  if (!isAuthenticated || !channel) return null;

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
          <nav className="hidden md:flex items-center gap-1">
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

          <div className="flex items-center gap-2">
            <button
              onClick={toggleLang}
              className="text-sm text-muted hover:text-ink px-2 py-1 rounded-lg hover:bg-cream transition-colors"
            >
              {i18n.language === 'zh-CN' ? 'EN' : '中文'}
            </button>
            <button
              onClick={() => { logout(); navigate('/'); }}
              className="text-sm text-muted hover:text-accent px-2 py-1 rounded-lg hover:bg-cream transition-colors"
            >
              {t('auth.login') === '登录' ? '退出' : 'Logout'}
            </button>
            <button
              onClick={() => setMobileNavOpen(!mobileNavOpen)}
              className="md:hidden text-xl p-1"
              aria-label="Menu"
            >
              ☰
            </button>
          </div>
        </div>

        {/* Mobile nav dropdown */}
        {mobileNavOpen && (
          <nav className="md:hidden border-t border-line bg-panel px-4 py-3 grid grid-cols-4 gap-2">
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
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 py-6">
        <Outlet />
      </main>

      <SafetyDisclaimer />
    </div>
  );
}
