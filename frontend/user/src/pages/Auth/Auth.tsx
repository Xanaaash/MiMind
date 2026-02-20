import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import { adminLogin, getEntitlements, register } from '../../api/auth';
import { toast } from '../../stores/toast';
import type { TriageChannel } from '../../types';
import Button from '../../components/Button/Button';

function toChannel(value: unknown): TriageChannel | null {
  if (value === 'GREEN' || value === 'YELLOW' || value === 'RED') {
    return value;
  }
  return null;
}

export default function Auth() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { setUser, setChannel } = useAuthStore();

  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await adminLogin(username, password);

      const email = `${username}@mimind.ai`;
      let userId = localStorage.getItem('mc_user_id');
      let resolvedChannel: TriageChannel | null = null;

      if (!userId) {
        const data = await register(email, 'zh-CN', '2026.02');
        userId = data.user_id;
        const triage = data.triage as { channel?: unknown } | undefined;
        resolvedChannel = toChannel(triage?.channel);
      }

      if (!resolvedChannel && userId) {
        try {
          const entitlements = await getEntitlements(userId);
          resolvedChannel = toChannel(entitlements.channel);
        } catch {
          resolvedChannel = null;
        }
      }

      setUser(userId!, email, 'zh-CN');
      setChannel(resolvedChannel);
      toast.success(t('auth.login') === '登录' ? '登录成功' : 'Login successful');
      navigate(resolvedChannel ? '/home' : '/onboarding');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <motion.div
        className="w-full max-w-sm bg-panel border border-line rounded-3xl shadow-lg p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Link to="/" className="flex items-center gap-2 mb-6">
          <span className="font-heading text-2xl font-bold text-accent">MiMind</span>
        </Link>

        <h1 className="font-heading text-2xl font-bold">{t('auth.login')}</h1>
        <p className="text-muted text-sm mt-1 mb-6">{t('app.tagline')}</p>

        <form onSubmit={handleLogin} className="grid gap-4">
          <label className="grid gap-1.5">
            <span className="text-sm font-medium text-muted">{t('auth.login') === '登录' ? '账号' : 'Username'}</span>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="border border-line rounded-xl px-4 py-3 bg-white/90 text-ink focus:outline-none focus:ring-2 focus:ring-accent/30 transition-shadow"
            />
          </label>

          <label className="grid gap-1.5">
            <span className="text-sm font-medium text-muted">{t('auth.password')}</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="border border-line rounded-xl px-4 py-3 bg-white/90 text-ink focus:outline-none focus:ring-2 focus:ring-accent/30 transition-shadow"
            />
          </label>

          <Button type="submit" loading={loading} className="w-full">
            {t('auth.login')}
          </Button>
        </form>

        <p className="text-xs text-muted text-center mt-6 leading-relaxed">
          {t('auth.agree_policy')}{' '}
          <Link to="/privacy" className="text-accent hover:underline">
            {t('auth.privacy_policy')}
          </Link>{' '}
          {t('auth.and')}{' '}
          <Link to="/terms" className="text-accent hover:underline">
            {t('auth.terms')}
          </Link>
        </p>
        <p className="text-xs text-muted text-center mt-3">{t('app.boundary')}</p>
      </motion.div>
    </div>
  );
}
