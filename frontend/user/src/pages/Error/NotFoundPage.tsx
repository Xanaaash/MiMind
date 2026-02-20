import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../../stores/auth';

export default function NotFoundPage() {
  const { t } = useTranslation();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const homePath = isAuthenticated ? '/home' : '/';

  return (
    <div className="min-h-screen px-4 py-12 flex items-center justify-center">
      <motion.div
        className="w-full max-w-2xl bg-panel border border-line rounded-3xl p-8 shadow-sm text-center"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="mx-auto w-24 h-24 rounded-3xl bg-warn-soft flex items-center justify-center text-5xl">
          🧭
        </div>
        <p className="mt-5 text-sm font-semibold text-warn">404</p>
        <h1 className="font-heading text-3xl font-bold mt-2">{t('not_found.title')}</h1>
        <p className="text-muted mt-3 leading-relaxed">{t('not_found.subtitle')}</p>

        <div className="mt-7 flex flex-wrap justify-center gap-3">
          <Link
            to={homePath}
            className="px-5 py-3 rounded-xl bg-accent text-white font-semibold hover:opacity-95 transition-opacity"
          >
            {t('not_found.back_home')}
          </Link>
          <Link
            to="/safety"
            className="px-5 py-3 rounded-xl border border-line bg-paper text-ink font-semibold hover:bg-cream transition-colors"
          >
            {t('not_found.safety')}
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
