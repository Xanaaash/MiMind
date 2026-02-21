import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import { adminLogin, getEntitlements, register } from '../../api/auth';
import { toast } from '../../stores/toast';
import type { TriageChannel } from '../../types';
import Button from '../../components/Button/Button';
import FieldError from '../../components/Form/FieldError';
import { emailFormat, maxLength, minLength, required, runValidators } from '../../utils/validators';

function toChannel(value: unknown): TriageChannel | null {
  if (typeof value !== 'string') {
    return null;
  }
  const normalized = value.trim().toUpperCase();
  if (normalized === 'GREEN' || normalized === 'YELLOW' || normalized === 'RED') {
    return normalized as TriageChannel;
  }
  return null;
}

export default function Auth() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { setUser, setChannel } = useAuthStore();

  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ username?: string; password?: string }>({});

  const validateUsername = (value: string): string | null => {
    const normalized = value.trim();
    const baseRuleError = runValidators(normalized, [
      required(t('validation.required', { field: t('fields.account') })),
      minLength(3, t('validation.min_length', { field: t('fields.account'), count: 3 })),
      maxLength(64, t('validation.max_length', { field: t('fields.account'), count: 64 })),
    ]);
    if (baseRuleError) return baseRuleError;

    if (normalized.includes('@')) {
      return runValidators(normalized, [emailFormat(t('validation.email'))]);
    }

    if (!/^[a-zA-Z0-9._-]+$/.test(normalized)) {
      return t('validation.account_chars');
    }

    return null;
  };

  const validatePassword = (value: string): string | null => {
    return runValidators(value, [
      required(t('validation.required', { field: t('fields.password') })),
      minLength(4, t('validation.min_length', { field: t('fields.password'), count: 4 })),
      maxLength(128, t('validation.max_length', { field: t('fields.password'), count: 128 })),
    ]);
  };

  const validateForm = (): boolean => {
    const nextErrors = {
      username: validateUsername(username) ?? undefined,
      password: validatePassword(password) ?? undefined,
    };
    setErrors(nextErrors);
    return !nextErrors.username && !nextErrors.password;
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);

    try {
      const normalized = username.trim();
      const loginAccount = normalized.includes('@') ? normalized.split('@')[0] : normalized;
      await adminLogin(loginAccount, password);

      const email = normalized.includes('@') ? normalized : `${normalized}@mimind.ai`;
      const currentLocale = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';
      let userId = localStorage.getItem('mc_user_id');
      let resolvedChannel: TriageChannel | null = null;

      if (!userId) {
        const data = await register(email, currentLocale, '2026.02');
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

      setUser(userId!, email, currentLocale);
      setChannel(resolvedChannel);

      if (resolvedChannel) {
        localStorage.setItem('mc_assessment_ts', String(Date.now()));
      }

      toast.success(t('auth.login_success'));
      navigate('/home');
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
            <span className="text-sm font-medium text-muted">{t('fields.account')}</span>
            <input
              type="text"
              value={username}
              onChange={(e) => {
                const value = e.target.value;
                setUsername(value);
                if (errors.username) {
                  setErrors((prev) => ({ ...prev, username: validateUsername(value) ?? undefined }));
                }
              }}
              onBlur={() => setErrors((prev) => ({ ...prev, username: validateUsername(username) ?? undefined }))}
              required
              className={`border rounded-xl px-4 py-3 bg-paper/90 text-ink focus:outline-none focus:ring-2 transition-shadow ${
                errors.username ? 'border-danger focus:ring-danger/30' : 'border-line focus:ring-accent/30'
              }`}
            />
            <FieldError message={errors.username} />
          </label>

          <label className="grid gap-1.5">
            <span className="text-sm font-medium text-muted">{t('auth.password')}</span>
            <input
              type="password"
              value={password}
              onChange={(e) => {
                const value = e.target.value;
                setPassword(value);
                if (errors.password) {
                  setErrors((prev) => ({ ...prev, password: validatePassword(value) ?? undefined }));
                }
              }}
              onBlur={() => setErrors((prev) => ({ ...prev, password: validatePassword(password) ?? undefined }))}
              required
              className={`border rounded-xl px-4 py-3 bg-paper/90 text-ink focus:outline-none focus:ring-2 transition-shadow ${
                errors.password ? 'border-danger focus:ring-danger/30' : 'border-line focus:ring-accent/30'
              }`}
            />
            <FieldError message={errors.password} />
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
