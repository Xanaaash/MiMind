import { motion } from 'framer-motion';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/Card/Card';

export default function MindfulnessHub() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="space-y-5">
      <motion.section
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        className="rounded-3xl border border-line bg-panel px-5 py-6 sm:px-6 sm:py-7"
      >
        <div className="text-xs uppercase tracking-[0.2em] text-accent font-semibold">
          {t('nav.mindfulness')}
        </div>
        <h1 className="mt-2 font-heading text-2xl sm:text-3xl font-bold text-ink">
          {t('mindfulness.title')}
        </h1>
        <p className="mt-2 text-sm text-muted max-w-2xl">
          {t('mindfulness.subtitle')}
        </p>
      </motion.section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Card hoverable onClick={() => navigate('/mindfulness/meditation')}>
          <div className="text-sm text-muted">{t('tools.meditation_title')}</div>
          <div className="mt-1 text-xl font-heading font-bold">{t('mindfulness.meditation_title')}</div>
          <p className="mt-1 text-sm text-muted">{t('mindfulness.meditation_desc')}</p>
        </Card>

        <Card>
          <div className="text-sm text-muted">{t('mindfulness.manifestation_badge')}</div>
          <div className="mt-1 text-xl font-heading font-bold">{t('mindfulness.manifestation_title')}</div>
          <p className="mt-1 text-sm text-muted">{t('mindfulness.manifestation_desc')}</p>
        </Card>
      </section>
    </div>
  );
}
