import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import { register } from '../../api/auth';
import Button from '../../components/Button/Button';

export default function Auth() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const isRegister = searchParams.get('mode') === 'register';
  const { setUser, setChannel } = useAuthStore();

  const [email, setEmail] = useState('');
  const [agreed, setAgreed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = await register(email, 'zh-CN', '2026.02');
      setUser(data.user_id, email, 'zh-CN');

      const triage = data.triage as { channel?: string } | undefined;
      if (triage?.channel) {
        setChannel(triage.channel as 'GREEN' | 'YELLOW' | 'RED');
      }

      navigate('/home');
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async () => {
    setError('');
    setLoading(true);
    try {
      const storedId = localStorage.getItem('mc_user_id');
      const storedEmail = localStorage.getItem('mc_email');
      if (storedId && storedEmail) {
        useAuthStore.getState().setUser(storedId, storedEmail, 'zh-CN');
        navigate('/home');
        return;
      }
      const tempEmail = `user-${Date.now()}@mindcoach.ai`;
      const data = await register(tempEmail, 'zh-CN', '2026.02');
      setUser(data.user_id, tempEmail, 'zh-CN');
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
        className="w-full max-w-md bg-panel border border-line rounded-3xl shadow-lg p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <Link to="/" className="flex items-center gap-2 mb-8">
          <span className="font-heading text-2xl font-bold text-accent">MindCoach</span>
          <span className="text-xs bg-accent-soft text-accent px-2 py-0.5 rounded-full font-semibold">AI</span>
        </Link>

        <h1 className="font-heading text-2xl font-bold">
          {isRegister ? t('auth.register') : t('auth.login')}
        </h1>
        <p className="text-muted text-sm mt-1 mb-6">{t('app.tagline')}</p>

        <form onSubmit={handleSubmit} className="grid gap-4">
          <label className="grid gap-1.5">
            <span className="text-sm font-medium text-muted">{t('auth.email')}</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder={t('auth.email_placeholder')}
              required
              className="border border-line rounded-xl px-4 py-3 bg-white/90 text-ink focus:outline-none focus:ring-2 focus:ring-accent/30 transition-shadow"
            />
          </label>

          {isRegister && (
            <label className="flex items-start gap-2 text-sm text-muted cursor-pointer">
              <input
                type="checkbox"
                checked={agreed}
                onChange={(e) => setAgreed(e.target.checked)}
                className="mt-1 accent-accent"
              />
              <span>
                {t('auth.agree_policy')}{' '}
                <a href="#" className="text-accent underline">{t('auth.privacy_policy')}</a>
                {' '}{t('auth.and')}{' '}
                <a href="#" className="text-accent underline">{t('auth.terms')}</a>
              </span>
            </label>
          )}

          {error && (
            <p className="text-danger text-sm font-medium">{error}</p>
          )}

          <Button
            type="submit"
            loading={loading}
            disabled={isRegister && !agreed}
            className="w-full"
          >
            {isRegister ? t('auth.submit_register') : t('auth.login')}
          </Button>

          <div className="relative my-2">
            <div className="absolute inset-0 flex items-center"><div className="w-full border-t border-line" /></div>
            <div className="relative flex justify-center"><span className="bg-panel px-3 text-xs text-muted">or</span></div>
          </div>

          <Button variant="ghost" type="button" onClick={handleQuickLogin} loading={loading}>
            {isRegister ? t('auth.login') : t('auth.register')}
          </Button>
        </form>

        <p className="text-center text-sm text-muted mt-6">
          {isRegister ? t('auth.have_account') : t('auth.no_account')}{' '}
          <Link
            to={isRegister ? '/auth' : '/auth?mode=register'}
            className="text-accent font-medium hover:underline"
          >
            {isRegister ? t('auth.go_login') : t('auth.go_register')}
          </Link>
        </p>

        <p className="text-xs text-muted text-center mt-4">{t('app.boundary')}</p>
      </motion.div>
    </div>
  );
}
