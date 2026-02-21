import { useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuthStore } from '../../stores/auth';
import { authLogin, authRegister, getEntitlements, requestPasswordReset, resetPassword } from '../../api/auth';
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

type AuthView = 'login' | 'register' | 'forgot' | 'reset';

export default function Auth() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const resetToken = searchParams.get('token')?.trim() ?? '';
  const { setUser, setChannel } = useAuthStore();

  const [view, setView] = useState<AuthView>(resetToken ? 'reset' : 'login');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const title = useMemo(() => {
    if (view === 'register') return t('auth.register');
    if (view === 'forgot') return t('auth.forgot_password');
    if (view === 'reset') return t('auth.reset_password');
    return t('auth.login');
  }, [t, view]);

  const validateEmail = (value: string): string | null => {
    const normalized = value.trim();
    return runValidators(normalized, [
      required(t('validation.required', { field: t('auth.email') })),
      emailFormat(t('validation.email')),
      maxLength(128, t('validation.max_length', { field: t('auth.email'), count: 128 })),
    ]);
  };

  const validatePassword = (value: string, strict: boolean): string | null => {
    const baseError = runValidators(value, [
      required(t('validation.required', { field: t('fields.password') })),
      minLength(strict ? 8 : 1, t('validation.min_length', { field: t('fields.password'), count: strict ? 8 : 1 })),
      maxLength(128, t('validation.max_length', { field: t('fields.password'), count: 128 })),
    ]);
    if (baseError) return baseError;

    if (strict && (!/[A-Za-z]/.test(value) || !/[0-9]/.test(value))) {
      return t('auth.password_hint');
    }

    return null;
  };

  const switchView = (next: AuthView) => {
    setView(next);
    setErrors({});
    if (next !== 'reset') {
      setSearchParams({});
    }
  };

  const validateForm = (): boolean => {
    const strictPassword = view === 'register' || view === 'reset';
    const nextErrors = {
      email: view === 'reset' ? undefined : validateEmail(email) ?? undefined,
      password: view === 'forgot' ? undefined : validatePassword(password, strictPassword) ?? undefined,
    };
    setErrors(nextErrors);
    return !nextErrors.email && !nextErrors.password;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    try {
      const normalizedEmail = email.trim().toLowerCase();
      const currentLocale = i18n.language === 'en-US' ? 'en-US' : 'zh-CN';

      if (view === 'forgot') {
        await requestPasswordReset(normalizedEmail);
        toast.success(t('auth.reset_email_sent'));
        setView('login');
        return;
      }

      if (view === 'reset') {
        if (!resetToken) {
          throw new Error(t('auth.reset_token_invalid'));
        }
        await resetPassword(resetToken, password);
        toast.success(t('auth.reset_success'));
        setPassword('');
        setSearchParams({});
        setView('login');
        return;
      }

      const authPayload =
        view === 'register'
          ? await authRegister(normalizedEmail, password, currentLocale, '2026.02')
          : await authLogin(normalizedEmail, password);

      const userId = authPayload.user?.user_id ?? authPayload.user_id;
      if (!userId) {
        throw new Error(t('common.error'));
      }

      const resolvedEmail = authPayload.user?.email ?? authPayload.email ?? normalizedEmail;
      const resolvedLocale = authPayload.user?.locale ?? currentLocale;
      let resolvedChannel: TriageChannel | null = toChannel(authPayload.channel);

      if (!resolvedChannel) {
        try {
          const entitlements = await getEntitlements(userId);
          resolvedChannel = toChannel(entitlements.channel);
        } catch {
          resolvedChannel = null;
        }
      }

      setUser(userId, resolvedEmail, resolvedLocale);
      setChannel(resolvedChannel);

      if (resolvedChannel) {
        localStorage.setItem('mc_assessment_ts', String(Date.now()));
      }

      toast.success(view === 'register' ? t('auth.register_success') : t('auth.login_success'));
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

        <h1 className="font-heading text-2xl font-bold">{title}</h1>
        <p className="text-muted text-sm mt-1 mb-6">{t('app.tagline')}</p>

        <form onSubmit={handleSubmit} className="grid gap-4">
          {view !== 'reset' ? (
            <label className="grid gap-1.5">
              <span className="text-sm font-medium text-muted">{t('auth.email')}</span>
              <input
                type="email"
                value={email}
                onChange={(e) => {
                  const value = e.target.value;
                  setEmail(value);
                  if (errors.email) {
                    setErrors((prev) => ({ ...prev, email: validateEmail(value) ?? undefined }));
                  }
                }}
                onBlur={() => setErrors((prev) => ({ ...prev, email: validateEmail(email) ?? undefined }))}
                placeholder={t('auth.email_placeholder')}
                required
                className={`border rounded-xl px-4 py-3 bg-paper/90 text-ink focus:outline-none focus:ring-2 transition-shadow ${
                  errors.email ? 'border-danger focus:ring-danger/30' : 'border-line focus:ring-accent/30'
                }`}
              />
              <FieldError message={errors.email} />
            </label>
          ) : null}

          {view !== 'forgot' ? (
            <label className="grid gap-1.5">
              <span className="text-sm font-medium text-muted">{t('auth.password')}</span>
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  const value = e.target.value;
                  setPassword(value);
                  if (errors.password) {
                    setErrors((prev) => ({
                      ...prev,
                      password: validatePassword(value, view === 'register' || view === 'reset') ?? undefined,
                    }));
                  }
                }}
                onBlur={() =>
                  setErrors((prev) => ({
                    ...prev,
                    password: validatePassword(password, view === 'register' || view === 'reset') ?? undefined,
                  }))
                }
                placeholder={t('auth.password_placeholder')}
                required
                className={`border rounded-xl px-4 py-3 bg-paper/90 text-ink focus:outline-none focus:ring-2 transition-shadow ${
                  errors.password ? 'border-danger focus:ring-danger/30' : 'border-line focus:ring-accent/30'
                }`}
              />
              <FieldError message={errors.password} />
              {view === 'register' || view === 'reset' ? (
                <p className="text-xs text-muted">{t('auth.password_hint')}</p>
              ) : null}
            </label>
          ) : null}

          <Button type="submit" loading={loading} className="w-full">
            {view === 'register'
              ? t('auth.submit_register')
              : view === 'forgot'
                ? t('auth.send_reset_link')
                : view === 'reset'
                  ? t('auth.reset_password_submit')
                  : t('auth.login')}
          </Button>
        </form>

        {view === 'login' ? (
          <>
            <div className="text-xs text-muted text-center mt-4">
              <button
                type="button"
                className="text-accent hover:underline"
                onClick={() => switchView('forgot')}
              >
                {t('auth.forgot_password')}
              </button>
            </div>
            <div className="text-xs text-muted text-center mt-2">
              {t('auth.no_account')}{' '}
              <button
                type="button"
                className="text-accent hover:underline"
                onClick={() => switchView('register')}
              >
                {t('auth.go_register')}
              </button>
            </div>
          </>
        ) : null}

        {view === 'register' || view === 'forgot' || view === 'reset' ? (
          <div className="text-xs text-muted text-center mt-4">
            {t('auth.have_account')}{' '}
            <button
              type="button"
              className="text-accent hover:underline"
              onClick={() => switchView('login')}
            >
              {t('auth.go_login')}
            </button>
          </div>
        ) : null}

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
