import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import { adminLogin, register } from '../../api/auth';
import Button from '../../components/Button/Button';

export default function Auth() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { setUser, setChannel } = useAuthStore();

  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await adminLogin(username, password);

      const email = `${username}@mindcoach.ai`;
      let userId = localStorage.getItem('mc_user_id');

      if (!userId) {
        const data = await register(email, 'zh-CN', '2026.02');
        userId = data.user_id;
        const triage = data.triage as { channel?: string } | undefined;
        if (triage?.channel) {
          setChannel(triage.channel as 'GREEN' | 'YELLOW' | 'RED');
        }
      }

      setUser(userId!, email, 'zh-CN');
      navigate('/home');
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
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
          <span className="font-heading text-2xl font-bold text-accent">MindCoach</span>
          <span className="text-xs bg-accent-soft text-accent px-2 py-0.5 rounded-full font-semibold">AI</span>
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

          {error && (
            <p className="text-danger text-sm font-medium">{error}</p>
          )}

          <Button type="submit" loading={loading} className="w-full">
            {t('auth.login')}
          </Button>
        </form>

        <p className="text-xs text-muted text-center mt-6">{t('app.boundary')}</p>
      </motion.div>
    </div>
  );
}
