import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

export default function ReliefHub() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="space-y-5">
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-line bg-panel px-5 py-6 sm:px-6 sm:py-7"
      >
        <div className="text-xs uppercase tracking-[0.2em] text-danger font-semibold">
          {t('nav.rescue')}
        </div>
        <h1 className="mt-2 font-heading text-2xl sm:text-3xl font-bold text-ink">
          {t('relief.title')}
        </h1>
        <p className="mt-2 text-sm text-muted max-w-2xl">
          {t('relief.subtitle')}
        </p>
      </motion.section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => navigate('/relief/sensory')}
          className="rounded-2xl border border-danger/40 bg-danger-soft px-5 py-6 text-left transition-colors hover:bg-danger hover:text-white"
        >
          <div className="text-xs uppercase tracking-wider font-semibold">{t('tools.sensory_title')}</div>
          <div className="mt-2 font-heading text-2xl font-bold">{t('relief.quick_sensory_title')}</div>
          <p className="mt-2 text-sm opacity-90">{t('relief.quick_sensory_desc')}</p>
        </button>

        <button
          type="button"
          onClick={() => navigate('/relief/breathing')}
          className="rounded-2xl border border-accent/40 bg-accent-soft px-5 py-6 text-left transition-colors hover:bg-accent hover:text-white"
        >
          <div className="text-xs uppercase tracking-wider font-semibold">{t('tools.breathing_title')}</div>
          <div className="mt-2 font-heading text-2xl font-bold">{t('relief.quick_breath_title')}</div>
          <p className="mt-2 text-sm opacity-90">{t('relief.quick_breath_desc')}</p>
        </button>
      </section>
    </div>
  );
}
